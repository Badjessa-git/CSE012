'''
    Author:
    Day 15 Homework - Problem #1

    Use the weather.get_report block to anwer the following question
    about a city: Is a snowstorm happening at the moment?
    For this problem, consider that a snowstorm may be happening if:
        The temperature is lower than or equal to 32.
        Humidity is above 80.
        Wind is higher than 30.
    Use this logic to calculate whether Seattle is going through one.
    Print "Yes" if it is, print "No" if it isn't.
'''

import weather

# Using cw as shorthand for current_weather
cw = weather.get_report("Seattle")
temperature = 0
humidity = 0
wind = 0
for forecast in cw:
    if temperature <= 32 and humidity > 80 and wind > 30:
        forecast = "yes"
    else:
        forecast = "No"
print(forecast)
    
