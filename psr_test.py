"""Carry out PS Regulation tests..."""

from time import sleep
from epics import caget, caput
from reportlab.platypus import Paragraph, PageBreak, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np


def power_supply_regulation_test(pv_prefix, ch_prefix, chan, props,
                                 good, bad, styles):
    """Test PS Regulation"""
    dac_sp = pv_prefix + ch_prefix + "DAC_SetPt-SP"
    ps_mode = pv_prefix + ch_prefix + "DAC_OpMode-SP"
    # on = pv_prefix + ch_prefix + "DigIn-I.B0"  # **UNUSED??**
    dcct_1 = pv_prefix + ch_prefix + "DCCT1-I"
    dcct_2 = pv_prefix + ch_prefix + "DCCT2-I"
    dac = pv_prefix + ch_prefix + "DAC-I"
    enb = pv_prefix + ch_prefix + "DigOut_ON2-SP"
    prk = pv_prefix + ch_prefix + "DigOut_Park-SP"
    pwr = pv_prefix + ch_prefix + "DigOut_ON1-SP"

    caput(dac_sp, 0)
    caput(enb, 1)
    caput(prk, 1)
    caput(pwr, 1)
    sleep(1)
    # on_stat = caget(on)  #**UNUSED?**
    sleep(5)
    caput(ps_mode, 0)
    caput(prk, 0)
    sp = 10
    caput(dac_sp, sp)
    sleep(10)
    # Collect 1 minute of data:
    lrb = []
    d1_rb = []
    d2_rb = []
    f, ax = plt.subplots(3, 1, figsize=(6, 9.5))
    plt.ion()
    for _ in range(0, 180):
        x = caget([dac, dcct_1, dcct_2])
        lrb.append(x[0])
        d1_rb.append(x[1])
        d2_rb.append(x[2])
        ax[0].clear()
        ax[1].clear()
        ax[2].clear()
        ax[0].plot(lrb)
        ax[1].plot(d1_rb)
        ax[2].plot(d2_rb)
        plt.pause(0.1)
        sleep(0.3)

    plt.ioff()
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    lrb_avg = np.mean(lrb)
    lrb = np.subtract(lrb, lrb_avg)
    lrb = np.multiply(lrb, 1000)
    lrb_err = abs(lrb_avg - sp)
    d1_rb_avg = np.mean(d1_rb)
    d1_rb = np.subtract(d1_rb, d1_rb_avg)
    d1_rb = np.multiply(d1_rb, 1000)
    d1_rb_err = abs(d1_rb_avg + sp)
    d2_rb_avg = np.mean(d2_rb)
    d2_rb = np.subtract(d2_rb, d2_rb_avg)
    d2_rb = np.multiply(d2_rb, 1000)
    d2_rb_err = abs(d2_rb_avg + sp)
    print(lrb_err, d1_rb_err, d2_rb_err)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(lrb)
    ax1.grid(True)
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("(Reading - Average) (mA)")
    ax1.set_title("Loopback Stability (SP=10A)")
    mstr = "Loopback Avg: " + str(round(lrb_avg, 5)) + "A"
    ax1.text(
        0.02,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )
    if lrb_err < 0.050:
        mstr = "Test: |Avg-SP|<50mA?  PASS"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=good,
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
            bbox=bad,
        )

    ax2.hist(lrb, bins=20, color="blue", edgecolor="black")
    ax2.grid(True)
    ax2.set_axisbelow(True)
    ax2.set_xlabel("Deviation from Average (mA)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("Loopback Deviation")
    plt.tight_layout()
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_Loopback_Stability.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(d1_rb)
    ax1.grid(True)
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("(Reading - Average) (mA)")
    ax1.set_title("DCCT1 Stability (SP=10A)")
    mstr = "DCCT1 Avg: " + str(round(d1_rb_avg, 5)) + "A"
    ax1.text(
        0.02,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )
    print("D1RBerr = ", d1_rb_err, d1_rb_avg, sp)
    if d1_rb_err < 0.050:
        mstr = "Test: |Avg-SP|<50mA?  PASS"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=good,
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
            bbox=bad,
        )

    ax2.hist(d1_rb, bins=20, color="blue", edgecolor="black")
    ax2.grid(True)
    ax2.set_axisbelow(True)
    ax2.set_xlabel("Deviation from Average (mA)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("DCC1 Deviation")
    plt.tight_layout()
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_DCCT1_Stability.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    f = plt.figure(figsize=(8, 4))
    gs = GridSpec(1, 3, figure=f)
    ax1 = f.add_subplot(gs[0, 0:2])
    ax2 = f.add_subplot(gs[0, 2])

    ax1.plot(d2_rb)
    ax1.grid(True)
    ax2.set_axisbelow(True)
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("(Reading - Average) (mA)")
    ax1.set_title("DCCT2 Stability (SP=10A)")
    mstr = "DCCT2 Avg: " + str(round(d2_rb_avg, 5)) + "A"
    ax1.text(
        0.02,
        0.97,
        mstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )
    if d2_rb_err < 0.050:
        mstr = "Test: |Avg-SP|<50mA?  PASS"
        ax1.text(
            0.5,
            0.07,
            mstr,
            transform=ax1.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=good,
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
            bbox=bad,
        )

    ax2.hist(d2_rb, bins=20, color="blue", edgecolor="black")
    ax2.grid(True)
    ax2.set_xlabel("Deviation from Average (mA)")
    ax2.set_ylabel("Frequency")
    ax2.set_title("DCC2 Deviation")
    plt.tight_layout()
    plt.pause(0.1)
    f.savefig("Chan" + str(chan) + "_DCCT2_Stability.png")
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    mstr = "Power Supply Regulation for Channel " + str(chan) + ":"

    p_style = ParagraphStyle(
        "Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=16,  # 👈 Set font size here
        leading=20,  # Optional: line spacing
        alignment=TA_CENTER,  # 👈 Centers the paragraph horizontally
    )

    title = Paragraph(mstr, p_style)

    local_elements = []
    local_elements.append(PageBreak())
    local_elements.append(title)
    im = Image("Chan" + str(chan) + "_Loopback_Stability.png", 7 * inch,
               3 * inch)
    local_elements.append(im)
    local_elements.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_DCCT1_Stability.png", 7 * inch, 3 * inch)
    local_elements.append(im)
    local_elements.append(Spacer(width=1, height=0.1 * inch))
    im = Image("Chan" + str(chan) + "_DCCT1_Stability.png", 7 * inch, 3 * inch)
    local_elements.append(im)
    local_elements.append(Spacer(width=1, height=0.1 * inch))
    return local_elements
