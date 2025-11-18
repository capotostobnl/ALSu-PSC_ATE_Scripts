"""EVR Timing Test Submodule
Modified M. Capotosto 11-9-2025
Original: T. Caracappy
"""

import os
from time import sleep
from epics import caget
from matplotlib import pyplot as plt
from reportlab.platypus import Image
from reportlab.lib.units import inch

from initialize_dut import DUT
from report_generator import ReportContext


def evr_timing_test(dut: DUT, ctx: ReportContext) -> None:
    EvrTS = dut.pv_prefix + "TS-S-I"
    EVRdate = dut.pv_prefix + "Timestamp-I.VALA"

    TS = []
    Telapse = []

    T0 = caget(EvrTS)
    date_array = caget(EVRdate)

    if date_array is None:
        date_text = ""
    else:
        date_text = ''.join(chr(i) for i in date_array if i != 0)

    Tlast = T0
    i = 0
    TSerror = 0
    zeroCnt = 0

    print("Collecting 30 seconds of EVR Timestamps:")
    f, ax = plt.subplots(1, 1, figsize=(7, 5))
    plt.ion()

    while i < 31:
        TM = caget(EvrTS)
        if TM is None:
            raise RuntimeError(f"PV {EvrTS} returned None")

        TD = TM - Tlast
        # print(TM, TD)

        if TD > 0:
            Telapse.append(TM - T0)
            if TD != 1:
                TSerror = 1
            TS.append(TM - T0)
            print("TD=%d EvrTS[%d] = %d  : Error = %d" % (TD, i, TM, TSerror))
            Tlast = TM
            i = i + 1
            zeroCnt = 0
        else:
            zeroCnt = zeroCnt + 1
            if zeroCnt > 5:
                raise RuntimeError("Timestamp Not Changed for 5 seconds..."
                                   "Stopping Program.")

        sleep(0.7)
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

    # if TSerror != 0 then this test has failed.
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

    # Add Timestamp Test to the Report....
    sleep(1)
    plt.ioff()
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    ctx.elements.append(Image(img_path, 6 * inch, 4 * inch))
