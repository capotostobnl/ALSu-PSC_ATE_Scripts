"""Jump Test

Modified M. Capotosto 11-9-2025
Original: T. Caracappy
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


def jump_test(dut: DUT, ate: ATE, section: list, chan: int,
              ctx: ReportContext):
    assert dut.psc is not None

    IgndSP = 0.1
    ate.set_ignd_channel(chan)
    sleep(0.5)
    ate.set_ignd_value(IgndSP, chan, dut)
    sleep(0.5)

    WfmPV = dut.psc.WfmPV
    dut.psc.set_wfm_xmin(chan, 0)
    dut.psc.set_wfm_xmax(chan, 100000)
    dut.psc.set_op_mode(chan, 3)  # Set Mode to Jump
    dut.psc.flush_io()

    if dut.num_channels == 2:
        if chan == 1:
            SP = 30.05
        else:
            SP = 50.05
    else:
        SP = 10.05

    dut.psc.set_dac_setpt(chan, SP)
    dut.psc.flush_io()
    sleep(0.1)
    dut.psc.user_shot(chan)
    sleep(2)
    while dut.psc.is_user_trig_active(chan) > 0:
        sleep(1)
        print("Waiting for Jump Snapshot data.....")
    DAC = dut.psc.get_wfm(chan, WfmPV.DAC)
    D1 = dut.psc.get_wfm(chan, WfmPV.DCCT1)
    D2 = dut.psc.get_wfm(chan, WfmPV.DCCT2)
    ERR = dut.psc.get_wfm(chan, WfmPV.ERR)
    REG = dut.psc.get_wfm(chan, WfmPV.REG)
    VOLT = dut.psc.get_wfm(chan, WfmPV.VOLT)
    GND = dut.psc.get_wfm(chan, WfmPV.GND)
    SPR = dut.psc.get_wfm(chan, WfmPV.SPARE)

    # ----------------------------------------------------------
    # Find Tindex based on DAC jump (largest absolute derivative)
    # ----------------------------------------------------------
    a = np.asarray(DAC)
    d = np.diff(a)
    Tindex = int(np.argmax(np.abs(d)))     # <-- the correct jump location

    # ----------------------------------------------------------
    # HARD-CODED original window: Tindex ± 500
    # ----------------------------------------------------------
    start = max(0, Tindex - 500)
    end = min(len(a), Tindex + 500)

    DACTRAN = a[start:end]
    ERRTRAN = np.asarray(ERR)[start:end]
    D1TRAN = np.asarray(D1)[start:end]
    D2TRAN = np.asarray(D2)[start:end]
    REGTRAN = np.asarray(REG)[start:end]
    VTRAN = np.asarray(VOLT)[start:end]
    GTRAN = np.asarray(GND)[start:end]
    STRAN = np.asarray(SPR)[start:end]

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(DAC)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Current (A)")
    ax1.set_title("DAC Loopback Jump Test")

    ax2.plot(DACTRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Current (A)")
    ax2.set_title("DAC Transition")
    plt.tight_layout()
    plt.pause(0.1)

    save_path = os.path.join(dut.raw_data_dir, f"Chan{chan}"
                             "_DAC_Jump.png")
    f.savefig(save_path)
    plt.close(f)
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(ERR)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Current (A)")
    ax1.set_title("ERROR Jump Test")

    ax2.plot(ERRTRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Current (A)")
    ax2.set_title("Error Transition")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_ERROR_Jump.png")
    f.savefig(save_path)
    plt.close(f)
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(D1)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Current (A)")
    ax1.set_title("DCCT1 Jump")

    ax2.plot(D1TRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Current (A)")
    ax2.set_title("DCCT1 Transition")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_DCCT1_Jump.png")
    f.savefig(save_path)
    plt.close(f)
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(D2)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Current (A)")
    ax1.set_title("DCCT2 Jump Test")

    ax2.plot(D2TRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Current (A)")
    ax2.set_title("DCCT2 Transition")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_DCCT2_Jump.png")
    f.savefig(save_path)
    plt.close(f)
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(REG)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Current (A)")
    ax1.set_title("Regulator Jump Test")

    ax2.plot(REGTRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Current (A)")
    ax2.set_title("REG Transition")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_REG_Jump.png")
    f.savefig(save_path)
    plt.close(f)
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(VOLT)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Voltage (V)")
    ax1.set_title("PS VOLT Jump Test")

    ax2.plot(VTRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Voltage (V)")
    ax2.set_title("VOLT Transition")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_VOLT_Jump.png")
    f.savefig(save_path)
    plt.close(f)
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    IgndAvg = float(np.mean(GND))
    print("####################IgndAvg=", IgndAvg, IgndSP)
    Diff = abs(IgndSP - IgndAvg)
    ax1.plot(GND)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Current (A)")
    ax1.set_title("IGND Jump Test")
    mstr = "Ignd SP: " + str(round(IgndSP, 3)) + "A"
    ax1.text(
        0.02,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=ctx.theme.props,
    )
    mstr = "Ignd Wfm Avg: " + str(round(IgndAvg, 3)) + "A"
    ax1.text(
        0.6,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=ctx.theme.props,
    )
    if Diff > 0.05:
        mstr = "Test: |IgndSP-IgndAvg|<50mA? : FAIL"
        ax1.text(
            0.3,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.bad,
        )
    else:
        mstr = "Test: |IgndSP-IgndAvg|<50mA? : PASS"
        ax1.text(
            0.3,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.good,
        )

    ax2.plot(GTRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Current (A)")
    ax2.set_title("IGND Transition")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_IGND_Jump.png")
    f.savefig(save_path)
    plt.close(f)
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(SPR)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Current (A)")
    ax1.set_title("SPARE Jump Test")

    ax2.plot(STRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Current (A)")
    ax2.set_title("SPARE Transition")
    plt.tight_layout()
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_SPARE_Jump.png")
    f.savefig(save_path)
    plt.close(f)
    plt.pause(0.1)
    base_style = ctx.styles["Normal"]
    mstr = "Jump Test Results:"
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
               f"Chan{chan}_DAC_Jump.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_DCCT1_Jump.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_DCCT2_Jump.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))

    section.append(PageBreak())
    section.append(title)
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_ERROR_Jump.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_REG_Jump.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_VOLT_Jump.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))

    section.append(PageBreak())
    section.append(title)
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_IGND_Jump.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_SPARE_Jump.png"), 7 * inch, 3 * inch)
    section.append(im)
