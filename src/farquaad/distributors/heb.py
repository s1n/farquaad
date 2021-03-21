from urllib.request import urlopen
import json

from . import Distributor
from ..base import Page

class HEB(Distributor):

    def __init__(self, driver, logger):
        super().__init__("H.E.B.", driver, logger)
        self.statusUrl = "https://heb-ecom-covid-vaccine.hebdigital-prd.com/vaccine_locations.json"
        self.page_appointment = AppointmentForm(driver, logger)
        self.page_patient = PatientForm(driver, logger)
        self.page_confirm = Page(driver, logger)
    
    def process(self, openSlot, patientData):
        self._logger.info("HEB processor; processing Appointment, Patient, Confirmation pages")
        
        shouldContinue = True
        if not self.page_appointment.load(openSlot["url"]):
            return False
        if not self.page_appointment.populate(patientData):
            return False
        self.page_appointment.capture("/tmp/farquaad/heb_appointment_page.png")
        self.page_appointment.proceed()

        if not self.page_patient.load():
            return False
        if not self.page_patient.populate(patientData):
            return False
        self.page_patient.capture("screenshots/heb_appointment_page.png")
        self.page_patient.proceed()

        # this is just a plain page, nothing to do here
        self.page_confirm.capture("screenshots/heb_appointment_page.png")
        return True

    def verify(self, openSlot):
        self._logger.info("HEB sanity test")
        return self.page_appointment.load(openSlot["url"])
    
    def checkAvailability(self):
        self._logger.info("Checking HEB API for availability")
        locations = json.loads(urlopen(self.statusUrl).read())['locations']

        filtered = [x for x in locations if x["openTimeslots"] > 0]
        return filtered

class AppointmentForm(Page):

    def __init__(self, driver, logger):
        super().__init__(driver, logger)
        self.widgets = {
            "combo-manufacturer": "//lightning-combobox[1]",
            "item-manufacturer": {
                "Any": "//lightning-combobox[1]//*[@data-value='Any']",
                "J&J/Janssen": "//lightning-combobox[1]//*[@data-value='Janssen']",
                "Moderna": "//lightning-combobox[1]//*[@data-value='Moderna']",
                "Pfizer": "//lightning-combobox[1]//*[@data-value='Pfizer']",
            },
            "combo-date": "//lightning-combobox[2]",
            "items-date": "//lightning-combobox[2]//*//lightning-base-combobox-item",
            "item-date": [
                "//lightning-combobox[2]//*//lightning-base-combobox-item[10]/span[2]/span",
            ],
            "combo-time": "//lightning-combobox[3]",
            "items-time": "//lightning-combobox[3]//*//lightning-base-combobox-item",
            "item-time": [
                "//lightning-combobox[3]//*//lightning-base-combobox-item[1]/span[2]/span",
            ],
            "button-continue": "//lightning-button/button",
            "sucka": "//*[contains(text(), 'There are no available time slots.')]",
        }

    def populate(self, patientData):
        self._logger.info("Populating the Appointment form")
        #self._logger.info("Form fields: " + json.dumps(self.widgets, indent=4))

        # for each manufacturer the patient will accept, find the first available date and time
        # problem here is this form is dynamic, uses shadow DOM, and errors out _lots_ of ways
        for m in patientData["manufacturer"]:
            self.scrollTo(self.widgets["combo-manufacturer"], click=True)
            self._logger.info(f"Selecting shot: {m}")
            self.clickOn(self.widgets["item-manufacturer"][m])
            try:
                self.wait(self.widgets["combo-date"], 1)
                self._logger.info(f"Manufacturer successfully selected as {m}")
            except:
                self._logger.info("Appointment date combobox is unavailable, continuing")
                continue
            self.scrollTo(self.widgets["combo-date"], click=True)
            dateOptions = self.findAll(self.widgets["items-date"])
            if len(dateOptions) <= 0:
                self._logger.info(f"No dates found for {m}, continuing")
                continue
            self._logger.info(f"Found {len(dateOptions)} date options for {m}")
            for d in dateOptions:
                d.click()
                try:
                    self.wait(self.widgets["combo-time"], 1)
                    self._logger.info(f"Date successfully selected for {m}")
                except:
                    self._logger.info("Appointment time combobox is unavailable, continuing")
                    continue
                self.scrollTo(self.widgets["combo-time"], click=True)
                timeOptions = self.findAll(self.widgets["items-time"])
                if len(timeOptions) <= 0:
                    self._logger.info("No time slots found, continuing")
                    continue
                self._logger.info(f"Found {len(timeOptions)} time slot options for {m}")
                for t in timeOptions:
                    t.click()
                    try:
                        self.wait(self.widgets["button-continue"], 1)
                        self._logger.info(f"Time slot successfully selected for {m}")
                    except:
                        self._logger.info("Continue button is unavailable, continuing")
                        continue
                    if self.isPresent(self.widgets["button-continue"]):
                        return True
        return False
    
    def load(self, url):
        self._logger.info("Loading the Appointment Form")
        return super().load(url, self.widgets["combo-manufacturer"]) and not self.isPresent(self.widgets["sucka"])

    def proceed(self):
        self._logger.info("Proceeding from the Appointment Form to the next page")
        self.scrollTo(self.widgets["button-continue"], click=True)

class PatientForm(Page):
    def __init__(self, driver, logger):
        super().__init__(driver, logger)
        self.widgets = {
            "text-firstname": "//input[contains(@name, 'First_Name')]",
            "text-lastname": "//input[contains(@name, 'Last_Name')]",
            "text-email": "//input[contains(@name, 'Email_Address')]",
            "text-birthdate": "//input[@data-type='birthdate']",
            "text-phone": "//input[@data-type='tel']",
            "text-peoplesoft": "//lightning-input[4]//*//input",
            "combo-provider": "//lightning-combobox[1]",
            "item-provider": {
                "yes": "//lightning-combobox[1]//*//lightning-base-combobox-item[1]/span[2]/span",
                "no": "//lightning-combobox[1]//*//lightning-base-combobox-item[2]/span[2]/span",
            },
            "text-provider": "//lightning-input[5]//*//input",
            "text-providerid": "//lightning-input[6]//*//input",
            "text-groupnumber": "//lightning-input[6]//*//input",
            "combo-phase": "//lightning-combobox[2]",
            "item-phase": {
                "phase1": "//lightning-combobox[2]//*//lightning-base-combobox-item[1]/span[2]/span",
                "phase1b": "//lightning-combobox[2]//*//lightning-base-combobox-item[2]/span[2]/span",
                "phase1bplus": "//lightning-combobox[2]//*//lightning-base-combobox-item[3]/span[2]/span",
                "phase1c": "//lightning-combobox[2]//*//lightning-base-combobox-item[4]/span[2]/span",
                #"phase2": "//lightning-combobox[2]//*//lightning-base-combobox-item[5]/span[2]/span"
            },
            "button-schedule": "//lightning-button[2]/button",
        }

    def populate(self, patientData):
        self._logger.info("Populating the Patient form")

        # first the mandatory text fields
        self.scrollTo(self.widgets["text-firstname"])
        self.sendKeys(self.widgets["text-firstname"], patientData["firstname"])
        self.scrollTo(self.widgets["text-lastname"])
        self.sendKeys(self.widgets["text-lastname"], patientData["lastname"])
        self.scrollTo(self.widgets["text-email"])
        self.sendKeys(self.widgets["text-email"], patientData["email"])
        self.scrollTo(self.widgets["text-birthdate"])
        self.sendKeys(self.widgets["text-birthdate"], patientData["birthdate"])
        self.scrollTo(self.widgets["text-phone"])
        self.sendKeys(self.widgets["text-phone"], patientData["phone"])

        self.scrollTo(self.widgets["text-peoplesoft"], click=True)
        if "peoplesoft" in patientData.keys() and patientData["peoplesoft"]:
            self.sendKeys(self.widgets["text-peoplesoft"], self.widgets["peoplesoft"])

        self.scrollTo(self.widgets["combo-provider"], click=True)
        if "provider" in patientData.keys() and patientData["provider"]:
            self.clickOn(self.widgets["item-provider"]["yes"])
            #click to force the combo closed, just in case
            self.scrollTo(self.widgets["text-provider"], click=True)
            self.sendKeys(self.widgets["text-provider"], patientData["provider"])
        else:
            self.clickOn(self.widgets["item-provider"]["no"])

        #clear the state, make sure none of the drop downs are open
        self.scrollTo(self.widgets["text-providerid"], click=True)
        if "providerid" in patientData.keys() and patientData["providerid"]:
            self.sendKeys(self.widgets["text-providerid"], self.widgets["providerid"])
        
        self.scrollTo(self.widgets["text-groupnumber"], click=True)
        if "groupnumber" in patientData.keys() and patientData["groupnumber"]:
            self.sendKeys(self.widgets["text-groupnumber"], self.widgets["groupnumber"])

        self.scrollTo(self.widgets["combo-phase"], click=True)
        self.clickOn(self.widgets["item-phase"][patientData["certify"].lower()])
        return True

    def load(self):
        self._logger.info("Loading the Appointment Form")
        #can't directly load, just confirm the page loaded from the prior proceed
        try:
            self.wait(self.widgets["button-schedule"])
        except:
            return False
        return self.isPresent(self.widgets["button-schedule"])
    
    def proceed(self):
        self._logger.info("Proceeding from the Patient Form to the next page")
        self.scrollTo(self.widgets["button-schedule"], click=True)