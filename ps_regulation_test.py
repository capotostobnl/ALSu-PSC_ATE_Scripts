"""Power Supply Regulation Test

Modified M. Capotosto 11-9-2025
Original: T. Caracappa
"""
import os
from time import sleep
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
from ate_epics import ATE


def ps_regulation_test(dut: DUT, ate: ATE, section: list, chan: int,
                       ctx: ReportContext):
    assert dut.psc is not None
    print(f"Preparing PSC Channel {chan} for Regulation test...")
    ate.set_ignd_channel(chan)
    ate.set_ignd_value(0, chan, dut)
    print("ATE ignd Set...")
    dut.psc.set_dac_setpt(1, 0)
    dut.psc.set_rate(chan, 10)
    dut.psc.set_dac_setpt(chan, 0)

    for i in range(1, dut.num_channels+1):
        dut.psc.set_power_on1(i, 1)
        dut.psc.set_enable_on2(i, 1)
        dut.psc.set_op_mode(i, 0)
        dut.psc.set_park(i, 0)
        dut.psc.set_dac_setpt(i, 0)
    while True:
        # Check for any faults on all 4 channels. If there's a fault, clear
        # before continuing...
        all_clear = True

        for ch in range(1, dut.num_channels+1):   # 1, 2, 3, 4
            faults = dut.psc.get_latched_faults(ch)

            if faults != 0:
                print(f"Clearing latched faults on CH{ch}: 0x{faults:X}")

                dut.psc.set_reset(ch, 1)
                dut.psc.clear_faults(ch, 1)
                sleep(0.5)
                dut.psc.clear_faults(ch, 0)
                dut.psc.set_reset(ch, 0)

                all_clear = False   # keep looping until all channels clear

        if all_clear:
            break

    sleep(0.2)   # optional short slowdown
    if dut.num_channels == 2:
        if chan == 1:
            SP = 30
        else:
            SP = 50
    else:
        SP = 10
    dut.psc.set_dac_setpt(chan, SP)
    print("PSC rate, DAC SP, Enable, Park, and Power bits set...")
    sleep(10)
    # Collect 1 minute of data:
    print(f"Preparing to collect 60 seconds of data for Channel {chan}")
    LRB = []
    D1RB = []
    D2RB = []
    f, ax = plt.subplots(3, 1, figsize=(6, 9.5))
    plt.ion()
    print("*******************************************\n")
    print(f"Channel {chan}: ")
    for i in range(0, 180):
        print(f"Collecting Regulation Data for Channel {chan} "
              f"datapoint {i} of 180...")
        v_dac = dut.psc.get_dac(chan)
        v_dcct1 = dut.psc.get_dcct1(chan)
        v_dcct2 = dut.psc.get_dcct2(chan)
        X = [v_dac, v_dcct1, v_dcct2]
        LRB.append(X[0])
        D1RB.append(X[1])
        D2RB.append(X[2])
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
