'''
    Author:
    Day 15 Classwork - Problem #2
    Calculating the average speed during a trip requires knowing:
        The total distance traveled and,
        The amount of time it took to cover it
    In this problem the trip data is stored in a dictionary
    with two keys:
        "distance"
        "time"
    For scientific purposes the information has been stored in
    meters and seconds.
    Reassemble the lines and complete the code to calculate the
    average speed. Some of the pieces are missing.
'''
trip_data = {"distance":123000.0, "time":14000.0}

distance_in_kilometers = trip_data["distance"]/1000

distance_miles = distance_in_kilometers / 1.6

time_in_hours = trip_data["time"]/ 3600

average_speed_in_mph = distance_miles / time_in_hours

print(average_speed_in_mph) 
