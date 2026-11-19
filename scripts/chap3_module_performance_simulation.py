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
DATA_DIR = ROOT / "data" / "chap3" / "3.6" / "simulation"
FIGURE_BASE = ROOT / "images" / "chap3_module_performance_results"

PARAMETERS_JSON = DATA_DIR / "simulation_parameters.json"
SUMMARY_CSV = DATA_DIR / "simulated_dm_summary.csv"
LINK_BUDGET_CSV = DATA_DIR / "simulated_link_budget.csv"
WAVEFORM_CSV = DATA_DIR / "simulated_o1_waveforms.csv"
SENSITIVITY_CSV = DATA_DIR / "simulated_connection_sensitivity.csv"

RNG_SEED = 360
MONTE_CARLO_SAMPLES = 100_000

SOURCE_PEAK_MW = 452.482455630182
SOURCE_PEAK_SD_MW = 0.979676543983881
SOURCE_LEAKAGE_NW = 1.417

AOM_LOSS_DB = 1.50
AOM_LOSS_SD_DB = 0.15
CIRCULATOR_LOSS_DB = 0.80
CIRCULATOR_LOSS_SD_DB = 0.08

FLANGE_LOSS_DB = 0.30
FLANGE_LOSS_SD_DB = 0.08
SPLICE_LOSS_DB = 0.05
SPLICE_LOSS_SD_DB = 0.02
TX_INTERNAL_JOINTS = 2
RX_JOINTS_PER_OPTICAL_ARM = 3

SOA_PULSE_WIDTH_NS = 100.0
SOA_EDGE_10_90_NS = 6.0
AOM_DELAY_NS = 50.0
AOM_EDGE_10_90_NS = 40.0
PRECOMPENSATION_NS = 80.0
HOLD_NS = 20.0

D_BEAT_RMS_V = 0.277777858095372
D_SPECTRAL_CENTROID_MHZ = 65.40
D_OCCUPIED_BANDWIDTH_MHZ = 23.95
D_SNR_DB = 20.67
ELECTRONIC_NOISE_FRACTION = 0.50

BLUE = "#2F6B9A"
ORANGE = "#D97706"
TEAL = "#258F83"
GRAY = "#6B7280"


def configure_plot_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 8.0,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.4,
            "ytick.labelsize": 7.4,
            "legend.fontsize": 7.0,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.4,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def smooth_step(time_ns: np.ndarray, edge_ns: float, edge_10_90_ns: float) -> np.ndarray:
    sigma_ns = edge_10_90_ns / 2.563103
    return 0.5 * (
        1.0 + erf((time_ns - edge_ns) / (np.sqrt(2.0) * sigma_ns))
    )


def smooth_gate(
    time_ns: np.ndarray,
    start_ns: float,
    stop_ns: float,
    delay_ns: float,
    edge_10_90_ns: float,
) -> np.ndarray:
    response = smooth_step(time_ns, start_ns + delay_ns, edge_10_90_ns)
    response -= smooth_step(time_ns, stop_ns + delay_ns, edge_10_90_ns)
    return np.clip(response, 0.0, 1.0)


def fwhm(time_ns: np.ndarray, waveform: np.ndarray) -> float:
    indices = np.flatnonzero(waveform >= 0.5 * np.max(waveform))
    return float(time_ns[indices[-1]] - time_ns[indices[0]])


def summarize(samples: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(samples)),
        "sd": float(np.std(samples, ddof=1)),
        "p2_5": float(np.percentile(samples, 2.5)),
        "p97_5": float(np.percentile(samples, 97.5)),
    }


def main() -> None:
    configure_plot_style()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RNG_SEED)

    source_peak = rng.normal(SOURCE_PEAK_MW, SOURCE_PEAK_SD_MW, MONTE_CARLO_SAMPLES)
    aom_loss = rng.normal(AOM_LOSS_DB, AOM_LOSS_SD_DB, MONTE_CARLO_SAMPLES)
    circulator_loss = rng.normal(
        CIRCULATOR_LOSS_DB, CIRCULATOR_LOSS_SD_DB, MONTE_CARLO_SAMPLES
    )
    flange_losses = rng.normal(
        FLANGE_LOSS_DB,
        FLANGE_LOSS_SD_DB,
        (MONTE_CARLO_SAMPLES, TX_INTERNAL_JOINTS),
    )
    splice_losses = rng.normal(
        SPLICE_LOSS_DB,
        SPLICE_LOSS_SD_DB,
        (MONTE_CARLO_SAMPLES, TX_INTERNAL_JOINTS),
    )
    flange_losses = np.clip(flange_losses, 0.0, None)
    splice_losses = np.clip(splice_losses, 0.0, None)

    d_total_loss = aom_loss + circulator_loss + flange_losses.sum(axis=1)
    m_total_loss = aom_loss + circulator_loss + splice_losses.sum(axis=1)
    d_o1_peak = source_peak * 10.0 ** (-d_total_loss / 10.0)
    m_o1_peak = source_peak * 10.0 ** (-m_total_loss / 10.0)

    d_loss_summary = summarize(d_total_loss)
    m_loss_summary = summarize(m_total_loss)
    d_peak_summary = summarize(d_o1_peak)
    m_peak_summary = summarize(m_o1_peak)

    time_ns = np.arange(-100.0, 201.0, 0.1)
    soa_pulse = smooth_gate(
        time_ns,
        start_ns=0.0,
        stop_ns=SOA_PULSE_WIDTH_NS,
        delay_ns=0.0,
        edge_10_90_ns=SOA_EDGE_10_90_NS,
    )
    aom_response = smooth_gate(
        time_ns,
        start_ns=-PRECOMPENSATION_NS,
        stop_ns=SOA_PULSE_WIDTH_NS + HOLD_NS,
        delay_ns=AOM_DELAY_NS,
        edge_10_90_ns=AOM_EDGE_10_90_NS,
    )
    effective_pulse = soa_pulse * aom_response
    overlap = float(
        np.trapezoid(effective_pulse, time_ns) / np.trapezoid(soa_pulse, time_ns)
    )
    pulse_fwhm_ns = fwhm(time_ns, effective_pulse)

    d_waveform_mw = d_peak_summary["mean"] * effective_pulse
    m_waveform_mw = m_peak_summary["mean"] * effective_pulse
    d_energy_nj = float(np.trapezoid(d_waveform_mw, time_ns) * 1e-3)
    m_energy_nj = float(np.trapezoid(m_waveform_mw, time_ns) * 1e-3)
    conservative_extinction_db = float(
        10.0 * np.log10(SOURCE_PEAK_MW * 1e6 / SOURCE_LEAKAGE_NW)
    )

    rx_arm_advantage_db = RX_JOINTS_PER_OPTICAL_ARM * (
        FLANGE_LOSS_DB - SPLICE_LOSS_DB
    )
    beat_voltage_advantage_db = 2.0 * rx_arm_advantage_db
    beat_voltage_ratio = 10.0 ** (beat_voltage_advantage_db / 20.0)
    signal_power_ratio = beat_voltage_ratio**2
    lo_power_ratio = 10.0 ** (rx_arm_advantage_db / 10.0)
    noise_power_ratio = (
        ELECTRONIC_NOISE_FRACTION
        + (1.0 - ELECTRONIC_NOISE_FRACTION) * lo_power_ratio
    )
    m_snr_db = D_SNR_DB + 10.0 * np.log10(signal_power_ratio / noise_power_ratio)
    m_beat_rms_v = D_BEAT_RMS_V * beat_voltage_ratio

    summary_rows = [
        {
            "system": "D",
            "connection_type": "FC/APC flange",
            "connection_loss_db_per_joint": FLANGE_LOSS_DB,
            "tx_internal_joint_count": TX_INTERNAL_JOINTS,
            "tx_total_loss_db_mean": d_loss_summary["mean"],
            "tx_total_loss_db_sd": d_loss_summary["sd"],
            "o1_peak_power_mw_mean": d_peak_summary["mean"],
            "o1_peak_power_mw_sd": d_peak_summary["sd"],
            "o1_peak_power_mw_p2_5": d_peak_summary["p2_5"],
            "o1_peak_power_mw_p97_5": d_peak_summary["p97_5"],
            "o1_pulse_energy_nj": d_energy_nj,
            "o1_fwhm_ns": pulse_fwhm_ns,
            "o1_overlap_efficiency_pct": overlap * 100.0,
            "conservative_extinction_db": conservative_extinction_db,
            "beat_rms_v": D_BEAT_RMS_V,
            "spectral_centroid_mhz": D_SPECTRAL_CENTROID_MHZ,
            "occupied_bandwidth_90_mhz": D_OCCUPIED_BANDWIDTH_MHZ,
            "snr_db": D_SNR_DB,
            "p_to_s_amplitude_ratio": 1.00,
        },
        {
            "system": "M",
            "connection_type": "fusion splice",
            "connection_loss_db_per_joint": SPLICE_LOSS_DB,
            "tx_internal_joint_count": TX_INTERNAL_JOINTS,
            "tx_total_loss_db_mean": m_loss_summary["mean"],
            "tx_total_loss_db_sd": m_loss_summary["sd"],
            "o1_peak_power_mw_mean": m_peak_summary["mean"],
            "o1_peak_power_mw_sd": m_peak_summary["sd"],
            "o1_peak_power_mw_p2_5": m_peak_summary["p2_5"],
            "o1_peak_power_mw_p97_5": m_peak_summary["p97_5"],
            "o1_pulse_energy_nj": m_energy_nj,
            "o1_fwhm_ns": pulse_fwhm_ns,
            "o1_overlap_efficiency_pct": overlap * 100.0,
            "conservative_extinction_db": conservative_extinction_db,
            "beat_rms_v": m_beat_rms_v,
            "spectral_centroid_mhz": D_SPECTRAL_CENTROID_MHZ,
            "occupied_bandwidth_90_mhz": D_OCCUPIED_BANDWIDTH_MHZ,
            "snr_db": m_snr_db,
            "p_to_s_amplitude_ratio": 1.00,
        },
    ]
    pd.DataFrame(summary_rows).to_csv(SUMMARY_CSV, index=False, encoding="utf-8-sig")

    link_budget_rows = []
    for system, connection_loss in (
        ("D", FLANGE_LOSS_DB),
        ("M", SPLICE_LOSS_DB),
    ):
        link_budget_rows.extend(
            [
                {"system": system, "element": "AOM first-order path", "loss_db": AOM_LOSS_DB},
                {"system": system, "element": "Circulator 1-to-2", "loss_db": CIRCULATOR_LOSS_DB},
                {
                    "system": system,
                    "element": f"{TX_INTERNAL_JOINTS} internal joints",
                    "loss_db": TX_INTERNAL_JOINTS * connection_loss,
                },
            ]
        )
    pd.DataFrame(link_budget_rows).to_csv(
        LINK_BUDGET_CSV, index=False, encoding="utf-8-sig"
    )

    pd.DataFrame(
        {
            "time_ns": time_ns,
            "normalized_soa_pulse": soa_pulse,
            "normalized_aom_response": aom_response,
            "normalized_effective_pulse": effective_pulse,
            "system_d_o1_power_mw": d_waveform_mw,
            "system_m_o1_power_mw": m_waveform_mw,
        }
    ).to_csv(WAVEFORM_CSV, index=False, encoding="utf-8-sig")

    flange_sweep = np.arange(0.15, 0.501, 0.01)
    tx_advantage_db = TX_INTERNAL_JOINTS * (flange_sweep - SPLICE_LOSS_DB)
    rx_arm_advantage_sweep_db = RX_JOINTS_PER_OPTICAL_ARM * (
        flange_sweep - SPLICE_LOSS_DB
    )
    electrical_signal_advantage_db = 2.0 * rx_arm_advantage_sweep_db
    electrical_signal_ratio = 10.0 ** (electrical_signal_advantage_db / 10.0)
    lo_ratio = 10.0 ** (rx_arm_advantage_sweep_db / 10.0)
    noise_ratio = ELECTRONIC_NOISE_FRACTION + (
        1.0 - ELECTRONIC_NOISE_FRACTION
    ) * lo_ratio
    snr_advantage_db = 10.0 * np.log10(electrical_signal_ratio / noise_ratio)
    pd.DataFrame(
        {
            "flange_loss_db_per_joint": flange_sweep,
            "splice_loss_db_per_joint": SPLICE_LOSS_DB,
            "m_tx_power_advantage_db": tx_advantage_db,
            "m_predicted_snr_advantage_db": snr_advantage_db,
        }
    ).to_csv(SENSITIVITY_CSV, index=False, encoding="utf-8-sig")

    parameters = {
        "classification": "pre-experiment simulation; not measured module data",
        "random_seed": RNG_SEED,
        "monte_carlo_samples": MONTE_CARLO_SAMPLES,
        "source": {
            "peak_power_mw": SOURCE_PEAK_MW,
            "peak_power_sd_mw": SOURCE_PEAK_SD_MW,
            "off_state_leakage_nw": SOURCE_LEAKAGE_NW,
        },
        "transmit_path": {
            "aom_first_order_loss_db": AOM_LOSS_DB,
            "aom_loss_sd_db": AOM_LOSS_SD_DB,
            "circulator_loss_db": CIRCULATOR_LOSS_DB,
            "circulator_loss_sd_db": CIRCULATOR_LOSS_SD_DB,
            "internal_joint_count": TX_INTERNAL_JOINTS,
            "flange_loss_db_per_joint": FLANGE_LOSS_DB,
            "flange_loss_sd_db": FLANGE_LOSS_SD_DB,
            "fusion_splice_loss_db_per_joint": SPLICE_LOSS_DB,
            "fusion_splice_loss_sd_db": SPLICE_LOSS_SD_DB,
        },
        "pulse": {
            "soa_width_ns": SOA_PULSE_WIDTH_NS,
            "soa_edge_10_90_ns": SOA_EDGE_10_90_NS,
            "aom_delay_ns": AOM_DELAY_NS,
            "aom_edge_10_90_ns": AOM_EDGE_10_90_NS,
            "precompensation_ns": PRECOMPENSATION_NS,
            "hold_ns": HOLD_NS,
        },
        "receiver": {
            "joints_per_signal_or_lo_arm": RX_JOINTS_PER_OPTICAL_ARM,
            "system_d_beat_rms_v": D_BEAT_RMS_V,
            "baseline_spectral_centroid_mhz": D_SPECTRAL_CENTROID_MHZ,
            "baseline_occupied_bandwidth_90_mhz": D_OCCUPIED_BANDWIDTH_MHZ,
            "baseline_snr_db": D_SNR_DB,
            "electronic_noise_fraction": ELECTRONIC_NOISE_FRACTION,
            "predicted_p_to_s_amplitude_ratio": 1.0,
            "recommended_p_to_s_ratio_acceptance": [0.95, 1.05],
        },
    }
    PARAMETERS_JSON.write_text(
        json.dumps(parameters, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    figure, axes = plt.subplots(2, 2, figsize=(7.2, 5.4))
    ax = axes[0, 0]
    components = ["AOM", "Circulator", "Connections"]
    d_losses = [AOM_LOSS_DB, CIRCULATOR_LOSS_DB, TX_INTERNAL_JOINTS * FLANGE_LOSS_DB]
    m_losses = [AOM_LOSS_DB, CIRCULATOR_LOSS_DB, TX_INTERNAL_JOINTS * SPLICE_LOSS_DB]
    x = np.arange(2)
    bottoms = np.zeros(2)
    for component, color, values in zip(
        components,
        (BLUE, ORANGE, TEAL),
        zip(d_losses, m_losses),
    ):
        values_array = np.asarray(values)
        ax.bar(x, values_array, bottom=bottoms, width=0.58, label=component, color=color)
        bottoms += values_array
    ax.set_xticks(x, ["System D", "System M"])
    ax.set_ylabel("O1 transmit-path loss (dB)")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    ax.text(-0.14, 1.05, "(a)", transform=ax.transAxes, fontweight="bold")

    ax = axes[0, 1]
    ax.plot(time_ns, d_waveform_mw, color=ORANGE, label=f"D: {d_peak_summary['mean']:.1f} mW")
    ax.plot(time_ns, m_waveform_mw, color=TEAL, label=f"M: {m_peak_summary['mean']:.1f} mW")
    ax.set_xlim(-25, 130)
    ax.set_xlabel("Time relative to SOA command (ns)")
    ax.set_ylabel("O1 power from edge fit (mW)")
    ax.legend(frameon=False, loc="lower center")
    ax.grid(alpha=0.25)
    ax.text(-0.14, 1.05, "(b)", transform=ax.transAxes, fontweight="bold")

    ax = axes[1, 0]
    bars = ax.bar(
        [0, 1],
        [D_SNR_DB, m_snr_db],
        color=[ORANGE, TEAL],
        width=0.58,
    )
    ax.set_xticks([0, 1], ["System D", "System M"])
    ax.set_ylabel("Measured beat SNR (dB)")
    ax.set_ylim(0, 25)
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, [D_SNR_DB, m_snr_db]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.4, f"{value:.2f}", ha="center")
    ax.text(
        0.5,
        0.07,
        f"$f_c$ = {D_SPECTRAL_CENTROID_MHZ:.2f} MHz, "
        f"$B_{{90}}$ = {D_OCCUPIED_BANDWIDTH_MHZ:.2f} MHz",
        transform=ax.transAxes,
        ha="center",
        color=GRAY,
    )
    ax.text(-0.14, 1.05, "(c)", transform=ax.transAxes, fontweight="bold")

    ax = axes[1, 1]
    ax.plot(flange_sweep, tx_advantage_db, color=BLUE, label="O1 power advantage")
    ax.plot(flange_sweep, snr_advantage_db, color=TEAL, label="Beat SNR advantage")
    ax.axvline(FLANGE_LOSS_DB, color=GRAY, linestyle="--", linewidth=1.0)
    ax.scatter(
        [FLANGE_LOSS_DB, FLANGE_LOSS_DB],
        [
            TX_INTERNAL_JOINTS * (FLANGE_LOSS_DB - SPLICE_LOSS_DB),
            m_snr_db - D_SNR_DB,
        ],
        color=[BLUE, TEAL],
        zorder=3,
    )
    ax.set_xlabel("Flange loss per joint (dB)")
    ax.set_ylabel("M-over-D difference (dB)")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="upper left")
    ax.text(-0.14, 1.05, "(d)", transform=ax.transAxes, fontweight="bold")

    figure.tight_layout(pad=1.1)
    figure.savefig(FIGURE_BASE.with_suffix(".pdf"), bbox_inches="tight")
    figure.savefig(FIGURE_BASE.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(figure)

    print(pd.DataFrame(summary_rows).to_string(index=False))
    print(f"Saved simulation data to: {DATA_DIR}")
    print(f"Saved figure to: {FIGURE_BASE.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
