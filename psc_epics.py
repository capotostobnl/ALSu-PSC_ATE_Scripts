"""f
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
from epics import caget, caput


@dataclass
class PSC:
    """
    EPICS adapter for a PSC device.

    Args:
        prefix:     Base PV prefix, e.g. 'lab{3}'
        ch_fmt:     Format string for channel prefix. Default 'CH{ch}:'
                    Examples:
                        'CH{ch}:'        -> CH1:, CH2:, ...
                        'USR:CH{ch}:'    -> USR:CH1:, ...
        timeout:    Default EPICS timeout (seconds)
    """

    prefix: str
    ch_fmt: str = "Chan{ch}:"
    timeout: float = 5.0

    # ---------- PV building ----------
    def ch_prefix(self, ch: int) -> str:
        return self.ch_fmt.format(ch=ch)

    def pv(self, suffix: str, *, ch: Optional[int] = None) -> str:
        """Full PV for suffix, optionally for a specific channel."""
        if ch is None:
            return f"{self.prefix}{suffix}"
        return f"{self.prefix}{self.ch_prefix(ch)}{suffix}"

    # ---------- I/O wrappers ----------
    def get(self, suffix: str, *, ch: Optional[int] = None,
            as_string: bool = False, timeout: Optional[float]
                            = None) -> Any:
        return caget(self.pv(suffix, ch=ch), as_string=as_string,
                     timeout=timeout or self.timeout)

    def put(self, suffix: str, value: Any, *, ch: Optional[int] = None,
            wait: bool = True, timeout: Optional[float] = None) -> bool:
        return bool(caput(self.pv(suffix, ch=ch), value, wait=wait,
                          timeout=timeout or self.timeout))

    def safe_get(self, suffix: str, *, ch: Optional[int] = None,
                 as_string: bool = False, timeout: Optional[float]
                                 = None) -> Any:
        try:
            return self.get(suffix, ch=ch, as_string=as_string,
                            timeout=timeout)
        except Exception as e:
            print(f"caget ERROR {self.pv(suffix, ch=ch)}: {e}")
            return None

    def safe_put(self, suffix: str, value: Any, *, ch: Optional[int] = None,
                 wait: bool = True, timeout: Optional[float] = None) -> bool:
        try:
            return self.put(suffix, value, ch=ch, wait=wait, timeout=timeout)
        except Exception as e:
            print(f"caput ERROR {self.pv(suffix, ch=ch)} <- {value}: {e}")
            return False

# ---------- DUT Info -------------

    def get_num_channels(self) -> int:
        raw = self.safe_get("NumChannels-Mode", as_string=True)
        return int(str(raw)[:1])

    def get_resolution(self) -> str:
        raw = self.safe_get("Resolution-Mode", as_string=True)
        return (str(raw))

    def get_bandwidth(self) -> str:
        raw = self.safe_get("Bandwidth-Mode", as_string=True)
        return str(raw)[:1]

    def get_polarity(self) -> str:
        raw = self.safe_get("Polarity-Mode", as_string=True)
        return (str(raw))

# ---------- Channel PVs ----------
    # Digital outs / modes / setpoints

    def set_power_on1(self, ch: int, val: int | bool) -> bool:
        return self.put("DigOut_ON1-SP", int(val), ch=ch)

    def set_enable_on2(self, ch: int, val: int | bool) -> bool:
        return self.put("DigOut_ON2-SP", int(val), ch=ch)

    def set_park(self, ch: int, val: int | bool) -> bool:
        return self.put("DigOut_Park-SP", int(val), ch=ch)

    def set_dac_setpt(self, ch: int, amps: float) -> bool:
        return self.put("DAC_SetPt-SP", amps, ch=ch)

    def set_op_mode(self, ch: int, mode: int | str) -> bool:
        return self.put("DAC_OpMode-SP", mode, ch=ch)

    def set_rate(self, ch: int, rate: float) -> bool:
        return self.put("SF:AmpsperSec-SP", rate, ch=ch)

    def set_reset(self, ch: int, val: int | bool) -> bool:
        return self.put("DigOut_Reset-SP", int(val), ch=ch)

    # Triggers / status
    def user_shot(self, ch: int) -> bool:
        return self.put("SS:Trig:Usr", 1, ch=ch)

    def is_user_trig_active(self, ch: int) -> int | None:
        return self.safe_get("UsrTrigActive-I", ch=ch)

    # Waveforms (return just the PV names if your code passes them into other
    # libs)
    def pv_dac_wfm(self, ch: int) -> str:
        return self.pv("USR:DAC-Wfm", ch=ch)

    def pv_dcct1_wfm(self, ch: int) -> str:
        return self.pv("USR:DCCT1-Wfm", ch=ch)

    def pv_dcct2_wfm(self, ch: int) -> str:
        return self.pv("USR:DCCT2-Wfm", ch=ch)

    def pv_err_wfm(self, ch: int) -> str:
        return self.pv("USR:Error-Wfm", ch=ch)

    def pv_reg_wfm(self, ch: int) -> str:
        return self.pv("USR:Reg-Wfm", ch=ch)

    def pv_volt_wfm(self, ch: int) -> str:
        return self.pv("USR:Volt-Wfm", ch=ch)

    def pv_gnd_wfm(self, ch: int) -> str:
        return self.pv("USR:Gnd-Wfm", ch=ch)

    def pv_spare_wfm(self, ch: int) -> str:
        return self.pv("USR:Spare-Wfm", ch=ch)

    def pv_wfm_xmax(self, ch: int) -> str:
        return self.pv("SS:WFM-Xmax", ch=ch)

    def pv_wfm_xmin(self, ch: int) -> str:
        return self.pv("SS:WFM-Xmin", ch=ch)

    # Non-channel PVs on the DUT
    def pv_ts_scalar(self) -> str:
        return self.pv("TS-S-I")

    def pv_timestamp_vala(self) -> str:
        return self.pv("Timestamp-I.VALA")

    # Other PVs
    def clear_faults(self, ch: int, val: int | bool) -> bool:
        return self.put("FaultClear-SP", int(val), ch=ch)

    def set_fault_mask(self, bit: int, ch: int, val: int | bool) -> bool:
        return self.put(f"FaultMask:B{bit}-SP", val, ch=ch)

    def get_live_faults(self, ch: int):
        return self.get("FaultsLive-I", ch=ch)

    def get_latched_faults(self, ch: int):
        return self.get("FaultsLat-I", ch=ch)
