'''
    Author:
    Day 15 Classwork - Problem #4

    Use the weather.get_report() block to check whether it is
    snowing, raining or clear in:
        Seattle
        Miami
        New York
        Blacksburg
    Use the same logic as the problem #3.
    As the new block also gives us a dictionary you may be able to reuse
    some of the code too.
    For your final submission, the code should be checking for the weather
    in New York only and printing the appropriate status message.
'''

import weather

temperature = 0
humidity = 0

current_weather = weather.get_report("Miami")
current_weather2 = weather.get_report("Seattle")
current_weather3 = weather.get_report("Blacksburg")
current_weather4 = weather.get_report("New York")
for forecast in current_weather:
    if temperature < 32 and humidity >= humidity / 2:
        forecast = "snowing"
    elif temperature > 32 and humidity >= humidity / 2:
        forecast = "raining" 
    else:
        forecast = "clear"

for forecast2 in current_weather2:
    if temperature < 32 and humidity >= humidity / 2:
        forecast2 = "snowing"
    elif temperature > 32 and humidity >= humidity / 2:
        forecast2 = "raining" 
    else:
        forecast2 = "clear"

for forecast3 in current_weather3:
    if temperature < 32 and humidity >= humidity / 2:
        forecast3 = "snowing"
    elif temperature > 32 and humidity >= humidity / 2:
        forecast3 = "raining" 
    else:
        forecast3 = "clear"        

for forecast4 in current_weather4:
    if temperature < 32 and humidity >= humidity / 2:
        forecast4 = "snowing"
    elif temperature > 32 and humidity >= humidity / 2:
        forecast4 = "raining" 
    else:
        forecast4 = "clear"

print(forecast4)



