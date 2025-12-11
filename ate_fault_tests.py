"""ATE Fault Test Submodule
Modified M. Capotosto 12-01-2025
Original: T. Caracappy
"""
from __future__ import annotations
import subprocess
import threading
from queue import Queue, Empty
from time import sleep, time
from reportlab.lib.units import inch
from reportlab.platypus import Table, Spacer
from reportlab.lib import colors

from initialize_dut import DUT
from ate_epics import ATE

# =============================================================================
# camonitor helpers
# =============================================================================


def _enqueue_output(pipe, queue: Queue):
    """Non-blocking line-reading thread for camonitor output."""
    for line in iter(pipe.readline, b""):
        queue.put(line.decode(errors="ignore"))
    pipe.close()


def _start_camonitor(pvname: str) -> tuple[subprocess.Popen, Queue]:
    """Start camonitor <pvname> and return (process, queue)."""
    proc = subprocess.Popen(
        ["camonitor", pvname],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    q = Queue()
    threading.Thread(target=_enqueue_output, args=(proc.stdout, q),
                     daemon=True).start()
    return proc, q


def _parse_camonitor_value(line: str) -> int:
    """Extract final integer from camonitor line."""
    try:
        return int(line.strip().split()[-1])
    except Exception:
        return 0

# =============================================================================
# Fault Configuration Table
# =============================================================================


FAULT_TESTS = [
    (0x80,  "#1",    "set_flt1", True),
    (0x100, "#2",    "set_flt2", True),
    (0x200, "SPARE", "set_fltspare", True),
    (0x40,  "DCCT",  "set_dcct_fault_channel", False),
]


def _run_single_fault_test(mask, label, setter, setter_bool, dut, ate, chan):
    """Run ONE fault test and return (result_string, color_flag).
       result_string = 'PASS' or 'FAIL'
       color_flag = 0 for PASS, 1 for FAIL
    """

    # Start monitoring BEFORE issuing the fault
    live_pv = dut.psc.pv("FaultsLive-I", ch=chan)
    lat_pv = dut.psc.pv("FaultsLat-I", ch=chan)
    live_proc, live_q = _start_camonitor(live_pv)
    lat_proc, lat_q = _start_camonitor(lat_pv)
    state = {"live": 0, "lat": 0}
    start_time = time()
    detected = False

    # Prime PVs
    prime_deadline = time() + 0.2
    while time() < prime_deadline:
        try:
            state["live"] = _parse_camonitor_value(live_q.get_nowait())
        except Empty:
            pass
        try:
            state["lat"] = _parse_camonitor_value(lat_q.get_nowait())
        except Empty:
            pass
        sleep(0.01)

    # Trigger the fault
    if setter_bool:
        setter(chan, True)
    else:
        setter(chan)

    set_command_time = time()

    # PV event loop
    while True:
        now = time()
        try:
            while True:
                state["live"] = _parse_camonitor_value(live_q.get_nowait())
        except Empty:
            pass
        try:
            while True:
                state["lat"] = _parse_camonitor_value(lat_q.get_nowait())
        except Empty:
            pass

        if (state["live"] & mask) or (state["lat"] & mask):
            detected = True

        if now - start_time > 10.0:
            break

        sleep(0.01)

    live_proc.kill()
    lat_proc.kill()

    # Wait remaining 2 seconds after ATE command
    remaining = 2.0 - (time() - set_command_time)
    if remaining > 0:
        sleep(remaining)

    # Clear the fault
    sleep(3)
    if setter_bool:
        setter(chan, False)
    else:
        setter(0)
    sleep(4)

    # PSC clear
    dut.psc.set_reset(chan, 1)
    sleep(1)
    dut.psc.clear_faults(chan, 1)
    sleep(1)
    dut.psc.set_reset(chan, 0)
    sleep(0.5)
    dut.psc.clear_faults(chan, 0)
    sleep(0.5)

    # Check cleared
    for _ in range(200):
        if (dut.psc.get_live_faults(chan) or 0) == 0 and \
           (dut.psc.get_latched_faults(chan) or 0) == 0:
            break
        sleep(0.05)

    final_live = dut.psc.get_live_faults(chan) or 0
    final_lat = dut.psc.get_latched_faults(chan) or 0

    pass1 = detected
    pass2 = (final_live == 0 and final_lat == 0)

    result = "PASS" if (pass1 and pass2) else "FAIL"
    color = 0 if result == "PASS" else 1

    return result, color


# =============================================================================
# Main Test Routine
# =============================================================================


def ate_fault_tests(dut: DUT, ate: ATE, section: list, chan: int):
    """Main driver for automated ATE Fault Testing using event-driven EPICS."""

    assert dut.psc is not None

    print("==============================================")
    print("          ATE Fault Test Starting")
    print("==============================================")
    print(f"Channel: {chan}\n")

    # Basic PSC setup (fast hardware)
    dut.psc.set_dac_setpt(chan, 0)
    sleep(0.5)
    dut.psc.set_power_on1(chan, 0)
    sleep(0.5)
    dut.psc.set_enable_on2(chan, 0)
    sleep(0.5)
    dut.psc.set_park(chan, 0)
    sleep(0.5)
    dut.psc.set_rate(chan, 4)
    sleep(0.5)

    # ATE setup
    ate.set_dcct_fault_channel(0)
    # sleep(4)
    ate.set_ignd_channel(chan)
    # sleep(4)
    ate.set_ignd_value(0.1, chan, dut)
    # sleep(4)

    tdata = [[f"ATE Fault Tests for Channel {chan}", 0]]
    tcolor = []

    # -------------------------------------------------------------------------
    # Loop over all fault tests
    # -------------------------------------------------------------------------
    for mask, label, method_name, setter_bool in FAULT_TESTS:
        print(f"\n--- Testing Fault {label} ---")
        setter = getattr(ate, method_name)

        # Start monitoring BEFORE issuing the fault
        live_pv = dut.psc.pv("FaultsLive-I", ch=chan)
        lat_pv = dut.psc.pv("FaultsLat-I", ch=chan)
        live_proc, live_q = _start_camonitor(live_pv)
        lat_proc, lat_q = _start_camonitor(lat_pv)
        state = {"live": 0, "lat": 0}
        start_time = time()
        detected = False

        # Prime PVs: read initial values to ensure subscription is active
        prime_deadline = time() + 0.2
        while time() < prime_deadline:
            try:
                line = live_q.get_nowait()
                state["live"] = _parse_camonitor_value(line)
            except Empty:
                pass
            try:
                line = lat_q.get_nowait()
                state["lat"] = _parse_camonitor_value(line)
            except Empty:
                pass
            sleep(0.01)

        # Trigger the fault
        if setter_bool:
            setter(chan, True)
        else:
            setter(chan)
        set_command_time = time()  # 4-second delay start

        # Event-driven detection loop (pass if either Live or Latched)
        while True:
            now = time()
            try:
                while True:
                    line = live_q.get_nowait()
                    state["live"] = _parse_camonitor_value(line)
            except Empty:
                pass
            try:
                while True:
                    line = lat_q.get_nowait()
                    state["lat"] = _parse_camonitor_value(line)
            except Empty:
                pass

            # Pass if either Live or Latched
            if (state["live"] & mask) != 0 or (state["lat"] & mask) != 0:
                if not detected:
                    print(f"✓ Fault {label} detected in PVs")
                    tdata.append([f"Fault {label} Generated and Detected",
                                  "PASS"])
                    tcolor.append(0)
                    detected = True

            # Timeout after 10 seconds if never detected
            if now - start_time > 10.0:
                if not detected:
                    print(f"✗ Fault {label} NOT detected within timeout")
                    tdata.append([f"Fault {label} Generated and Detected",
                                  "FAIL"])
                    tcolor.append(1)
                break

            sleep(0.01)

        live_proc.kill()
        lat_proc.kill()

        # Wait remaining of 4s after ATE set command if needed
        remaining = 2.0 - (time() - set_command_time)
        if remaining > 0:
            sleep(remaining)

        # Clear the fault
        sleep(3)
        if setter_bool:
            setter(chan, False)
        else:
            setter(0)
        sleep(4)  # 4-second delay after clear

        # PSC reset/clear
        dut.psc.set_reset(chan, 1)
        sleep(1)
        dut.psc.clear_faults(chan, 1)
        sleep(1)
        dut.psc.set_reset(chan, 0)
        sleep(0.5)
        dut.psc.clear_faults(chan, 0)
        sleep(0.5)

        # Verify PVs cleared (poll up to 10s)
        for _ in range(200):
            live_raw = dut.psc.get_live_faults(chan) or 0
            lat_raw = dut.psc.get_latched_faults(chan) or 0
            if live_raw == 0 and lat_raw == 0:
                break
            sleep(0.05)

        live_raw = dut.psc.get_live_faults(chan) or 0
        lat_raw = dut.psc.get_latched_faults(chan) or 0
        if live_raw == 0 and lat_raw == 0:
            print(f"✓ Fault {label} cleared")
            tdata.append([f"Fault {label} Successfully Cleared", "PASS"])
            tcolor.append(0)
        else:
            print(f"✗ Fault {label} NOT fully cleared")
            tdata.append([f"Fault {label} Successfully Cleared", "FAIL"])
            tcolor.append(1)

    # -------------------------------------------------------------------------
    # Build ReportLab Table
    # -------------------------------------------------------------------------
    row_h = [0.35 * inch] + [0.27 * inch] * (len(tdata) - 1)
    col_w = [4 * inch, 2 * inch]

    style = [
        ("SPAN", (0, 0), (1, 0)),
        ("ALIGN", (0, 0), (1, 0), "CENTER"),
        ("FONTSIZE", (0, 0), (1, 0), 16),
        ("VALIGN", (0, 0), (1, len(tdata) - 1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BOX", (0, 0), (-1, -1), 2, colors.black),
        ("BACKGROUND", (0, 0), (1, 0), colors.lemonchiffon),
    ]

    for i in range(1, len(tdata)):
        bg = colors.lightgreen if tcolor[i - 1] == 0 else colors.pink
        style.append(("BACKGROUND", (1, i), (1, i), bg))

    section.append(Spacer(1, 0.2 * inch))
    section.append(Table(tdata, col_w, row_h, style=style))
