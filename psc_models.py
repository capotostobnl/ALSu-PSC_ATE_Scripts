"""
PSC Model Definitions and Selection Utilities.

This module defines the `PSCModel` dataclass, which encapsulates the
hardware specifications and test parameters for various Power Supply
Controller (PSC) versions. It also provides a utility to interactively
select a model based on detected hardware channels.
"""

# flake8: noqa: E501
# pylint: disable=line-too-long

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class ChannelValues:
    """
    A per-channel data container for PSC hardware parameters.

    This class provides an explicit mapping of values (current, voltage,
    or logic steps) to physical PSC channels. It supports both 2-channel
    and 4-channel hardware configurations by allowing channels 3 and 4
    to be optional.

    Attributes:
        ch1: The parameter value assigned to Channel 1.
        ch2: The parameter value assigned to Channel 2.
        ch3: The parameter value assigned to Channel 3. Defaults to None
            for 2-channel hardware.
        ch4: The parameter value assigned to Channel 4. Defaults to None
            for 2-channel hardware.
    """
    ch1: float
    ch2: float
    ch3: float | None = None
    ch4: float | None = None


@dataclass(frozen=True)
class RegulatorTestParams:
    """
        Encapsulates configuration parameters for the Power Supply
        Regulation test.

        This class defines the target setpoints, timing, and acceptance
        criteria used to evaluate the stability and accuracy of a PSC
        channel over a fixed duration.

        Attributes:
            setpoints: A ChannelValues instance mapping specific current
                setpoints (Amps) to each physical channel.
            settling_time: The duration (seconds) to wait after applying the
                setpoint before beginning data collection.
            tolerance: The maximum allowable deviation (Amps) between the
                measured average and the setpoint for a 'PASS' result.
            ramp_rate: The slew rate (Amps/second) at which the PSC should
                transition to the target setpoint.
            num_samples: The total number of data points to capture during
                the regulation stability window.
            sample_interval: The time delay (seconds) between successive
                register reads during data collection.
        """
    setpoints: ChannelValues  # Set Regulator Test Current SP
    settling_time: float = 10  # Default settling time of 10 seconds
    tolerance: float = 0.050  # Default Pass/Fail Threshold to 50mA
    ramp_rate: float = 10  # Default to 10A/s
    num_samples: int = 180  # Total number of data points to collect
    sample_interval: float = 0.3  # Default 300ms between samples


@dataclass(frozen=True)
class SmoothRampTestParams:
    """
    Encapsulates configuration parameters for the Smooth Ramp Test.

    Validates that the PSC can transition between a 'Start' and 'End'
    setpoint at a specific rate without regulation errors.

    Attributes:
        start_setpoints: The starting current (Amps) for the ramp.
        end_setpoints: The target current (Amps) to reach.
        ramp_rate: The slew rate (Amps/second) for the move.
        settling_time: Extra buffer time (seconds) to wait after the
            calculated ramp duration to ensure the waveform is captured.
        tolerance: The allowable deviation (Amps) for ground current checks.
    """

    start_setpoints: ChannelValues  # Set START current for the ramp test
    end_setpoints: ChannelValues  # Set the END current for the ramp test
    ramp_rate: ChannelValues  # Set Per-Channel Ramp Rates for Smooth Test
    settling_time: float = 10  # Default settling time of 10 seconds
    tolerance: float = 0.050  # Default Pass/Fail Threshold to 50mA


@dataclass(frozen=True)
class JumpTestParams:
    """
    Configuration for the Jump (Step Response) Test.
    
    Used to evaluate the control loop stability by measuring overshoot, 
    ringing, and settling time during a sudden current step.
    """
    start_setpoints: ChannelValues  # Baseline current before the jump
    step_size: ChannelValues       # The magnitude of the jump (Amps)
    sample_window: int = 500        # Points to show before/after the jump
    tolerance: float = 0.050        # Ground current pass/fail threshold (A)


@dataclass(frozen=True)
class PSCModel:
    """
    Represents the technical specifications and test limits for a specific
    PSC model.

    Attributes:
        model_id: Unique internal identifier for the unit type (e.g., "R1-HSS").
        display_name: Short name used for console menus and reporting titles.
        description: Full hardware string (e.g., "PSC-2CH-HSS-AR-QD-QF").
        channels: The physical number of channels (2 or 4).
        reg: An instance of RegulatorTestParams defining stability test criteria.
        smooth: An instance of SmoothRampTestParams defining slew rate and range.
        jump: An instance of JumpTestParams defining step response behavior.
    """

    model_id: str         # Internal ID (e.g., "R1-HSS")
    display_name: str     # Short name for menu (e.g., "R1 2Ch")
    description: str      # Full description (e.g., "PSC-2CH-HSS-AR-QD-QF")
    channels: int
    reg: RegulatorTestParams  # Regulator Test Parameters Class
    smooth: SmoothRampTestParams  # Smooth Ramp Test Parameters Class
    jump: JumpTestParams  # Jump Test Parameters Class


# Define the Registry of all known units
MODELS = {
    # 2-Channel Units
    "R1-HSS": PSCModel(model_id="R1-HSS",
                       display_name="R1 2Ch",
                       description="PSC-2CH-HSS-AR-QD-QF",
                       channels=2,
                       reg=RegulatorTestParams(
                           setpoints=(reg_pts := ChannelValues(ch1=30,
                                                   ch2=50)),
                           settling_time=10),


                       smooth=SmoothRampTestParams(
                           start_setpoints=ChannelValues(ch1=0,
                                                         ch2=0,
                                                         ),
                           end_setpoints=ChannelValues(ch1=49.9,
                                                       ch2=99.9,
                                                       ),
                           ramp_rate=ChannelValues(ch1=10,
                                                   ch2=20),
                           settling_time=10,
                           tolerance=0.05),
                       jump=JumpTestParams(
                           start_setpoints=reg_pts,
                           step_size=ChannelValues(ch1=0.05,
                                                   ch2=0.05),
                           sample_window=500,
                           tolerance=0.05
                        )
                       ),

    "ABEND-QFA": PSCModel(model_id="ABEND-QFA",
                          display_name="ABEND QFA - R3 2Ch",
                          description="PSC-2CH-HSS-AR-Abend-QFA",
                          channels=2,
                          reg=RegulatorTestParams(
                           setpoints=(reg_pts := ChannelValues(ch1=200,
                                                   ch2=100)),
                           settling_time=30),

                          smooth=SmoothRampTestParams(
                              start_setpoints=ChannelValues(ch1=0,
                                                            ch2=0,
                                                            ),
                              end_setpoints=ChannelValues(ch1=385,
                                                          ch2=185,
                                                          ),
                              ramp_rate=ChannelValues(ch1=60,
                                                      ch2=30),
                              settling_time=10,
                              tolerance=0.05),
                          jump=JumpTestParams(
                              start_setpoints=reg_pts,
                              step_size=ChannelValues(ch1=0.5,
                                                      ch2=0.5),
                              sample_window=500,
                              tolerance=0.05
                           )
                          ),

    # 4-Channel Units
    "R1-MSS": PSCModel(model_id="R1-MSS",
                       display_name="R1 4Ch MSS",
                       description="PSC-4CH-MSS-AR-Slow XY Corr.",
                       channels=4,
                       reg=RegulatorTestParams(
                           setpoints=(reg_pts := ChannelValues(ch1=10,
                                                   ch2=10,
                                                   ch3=10,
                                                   ch4=10)),
                           settling_time=10),


                       smooth=SmoothRampTestParams(
                           start_setpoints=ChannelValues(ch1=-23.9,
                                                         ch2=-23.9,
                                                         ch3=-23.9,
                                                         ch4=-23.9),
                           end_setpoints=ChannelValues(ch1=23.9,
                                                       ch2=23.9,
                                                       ch3=23.9,
                                                       ch4=23.9),
                           ramp_rate=ChannelValues(ch1=10,
                                                   ch2=10,
                                                   ch3=10,
                                                   ch4=10),
                           settling_time=10,
                           tolerance=0.05),
                       jump=JumpTestParams(
                           start_setpoints=reg_pts,
                           step_size=ChannelValues(ch1=0.05,
                                                   ch2=0.05,
                                                   ch3=0.05,
                                                   ch4=0.05),
                           sample_window=500,
                           tolerance=0.05
                        )
                       ),


    "R1-SKQ": PSCModel(model_id="R1-SKQ",
                       display_name="R1B 4Ch MSS SKEW QUAD",
                       description="PSC-4CH-MSS-AR-SK",
                       channels=4,
                       reg=RegulatorTestParams(
                           setpoints=(reg_pts := ChannelValues(ch1=10,
                                                   ch2=10,
                                                   ch3=10,
                                                   ch4=10)),
                           settling_time=10
                                                   ),
                       smooth=SmoothRampTestParams(
                           start_setpoints=ChannelValues(ch1=-23.9,
                                                         ch2=-23.9,
                                                         ch3=-23.9,
                                                         ch4=-23.9),
                           end_setpoints=ChannelValues(ch1=23.9,
                                                       ch2=23.9,
                                                       ch3=23.9,
                                                       ch4=23.9),
                           ramp_rate=ChannelValues(ch1=10,
                                                   ch2=10,
                                                   ch3=10,
                                                   ch4=10),
                           settling_time=10,
                           tolerance=0.05),
                       jump=JumpTestParams(
                           start_setpoints=reg_pts,
                           step_size=ChannelValues(ch1=0.05,
                                                   ch2=0.05,
                                                   ch3=0.05,
                                                   ch4=0.05),
                           sample_window=500,
                           tolerance=0.05
                        )
                       ),

    "R1-MSF": PSCModel(model_id="R1-MSF",
                       display_name="R1 4Ch MSF",
                       description="PSC-4CH-MSF-AR-Fast XY Corr.",
                       channels=4,
                       reg=RegulatorTestParams(
                           setpoints=(reg_pts := ChannelValues(ch1=10,
                                                   ch2=10,
                                                   ch3=10,
                                                   ch4=10)),
                           settling_time=10),
                       smooth=SmoothRampTestParams(
                           start_setpoints=ChannelValues(ch1=-23.9,
                                                         ch2=-23.9,
                                                         ch3=-23.9,
                                                         ch4=-23.9),
                           end_setpoints=ChannelValues(ch1=23.9,
                                                       ch2=23.9,
                                                       ch3=23.9,
                                                       ch4=23.9),
                           ramp_rate=ChannelValues(ch1=10,
                                                   ch2=10,
                                                   ch3=10,
                                                   ch4=10),
                           settling_time=10,
                           tolerance=0.05),
                       jump=JumpTestParams(
                           start_setpoints=reg_pts,
                           step_size=ChannelValues(ch1=0.05,
                                                   ch2=0.05,
                                                   ch3=0.05,
                                                   ch4=0.05),
                           sample_window=500,
                           tolerance=0.05
                        )
                       ),

    "R2-AR-SD-SF": PSCModel(model_id="R2-AR-SD-SF",
                            display_name="R2 4Ch MSS AR-SD-SF",
                            description="PSC-4CH-MSS-AR-SD-SF",
                            channels=4,
                            reg=RegulatorTestParams(
                                setpoints=(reg_pts := ChannelValues(ch1=30,
                                                        ch2=65,
                                                        ch3=30,
                                                        ch4=65)),
                                settling_time=10),
                            smooth=SmoothRampTestParams(
                                start_setpoints=ChannelValues(ch1=0,
                                                              ch2=0,
                                                              ch3=0,
                                                              ch4=0),
                                end_setpoints=ChannelValues(ch1=59,
                                                            ch2=124,
                                                            ch3=59,
                                                            ch4=124),
                                ramp_rate=ChannelValues(ch1=20,
                                                        ch2=20,
                                                        ch3=20,
                                                        ch4=20),
                                settling_time=10,
                                tolerance=0.05),
                            jump=JumpTestParams(
                                start_setpoints=reg_pts,
                                step_size=ChannelValues(ch1=0.05,
                                                        ch2=0.1,
                                                        ch3=0.05,
                                                        ch4=0.1),
                                sample_window=500,
                                tolerance=0.05
                             )
                            ),

    "R3-QFA-SHUNT": PSCModel(model_id="R3-QFA-SHUNT",
                             display_name="R3 4Ch MSS QFA SHUNT",
                             description="PSC-4CH-MSS-QFA Shunt",
                             channels=4,
                             reg=RegulatorTestParams(
                                setpoints=(reg_pts := ChannelValues(ch1=5,
                                                        ch2=5,
                                                        ch3=5,
                                                        ch4=5)),
                                settling_time=10),
                             smooth=SmoothRampTestParams(
                                 start_setpoints=ChannelValues(ch1=-5.9,
                                                               ch2=-5.9,
                                                               ch3=-5.9,
                                                               ch4=-5.9),
                                 end_setpoints=ChannelValues(ch1=5.9,
                                                             ch2=5.9,
                                                             ch3=5.9,
                                                             ch4=5.9),
                                 ramp_rate=ChannelValues(ch1=10,
                                                         ch2=10,
                                                         ch3=10,
                                                         ch4=10),
                                 settling_time=10,
                                 tolerance=0.05),
                             jump=JumpTestParams(
                                 start_setpoints=reg_pts,
                                 step_size=ChannelValues(ch1=0.05,
                                                         ch2=0.05,
                                                         ch3=0.05,
                                                         ch4=0.05),
                                 sample_window=500,
                                 tolerance=0.05
                              )
                             ),
}


def get_psc_model_from_user(num_channels: int) -> PSCModel:
    """Filters models and prompts operator with aligned columns."""

    try:
        available_models = [m for m in MODELS.values()
                            if m.channels == num_channels]

        if not available_models:
            raise ValueError(f"No models defined for {num_channels} channels.")

        # Calculate padding: find the longest display name string
        # We add quotes in the length calc to match the print format
        max_label_len = max(len(f"'{m.display_name}'")
                            for m in available_models) + 2

        print(f"\n--- Select {num_channels}-Channel PSC Type ---")
        for i, model in enumerate(available_models, 1):
            label = f"'{model.display_name}'".ljust(max_label_len)
            print(f"{i}. {label} | {model.description}")

        while True:
            try:
                choice = input("\nEnter Type (or 'q' to quit): ")\
                    .strip().lower()

                if choice == 'q':
                    print("Testing aborted by operator.")
                    sys.exit(0)

                idx = int(choice) - 1
                if 0 <= idx < len(available_models):
                    selected = available_models[idx]
                    print(f"--> Selected: {selected.display_name}\n")
                    return selected

                print(f"Invalid choice. Select 1-{len(available_models)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by operator (Ctrl+C). Exiting...")
        sys.exit(0)
