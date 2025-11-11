"""Smooth Ramp Test Submodule

Modified M. Capotosto 11-9-2025
Original: T. Caracappa
"""

import os
from time import sleep
from epics import caget, caput
import numpy as np
from matplotlib import pyplot as plt
from reportlab.platypus import Image, PageBreak
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from report_generator import ReportContext
from initialize_dut import DUT


def smooth_ramp_test(dut: DUT, section: list, chan: int, ctx: ReportContext):
    CHprefix = "Chan" + str(chan) + ":"
    RATE = dut.PVprefix + CHprefix + "SF:AmpsperSec-SP"
    Shot = dut.PVprefix + CHprefix + "SS:Trig:Usr"
    DACwfm = dut.PVprefix + CHprefix + "USR:DAC-Wfm"
    D1wfm = dut.PVprefix + CHprefix + "USR:DCCT1-Wfm"
    D2wfm = dut.PVprefix + CHprefix + "USR:DCCT2-Wfm"
    ERRwfm = dut.PVprefix + CHprefix + "USR:Error-Wfm"
    REGwfm = dut.PVprefix + CHprefix + "USR:Reg-Wfm"
    VOLTwfm = dut.PVprefix + CHprefix + "USR:Volt-Wfm"
    GNDwfm = dut.PVprefix + CHprefix + "USR:Gnd-Wfm"
    SPRwfm = dut.PVprefix + CHprefix + "USR:Spare-Wfm"
    ACTV = dut.PVprefix + CHprefix + "UsrTrigActive-I"
    DacSP = dut.PVprefix + CHprefix + "DAC_SetPt-SP"
    PSMode = dut.PVprefix + CHprefix + "DAC_OpMode-SP"
    AteIgndVal = "PSCtest:Ignd-SP"

    caput(PSMode, 0)  # Set PS Mode to SMOOTH
    caput(RATE, 10)  # Set Ramp Rate to 10 Amps/Sec
    if dut.num_channels == 2:
        if chan == 1:
            caput(DacSP, 0)  # Set DAC to 0 Amps
            sleep(10)
            caput(DacSP, 49.9)  # Set DAC SP to +49.9 Amps
        else:
            caput(RATE, 20)  # Set Ramp Rate to 20 Amps/Sec
            caput(DacSP, 0)  # Set DAC to 0 Amps
            sleep(10)
            caput(DacSP, 99.9)  # Set DAC SP to +99.9 Amps
    else:
        caput(DacSP, -23.9)  # Set DAC to -23.9 Amps
        sleep(10)  # Wait 10 Seconds for Ramp to Complete
        caput(DacSP, 23.9)  # Set DAC SP to +23.9 Amps
    sleep(2)  # Wait 2 Seconds before taking Snapshot
    caput(Shot, 1)  # Take the Snapshot.
    sleep(2)
    while caget(ACTV) > 0:  # type: ignore
        sleep(1)
        print("Wating for Smooth Snapshot data.....")

    DAC = caget(DACwfm)
    D1 = caget(D1wfm)
    D2 = caget(D2wfm)
    ERR = caget(ERRwfm)
    REG = caget(REGwfm)
    VOLT = caget(VOLTwfm)
    GND = caget(GNDwfm)
    SPR = caget(SPRwfm)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(DAC)  # type: ignore
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("DAC Loopback Smooth Test")
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_DAC_Smooth.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(D1)  # type: ignore
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("DCCT1 Smooth Test")
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_DCCT1_Smooth.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(D2)  # type: ignore
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("DCCT2 Smooth Test")
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_DCCT2_Smooth.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ERR)  # type: ignore
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("ERROR Smooth Test")
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_ERROR_Smooth.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(REG)  # type: ignore
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("REG Smooth Test")
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_REG_Smooth.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(VOLT)  # type: ignore
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Voltage (V)")
    ax.set_title("PS VOLT Smooth Test")
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_VOLT_Smooth.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    IgndSP = 0.1
    caput(AteIgndVal, IgndSP)
    IgndSP = 0.1

    f, ax = plt.subplots(figsize=(8, 4))
    IgndAvg = float(np.mean(GND))  # type: ignore
    Diff = abs(IgndSP - IgndAvg)
    ax.plot(GND)  # type: ignore
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("IGND Smooth Test")
    mstr = "Ignd SP: " + str(round(IgndSP, 3)) + "A"
    ax.text(
        0.02,
        0.97,
        mstr,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=ctx.theme.props
    )
    mstr = "Ignd Wfm Avg: " + str(round(IgndAvg, 3)) + "A"
    ax.text(
        0.6,
        0.97,
        mstr,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=ctx.theme.props,
    )
    if Diff > 0.05:
        mstr = "Test: |IgndSP-IgndAvg|<50mA? : FAIL"
        ax.text(
            0.4,
            0.07,
            mstr,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.bad,
        )
    else:
        mstr = "Test: |IgndSP-IgndAvg|<50mA? : PASS"
        ax.text(
            0.4,
            0.07,
            mstr,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.good,
        )

    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_IGND_Smooth.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(SPR)  # type: ignore
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("SPARE Smooth Test")
    plt.pause(0.1)
    save_path = os.path.join(dut.raw_data_dir,
                             f"Chan{chan}_SPARE_Smooth.png")
    f.savefig(save_path)
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    base_style = ctx.styles["Normal"]
    mstr = "Smooth Test Results:"
    Pstyle = ParagraphStyle(
        "Custom",
        parent=base_style,
        fontName="Helvetica",
        fontSize=16,  # 👈 Set font size here
        leading=20,  # Optional: line spacing
        alignment=TA_CENTER,  # 👈 Centers the paragraph horizontally
    )

    title = Paragraph(mstr, Pstyle)
    section.append(PageBreak())
    section.append(title)
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_DAC_Smooth.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_DCCT1_Smooth.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_DCCT2_Smooth.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))

    section.append(PageBreak())
    section.append(title)
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_ERROR_Smooth.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_REG_Smooth.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_VOLT_Smooth.png"), 7 * inch, 3 * inch)
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))

    section.append(PageBreak())
    section.append(title)
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_IGND_Smooth.png"),
               7 * inch, 3 * inch)  # type: ignore
    section.append(im)
    section.append(Spacer(width=1, height=0.1 * inch))
    im = Image(os.path.join(dut.raw_data_dir,
               f"Chan{chan}_SPARE_Smooth.png"), 7 * inch, 3 * inch)
    section.append(im)
    caput(DacSP, 0)  # Channel test complete.  Set DAC SP to 0 Amps
