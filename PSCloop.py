"""DocstringPlaceholder
"""
import os
from time import sleep
from datetime import datetime

from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import (SimpleDocTemplate, Table)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from epics import caget, caput
from evr_test import run_evr_test
from fault_tests import fault_tests
from psr_test import power_supply_regulation_test
from jump_test import jump_test
from smooth_ramp_test import smooth_ramp_test
###############################################################################
# ************Channel Access flags for correcting environment issues***********
# os.environ['EPICS_CA_DEBUG'] = '0'
# os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'
# os.environ['EPICS_CA_ADDR_LIST'] = '127.0.0.1'


###############################################################################
# **************Get DUT Info************
while True:
    PSCsn = input('\nEnter PSC serial number: (Enter "H" for help,): ')

    # Check for the 'H' help command
    if PSCsn.upper() == "H":
        print(
            "Stopping Program. Serial Number is on the ITR document attached "
            "to the PSC Chassis"
        )
        exit()

    # Check for a 4-digit serial number, checks if the string contains
    # only digits (0-9), 4 digits
    elif PSCsn.isdigit() and len(PSCsn) == 4:
        # If valid, continue...
        print(f"Serial number {PSCsn} accepted.")
        break

    # Handle invalid input
    else:
        print(
            "Invalid input. Please enter 'H' for help, or a valid 4-digit "
            "serial number (e.g., '0015', '9876')."
        )

while True:
    unit_num = input('\nEnter the PSC Unit Number: ')
    if unit_num.isdigit():
        num_value = int(unit_num)
        if 1 <= num_value <= 6:
            print(f"PSC Unit Number {unit_num} accepted.")
            break
        else:
            print("Invalid input. The PSC Unit Number must be a number"
                  "between 1 and 6.")

PV_PREFIX = input('\nEnter the PV prefix for this device, excluding unit'
                  'number (Default="lab{unit_num}):')
if PV_PREFIX == "":
    PV_PREFIX = "lab"

PV_PREFIX = PV_PREFIX + f"{{{unit_num}}}"
print(f"PV_PREFIX = {PV_PREFIX}")

###############################################################################


###############################################################################
# **************PV Configuration************
# EPICS PVs for PSC IOC:
# PSC Device Type PVs:
NumChan = PV_PREFIX + "NumChannels-Mode"
Resolution = PV_PREFIX + "Resolution-Mode"
Bandwidth = PV_PREFIX + "Bandwidth-Mode"
Polarity = PV_PREFIX + "Polarity-Mode"

num_chans = caget(NumChan, as_string=True)  # Number of Channels
Res = caget(Resolution, as_string=True)  # Resolution
BW = caget(Bandwidth, as_string=True)  # Bandwidth
Pol = caget(Polarity, as_string=True)  # Polarity
CH_MAX = 2  # Initialize for 2ch PSC...
if num_chans == "4 Channel":
    CH_MAX = 4
print(f"This PSC has {CH_MAX} Channels")
###############################################################################

###############################################################################
# **************Report Generator************
props = dict(boxstyle="round", facecolor="wheat", alpha=0.9)
good = dict(boxstyle="round", facecolor="palegreen", alpha=0.9)
bad = dict(boxstyle="round", facecolor="pink", alpha=0.9)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Create timestamps
# This is the base name for the directory and the PDF,
# e.g., "PSC0015_20251106_010800"

REPORT_BASE_NAME = f"PSC-{num_chans}CH-{Resolution}{Bandwidth}-" \
                   f"SN{PSCsn}_{timestamp}"
output_dir_path = os.path.join(os.getcwd(), REPORT_BASE_NAME)

try:
    # We use exist_ok=False to safely abort if the dir (somehow) exists
    os.makedirs(output_dir_path, exist_ok=False)
    print(f"Successfully created output directory:\n{output_dir_path}\n")
except FileExistsError:
    print(f"Directory {output_dir_path} already exists. Aborting.")
    exit()
except OSError as e:
    print(f"****** ERROR ******\nFailed to create directory: {e}")
    exit()

try:
    os.chdir(output_dir_path)
    print(f"Changed working directory to: {output_dir_path}")
except OSError as e:
    print(f"****** ERROR ******\nFailed to change directory: {e}")
    exit()

FREPORT_FILENAME = f"{REPORT_BASE_NAME}.pdf"

# Create the Report Document....
doc = SimpleDocTemplate(
    FREPORT_FILENAME,
    pagesize=letter,
    rightMargin=30,
    leftMargin=30,
    topMargin=30,
    bottomMargin=18,
)
styles = getSampleStyleSheet()
elements = []


tdata = []
tdata.append(["PSC Functional Test Results", 0])
tdata.append(["Power Supply Controller Configuration", 0])
tdata.append(["Serial Number", PSCsn])
tdata.append(["Number of Channels", num_chans])
tdata.append(["Resolution", Res])
tdata.append(["Bandwidth", BW])
tdata.append(["Polarity", Pol])

rowH = [
    0.4 * inch,
    0.35 * inch,
    0.27 * inch,
    0.27 * inch,
    0.27 * inch,
    0.27 * inch,
    0.27 * inch,
]
colH = [3 * inch, 3 * inch]

ta = Table(
    tdata,
    colH,
    rowH,
    style=[
        ("SPAN", (0, 0), (1, 0)),
        ("SPAN", (0, 1), (1, 1)),
        ("ALIGN", (0, 0), (1, 1), "CENTER"),
        ("FONTSIZE", (0, 0), (1, 0), 16),
        ("FONTSIZE", (0, 1), (1, 1), 14),
        ("VALIGN", (0, 0), (1, 6), "MIDDLE"),
        ("LINEABOVE", (0, 1), (1, 2), 2, colors.black),
        ("BACKGROUND", (0, 0), (1, 1), colors.lemonchiffon),
        ("BACKGROUND", (0, 2), (0, 6), colors.lightblue),
        ("FONTSIZE", (0, 1), (1, 6), 12),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BOX", (0, 0), (-1, -1), 2, colors.black),
    ],
)

elements.append(ta)

print(num_chans, Res, BW, Pol)
###############################################################################


###############################################################################
# **************EVR Test************
evr_image = run_evr_test(PV_PREFIX, props, good, bad)
elements.append(evr_image)
###############################################################################


######################################################################
# Start of the Big Loop!
######################################################################
ATE_I_GND_CHAN = "PSCtest:Ignd:Channel-SP"
caput(ATE_I_GND_CHAN, 3)
sleep(1)
for chan in range(1, (CH_MAX + 1)):
    CH_PREFIX = "Chan" + str(chan) + ":"
    print("Top of Loop", chan, CH_PREFIX)
    PWR = PV_PREFIX + CH_PREFIX + "DigOut_ON1-SP"
    ENB = PV_PREFIX + CH_PREFIX + "DigOut_ON2-SP"
    PRK = PV_PREFIX + CH_PREFIX + "DigOut_Park-SP"
    DacSP = PV_PREFIX + CH_PREFIX + "DAC_SetPt-SP"
    RATE = PV_PREFIX + CH_PREFIX + "SF:AmpsperSec-SP"
    caput(DacSP, 0)
    caput(PWR, 0)
    caput(ENB, 0)
    caput(PRK, 0)
    caput(RATE, 4)

    ###########################################################################
    # **************Fault Tests************
    fault_test_elements, IgndSP = fault_tests(PV_PREFIX, CH_PREFIX, chan)
    elements.extend(fault_test_elements)
    ###########################################################################

    ###########################################################################
    # **************PS Regulation Tests************
    psr_test_elements = power_supply_regulation_test(PV_PREFIX, CH_PREFIX,
                                                     chan, props, good, bad,
                                                     styles)
    elements.extend(psr_test_elements)
    ###########################################################################

    ###########################################################################
    # **************Jump Tests************
    jump_test_elements = jump_test(PV_PREFIX, CH_PREFIX, chan, props,
                                   styles, IgndSP)
    elements.extend(jump_test_elements)
    ###########################################################################

    ###########################################################################
    # **************Smooth Ramp Tests************
    smooth_ramp_test_elements = smooth_ramp_test(PV_PREFIX, CH_PREFIX, chan,
                                                 props, styles, IgndSP)
    elements.extend(smooth_ramp_test_elements)
    ###########################################################################

##############################################################################
# End of Report...Building....
##############################################################################
doc.build(elements)
