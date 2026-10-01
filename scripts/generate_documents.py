"""Generate current reports from a single validated JSON artifact."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any

from myoshift.provenance import verify

ROOT = Path(__file__).resolve().parents[1]


def write_or_check(path: Path, content: str, *, check: bool) -> None:
    if check:
        if not path.exists() or path.read_text() != content:
            raise ValueError(f"generated document mismatch: {path.name}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def interval(metric: dict[str, Any]) -> str:
    value, low, high = metric["value"], metric["ci_low"], metric["ci_high"]
    if value is None:
        return "unavailable"
    if low is None or high is None:
        return f"{value:.3f} [unavailable]"
    return f"{value:.3f} [{low:.3f}, {high:.3f}]"


def tables(data: dict[str, Any]) -> str:
    text = ""
    for shift in ("person", "session", "electrode"):
        text += f"\n## {shift.capitalize()} shift\n\n"
        text += (
            "| Decoder | Trial-event recall [95% interval] | Window recall [95% interval] | "
            "False events/rest hour [95% interval] | Risk [95% interval] | "
            "Coverage [95% interval] | Test windows | Gesture events | Participants | "
            "p95 predict ms |\n"
        )
        text += "|---|---|---|---|---|---|---:|---:|---:|---:|\n"
        for run in data["runs"]:
            if run["shift"] != shift:
                continue
            if run["status"] == "unavailable":
                text += f"| {run['decoder']} | unavailable: {run['reason']} | | | | | | | | |\n"
                continue
            cells = [
                interval(run["metrics"][name])
                for name in (
                    "event_recall",
                    "window_recall",
                    "false_activations_per_rest_hour",
                    "risk",
                    "coverage",
                )
            ]
            text += (
                f"| {run['decoder']} | "
                + " | ".join(cells)
                + f" | {run['n_test']} | {run['n_gesture_events']} | {run['n_participants']}"
                + f" | {run['latency_ms_p95']:.3f} |\n"
            )
        measured = next(
            r for r in data["runs"] if r["shift"] == shift and r["status"] == "available"
        )
        text += (
            f"\nMeasured eligible rest exposure: {measured['rest_exposure_s']:.6f} seconds. "
            f"{measured['n_trials']} independent test records.\n"
        )
    text += "\n## Paired participant comparisons\n\n"
    text += (
        "| Shift | Contrast | Event recall difference [95% interval] | "
        "Window recall difference [95% interval] | Coverage difference [95% interval] |\n"
        "|---|---|---|---|---|\n"
    )
    for contrast in data["paired_comparisons"]:
        text += (
            f"| {contrast['shift']} | {contrast['contrast']} | "
            + " | ".join(
                interval(contrast["metrics"][name])
                for name in ("event_recall", "window_recall", "coverage")
            )
            + " |\n"
        )
    return text


def limitations_block(data: dict[str, Any]) -> str:
    budget = data["config"]["budget"]["max_calibration_windows"]
    return (
        "GRABMyoFlow participants are healthy adults recorded in seated laboratory conditions; "
        "clinical or impaired-population generalisation is untested. "
        f"Person and electrode shifts each fit one model per held-out participant with a "
        f"{budget}-window calibration prefix on that participant's unpermuted windows "
        f"({budget * len(data['config']['participants'])} windows across four folds). "
        f"Session shift pools all participants' held-out session-3 windows and takes one "
        f"global {budget}-window prefix before thresholding all four participants together. "
        "That prefix is the first lexicographically ordered windows of participant 44's "
        "session-3 rest record, not a separate calibration per participant. "
        "Electrode shift calibrates on the held-out participant's unpermuted prefix, then "
        "permutes only test features within each wrist ring, combining participant hold-out "
        "with a synthetic post-calibration channel change. "
        "Feature samples for the full pilot are materialised before replay; waveforms load "
        "trial by trial. This is causal-window offline replay without validated live "
        "acquisition, continuous transitions or physiological onset timing. "
        "Trial-level detection saturates easily and cannot measure physiological timing. "
        "Calibration contains only rest and cannot validate gesture-conditioned confidence "
        "rejection. "
        f"{data['provenance'].get('latency_scope', 'decoder.predict call only')}; "
        "The governing compressed/swapped footprint gate remains unverified when measurement "
        "is blocked or unavailable. No second dataset, external official controller, "
        "population safety claim or threshold frontier has been validated."
    )


def interpretation(data: dict[str, Any]) -> str:
    person = {r["decoder"]: r for r in data["runs"] if r["shift"] == "person"}
    static, selective = person["static_lda"], person["myoshift"]
    relation = (
        "lower"
        if selective["metrics"]["window_recall"]["value"]
        < static["metrics"]["window_recall"]["value"]
        else "at least as high"
    )
    false = sum(r.get("false_activation_events", 0) for r in data["runs"])
    return (
        f"Person-shift selective window recall is {relation} than static LDA: "
        f"{interval(selective['metrics']['window_recall'])} versus "
        f"{interval(static['metrics']['window_recall'])}. Trial-event recall is a separate, "
        "coarse detection metric, not physiological event timing. "
        f"The available runs counted {false} false command events in total across the repeated "
        "method evaluations. Short laboratory rest exposure and a zero-count bootstrap interval "
        "cannot establish safety equivalence. Decoder novelty remains withdrawn. "
        "Threshold-swept risk-coverage and matched-recall comparisons are untested. "
        f"Person coverage stop rule fired: {data['stop_rules']['person_coverage_failure']}. "
        f"Hysteresis interval-overlap novelty stop fired: "
        f"{data['stop_rules']['hysteresis_interval_stop_fired']}. "
        "This withdrawal stop is not an equivalence test. "
        "The few-shot baseline is unavailable under the frozen rest-only calibration prefix. "
        "No general benchmark novelty or clinical usefulness is established by this repair."
    )


def generate(*, check: bool = False) -> None:
    source = ROOT / "results/results.json"
    data = json.loads(source.read_text())
    verify(ROOT, data)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    provenance_block = (
        f"Generated from `results/results.json`, SHA-256 `{digest}`. "
        f"Python {data['provenance']['python']}; software versions: "
        f"`{json.dumps(data['provenance']['software'], sort_keys=True)}`.\n\n"
        f"Protocol hash: `{data['provenance']['protocol_sha256']}`. "
        "Pre-result freeze chronology is unverified. "
        "All repair amendments were made after results had been seen.\n"
    )
    run_provenance = data["provenance"]
    config = data["config"]
    methods = (
        f"Real GRABMyoFlow pilot: {config['n_records']} records, "
        f"{config['n_windows']} windows, {len(config['participants'])} participants "
        f"({', '.join(map(str, config['participants']))}), "
        f"{config['feature_dimensions']} features from named wrist channels. "
        "Person and electrode shifts use all participant hold-out folds; session shift holds out "
        "session 3. Calibration is the original prefix budget with raw-support overlap purged. "
        "Every independent record resets decoder state. "
        "Source LDA fitting uses source labels only; selective calibration uses independent target "
        "windows and the same confidence score at calibration and prediction. "
        "There is no affine session adaptation or conformal guarantee. "
        "The fixed bespoke hysteresis reference uses the same source training data. "
        "All source-informed methods have the same optional target-window budget; "
        "few-shot has only target calibration labels and no source data.\n\n"
        "Command onsets require one decision interval with non-rest output, confidence at least "
        "0.5 and no abstention. Holding a command counts once, until rest, abstention, low "
        "confidence, a changed command or record boundary. One eligible gesture record is "
        "one metadata-defined event; any correct command in its eligible test portion detects it. "
        "Exposure covers actual decision intervals after feature warm-up, clipped to raw "
        "record duration. No exposure and no accepted predictions give unavailable rate and risk, "
        "respectively. See the amendments for the complete rule.\n\n"
        "Intervals resample whole participant clusters with paired methods. They are descriptive "
        "small-pilot intervals: participant hold-out folds share training data. "
        "They do not establish population safety, and zero-count intervals "
        "are not equivalence tests.\n"
    )
    resource = (
        f"Full evaluation runtime: {data['runtime_s']:.3f} s. Cumulative process peak RSS: "
        f"{data['cumulative_process_peak_rss_mb']:.3f} MiB. "
        f"Host: {run_provenance.get('hostname', 'unknown')}; "
        f"platform: {run_provenance.get('platform', run_provenance.get('hardware', 'unknown'))}. "
        f"Footprint measurement: {run_provenance.get('footprint_measurement', 'not recorded')}. "
        "Latency p95 columns time `decoder.predict` only; they exclude feature extraction, "
        "acquisition and end-to-end command response. "
        "RSS is not isolated evaluation memory or macOS compressed/swapped footprint. "
        "The required footprint gate remains unverified when measurement is blocked "
        "or unavailable.\n"
    )
    result_tables = tables(data)
    conclusion = interpretation(data)
    results = (
        "# Corrected results\n\n" + provenance_block + "\n## Reproduction\n\n"
        '```sh\npip install -e ".[dev]"\nbash scripts/download_pilot.sh\n'
        "python scripts/run_benchmark.py\npython scripts/generate_documents.py --check\n```\n\n"
        "The benchmark command regenerates JSON, prediction traces, figures and all current "
        "result documents. Frozen protocol bytes are untouched.\n\n"
        + methods
        + result_tables
        + "\n## Interpretation\n\n"
        + conclusion
        + "\n\n## Limitations\n\n"
        + limitations_block(data)
        + "\n\n## Resource receipt\n\n"
        + resource
    )
    readme = (
        "# MyoShift\n\n"
        "RoboteX Labs' public-data engineering demonstration of reproducible sEMG "
        "command-event evaluation under participant, session and proxy electrode shifts. "
        "The reusable capability is an audited data-to-report pipeline: verified inputs, "
        "leakage-aware splits, record resets, measured rest exposure and participant uncertainty. "
        "This corrected negative study provides no evidence of client delivery, paid firm "
        "past performance, adoption or clinical benefit.\n\n"
        "![Person-shift risk and coverage operating points]"
        "(results/figures/risk_coverage_person.png)\n\n"
        "Each annotated point is one fixed operating point, not a measured frontier. "
        "Four healthy seated participants, heavy abstention and short rest exposure limit "
        "interpretation; zero counts cannot establish safety.\n\n"
        + conclusion
        + "\n\n## Run the demonstration\n\n"
        "```sh\npython3 -m venv .venv\nsource .venv/bin/activate\n"
        'pip install -e ".[dev]"\nbash scripts/download_pilot.sh\n'
        "python scripts/run_benchmark.py\npython scripts/generate_documents.py --check\n"
        "python -m pytest -o addopts= -m 'not network' --cov=myoshift --cov-fail-under=90\n"
        "```\n\n"
        "The single benchmark command regenerates JSON, traces, figures and current documents "
        "headlessly from downloaded public data. The network test needs internet access and "
        "an empty destination; cached acceptance is recorded separately. "
        "Python 3.11 on macOS arm64 is locally exercised; Python 3.12 is configured in CI "
        "and awaits a hosted receipt. No other platform is validated.\n\n"
        "CLI example: `myoshift verify-scorers`; library entry: "
        "`myoshift.eval.benchmark.run_full_benchmark(data_root, output_dir)`.\n\n"
        "## Inspect the evidence\n\n"
        "[Compact verification receipt](docs/milestones/PUBLICATION_FIX_REPORT_3_2026-10-01.md), "
        "[full results and limitations](RESULTS.md), "
        "[negative-result report](docs/negative-result-report.md), "
        "[technical report](docs/technical-report.md). Frozen protocol bytes are preserved; "
        "the chronology of a pre-result freeze remains unverified.\n\n"
        "Related work: [EMGBench](https://arxiv.org/abs/2410.23625), "
        "[generic neuromotor interface](https://doi.org/10.1038/s41586-025-09255-w). "
        "Data: [GRABMyoFlow](https://physionet.org/content/grabmyo-flow/1.0.0/). "
        "No omission or superiority over these resources is claimed.\n\n"
        "## Licence and citation\n\nCode: [Apache-2.0](LICENSE). Documentation and derived "
        "results: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). "
        "See [NOTICE](NOTICE) for exhaustive scopes and upstream credit, and "
        "[CITATION.cff](CITATION.cff).\n"
    )
    technical = (
        "# MyoShift: corrected static-trial sEMG pilot\n\nDraft technical report.\n\n"
        + provenance_block
        + "\n## Problem and related work\n\n"
        "Reliable command scoring requires preserved trial labels, measured exposure and "
        "independent calibration. This repair evaluates a small static-trial pilot; it does "
        "not demonstrate physiological onset detection or a new best decoder. "
        "[EMGBench](https://arxiv.org/abs/2410.23625) and the "
        "[generic neuromotor interface study](https://doi.org/10.1038/s41586-025-09255-w) "
        "are related work; no unverified omission in either is claimed.\n\n"
        "## Data and method\n\n" + methods + "\n## Experiments\n\n"
        "The frozen dated protocol remains byte-identical; pre-result chronology is unverified. "
        "The repair amendments describe all departures after observing results. "
        "The within-ring channel permutation is a proxy, not a measured physical displacement.\n"
        + result_tables
        + "\n## Interpretation and limitations\n\n"
        + conclusion
        + "\n\n"
        + limitations_block(data)
        + "\n\n## Resources\n\n"
        + resource
        + "\n\n## References\n\n"
        "GRABMyoFlow: [Ehlert, Tung and Pradhan, PhysioNet 1.0.0]"
        "(https://doi.org/10.13026/ah52-zq51), "
        "CC BY 4.0. The official extension converter selects wrist indices 1-6 and 9-14. "
        "PhysioNet platform (current): Pollard T, Moody BE, Lehman L, Gow B, Fernandes C, "
        "Xie C, Johnson A, Mark RG, Heldt T. PhysioNet as a global platform for biomedical "
        "research. Nature Health. 2026. doi:10.1038/s44360-026-00096-z. "
        "Earlier platform citation: Goldberger AL, Amaral LAN, Glass L, et al. Circulation. "
        "2000;101(23):e215-e220.\n"
    )
    site = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>MyoShift public-data demonstration</title><style>"
        "body{font-family:system-ui;line-height:1.6;max-width:52rem;margin:auto;padding:1rem}"
        "img{max-width:100%;height:auto}pre{overflow:auto}"
        "a:focus-visible{outline:3px solid #1257ab}"
        "</style></head><body><header><h1>MyoShift</h1></header><main>"
        "<p>RoboteX Labs' public-data engineering demonstration: a reproducible sEMG "
        "data-to-report pipeline with verified inputs, leakage-aware splits, record resets, "
        "rest-exposure scoring and participant uncertainty. This corrected negative study "
        "does not establish client delivery, adoption or clinical benefit.</p>"
        '<figure><img src="../../results/figures/risk_coverage_person.png" '
        'alt="Annotated person-shift risk and coverage operating points">'
        "<figcaption>Fixed operating points; the frontier is untested. Four healthy seated "
        "participants and heavy abstention limit interpretation. Short rest exposure and "
        "zero counts cannot establish safety.</figcaption></figure>"
        "<p>" + html.escape(conclusion) + "</p>"
        '<h2>Run the demonstration</h2><pre>pip install -e ".[dev]"\n'
        "bash scripts/download_pilot.sh\npython scripts/run_benchmark.py\n"
        "myoshift verify-scorers</pre>"
        "<p>Headless regeneration writes JSON, prediction traces, figures and reports. "
        "Python 3.11/macOS arm64 is locally exercised; Python 3.12 is CI-configured "
        "and awaits a hosted receipt.</p>"
        '<p><a href="../milestones/PUBLICATION_FIX_REPORT_3_2026-10-01.md">'
        "Compact verification receipt</a>; "
        '<a href="../../RESULTS.md">full tables and limitations</a>; '
        '<a href="../negative-result-report.md">negative-result report</a>; '
        '<a href="../technical-report.md">technical report and provenance</a>.</p>'
        "</main><footer><p>Code Apache-2.0. Documentation and derived results "
        '<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. '
        'Data: <a href="https://physionet.org/content/grabmyo-flow/1.0.0/">GRABMyoFlow</a>. '
        '<a href="../../NOTICE">Full licence scopes and credit</a>.</p>'
        "</footer></body></html>\n"
    )
    for path, content in [
        (ROOT / "RESULTS.md", results),
        (ROOT / "README.md", readme),
        (ROOT / "docs/technical-report.md", technical),
        (ROOT / "docs/site/index.html", site),
    ]:
        write_or_check(path, content, check=check)

    try:
        from scripts.generate_report_tables import generate as generate_report
    except ModuleNotFoundError:
        from generate_report_tables import generate as generate_report

    generate_report(check=check)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    generate(check=parser.parse_args().check)
