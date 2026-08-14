from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, Rectangle
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
SOURCES = IMAGES / "sources"
PAPER_RENDER = ROOT / "tmp" / "pdfs" / "cheng2023"

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


def prepare_literature_photos() -> None:
    """
    Extract only the photograph panels from Cheng et al. (2023), Fig. 1c
    and the inset of Fig. 4a. The page crops are normalized coordinates so
    the extraction remains stable if the Poppler render resolution changes.
    """
    crops = [
        (
            PAPER_RENDER / "hi-2.png",
            IMAGES / "chap1_literature_photonic_chip.png",
            (0.596, 0.703, 0.794, 0.735),
        ),
        (
            PAPER_RENDER / "hi-5.png",
            IMAGES / "chap1_literature_packaged_eom_aom.png",
            (0.206, 0.125, 0.279, 0.194),
        ),
    ]
    for source_path, output_path, (x0, y0, x1, y1) in crops:
        with Image.open(source_path) as page:
            box = (
                round(page.width * x0),
                round(page.height * y0),
                round(page.width * x1),
                round(page.height * y1),
            )
            panel = page.crop(box).convert("RGB")
            panel = ImageOps.expand(panel, border=8, fill="white")
            panel.save(output_path, dpi=(600, 600))


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
    dark_blue = "#1f4e79"
    light_blue = "#eaf1f7"
    light_gray = "#f2f2f2"
    mid_gray = "#d9d9d9"

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
        dark_blue,
        dark_blue,
        fontsize=10.2,
        bold=True,
        linewidth=1.1,
        text_color="white",
    )

    add_arrow(ax, (0.5, 0.89), (0.5, 0.845))

    # Theoretical basis.
    add_box(
        ax,
        (0.08, 0.75),
        0.84,
        0.095,
        "理论基础（第2章）\nφ-OTDR传感机理  |  DFB-LD/SOA工作特性  |  AOM移频与外差探测  |  数字相位解调",
        light_gray,
        "#444444",
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
        "分光集成器件发射链路\n"
        "内部集成：DFB-LD + SOA\n"
        "驱动电流、光脉冲、消光比与ASE\n"
        "外差拍频与SOA-AOM-DAQ协同门控",
        "white",
        dark_blue,
        fontsize=8.6,
        bold=True,
        linewidth=1.2,
    )
    add_box(
        ax,
        (0.52, 0.49),
        0.40,
        0.215,
        "DAS收发一体化光电模组\n"
        "AOM、耦合器、环形器、PBS与BPD\n"
        "光路拓扑、接口、封装与通道一致性\n"
        "分立式基线与模组光电性能对比",
        "white",
        dark_blue,
        fontsize=8.6,
        bold=True,
        linewidth=1.2,
    )

    ax.plot([0.28, 0.72], [0.725, 0.725], color="#333333", linewidth=1.0)
    add_arrow(ax, (0.28, 0.725), (0.28, 0.705))
    add_arrow(ax, (0.72, 0.725), (0.72, 0.705))

    add_arrow(ax, (0.28, 0.49), (0.40, 0.445))
    add_arrow(ax, (0.72, 0.49), (0.60, 0.445))

    # Fixed processing and end-to-end validation.
    add_box(
        ax,
        (0.12, 0.34),
        0.76,
        0.105,
        "固定解调流程与端到端验证（第4章）\n双通道标定  →  数字下变频与I/Q提取  →  复共轭差分与双偏振合成  →  PZT振动恢复",
        light_blue,
        dark_blue,
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
        light_gray,
        "#444444",
        fontsize=8.7,
        bold=True,
    )

    add_arrow(ax, (0.5, 0.20), (0.5, 0.155))

    add_box(
        ax,
        (0.12, 0.08),
        0.76,
        0.075,
        "研究结论（第5章）：发射特性—光路集成—固定解调—传感验证",
        mid_gray,
        "#333333",
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
    prepare_literature_photos()
    draw_research_route()


if __name__ == "__main__":
    main()
