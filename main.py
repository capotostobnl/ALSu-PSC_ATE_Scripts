"""Main module for PSC Testing.

M. Capotosto 11/11/2025
"""

from EPICS_Adapters.ate_epics import ATE
from initialize_dut import DUT
from report_generator import start_report, finalize_report, \
    channel_section
from ate_init import ate_init
from Functional_Tests.evr_timing_test import evr_timing_test
from Functional_Tests.ate_fault_tests import ate_fault_tests
from Functional_Tests.ps_regulation_test import ps_regulation_test
from Functional_Tests.jump_test import jump_test
from Functional_Tests.smooth_ramp_test import smooth_ramp_test
from Functional_Tests.fofb_test import \
    fofb_daisy_packet_monotonic_test


if __name__ == "__main__":

    ate = ATE(prefix="PSCtest:", ch_fmt="CH{ch}:")

    ##############################################################
    # Get user inputs...
    ##############################################################
    dut = DUT()  # Create DUT class instance

    # Prompt the user for PSC Info
    # Create Shipment directory, Report Gen Directory, and
    # Raw Data directories for this test run.
    dut.prompt_inputs()
    dut.init()

    ctx, pdf_path = start_report(dut)

    evr_timing_test(dut, ctx)
    ate_init(ate, dut)

    for chan in range(1, dut.num_channels+1):
        with channel_section(ctx, chan) as sec:
            print("\n\n*******************************************"
                  f"\nBeginning Channel {chan} ATE Fault Tests..."
                  "\n*******************************************")
            ate_fault_tests(dut, ate, sec, chan)

            print("\n\n*******************************************"
                  f"\nBeginning Channel {chan} Regulation Tests..."
                  "\n*******************************************")
            ps_regulation_test(dut, ate, sec, chan, ctx)

            print("\n\n*******************************************"
                  f"\nBeginning Channel {chan} Jump Tests..."
                  "\n*******************************************")
            jump_test(dut, ate, sec, chan, ctx)

            print("\n\n*******************************************"
                  f"\nBeginning Channel {chan} Smooth Ramp Tests..."
                  "\n*******************************************")
            smooth_ramp_test(dut, ate, sec, chan, ctx)

    print(dut.bandwidth)
    if dut.bandwidth == "F":
        print("\n\n*******************************************"
              "\nBeginning FOFB Tests..."
              "\n************************************* ******")
        fofb_daisy_packet_monotonic_test(dut, ctx)

    finalize_report(ctx)
    print("Test complete! See folder for report.")
