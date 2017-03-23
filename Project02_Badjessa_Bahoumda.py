# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 13:07:05 2016

@author: Romeo
"""

import sqlite3
import matplotlib.pyplot as plt 

conn = sqlite3.connect('CollegeScoreboard.db')
d= conn.cursor()

###Question 1
rows = d.execute('''select instnm, npt4_pub from Scoreboard 
                        where HBCU = 1 and control = 1 ''')
### 1. public
### 2. private nonprofit
### 3. private for profit
list_1 = []
list_2 = []

for row in rows:
    list_1.append(unicode(row[1]))
    print row

rows1 = d.execute('''select instnm, npt4_priv from scoreboard
                    where HBCU = 1  and control > 1 ''')

for row1 in rows1:
    list_2.append(unicode(row1[1]))
    print row1
    
hbcu = d.execute('''select count(instnm) from scoreboard
                    where HBCU = 1''')
for b in hbcu:
    print b

nu = d.execute('''select count(instnm) from scoreboard''')
for a in nu:
    print a

proportion_list=[]

list_3 = a + b

total= sum(list_3)
print(list_3)

for c in list_3:
    proportion_list.append((c/float(total))*100)
    
print proportion_list

plt.pie(proportion_list, labels=proportion_list, autopct='%1.1f%%', shadow=True, startangle=140)
plt.axis('equal')
plt.show()
plt.clf()

### HBCU colleges make up for 1.8% of the total colleges in the dataset

### Question 2

avg = d.execute('''select distinct instnm, SAT_AVG from scoreboard
                   where SAT_AVG group by instnm 
                   order by SAT_AVG DESC limit 200;''')
avg_list=[]

for i in avg:
    avg_list.append(int(i[1]))
    print i

avg_list.sort()

print(avg_list)

plt.hist(avg_list)
plt.title("Occurence of SAT average for top 200 schools")
plt.xlabel("SAT Average")
plt.ylabel("Occurence")
plt.show()
plt.clf()

### The SAT averages between 1000 and 1060 occurs most often and the SAT ranges between 1400 and 1500 occur less often.

### Question 3
loans = d.execute(''' select instnm, scoreboard.PCTFLOAN, SAT_AVG from scoreboard
                        where scoreboard.PCTFLOAN 
                        and SAT_AVG limit 1400;''')
list_4=[]
list_4i=[]

for x in loans:
    list_4.append(float(x[1]))
    list_4i.append(float(x[2]))
    

plt.scatter(list_4, list_4i, c='r', marker='x')
# Label Axis
plt.xlabel('Percentage loans')
plt.ylabel('SAT Average')
plt.title('Correlation betweeen percentage of Loans and SAT Averages')

# Display bar chart
plt.show()
plt.clf

