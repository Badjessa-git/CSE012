# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 19:30:36 2016

@author: Romeo
"""

import earthquakes


all_quakes = earthquakes.get("magnitude")
in_hour = 0
for quake in all_quakes:
    in_hour = in_hour + 1
in_year = (in_hour * 24) * 365
print(in_year)
