"""Carry out fault tests..."""

from time import sleep
from epics import caget, caput
from reportlab.lib.pagesizes import inch
from reportlab.platypus import (
    Table, Spacer)
from reportlab.lib import colors


def fault_tests(pv_prefix, ch_prefix, chan):
    """
    # ATE Fault Tests:
    """
    live_fault = pv_prefix + ch_prefix + "FaultsLive-I"
    lat_fault = pv_prefix + ch_prefix + "FaultsLat-I"
    clr_fault = pv_prefix + ch_prefix + "FaultClear-SP"
    fault_1 = pv_prefix + ch_prefix + "FaultMask:B7-SP"
    fault_2 = pv_prefix + ch_prefix + "FaultMask:B8-SP"
    fault_3 = pv_prefix + ch_prefix + "FaultMask:B9-SP"
    rst = pv_prefix + ch_prefix + "DigOut_Reset-SP"
    pwr = pv_prefix + ch_prefix + "DigOut_ON1-SP"
    enb = pv_prefix + ch_prefix + "DigOut_ON2-SP"
    prk = pv_prefix + ch_prefix + "DigOut_Park-SP"
    dac_sp = pv_prefix + ch_prefix + "DAC_SetPt-SP"

    # ATE PVs Used here:
    ate_chan_fault = "PSCtest:CH" + str(chan) + ":Fault-SP"
    ate_dcct_fault = "PSCtest:DCCT:Fault:Channel-SP"
    ate_i_gnd_chan = "PSCtest:Ignd:Channel-SP"
    ate_i_gnd_val = "PSCtest:Ignd-SP"

    caput(ate_dcct_fault, 0)  # Set ATE DCCT Fault to "NONE"
    caput(ate_i_gnd_chan, (chan - 1))  # Select Channel for Ignd Setting
    sleep(1)
    i_gnd_sp = 0.1
    caput(ate_i_gnd_val, i_gnd_sp)  # Set Ignd to something sensible, like 0.1A
    sleep(5)

    tdata = []
    tdata.append(["ATE Fault Tests for Channel " + str(chan), 0])

    caput(ate_chan_fault, 2)
    caput(dac_sp, 0)
    caput(pwr, 0)
    caput(enb, 0)
    caput(prk, 0)
    caput(rst, 1)
    sleep(1)
    caput(clr_fault, 1)
    sleep(1)
    caput(rst, 0)
    caput(fault_1, 1)
    caput(fault_2, 1)
    caput(fault_3, 1)
    tcolor = []
    print("RESET", caget(live_fault), caget(lat_fault))
    if caget(live_fault) == 0 and caget(lat_fault) == 0:
        tdata.append(["All Faults Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["All Faults Successfully Cleared", "FAIL"])
        tcolor.append(1)
    # Set Fault 1:
    caput(ate_chan_fault, 0)
    count = 0
    error = 0
    while (caget(live_fault) & 0x80 == 0 or caget(lat_fault) & 0x80 == 0) \
            and error == 0:
        sleep(1)
        print(caget(live_fault), caget(lat_fault))
        count = count + 1
        if count > 10:
            error = 1
    if error == 0:
        tdata.append(["Fault #1 Generated and Detected", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #1 Generated and Detected", "FAIL"])
        tcolor.append(1)
    # Set Fault 2:
    caput(rst, 1)
    sleep(1)
    caput(clr_fault, 1)
    sleep(1)
    caput(rst, 0)
    sleep(1)
    count = 0
    while (caget(live_fault) != 0 or caget(lat_fault) != 0) and count != 10:
        sleep(1)
        count = count + 1
        print("Waiting...", count)
    print("RESET:", caget(live_fault), caget(lat_fault))
    if caget(live_fault) == 0 and caget(lat_fault) == 0:
        tdata.append(["Fault #1 Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #1 Successfully Cleared", "FAIL"])
        tcolor.append(1)
    caput(ate_chan_fault, 1)
    count = 0
    error = 0
    while (
        caget(live_fault) & 0x100 == 0 or caget(lat_fault) & 0x100 == 0
    ) and error == 0:
        sleep(1)
        print(caget(live_fault), caget(lat_fault))
        count = count + 1
        if count > 10:
            error = 1
    if error == 0:
        tdata.append(["Fault #2 Generated and Detected", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #2 Generated and Detected", "FAIL"])
        tcolor.append(1)
    # Set Fault 3:
    caput(rst, 1)
    sleep(1)
    caput(clr_fault, 1)
    sleep(1)
    caput(rst, 0)
    sleep(1)
    count = 0
    while (caget(live_fault) != 0 or caget(lat_fault) != 0) and count != 10:
        sleep(1)
        count = count + 1
        print("Waiting for Faults to Clear...", count)
    print("RESET:", caget(live_fault), caget(lat_fault))
    if caget(live_fault) == 0 and caget(lat_fault) == 0:
        tdata.append(["Fault #2 Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #2 Successfully Cleared", "FAIL"])
        tcolor.append(1)
    caput(ate_chan_fault, 2)
    count = 0
    error = 0
    while (
        caget(live_fault) & 0x200 == 0 or caget(lat_fault) & 0x200 == 0
    ) and error == 0:
        sleep(1)
        print(caget(live_fault), caget(lat_fault))
        count = count + 1
        if count > 10:
            error = 1
    if error == 0:
        tdata.append(["Fault #3 Generated and Detected", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #3 Generated and Detected", "FAIL"])
        tcolor.append(1)
    caput(rst, 1)
    sleep(1)
    caput(clr_fault, 1)
    sleep(1)
    caput(rst, 0)
    sleep(1)
    count = 0
    while (caget(live_fault) != 0 or caget(lat_fault) != 0) and count != 10:
        sleep(1)
        count = count + 1
        print("Waiting for Faults to Clear...", count)
    print("RESET:", caget(live_fault), caget(lat_fault))
    if caget(live_fault) == 0 and caget(lat_fault) == 0:
        tdata.append(["Fault #3 Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #3 Successfully Cleared", "FAIL"])
        tcolor.append(1)

    caput(ate_dcct_fault, chan)
    sleep(1)
    count = 0
    error = 0
    while (caget(live_fault) & 0x40 == 0 or caget(lat_fault) & 0x40 == 0) \
            and error == 0:
        sleep(1)
        print(caget(live_fault), caget(lat_fault))
        count = count + 1
        if count > 10:
            error = 1
    print(caget(live_fault), caget(lat_fault))
    if error == 0:
        tdata.append(["DCCT Fault Generated and Detected", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["DCCT Fault Generated and Detected", "FAIL"])
        tcolor.append(1)
    caput(rst, 1)
    caput(ate_dcct_fault, 0)  # Reset the ATE DCCT Fault to "NONE"
    sleep(5)
    caput(clr_fault, 1)
    sleep(1)
    caput(rst, 0)
    sleep(1)
    count = 0
    while (caget(live_fault) != 0 or caget(lat_fault) != 0) and count != 10:
        sleep(1)
        count = count + 1
        print("Waiting for Faults to Clear...", count)
    print("RESET:", caget(live_fault), caget(lat_fault))
    if caget(live_fault) == 0 and caget(lat_fault) == 0:
        tdata.append(["DCCT Fault Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["DCCT Fault Successfully Cleared", "FAIL"])
        tcolor.append(1)

    row_h = [
        0.35 * inch,
        0.27 * inch,
        0.27 * inch,
        0.27 * inch,
        0.27 * inch,
        0.27 * inch,
        0.27 * inch,
        0.27 * inch,
        0.27 * inch,
        0.27 * inch,
    ]
    col_h = [4 * inch, 2 * inch]

    style = [
        ("SPAN", (0, 0), (1, 0)),
        ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ("FONTSIZE", (0, 0), (1, 0), 16),
        ("FONTSIZE", (0, 1), (1, 1), 14),
        ("VALIGN", (0, 0), (1, 6), "MIDDLE"),
        ("LINEABOVE", (0, 1), (1, 1), 2, colors.black),
        ("LINEAFTER", (0, 1), (0, 9), 2, colors.black),
        ("BACKGROUND", (0, 0), (1, 0), colors.lemonchiffon),
        ("BACKGROUND", (0, 1), (0, 9), colors.lightblue),
        ("FONTSIZE", (0, 1), (1, 9), 12),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BOX", (0, 0), (-1, -1), 2, colors.black),
    ]

    for i in range(0, 9):
        if tcolor[i] == 0:
            style.append(("BACKGROUND", (1, i + 1), (1, i + 1),
                          colors.lightgreen))
        else:
            style.append(("BACKGROUND", (1, i + 1), (1, i + 1),
                          colors.pink))

    ta = Table(tdata, col_h, row_h, style=style)
    local_elements = []
    local_elements.append(Spacer(width=1, height=0.2 * inch))
    local_elements.append(ta)
    return local_elements, i_gnd_sp
