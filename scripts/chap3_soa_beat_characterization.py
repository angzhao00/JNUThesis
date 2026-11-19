from __future__ import annotations

import json
import struct
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import welch


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "chap3" / "3.3_soa_characterization" / "3.3.3"
FILE_METRICS_CSV = DATA_DIR / "processed_soa_beat_file_metrics.csv"
SUMMARY_CSV = DATA_DIR / "processed_soa_beat_summary.csv"
CONTROL_CSV = DATA_DIR / "processed_soa_beat_controls.csv"
STATS_JSON = DATA_DIR / "processed_soa_beat_stats.json"
FIGURE_BASE = ROOT / "images" / "chap3_soa_beat_characterization"
CONTROL_FIGURE_BASE = ROOT / "images" / "chap3_soa_beat_controls"

HEADER_BYTES = 172
EXPECTED_MAGIC = b"RG03"
EXPECTED_SAMPLE_INTERVAL_S = 0.5e-9
REPETITION_HZ = 2_000.0
SIGNAL_WINDOW_US = (0.0, 150.0)
NOISE_WINDOW_US = (300.0, 450.0)
ANALYSIS_BAND_MHZ = (40.0, 120.0)
WELCH_SEGMENT_SAMPLES = 32_768
SPECTRAL_SMOOTHING_MHZ = 0.5
ENVELOPE_BIN_US = 5.0

CURRENT_RUNS = [
    {
        "run_id": 1,
        "direction": "forward",
        "directory": "SOA 2KHZ 脉宽100ns-第一次",
    },
    {
        "run_id": 2,
        "direction": "reverse",
        "directory": "SOA 2KHZ 脉宽100ns-第二次-反向扫描",
    },
    {
        "run_id": 3,
        "direction": "forward",
        "directory": "SOA 2KHZ 脉宽100ns-第三次",
    },
]

WIDTH_RUNS = [
    {
        "run_id": 1,
        "direction": "forward",
        "directory": "SOA 2KHZ 1.6A-不同脉宽-第一次",
        "files": {width: f"{width}.bin" for width in (50, 100, 150, 200, 250)},
    },
    {
        "run_id": 2,
        "direction": "reverse",
        "directory": "SOA 2KHZ 1.6A-不同脉宽-第二次-反向扫描",
        "files": {width: f"{width}.bin" for width in (50, 100, 150, 200, 250)},
    },
    {
        "run_id": 3,
        "direction": "forward",
        "directory": "SOA 2KHZ 1.6A-不同脉宽 - 第三次",
        "files": {width: f"{width}.bin" for width in (50, 100, 150, 200, 250)},
    },
]

CONTROLS = [
    {
        "control": "BPD blocked, AOM RF off",
        "directory": "暗态对照-BPD遮光-AOM关闭",
        "file": "1.bin",
    },
    {
        "control": "BPD blocked, AOM RF on",
        "directory": "暗态对照-BPD遮光-AOM开启",
        "file": "1.bin",
    },
    {
        "control": "Optical path connected, AOM RF off",
        "directory": "射频对照-AOM射频驱动关闭",
        "file": "1.bin",
    },
]

BLUE = "#2F6B9A"
ORANGE = "#D97706"
TEAL = "#258F83"
PURPLE = "#7A5195"
GRAY = "#6B7280"
LIGHT_BLUE = "#9EC5DF"


def read_header(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        header = handle.read(HEADER_BYTES)
    if len(header) != HEADER_BYTES or header[:4] != EXPECTED_MAGIC:
        raise ValueError(f"Unsupported waveform header: {path}")

    point_count = struct.unpack_from("<I", header, 28)[0]
    sample_interval_s = struct.unpack_from("<d", header, 48)[0]
    expected_size = HEADER_BYTES + point_count * np.dtype("<f4").itemsize
    if path.stat().st_size != expected_size:
        raise ValueError(
            f"Waveform size mismatch for {path}: "
            f"expected {expected_size}, received {path.stat().st_size}"
        )
    if not np.isclose(sample_interval_s, EXPECTED_SAMPLE_INTERVAL_S, rtol=1e-6):
        raise ValueError(f"Unexpected sample interval in {path}: {sample_interval_s}")

    return {
        "point_count": point_count,
        "sample_interval_s": sample_interval_s,
        "sample_rate_Hz": 1.0 / sample_interval_s,
        "vertical_scale_header": struct.unpack_from("<f", header, 36)[0],
        "channel": header[128:144].split(b"\0")[0].decode(errors="replace"),
        "scope": header[104:128].split(b"\0")[0].decode(errors="replace"),
        "acquisition_date": header[72:88].split(b"\0")[0].decode(errors="replace"),
        "acquisition_time": header[88:104].split(b"\0")[0].decode(errors="replace"),
    }


def waveform_frames(path: Path) -> tuple[np.memmap, dict[str, object]]:
    header = read_header(path)
    sample_rate_hz = float(header["sample_rate_Hz"])
    samples_per_frame = round(sample_rate_hz / REPETITION_HZ)
    point_count = int(header["point_count"])
    if point_count % samples_per_frame:
        raise ValueError(
            f"Point count is not an integer number of 2 kHz frames: {path}"
        )
    waveform = np.memmap(
        path,
        dtype="<f4",
        mode="r",
        offset=HEADER_BYTES,
        shape=(point_count,),
    )
    frames = waveform.reshape(point_count // samples_per_frame, samples_per_frame)
    return frames, header


def window_indices(window_us: tuple[float, float], sample_rate_hz: float) -> slice:
    start = round(window_us[0] * 1e-6 * sample_rate_hz)
    stop = round(window_us[1] * 1e-6 * sample_rate_hz)
    return slice(start, stop)


def spectrum(signal: np.ndarray, sample_rate_hz: float) -> tuple[np.ndarray, np.ndarray]:
    frequency, density = welch(
        signal,
        fs=sample_rate_hz,
        window="hann",
        nperseg=WELCH_SEGMENT_SAMPLES,
        noverlap=0,
        detrend="constant",
        scaling="density",
    )
    return frequency, density


def spectral_metrics(
    frequency: np.ndarray,
    signal_psd: np.ndarray,
    noise_psd: np.ndarray,
) -> dict[str, float]:
    low_hz, high_hz = (value * 1e6 for value in ANALYSIS_BAND_MHZ)
    band = (frequency >= low_hz) & (frequency <= high_hz)
    band_frequency = frequency[band]
    signal_band = signal_psd[band]
    noise_band = noise_psd[band]
    excess = np.maximum(signal_band - noise_band, 0.0)
    if not np.any(excess > 0):
        return {
            "smoothed_peak_frequency_MHz": float("nan"),
            "spectral_centroid_MHz": float("nan"),
            "occupied_bandwidth_90_MHz": float("nan"),
            "band_power_ratio_dB": float(
                10.0 * np.log10(signal_band.sum() / noise_band.sum())
            ),
        }

    bin_width_hz = frequency[1] - frequency[0]
    sigma_bins = max(
        1, round(SPECTRAL_SMOOTHING_MHZ * 1e6 / bin_width_hz)
    )
    smoothed = gaussian_filter1d(excess, sigma_bins)
    smoothed_peak_hz = band_frequency[int(np.argmax(smoothed))]
    centroid_hz = float(np.sum(band_frequency * excess) / np.sum(excess))
    cumulative = np.cumsum(excess)
    five_hz = band_frequency[np.searchsorted(cumulative, 0.05 * cumulative[-1])]
    ninety_five_hz = band_frequency[
        np.searchsorted(cumulative, 0.95 * cumulative[-1])
    ]
    return {
        "smoothed_peak_frequency_MHz": float(smoothed_peak_hz / 1e6),
        "spectral_centroid_MHz": float(centroid_hz / 1e6),
        "occupied_bandwidth_90_MHz": float((ninety_five_hz - five_hz) / 1e6),
        "band_power_ratio_dB": float(
            10.0 * np.log10(signal_band.sum() / noise_band.sum())
        ),
    }


def analyze_waveform(path: Path) -> tuple[dict[str, object], dict[str, np.ndarray]]:
    frames, header = waveform_frames(path)
    sample_rate_hz = float(header["sample_rate_Hz"])
    signal_slice = window_indices(SIGNAL_WINDOW_US, sample_rate_hz)
    noise_slice = window_indices(NOISE_WINDOW_US, sample_rate_hz)

    signal_psds = []
    noise_psds = []
    frame_metrics = []
    signal_sum_squares = 0.0
    noise_sum_squares = 0.0
    signal_count = 0
    noise_count = 0
    raw_min = np.inf
    raw_max = -np.inf
    raw_min_count = 0
    raw_max_count = 0

    for frame in frames:
        signal = np.asarray(frame[signal_slice], dtype=np.float64)
        noise = np.asarray(frame[noise_slice], dtype=np.float64)
        signal_centered = signal - signal.mean()
        noise_centered = noise - noise.mean()
        frequency, signal_psd = spectrum(signal, sample_rate_hz)
        _, noise_psd = spectrum(noise, sample_rate_hz)
        signal_psds.append(signal_psd)
        noise_psds.append(noise_psd)

        frame_spectral = spectral_metrics(frequency, signal_psd, noise_psd)
        signal_variance = float(np.var(signal))
        noise_variance = float(np.var(noise))
        signal_to_noise = max(signal_variance / noise_variance - 1.0, 1e-12)
        frame_metrics.append(
            {
                **frame_spectral,
                "time_domain_snr_dB": float(10.0 * np.log10(signal_to_noise)),
            }
        )
        signal_sum_squares += float(np.sum(signal_centered**2))
        noise_sum_squares += float(np.sum(noise_centered**2))
        signal_count += signal.size
        noise_count += noise.size

        frame_min = float(signal.min())
        frame_max = float(signal.max())
        if frame_min < raw_min:
            raw_min = frame_min
            raw_min_count = int(np.count_nonzero(signal == frame_min))
        elif frame_min == raw_min:
            raw_min_count += int(np.count_nonzero(signal == frame_min))
        if frame_max > raw_max:
            raw_max = frame_max
            raw_max_count = int(np.count_nonzero(signal == frame_max))
        elif frame_max == raw_max:
            raw_max_count += int(np.count_nonzero(signal == frame_max))

    mean_signal_psd = np.mean(np.stack(signal_psds), axis=0)
    mean_noise_psd = np.mean(np.stack(noise_psds), axis=0)
    pooled_spectral = spectral_metrics(frequency, mean_signal_psd, mean_noise_psd)
    signal_variance = signal_sum_squares / signal_count
    noise_variance = noise_sum_squares / noise_count
    time_domain_snr = max(signal_variance / noise_variance - 1.0, 1e-12)
    frame_table = pd.DataFrame(frame_metrics)
    record_duration_s = int(header["point_count"]) / sample_rate_hz

    metrics: dict[str, object] = {
        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
        "channel": header["channel"],
        "scope": header["scope"],
        "acquisition_date": header["acquisition_date"],
        "acquisition_time": header["acquisition_time"],
        "sample_rate_GSa_s": sample_rate_hz / 1e9,
        "point_count": int(header["point_count"]),
        "record_duration_ms": record_duration_s * 1e3,
        "frame_count": int(len(frames)),
        **pooled_spectral,
        "time_domain_snr_dB": float(10.0 * np.log10(time_domain_snr)),
        "signal_rms_raw": float(np.sqrt(signal_variance)),
        "noise_rms_raw": float(np.sqrt(noise_variance)),
        "frame_centroid_sd_MHz": float(
            frame_table["spectral_centroid_MHz"].std(ddof=1)
        ),
        "frame_snr_sd_dB": float(frame_table["time_domain_snr_dB"].std(ddof=1)),
        "signal_min_raw": raw_min,
        "signal_max_raw": raw_max,
        "extreme_sample_fraction": float(
            (raw_min_count + raw_max_count) / signal_count
        ),
    }
    spectra = {
        "frequency_Hz": frequency,
        "signal_psd": mean_signal_psd,
        "noise_psd": mean_noise_psd,
        "excess_psd": np.maximum(mean_signal_psd - mean_noise_psd, 0.0),
    }
    return metrics, spectra


def summarize_runs(file_metrics: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "smoothed_peak_frequency_MHz",
        "spectral_centroid_MHz",
        "occupied_bandwidth_90_MHz",
        "time_domain_snr_dB",
        "band_power_ratio_dB",
        "signal_rms_raw",
        "noise_rms_raw",
        "frame_centroid_sd_MHz",
        "frame_snr_sd_dB",
    ]
    rows = []
    for (experiment, value, unit), group in file_metrics.groupby(
        ["experiment", "condition_value", "condition_unit"], sort=True
    ):
        row = {
            "experiment": experiment,
            "condition_value": float(value),
            "condition_unit": unit,
            "run_count": int(len(group)),
            "frame_count_total": int(group["frame_count"].sum()),
        }
        for field in fields:
            values = group[field].to_numpy(float)
            row[f"{field}_mean"] = float(values.mean())
            row[f"{field}_sd"] = float(values.std(ddof=1))
        rows.append(row)
    return pd.DataFrame(rows).sort_values(
        ["experiment", "condition_value"]
    ).reset_index(drop=True)


def style_axes(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.55, alpha=0.35)
    ax.tick_params(direction="out", length=3, width=0.8)


def add_panel_label(ax: plt.Axes, label: str) -> None:
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


def configure_plot_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 7.6,
            "axes.labelsize": 8.3,
            "xtick.labelsize": 7.1,
            "ytick.labelsize": 7.1,
            "legend.fontsize": 6.7,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.25,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def averaged_spectrum(
    spectra: dict[tuple[str, int, float], dict[str, np.ndarray]],
    experiment: str,
    condition_value: float,
) -> tuple[np.ndarray, np.ndarray]:
    matching = [
        spectrum_data["excess_psd"]
        for (kind, _, value), spectrum_data in spectra.items()
        if kind == experiment and value == condition_value
    ]
    frequency = next(iter(spectra.values()))["frequency_Hz"]
    return frequency, np.mean(np.stack(matching), axis=0)


def plot_characterization(
    file_metrics: pd.DataFrame,
    summary: pd.DataFrame,
    spectra: dict[tuple[str, int, float], dict[str, np.ndarray]],
) -> None:
    configure_plot_style()
    fig, axes = plt.subplots(2, 3, figsize=(7.25, 5.15), constrained_layout=True)

    selections = {
        "current": [400, 800, 1200, 1600, 1800],
        "pulse_width": [50, 100, 150, 200, 250],
    }
    colors = mpl.colormaps["viridis"](np.linspace(0.12, 0.88, 5))

    for row, experiment in enumerate(("current", "pulse_width")):
        ax_spectrum, ax_frequency, ax_snr = axes[row]
        values = selections[experiment]
        for color, value in zip(colors, values):
            frequency, excess = averaged_spectrum(spectra, experiment, value)
            band = (
                (frequency >= ANALYSIS_BAND_MHZ[0] * 1e6)
                & (frequency <= ANALYSIS_BAND_MHZ[1] * 1e6)
            )
            density = excess[band]
            normalized_db = 10.0 * np.log10(
                np.maximum(density / density.max(), 1e-5)
            )
            label = f"{value / 1000:.1f} A" if experiment == "current" else f"{int(value)} ns"
            ax_spectrum.plot(
                frequency[band][::2] / 1e6,
                normalized_db[::2],
                color=color,
                label=label,
            )
        ax_spectrum.set_xlim(*ANALYSIS_BAND_MHZ)
        ax_spectrum.set_ylim(-35, 2)
        ax_spectrum.set_xlabel("Frequency (MHz)")
        ax_spectrum.set_ylabel("Normalized excess PSD (dB)")
        ax_spectrum.legend(frameon=False, ncol=2, loc="lower left")

        experiment_files = file_metrics[file_metrics["experiment"] == experiment]
        experiment_summary = summary[summary["experiment"] == experiment]
        x = experiment_summary["condition_value"].to_numpy(float)
        x_plot = x / 1000.0 if experiment == "current" else x
        for run_id, run in experiment_files.groupby("run_id"):
            run = run.sort_values("condition_value")
            run_x = run["condition_value"].to_numpy(float)
            if experiment == "current":
                run_x = run_x / 1000.0
            ax_frequency.plot(
                run_x,
                run["spectral_centroid_MHz"],
                color=LIGHT_BLUE,
                marker="o",
                markersize=2.4,
                linewidth=0.75,
                alpha=0.65,
            )
        centroid = experiment_summary["spectral_centroid_MHz_mean"].to_numpy(float)
        centroid_sd = experiment_summary["spectral_centroid_MHz_sd"].to_numpy(float)
        bandwidth = experiment_summary[
            "occupied_bandwidth_90_MHz_mean"
        ].to_numpy(float)
        bandwidth_sd = experiment_summary[
            "occupied_bandwidth_90_MHz_sd"
        ].to_numpy(float)
        line_centroid = ax_frequency.errorbar(
            x_plot,
            centroid,
            yerr=centroid_sd,
            color=BLUE,
            marker="o",
            markersize=4.0,
            markeredgecolor="white",
            markeredgewidth=0.5,
            capsize=2.0,
            label="Spectral centroid",
            zorder=4,
        )
        ax_frequency.set_ylabel("Spectral centroid (MHz)", color=BLUE)
        ax_frequency.tick_params(axis="y", colors=BLUE)
        ax_frequency_right = ax_frequency.twinx()
        line_bandwidth = ax_frequency_right.errorbar(
            x_plot,
            bandwidth,
            yerr=bandwidth_sd,
            color=ORANGE,
            linestyle="--",
            marker="s",
            markerfacecolor="white",
            markersize=3.8,
            capsize=2.0,
            label="90% occupied bandwidth",
        )
        ax_frequency_right.set_ylabel("90% occupied bandwidth (MHz)", color=ORANGE)
        ax_frequency_right.tick_params(axis="y", colors=ORANGE, direction="out", length=3)
        ax_frequency_right.spines["top"].set_visible(False)
        ax_frequency_right.spines["right"].set_color(ORANGE)
        ax_frequency.legend(
            [line_centroid, line_bandwidth],
            ["Spectral centroid", "90% occupied bandwidth"],
            frameon=False,
            loc="best",
        )

        snr = experiment_summary["time_domain_snr_dB_mean"].to_numpy(float)
        snr_sd = experiment_summary["time_domain_snr_dB_sd"].to_numpy(float)
        frame_sd = experiment_summary["frame_centroid_sd_MHz_mean"].to_numpy(float)
        frame_sd_error = experiment_summary["frame_centroid_sd_MHz_sd"].to_numpy(float)
        line_snr = ax_snr.errorbar(
            x_plot,
            snr,
            yerr=snr_sd,
            color=TEAL,
            marker="o",
            markersize=4.0,
            markeredgecolor="white",
            markeredgewidth=0.5,
            capsize=2.0,
            label="SNR",
        )
        ax_snr.set_ylabel("Time-domain SNR (dB)", color=TEAL)
        ax_snr.tick_params(axis="y", colors=TEAL)
        ax_snr_right = ax_snr.twinx()
        line_stability = ax_snr_right.errorbar(
            x_plot,
            frame_sd,
            yerr=frame_sd_error,
            color=PURPLE,
            linestyle="--",
            marker="D",
            markerfacecolor="white",
            markersize=3.6,
            capsize=2.0,
            label="Frame centroid SD",
        )
        ax_snr_right.set_ylabel("Frame centroid SD (MHz)", color=PURPLE)
        ax_snr_right.tick_params(axis="y", colors=PURPLE, direction="out", length=3)
        ax_snr_right.spines["top"].set_visible(False)
        ax_snr_right.spines["right"].set_color(PURPLE)
        ax_snr.legend(
            [line_snr, line_stability],
            ["SNR", "Frame centroid SD"],
            frameon=False,
            loc="best",
        )

        x_label = "SOA pulse current (A)" if experiment == "current" else "SOA pulse width (ns)"
        ax_frequency.set_xlabel(x_label)
        ax_snr.set_xlabel(x_label)
        if experiment == "current":
            ticks = [0.4, 0.8, 1.2, 1.6, 1.8]
            ax_frequency.set_xticks(ticks)
            ax_snr.set_xticks(ticks)
        else:
            ax_frequency.set_xticks(values)
            ax_snr.set_xticks(values)

    for label, ax in zip(("(a)", "(b)", "(c)", "(d)", "(e)", "(f)"), axes.flat):
        style_axes(ax)
        add_panel_label(ax, label)

    fig.savefig(FIGURE_BASE.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(FIGURE_BASE.with_suffix(".png"), dpi=600, bbox_inches="tight")
    plt.close(fig)


def rms_envelope(path: Path) -> tuple[np.ndarray, np.ndarray]:
    frames, header = waveform_frames(path)
    sample_rate_hz = float(header["sample_rate_Hz"])
    samples_per_bin = round(ENVELOPE_BIN_US * 1e-6 * sample_rate_hz)
    usable = frames.shape[1] // samples_per_bin * samples_per_bin
    blocks = np.asarray(frames[:, :usable], dtype=np.float32).reshape(
        len(frames), -1, samples_per_bin
    )
    centered = blocks - blocks.mean(axis=2, keepdims=True)
    envelope = np.sqrt(np.mean(centered.astype(np.float64) ** 2, axis=2)).mean(axis=0)
    time_us = (np.arange(envelope.size) + 0.5) * ENVELOPE_BIN_US
    return time_us, envelope


def plot_controls(
    control_metrics: pd.DataFrame,
    control_spectra: dict[str, dict[str, np.ndarray]],
    active_path: Path,
    active_spectrum: dict[str, np.ndarray],
) -> None:
    configure_plot_style()
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.25, 2.8), constrained_layout=True)
    colors = {
        "Active: 1.6 A, 100 ns": BLUE,
        "BPD blocked, AOM RF off": GRAY,
        "BPD blocked, AOM RF on": ORANGE,
        "Optical path connected, AOM RF off": TEAL,
    }

    envelope_paths = {
        "Active: 1.6 A, 100 ns": active_path,
        **{
            control["control"]: DATA_DIR / control["directory"] / control["file"]
            for control in CONTROLS
        },
    }
    envelopes = {
        label: rms_envelope(path) for label, path in envelope_paths.items()
    }
    active_max = envelopes["Active: 1.6 A, 100 ns"][1].max()
    for label, (time_us, envelope) in envelopes.items():
        ax_a.plot(time_us, envelope / active_max, color=colors[label], label=label)
    ax_a.axvspan(*SIGNAL_WINDOW_US, color=LIGHT_BLUE, alpha=0.15, linewidth=0)
    ax_a.set_xlim(0, 500)
    ax_a.set_ylim(0, 1.08)
    ax_a.set_xlabel("Time in one 2 kHz frame (μs)")
    ax_a.set_ylabel("Normalized RMS amplitude")
    ax_a.legend(frameon=False, loc="upper right")

    all_spectra = {"Active: 1.6 A, 100 ns": active_spectrum, **control_spectra}
    active_frequency = active_spectrum["frequency_Hz"]
    band = (
        (active_frequency >= ANALYSIS_BAND_MHZ[0] * 1e6)
        & (active_frequency <= ANALYSIS_BAND_MHZ[1] * 1e6)
    )
    active_peak = active_spectrum["signal_psd"][band].max()
    for label, spectrum_data in all_spectra.items():
        relative_db = 10.0 * np.log10(
            np.maximum(spectrum_data["signal_psd"][band] / active_peak, 1e-8)
        )
        ax_b.plot(
            spectrum_data["frequency_Hz"][band][::2] / 1e6,
            relative_db[::2],
            color=colors[label],
            label=label,
        )
    ax_b.set_xlim(*ANALYSIS_BAND_MHZ)
    ax_b.set_ylim(-55, 3)
    ax_b.set_xlabel("Frequency (MHz)")
    ax_b.set_ylabel("PSD relative to active peak (dB)")
    ax_b.legend(frameon=False, loc="lower left")

    for label, ax in zip(("(a)", "(b)"), (ax_a, ax_b)):
        style_axes(ax)
        add_panel_label(ax, label)

    fig.savefig(CONTROL_FIGURE_BASE.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(CONTROL_FIGURE_BASE.with_suffix(".png"), dpi=600, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    records = []
    spectra: dict[tuple[str, int, float], dict[str, np.ndarray]] = {}

    for run in CURRENT_RUNS:
        directory = DATA_DIR / str(run["directory"])
        for current_mA in range(400, 1801, 200):
            path = directory / f"SOA{current_mA}.bin"
            metrics, spectrum_data = analyze_waveform(path)
            metrics.update(
                {
                    "experiment": "current",
                    "run_id": int(run["run_id"]),
                    "scan_direction": run["direction"],
                    "condition_value": current_mA,
                    "condition_unit": "mA",
                }
            )
            records.append(metrics)
            spectra[("current", int(run["run_id"]), current_mA)] = spectrum_data

    for run in WIDTH_RUNS:
        directory = DATA_DIR / str(run["directory"])
        filenames = run["files"]
        for width_ns in (50, 100, 150, 200, 250):
            path = directory / filenames[width_ns]
            metrics, spectrum_data = analyze_waveform(path)
            metrics.update(
                {
                    "experiment": "pulse_width",
                    "run_id": int(run["run_id"]),
                    "scan_direction": run["direction"],
                    "condition_value": width_ns,
                    "condition_unit": "ns",
                }
            )
            records.append(metrics)
            spectra[("pulse_width", int(run["run_id"]), width_ns)] = spectrum_data

    file_metrics = pd.DataFrame(records).sort_values(
        ["experiment", "run_id", "condition_value"]
    )
    summary = summarize_runs(file_metrics)
    file_metrics.to_csv(FILE_METRICS_CSV, index=False, encoding="utf-8-sig")
    summary.to_csv(SUMMARY_CSV, index=False, encoding="utf-8-sig")

    control_records = []
    control_spectra = {}
    for control in CONTROLS:
        path = DATA_DIR / control["directory"] / control["file"]
        metrics, spectrum_data = analyze_waveform(path)
        metrics["control"] = control["control"]
        control_records.append(metrics)
        control_spectra[control["control"]] = spectrum_data
    control_metrics = pd.DataFrame(control_records)
    control_metrics.to_csv(CONTROL_CSV, index=False, encoding="utf-8-sig")

    current_summary = summary[summary["experiment"] == "current"].set_index(
        "condition_value"
    )
    width_summary = summary[summary["experiment"] == "pulse_width"].set_index(
        "condition_value"
    )
    stats_output = {
        "fixed_conditions": {
            "ld_current_mA": 200,
            "tec_temperature_C": 30,
            "aom_drive_frequency_MHz": 80,
            "fiber_length_km": 15,
            "soa_pulse_repetition_Hz": 2000,
            "current_scan_pulse_width_ns": 100,
            "pulse_width_scan_current_mA": 1600,
        },
        "recording": {
            "scope": str(file_metrics.iloc[0]["scope"]),
            "channel": str(file_metrics.iloc[0]["channel"]),
            "sample_rate_GSa_s": float(file_metrics.iloc[0]["sample_rate_GSa_s"]),
            "points_per_file": int(file_metrics.iloc[0]["point_count"]),
            "record_duration_ms": float(file_metrics.iloc[0]["record_duration_ms"]),
            "frames_per_file": int(file_metrics.iloc[0]["frame_count"]),
        },
        "analysis": {
            "signal_window_us": list(SIGNAL_WINDOW_US),
            "noise_window_us": list(NOISE_WINDOW_US),
            "frequency_band_MHz": list(ANALYSIS_BAND_MHZ),
            "welch_segment_samples": WELCH_SEGMENT_SAMPLES,
            "spectrum_window": "Hann",
            "spectral_centroid": "first moment of non-negative signal-minus-noise PSD",
            "occupied_bandwidth": "5th-to-95th percentile of cumulative excess PSD",
            "snr": "10*log10((signal-window variance-noise-window variance)/noise-window variance)",
        },
        "current_scan": {
            "conditions_mA": [int(value) for value in current_summary.index],
            "runs_per_condition": 3,
            "centroid_endpoints_MHz": [
                float(current_summary.iloc[0]["spectral_centroid_MHz_mean"]),
                float(current_summary.iloc[-1]["spectral_centroid_MHz_mean"]),
            ],
            "bandwidth90_endpoints_MHz": [
                float(current_summary.iloc[0]["occupied_bandwidth_90_MHz_mean"]),
                float(current_summary.iloc[-1]["occupied_bandwidth_90_MHz_mean"]),
            ],
            "snr_endpoints_dB": [
                float(current_summary.iloc[0]["time_domain_snr_dB_mean"]),
                float(current_summary.iloc[-1]["time_domain_snr_dB_mean"]),
            ],
            "max_across_run_centroid_sd_MHz": float(
                current_summary["spectral_centroid_MHz_sd"].max()
            ),
            "frame_centroid_sd_range_MHz": [
                float(file_metrics.loc[file_metrics["experiment"] == "current", "frame_centroid_sd_MHz"].min()),
                float(file_metrics.loc[file_metrics["experiment"] == "current", "frame_centroid_sd_MHz"].max()),
            ],
        },
        "pulse_width_scan": {
            "conditions_ns": [int(value) for value in width_summary.index],
            "runs_per_condition": 3,
            "centroid_endpoints_MHz": [
                float(width_summary.iloc[0]["spectral_centroid_MHz_mean"]),
                float(width_summary.iloc[-1]["spectral_centroid_MHz_mean"]),
            ],
            "bandwidth90_endpoints_MHz": [
                float(width_summary.iloc[0]["occupied_bandwidth_90_MHz_mean"]),
                float(width_summary.iloc[-1]["occupied_bandwidth_90_MHz_mean"]),
            ],
            "snr_endpoints_dB": [
                float(width_summary.iloc[0]["time_domain_snr_dB_mean"]),
                float(width_summary.iloc[-1]["time_domain_snr_dB_mean"]),
            ],
            "max_across_run_centroid_sd_MHz": float(
                width_summary["spectral_centroid_MHz_sd"].max()
            ),
            "frame_centroid_sd_range_MHz": [
                float(file_metrics.loc[file_metrics["experiment"] == "pulse_width", "frame_centroid_sd_MHz"].min()),
                float(file_metrics.loc[file_metrics["experiment"] == "pulse_width", "frame_centroid_sd_MHz"].max()),
            ],
        },
        "controls": {
            row["control"]: {
                "signal_window_rms_raw": float(row["signal_rms_raw"]),
                "noise_window_rms_raw": float(row["noise_rms_raw"]),
                "band_power_ratio_dB": float(row["band_power_ratio_dB"]),
            }
            for _, row in control_metrics.iterrows()
        },
    }
    STATS_JSON.write_text(
        json.dumps(stats_output, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    plot_characterization(file_metrics, summary, spectra)
    active_path = DATA_DIR / CURRENT_RUNS[0]["directory"] / "SOA1600.bin"
    active_spectrum = spectra[("current", 1, 1600)]
    plot_controls(control_metrics, control_spectra, active_path, active_spectrum)
    print(json.dumps(stats_output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
