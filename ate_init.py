"""ATE Initializtion Submodule
Modified M. Capotosto 11-9-2025
Original: T. Caracappy
"""

from time import sleep
from EPICS_Adapters.ate_epics import ATE
from initialize_dut import DUT


def ate_init(ate: ATE, dut: DUT) -> None:
    assert dut.psc is not None
    print("#########################################\n"
          "# **********Initializing ATE...**********\n"
          "#########################################\n")
    for ch in range(1, dut.num_channels+1):
        print(f"Initializing ATE, Ch{ch}")
        ate.set_dcct_fault_channel(0)
        ate.set_ignd_channel(ch)
        ate.set_ignd_value(0, ch, dut)
        ate.set_mode(ch, 0)
        ate.set_vmon_gain(ch, 0.5)
        ate.set_imon_gain(ch, 0.25)
        print("Initialized DCCT, IGND, Mode, VMON, IMON...")
        ate.set_polarity(dut.psc.get_polarity())
        # ate.set_polarity(0)
        ate.set_cal_state(0)
        ate.set_cal_dac(0)
        print("Initialize Polarity Mode, Cal State, Cal DAC...")
        ate.set_pc_fault(ch, 0)
        sleep(4)
        print("Initialize PC Fault...")
    sleep(1)
    print("ATE is Initialized...")
