#!/usr/bin/python3

#Load required modules
from bs4 import BeautifulSoup
import requests
import urllib.request
from lxml.html import fromstring
import re
import csv
import pandas as pd
from datetime import datetime
from statistics import mean

#ONLY CHANGE THESE VALUES
url = "http://<IP OF ECU>/index.php/realtimedata"
URL = "https://pvoutput.org/service/r1/addstatus.jsp"
APIID = "xxxxxx"
SYSTEMID = "xxxxxx"

#Basic Vars
page = requests.get(url)
soup = BeautifulSoup(page.text,features="lxml")
table = soup.find_all('table')[0]
tmp = table.find_all('tr')

# fix_rowspan
first = tmp[0]
allRows = tmp[1:-1]
headers = [header.get_text() for header in first.find_all('th')]
results = [[data.get_text() for data in row.find_all('td')] for row in allRows]
rowspan = []

for no, tr in enumerate(allRows):
    tmp = []
    for td_no, data in enumerate(tr.find_all('td')):
        if data.has_attr("rowspan"):
            rowspan.append((no, td_no, int(data["rowspan"]), data.get_text()))

if rowspan:
    for i in rowspan:
        # tr value of rowspan in present in 1th place in results
        for j in range(1, i[2]):
            #- Add value in next tr.
            results[i[0]+j].insert(i[1], i[3])

#Looping through the table
res1 = []
res3 = []
res4 = []
for result in results:
    print("Inverter ID: {}".format(result[0].replace(" ","")))
    for i in result[1].split():
        if i.isdigit():
            res1.append(int(i))
            print("(Filtered) Current Power: {}".format(i))
    print("Grid Frequency: {}".format(result[2].replace(" ","")))
    for voltage in result[3].split():
        if voltage.isdigit():
            res3.append(int(voltage))
            print("(Filtered) Voltage: {}".format(voltage))
    for temp in result[4].split():
        if temp.isdigit():
            res4.append(int(temp))
            print("(Filtered) Temp: {}".format(temp))
    datum = format(result[5]).strip().replace("\n","")
    date_time_obj = datetime. strptime(datum, '%Y-%m-%d %H:%M:%S')
    date = date_time_obj.strftime("%Y%m%d")
    time = date_time_obj.strftime("%H:%M")
    print("Date: {}".format(date))
    print("Time: {}".format(time))
    print("\n")

#Combine results
avgtemp = mean(res4)
avgvoltage = mean(res3)
totalpower = format(sum(res1))
avaragetemp = round(avgtemp)
avaragevoltage = round(avgvoltage)

#Print it!
print("Summary:")
print("Date:",date)
print("Time:",time)
print("Total power:",totalpower)
print("Avarage inverter temp:",avaragetemp)
print("Average inverter voltage:",avaragevoltage)

#Pushing to PVOUTPUT
gegevens = {'sid':SYSTEMID,'key':APIID,'d':date,'t':time,'v2':totalpower,'v5':avgtemp,'v6':avaragevoltage}
r = requests.get(URL,params=gegevens)
