#!/usr/bin/env python3
"""Verify that every numbered paper table has a regenerated output."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Each entry maps the submitted paper table to one or more output files and
# stable anchors that identify the reported analysis. Values use the full
# precision printed by the analysis scripts where practical.
CHECKS = {
    1: [
        ("reproduced/table_1_main_arithmetic.txt", ["median_contrast=+1.107", "median_contrast=-0.731"]),
        ("reproduced/table_2_main_chartqa.txt", ["cll\tQwen2-VL-2B-Instruct\t229\t+2.9549", "cll\tPhi-3.5-vision-instruct\t229"]),
    ],
    2: [("reproduced/table_2_checkpoint_revisions.txt", ["895c3a49bc3fa70a340399125c650a463535e71c", "6fb9ad6924f69424e57fab2ab061d707688f0296"])],
    3: [
        ("reproduced/frontier_chartqa_contrast_luna.txt", ["-0.9249", "[-0.9711,-0.8728]"]),
        ("reproduced/frontier_chartqa_contrast_gemini.txt", ["-0.7719", "[-0.8538,-0.6842]"]),
    ],
    4: [("reproduced/frontier_chartqa_trajectories.txt", ["GPT-5.6-Luna\timage\tL4\ttext\t0.9630", "Gemini-3.5-Flash\timage\tL5\ttext\t0.9362"])],
    5: [("reproduced/appendix/cll_generation_agreement.txt", ["POOLED/both_arms_L0_deduplicated\t20281\t26893\t0.7541"])],
    6: [
        ("reproduced/appendix/pooled_accuracy_regression_gsm8k.txt", ["OLS_clustered_by_model\t+2.704858\t0.906258"]),
        ("reproduced/appendix/pooled_accuracy_regression_gsm8k_winsor01.txt", ["OLS_clustered_by_model\t+2.429470\t0.666446"]),
        ("reproduced/appendix/pooled_accuracy_regression_svamp.txt", ["OLS_clustered_by_model\t+3.273214\t0.979128"]),
        ("reproduced/appendix/pooled_accuracy_regression_svamp_winsor01.txt", ["OLS_clustered_by_model\t+3.077260\t0.828995"]),
        ("reproduced/appendix/calibration_axes_gsm8k.txt", ["mod:leg(b3)      = +1.779", "mod:leg(b3)      = +5.551"]),
        ("reproduced/appendix/calibration_axes_svamp.txt", ["mod:leg(b3)      = +1.982", "mod:leg(b3)      = +7.965"]),
    ],
    7: [("reproduced/appendix/calibrated_slopes.txt", ["gsm8k\tQwen2-VL-2B\t1319\t+0.1305\t+0.9571\t+0.8266", "svamp\tPhi-3.5\t300\t+0.0176\t+3.3119\t+3.2942"])],
    8: [("reproduced/appendix/calibrated_slopes.txt", ["chartqa\tQwen2-VL-2B\t229\t+2.8968\t+1.7399\t-1.1569", "chartqa\tPhi-3.5\t229\t+3.4105\t+2.8099\t-0.6006"] )],
    9: [
        ("reproduced/appendix_chartqa_chart_vs_table.txt", ["Qwen2.5-VL-7B-Instruct\t229\t-1.3615\t-1.7009\t-0.3349"]),
        ("reproduced/appendix_chartqa_table_endpoint.txt", ["cll\tQwen2-VL-2B-Instruct\t229\t+3.1351\t+2.1457\t-0.9702\t[-1.2172,-0.8125]"]),
    ],
    10: [("reproduced/appendix/length_normalization.txt", [
        "gsm8k_neutral\tQwen2-VL-2B-Instruct\t0\t1319",
        "svamp_neutral\tPhi-3.5-vision-instruct\t1\t300",
        "chartqa\tPhi-3.5-vision-instruct\t1\t229",
    ])],
    11: [("reproduced/appendix/chartqa_generated_answers.txt", ["generation\tQwen2-VL-2B-Instruct\t113\t+0.9292", "generation\tPhi-3.5-vision-instruct\t9\t+1.0000", "generation\tInternVL2-8B\t105\t+0.2857"] )],
    12: [("reproduced/appendix/prompt_framing.txt", ["Qwen2.5-VL-7B-Instruct\t1319\t+0.8125\t+0.0595\t-0.3750", "Phi-3.5-vision-instruct\t1319\t+1.3750\t+1.3104\t+0.0000"] )],
}


def main() -> None:
    failures = []
    for table, outputs in CHECKS.items():
        for relative, anchors in outputs:
            path = ROOT / relative
            if not path.is_file():
                failures.append(f"Table {table}: missing {relative}")
                continue
            payload = path.read_bytes()
            try:
                text = payload.decode("utf-8")
            except UnicodeDecodeError:
                # PowerShell's Tee-Object may create UTF-16 files during an
                # ad-hoc Windows run; reproduce_all.py itself writes UTF-8.
                text = payload.decode("utf-16")
            for anchor in anchors:
                if anchor not in text:
                    failures.append(f"Table {table}: {relative} lacks {anchor!r}")
        if not any(message.startswith(f"Table {table}:") for message in failures):
            print(f"Table {table}: PASS")
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print("All 12 numbered paper tables are backed by regenerated artifact outputs.")


if __name__ == "__main__":
    main()
