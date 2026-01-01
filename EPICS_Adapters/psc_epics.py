"""
PSC EPICS Adapter Module

This module provides the driver level interface for the Power
Supply Controller. It handles EPICS Channel Access communication, PV naming
formatting, and provides a standard API for setting currents, reading status,
and retrieving waveforms.

Modified to support:
- Dynamic prefixing (e.g., "lab{5}")
- Configurable channel formatting (e.g., "Chan{}")
- Global timeouts
"""
from __future__ import annotations
from enum import Enum, unique
from typing import Any, Optional
from epics import caget, caput, ca
from epics.ca import ChannelAccessException  # type: ignore

# =============================================================================
# Constants & Enums
# =============================================================================


@unique
class WfmPV(Enum):
    """Enumeration for Waveform PV suffixes."""
    DAC = "DAC-I"
    DCCT1 = "DCCT1-I"
    DCCT2 = "DCCT2-I"
    ERR = "Err-I"
    REG = "Reg-I"
    VOLT = "V-Mon"
    GND = "IGND-I"
    SPARE = "Spare-I"

# =============================================================================
# PSC Driver Class
# =============================================================================


class PSC:
    """
    EPICS Driver for the Power Supply Controller.

    Handles the construction of PV names based on the provided prefix and
    channel format, and wraps PyEpics calls with specific timeouts.

    Attributes:
        prefix (str): The base PV prefix (e.g., "lab{1}").
        ch_fmt (str): The format string for channel insertion (e.g., "Chan{}").
        timeout (float): Default timeout for EPICS operations in seconds.
        WfmPV (Enum): Access to waveform suffix enums.
    """

    # Expose the Enum so it can be accessed via dut.psc.WfmPV
    WfmPV = WfmPV

    def __init__(self, prefix: str, ch_fmt: str = "Chan{}",
                 timeout: float = 3.0):
        """
        Initialize the PSC driver.

        Args:
            prefix (str): The EPICS prefix for the unit (e.g., 'lab{5}').
            ch_fmt (str): Format string for the channel (default: 'Chan{}').
            timeout (float): Max wait time for EPICS connects/puts
            (default: 3.0s).
        """
        self.prefix = prefix
        self.ch_fmt = ch_fmt
        self.timeout = timeout

    def pv(self, suffix: str, ch: int | None = None) -> str:
        """
        Construct the full PV name.

        Args:
            suffix (str): The specific parameter suffix (e.g., "DAC-I").
            ch (int | None): The channel number. If None, assumes
            unit-level PV.

        Returns:
            str: The fully formatted PV string (e.g., "lab{5}Chan1:DAC-I").
        """
        if ch is not None:
            # e.g. "lab{5}" + "Chan1" + ":" + "DAC-I"
            return f"{self.prefix}{self.ch_fmt.format(ch)}:{suffix}"
        return f"{self.prefix}:{suffix}"

    def flush_io(self) -> None:
        """
        Force a flush of the EPICS Channel Access IO buffer.
        Ensures pending 'put' requests are sent to the IOC immediately.
        """
        ca.flush_io()

    # =========================================================================
    # Core I/O Wrappers (Safe Methods)
    # =========================================================================

    def get(self, suffix: str, *, ch: Optional[int] = None,
            as_string: bool = False, timeout: Optional[float] = None) -> Any:
        """Raw wrapper around caget."""
        return caget(self.pv(suffix, ch=ch), as_string=as_string,
                     timeout=timeout or self.timeout)

    def put(self, suffix: str, value: Any, *, ch: Optional[int] = None,
            wait: bool = True, timeout: Optional[float] = None) -> bool:
        """Raw wrapper around caput."""
        return bool(caput(self.pv(suffix, ch=ch), value, wait=wait,
                          timeout=timeout or self.timeout))

    def safe_get(self, suffix: str, *, ch: Optional[int] = None,
                 as_string: bool = False, timeout: Optional[float] =
                 None) -> Any:
        """
        Wrapper for caget that catches exceptions and logs errors.
        Returns None on failure.
        """
        try:
            return self.get(suffix, ch=ch, as_string=as_string,
                            timeout=timeout)
        except (ChannelAccessException, OSError, ValueError) as e:
            print(f"caget ERROR {self.pv(suffix, ch=ch)}: {e}")
            return None

    def safe_put(self, suffix: str, value: Any, *, ch: Optional[int] = None,
                 wait: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Wrapper for caput that catches exceptions and logs errors.
        Returns False on failure.
        """
        try:
            return self.put(suffix, value, ch=ch, wait=wait, timeout=timeout)
        except (ChannelAccessException, OSError, ValueError) as e:
            print(f"caput ERROR {self.pv(suffix, ch=ch)} <- {value}: {e}")
            return False

    # =========================================================================
    # Setters (Controls)
    # =========================================================================

    def set_dac_setpt(self, ch: int, amps: float) -> bool:
        """Set the DAC current setpoint (Amps)."""
        return self.safe_put("DAC_SetPt-SP", amps, ch=ch)

    def set_power_on1(self, ch: int, val: int | bool) -> bool:
        """Set Power On 1 Command (1/True=On, 0/False=Off)."""
        return self.safe_put("DigOut_ON1-SP", int(val), ch=ch)

    def set_enable_on2(self, ch: int, val: int | bool) -> bool:
        """Set Enable On 2 Command (1/True=Enable, 0/False=Disable)."""
        return self.safe_put("DigOut_ON2-SP", int(val), ch=ch)

    def set_park(self, ch: int, val: int | bool) -> bool:
        """Set Park Command (1/True=Park, 0/False=Unpark)."""
        return self.safe_put("DigOut_Park-SP", int(val), ch=ch)

    def set_rate(self, ch: int, rate: float) -> bool:
        """Set the current ramp rate (Amps/second)."""
        return self.safe_put("SF:AmpsperSec-SP", rate, ch=ch)

    def set_op_mode(self, ch: int, mode: int | str) -> bool:
        """Set the operational mode (e.g., 3 for Jump/Waveform)."""
        return self.safe_put("DAC_OpMode-SP", mode, ch=ch, wait=True)

    def set_reset(self, ch: int, val: int | bool) -> bool:
        """Set the Soft Reset command."""
        return self.safe_put("DigOut_Reset-SP", int(val), ch=ch)

    def set_digout_spare(self, ch: int, val: int | bool) -> bool:
        """Set DigOut_Spare-SP"""
        return self.safe_put("DigOut_Spare-SP", int(val), ch=ch)

    # =========================================================================
    # Triggers & Status
    # =========================================================================
    def user_shot(self, ch: int) -> bool:
        """Trigger a User Snapshot (Waveform Capture)."""
        return self.safe_put("SS:Trig:Usr", 1, ch=ch, wait=True)

    def is_user_trig_active(self, ch: int) -> int:
        """
        Check if the user trigger is active.
        Returns 1 if Active/Busy, 0 if Idle or on read error.
        """
        val = self.safe_get("UsrTrigActive-I", ch=ch)
        return int(val) if val is not None else 0

    # =========================================================================
    # Waveform Handling
    # =========================================================================
    def set_wfm_xmin(self, ch: int, value: float) -> bool:
        """Set the Xmin waveform value for a channel."""
        return self.safe_put("SS:WFM-Xmin", value, ch=ch)

    def set_wfm_xmax(self, ch: int, value: float) -> bool:
        """Set the Xmax waveform value for a channel."""
        return self.safe_put("SS:WFM-Xmax", value, ch=ch)

    def get_wfm(self, ch: int, pv: WfmPV):
        """
        Retrieve a specific waveform array for a channel.

        Args:
            ch (int): Channel number.
            pv (WfmPV): The waveform type Enum (e.g., WfmPV.DAC).

        Returns:
            list/ndarray: The waveform data, or None on failure.
        """
        suffix_map = {
            self.WfmPV.DAC:   "USR:DAC-Wfm",
            self.WfmPV.DCCT1: "USR:DCCT1-Wfm",
            self.WfmPV.DCCT2: "USR:DCCT2-Wfm",
            self.WfmPV.ERR:   "USR:Error-Wfm",
            self.WfmPV.REG:   "USR:Reg-Wfm",
            self.WfmPV.VOLT:  "USR:Volt-Wfm",
            self.WfmPV.GND:   "USR:Gnd-Wfm",
            self.WfmPV.SPARE: "USR:Spare-Wfm",
        }
        suffix = suffix_map[pv]
        return self.safe_get(suffix, ch=ch)

    # =========================================================================
    # Getters (Readbacks)
    # =========================================================================
    def get_dac(self, ch: int) -> float | None:
        """Read DAC Current Readback (DAC-I)."""
        return self.safe_get("DAC-I", ch=ch)

    def get_dcct1(self, ch: int) -> float | None:
        """Read DCCT1 Current (DCCT1-I)."""
        return self.safe_get("DCCT1-I", ch=ch)

    def get_dcct2(self, ch: int) -> float | None:
        """Read DCCT2 Current (DCCT2-I)."""
        return self.safe_get("DCCT2-I", ch=ch)

    def get_ignd_val(self, ch: int) -> float:
        """Read Ground Current (Gnd-I)."""
        return self.safe_get("Gnd-I", ch=ch)

    def get_dig_in_b0(self, ch: int) -> int | None:
        """Read Digital Input Bit 0 (DigIn-I.B0)."""
        return self.safe_get("DigIn-I.B0", ch=ch)

    def get_num_channels(self) -> int:
        """Read number of channels from NumChannels-Mode."""
        raw = self.safe_get("NumChannels-Mode", as_string=True)
        return int(str(raw)[:1])

    def get_resolution(self) -> str:
        """Read Resolution-Mode string."""
        raw = self.safe_get("Resolution-Mode", as_string=True)
        return str(raw)

    def get_bandwidth(self) -> str:
        """Read Bandwidth-Mode (first char)."""
        raw = self.safe_get("Bandwidth-Mode", as_string=True)
        return str(raw)[:1]

    def get_polarity(self) -> str:
        """Read Polarity-Mode string."""
        raw = self.safe_get("Polarity-Mode", as_string=True)
        return str(raw)

    # =========================================================================
    # Faults
    # =========================================================================

    def clear_faults(self, ch: int, val: int | bool) -> bool:
        """Set FaultClear-SP (1=Clear)."""
        return self.safe_put("FaultClear-SP", int(val), ch=ch)

    def set_fault_mask(self, bit: int, ch: int, val: int | bool) -> bool:
        """Set a specific Fault Mask bit."""
        return self.safe_put(f"FaultMask:B{bit}-SP", val, ch=ch)

    def get_live_faults(self, ch: int):
        """Get the Live Fault Status Word."""
        return self.get("FaultsLive-I", ch=ch)

    def get_latched_faults(self, ch: int):
        """Get the Latched Fault Status Word."""
        return self.get("FaultsLat-I", ch=ch)

    # =========================================================================
    # PV Name Accessors (Return Strings)
    # =========================================================================

    def pv_dac_wfm(self, ch: int) -> str:
        """Get the full PV name for the DAC Waveform."""
        return self.pv("USR:DAC-Wfm", ch=ch)

    def pv_dcct1_wfm(self, ch: int) -> str:
        """Get the full PV name for the DCCT1 Waveform."""
        return self.pv("USR:DCCT1-Wfm", ch=ch)

    def pv_dcct2_wfm(self, ch: int) -> str:
        """Get the full PV name for the DCCT2 Waveform."""
        return self.pv("USR:DCCT2-Wfm", ch=ch)

    def pv_err_wfm(self, ch: int) -> str:
        """Get the full PV name for the Error Waveform."""
        return self.pv("USR:Error-Wfm", ch=ch)

    def pv_reg_wfm(self, ch: int) -> str:
        """Get the full PV name for the Regulation Waveform."""
        return self.pv("USR:Reg-Wfm", ch=ch)

    def pv_volt_wfm(self, ch: int) -> str:
        """Get the full PV name for the Voltage Monitor Waveform."""
        return self.pv("USR:Volt-Wfm", ch=ch)

    def pv_gnd_wfm(self, ch: int) -> str:
        """Get the full PV name for the Ground Current Waveform."""
        return self.pv("USR:Gnd-Wfm", ch=ch)

    def pv_spare_wfm(self, ch: int) -> str:
        """Get the full PV name for the Spare Waveform."""
        return self.pv("USR:Spare-Wfm", ch=ch)

    def pv_wfm_xmax(self, ch: int) -> str:
        """Get the full PV name for Waveform X-Max."""
        return self.pv("SS:WFM-Xmax", ch=ch)

    def pv_wfm_xmin(self, ch: int) -> str:
        """Get the full PV name for Waveform X-Min."""
        return self.pv("SS:WFM-Xmin", ch=ch)

    def pv_ts_scalar(self) -> str:
        """Get the full PV name for the Timestamp Scalar (non-channel)."""
        return self.pv("TS-S-I")

    def pv_timestamp_vala(self) -> str:
        """Get the full PV name for the Timestamp VALA (non-channel)."""
        return self.pv("Timestamp-I.VALA")
