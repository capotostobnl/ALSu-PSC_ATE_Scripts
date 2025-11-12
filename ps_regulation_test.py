"""Power Supply Regulation Test

Modified M. Capotosto 11-9-2025
Original: T. Caracappa
"""
import os
from time import sleep
from epics import caget, caput
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from reportlab.platypus import Image, PageBreak
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from report_generator import ReportContext
from initialize_dut import DUT


def ps_regulation_test(dut: DUT, section: list, chan: int, ctx: ReportContext):
    CHprefix = "Chan" + str(chan) + ":"
    PWR = dut.pv_prefix + CHprefix + "DigOut_ON1-SP"
    ENB = dut.pv_prefix + CHprefix + "DigOut_ON2-SP"
    PRK = dut.pv_prefix + CHprefix + "DigOut_Park-SP"

    DacSP = dut.pv_prefix + CHprefix + "DAC_SetPt-SP"
    PSMode = dut.pv_prefix + CHprefix + "DAC_OpMode-SP"
    EXT = dut.pv_prefix + CHprefix + "DigOut_Spare-SP"  # noqa: F841
    ON = dut.pv_prefix + CHprefix + "DigIn-I.B0"
    DCCT1 = dut.pv_prefix + CHprefix + "DCCT1-I"
    DCCT2 = dut.pv_prefix + CHprefix + "DCCT2-I"
    DAC = dut.pv_prefix + CHprefix + "DAC-I"
    RATE = dut.pv_prefix + CHprefix + "SF:AmpsperSec-SP"
    caput(RATE, 10)
    caput(DacSP, 0)
    caput(ENB, 1)
    caput(PRK, 1)
    caput(PWR, 1)
    sleep(1)
    ONstat = caget(ON)  # noqa: F841
    sleep(5)
    caput(PSMode, 0)
    caput(PRK, 0)
    if dut.num_channels == 2:
        if chan == 1:
            SP = 30
        else:
            SP = 50
    else:
        SP = 10
    caput(DacSP, SP)
    sleep(10)
    # Collect 1 minute of data:
    LRB = []
    D1RB = []
    D2RB = []
    f, ax = plt.subplots(3, 1, figsize=(6, 9.5))
    plt.ion()
    for i in range(0, 180):
        v_dac = caget(DAC)
        v_dcct1 = caget(DCCT1)
        v_dcct2 = caget(DCCT2)
        X = [v_dac, v_dcct1, v_dcct2]
        LRB.append(X[0])  # type: ignore
        D1RB.append(X[1])  # type: ignore
        D2RB.append(X[2])  # type: ignore
        ax[0].clear()
        ax[1].clear()
        ax[2].clear()
        ax[0].plot(LRB)
        ax[1].plot(D1RB)
        ax[2].plot(D2RB)
        plt.pause(0.1)
        sleep(0.3)

    plt.ioff()
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    LRBavg = np.mean(LRB)
    LRB = np.subtract(LRB, LRBavg)
    LRB = np.multiply(LRB, 1000)
    LRBerr = abs(LRBavg - SP)
    D1RBavg = np.mean(D1RB)
    D1RB = np.subtract(D1RB, D1RBavg)
    D1RB = np.multiply(D1RB, 1000)
    D1RBerr = abs(D1RBavg + SP)
    D2RBavg = np.mean(D2RB)
    D2RB = np.subtract(D2RB, D2RBavg)
    D2RB = np.multiply(D2RB, 1000)
    D2RBerr = abs(D2RBavg + SP)
    print(LRBerr, D1RBerr, D2RBerr)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(LRB)
    ax1.grid(True)
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("(Reading - Average) (mA)")
    ax1.set_title("Loopback Stability (SP=" + str(SP) + "A)")
    mstr = "Loopback Avg: " + str(round(LRBavg, 5)) + "A"
    ax1.text(
        0.02,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=ctx.theme.props,
    )
    if LRBerr < 0.050:
        mstr = "Test: |Avg-SP|<50mA?  PASS"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.good,
        )
    else:
        mstr = "Test: |Avg-SP|<50mA?  FAIL"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.bad,
        )

    ax2.hist(LRB, bins=20, color="blue", edgecolor="black")
    ax2.grid(True)
    ax2.set_axisbelow(True)
    ax2.set_xlabel("Deviation from Average (mA)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Loopback Deviation")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_Loopback_Stability.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(D1RB)
    ax1.grid(True)
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("(Reading - Average) (mA)")
    ax1.set_title("DCCT1 Stability (SP=" + str(SP) + "A)")
    mstr = "DCCT1 Avg: " + str(round(D1RBavg, 5)) + "A"
    ax1.text(
        0.02,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=ctx.theme.props,
    )
    print("D1RBerr = ", D1RBerr, D1RBavg, SP)
    if D1RBerr < 0.050:
        mstr = "Test: |Avg-SP|<50mA?  PASS"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.good,
        )
    else:
        mstr = "Test: |Avg-SP|<50mA?  FAIL"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.bad,
        )

    ax2.hist(D1RB, bins=20, color="blue", edgecolor="black")
    ax2.grid(True)
    ax2.set_axisbelow(True)
    ax2.set_xlabel("Deviation from Average (mA)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("DCCT1 Deviation")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_DCCT1_Stability.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(D2RB)
    ax1.grid(True)
    ax2.set_axisbelow(True)
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("(Reading - Average) (mA)")
    ax1.set_title("DCCT2 Stability (SP=" + str(SP) + "A)")
    mstr = "DCCT2 Avg: " + str(round(D2RBavg, 5)) + "A"
    ax1.text(
        0.02,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=ctx.theme.props,
    )
    if D2RBerr < 0.050:
        mstr = "Test: |Avg-SP|<50mA?  PASS"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.good,
        )
    else:
        mstr = "Test: |Avg-SP|<50mA?  FAIL"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.bad,
        )

    ax2.hist(D2RB, bins=20, color="blue", edgecolor="black")
    ax2.grid(True)
    ax2.set_xlabel("Deviation from Average (mA)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("DCCT2 Deviation")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_DCCT2_Stability.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    mstr = "Power Supply Regulation for Channel " + str(chan) + ":"

    base_style = ctx.styles["Normal"]

    Pstyle = ParagraphStyle(
        "Custom",
        parent=base_style,
        fontName="Helvetica",
        fontSize=16,
        leading=20,  # Optional: line spacing
        alignment=TA_CENTER,
    )

    title = Paragraph(mstr, Pstyle)
    section.append(PageBreak())
    section.append(title)

    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_Loopback_Stability.png"),
               7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_DCCT1_Stability.png"),
               7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_DCCT2_Stability.png"),
               7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
