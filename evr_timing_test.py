"""EVR Timing Test Submodule
Modified M. Capotosto 11-9-2025
Original: T. Caracappy
"""

import os
from time import sleep
from epics import caget, caput
from matplotlib import pyplot as plt
from reportlab.platypus import Image
from reportlab.lib.units import inch

from initialize_dut import DUT
from report_generator import ReportContext

#######################################################################
# ******Disable Scientific Notation Conversions on X/Y Axis Plots******
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['axes.formatter.limits'] = [-7, 7]
########################################################################


def evr_timing_test(dut: DUT, ctx: ReportContext) -> None:
    EvrTS = dut.pv_prefix + "TS-S-I"
    EVRdate = dut.pv_prefix + "Timestamp-I.VALA"

    # --- Program EVR and reset, but wait for the puts to complete ---
    caput(f"{dut.pv_prefix}EVR:1Hz-EventNo-SP", 32, wait=True, timeout=2.0)
    caput(f"{dut.pv_prefix}EVR:Reset-SP", 1, wait=True, timeout=2.0)
    sleep(0.1)
    caput(f"{dut.pv_prefix}EVR:Reset-SP", 0, wait=True, timeout=2.0)

    # OPTIONAL: short settle time
    sleep(0.5)

    TS: list[float] = []
    Telapse: list[float] = []

    # --- Get date string (same as before) ---
    date_array = caget(EVRdate)
    if date_array is None:
        date_text = ""
    else:
        date_text = "".join(chr(i) for i in date_array if i != 0)

    # --- Wait for the first EVR tick after reset ---
    initial_ts = caget(EvrTS)
    if initial_ts is None:
        raise RuntimeError(f"PV {EvrTS} returned None after EVR reset")

    print("Waiting for first EVR timestamp tick...")
    T0 = None
    Tlast = None
    for _ in range(20):  # ~10 seconds max (with 0.5 s sleeps)
        TM = caget(EvrTS)
        if TM is None:
            sleep(0.5)
            continue
        if TM != initial_ts:
            T0 = TM
            Tlast = TM
            break
        sleep(0.5)

    if T0 is None or Tlast is None:
        raise RuntimeError("EVR timestamp never started after reset.")

    print(f"First tick detected: T0 = {T0}")

    i = 0
    TSerror = 0
    zeroCnt = 0

    print("Collecting 30 seconds of EVR Timestamps:")
    f, ax = plt.subplots(1, 1, figsize=(7, 5))

    started = False

    # --- Main acquisition loop (mostly unchanged) ---
    while i < 31:
        TM = caget(EvrTS)
        if TM is None:
            raise RuntimeError(f"PV {EvrTS} returned None")

        TD = TM - Tlast

        if TD > 0:
            if not started:
                # First usable tick: initialize T0/Tlast and don't check TD yet
                T0 = TM
                Tlast = TM
                started = True
                Telapse.append(0.0)
                TS.append(0.0)
                print(f"First stable tick: T0 = {T0}")
            else:
                rel = TM - T0
                Telapse.append(rel)
                if TD != 1:
                    TSerror = 1
                TS.append(rel)
                print(f"TD={TD} EvrTS[{i}] = {TM}  : Error = {TSerror}")
                Tlast = TM
                i += 1
            zeroCnt = 0
        else:
            zeroCnt += 1
            if zeroCnt > 5:
                raise RuntimeError("Timestamp Not Changed for 5 seconds..."
                                   "Stopping Program.")

        sleep(0.7)

        # --- Plot update ---
        ax.clear()
        ax.plot(Telapse, TS, "-o")
        ax.grid(True)
        ax.set_xlabel("Elapsed Time (Seconds)")
        ax.set_ylabel("TmStamp - T0")
        ax.set_title("EVR Timestamp Test")

        mstr = f"T0: {T0} = {date_text}"
        ax.text(
            0.05,
            0.95,
            mstr,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=ctx.theme.props,
        )
        plt.pause(0.01)

    # PASS/FAIL annotation (unchanged)
    if TSerror == 0:
        mstr = "Test: All time increments equal 1 second? : PASS"
        ax.text(
            0.2,
            0.1,
            mstr,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox=ctx.theme.good,
        )
        print("EVR Timestamp Test PASSED.")
    else:
        mstr = "Test: All time increments equal 1 second? : FAIL"
        ax.text(
            0.2,
            0.1,
            mstr,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox=ctx.theme.bad,
        )
        print("EVR Timestamp Test FAILED.")

    plt.pause(0.01)

    img_path = os.path.join(dut.raw_data_dir, "EVR_Timestamp.png")
    f.savefig(img_path)

    # Cleanup / add to report
    sleep(1)
    plt.ioff()
    plt.close(f)
    plt.pause(0.1)

    ctx.elements.append(Image(img_path, 6 * inch, 4 * inch))
