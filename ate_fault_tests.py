"""ATE Fault Test Submodule
Modified M. Capotosto 11-9-2025
Original: T. Caracappy
"""
from typing import Callable, Any
from time import sleep, time
from reportlab.lib.units import inch
from reportlab.platypus import Table, Spacer
from reportlab.lib import colors
from initialize_dut import DUT
from epics import PV
from ate_epics import ATE


def _check_fault(dut: DUT, chan: int, mask: int, fault_str: str,
                 set_fault_f: Callable[[int, bool], Any],
                 tdata: list, tcolor: list, poll_int: float = 1.0,
                 set_fault_v: bool = False, max_tries: int = 10,
                 use_monitor: bool = False, min_monitor_time: float = 5.0,) \
                    -> tuple[list, list]:
    assert dut.psc is not None

    error = 0
    if not use_monitor:
        count = 0
        while True:
            live_raw = dut.psc.get_live_faults(chan)
            lat_raw = dut.psc.get_latched_faults(chan)

            # Coerce None → 0 so bitmask operations are safe
            live = int(live_raw) if live_raw is not None else 0
            lat = int(lat_raw) if lat_raw is not None else 0

            live_set = (live & mask) != 0
            lat_set = (lat & mask) != 0

            if live_set and lat_set:
                sleep(4)
                break  # both bits set → success

            sleep(poll_int)
            count += 1
            if count > max_tries:
                error = 1
                break

    else:
        # ----------------------------
        # Monitor-based behavior
        # ----------------------------
        # Build full PV names using PSC helper
        live_pvname = dut.psc.pv("FaultsLive-I", ch=chan)
        lat_pvname = dut.psc.pv("FaultsLat-I", ch=chan)

        live_pv = PV(live_pvname, auto_monitor=True)
        lat_pv = PV(lat_pvname, auto_monitor=True)

        state: dict[str, int] = {"live": 0, "lat": 0}

        def _live_cb(pvname=None, value=None, **kws):
            try:
                state["live"] = int(value) if value is not None else 0
            except Exception:
                state["live"] = 0

        def _lat_cb(pvname=None, value=None, **kws):
            try:
                state["lat"] = int(value) if value is not None else 0
            except Exception:
                state["lat"] = 0

        live_pv.add_callback(_live_cb)
        lat_pv.add_callback(_lat_cb)

        start = time()
        timeout = min_monitor_time + max_tries * poll_int

        while True:
            now = time()
            live_set = (state["live"] & mask) != 0
            lat_set = (state["lat"] & mask) != 0

            # Condition: bit seen in both + at least min_monitor_time elapsed
            if live_set and lat_set and (now - start) >= min_monitor_time:
                break

            if now - start > timeout:
                error = 1
                break

            sleep(poll_int)

        # Clean up callbacks
        live_pv.clear_callbacks()
        lat_pv.clear_callbacks()

    if error == 0:
        tdata.append([f"Fault {fault_str} Generated and Detected", "PASS"])
        tcolor.append(0)
        print(f"Fault {fault_str} Generated and Detected: PASS")
    else:
        tdata.append([f"Fault {fault_str} Generated and Detected", "FAIL"])
        tcolor.append(1)
        print(f"Fault {fault_str} Generated and Detected: FAIL")

    # Clear the fault and reset...
    set_fault_f(chan, set_fault_v)  # Set fault function to call
    sleep(4)
    dut.psc.set_reset(chan, 1)
    sleep(1)
    dut.psc.clear_faults(chan, 1)
    sleep(1)
    dut.psc.set_reset(chan, 0)
    sleep(1)
    dut.psc.clear_faults(chan, 0)
    sleep(1)
    # Append the clear result to tdata and tcolor
    live_raw = dut.psc.get_live_faults(chan)
    lat_raw = dut.psc.get_latched_faults(chan)
    if live_raw == 0 and lat_raw == 0:
        tdata.append([f"Fault {fault_str} Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        tdata.append([f"Fault {fault_str} Successfully Cleared", "FAIL"])
        tcolor.append(1)
    return tdata, tcolor


def ate_fault_tests(dut: DUT, ate: ATE, section: list, chan: int):
    """Main module for carrying out ATE Fault Testing"""
    print("#########################################\n"
          "# **********ATE Fault Test...**********\n"
          "#########################################\n")
    print(f"Beginning Channel {chan}: ")
    assert dut.psc is not None

    # DUT control via PSC adapter
    dut.psc.set_dac_setpt(chan, 0)
    dut.psc.set_power_on1(chan, 0)
    dut.psc.set_enable_on2(chan, 0)
    dut.psc.set_park(chan, 0)
    dut.psc.set_rate(chan, 4)

    # ATE PVs Used here:
#    AteChanFault = "PSCtest:CH" + str(chan) + ":Fault-SP"
#    AteDcctFault = "PSCtest:DCCT:Fault:Channel-SP"
#    AteIgndChan = "PSCtest:Ignd:Channel-SP"
#    AteIgndVal = "PSCtest:Ignd-SP"

    # Set ATE DCCT Fault to "NONE"
    ate.set_dcct_fault_channel(0)

    # Select Channel for Ignd Setting
    ate.set_ignd_channel(chan)
    sleep(1)

    # Set Ignd to something sensible, like 0.1A
    i_gnd_sp = 0.1
    ate.set_ignd_value(i_gnd_sp)
    sleep(5)

    tdata = []
    tdata.append(["ATE Fault Tests for Channel " + str(chan), 0])

    print("\n\nClearing all ATE Faults...\n")
    ate.set_flt1(chan, 0)
    sleep(3.5)
    ate.set_flt2(chan, 0)
    sleep(3.5)
    ate.set_fltspare(chan, 0)
    sleep(3.5)
    ate.set_pc_fault(chan, 0)
    sleep(3.5)

    dut.psc.set_dac_setpt(chan, 0)
    dut.psc.set_power_on1(chan, 0)
    dut.psc.set_enable_on2(chan, 0)
    dut.psc.set_park(chan, 0)
    dut.psc.set_reset(chan, 1)
    sleep(1)
    dut.psc.clear_faults(chan, 1)
    sleep(1)

    dut.psc.set_reset(chan, 0)
    sleep(1)
    dut.psc.clear_faults(chan, 0)
    sleep(1)

    dut.psc.set_fault_mask(7, chan, 1)
    dut.psc.set_fault_mask(8, chan, 1)
    dut.psc.set_fault_mask(9, chan, 1)

    tcolor = []

    print("RESET", "Live Faults: ", dut.psc.get_live_faults(chan),
          "Latched Faults: ", dut.psc.get_latched_faults(chan))

    if dut.psc.get_live_faults(chan) == 0 and \
            dut.psc.get_latched_faults(chan) == 0:
        print("\n\nFault Clear: PASSED")
        tdata.append(["All Faults Successfully Cleared", "PASS"])
        tcolor.append(0)
    else:
        print("\n\nFault Clear: FAILED")
        tdata.append(["All Faults Successfully Cleared", "FAIL"])
        tcolor.append(1)

    # --------------------------------------------------------------------
    # Test Fault 1
    # --------------------------------------------------------------------

    # Set Fault 1:
    print("Testing Fault 1...")
    ate.set_flt1(chan, 1)
    sleep(2)
    # Wait for Fault #1 (bit 0x80) to be set in BOTH LiveFault and LatFault
    mask = 0x80

    fault_str = "#1"
    set_fault_f = ate.set_flt1
    tdata, tcolor = _check_fault(dut, chan, mask, fault_str, set_fault_f,
                                 tdata, tcolor, use_monitor=False,
                                 min_monitor_time=5.0)

    # --------------------------------------------------------------------
    # Test Fault 2
    # --------------------------------------------------------------------
    # Set Fault 2:
    print("Testing Fault 2...")
    ate.set_flt2(chan, 1)
    sleep(2)

    # Wait for Fault #2 (bit 0x100) to be set in BOTH LiveFault and LatFault
    mask = 0x100
    fault_str = "#2"
    set_fault_f = ate.set_flt2

    tdata, tcolor = _check_fault(dut, chan, mask, fault_str, set_fault_f,
                                 tdata, tcolor, use_monitor=False,
                                 min_monitor_time=5.0)

    # --------------------------------------------------------------------
    # Test Fault 3
    # --------------------------------------------------------------------
    # Set Fault 3:
    ate.set_fltspare(chan, 1)
    sleep(2)

    print("Testing Fault 3...")

    # Wait for Fault #3 (bit 0x200) to be set in BOTH LiveFault and LatFault
    mask = 0x200
    fault_str = "SPARE"
    set_fault_f = ate.set_fltspare

    tdata, tcolor = _check_fault(dut, chan, mask, fault_str, set_fault_f,
                                 tdata, tcolor, use_monitor=False,
                                 min_monitor_time=5.0)

    # --------------------------------------------------------------------
    # Test DCCT Fault
    # --------------------------------------------------------------------
    # Set DCCT Fault:
    ate.set_dcct_fault_channel(chan)
    sleep(2)

    print("Testing DCCT Faults......")

    # Wait for DCCT Fault (bit 0x40) to be set in BOTH LiveFault and LatFault
    mask = 0x40
    fault_str = "DCCT"

    def _clear_dcct_fault(bit: int, val: bool) -> None:
        """Clears DCCT fault by setting fault channel to NONE."""
        ate.set_dcct_fault_channel(0)

    tdata, tcolor = _check_fault(dut, chan, mask, fault_str,
                                 set_fault_f=_clear_dcct_fault,
                                 tdata=tdata, tcolor=tcolor)

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
    section.append(Spacer(width=1, height=0.2 * inch))
    section.append(ta)
