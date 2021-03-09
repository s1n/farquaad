========
farquaad
========


Named after our incompetent governor, Greg Abbott, farquaad is designed to 
find a vaccine appointment for you. A fitting name to the worst governor
in the country.


Description
===========

There is no system in Texas to place you in a queue, this monitors known 
providers for availability and automatically schedules the first appointment 
within your specified distance.

Currently integrated providers:

- HEB

How this works is you provide details about yourself, a home location and a 
distance you're willig to travel to get the shot(s). farquaad will book your 
appointment automatically. 

Be prepared to travel to the locations within the radius you provide. The 
distance is calculated from the (center) of the home location to the 
destination via geodesic distance measure, not travel time. You can 
ball-park how far you might be willing to travel by checking Google Maps. 
For example, if you're willing to drive from downtown Austin, TX to 
San Antonio, TX, search for HEB stores in San Antonio, TX, and calculate the 
drive time and distance from (for example) 78701. So be warned, travel time 
may be longer or shorter depending on directness of route and traffic.

Note this is subject to change.

Note that some providers may be using Google's reCAPTCHA v3. For those that do,
you will need to have approximately 9 days worth of general browsing with Firefox
to bypass that system. farquaad currently only supports Firefox Selenium driver.

Search Pattern
==============
Several parameters are contribute to the search pattern restriction. That is,
potential vaccination sites are ignored if they fail to meet the search pattern
restrictions specified on the command line. Search pattern restrictions work in
combination so all of them could apply to your search if specified. For example:

-c "Austin,Round Rock" -z 78701,78681

This will restrict it's search to available slots within 50 miles of Austin or 
Round Rock and only within the zipcodes 78701 and 78681. If an appointment in 
78664 is found, it will be ignored (not present in the zipcodes restriction). 
Similarly, if an appointment in Cedar Park is found, it will also be ignored 
(not present in the cities restriction).

-d 50 -H TX,78701

This will restrict it's search to within 50 miles of home (78701). If an appointment
in San Antonio, TX is found, it will be ignored (not within the distance restriction).

Args
====

-H home
    Home location that can be identified by OpenMapQuest

-d miles
    Restriction - Distance in miles you are willing to travel.

-P file
    Patient data file. See data/form.schema.json for JSON schema validation.
    Note that this file is not currently validated against the schema.

-c city,city,...
    Restriction - List of cities to restrict your search.

-z zip,zip,...
    Restriction - List of zipcodes to restrict your search.

-v
    Info level verbosity logged

-vv
    Debug level verbosity logged

--version
    Print the current version
