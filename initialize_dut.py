import os
from datetime import datetime
from dataclasses import dataclass, field
from epics import caget


@dataclass
class DUT:
    PSCsn: str = ""
    PVprefix: str = ""
    report_dir: str = field(init=False, default="")
    raw_data_dir: str = field(init=False, default="")
    num_channels: int = field(init=False, default=2)
    resolution: str = field(init=False, default="")
    bandwidth: str = field(init=False, default="")
    polarity: str = field(init=False, default="")
    shipment_num: int = field(init=False)
    shipment_dir: str = field(init=False)
    raw_data_dir: str = field(init=False)
    dir_timestamp: str = field(init=False)

    def prompt_inputs(self):
        """Prompt user for basic DUT info."""
        self.shipment_num = self._get_shipment_num()
        self.PSCsn = self._get_psc_sn()
        self.PVprefix = self._get_psc_pv_prefix()
        self.query_psc_config()
        self.report_dir = \
            self.make_shipment_dir()
        self.raw_data_dir, self.dir_timestamp = \
            self.make_rawdata_subdir()

    def _get_shipment_num(self) -> int:
        while (True):
            shipment_num = input('\nEnter Shipment Number (Used for"'
                                 'report directory): ')

            # Check if a digit was entered and re-prompt if not...
            if (not shipment_num.isdigit()):
                print("Shipment Number must be a numeric value")
                continue

            else:
                return int(shipment_num)

    def _get_psc_sn(self) -> str:
        while (True):
            PSCsn = input('\nEnter PSC serial number: (Enter "H" '
                          'for help):')
            # If Help...
            if (PSCsn == "H"):
                print("Serial Number is on the ITR document"
                      "attached to the PSC Chassis")
                continue

            # Check if a digit was entered and re-prompt if not...
            elif (not PSCsn.isdigit()):
                print("Serial number must be numeric, "
                      "between 0001 and 9999")
                continue

            # Check if digit between 1 and 9999...
            else:
                PSCsn = int(PSCsn)
                if not 1 <= PSCsn <= 9999:
                    print("Serial number must be numeric, "
                          "between 001 and 9999")
                    continue

            # Add leading zeroes to PSCsn...
            PSCsn = f"{PSCsn:04d}"
            return PSCsn

    def _get_psc_pv_prefix(self):
        while (True):
            psc_num = input("Enter the PSC Number under test "
                            "(e.g., for PSC 'lab{3}', enter "
                            "'3': ")

            # Check if numeric...
            if (not psc_num.isdigit()):
                print("PSC Number must be a numeric, "
                      "between 1 and 6")
                continue

            else:
                # Check if between 1 and 6...
                psc_num = int(psc_num)
                if not 1 <= psc_num <= 6:
                    print("Serial number must be numeric, "
                          "between 001 and 9999")
                    continue

            # psc_num is now confirmed to be valid...break
            break

        PVprefix = f"lab{{{psc_num}}}"
        print(f"PVprefix = {PVprefix}")
        return PVprefix

    def make_shipment_dir(self, base_dir="."):
        """Create shipment directory"""

        dir_name = f"Shipment #{self.shipment_num}"
        shipment_dir = os.path.join(base_dir, dir_name)
        os.makedirs(shipment_dir, exist_ok=True)
        return shipment_dir

    def make_rawdata_subdir(self):
        """Create a subdir under shipment_dir"""

        # Create timestamp...
        dir_timestamp = datetime.now().strftime(
            "%m-%d-%y_%H-%M")

        # build dir name...
        subdir_name = (f"{self.num_channels}ch_{self.resolution[:2]}"
                       f"{self.bandwidth[:1]}_SN{self.PSCsn}_RawData_"
                       f"{dir_timestamp}")
        raw_data_dir = os.path.join(
            self.report_dir, subdir_name)

        os.makedirs(raw_data_dir, exist_ok=True)

        return raw_data_dir, dir_timestamp

    def query_psc_config(self):
        """Perform CA Get commands, populate fields for PSC CFG"""
        print(f"Self.PVprefix = {self.PVprefix}")
        num_chan_pv = f"{self.PVprefix}NumChannels-Mode"
        resolution_pv = f"{self.PVprefix}Resolution-Mode"
        bandwidth_pv = f"{self.PVprefix}Bandwidth-Mode"
        polarity_pv = f"{self.PVprefix}Polarity-Mode"

        # Strip/slice ' Channel' from the end of number of chans...
        # Then convert to int...
        self.num_channels = int(str(caget(num_chan_pv, as_string=True)
                                    or "")[:1])
        self.resolution = str(caget(resolution_pv, as_string=True))
        self.bandwidth = str(caget(bandwidth_pv, as_string=True))
        self.polarity = str(caget(polarity_pv, as_string=True))
