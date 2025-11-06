"""Module for testing that the EVR Timestamp updating."""

from time import sleep
import matplotlib.pyplot as plt
from reportlab.platypus import Image
from reportlab.lib.units import inch
from epics import caget
# from cothread.catools import caget, Sleep


###############################################################################
# EVR Timing Test.........................................


def run_evr_test(pv_prefix, props, good, bad):
    """Perform the EVR timestamp test, generating the plot of the timestamp."""
    print("Starting EVR Timing Test...")

    # EVR Timing PVs:
    evr_timestamp = pv_prefix + "TS-S-I"
    evr_date = pv_prefix + "Timestamp-I.VALA"
    timestamp = []
    time_elapsed = []
    time_0 = caget(evr_timestamp)
    date_raw = caget(evr_date)
    t_last = time_0
    i = 0
    timestamp_error = 0
    zero_cnt = 0
    print("Collecting 30 seconds of EVR Timestamps:")
    f, ax = plt.subplots(1, 1, figsize=(7, 5))
    plt.ion()
    while i < 31:
        tm = caget(evr_timestamp)
        td = tm - t_last
        print(tm, td)
        if td > 0:
            time_elapsed.append(tm - time_0)
            if td != 1:
                timestamp_error = 1
            timestamp.append(tm - time_0)
            print(f"TD={td} evr_timestamp[{i}] = tm  : "
                  "Error = {timestamp_error}")
            t_last = tm
            i = i + 1
            zero_cnt = 0
        else:
            zero_cnt = zero_cnt + 1
            if zero_cnt > 5:
                print("Timestamp Not Changed for 5 seconds. Stopping Program.")
                exit()
        sleep(0.7)
        ax.clear()
        ax.plot(time_elapsed, timestamp, "-o")
        ax.grid(True)
        ax.set_xlabel("Elapsed Time (Seconds)")
        ax.set_ylabel("TmStamp - T0")
        ax.set_title("EVR Timestamp Test")
        clean_date = bytes(date_raw).decode("utf-8").rstrip("\x00")
        mstr = f"T0: {time_0} = {clean_date}"
        ax.text(
            0.05,
            0.95,
            mstr,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=props,
        )
        plt.pause(0.01)
    # if timestamp_error != 0 then this test has failed.
    if timestamp_error == 0:
        mstr = "Test: All time increments equal 1 second? : PASS"
        ax.text(
            0.2,
            0.1,
            mstr,
            transform=ax.transAxes,
            fontsize=12,
            verticalalignment="top",
            bbox=good,
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
            bbox=bad,
        )
        print("EVR Timestamp Test FAILED.")
    plt.pause(0.01)
    f.savefig("EVR_TimeStamp.png")
    # Add Timestamp Test to the Report....
    sleep(1)
    plt.ioff()
    plt.close(f)
    f.canvas.flush_events()  # ensure all GUI events are handled
    plt.pause(0.1)

    im = Image("EVR_TimeStamp.png", 6 * inch, 4 * inch)
    # elements.append(im)
    return im
    ###########################################################################
