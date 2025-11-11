"""ATE Fault Test Submodule
Modified M. Capotosto 11-9-2025
Original: T. Caracappy
"""

from time import sleep
from epics import caget, caput
from reportlab.lib.units import inch
from reportlab.platypus import Table, Spacer
from reportlab.lib import colors
from initialize_dut import DUT


def ate_fault_tests(dut: DUT, section: list, chan: int):
    print(chan)
    CHprefix = "Chan" + str(chan) + ":"
    print("Top of Loop", chan, CHprefix)
    PWR = dut.PVprefix + CHprefix + "DigOut_ON1-SP"
    ENB = dut.PVprefix + CHprefix + "DigOut_ON2-SP"
    PRK = dut.PVprefix + CHprefix + "DigOut_Park-SP"
    DacSP = dut.PVprefix + CHprefix + "DAC_SetPt-SP"
    RATE = dut.PVprefix + CHprefix + "SF:AmpsperSec-SP"
    caput(DacSP, 0)
    caput(PWR, 0)
    caput(ENB, 0)
    caput(PRK, 0)
    caput(RATE, 4)
    ###########################################################
    # ATE Fault Tests:
    ###########################################################
    LiveFault = dut.PVprefix + CHprefix + "FaultsLive-I"
    LatFault = dut.PVprefix + CHprefix + "FaultsLat-I"
    ClrFault = dut.PVprefix + CHprefix + "FaultClear-SP"
    Fault1 = dut.PVprefix + CHprefix + "FaultMask:B7-SP"
    Fault2 = dut.PVprefix + CHprefix + "FaultMask:B8-SP"
    Fault3 = dut.PVprefix + CHprefix + "FaultMask:B9-SP"
    RST = dut.PVprefix + CHprefix + "DigOut_Reset-SP"

    # ATE PVs Used here:
    AteChanFault = "PSCtest:CH" + str(chan) + ":Fault-SP"
    AteDcctFault = "PSCtest:DCCT:Fault:Channel-SP"
    AteIgndChan = "PSCtest:Ignd:Channel-SP"
    AteIgndVal = "PSCtest:Ignd-SP"

    # Set ATE DCCT Fault to "NONE"
    caput(AteDcctFault, 0)

    # Select Channel for Ignd Setting
    caput(AteIgndChan, (chan - 1))
    sleep(1)
    IgndSP = 0.1

    # Set Ignd to something sensible, like 0.1A
    caput(AteIgndVal, IgndSP)
    IgndSP = 0.1
    sleep(5)

    tdata = []
    tdata.append(["ATE Fault Tests for Channel " + str(chan), 0])

    caput(AteChanFault, 2)
    caput(DacSP, 0)
    caput(PWR, 0)
    caput(ENB, 0)
    caput(PRK, 0)
    caput(RST, 1)
    sleep(1)
    caput(ClrFault, 1)
    sleep(1)
    caput(RST, 0)
    caput(Fault1, 1)
    caput(Fault2, 1)
    caput(Fault3, 1)
    tcolor = []
    print("RESET", caget(LiveFault), caget(LatFault))
    if caget(LiveFault) == 0 and caget(LatFault) == 0:
        tdata.append(["All Faults Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["All Faults Successfully Cleared", "FAIL"])
        tcolor.append(1)

    def _read_pv_int(pv) -> int:
        """caget → int, with None coerced to 0 so bit ops are safe."""
        val = caget(pv)
        return int(val) if val is not None else 0

    # Set Fault 1:
    caput(AteChanFault, 0)
    Count = 0
    error = 0

    # Wait for Fault #1 (bit 0x80) to be set in BOTH LiveFault and LatFault
    MASK = 0x80
    MAX_TRIES = 10
    Count = 0
    error = 0

    while True:
        live_raw = caget(LiveFault)
        lat_raw = caget(LatFault)

        # Coerce None → 0 so bitmask ops are safe
        live = int(live_raw) if live_raw is not None else 0
        lat = int(lat_raw) if lat_raw is not None else 0

        print(live, lat)

        live_set = (live & MASK) != 0
        lat_set = (lat & MASK) != 0

        if live_set and lat_set:
            break  # both bits set → success

        sleep(1)
        Count += 1
        if Count > MAX_TRIES:
            error = 1
            break

    if error == 0:
        tdata.append(["Fault #1 Generated and Detected", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #1 Generated and Detected", "FAIL"])
        tcolor.append(1)

    # Set Fault 2:
    caput(RST, 1)
    sleep(1)
    caput(ClrFault, 1)
    sleep(1)
    caput(RST, 0)
    sleep(1)
    Count = 0
    while (caget(LiveFault) != 0 or caget(LatFault) != 0) and Count != 10:
        sleep(1)
        Count = Count + 1
        print("Waiting...", Count)
    print("RESET:", caget(LiveFault), caget(LatFault))
    if caget(LiveFault) == 0 and caget(LatFault) == 0:
        tdata.append(["Fault #1 Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #1 Successfully Cleared", "FAIL"])
        tcolor.append(1)
    caput(AteChanFault, 1)
    Count = 0
    error = 0
    while True:
        live_raw = caget(LiveFault)
        lat_raw = caget(LatFault)

        # Coerce None → 0 so bitmask operations are safe
        live = int(live_raw) if live_raw is not None else 0
        lat = int(lat_raw) if lat_raw is not None else 0

        if ((live & 0x100) != 0) and ((lat & 0x100) != 0):
            break  # both bits set → success

        if error != 0:
            break

        sleep(1)
        Count += 1
        if Count > 10:
            error = 1
            break
    if error == 0:
        tdata.append(["Fault #2 Generated and Detected", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #2 Generated and Detected", "FAIL"])
        tcolor.append(1)
    # Set Fault 3:
    caput(RST, 1)
    sleep(1)
    caput(ClrFault, 1)
    sleep(1)
    caput(RST, 0)
    sleep(1)
    Count = 0
    while (caget(LiveFault) != 0 or caget(LatFault) != 0) and Count != 10:
        sleep(1)
        Count = Count + 1
        print("Waiting for Faults to Clear...", Count)
    print("RESET:", caget(LiveFault), caget(LatFault))
    if caget(LiveFault) == 0 and caget(LatFault) == 0:
        tdata.append(["Fault #2 Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #2 Successfully Cleared", "FAIL"])
        tcolor.append(1)
    caput(AteChanFault, 2)
    MAX_TRIES = 10
    Count = 0
    error = 0

    while error == 0:
        live_raw = caget(LiveFault)
        lat_raw = caget(LatFault)

        # Coerce None → 0 so bitmask ops are safe
        live = int(live_raw) if live_raw is not None else 0
        lat = int(lat_raw) if lat_raw is not None else 0

        print(live, lat)

        # Break out once both have bit 0x200 set
        if (live & 0x200) != 0 and (lat & 0x200) != 0:
            break

        sleep(1)
        Count += 1
        if Count > MAX_TRIES:
            error = 1
            break

    if error == 0:
        tdata.append(["Fault #3 Generated and Detected", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #3 Generated and Detected", "FAIL"])
        tcolor.append(1)
    caput(RST, 1)
    sleep(1)
    caput(ClrFault, 1)
    sleep(1)
    caput(RST, 0)
    sleep(1)
    Count = 0
    while (caget(LiveFault) != 0 or caget(LatFault) != 0) and Count != 10:
        sleep(1)
        Count = Count + 1
        print("Waiting for Faults to Clear...", Count)
    print("RESET:", caget(LiveFault), caget(LatFault))
    if caget(LiveFault) == 0 and caget(LatFault) == 0:
        tdata.append(["Fault #3 Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["Fault #3 Successfully Cleared", "FAIL"])
        tcolor.append(1)

    caput(AteDcctFault, chan)
    sleep(1)
    Count = 0
    error = 0
    MAX_TRIES = 10

    while error == 0:
        live_raw = caget(LiveFault)
        lat_raw = caget(LatFault)

        # Coerce None → 0 so bitmask ops are safe
        live = int(live_raw) if live_raw is not None else 0
        lat = int(lat_raw) if lat_raw is not None else 0

        print(live, lat)

        # Break out once both have bit 0x40 set
        if (live & 0x40) != 0 and (lat & 0x40) != 0:
            break

        sleep(1)
        Count += 1
        if Count > MAX_TRIES:
            error = 1
            break

    print(caget(LiveFault), caget(LatFault))
    if error == 0:
        tdata.append(["DCCT Fault Generated and Detected", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["DCCT Fault Generated and Detected", "FAIL"])
        tcolor.append(1)
    caput(RST, 1)
    caput(AteDcctFault, 0)  # Reset the ATE DCCT Fault to "NONE"
    sleep(5)
    caput(ClrFault, 1)
    sleep(1)
    caput(RST, 0)
    sleep(1)
    Count = 0
    while (caget(LiveFault) != 0 or caget(LatFault) != 0) and Count != 10:
        sleep(1)
        Count = Count + 1
        print("Waiting for Faults to Clear...", Count)
    print("RESET:", caget(LiveFault), caget(LatFault))
    if caget(LiveFault) == 0 and caget(LatFault) == 0:
        tdata.append(["DCCT Fault Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append(["DCCT Fault Successfully Cleared", "FAIL"])
        tcolor.append(1)

    rowH = [
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
    colH = [4 * inch, 2 * inch]

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

    ta = Table(tdata, colH, rowH, style=style)
    section.append(Spacer(width=1, height=0.2 * inch))
    section.append(ta)
