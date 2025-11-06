"""Carry out jump tests..."""

from time import sleep
from epics import caget, caput
from reportlab.platypus import Paragraph, PageBreak, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np


def jump_test(pv_prefix, ch_prefix, chan, props, styles, i_gnd_sp):
    """Carry out jump test testing"""
    dac_sp = pv_prefix + ch_prefix + "DAC_SetPt-SP"
    Shot = pv_prefix + ch_prefix + "SS:Trig:Usr"
    DACwfm = pv_prefix + ch_prefix + "USR:DAC-Wfm"
    D1wfm = pv_prefix + ch_prefix + "USR:DCCT1-Wfm"
    D2wfm = pv_prefix + ch_prefix + "USR:DCCT2-Wfm"
    ERRwfm = pv_prefix + ch_prefix + "USR:Error-Wfm"
    REGwfm = pv_prefix + ch_prefix + "USR:Reg-Wfm"
    VOLTwfm = pv_prefix + ch_prefix + "USR:Volt-Wfm"
    GNDwfm = pv_prefix + ch_prefix + "USR:Gnd-Wfm"
    SPRwfm = pv_prefix + ch_prefix + "USR:Spare-Wfm"
    XMAX = pv_prefix + ch_prefix + "SS:WFM-Xmax"
    XMIN = pv_prefix + ch_prefix + "SS:WFM-Xmin"
    ACTV = pv_prefix + ch_prefix + "UsrTrigActive-I"
    ps_mode = pv_prefix + ch_prefix + "DAC_OpMode-SP"

    caput(XMIN, 0)  # Set Snapshot Min to 0
    caput(XMAX, 100000)  # Set Snapshot Max to 100000 10KHz Samples
    caput(ps_mode, 3)  # Set Mode to Jump
    caput(dac_sp, 10.05)  # Set DAC SP to 10.05 Amps (from 10.0 Amps)
    sleep(0.1)
    caput(Shot, 1)  # Take the Snapshot.
    sleep(2)
    while caget(ACTV) > 0:
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

    Tindex = np.argmax(ERR)
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
            DACTRAN.append(DAC[i])
            ERRTRAN.append(ERR[i])
            D1TRAN.append(D1[i])
            D2TRAN.append(D2[i])
            REGTRAN.append(REG[i])
            VTRAN.append(VOLT[i])
            GTRAN.append(GND[i])
            STRAN.append(SPR[i])

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
    f.savefig("Chan" + str(chan) + "_DAC_Jump.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
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
    f.savefig("Chan" + str(chan) + "_ERROR_Jump.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
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
    f.savefig("Chan" + str(chan) + "_DCCT1_Jump.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
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
    f.savefig("Chan" + str(chan) + "_DCCT2_Jump.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
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
    f.savefig("Chan" + str(chan) + "_REG_Jump.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
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
    f.savefig("Chan" + str(chan) + "_VOLT_Jump.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(GND)
    ax1.grid(True)
    ax1.set_xlabel("10KHz Samples")
    ax1.set_ylabel("Current (A)")
    ax1.set_title("IGND Jump Test")
    mstr = "Ignd SP: " + str(round(i_gnd_sp, 3)) + "A"
    ax1.text(
        0.02,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )

    ax2.plot(GTRAN)
    ax2.grid(True)
    ax2.set_xlabel("10KHz Samples")
    ax2.set_ylabel("Current (A)")
    ax2.set_title("IGND Transition")
    plt.tight_layout()
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_IGND_Jump.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
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
    f.savefig("Chan" + str(chan) + "_SPARE_Jump.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    mstr = "Jump Test Results:"
    p_style = ParagraphStyle(
        "Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=16,  # 👈 Set font size here
        leading=20,  # Optional: line spacing
        alignment=TA_CENTER,  # 👈 Centers the paragraph horizontally
    )
    elements_local = []
    title = Paragraph(mstr, p_style)
    elements_local.append(PageBreak())
    elements_local.append(title)
    im = Image("Chan" + str(chan) + "_DAC_Jump.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_DCCT1_Jump.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_DCCT1_Jump.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))

    elements_local.append(PageBreak())
    elements_local.append(title)
    im = Image("Chan" + str(chan) + "_ERROR_Jump.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_REG_Jump.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_VOLT_Jump.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))

    elements_local.append(PageBreak())
    elements_local.append(title)
    im = Image("Chan" + str(chan) + "_IGND_Jump.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_SPARE_Jump.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    return elements_local
