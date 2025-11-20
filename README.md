# **PSC Automated Test Environment (ATE) – Test Suite**

This repository contains the full automated test environment (ATE) and reporting framework for **ALSu Power Supply Controller (PSC)** validation.  
It performs end-to-end testing of PSC hardware, ATE interfaces, EVR timing, DCCT/IGND/SPARE regulation, FOFB behavior, and produces a professionally formatted PDF report for shipment documentation.

The system integrates:

- **PSC EPICS IOC communication** (`psc_epics.py`)
- **ATE Tester IOC communication** (`ate_epics.py`)
- Automated test modules (jump, smooth ramp, regulation, EVR timing, FOFB)
- Auto-generated reports with plots and pass/fail tables
- Automated directory management and shipment logging

---

## **Repository Structure**

```
├── main.py                     # Top-level test runner (entry point)
├── initialize_dut.py           # DUT class: PSC info, directory management, PV prefix, etc.
├── report_generator.py         # PDF generation, formatting, section helpers
│
├── ate_epics.py                # EPICS adapter for ATE Tester IOC
├── psc_epics.py                # EPICS adapter for PSC IOC (waveforms, setpoints, state)
│
├── ate_init.py                 # ATE initialization & channel setup
├── ate_fault_tests.py          # Automated ATE fault injection and detection tests
├── jump_test.py                # PSC jump test (transient response, DCCT, IGND, SPARE)
├── smooth_ramp_test.py         # PSC smooth ramp characterization
├── ps_regulation_test.py       # Regulation tests using PSC DAC loopback / rails
├── evr_timing_test.py          # EVR 1 Hz timestamp verification
├── fofb_test.py                # FOFB Daisy Packet monotonicity & RX timing test
│
├── caen_fast_genpacket.c       # Low-level UDP packet generator (used by FOFB test)
├── caen_fast_genpacket_loop_inf.sh  # Continuous DAISY packet loop script
│
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation
```

---

## **Overview of the Test Flow**

The main entry point is:

```
python3 main.py
```

The test sequence inside `main.py`:

1. **DUT Initialization**
   - User enters serial number, shipment number, operator, etc.
   - Creates a new `Shipment #XX/` directory
   - Creates raw data and PDF report folders

2. **ATE & PSC Initialization (`ate_init.py`)**
   - Clears faults and resets PSC
   - Configures IGND routing and DCCT channels
   - Configures gains, polarity, and calibration state

3. **Tests Executed**
   - **EVR Timing Test** *(optional)*
   - **ATE Fault Tests**  
     - FLT1, FLT2, SPARE, and DCCT fault injection
   - **PSC Regulation Test**
   - **Jump Test**
   - **Smooth Ramp Test**
   - **FOFB Packet Test** *(fast-bandwidth PSC only)*

4. **PDF Report Generation**
   - Plots of all waveforms  
   - Pass/Fail tables  
   - EVR timestamp plot  
   - FOFB results (if applicable)  
   - Auto-naming based on DUT info  

---

## **Key Modules**

### **`psc_epics.py`**
Handles PSC-specific PV interactions:
- DAC/SP, GND/SP, MODE, RATE
- DCCT1/2 waveforms
- IGND readbacks
- Snapshot triggers and waveform extraction
- Fault masks, resets, live & latched faults

### **`ate_epics.py`**
Abstraction layer for the ATE tester IOC:
- Sets IGND channel and IGND setpoint
- DCCT fault routing
- Fault injection (FLT1, FLT2, Spare, PCFault)
- Tester2 command interface
- Tester status readback

### **`ate_fault_tests.py`**
Fault injection & verification:
- Checks live + latched fault bits
- Uses bit masks (0x80, 0x100, 0x200, 0x40)
- Clears faults and verifies zero state
- Builds Pass/Fail report table

### **`jump_test.py`**
Transient measurement of PSC performance:
- Detects fast transitions (diff → argmax)
- Extracts pre/post transition windows
- Plots DAC, DCCT1/2, ERR, REG, VOLT, GND, SPARE

### **`smooth_ramp_test.py`**
Smooth-ramp behavior & loop stability:
- Slow directional ramps (positive/negative)
- IGND stability verification
- DCCT and ERR tracking

### **`ps_regulation_test.py`**
Regulation loop stability tests:
- DAC and Regulation waveform capture
- Overshoot/settling visualization

### **`evr_timing_test.py`**
Verifies EVR 1 Hz timestamps increment correctly.

### **`fofb_test.py`**
Daisy packet monotonicity test:
- Uses CAEN generator (C version + shell script)
- Validates packet ordering & RX timing

---

## **Installation**

Install Python dependencies:

```
pip install -r requirements.txt
```

Includes:
- `numpy`
- `matplotlib`
- `pyepics`
- `reportlab`

---

## **Supported Environment**

- Python **3.10+**
- EPICS Channel Access available on the network
- Access to PSC IOC and ATE Tester IOC

---

## **Output Directory Structure**

Every test run creates:

```
Shipment #{N}/		     # If it does not yet exist
├── Raw_Data/                # PNG waveform images
└── Test_Report_{SN}.pdf     # Final auto-generated report

```

---



---

## **Contact**

NSLS-II Diagnostics & Instrumentation Group  
Brookhaven National Laboratory  
PSC ATE Maintainer: **Michael Capotosto**

---


