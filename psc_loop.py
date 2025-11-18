"""Main module for PSC Testing.

M. Capotosto 11/11/2025
"""

from ate_epics import ATE
from psc_epics import PSC
from initialize_dut import DUT
from report_generator import start_report, finalize_report, \
    channel_section
from evr_timing_test import evr_timing_test
from ate_init import ate_init
from ate_fault_tests import ate_fault_tests
from ps_regulation_test import ps_regulation_test
from jump_test import jump_test
from smooth_ramp_test import smooth_ramp_test
from fofb_test import \
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
            ps_regulation_test(dut, sec, chan, ctx)

            print("\n\n*******************************************"
                  f"\nBeginning Channel {chan} Jump Tests..."
                  "\n*******************************************")
            jump_test(dut, sec, chan, ctx)

            print("\n\n*******************************************"
                  f"\nBeginning Channel {chan} Smooth Ramp Tests..."
                  "\n*******************************************")
            smooth_ramp_test(dut, ate, sec, chan, ctx)

    if dut.bandwidth == "Fast":
        print("\n\n*******************************************"
              "\nBeginning FOFB Tests..."
              "\n************************************* ******")
        fofb_daisy_packet_monotonic_test(dut, ctx)

    finalize_report(ctx)
