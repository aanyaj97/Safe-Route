Welcome to our CMSC 122 Project: Safe-Route. 

We created an algorthim to compute the 'safest' route to walk from one destination to another using historical crime data to evaluate the likelihood of a crime occuring at your time of travel.

In order to launch our web interface, please navigate to the "saferoutesite" folder and run the following command "python3 manage.py runserver". Then, open this link: http://127.0.0.1:8000/routemanager/ in your browser. 

The web interface allows you to enter a starting and ending address within the City of Chicago. Please follow the input examples when formatting your entries. If you would like, you may enter in a date of travel, time of travel, temperature, or precipitation level to see the best path to take in those scenarios. These fields are optional and you may enter in as many or as little as you would like.

Please note that as the algorithm runs a regression on each city block, it may take a few seconds to output a route within a neighborhood and up to a minute to output a route from one end of the city to the other. Additionally, we use a service calling 'geocoding' to retrieve longitudes and latitudes for entered addresses which can timeout with too many requests (1 per second max.) or with broken internet connection. If you get a geocoder timeout error, just refresh the page! 

Thank you! 

-Cale, Megan, Aanya, and Katarina
