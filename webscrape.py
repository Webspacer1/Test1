#!/usr/bin/python3

from bs4 import BeautifulSoup  
import configparser
import csv
import datetime
import re
import requests
import sqlite3
import sys
import time

from balloon import *
from telemetry import *

config = configparser.ConfigParser()
config.read('balloon.ini')
balloons = config['main']['balloons']
filter_only_spots_newer = config['main']['filter_only_spots_newer']

balloons = json.loads(config.get('main','balloons'))

print("Tracking these minutes:")
for b in balloons:
      print(b)
# print("Tracking these balloons:\n",type(balloons))

# sys.exit(0)

def getspots (nrspots):
#    print("Fetching...")
    wiki = "http://wsprnet.org/olddb?mode=html&band=all&limit=" + str(nrspots) + "&findcall=&findreporter=&sort=spotnum"
    try:
        page = requests.get(wiki)
    except requests.exceptions.RequestException as e:
        print("ERROR",e)
        return []

#    print(page.status)
#    print(page.data)

    soup = BeautifulSoup(page.content, 'html.parser')
    
    data = []

    try:
        table = soup.find_all('table')[2]
        # print("TABLE:",table)

        rows = table.findAll('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele]) # Get rid of empty values

    except IndexError as e:
        print("ERROR",e)

    # Strip empty rows
    newspots = [ele for ele in data if ele] 

    # Strip redundant columns Watt & miles and translate/filter data
    for row in newspots:
        row[0] = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M')
        row[6] = int(row[6].replace('+',''))

        del row[10]
        del row[11]
        del row[7]
        

    # Reverse the sorting order of time to get new spots firsts
    newspots.reverse()

    return newspots


# 
# Dump new spots to db. Note stripping of redundant fields
#
# 2018-05-28 05:50,OM1AI,7.040137,-15,0,JN88,+23,DA5UDI,JO30qj,724
# write datas of the telemetry slot in the database which where reported minimum twice
def dumpnewdb(spotlist):
    con = None
    data = None
    length = 0
    spotlist_db = spotlist

    # compare if new spots reported twice and delete duplicates
    spotlist_db = count_and_delete(spotlist_db)
    
    try:
        # filter out Grids which are longer than 4 digits, that are probably ghost reports
        for grid in spotlist_db:
            #print("SPOTLIST_DB", grid)
            length = len(grid[3])
            print("LENGTH GRID:", length)

        if length == 4:
            con = sqlite3.connect('wsprdb.db')
            cur = con.cursor()
            cur.execute('create table if not exists newspots(unixtime timestamp, last_seen varchar(20), frequency integer, timestamp integer, slot varchar(10), alt integer)')
            cur.execute('create table if not exists counter(unixtime_counter timestamp, frequency_counter integer, timestamp_counter integer, slot_counter varchar(10))')

            for row in spotlist_db:
                # Calculate the altitude out of the callsign
                call_to_altitude = row[1]
                altitude = decode_altitude(call_to_altitude)
                # Slicing
                first_digit = row[1]
                first_digit = first_digit[0:1]
                second_digit = row[1]
                second_digit = second_digit[2:3]
                #print("first_digit:", first_digit, second_digit)
                digits_timeslot = first_digit+"x"+second_digit
                #print("digits_timeslot:", digits_timeslot)
    
                # convert datetime to unixtime
                datetime_counter = row[0]
                datetime_counter = time.mktime(datetime_counter.timetuple())
                #print(datetime_counter)

                row_newspots = [int(time.time()), row[0], row[2], row[0].minute % 10, digits_timeslot, altitude]
                print("Send Datas to Newspots DB:", row_newspots)
                row_counter = [datetime_counter, row[2], row[0].minute % 10, digits_timeslot]
                print("Send Datas to Counter DB:", row_counter)
                cur.execute("INSERT INTO newspots VALUES(?,?,?,?,?,?)", (row_newspots))
                cur.execute("INSERT INTO counter VALUES(?,?,?,?)", (row_counter))
                data = cur.fetchall()

            # delete the oldest db duplicates:
            cur.execute("DELETE FROM newspots WHERE EXISTS (SELECT * FROM newspots p2 WHERE newspots.timestamp = p2.timestamp AND newspots.slot = p2.slot AND newspots.rowid < p2.rowid)")
            # delete db duplicates:
            cur.execute("DELETE FROM counter WHERE rowid NOT IN (SELECT min(rowid) FROM counter GROUP BY unixtime_counter,frequency_counter,timestamp_counter,slot_counter)")

            if not data:
                con.commit()
    except sqlite3.Error as e:
        print("Database error: %s" % e)
    except Exception as e:
        print("Exception in _query: %s" % e)
    finally:
        if con:
            con.close()

    return

# write datas of the telemetry slot in the database which where reported only once
def dumpnewdb_one_report(spotlist):
    con_one_report = None
    data_one_report = None
    length = 0
    spotlist_db_one_report = spotlist

    # check if we have an timeslot with only one single report
    length_one_report = len(spotlist_db_one_report)
    
    try:
        if length_one_report == 1:
            # filter out Grids which are longer than 4 digits, that are probably ghost reports
            for grid_one_report in spotlist_db_one_report:
                #print("SPOTLIST_DB", grid_one_report)
                length_one_report = len(grid_one_report[3])
                print("LENGTH ONE REPORT GRID:", length_one_report)

            if length_one_report == 4:
                con_one_report = sqlite3.connect('wsprdb_one_report.db')
                cur_one_report = con_one_report.cursor()
                cur_one_report.execute('create table if not exists newspots_one_report(unixtime timestamp, last_seen varchar(20), frequency integer, timestamp integer, slot varchar(10), alt integer)')
                cur_one_report.execute('create table if not exists counter_one_report(unixtime_counter timestamp, frequency_counter integer, timestamp_counter integer, slot_counter varchar(10))')

                for row_one_report in spotlist_db_one_report:
                    # Calculate the altitude out of the callsign
                    call_to_altitude_one_report = row_one_report[1]
                    altitude_one_report = decode_altitude(call_to_altitude_one_report)
                    # Slicing
                    first_digit = row_one_report[1]
                    first_digit = first_digit[0:1]
                    second_digit = row_one_report[1]
                    second_digit = second_digit[2:3]
                    #print("first_digit:", first_digit, second_digit)
                    digits_timeslot_one_report = first_digit+"x"+second_digit
                    #print("digits_timeslot:", digits_timeslot)
    
                    # convert datetime to unixtime
                    datetime_counter_one_report = row_one_report[0]
                    datetime_counter_one_report = time.mktime(datetime_counter_one_report.timetuple())
                    #print(datetime_counter_one_report)

                    row_newspots_one_report = [int(time.time()), row_one_report[0], row_one_report[2], row_one_report[0].minute % 10, digits_timeslot_one_report, altitude_one_report]
                    print("Send Datas to Newspots DB one Report:", row_newspots_one_report)
                    row_counter_one_report = [datetime_counter_one_report, row_one_report[2], row_one_report[0].minute % 10, digits_timeslot_one_report]
                    print("Send Datas to Counter DB one Report:", row_counter_one_report)
                    cur_one_report.execute("INSERT INTO newspots_one_report VALUES(?,?,?,?,?,?)", (row_newspots_one_report))
                    cur_one_report.execute("INSERT INTO counter_one_report VALUES(?,?,?,?)", (row_counter_one_report))
                    data_one_report = cur_one_report.fetchall()

                # delete the oldest db duplicates:
                cur_one_report.execute("DELETE FROM newspots_one_report WHERE EXISTS (SELECT * FROM newspots_one_report p2 WHERE newspots_one_report.timestamp = p2.timestamp AND newspots_one_report.slot = p2.slot AND newspots_one_report.rowid < p2.rowid)")
                # delete db duplicates:
                cur_one_report.execute("DELETE FROM counter_one_report WHERE rowid NOT IN (SELECT min(rowid) FROM counter_one_report GROUP BY unixtime_counter,frequency_counter,timestamp_counter,slot_counter)")

                if not data_one_report:
                    con_one_report.commit()
    except sqlite3.Error as e:
        print("Database error: %s" % e)
    except Exception as e:
        print("Exception in _query: %s" % e)
    finally:
        if con_one_report:
            con_one_report.close()

    return

# Fitler out only calls from balloons and telemetrypackets
def balloonfilter(spots,balloons):
    filtered = []
    telemetry = []

    for b in balloons:
        telemetry.append(b[1])

    for row in spots:

        for t in telemetry:
            # filter out the single minute digit of the spotted packet
            minute_var = row[0].minute % 10
            # we need to compare two list elements, so lets convert this two elements in list elements
            minute_var_list = [int(x) for x in str(minute_var)]
            minute_s_list = [int(y) for y in str(t)]
            # if timeslot (minute) from balloon.ini is the same as spotted minutes
            if minute_s_list == minute_var_list:
                if re.match('(^0|^1|^Q).[0-9].*', row[1]):
                    # Coarse bogus filter - just save 30m, 20m, 15m and 10m
                    if re.match('10\..*', row[2]) or re.match('14\..*', row[2]) or re.match('21\..*', row[2]) or re.match('28\..*', row[2]):
                        #               print("Found", row)
                        filtered.append(row)

    return filtered

# 2018-05-28 05:50,OM1AI,7.040137,-15,0,JN88,+23,DA5UDI,JO30qj,724
def deduplicate(spotlist):
    pre=len(spotlist)
    
    rc = 0
    rc_max = len(spotlist)-1
    if rc_max > 1:
        while rc < rc_max:
            #print("R:",rc, rc_max, len(spotlist))
            #print("SPOTLIST RC", spotlist[rc])
            #print("SPOTLIST RC +1", spotlist[rc+1])
            if (spotlist[rc][0] == spotlist[rc+1][0]) and (spotlist[rc][1] == spotlist[rc+1][1]):
#                print("Duplicate entry")
                del spotlist[rc]
                rc_max -= 1
            else:
                rc += 1
                
    return spotlist


# compare if new spots reported twice and delete duplicates
def count_and_delete(spotlist_db):
    # accept only spots which are reported minimum twice
    duplicates = list()
    seen = set()
    for i in spotlist_db:
        frozen = tuple(i)
        if frozen in seen:
            duplicates.append(i)
        else:
            seen.add(frozen)
#            return duplicates

    # delete unique spots
    spotlist_db = list(set(tuple(x) for x in duplicates))

    return spotlist_db




spots = []

# Read active balloons from db
# balloons = readballoonsdb()

# Spots to pull from wsprnet
nrspots_pull= 2000
spotcache = []

print("Preloading cache from wsprnet...")
#spotcache = getspots(10000)
spotcache = getspots(3000)
print("Fspots1",len(spotcache))
spotcache = balloonfilter(spotcache ,balloons)
print("Fspots2",len(spotcache))

spots = spotcache
cache_max = 10000
new_max = 0
only_balloon=False
#sleeptime = 75
sleeptime = 100

print("Entering pollingloop.")
while 1==1:
    tnow = datetime.datetime.now() 

    wwwspots = getspots(nrspots_pull)
    wwwspots = balloonfilter(wwwspots ,balloons)
    newspots = [] 
    newspots_spots = []
    # 
    # wwwspots.reverse()

#    for q in spotcache:
#        print("cache:",q)

    # Sort in case some spots arrived out of order
    
    spotcache.sort(reverse=False)   
    spotcache = timetrim(spotcache,120)

    src_cc = 0 

    # Loop trough cache and check for new spots
    for row in wwwspots:

        old = 0
        for srow in spotcache:
            # print("testing:",row, "\nagainst:", srow)
            src_cc += 1
            if row == srow:
                # print("Found",row)
                old = 1
                break

        if old == 0:
            print("New",row)
            # Display Altitude
            altitude_newspots = decode_altitude(row[1])
            print("Altitude:", altitude_newspots)
            
            # Insert in beginning for cache
            spotcache.insert(0, row)

 #           for w in spotcache:
 #               print("cache2:", w)

            # Add last for log
#            newspots.append(row)

            newspots_spots.append(row)


            # NEWSPOT LIST: Date, Callsign, Frequency (for the frequency we need only the first digits) and grid locator
            freq = int(float(row[2]))
            row = row[0],row[1],freq,row[5]
            newspots.append(row)

#     spotcache.sort(reverse=True)
#    print("first:",spotcache[0][0]," last: ",spotcache[-1:][0][0])
#    print("DATA:\n")
#    for row in newspots:
#        print("Newspots:",row)

#    dumpcsv(newspots)
    dumpnewdb(newspots)
    dumpnewdb_one_report(newspots)

    spots = spots + newspots_spots
    spots.sort(reverse=False)   
    spots = deduplicate(spots) # needs sorted list
#    print("DEDUPLICATED:", spots)
    # Filter out all spots newer that x minutes
    spots = timetrim(spots,int(filter_only_spots_newer))
    print(time.strftime("%Y-%m-%d %H:%M:%S"), "Filter all spots out newer than", int(filter_only_spots_newer), "minutes....")

#    if len(spots) > 1:

#        print("pre-tele:",len(spots))
#+        spots = process_telemetry(spots, balloons)
        # print("pro-tele:",len(spots))
 
#        try:
#            print("pre-tele:",len(spots))
#            spots = process_telemetry(spots, balloons)
#            # print("pro-tele:",len(spots))
#        except:
#            print("Network Error!!!")        

    if new_max < len(newspots_spots):
#  and len(newspots) != nrspots_pull:
        new_max = len(newspots_spots)

    if len(newspots_spots) == nrspots_pull:
        print("Hit max spots. Increasing set to fetch")
        nrspots_pull += 100

#    print("%s Spots: %6d New: %5d (max: %5d) Nrspots: %5d Looptime: %s Checks: %8d Hitrate: %5.2f%%" % 
#          (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(spotcache), len(newspots), new_max, nrspots_pull, str(datetime.datetime.now() - tnow).split(":")[2], src_cc, 100-(src_cc / (len(spotcache)*nrspots_pull))*100))

#+    print("%s Spots: %5d Cache: %6d New: %5d (max: %5d) Nrspots: %5d Looptime: %s Checks: %8d" % 
#+          (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(spots), len(spotcache), len(newspots), new_max, nrspots_pull, str(datetime.datetime.now() - tnow).split(":")[2], src_cc)) 

    spotcache = spotcache[:cache_max]


    sleeping = sleeptime - int(datetime.datetime.now().strftime('%S')) % sleeptime
#    print("Sleep:", sleeping)
    time.sleep(sleeping)







        
