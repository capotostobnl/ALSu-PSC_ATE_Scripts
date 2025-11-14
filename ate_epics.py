"""
EPICS adapter for the ATE / Tester IOC.

M. Capotosto 11/11/2025
"""

from typing import Literal, Iterable, Optional, Any
from dataclasses import dataclass
from epics import caget, caput

Mode = Literal["TEST", "CAL"]
Polarity = Literal["BPC", "UPC"]  # bo ZNAM/ONAM
CalState = Literal["OFF", "ON"]   # bo ZNAM/ONAM


class FaultChannel:
    NONE = 0
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4


class IgndChannel:
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4


def _as_int_bool(val: int | bool) -> int:
    return int(bool(val))


def _as_mode(value: int | str) -> int:
    """TEST->0, CAL->1; integers pass through (0/1)."""
    if isinstance(value, str):
        v = value.strip().upper()
        if v == "TEST":
            return 0
        if v == "CAL":
            return 1
        raise ValueError("Mode must be 'TEST' or 'CAL' (or 0/1).")
    if value in (0, 1):
        return int(value)
    raise ValueError("Mode integer must be 0 or 1.")


def _as_cal_state(value: int | str | bool) -> int:
    """OFF->0, ON->1; bool maps to 0/1."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, str):
        v = value.strip().upper()
        if v == "OFF":
            return 0
        if v == "ON":
            return 1
        raise ValueError("CAL state must be 'OFF' or 'ON' (or 0/1).")
    if value in (0, 1):
        return int(value)
    raise ValueError("CAL state integer must be 0 or 1.")


def _as_polarity(value: int | str) -> int:
    """BPC->0, UPC->1; integers pass (0/1)."""
    if isinstance(value, str):
        v = value.strip().upper()
        if v == "BPC":
            return 0
        if v == "UPC":
            return 1
        raise ValueError("Polarity must be 'BPC' or 'UPC' (or 0/1).")
    if value in (0, 1):
        return int(value)
    raise ValueError("Polarity integer must be 0 or 1.")


# --------------------------------- Tester ----------------------------------

@dataclass
class ATE:
    """
    Specialized EPICS adapter for the ATE tester IOC.

    Args:
        prefix: $(P) base, e.g. 'PSCtest:' (include trailing colon if used).
        ch_fmt: channel segment format; this IOC uses 'CH{ch}:'.
        timeout: default EPICS timeout in seconds.
    """
    prefix: str = "PSCtest:"
    ch_fmt: str = "CH{ch}:"
    timeout: float = 5.0

    # ---------------- PV building ----------------
    def _ch(self, ch: int) -> str:
        return self.ch_fmt.format(ch=ch)

    def pv(self, suffix: str, *, ch: Optional[int] = None) -> str:
        if ch is None:
            return f"{self.prefix}{suffix}"
        return f"{self.prefix}{self._ch(ch)}{suffix}"

    # ---------------- I/O wrappers ----------------
    def get(self, suffix: str, *, ch: Optional[int] = None, as_string:
            bool = False,
            timeout: Optional[float] = None) -> Any:
        return caget(self.pv(suffix, ch=ch), as_string=as_string,
                     timeout=timeout or self.timeout)

    def put(self, suffix: str, value: Any, *, ch: Optional[int] = None,
            wait: bool = True, timeout: Optional[float] = None) -> bool:
        return bool(caput(self.pv(suffix, ch=ch), value, wait=wait,
                          timeout=timeout or self.timeout))

    # Safe variants (log to stdout; don't raise)
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

    # ---------------- Non-channel PVs ----------------
    def set_ip_settings(self, ip_port: str) -> bool:
        """$(P)IP:Settings-SP (stringout) — e.g. '192.168.1.10:1234'."""
        return self.put("IP:Settings-SP", ip_port)

    def set_cal_state(self, state: CalState | int | bool) -> bool:
        """$(P)CAL:State-SP (bo) — OFF/ON."""
        return self.put("CAL:State-SP", _as_cal_state(state))

    def set_polarity(self, pol: Polarity | str | int) -> bool:
        """$(P)Polarity-SP (bo) — BPC/UPC."""
        return self.put("Polarity-SP", _as_polarity(pol))

    def set_dcct_fault_channel(self, chan: int) -> bool:
        """$(P)DCCT:Fault:Channel-SP (mbbo) — 0 NONE, 1..4 CHn."""
        if chan not in (FaultChannel.NONE, FaultChannel.CH1, FaultChannel.CH2,
                        FaultChannel.CH3, FaultChannel.CH4):
            raise ValueError("Fault channel must be 0..4 (NONE/CH1..CH4).")
        return self.put("DCCT:Fault:Channel-SP", int(chan))

    def set_ignd_channel(self, chan: int) -> bool:
        """$(P)Ignd:Channel-SP (mbbo) — 1..4 CHn."""
        if chan not in (IgndChannel.CH1, IgndChannel.CH2, IgndChannel.CH3,
                        IgndChannel.CH4):
            raise ValueError("Ignd channel must be 1..4 (CH1..CH4).")
        return self.put("Ignd:Channel-SP", int(chan))

    def set_cal_dac(self, value: float) -> bool:
        """$(P)CAL:DAC-SP (ao)."""
        return self.put("CAL:DAC-SP", float(value))

    def set_ignd_value(self, value: float) -> bool:
        """$(P)Ignd-SP (ao)."""
        return self.put("Ignd-SP", float(value))

    def get_status(self) -> int | None:
        """$(P)Readback:Status-I (longin)."""
        v = self.safe_get("Readback:Status-I")
        return None if v is None else int(v)

    # Waveform/string PVs
    def write_manual_cmd(self, text: str) -> bool:
        """$(P)MAN-CMD-SP (waveform CHAR, NELM=20). Truncates to 20 chars."""
        return self.put("MAN-CMD-SP", text[:20])

    def read_tester2_cmd(self) -> str | None:
        """$(P)Tester2:CMD-I (waveform CHAR, NELM=30)."""
        val = self.safe_get("Tester2:CMD-I", as_string=True)
        if val is None:
            return None
        # pyepics may return bytes/str depending on config
        try:
            return val.decode()[:30] if isinstance(val, (bytes, bytearray)) \
                else str(val)[:30]
        except Exception:
            return str(val)[:30]

    # DCCT rails (ai)
    def read_p15_14(self) -> float | None:
        return self.safe_get("DCCT:P15V:14-I")

    def read_n15_14(self) -> float | None:
        return self.safe_get("DCCT:N15V:14-I")

    def read_p15_58(self) -> float | None:
        return self.safe_get("DCCT:P15V:58-I")

    def read_n15_58(self) -> float | None:
        return self.safe_get("DCCT:N15V:58-I")

    # ---------------- Channel PVs ----------------
    # CHx:Mode-SP (bo) with ZNAM TEST, ONAM CAL
    def set_mode(self, ch: int, mode: Mode | int) -> bool:
        """$(P)CH{n}:Mode-SP — 'TEST'/0 or 'CAL'/1."""
        return self.put("Mode-SP", _as_mode(mode), ch=ch)

    # Fault inputs per-channel (bo Low/High)
    def set_flt1(self, ch: int, level: int | bool) -> bool:
        """$(P)CH{n}:FLT1-SP — 0 Low / 1 High."""
        return self.put("FLT1-SP", _as_int_bool(level), ch=ch)

    def set_flt2(self, ch: int, level: int | bool) -> bool:
        """$(P)CH{n}:FLT2-SP — 0 Low / 1 High."""
        return self.put("FLT2-SP", _as_int_bool(level), ch=ch)

    def set_fltspare(self, ch: int, level: int | bool) -> bool:
        """$(P)CH{n}:Spare-SP — 0 Low / 1 High."""
        return self.put("Spare-SP", _as_int_bool(level), ch=ch)

    # PC Fault per-channel (bo Reset/Set)
    def set_pc_fault(self, ch: int, set_fault: int | bool) -> bool:
        """$(P)CH{n}:PCFault-SP — 0 Reset / 1 Set."""
        return self.put("PCFault-SP", _as_int_bool(set_fault), ch=ch)

    # Gains per-channel
    def set_vmon_gain(self, ch: int, gain: float) -> bool:
        """$(P)CH{n}:Vmon:Gain-SP (ao)."""
        return self.put("Vmon:Gain-SP", float(gain), ch=ch)

    def set_imon_gain(self, ch: int, gain: float) -> bool:
        """$(P)CH{n}:Imon:Gain-SP (ao)."""
        return self.put("Imon:Gain-SP", float(gain), ch=ch)

    # ---------------- Batch helpers ----------------
    def set_all_modes(self, mode: Mode | int,
                      channels: Iterable[int] = (1, 2, 3, 4)) -> list[bool]:
        return [self.set_mode(ch, mode) for ch in channels]

    def set_all_vmon_gain(self, gain: float, channels: Iterable[int] =
                          (1, 2, 3, 4)) -> list[bool]:
        return [self.set_vmon_gain(ch, gain) for ch in channels]

    def set_all_imon_gain(self, gain: float,
                          channels: Iterable[int] =
                          (1, 2, 3, 4)) -> list[bool]:
        return [self.set_imon_gain(ch, gain) for ch in channels]

    def clear_all_pc_faults(self, channels: Iterable[int] =
                            (1, 2, 3, 4)) -> list[bool]:
        """Reset (0) all PCFault bo's."""
        return [self.set_pc_fault(ch, 0) for ch in channels]
