import sys
from time import sleep
from ..base import Filter

class Distributor:
    def __init__(self, name, driver, logger):
        self._name = name
        self._driver = driver
        self._logger = logger
        self._logger.info(f"Initialized distributor registration journey: {self._name}")

    def checkAvailability(self, restrictions):
        self._logger.info(f"Checking distributor registration availability: {self._name}")

    def monitor(self, home, restrictions, delay):
        self._logger.info(f"Monitoring distributor registration availability: {self._name}")
        availability = None
        refine = Filter(home, restrictions)
        while not availability:
            sleep(delay)
            availability = self.checkAvailability(restrictions)
            availability = refine.apply(availability)
            availability = sorted(availability, key=lambda slot: slot["distance"])
        return availability
    
    def process(self, openSlot, patientData):
        self._logger.info(f"Processing distributor registration journey: {self._name}")

    def schedule(self, availability, patientdata):
        self._logger.info(f"Searching for and scheduling distributor registration journey: {self._name}")
        booked = False
        for appt in availability:
            booked = self.process(appt, patientdata)
            if booked:
                return appt

    def finalize(self):
        self._driver.quit()
        self._logger.info(f"Finalizing registration distributor: {self._name}")

