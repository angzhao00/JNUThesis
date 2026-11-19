from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import erf


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "chap3" / "3.4_coordinated_gating" / "3.4.1_simulation"
WAVEFORM_CSV = DATA_DIR / "simulated_gating_waveforms.csv"
SWEEP_CSV = DATA_DIR / "simulated_precompensation_sweep.csv"
SENSITIVITY_CSV = DATA_DIR / "simulated_delay_sensitivity.csv"
SUMMARY_CSV = DATA_DIR / "simulated_strategy_summary.csv"
PARAMETERS_JSON = DATA_DIR / "simulation_parameters.json"
FIGURE_BASE = ROOT / "images" / "chap3_coordinated_gating_simulation"

TIME_STEP_NS = 0.1
TIME_RANGE_NS = (-200.0, 400.0)
SOA_PULSE_WIDTH_NS = 100.0
SOA_RISE_FALL_10_90_NS = 6.0
AOM_DELAY_NS = 50.0
AOM_RISE_FALL_10_90_NS = 40.0
PRECOMPENSATION_NS = 80.0
HOLD_NS = 20.0
REPETITION_HZ = 2_000.0

BLUE = "#2F6B9A"
ORANGE = "#D97706"
TEAL = "#258F83"
PURPLE = "#7A5195"
GRAY = "#6B7280"


def sigma_from_rise_time(rise_time_10_90_ns: float) -> float:
    # A Gaussian-smoothed step traverses 10% to 90% in about 2.563 sigma.
    return rise_time_10_90_ns / 2.563103


def smooth_step(time_ns: np.ndarray, edge_ns: float, rise_time_ns: float) -> np.ndarray:
    sigma_ns = sigma_from_rise_time(rise_time_ns)
    return 0.5 * (
        1.0 + erf((time_ns - edge_ns) / (np.sqrt(2.0) * sigma_ns))
    )


def smooth_gate(
    time_ns: np.ndarray,
    start_ns: float,
    stop_ns: float,
    delay_ns: float,
    rise_fall_ns: float,
) -> np.ndarray:
    response = smooth_step(time_ns, start_ns + delay_ns, rise_fall_ns)
    response -= smooth_step(time_ns, stop_ns + delay_ns, rise_fall_ns)
    return np.clip(response, 0.0, 1.0)


def normalized_overlap(
    time_ns: np.ndarray, soa_pulse: np.ndarray, aom_response: np.ndarray
) -> float:
    return float(
        np.trapezoid(soa_pulse * aom_response, time_ns)
        / np.trapezoid(soa_pulse, time_ns)
    )


def strategy_metrics(
    time_ns: np.ndarray,
    soa_pulse: np.ndarray,
    aom_response: np.ndarray,
    rf_gate_width_ns: float | None,
) -> dict[str, float]:
    effective = soa_pulse * aom_response
    total_energy = np.trapezoid(soa_pulse, time_ns)
    midpoint_ns = SOA_PULSE_WIDTH_NS / 2.0
    leading = time_ns <= midpoint_ns
    trailing = time_ns > midpoint_ns
    leading_loss = np.trapezoid((soa_pulse - effective)[leading], time_ns[leading])
    trailing_loss = np.trapezoid((soa_pulse - effective)[trailing], time_ns[trailing])
    rf_duty_cycle = 1.0 if rf_gate_width_ns is None else rf_gate_width_ns * 1e-9 * REPETITION_HZ
    return {
        "overlap_efficiency_pct": normalized_overlap(time_ns, soa_pulse, aom_response) * 100.0,
        "leading_energy_loss_pct": float(leading_loss / total_energy * 100.0),
        "trailing_energy_loss_pct": float(trailing_loss / total_energy * 100.0),
        "rf_gate_width_ns": float("nan") if rf_gate_width_ns is None else rf_gate_width_ns,
        "rf_duty_cycle_pct": rf_duty_cycle * 100.0,
    }


def style_axes(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.55, alpha=0.35)
    ax.tick_params(direction="out", length=3, width=0.8)


def add_panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.13,
        1.07,
        label,
        transform=ax.transAxes,
        fontsize=9.5,
        fontweight="bold",
        va="top",
        ha="left",
    )


def configure_plot_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 7.8,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 6.8,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.35,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    time_ns = np.arange(
        TIME_RANGE_NS[0], TIME_RANGE_NS[1] + TIME_STEP_NS, TIME_STEP_NS
    )
    soa_pulse = smooth_gate(
        time_ns,
        start_ns=0.0,
        stop_ns=SOA_PULSE_WIDTH_NS,
        delay_ns=0.0,
        rise_fall_ns=SOA_RISE_FALL_10_90_NS,
    )
    responses = {
        "Continuous RF": np.ones_like(time_ns),
        "Edge-synchronous": smooth_gate(
            time_ns,
            start_ns=0.0,
            stop_ns=SOA_PULSE_WIDTH_NS,
            delay_ns=AOM_DELAY_NS,
            rise_fall_ns=AOM_RISE_FALL_10_90_NS,
        ),
        "Precompensated": smooth_gate(
            time_ns,
            start_ns=-PRECOMPENSATION_NS,
            stop_ns=SOA_PULSE_WIDTH_NS + HOLD_NS,
            delay_ns=AOM_DELAY_NS,
            rise_fall_ns=AOM_RISE_FALL_10_90_NS,
        ),
    }
    rf_gate_widths = {
        "Continuous RF": None,
        "Edge-synchronous": SOA_PULSE_WIDTH_NS,
        "Precompensated": SOA_PULSE_WIDTH_NS + PRECOMPENSATION_NS + HOLD_NS,
    }

    waveform = pd.DataFrame({"time_ns": time_ns, "soa_pulse": soa_pulse})
    summary_rows = []
    for strategy, response in responses.items():
        column = strategy.lower().replace(" ", "_").replace("-", "_")
        waveform[f"aom_{column}"] = response
        waveform[f"effective_{column}"] = soa_pulse * response
        summary_rows.append(
            {
                "strategy": strategy,
                **strategy_metrics(
                    time_ns,
                    soa_pulse,
                    response,
                    rf_gate_widths[strategy],
                ),
            }
        )
    waveform.to_csv(WAVEFORM_CSV, index=False, encoding="utf-8-sig")
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY_CSV, index=False, encoding="utf-8-sig")

    pre_values = np.arange(0.0, 121.0, 1.0)
    hold_values = np.arange(0.0, 81.0, 1.0)
    sweep_rows = []
    overlap_grid = np.empty((hold_values.size, pre_values.size))
    for hold_index, hold_ns in enumerate(hold_values):
        for pre_index, pre_ns in enumerate(pre_values):
            response = smooth_gate(
                time_ns,
                start_ns=-pre_ns,
                stop_ns=SOA_PULSE_WIDTH_NS + hold_ns,
                delay_ns=AOM_DELAY_NS,
                rise_fall_ns=AOM_RISE_FALL_10_90_NS,
            )
            overlap_pct = normalized_overlap(time_ns, soa_pulse, response) * 100.0
            overlap_grid[hold_index, pre_index] = overlap_pct
            sweep_rows.append(
                {
                    "precompensation_ns": pre_ns,
                    "hold_ns": hold_ns,
                    "overlap_efficiency_pct": overlap_pct,
                    "rf_gate_width_ns": SOA_PULSE_WIDTH_NS + pre_ns + hold_ns,
                    "rf_duty_cycle_pct": (
                        SOA_PULSE_WIDTH_NS + pre_ns + hold_ns
                    )
                    * 1e-9
                    * REPETITION_HZ
                    * 100.0,
                }
            )
    pd.DataFrame(sweep_rows).to_csv(SWEEP_CSV, index=False, encoding="utf-8-sig")

    delay_values = np.arange(20.0, 101.0, 1.0)
    sensitivity_rows = []
    for delay_ns in delay_values:
        simple_response = smooth_gate(
            time_ns,
            start_ns=0.0,
            stop_ns=SOA_PULSE_WIDTH_NS,
            delay_ns=delay_ns,
            rise_fall_ns=AOM_RISE_FALL_10_90_NS,
        )
        precompensated_response = smooth_gate(
            time_ns,
            start_ns=-PRECOMPENSATION_NS,
            stop_ns=SOA_PULSE_WIDTH_NS + HOLD_NS,
            delay_ns=delay_ns,
            rise_fall_ns=AOM_RISE_FALL_10_90_NS,
        )
        sensitivity_rows.extend(
            [
                {
                    "aom_delay_ns": delay_ns,
                    "strategy": "Continuous RF",
                    "overlap_efficiency_pct": 100.0,
                },
                {
                    "aom_delay_ns": delay_ns,
                    "strategy": "Edge-synchronous",
                    "overlap_efficiency_pct": normalized_overlap(
                        time_ns, soa_pulse, simple_response
                    )
                    * 100.0,
                },
                {
                    "aom_delay_ns": delay_ns,
                    "strategy": "Precompensated",
                    "overlap_efficiency_pct": normalized_overlap(
                        time_ns, soa_pulse, precompensated_response
                    )
                    * 100.0,
                },
            ]
        )
    sensitivity = pd.DataFrame(sensitivity_rows)
    sensitivity.to_csv(SENSITIVITY_CSV, index=False, encoding="utf-8-sig")

    parameters = {
        "data_classification": "deterministic numerical simulation for teaching",
        "time_step_ns": TIME_STEP_NS,
        "time_range_ns": list(TIME_RANGE_NS),
        "soa_pulse_width_ns": SOA_PULSE_WIDTH_NS,
        "soa_rise_fall_10_90_ns": SOA_RISE_FALL_10_90_NS,
        "aom_command_to_optical_delay_ns": AOM_DELAY_NS,
        "aom_rise_fall_10_90_ns": AOM_RISE_FALL_10_90_NS,
        "nominal_precompensation_ns": PRECOMPENSATION_NS,
        "nominal_hold_ns": HOLD_NS,
        "repetition_rate_Hz": REPETITION_HZ,
        "precompensation_sweep_ns": [float(pre_values.min()), float(pre_values.max()), 1.0],
        "hold_sweep_ns": [float(hold_values.min()), float(hold_values.max()), 1.0],
        "aom_delay_sensitivity_ns": [float(delay_values.min()), float(delay_values.max()), 1.0],
        "model": "difference of Gaussian-smoothed steps; t10-90 = 2.563103 sigma",
        "strategy_summary": [
            {
                key: None if pd.isna(value) else value
                for key, value in record.items()
            }
            for record in summary.to_dict(orient="records")
        ],
    }
    PARAMETERS_JSON.write_text(
        json.dumps(parameters, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    configure_plot_style()
    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.4), constrained_layout=True)
    ax_a, ax_b, ax_c, ax_d = axes.flat
    colors = {
        "Continuous RF": GRAY,
        "Edge-synchronous": ORANGE,
        "Precompensated": TEAL,
    }

    ax_a.plot(time_ns, soa_pulse, color=BLUE, linewidth=1.7, label="SOA pulse")
    for strategy, response in responses.items():
        ax_a.plot(time_ns, response, color=colors[strategy], label=f"AOM: {strategy}")
    ax_a.set_xlim(-120, 220)
    ax_a.set_ylim(-0.04, 1.08)
    ax_a.set_xlabel("Time relative to SOA command (ns)")
    ax_a.set_ylabel("Normalized amplitude")
    ax_a.legend(frameon=False, loc="lower right")

    for strategy, response in responses.items():
        ax_b.plot(
            time_ns,
            soa_pulse * response,
            color=colors[strategy],
            label=f"{strategy}: {summary.loc[summary['strategy'] == strategy, 'overlap_efficiency_pct'].iloc[0]:.1f}%",
        )
    ax_b.plot(time_ns, soa_pulse, color=BLUE, linestyle=":", label="SOA reference")
    ax_b.set_xlim(-30, 150)
    ax_b.set_ylim(-0.04, 1.08)
    ax_b.set_xlabel("Time relative to SOA command (ns)")
    ax_b.set_ylabel("Effective transmitted pulse")
    ax_b.legend(frameon=False, loc="lower center")

    image = ax_c.imshow(
        overlap_grid,
        origin="lower",
        aspect="auto",
        extent=[pre_values.min(), pre_values.max(), hold_values.min(), hold_values.max()],
        cmap="viridis",
        vmin=45,
        vmax=100,
    )
    contour = ax_c.contour(
        pre_values,
        hold_values,
        overlap_grid,
        levels=[95, 99],
        colors=["white", "#F59E0B"],
        linewidths=[0.9, 1.1],
    )
    ax_c.clabel(contour, inline=True, fontsize=7, fmt="%.0f%%")
    ax_c.scatter(
        [PRECOMPENSATION_NS],
        [HOLD_NS],
        marker="*",
        s=55,
        color="#DC2626",
        edgecolor="white",
        linewidth=0.6,
        label="Nominal point",
    )
    ax_c.set_xlabel(r"Precompensation $\Delta t_{\mathrm{pre}}$ (ns)")
    ax_c.set_ylabel(r"Hold time $\Delta t_{\mathrm{hold}}$ (ns)")
    ax_c.legend(frameon=False, loc="lower right")
    colorbar = fig.colorbar(image, ax=ax_c, pad=0.02)
    colorbar.set_label("Overlap efficiency (%)")

    for strategy, group in sensitivity.groupby("strategy", sort=False):
        ax_d.plot(
            group["aom_delay_ns"],
            group["overlap_efficiency_pct"],
            color=colors[strategy],
            label=strategy,
        )
    ax_d.axvline(AOM_DELAY_NS, color=PURPLE, linestyle=":", linewidth=1.0)
    ax_d.set_xlim(delay_values.min(), delay_values.max())
    ax_d.set_ylim(0, 104)
    ax_d.set_xlabel("AOM command-to-optical delay (ns)")
    ax_d.set_ylabel("Overlap efficiency (%)")
    ax_d.legend(frameon=False, loc="lower left")

    for label, ax in zip(("(a)", "(b)", "(c)", "(d)"), axes.flat):
        style_axes(ax)
        add_panel_label(ax, label)

    fig.savefig(FIGURE_BASE.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(FIGURE_BASE.with_suffix(".png"), dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(summary.to_string(index=False))
    print(json.dumps(parameters, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
