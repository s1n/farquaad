import sys
import queue

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Restrictions(object):
    def __init__(self, cities=[], zipcodes=[], distance=0):
        self.cities = cities
        self.zipcodes = zipcodes
        self.distance = distance

class Page:
    """Base class for defining common page interaction elements
    """

    def __init__(self, driver, logger):
        self._driver = driver
        self._logger = logger
    
    def clickOn(self, xpath):
        return self._driver.find_element_by_xpath(xpath).click()
    
    def sendKeys(self, xpath, value):
        return self.find(xpath).send_keys(value)

    def wait(self, waitxpath, waittime=10):
        return WebDriverWait(self._driver, waittime).until(EC.presence_of_element_located((By.XPATH, waitxpath)))
    
    def load(self, url, waitxpath, waittime=10):
        self._driver.get(url)
        try:
            self.wait(waitxpath, waittime=waittime)
        except TimeoutException:
            self._logger.info(f"Failed to fully load {url} within {waittime}s")
            return False
        return True

    def find(self, xpath):
        return self._driver.find_element_by_xpath(xpath)
    
    def findAll(self, xpath):
        return self._driver.find_elements_by_xpath(xpath)
    
    def scrollTo(self, xpath, click=False):
        element = self.find(xpath)
        self._driver.execute_script("arguments[0].scrollIntoView();", element)
        if click:
            element.click()
    
    def isPresent(self, xpath):
        try:
            return self.find(xpath)
        except NoSuchElementException:
            return False
    
    def populate(self):
        return True
    
    def capture(self, filename, xpath="html"):
        return self.find(xpath).screenshot(filename)

    def quit():
        return self._driver.quit()

    def driver(self):
        return self._driver

    def proceed(self):
        return True

class Filter(object):
    def __init__(self, home, restrictions):
        self.home = home
        self.restrictions = restrictions
        self.geolocator = Nominatim(user_agent='farquaad-cli')
        self.truehome = self.geolocator.geocode(self.home)
        self.latlong = (self.truehome.latitude, self.truehome.longitude)
        self.store_name_to_distance = {}

    def apply(self, locations):
        # 1. filter out the locations with no availability
        # 2. filter out the locations by restricted city
        # 3. filter out the locations by restricted zip
        # for each available location
        #   4. calculate the distance to home
        #   5. filter out the location if greater than the restricted distance
        #   6. store in the result list
        # return the result list

        results = []
        for loc in locations:
            if self.restrictions.cities is not None and loc["city"] not in self.restrictions.cities:
                continue
            if self.restrictions.zipcodes is not None and loc["zip"] not in self.restrictions.zip:
                continue
            distance = None
            if loc["name"] in self.store_name_to_distance:
                distance = self.store_name_to_distance[loc["name"]]
            else:
                latlong = (loc['latitude'], loc['longitude'])
                if any(l is None for l in latlong):
                    geoloc = self.geolocator.geocode(', '.join(loc[key] for key in ['street', 'city', 'state', 'zip']))
                    if geoloc is None:
                        geoloc = self.geolocator.geocode(loc['zip'])
                    latlong = (geoloc.latitude, geoloc.longitude)
                distance = geodesic(self.latlong, latlong)
                self.store_name_to_distance[loc['name']] = distance
            loc["distance"] = distance.miles
            if self.restrictions is not None and distance.miles > self.restrictions.distance:
                continue
            results.append(loc)
            
        return results