"""Carry out smooth ramp tests..."""

from time import sleep
from epics import caget, caput
from reportlab.platypus import Paragraph, PageBreak, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
import matplotlib.pyplot as plt


def smooth_ramp_test(pv_prefix, ch_prefix, chan,
                     props, styles, i_gnd_sp):
    """Smooth ramp testing"""
    dac_sp = pv_prefix + ch_prefix + "DAC_SetPt-SP"
    RATE = pv_prefix + ch_prefix + "SF:AmpsperSec-SP"
    ps_mode = pv_prefix + ch_prefix + "DAC_OpMode-SP"
    Shot = pv_prefix + ch_prefix + "SS:Trig:Usr"
    DACwfm = pv_prefix + ch_prefix + "USR:DAC-Wfm"
    D1wfm = pv_prefix + ch_prefix + "USR:DCCT1-Wfm"
    D2wfm = pv_prefix + ch_prefix + "USR:DCCT2-Wfm"
    ERRwfm = pv_prefix + ch_prefix + "USR:Error-Wfm"
    REGwfm = pv_prefix + ch_prefix + "USR:Reg-Wfm"
    VOLTwfm = pv_prefix + ch_prefix + "USR:Volt-Wfm"
    GNDwfm = pv_prefix + ch_prefix + "USR:Gnd-Wfm"
    SPRwfm = pv_prefix + ch_prefix + "USR:Spare-Wfm"
    ACTV = pv_prefix + ch_prefix + "UsrTrigActive-I"

    caput(ps_mode, 0)  # Set PS Mode to SMOOTH
    caput(RATE, 10)  # Set Ramp Rate to 10 Amps/Sec
    caput(dac_sp, -23.9)  # Set DAC to -23.9 Amps
    sleep(10)  # Wait 10 Seconds for Ramp to Complete
    caput(dac_sp, 23.9)  # Set DAC SP to +23.9 Amps
    sleep(2)  # Wait 2 Seconds before taking Snapshot
    caput(Shot, 1)  # Take the Snapshot.
    sleep(2)
    while caget(ACTV) > 0:
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
    ax.plot(DAC)
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("DAC Loopback Smooth Test")
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_DAC_Smooth.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(D1)
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("DCCT1 Smooth Test")
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_DCCT1_Smooth.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(D2)
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("DCCT2 Smooth Test")
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_DCCT2_Smooth.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ERR)
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("ERROR Smooth Test")
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_ERROR_Smooth.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(REG)
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("REG Smooth Test")
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_REG_Smooth.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(VOLT)
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Voltage (V)")
    ax.set_title("PS VOLT Smooth Test")
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_VOLT_Smooth.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(GND)
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("IGND Smooth Test")
    mstr = "Ignd SP: " + str(round(i_gnd_sp, 3)) + "A"
    ax.text(
        0.02,
        0.97,
        mstr,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_IGND_Smooth.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f, ax = plt.subplots(figsize=(8, 4))
    ax.plot(SPR)
    ax.grid(True)
    ax.set_xlabel("10KHz Samples")
    ax.set_ylabel("Current (A)")
    ax.set_title("SPARE Smooth Test")
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_SPARE_Smooth.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    mstr = "Smooth Test Results:"
    Pstyle = ParagraphStyle(
        "Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=16,  # 👈 Set font size here
        leading=20,  # Optional: line spacing
        alignment=TA_CENTER,  # 👈 Centers the paragraph horizontally
    )

    title = Paragraph(mstr, Pstyle)
    elements_local = []
    elements_local.append(PageBreak())
    elements_local.append(title)
    im = Image("Chan" + str(chan) + "_DAC_Smooth.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_DCCT1_Smooth.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_DCCT1_Smooth.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))

    elements_local.append(PageBreak())
    elements_local.append(title)
    im = Image("Chan" + str(chan) + "_ERROR_Smooth.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_REG_Smooth.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_VOLT_Smooth.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))

    elements_local.append(PageBreak())
    elements_local.append(title)
    im = Image("Chan" + str(chan) + "_IGND_Smooth.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    elements_local.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_SPARE_Smooth.png", 7 * inch, 3 * inch)
    elements_local.append(im)
    return elements_local
