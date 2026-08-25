from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
SOURCES = IMAGES / "sources"

FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
CN = font_manager.FontProperties(fname=str(FONT_REGULAR))
CN_BOLD = font_manager.FontProperties(fname=str(FONT_BOLD))


def crop_cover(image: Image.Image, size: tuple[int, int], focus_y: float = 0.5) -> Image.Image:
    """Resize and center-crop an image to a fixed publication panel size."""
    target_w, target_h = size
    src_w, src_h = image.size
    scale = max(target_w / src_w, target_h / src_h)
    resized = image.resize(
        (round(src_w * scale), round(src_h * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (resized.width - target_w) // 2)
    top = round((resized.height - target_h) * focus_y)
    top = max(0, min(top, resized.height - target_h))
    return resized.crop((left, top, left + target_w, top + target_h))


def prepare_application_photos() -> None:
    specs = [
        ("railway_cc0.jpg", "chap1_application_railway.jpg", 0.58),
        ("pipeline_public_domain.jpg", "chap1_application_pipeline.jpg", 0.50),
        ("wind_turbine_cc0.jpg", "chap1_application_wind.jpg", 0.42),
    ]
    for source_name, output_name, focus_y in specs:
        with Image.open(SOURCES / source_name) as source:
            panel = crop_cover(source.convert("RGB"), (1800, 1200), focus_y=focus_y)
            panel.save(IMAGES / output_name, quality=94, subsampling=0, dpi=(300, 300))


def draw_packaged_eom_aom() -> None:
    """Draw a slim packaged EOM phase modulator and a blue AOM Bragg cell in
    clearly distinct styles so the two device panels are easy to tell apart."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")

    fiber_color = "#e8b13a"

    # ------------------------------------------------------------------
    # EOM: low-profile silver phase modulator with a straight through path.
    # ------------------------------------------------------------------
    for (x0, x1) in ((0.15, 1.0), (5.35, 6.3)):
        ax.plot([x0, x1], [4.1, 4.1], color=fiber_color, linewidth=5.0, solid_capstyle="round")
        ax.plot([x0, x1], [4.1, 4.1], color="#ffe9a3", linewidth=1.2, solid_capstyle="round")

    ax.add_patch(
        FancyBboxPatch(
            (1.0, 2.85),
            4.35,
            2.5,
            boxstyle="round,pad=0.03,rounding_size=0.14",
            facecolor="#d7dde2",
            edgecolor="#4f5559",
            linewidth=1.4,
        )
    )
    ax.add_patch(Rectangle((1.45, 3.25), 3.45, 1.7, facecolor="#bcc3c9", edgecolor="#626a70", linewidth=1.0))

    # LiNbO3 chip with two waveguide lines and a phase-modulation symbol.
    ax.add_patch(Rectangle((2.05, 3.6), 1.55, 1.0, facecolor="#e9d6f2", edgecolor="#7a5a8a", linewidth=0.9))
    ax.plot([2.1, 3.55], [4.03, 4.03], color="#6a4a7a", linewidth=0.9)
    ax.plot([2.1, 3.55], [4.27, 4.27], color="#6a4a7a", linewidth=0.9)
    xs = np.linspace(2.15, 3.5, 60)
    ax.plot(xs, 4.15 + 0.10 * np.sin(9 * (xs - 2.15)), color="#c0392b", linewidth=1.1)

    # Straight light path through the modulator.
    ax.add_patch(FancyArrowPatch((1.42, 4.1), (2.0, 4.1), arrowstyle="-|>", mutation_scale=8, color="#333333"))
    ax.add_patch(FancyArrowPatch((3.65, 4.1), (4.75, 4.1), arrowstyle="-|>", mutation_scale=8, color="#333333"))

    # Small RF pin on top of the EOM package.
    ax.add_patch(Rectangle((2.85, 5.35), 0.55, 0.35, facecolor="#8d9499", edgecolor="#4f5559", linewidth=0.8))
    ax.add_patch(Rectangle((3.03, 5.55), 0.14, 0.30, facecolor="#d9dde0", edgecolor="#4f5559", linewidth=0.6))

    # ------------------------------------------------------------------
    # AOM: blue Bragg cell with an RF drive and an angled diffracted order.
    # ------------------------------------------------------------------
    for (x0, x1) in ((6.4, 7.15), (11.1, 11.95)):
        ax.plot([x0, x1], [3.15, 3.15], color=fiber_color, linewidth=5.0, solid_capstyle="round")
        ax.plot([x0, x1], [3.15, 3.15], color="#ffe9a3", linewidth=1.2, solid_capstyle="round")

    ax.add_patch(
        FancyBboxPatch(
            (7.15, 1.6),
            3.95,
            4.0,
            boxstyle="round,pad=0.03,rounding_size=0.14",
            facecolor="#5f94ad",
            edgecolor="#485a63",
            linewidth=1.4,
        )
    )
    ax.add_patch(Rectangle((7.5, 1.95), 3.25, 3.3, facecolor="#4c83a0", edgecolor="#3d6b84", linewidth=1.0))

    # Acousto-optic crystal, gold transducer and SMA connector.
    ax.add_patch(Rectangle((7.75, 2.35), 2.75, 2.15, facecolor="#a8ccdd", edgecolor="#3d6b84", linewidth=0.9))
    ax.add_patch(Rectangle((8.6, 4.35), 1.05, 0.7, facecolor="#d89a4a", edgecolor="#8a5a1f", linewidth=0.8))
    ax.add_patch(Rectangle((8.5, 5.6), 1.25, 0.85, facecolor="#22262b", edgecolor="#0e1113", linewidth=1.0))
    ax.add_patch(Rectangle((9.08, 6.15), 0.14, 0.55, facecolor="#d9dde0", edgecolor="#0e1113", linewidth=0.6))

    # Acoustic waves travelling downward from the transducer.
    for k, yy in enumerate((4.22, 3.92, 3.62)):
        xs = np.linspace(8.85, 9.40, 30)
        ax.plot(xs, yy + 0.05 * np.sin(10 * (xs - 8.85) + 0.8 * k), color="#1f4a5f", linewidth=1.0)

    # 0th order continues into the output fiber; 1st order is diffracted up.
    ax.add_patch(FancyArrowPatch((7.5, 3.15), (8.6, 3.15), arrowstyle="-|>", mutation_scale=8, color="#c0392b"))
    ax.plot([8.6, 10.9], [3.15, 3.15], color="#c0392b", linewidth=1.1)
    ax.add_patch(
        FancyArrowPatch((8.9, 3.15), (10.45, 3.95), arrowstyle="-|>", mutation_scale=8, color="#c0392b", linestyle=(0, (4, 2)))
    )

    # Device captions below each package.
    ax.text(3.2, 2.45, "EOM · 1550 nm", ha="center", va="center", fontsize=11, weight="bold", color="#174f78")
    ax.text(9.15, 1.15, "AOM", ha="center", va="center", fontsize=11, weight="bold", color="#174f78")

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(
        IMAGES / "chap1_literature_packaged_eom_aom.png",
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.04,
        facecolor="white",
    )
    plt.close(fig)


def draw_dfb_laser() -> None:
    """Draw a butterfly-packaged DFB laser in cutaway, showing the laser chip
    and lasing beam so it reads clearly as a light source next to the EOM/AOM."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")

    # Output fiber pigtail entering the package from the left.
    ax.plot([0.15, 2.6], [3.5, 3.5], color="#e8b13a", linewidth=5.0, solid_capstyle="round")
    ax.plot([0.15, 2.6], [3.5, 3.5], color="#ffe9a3", linewidth=1.2, solid_capstyle="round")
    ax.add_patch(Rectangle((2.2, 3.14), 0.75, 0.72, facecolor="#8d9499", edgecolor="#4f5559", linewidth=1.0))

    # Butterfly package body.
    ax.add_patch(
        FancyBboxPatch(
            (1.9, 1.1),
            8.2,
            4.8,
            boxstyle="round,pad=0.03,rounding_size=0.18",
            facecolor="#c5cbd0",
            edgecolor="#52595f",
            linewidth=1.5,
        )
    )
    ax.add_patch(Rectangle((2.45, 1.4), 7.1, 4.2, facecolor="#aeb6bc", edgecolor="#626a70", linewidth=1.0))

    # Fourteen gold pins along the package sides.
    pin_x = [2.85, 3.75, 4.65, 5.55, 6.45, 7.35, 8.25]
    for x in pin_x:
        ax.add_patch(Rectangle((x - 0.10, 0.25), 0.20, 0.95, facecolor="#e0b84f", edgecolor="#8a6d1f", linewidth=0.7))
        ax.add_patch(Rectangle((x - 0.10, 5.80), 0.20, 0.95, facecolor="#e0b84f", edgecolor="#8a6d1f", linewidth=0.7))

    # Mounting holes.
    for x in (2.3, 9.7):
        for y in (1.5, 5.5):
            ax.add_patch(Circle((x, y), 0.17, facecolor="#555d62", edgecolor="#30363a", linewidth=0.8))
            ax.add_patch(Circle((x, y), 0.07, facecolor="#d9dde0", edgecolor="none"))

    # Cutaway window exposing the internal optical bench.
    ax.add_patch(Rectangle((2.8, 1.8), 4.9, 3.4, facecolor="#f4f6f7", edgecolor="#52595f", linewidth=1.1))

    # Internal fiber stub, coupling lens and TEC.
    ax.plot([2.9, 4.05], [3.5, 3.5], color="#e8b13a", linewidth=3.0, solid_capstyle="round")
    ax.add_patch(Circle((4.12, 3.5), 0.18, facecolor="#8d9499", edgecolor="#4f5559", linewidth=0.8))
    ax.add_patch(Rectangle((4.65, 2.5), 1.6, 0.85, facecolor="#d7dde2", edgecolor="#626a70", linewidth=0.8, hatch="////"))

    # Laser chip with a glowing active stripe.
    ax.add_patch(Rectangle((4.65, 3.05), 1.6, 0.9, facecolor="#2f3b44", edgecolor="#141a1f", linewidth=1.1))
    ax.plot([4.65, 6.25], [3.5, 3.5], color="#e63946", linewidth=1.7)

    # Lasing beam launched into the fiber.
    ax.add_patch(
        Polygon(
            [(4.62, 3.30), (4.62, 3.70), (3.05, 3.56), (3.05, 3.44)],
            closed=True,
            facecolor="#e63946",
            alpha=0.22,
            edgecolor="none",
        )
    )
    ax.add_patch(Circle((4.62, 3.5), 0.30, facecolor="#e63946", alpha=0.25, edgecolor="none"))
    ax.add_patch(FancyArrowPatch((4.25, 3.5), (3.30, 3.5), arrowstyle="-|>", mutation_scale=9, color="#e63946"))

    # Monitor photodiode behind the rear facet.
    ax.add_patch(Rectangle((6.45, 3.28), 0.5, 0.44, facecolor="#7b8790", edgecolor="#4f5559", linewidth=0.8))
    ax.add_patch(FancyArrowPatch((6.32, 3.5), (6.44, 3.5), arrowstyle="-|>", mutation_scale=8, color="#c0392b"))

    # Internal labels.
    ax.annotate(
        "激光芯片",
        xy=(5.40, 3.90),
        xytext=(5.20, 4.75),
        fontproperties=CN,
        fontsize=9.5,
        color="#333333",
        ha="center",
        arrowprops=dict(arrowstyle="-", color="#333333", linewidth=0.8),
    )
    ax.annotate(
        "TEC",
        xy=(5.45, 2.55),
        xytext=(5.20, 2.02),
        fontproperties=CN,
        fontsize=9.5,
        color="#333333",
        ha="center",
        arrowprops=dict(arrowstyle="-", color="#333333", linewidth=0.8),
    )

    # Identification plate.
    ax.add_patch(
        FancyBboxPatch(
            (7.85, 3.05),
            1.65,
            1.55,
            boxstyle="round,pad=0.04,rounding_size=0.10",
            facecolor="#eef1f3",
            edgecolor="#737b80",
            linewidth=1.0,
        )
    )
    ax.text(8.675, 3.95, "DFB", ha="center", va="center", fontsize=17, weight="bold", color="#174f78")
    ax.text(8.675, 3.35, "1550 nm", ha="center", va="center", fontsize=9.5, color="#3e474d")

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    fig.savefig(IMAGES / "chap1_dfb_laser.png", dpi=300, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    face: str = "white",
    edge: str = "#222222",
    fontsize: float = 9.2,
    bold: bool = False,
    linewidth: float = 1.0,
    text_color: str = "#111111",
) -> None:
    x, y = xy
    box = Rectangle(
        (x, y),
        width,
        height,
        linewidth=linewidth,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(box)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontproperties=CN_BOLD if bold else CN,
        fontsize=fontsize,
        color=text_color,
        linespacing=1.25,
    )


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = "#333333",
    width: float = 1.0,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=width,
            color=color,
            shrinkA=2,
            shrinkB=2,
            connectionstyle="arc3",
        )
    )


def draw_research_route() -> None:
    line_color = "#333333"
    no_fill = "white"

    fig, ax = plt.subplots(figsize=(7.15, 5.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Overall objective.
    add_box(
        ax,
        (0.12, 0.89),
        0.76,
        0.075,
        "研究目标：外差式DAS收发系统的小型化、模块化与稳定运行",
        no_fill,
        line_color,
        fontsize=10.2,
        bold=True,
        linewidth=1.1,
        text_color="#111111",
    )

    add_arrow(ax, (0.5, 0.89), (0.5, 0.845))

    # Theoretical basis.
    add_box(
        ax,
        (0.08, 0.75),
        0.84,
        0.095,
        "理论基础（第2章）\nφ-OTDR传感机理  |  ECL--SOA工作特性  |  AOM移频与外差探测  |  数字相位解调",
        no_fill,
        line_color,
        fontsize=8.7,
        bold=True,
    )

    add_arrow(ax, (0.5, 0.75), (0.5, 0.725))

    # Parallel hardware studies.
    add_box(
        ax,
        (0.08, 0.49),
        0.40,
        0.215,
        "双输出ECL--SOA发射链路\n"
        "LD端参考光 + SOA端脉冲信号光\n"
        "驱动电流、光脉冲、消光比与ASE\n"
        "外差拍频与SOA-AOM-DAQ协同门控",
        "white",
        line_color,
        fontsize=8.6,
        bold=True,
        linewidth=1.2,
    )
    add_box(
        ax,
        (0.52, 0.49),
        0.40,
        0.215,
        "DAS一体化收发模组\n"
        "传统EDFA与本文ECL--SOA光路对比\n"
        "分立基线、集成封装与统一接口\n"
        "等条件光电及传感性能验证",
        "white",
        line_color,
        fontsize=8.6,
        bold=True,
        linewidth=1.2,
    )

    ax.plot([0.28, 0.72], [0.725, 0.725], color="#333333", linewidth=1.0)
    add_arrow(ax, (0.28, 0.725), (0.28, 0.705))
    add_arrow(ax, (0.72, 0.725), (0.72, 0.705))

    ax.plot([0.28, 0.28], [0.49, 0.467], color=line_color, linewidth=1.0)
    ax.plot([0.72, 0.72], [0.49, 0.467], color=line_color, linewidth=1.0)
    ax.plot([0.28, 0.72], [0.467, 0.467], color=line_color, linewidth=1.0)
    add_arrow(ax, (0.5, 0.467), (0.5, 0.445))

    # Fixed processing and end-to-end validation.
    add_box(
        ax,
        (0.12, 0.34),
        0.76,
        0.105,
        "数字相位解调与传感验证（第4章）\n双通道标定  →  数字下变频与I/Q提取  →  复共轭差分与双偏振合成  →  PZT振动恢复",
        no_fill,
        line_color,
        fontsize=8.6,
        bold=True,
    )

    add_arrow(ax, (0.5, 0.34), (0.5, 0.295))

    # Evaluation metrics.
    add_box(
        ax,
        (0.08, 0.20),
        0.84,
        0.095,
        "性能评价\n光功率、消光比与ASE  |  拍频质量与噪声底  |  定位、频率及波形恢复  |  稳定性与工程指标",
        no_fill,
        line_color,
        fontsize=8.7,
        bold=True,
    )

    add_arrow(ax, (0.5, 0.20), (0.5, 0.155))

    add_box(
        ax,
        (0.12, 0.08),
        0.76,
        0.075,
        "研究结论（第5章）：发射特性—光路集成—信号解调—传感验证",
        no_fill,
        line_color,
        fontsize=9.0,
        bold=True,
    )

    fig.subplots_adjust(left=0.02, right=0.98, top=0.99, bottom=0.01)
    fig.savefig(IMAGES / "chap1_research_route.pdf", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(IMAGES / "chap1_research_route.png", dpi=600, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    prepare_application_photos()
    draw_packaged_eom_aom()
    draw_dfb_laser()
    draw_research_route()


if __name__ == "__main__":
    main()
