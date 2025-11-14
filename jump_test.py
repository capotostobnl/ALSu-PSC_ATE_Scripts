"""Jump Test

Modified M. Capotosto 11-9-2025
Original: T. Caracappy
"""
import os
from time import sleep
from epics import caget, caput, ca
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


def jump_test(dut: DUT, section: list, chan: int, ctx: ReportContext):
    # Jump test PVs:
    CHprefix = "Chan" + str(chan) + ":"
    Shot = dut.pv_prefix + CHprefix + "SS:Trig:Usr"
    DACwfm = dut.pv_prefix + CHprefix + "USR:DAC-Wfm"
    D1wfm = dut.pv_prefix + CHprefix + "USR:DCCT1-Wfm"
    D2wfm = dut.pv_prefix + CHprefix + "USR:DCCT2-Wfm"
    ERRwfm = dut.pv_prefix + CHprefix + "USR:Error-Wfm"
    REGwfm = dut.pv_prefix + CHprefix + "USR:Reg-Wfm"
    VOLTwfm = dut.pv_prefix + CHprefix + "USR:Volt-Wfm"
    GNDwfm = dut.pv_prefix + CHprefix + "USR:Gnd-Wfm"
    SPRwfm = dut.pv_prefix + CHprefix + "USR:Spare-Wfm"
    XMAX = dut.pv_prefix + CHprefix + "SS:WFM-Xmax"
    XMIN = dut.pv_prefix + CHprefix + "SS:WFM-Xmin"
    ACTV = dut.pv_prefix + CHprefix + "UsrTrigActive-I"
    DacSP = dut.pv_prefix + CHprefix + "DAC_SetPt-SP"
    PSMode = dut.pv_prefix + CHprefix + "DAC_OpMode-SP"

    caput(XMIN, 0)  # Set Snapshot Min to 0
    caput(XMAX, 100000)  # Set Snapshot Max to 100000 10KHz Samples
    caput(PSMode, 3, wait=True)  # Set Mode to Jump
    ca.flush_io()

    if dut.num_channels == 2:
        if chan == 1:
            SP = 30.05
        else:
            SP = 50.05
    else:
        SP = 10.05
    caput(DacSP, SP, wait=True)  # Set DAC SP to 0.05 Amps Higher from
    #                 #the previous setting
    ca.flush_io()
    sleep(0.1)
    caput(Shot, 1, wait=True)  # Take the Snapshot.
    sleep(2)
    while caget(ACTV) > 0:  # type: ignore
        sleep(1)
        print("Wating for Jump Snapshot data.....")
    DAC = caget(DACwfm)
    D1 = caget(D1wfm)
    D2 = caget(D2wfm)
    ERR = caget(ERRwfm)
    REG = caget(REGwfm)
    VOLT = caget(VOLTwfm)
    GND = caget(GNDwfm)
    SPR = caget(SPRwfm)

    Tindex = np.argmax(ERR)  # type: ignore
    DACTRAN = []
    ERRTRAN = []
    D1TRAN = []
    D2TRAN = []
    REGTRAN = []
    VTRAN = []
    GTRAN = []
    STRAN = []

    if Tindex > 500 and Tindex < 98000:
        for i in range((Tindex - 500), (Tindex + 500)):
            DACTRAN.append(DAC[i])  # type: ignore
            ERRTRAN.append(ERR[i])  # type: ignore
            D1TRAN.append(D1[i])  # type: ignore
            D2TRAN.append(D2[i])  # type: ignore
            REGTRAN.append(REG[i])  # type: ignore
            VTRAN.append(VOLT[i])  # type: ignore
            GTRAN.append(GND[i])  # type: ignore
            STRAN.append(SPR[i])  # type: ignore

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(DAC)  # type: ignore
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
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(ERR)  # type: ignore
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
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(D1)  # type: ignore
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
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(D2)  # type: ignore
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
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(REG)  # type: ignore
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
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(VOLT)  # type: ignore
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
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    IgndSP = 0.1
    IgndAvg = float(np.mean(GND))  # type: ignore
    print("####################IgndAvg=", IgndAvg, IgndSP)
    Diff = abs(IgndSP - IgndAvg)
    ax1.plot(GND)  # type: ignore
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
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(SPR)  # type: ignore
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
    f.canvas.flush_events()  # ensure all GUI events are handled
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
