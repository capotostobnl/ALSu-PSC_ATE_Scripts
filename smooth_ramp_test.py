"""Smooth Ramp Test Submodule

Modified M. Capotosto 11-9-2025
Original: T. Caracappa
"""

import os
from time import sleep
import numpy as np
from matplotlib import pyplot as plt
from reportlab.platypus import Image, PageBreak
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from report_generator import ReportContext
from initialize_dut import DUT
from ate_epics import ATE


def smooth_ramp_test(dut: DUT, ate: ATE, section: list,
                     chan: int, ctx: ReportContext):
    assert dut.psc is not None

    IgndSP = 0.1
    ate.set_ignd_channel(chan)
    sleep(0.5)
    ate.set_ignd_value(IgndSP, chan, dut)
    sleep(0.1)

    WfmPV = dut.psc.WfmPV
    dut.psc.set_op_mode(chan, 0)  # Set PS Mode to SMOOTH
    dut.psc.set_rate(chan, 10)  # Set Ramp Rate to 10 Amps/Sec

    if dut.num_channels == 2:
        if chan == 1:
            dut.psc.set_dac_setpt(chan, 0)  # Set DAC to 0 Amps
            sleep(10)
            dut.psc.set_dac_setpt(chan, 49.9)  # Set DAC SP to +49.9 Amps
        else:
            dut.psc.set_rate(chan, 20)  # Set Ramp Rate to 20 Amps/Sec
            dut.psc.set_dac_setpt(chan, 0)  # Set DAC to 0 Amps
            sleep(10)
            dut.psc.set_dac_setpt(chan, 99.9)  # Set DAC SP to +99.9 Amps
    else:
        dut.psc.set_dac_setpt(chan, -23.9)  # Set DAC to -23.9 Amps
        sleep(10)  # Wait 10 Seconds for Ramp to Complete
        dut.psc.set_dac_setpt(chan, 23.9)  # Set DAC SP to +23.9 Amps
    sleep(2)  # Wait 2 Seconds before taking Snapshot
    dut.psc.user_shot(chan)  # Take the Snapshot.
    sleep(2)
    while dut.psc.is_user_trig_active(chan) > 0:
        sleep(1)
        print("Wating for Smooth Snapshot data.....")

    DAC = dut.psc.get_wfm(chan, WfmPV.DAC)
    D1 = dut.psc.get_wfm(chan, WfmPV.DCCT1)
    D2 = dut.psc.get_wfm(chan, WfmPV.DCCT2)
    ERR = dut.psc.get_wfm(chan, WfmPV.ERR)
    REG = dut.psc.get_wfm(chan, WfmPV.REG)
    VOLT = dut.psc.get_wfm(chan, WfmPV.VOLT)
    GND = dut.psc.get_wfm(chan, WfmPV.GND)
    SPR = dut.psc.get_wfm(chan, WfmPV.SPARE)

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
    plt.pause(0.1)

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
    dut.psc.set_dac_setpt(chan, 0)
