from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
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
    """Draw packaged EOM and AOM devices in the same style as the DFB laser."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")

    # Optical pigtails use the same two-tone treatment as the DFB illustration.
    fiber_segments = [
        ((0.2, 1.3), (3.5, 3.5)),
        ((5.35, 5.95), (3.5, 3.5)),
        ((6.05, 6.65), (3.5, 3.5)),
        ((10.85, 11.8), (3.5, 3.5)),
    ]
    for (x0, x1), (y0, y1) in fiber_segments:
        ax.plot([x0, x1], [y0, y1], color="#f2c230", linewidth=5.0, solid_capstyle="round")
        ax.plot([x0, x1], [y0, y1], color="#fff1a8", linewidth=1.2, solid_capstyle="round")

    # EOM: compact silver package with electrical pins and an identification plate.
    for x in (2.0, 2.65, 3.30, 3.95, 4.60):
        ax.add_patch(Rectangle((x - 0.08, 1.18), 0.16, 0.92, facecolor="#d8bd68", edgecolor="#806d32", linewidth=0.7))
        ax.add_patch(Rectangle((x - 0.08, 4.90), 0.16, 0.92, facecolor="#d8bd68", edgecolor="#806d32", linewidth=0.7))
    ax.add_patch(Rectangle((1.0, 3.18), 0.52, 0.64, facecolor="#8d9499", edgecolor="#4f5559", linewidth=1.0))
    ax.add_patch(Rectangle((5.18, 3.18), 0.52, 0.64, facecolor="#8d9499", edgecolor="#4f5559", linewidth=1.0))
    ax.add_patch(
        FancyBboxPatch(
            (1.25, 1.95),
            4.15,
            3.10,
            boxstyle="round,pad=0.03,rounding_size=0.16",
            facecolor="#c5cbd0",
            edgecolor="#52595f",
            linewidth=1.4,
        )
    )
    ax.add_patch(Rectangle((1.62, 2.27), 3.41, 2.46, facecolor="#aeb6bc", edgecolor="#626a70", linewidth=1.0))
    for x in (1.52, 5.13):
        for y in (2.25, 4.75):
            ax.add_patch(Circle((x, y), 0.13, facecolor="#555d62", edgecolor="#30363a", linewidth=0.7))
            ax.add_patch(Circle((x, y), 0.05, facecolor="#d9dde0", edgecolor="none"))
    ax.add_patch(
        FancyBboxPatch(
            (2.0, 2.72),
            2.65,
            1.56,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            facecolor="#eef1f3",
            edgecolor="#737b80",
            linewidth=1.0,
        )
    )
    ax.text(3.325, 3.72, "EOM", ha="center", va="center", fontsize=17, weight="bold", color="#174f78")
    ax.text(3.325, 3.18, "1550 nm", ha="center", va="center", fontsize=10.5, color="#3e474d")
    ax.plot([2.42, 4.23], [2.91, 2.91], color="#d43b32", linewidth=1.3)
    ax.add_patch(FancyArrowPatch((3.05, 2.91), (2.50, 2.91), arrowstyle="-|>", mutation_scale=9, color="#d43b32"))

    # AOM: blue anodized package, drawn with matching geometry and line weights.
    ax.add_patch(Rectangle((6.30, 3.18), 0.52, 0.64, facecolor="#8d9499", edgecolor="#4f5559", linewidth=1.0))
    ax.add_patch(Rectangle((10.68, 3.18), 0.52, 0.64, facecolor="#8d9499", edgecolor="#4f5559", linewidth=1.0))
    ax.add_patch(
        FancyBboxPatch(
            (6.55, 1.95),
            4.35,
            3.10,
            boxstyle="round,pad=0.03,rounding_size=0.16",
            facecolor="#75a9c1",
            edgecolor="#485a63",
            linewidth=1.4,
        )
    )
    ax.add_patch(Rectangle((6.93, 2.27), 3.59, 2.46, facecolor="#5f94ad", edgecolor="#526b77", linewidth=1.0))
    for x in (6.82, 10.63):
        for y in (2.25, 4.75):
            ax.add_patch(Circle((x, y), 0.13, facecolor="#555d62", edgecolor="#30363a", linewidth=0.7))
            ax.add_patch(Circle((x, y), 0.05, facecolor="#d9dde0", edgecolor="none"))
    ax.add_patch(
        FancyBboxPatch(
            (7.28, 2.72),
            2.90,
            1.56,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            facecolor="#edf3f5",
            edgecolor="#60737c",
            linewidth=1.0,
        )
    )
    ax.text(8.73, 3.72, "AOM", ha="center", va="center", fontsize=17, weight="bold", color="#174f78")
    ax.text(8.73, 3.18, "80 MHz", ha="center", va="center", fontsize=10.5, color="#3e474d")
    ax.plot([7.70, 9.76], [2.91, 2.91], color="#d43b32", linewidth=1.3)
    ax.add_patch(FancyArrowPatch((8.42, 2.91), (7.78, 2.91), arrowstyle="-|>", mutation_scale=9, color="#d43b32"))

    # RF input connector distinguishes the AOM from the optical EOM package.
    ax.add_patch(Rectangle((8.48, 1.53), 0.50, 0.45, facecolor="#8d9499", edgecolor="#4f5559", linewidth=1.0))
    ax.add_patch(Rectangle((8.57, 1.03), 0.32, 0.50, facecolor="#d8bd68", edgecolor="#806d32", linewidth=0.8))

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
    """Draw a clean butterfly-packaged DFB laser for the chapter overview."""
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.set_aspect("equal")
    ax.axis("off")

    # Fiber pigtail and strain relief.
    ax.plot([0.2, 2.1], [3.5, 3.5], color="#f2c230", linewidth=5.0, solid_capstyle="round")
    ax.plot([0.2, 2.1], [3.5, 3.5], color="#fff1a8", linewidth=1.2, solid_capstyle="round")
    ax.add_patch(Rectangle((1.75, 3.18), 0.65, 0.64, facecolor="#8d9499", edgecolor="#4f5559", linewidth=1.0))

    # Fourteen electrical pins along the package sides.
    pin_x = [2.75, 3.65, 4.55, 5.45, 6.35, 7.25, 8.15]
    for x in pin_x:
        ax.add_patch(Rectangle((x - 0.09, 0.45), 0.18, 1.28, facecolor="#d8bd68", edgecolor="#806d32", linewidth=0.7))
        ax.add_patch(Rectangle((x - 0.09, 5.27), 0.18, 1.28, facecolor="#d8bd68", edgecolor="#806d32", linewidth=0.7))

    # Metal flange, mounting holes, and raised package body.
    ax.add_patch(
        FancyBboxPatch(
            (2.0, 1.55),
            8.0,
            3.9,
            boxstyle="round,pad=0.03,rounding_size=0.18",
            facecolor="#c5cbd0",
            edgecolor="#52595f",
            linewidth=1.4,
        )
    )
    ax.add_patch(Rectangle((2.65, 1.85), 6.7, 3.3, facecolor="#aeb6bc", edgecolor="#626a70", linewidth=1.0))
    for x in (2.35, 9.65):
        for y in (1.95, 5.05):
            ax.add_patch(Circle((x, y), 0.18, facecolor="#555d62", edgecolor="#30363a", linewidth=0.8))
            ax.add_patch(Circle((x, y), 0.07, facecolor="#d9dde0", edgecolor="none"))

    # Identification plate and optical-axis mark.
    ax.add_patch(
        FancyBboxPatch(
            (3.35, 2.35),
            5.3,
            2.3,
            boxstyle="round,pad=0.04,rounding_size=0.10",
            facecolor="#eef1f3",
            edgecolor="#737b80",
            linewidth=1.0,
        )
    )
    ax.text(6.0, 3.85, "DFB LASER", ha="center", va="center", fontsize=19, weight="bold", color="#174f78")
    ax.text(6.0, 3.15, "1550 nm", ha="center", va="center", fontsize=13, color="#3e474d")
    ax.plot([4.3, 7.7], [2.78, 2.78], color="#d43b32", linewidth=1.5)
    ax.add_patch(FancyArrowPatch((5.35, 2.78), (4.45, 2.78), arrowstyle="-|>", mutation_scale=10, color="#d43b32"))

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
