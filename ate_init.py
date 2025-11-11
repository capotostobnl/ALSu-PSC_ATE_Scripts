"""ATE Initializtion Submodule
Modified M. Capotosto 11-9-2025
Original: T. Caracappy
"""

from time import sleep
from epics import caput


def ate_init() -> None:
    AteIgndChan = "PSCtest:Ignd:Channel-SP"
    caput("PSCtest:CH1:Vmon:Gain-SP", 0.5)
    caput("PSCtest:CH1:Imon:Gain-SP", 0.25)
    caput("PSCtest:CH2:Vmon:Gain-SP", 0.5)
    caput("PSCtest:CH2:Imon:Gain-SP", 0.25)
    caput("PSCtest:CH3:Vmon:Gain-SP", 0.5)
    caput("PSCtest:CH3:Imon:Gain-SP", 0.25)
    caput("PSCtest:CH4:Vmon:Gain-SP", 0.5)
    caput("PSCtest:CH4:Imon:Gain-SP", 0.25)
    caput(AteIgndChan, 3)
    sleep(1)
    print("ATE is Initialized...")
