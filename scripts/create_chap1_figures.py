from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
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
    face: str,
    edge: str,
    fontsize: float = 9.2,
    bold: bool = False,
) -> None:
    x, y = xy
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.2,
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
        color="#1f2933",
        linespacing=1.35,
    )


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = "#52606d",
    width: float = 1.4,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=width,
            color=color,
            shrinkA=2,
            shrinkB=2,
            connectionstyle="arc3",
        )
    )


def draw_research_route() -> None:
    colors = {
        "blue": "#dceefb",
        "blue_edge": "#2680a8",
        "green": "#e3f9e5",
        "green_edge": "#3f9142",
        "amber": "#fff3c4",
        "amber_edge": "#c99a2e",
        "purple": "#eee6ff",
        "purple_edge": "#7f5db7",
        "gray": "#f0f4f8",
        "gray_edge": "#627d98",
    }
    fig, ax = plt.subplots(figsize=(7.15, 5.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.965,
        "本文研究技术路线",
        ha="center",
        va="center",
        fontproperties=CN_BOLD,
        fontsize=15,
        color="#102a43",
    )

    # Research objects and questions.
    add_box(
        ax,
        (0.06, 0.805),
        0.40,
        0.095,
        "集成 LD-SOA 发射链路\n驱动、脉冲与瞬态频率特性",
        colors["blue"],
        colors["blue_edge"],
        bold=True,
    )
    add_box(
        ax,
        (0.54, 0.805),
        0.40,
        0.095,
        "分立/集成 DAS 收发光路\n性能与工程一致性",
        colors["blue"],
        colors["blue_edge"],
        bold=True,
    )

    # Unified theory in Chapter 2.
    add_arrow(ax, (0.26, 0.805), (0.41, 0.744))
    add_arrow(ax, (0.74, 0.805), (0.59, 0.744))
    add_box(
        ax,
        (0.13, 0.655),
        0.74,
        0.09,
        "第2章：统一理论模型\n瑞利散射与距离映射｜SOA 动态｜AOM 移频与外差探测｜I/Q、频偏与偏振",
        colors["gray"],
        colors["gray_edge"],
        fontsize=9.0,
        bold=True,
    )

    # Chapter 3 and Chapter 4 branches.
    add_arrow(ax, (0.39, 0.655), (0.27, 0.592))
    add_arrow(ax, (0.61, 0.655), (0.73, 0.592))
    add_box(
        ax,
        (0.055, 0.435),
        0.42,
        0.16,
        "第3章：发射链路与收发集成光模组\n"
        "• SOA 电流、脉宽、ASE 与拍频表征\n"
        "• SOA-AOM-DAQ 协同门控\n"
        "• 分立/集成等条件与各自优化比较",
        colors["green"],
        colors["green_edge"],
        fontsize=8.7,
        bold=True,
    )
    add_box(
        ax,
        (0.525, 0.435),
        0.42,
        0.16,
        "第4章：接收与数字解调优化\n"
        "• BPD/PBS 双通道校准与合成\n"
        "• 中心频率、标距、区域与滤波配置\n"
        "• PZT 定位、频率恢复与稳定性测试",
        colors["purple"],
        colors["purple_edge"],
        fontsize=8.7,
        bold=True,
    )

    # Verification and comparison.
    add_arrow(ax, (0.265, 0.435), (0.39, 0.368))
    add_arrow(ax, (0.735, 0.435), (0.61, 0.368))
    add_box(
        ax,
        (0.12, 0.255),
        0.76,
        0.115,
        "实验验证与综合评价\n"
        "光脉冲/消光比/ASE/拍频｜噪声底/相位跳变/SNR｜频率与定位误差｜体积/接口/功耗/长期漂移",
        colors["amber"],
        colors["amber_edge"],
        fontsize=8.9,
        bold=True,
    )
    add_arrow(ax, (0.5, 0.255), (0.5, 0.188))
    add_box(
        ax,
        (0.16, 0.095),
        0.68,
        0.095,
        "第5章：形成“发射特性—光路集成—接收解调—传感验证”的证据链\n总结适用范围、局限与后续集成方向",
        "#fde2e4",
        "#b44c55",
        fontsize=9.1,
        bold=True,
    )

    fig.subplots_adjust(left=0.015, right=0.985, top=0.985, bottom=0.02)
    fig.savefig(IMAGES / "chap1_research_route.pdf", bbox_inches="tight")
    fig.savefig(IMAGES / "chap1_research_route.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    prepare_application_photos()
    prepare_literature_photos()
    draw_research_route()


if __name__ == "__main__":
    main()
