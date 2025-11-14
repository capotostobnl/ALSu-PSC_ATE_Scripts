"""ATE Initializtion Submodule
Modified M. Capotosto 11-9-2025
Original: T. Caracappy
"""

from time import sleep
from ate_epics import ATE
from initialize_dut import DUT


def ate_init(ate: ATE, dut: DUT) -> None:
    assert dut.psc is not None
    for ch in range(1, 4):
        ate.set_dcct_fault_channel(0)
        ate.set_ignd_channel(1)
        ate.set_ignd_value(0)
        ate.set_mode(ch, 0)
        ate.set_vmon_gain(ch, 0.5)
        ate.set_imon_gain(ch, 0.25)
        ate.set_flt1(ch, 0)
        ate.set_flt2(ch, 0)
        ate.set_fltspare(ch, 0)
        ate.set_pc_fault(ch, 0)
        ate.set_polarity(dut.psc.get_polarity())
        ate.set_cal_state(0)
        ate.set_cal_dac(0)
    sleep(1)
    print("ATE is Initialized...")
