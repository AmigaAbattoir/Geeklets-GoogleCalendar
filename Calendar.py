#!/usr/bin/python
# -*- coding: utf-8 -*-

from _ast import TryExcept
import csv
import datetime
import os
import subprocess
import sys
import urllib2


START_DATE = 0
START_TIME = 1
END_DATE = 2
END_TIME = 3
TITLE = 6

#Linkage
LINK = 4
HANGOUTLIN = 5
#These fields are not always available
LOCATION = 7
DESCRIPTION = 8

NORMAL = "\033[0m"

BOLD = "\033[1m"
BOLD_OFF = "\033[22m"

ITALIC = "\033[3m"
ITALIC_OFF = "\033[23m"

DIM = "\033[2m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

def smart_truncate(content, length=100, suffix='...'):
	if len(content) <= length:
		return content
	else:
		return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

bin = "/usr/local/bin/gcalcli"

datetimeToday = datetime.date.today()
today = str(datetimeToday)
todayWithTimeStr = datetimeToday.strftime("%Y-%m-%d %H:%M:%S")

cmd = bin + " --tsv agenda --detail_description --detail_location --detail_url short '" + today + "'"

# If on a Friday, then do the entire week
if(datetimeToday.isoweekday()==5):
	week = datetime.timedelta(days=8) + datetimeToday
	cmd = cmd + " '" + str(week) + "'"

previousDay = ""
isToday = False
currentColor = NORMAL
currentTime = datetime.datetime.today()

totalDisplay = "Last update: " + currentTime.strftime("%Y-%m-%d %H:%M:%S") + "\n"

# Create the subprocess to call the calendar
proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in proc.stdout.readlines():
	data = line.strip().split('\t');
	dataLength = len(data)

#	print  str(dataLength)
#	print data

	if(dataLength>1):
		day = data[START_DATE]

		# Ignore "No title" items from other's calendars.
		if(data[TITLE]!="(No title)"):
			# Start display, if new day write it!
			if(previousDay!=day):
				if(day==today):
					display = WHITE + BOLD + "TODAY" + NORMAL + "\n"
					isToday = True
				else:
					display = NORMAL + "\n" + BOLD
					if(isToday):
						if(datetime.date.today().isoweekday()==5):
							display = display = display + "NEXT WEEK\n"
						isToday = False
					display = display + datetime.datetime.strptime(day,"%Y-%m-%d").strftime('%A') + " - " + day + NORMAL + "\n"
				previousDay = day
			else:
				display = ""

			# Display time if not all day
			if(data[START_TIME]=="00:00" and data[END_TIME]=="00:00"):
				if(isToday):
					display = display + WHITE
				else:
					display = display + NORMAL
				display = display + ITALIC + "     All day" + ITALIC_OFF + "\t\t" + data[TITLE]
			else:
				# Adjust the color for today, highlighting those that are up-coming
				if(isToday):
					format = "%Y-%m-%d %H:%M"
					startTime = datetime.datetime.strptime(data[START_DATE] + " " + data[START_TIME],format)
					endTime = datetime.datetime.strptime(data[END_DATE] + " " + data[END_TIME],format)
					if(currentTime>=startTime and currentTime<=endTime):
						display = display + GREEN
					elif((startTime - currentTime).seconds/60 < 5):
						display = display + RED
					elif((startTime - currentTime).seconds/60 < 16):
						display = display + YELLOW
					elif(currentTime < startTime):
						display = display + WHITE
					else:
						display = display + NORMAL

				display = display + data[START_TIME] + " - " + data[END_TIME] + "\t\t" + BOLD + data[TITLE] + BOLD_OFF

			# Display info if available
			if(dataLength>LOCATION):
				if(data[LOCATION]!=""):
					display = display + " " + smart_truncate(data[LOCATION],30)

			# Display description if it is available
			if(dataLength>DESCRIPTION):
				if(data[DESCRIPTION]!=""):
					desc = data[DESCRIPTION]
					desc = smart_truncate(data[DESCRIPTION], 45)
					desc = desc.replace("\\n\\n",'\n\t\t\t')
					desc = desc.replace("\\n",'')
					display = display + "\n\t\t\t\t" + DIM + ITALIC + desc + ITALIC_OFF

			#print display
			totalDisplay = totalDisplay + display + "\n"

#Write to file, so that even if this fails to connect or what not, it can be displayed as text
f = open("/tmp/Geeklet-calendar.txt","w")
f.writelines(totalDisplay)
f.close()
