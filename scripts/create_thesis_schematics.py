from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"

FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
CN = font_manager.FontProperties(fname=str(FONT_REGULAR))
CN_BOLD = font_manager.FontProperties(fname=str(FONT_BOLD))

INK = "#26333F"
BLUE = "#3F73C9"
LIGHT_BLUE = "#DDEAF7"
RED = "#D95C4F"
LIGHT_RED = "#F7DDD8"
GREEN = "#2A9D8F"
LIGHT_GREEN = "#D9EEE9"
ORANGE = "#E58A3A"
LIGHT_ORANGE = "#FAE6CE"
PURPLE = "#7656B8"
LIGHT_PURPLE = "#E7E0F3"
GRAY = "#6B7280"
LIGHT_GRAY = "#F2F4F6"


def canvas(figsize: tuple[float, float]) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    face: str = "white",
    edge: str = INK,
    fontsize: float = 8.2,
    bold: bool = False,
    linewidth: float = 1.0,
    linestyle: str = "-",
    zorder: int = 2,
) -> None:
    x, y = xy
    ax.add_patch(
        Rectangle(
            (x, y),
            width,
            height,
            facecolor=face,
            edgecolor=edge,
            linewidth=linewidth,
            linestyle=linestyle,
            zorder=zorder,
        )
    )
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontproperties=CN_BOLD if bold else CN,
        fontsize=fontsize,
        color=INK,
        linespacing=1.2,
        zorder=zorder + 1,
    )


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = INK,
    width: float = 1.2,
    style: str = "-|>",
    connection: str = "arc3",
    linestyle: str = "-",
    zorder: int = 3,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=10,
            linewidth=width,
            color=color,
            connectionstyle=connection,
            linestyle=linestyle,
            shrinkA=2,
            shrinkB=2,
            zorder=zorder,
        )
    )


def text(
    ax: plt.Axes,
    xy: tuple[float, float],
    value: str,
    *,
    fontsize: float = 7.8,
    color: str = INK,
    bold: bool = False,
    ha: str = "center",
    va: str = "center",
) -> None:
    ax.text(
        *xy,
        value,
        ha=ha,
        va=va,
        fontproperties=CN_BOLD if bold else CN,
        fontsize=fontsize,
        color=color,
        linespacing=1.2,
    )


def save(fig: plt.Figure, name: str) -> None:
    fig.subplots_adjust(left=0.015, right=0.985, top=0.985, bottom=0.015)
    fig.savefig(IMAGES / f"{name}.pdf", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(IMAGES / f"{name}.png", dpi=500, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def draw_phi_otdr_principle() -> None:
    fig, ax = canvas((7.15, 3.55))

    box(ax, (0.03, 0.66), 0.16, 0.17, "窄线宽脉冲光\n$t=t_0$", face=LIGHT_RED, edge=RED, bold=True)
    box(ax, (0.25, 0.66), 0.13, 0.17, "环形器", face=LIGHT_BLUE, edge=BLUE, bold=True)
    box(ax, (0.45, 0.61), 0.50, 0.27, "传感光纤", face="#F7FAFC", edge=BLUE, bold=True)
    arrow(ax, (0.19, 0.745), (0.25, 0.745), color=RED)
    arrow(ax, (0.38, 0.745), (0.45, 0.745), color=RED)

    scatter_x = [0.57, 0.70, 0.84]
    scatter_labels = ["$z_1$", "$z_2$", "$z_3$"]
    for x, label in zip(scatter_x, scatter_labels):
        ax.plot([x, x], [0.68, 0.80], color=GREEN, linewidth=2.0)
        ax.scatter([x], [0.745], s=25, color=GREEN, zorder=4)
        text(ax, (x, 0.835), label, fontsize=8.0, color=GREEN)
    text(ax, (0.70, 0.64), "沿程瑞利后向散射", fontsize=7.6, color=GREEN)

    arrow(ax, (0.84, 0.61), (0.38, 0.54), color=GREEN, connection="arc3,rad=-0.08")
    text(ax, (0.62, 0.49), "往返延迟 $t-t_0=2n_gz/c$", fontsize=7.8, color=GREEN)

    box(ax, (0.25, 0.22), 0.13, 0.16, "相干接收\n与BPD", face=LIGHT_GREEN, edge=GREEN, bold=True)
    box(ax, (0.45, 0.22), 0.12, 0.16, "DAQ采样", face=LIGHT_ORANGE, edge=ORANGE, bold=True)
    box(ax, (0.64, 0.19), 0.13, 0.22, "采样点\n$n=f_st$", face=LIGHT_PURPLE, edge=PURPLE, bold=True)
    box(ax, (0.83, 0.16), 0.14, 0.28, r"距离映射" "\n" r"$z=ct/(2n_g)$" "\n" r"$\Delta z_s=c/(2n_gf_s)$", face=LIGHT_BLUE, edge=BLUE, fontsize=7.4, bold=True)
    arrow(ax, (0.315, 0.54), (0.315, 0.38), color=GREEN)
    arrow(ax, (0.38, 0.30), (0.45, 0.30))
    arrow(ax, (0.57, 0.30), (0.64, 0.30))
    arrow(ax, (0.77, 0.30), (0.83, 0.30))
    text(ax, (0.04, 0.08), "空间位置由回波到达时间确定；距离采样间隔不等同于脉冲宽度限定的空间分辨率。", fontsize=7.7, ha="left")
    save(fig, "chap2_phi_otdr_principle")


def draw_soa_coupling_chain() -> None:
    fig, ax = canvas((7.15, 3.35))
    labels = [
        ("SOA驱动\n$I(t)$", LIGHT_ORANGE, ORANGE),
        ("载流子密度\n$N(t)$", LIGHT_BLUE, BLUE),
        ("增益与ASE\n$G(t)$", LIGHT_GREEN, GREEN),
        (r"折射率与相位" "\n" r"$\Delta\phi(t)$", LIGHT_PURPLE, PURPLE),
        (r"瞬时频率" "\n" r"$\Delta f(t)$", LIGHT_RED, RED),
        ("拍频与解调相位\n可观测变化", LIGHT_GRAY, INK),
    ]
    x_values = [0.025, 0.19, 0.355, 0.52, 0.685, 0.84]
    widths = [0.125, 0.125, 0.125, 0.125, 0.125, 0.135]
    for index, ((label, face, edge), x, width) in enumerate(zip(labels, x_values, widths)):
        box(ax, (x, 0.60), width, 0.20, label, face=face, edge=edge, bold=True, fontsize=7.8)
        if index < len(labels) - 1:
            arrow(ax, (x + width, 0.70), (x_values[index + 1], 0.70))

    box(
        ax,
        (0.175, 0.53),
        0.65,
        0.34,
        "",
        face="none",
        edge=GRAY,
        linewidth=1.0,
        linestyle="--",
        zorder=1,
    )
    text(ax, (0.50, 0.90), "候选物理传递链：用于提出可检验假设，不直接替代实验归因", fontsize=8.0, color=GRAY, bold=True)

    box(ax, (0.05, 0.20), 0.24, 0.17, "受控变量\n电流、脉宽、温度、输入功率", face=LIGHT_ORANGE, edge=ORANGE, fontsize=7.6)
    box(ax, (0.38, 0.20), 0.24, 0.17, "排他性对照\n固定AOM、改变时延、暗态与断光", face=LIGHT_BLUE, edge=BLUE, fontsize=7.6)
    box(ax, (0.71, 0.20), 0.24, 0.17, "分层观测\n电脉冲、光脉冲、光谱、拍频与相位", face=LIGHT_GREEN, edge=GREEN, fontsize=7.6)
    arrow(ax, (0.17, 0.37), (0.09, 0.60), color=ORANGE, linestyle="--")
    arrow(ax, (0.50, 0.37), (0.58, 0.60), color=BLUE, linestyle="--")
    arrow(ax, (0.83, 0.37), (0.91, 0.60), color=GREEN, linestyle="--")
    text(ax, (0.50, 0.08), "只有候选链条与多层观测在受控实验中一致，才能提高机理结论的证据强度。", fontsize=7.8)
    save(fig, "chap2_soa_coupling_chain")


def draw_demodulation_flow() -> None:
    fig, ax = canvas((7.15, 3.7))
    top = [
        (0.03, "P/S双通道\n原始外差拍频", LIGHT_BLUE, BLUE),
        (0.27, "偏置、幅值、方向\n与时延标定", LIGHT_ORANGE, ORANGE),
        (0.51, "数字本振正交混频\n$f_d$固定", LIGHT_PURPLE, PURPLE),
        (0.75, "低通滤波与\nI/Q提取", LIGHT_GREEN, GREEN),
    ]
    bottom = [
        (0.75, "构造复包络\n$S_x,S_y$", LIGHT_GREEN, GREEN),
        (0.51, "复共轭空间差分\n$C(z,m)$", LIGHT_PURPLE, PURPLE),
        (0.27, "可信度门限与\n功率加权双偏振合成", LIGHT_ORANGE, ORANGE),
        (0.03, "差分相位\n定位、频率与波形", LIGHT_BLUE, BLUE),
    ]
    width = 0.19
    for index, (x, label, face, edge) in enumerate(top):
        box(ax, (x, 0.65), width, 0.21, label, face=face, edge=edge, bold=True, fontsize=7.7)
        text(ax, (x + 0.018, 0.88), str(index + 1), fontsize=8.0, color=edge, bold=True)
        if index < len(top) - 1:
            arrow(ax, (x + width, 0.755), (top[index + 1][0], 0.755))
    arrow(ax, (0.845, 0.65), (0.845, 0.47), connection="arc3")
    for index, (x, label, face, edge) in enumerate(bottom):
        box(ax, (x, 0.25), width, 0.21, label, face=face, edge=edge, bold=True, fontsize=7.7)
        text(ax, (x + 0.018, 0.48), str(index + 5), fontsize=8.0, color=edge, bold=True)
        if index < len(bottom) - 1:
            arrow(ax, (x, 0.355), (bottom[index + 1][0] + width, 0.355))
    text(ax, (0.50, 0.10), "第4章采用统一的解调流程和参数配置评价定位、频率与波形恢复结果。", fontsize=8.1, bold=True)
    save(fig, "chap2_fixed_demodulation_flow")


def architecture_row(
    ax: plt.Axes,
    y: float,
    title: str,
    blocks: list[tuple[str, str, str]],
    *,
    boundary_color: str,
    note: str,
) -> None:
    text(ax, (0.02, y + 0.115), title, fontsize=8.4, bold=True, ha="left")
    box(ax, (0.15, y), 0.82, 0.23, "", face="none", edge=boundary_color, linewidth=1.2, linestyle="--", zorder=1)
    block_width = 0.14
    start = 0.18
    gap = 0.055
    for index, (label, face, edge) in enumerate(blocks):
        x = start + index * (block_width + gap)
        box(ax, (x, y + 0.055), block_width, 0.12, label, face=face, edge=edge, fontsize=7.0, bold=True)
        if index < len(blocks) - 1:
            arrow(ax, (x + block_width, y + 0.115), (x + block_width + gap, y + 0.115), color=boundary_color, width=1.0)
    text(ax, (0.16, y + 0.012), note, fontsize=6.8, color=GRAY, ha="left", va="bottom")


def draw_traditional_proposed_architectures() -> None:
    fig, ax = canvas((7.15, 4.6))

    # Traditional topology: a single-output laser is split into signal and
    # reference branches, with external pulse modulation and EDFA amplification.
    box(ax, (0.02, 0.54), 0.96, 0.40, "", face="white", edge=GRAY, linewidth=1.0, zorder=0)
    text(ax, (0.04, 0.91), "（a）传统EDFA分立光路", fontsize=8.4, bold=True, ha="left")
    box(ax, (0.04, 0.76), 0.11, 0.09, "窄线宽\n激光器", face=LIGHT_BLUE, edge=BLUE, fontsize=6.9, bold=True)
    box(ax, (0.18, 0.76), 0.08, 0.09, "分光器", face=LIGHT_PURPLE, edge=PURPLE, fontsize=6.9, bold=True)
    box(ax, (0.31, 0.79), 0.12, 0.09, "外部脉冲调制\n与AOM移频", face=LIGHT_ORANGE, edge=ORANGE, fontsize=6.5, bold=True)
    box(ax, (0.47, 0.79), 0.09, 0.09, "EDFA", face=LIGHT_RED, edge=RED, fontsize=7.1, bold=True)
    box(ax, (0.60, 0.79), 0.10, 0.09, "环形器", face=LIGHT_GREEN, edge=GREEN, fontsize=6.9, bold=True)
    box(ax, (0.75, 0.79), 0.13, 0.09, "传感光纤", face=LIGHT_GREEN, edge=GREEN, fontsize=6.9, bold=True)
    box(ax, (0.58, 0.60), 0.12, 0.09, "2×2耦合器", face=LIGHT_PURPLE, edge=PURPLE, fontsize=6.7, bold=True)
    box(ax, (0.76, 0.60), 0.12, 0.09, "PBS与双路BPD", face=LIGHT_GREEN, edge=GREEN, fontsize=6.4, bold=True)
    arrow(ax, (0.15, 0.805), (0.18, 0.805), color=BLUE)
    arrow(ax, (0.26, 0.805), (0.31, 0.835), color=RED)
    arrow(ax, (0.43, 0.835), (0.47, 0.835), color=RED)
    arrow(ax, (0.56, 0.835), (0.60, 0.835), color=RED)
    arrow(ax, (0.70, 0.835), (0.75, 0.835), color=RED)
    arrow(ax, (0.22, 0.76), (0.58, 0.645), color=BLUE, connection="angle3,angleA=-90,angleB=180")
    arrow(ax, (0.815, 0.79), (0.70, 0.645), color=GREEN, connection="angle3,angleA=-90,angleB=0")
    arrow(ax, (0.70, 0.645), (0.76, 0.645), color=PURPLE)
    text(ax, (0.38, 0.735), "参考光", fontsize=6.5, color=BLUE)
    text(ax, (0.79, 0.735), "瑞利回波", fontsize=6.5, color=GREEN)
    text(ax, (0.50, 0.565), "外部调制器形成脉冲，EDFA仅承担光功率放大。", fontsize=6.9, color=GRAY)

    # Proposed topology: the two device ports directly provide the signal and
    # reference branches, so no external EDFA is used.
    box(ax, (0.02, 0.05), 0.96, 0.40, "", face="white", edge=BLUE, linewidth=1.1, zorder=0)
    text(ax, (0.04, 0.42), "（b）本文双输出ECL--SOA光路", fontsize=8.4, bold=True, ha="left")
    box(ax, (0.04, 0.20), 0.14, 0.14, "双输出\nECL--SOA", face=LIGHT_BLUE, edge=BLUE, fontsize=7.0, bold=True)
    box(ax, (0.31, 0.29), 0.11, 0.09, "AOM移频", face=LIGHT_ORANGE, edge=ORANGE, fontsize=6.9, bold=True)
    box(ax, (0.47, 0.29), 0.10, 0.09, "环形器", face=LIGHT_GREEN, edge=GREEN, fontsize=6.9, bold=True)
    box(ax, (0.62, 0.29), 0.13, 0.09, "传感光纤", face=LIGHT_GREEN, edge=GREEN, fontsize=6.9, bold=True)
    box(ax, (0.56, 0.11), 0.13, 0.09, "2×2耦合器", face=LIGHT_PURPLE, edge=PURPLE, fontsize=6.7, bold=True)
    box(ax, (0.76, 0.11), 0.12, 0.09, "PBS与双路BPD", face=LIGHT_GREEN, edge=GREEN, fontsize=6.4, bold=True)
    arrow(ax, (0.18, 0.305), (0.31, 0.335), color=RED)
    arrow(ax, (0.42, 0.335), (0.47, 0.335), color=RED)
    arrow(ax, (0.57, 0.335), (0.62, 0.335), color=RED)
    arrow(ax, (0.18, 0.235), (0.56, 0.155), color=BLUE, connection="angle3,angleA=-90,angleB=180")
    arrow(ax, (0.685, 0.29), (0.69, 0.155), color=GREEN, connection="angle3,angleA=-90,angleB=0")
    arrow(ax, (0.69, 0.155), (0.76, 0.155), color=PURPLE)
    text(ax, (0.235, 0.345), "SOA端脉冲信号光", fontsize=6.4, color=RED)
    text(ax, (0.35, 0.185), "LD端连续参考光", fontsize=6.4, color=BLUE)
    text(ax, (0.50, 0.075), "SOA完成放大与电流门控，发射链路不配置EDFA。", fontsize=6.9, color=GRAY)

    save(fig, "chap3_traditional_proposed_architectures")


def timing_bar(
    ax: plt.Axes,
    x0: float,
    x1: float,
    y: float,
    color: str,
    *,
    alpha: float = 0.85,
    hatch: str | None = None,
) -> None:
    ax.add_patch(
        Rectangle(
            (x0, y - 0.018),
            x1 - x0,
            0.036,
            facecolor=color,
            edgecolor=color,
            linewidth=0.8,
            alpha=alpha,
            hatch=hatch,
        )
    )


def timing_panel(
    ax: plt.Axes,
    y: float,
    title: str,
    aom_command: tuple[float, float],
    stable_window: tuple[float, float],
    *,
    note: str,
) -> None:
    box(ax, (0.015, y - 0.115), 0.97, 0.23, "", face="white", edge="#C7CDD3", linewidth=0.8, zorder=0)
    text(ax, (0.03, y + 0.085), title, fontsize=7.8, bold=True, ha="left")
    labels = ["AOM射频命令", "稳定衍射窗口", "SOA光脉冲", "DAQ有效采样"]
    ys = [y + 0.048, y + 0.012, y - 0.024, y - 0.060]
    for label, row_y in zip(labels, ys):
        text(ax, (0.19, row_y), label, fontsize=6.6, ha="right")
        ax.plot([0.22, 0.93], [row_y, row_y], color="#D9DEE3", linewidth=0.6)
    timing_bar(ax, *aom_command, ys[0], ORANGE)
    timing_bar(ax, *stable_window, ys[1], BLUE)
    timing_bar(ax, 0.50, 0.64, ys[2], RED)
    timing_bar(ax, 0.68, 0.89, ys[3], GREEN)
    text(ax, (0.95, y - 0.085), note, fontsize=6.4, color=GRAY, ha="right")


def draw_timing_comparison() -> None:
    fig, ax = canvas((7.15, 5.0))
    timing_panel(
        ax,
        0.78,
        "（a）AOM连续射频",
        (0.22, 0.93),
        (0.22, 0.93),
        note="衍射窗口稳定，但射频功耗与温升持续存在",
    )
    timing_panel(
        ax,
        0.49,
        "（b）命令边沿简单同步",
        (0.50, 0.64),
        (0.55, 0.69),
        note="声场建立滞后，有效光脉冲与稳定窗口仅部分重合",
    )
    timing_panel(
        ax,
        0.20,
        "（c）预补偿协同门控",
        (0.42, 0.72),
        (0.47, 0.77),
        note="提前建立并延迟保持，使SOA光脉冲落入稳定衍射窗口",
    )
    arrow(ax, (0.50, 0.955), (0.64, 0.955), color=INK, width=0.9)
    text(ax, (0.50, 0.955), "时间", fontsize=7.0, ha="right")
    text(ax, (0.42, 0.055), r"$\Delta t_{\mathrm{pre}}$", fontsize=7.2, color=ORANGE)
    text(ax, (0.72, 0.055), r"$\Delta t_{\mathrm{hold}}$", fontsize=7.2, color=ORANGE)
    text(ax, (0.50, 0.015), "示意图不按实际器件响应时间比例绘制，具体提前量与保持量由实验确定。", fontsize=6.8, color=GRAY)
    save(fig, "chap3_coordinated_timing")


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    draw_phi_otdr_principle()
    draw_soa_coupling_chain()
    draw_demodulation_flow()
    draw_traditional_proposed_architectures()
    draw_timing_comparison()


if __name__ == "__main__":
    main()
