from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "chap3" / "3.3_soa_characterization" / "3.3.1-2"
XLSX = DATA_DIR / "不同电流下的SOA，输出光功率.xlsx"
FIGURE_BASE = ROOT / "images" / "chap3_soa_current_characterization"
SUMMARY_CSV = DATA_DIR / "processed_soa_characterization_summary.csv"
STATS_JSON = DATA_DIR / "processed_soa_characterization_stats.json"

DT = 20e-9
REPETITION_HZ = 2_000.0
PERIOD_SAMPLES = round(1.0 / (REPETITION_HZ * DT))

BLUE = "#2F6B9A"
ORANGE = "#D97706"
TEAL = "#258F83"
PURPLE = "#7A5195"
GRAY = "#6B7280"
LIGHT_BLUE = "#9EC5DF"


def load_excel_data():
    ws = load_workbook(XLSX, data_only=True).active
    currents = np.array([ws.cell(r, 3).value for r in range(8, 27)], dtype=float)
    voltage_columns = (5, 7, 9, 11, 13)
    power_columns = (4, 6, 8, 10, 12)
    voltage_runs = np.array(
        [[ws.cell(r, c).value for c in voltage_columns] for r in range(8, 27)],
        dtype=float,
    )
    power_runs = np.array(
        [[ws.cell(r, c).value for c in power_columns] for r in range(8, 13)],
        dtype=float,
    )
    reverse = {
        float(ws.cell(r, 3).value): float(ws.cell(r, 5).value)
        for r in range(37, 56)
    }
    reverse_voltage = np.array([reverse[current] for current in currents])
    return currents, voltage_runs, power_runs, reverse_voltage


def fit_power_calibration(voltage_runs, power_runs):
    voltage = voltage_runs[:5].reshape(-1)
    power = power_runs.reshape(-1)
    design = np.column_stack([np.ones_like(voltage), voltage])
    intercept, slope = np.linalg.lstsq(design, power, rcond=None)[0]
    fitted = intercept + slope * voltage
    residual = power - fitted
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((power - power.mean()) ** 2))
    dof = voltage.size - 2
    residual_variance = ss_res / dof
    result = {
        "intercept_mW": float(intercept),
        "slope_mW_per_mV": float(slope),
        "r_squared": float(1.0 - ss_res / ss_tot),
        "rmse_mW": float(np.sqrt(np.mean(residual**2))),
        "degrees_of_freedom": int(dof),
        "residual_variance": float(residual_variance),
        "voltage_mean_mV": float(voltage.mean()),
        "voltage_sxx_mV2": float(np.sum((voltage - voltage.mean()) ** 2)),
        "calibration_n": int(voltage.size),
    }
    return result


def mean_calibration_ci(voltage_mV, calibration):
    x = np.asarray(voltage_mV, dtype=float)
    se = np.sqrt(
        calibration["residual_variance"]
        * (
            1.0 / calibration["calibration_n"]
            + (x - calibration["voltage_mean_mV"]) ** 2
            / calibration["voltage_sxx_mV2"]
        )
    )
    t_critical = stats.t.ppf(0.975, calibration["degrees_of_freedom"])
    return t_critical * se


def csv_name(current_mA):
    if current_mA == 200:
        return "0.2.csv"
    if current_mA == 700:
        return "0.71.csv"
    return f"{current_mA / 1000:.2f}.csv"


def read_waveform(current_mA):
    path = DATA_DIR / csv_name(int(current_mA))
    return pd.read_csv(
        path,
        skiprows=1,
        header=None,
        usecols=[0],
        dtype=np.float32,
    ).iloc[:, 0].to_numpy()


def extract_pulse_metrics(signal):
    baseline = float(np.median(signal))
    cycles = signal.size // PERIOD_SAMPLES
    cycle_view = signal[: cycles * PERIOD_SAMPLES].reshape(cycles, PERIOD_SAMPLES)
    median_amplitude = float(np.median(cycle_view.max(axis=1) - baseline))
    threshold = baseline + 0.5 * median_amplitude
    indices = np.flatnonzero(signal > threshold)
    cuts = np.flatnonzero(np.diff(indices) > 1) + 1
    groups = [group for group in np.split(indices, cuts) if group.size >= 2]
    peak_indices = np.array(
        [group[np.argmax(signal[group])] for group in groups], dtype=int
    )
    pulse_peaks = signal[peak_indices] - baseline
    widths_ns = np.array([group.size * DT * 1e9 for group in groups])
    complete = (peak_indices >= 12) & (peak_indices < signal.size - 18)
    peak_indices = peak_indices[complete]
    pulse_peaks = pulse_peaks[complete]
    widths_ns = widths_ns[complete]
    intervals_us = np.diff(peak_indices) * DT * 1e6

    traces = []
    for peak_index in peak_indices:
        trace = signal[peak_index - 12 : peak_index + 19].astype(float)
        local_baseline = np.mean(np.r_[trace[:6], trace[-6:]])
        traces.append(trace - local_baseline)
    mean_trace = np.mean(np.vstack(traces), axis=0)
    time_ns = np.arange(-12, 19) * DT * 1e9
    return {
        "pulse_count": int(pulse_peaks.size),
        "peak_mean_mV": float(pulse_peaks.mean() * 1e3),
        "peak_sd_mV": float(pulse_peaks.std(ddof=1) * 1e3),
        "peak_cv_pct": float(pulse_peaks.std(ddof=1) / pulse_peaks.mean() * 100),
        "width_mean_ns": float(widths_ns.mean()),
        "width_sd_ns": float(widths_ns.std(ddof=1)),
        "period_mean_us": float(intervals_us.mean()),
        "period_sd_us": float(intervals_us.std(ddof=1)),
        "time_ns": time_ns,
        "mean_trace_V": mean_trace,
    }


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.55, alpha=0.35)
    ax.tick_params(direction="out", length=3, width=0.8)


def add_panel_label(ax, label):
    ax.text(
        -0.14,
        1.07,
        label,
        transform=ax.transAxes,
        fontsize=9.5,
        fontweight="bold",
        va="top",
        ha="left",
    )


def main():
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.35,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )

    currents, voltage_runs, power_runs, reverse_voltage = load_excel_data()
    calibration = fit_power_calibration(voltage_runs, power_runs)
    voltage_mean = voltage_runs.mean(axis=1)
    voltage_sd = voltage_runs.std(axis=1, ddof=1)
    scan_cv = voltage_sd / voltage_mean * 100
    reverse_delta_pct = (reverse_voltage - voltage_mean) / voltage_mean * 100

    slope = calibration["slope_mW_per_mV"]
    intercept = calibration["intercept_mW"]
    converted_runs = intercept + slope * voltage_runs
    power_mean = converted_runs.mean(axis=1)
    power_sd = converted_runs.std(axis=1, ddof=1)
    direct_mean = power_runs.mean(axis=1)
    direct_sd = power_runs.std(axis=1, ddof=1)
    power_mean[:5] = direct_mean
    power_sd[:5] = direct_sd
    calibration_ci = mean_calibration_ci(voltage_mean, calibration)

    raw_metrics = {}
    representative_currents = {200, 500, 1000, 1500, 2000}
    representative_traces = {}
    for current in currents.astype(int):
        metrics = extract_pulse_metrics(read_waveform(current))
        raw_metrics[current] = metrics
        if current in representative_currents:
            representative_traces[current] = (
                metrics["time_ns"],
                metrics["mean_trace_V"],
            )

    pulse_cv = np.array([raw_metrics[int(c)]["peak_cv_pct"] for c in currents])
    pulse_width = np.array([raw_metrics[int(c)]["width_mean_ns"] for c in currents])
    pulse_width_sd = np.array([raw_metrics[int(c)]["width_sd_ns"] for c in currents])

    summary = pd.DataFrame(
        {
            "soa_current_mA": currents.astype(int),
            "bpd_peak_voltage_mean_mV": voltage_mean,
            "bpd_peak_voltage_sd_mV": voltage_sd,
            "scan_cv_pct": scan_cv,
            "reverse_peak_voltage_mV": reverse_voltage,
            "reverse_delta_pct": reverse_delta_pct,
            "peak_power_mean_mW": power_mean,
            "peak_power_sd_mW": power_sd,
            "calibration_95ci_halfwidth_mW": calibration_ci,
            "raw_complete_pulses": [raw_metrics[int(c)]["pulse_count"] for c in currents],
            "raw_peak_cv_pct": pulse_cv,
            "raw_apparent_width_mean_ns": pulse_width,
            "raw_apparent_width_sd_ns": pulse_width_sd,
            "raw_period_mean_us": [raw_metrics[int(c)]["period_mean_us"] for c in currents],
            "raw_period_sd_us": [raw_metrics[int(c)]["period_sd_us"] for c in currents],
            "power_method": ["JW8103A direct"] * 5 + ["BPD calibrated"] * 14,
        }
    )
    summary.to_csv(SUMMARY_CSV, index=False, encoding="utf-8-sig")

    stats_output = {
        "calibration": calibration,
        "fixed_attenuation_dB": 42,
        "current_range_mA": [int(currents.min()), int(currents.max())],
        "forward_scan_repeats": int(voltage_runs.shape[1]),
        "raw_complete_pulses_per_current": [
            int(min(row["pulse_count"] for row in raw_metrics.values())),
            int(max(row["pulse_count"] for row in raw_metrics.values())),
        ],
        "voltage_mean_endpoints_mV": [float(voltage_mean[0]), float(voltage_mean[-1])],
        "power_mean_endpoints_mW": [float(power_mean[0]), float(power_mean[-1])],
        "scan_cv_range_pct": [float(scan_cv.min()), float(scan_cv.max())],
        "pulse_cv_range_pct": [float(pulse_cv.min()), float(pulse_cv.max())],
        "apparent_width_range_ns": [float(pulse_width.min()), float(pulse_width.max())],
        "max_abs_reverse_delta_pct": float(np.max(np.abs(reverse_delta_pct))),
    }
    STATS_JSON.write_text(
        json.dumps(stats_output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.85), constrained_layout=True)
    ax_a, ax_b, ax_c, ax_d = axes.flat

    colors = mpl.colormaps["viridis"](np.linspace(0.12, 0.88, 5))
    for color, current in zip(colors, sorted(representative_currents)):
        time_ns, trace = representative_traces[current]
        ax_a.plot(
            time_ns,
            trace,
            color=color,
            marker="o",
            markersize=2.3,
            markeredgewidth=0,
            label=f"{current / 1000:.1f} A",
        )
    ax_a.axhline(0, color="#9CA3AF", linewidth=0.65)
    ax_a.set_xlim(-180, 300)
    ax_a.set_xlabel("Time relative to pulse peak (ns)")
    ax_a.set_ylabel("BPD output (V)")
    ax_a.legend(frameon=False, ncol=2, loc="upper right", handlelength=1.7)
    ax_a.text(
        0.03,
        0.95,
        r"$n=399$ pulses, $\Delta t=20$ ns",
        transform=ax_a.transAxes,
        ha="left",
        va="top",
        fontsize=7,
        color=GRAY,
    )

    for run in range(voltage_runs.shape[1]):
        ax_b.plot(
            currents,
            voltage_runs[:, run],
            color=LIGHT_BLUE,
            marker="o",
            markersize=2.2,
            linewidth=0.75,
            alpha=0.55,
        )
    ax_b.errorbar(
        currents,
        voltage_mean,
        yerr=voltage_sd,
        color=BLUE,
        marker="o",
        markersize=4.2,
        markeredgecolor="white",
        markeredgewidth=0.55,
        capsize=2.1,
        linewidth=1.5,
        label="Forward mean ± SD (n=5)",
        zorder=4,
    )
    ax_b.plot(
        currents,
        reverse_voltage,
        color=ORANGE,
        linestyle="--",
        marker="D",
        markerfacecolor="white",
        markeredgewidth=0.9,
        markersize=3.5,
        label="Reverse sweep",
    )
    ax_b.set_xlabel("SOA pulse current (mA)")
    ax_b.set_ylabel("BPD peak voltage (mV)")
    ax_b.set_xticks([200, 600, 1000, 1400, 1800, 2000])
    ax_b.legend(frameon=False, loc="upper left")

    jitter = np.linspace(-16, 16, power_runs.shape[1])
    for row, current in enumerate(currents[:5]):
        ax_c.scatter(
            current + jitter,
            power_runs[row],
            s=11,
            facecolor=BLUE,
            edgecolor="white",
            linewidth=0.35,
            alpha=0.58,
            zorder=2,
        )
    for row, current in enumerate(currents[5:], start=5):
        ax_c.scatter(
            current + jitter,
            converted_runs[row],
            s=12,
            facecolor="white",
            edgecolor=ORANGE,
            linewidth=0.75,
            alpha=0.72,
            zorder=2,
        )
    ax_c.plot(currents, power_mean, color="#9CA3AF", linewidth=0.8, zorder=1)
    ax_c.errorbar(
        currents[:5],
        direct_mean,
        yerr=direct_sd,
        color=BLUE,
        marker="o",
        markersize=4.4,
        markeredgecolor="white",
        markeredgewidth=0.55,
        capsize=2.2,
        linewidth=1.45,
        label="JW8103A direct (n=5)",
        zorder=4,
    )
    ax_c.fill_between(
        currents[5:],
        power_mean[5:] - calibration_ci[5:],
        power_mean[5:] + calibration_ci[5:],
        color=ORANGE,
        alpha=0.12,
        linewidth=0,
        label="Calibration 95% CI",
    )
    ax_c.errorbar(
        currents[5:],
        power_mean[5:],
        yerr=power_sd[5:],
        color=ORANGE,
        linestyle="--",
        marker="s",
        markerfacecolor="white",
        markeredgewidth=0.9,
        markersize=4.2,
        capsize=2.2,
        linewidth=1.4,
        label="BPD calibrated (n=5)",
        zorder=4,
    )
    ax_c.axvline(650, color="#9CA3AF", linewidth=0.75, linestyle=":")
    ax_c.text(
        0.97,
        0.06,
        (
            rf"$P_{{\mathrm{{peak}}}}={slope:.3f}V_{{\mathrm{{peak}}}}"
            rf"+{intercept:.2f}$"
            + "\n"
            + rf"$R^2={calibration['r_squared']:.4f}$"
        ),
        transform=ax_c.transAxes,
        ha="right",
        va="bottom",
        fontsize=7,
        color="#374151",
    )
    ax_c.set_xlabel("SOA pulse current (mA)")
    ax_c.set_ylabel("Peak optical power (mW)")
    ax_c.set_xticks([200, 600, 1000, 1400, 1800, 2000])
    ax_c.legend(frameon=False, loc="upper left", ncol=1)

    line1 = ax_d.plot(
        currents,
        scan_cv,
        color=BLUE,
        marker="o",
        markersize=3.8,
        label="Scan-to-scan CV",
    )[0]
    line2 = ax_d.plot(
        currents,
        pulse_cv,
        color=ORANGE,
        linestyle="--",
        marker="s",
        markerfacecolor="white",
        markeredgewidth=0.8,
        markersize=3.8,
        label="Pulse-to-pulse CV",
    )[0]
    ax_d.set_xlabel("SOA pulse current (mA)")
    ax_d.set_ylabel("Coefficient of variation (%)")
    ax_d.set_xticks([200, 600, 1000, 1400, 1800, 2000])
    ax_d.set_ylim(0, 5.25)
    ax_d_right = ax_d.twinx()
    line3 = ax_d_right.plot(
        currents,
        pulse_width,
        color=TEAL,
        marker="^",
        markerfacecolor="white",
        markeredgewidth=0.8,
        markersize=3.8,
        linewidth=1.15,
        label="Apparent width",
    )[0]
    ax_d_right.set_ylabel("Apparent pulse width (ns)", color=TEAL)
    ax_d_right.tick_params(axis="y", colors=TEAL, direction="out", length=3)
    ax_d_right.spines["top"].set_visible(False)
    ax_d_right.spines["right"].set_color(TEAL)
    ax_d_right.set_ylim(88, 112)
    ax_d.legend(
        [line1, line2, line3],
        ["Scan-to-scan CV", "Pulse-to-pulse CV", "Apparent width"],
        frameon=False,
        loc="upper right",
    )
    ax_d_right.text(
        0.98,
        0.07,
        r"50% threshold; $\Delta t=20$ ns",
        transform=ax_d_right.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.0,
        color=GRAY,
    )

    for label, ax in zip(("(a)", "(b)", "(c)", "(d)"), axes.flat):
        style_axes(ax)
        add_panel_label(ax, label)

    fig.savefig(FIGURE_BASE.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(FIGURE_BASE.with_suffix(".png"), dpi=600, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(stats_output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
