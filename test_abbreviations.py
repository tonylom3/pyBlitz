#!/usr/bin/env python3

import json
import pdb
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import datetime
import re
import sys, getopt

import scrape_schedule

path = "data/"

def GetMergeAbbr(teama, teamb, dict_merge):
    abbra = ""
    abbrb = ""
    items = re.split(r'(,|\s)\s*', str(scores).lower())
    if (items[0].strip() == "?"):   # Cancelled, Postponed or not yet Played Game
        return -1, -1
    if (len(items) != 7):
        return -1, -1
    if (abbra.lower().strip() not in items):
        if (verbose):
            print ("Missing Abbreviation [{0}] [{1}] in Score {2}".format(abbra, abbrb, scores))
        return -1, -1
    if (abbrb.lower().strip() not in items):
        if (verbose):
            print ("Missing Abbreviation [{0}] [{1}] in Score {2}".format(abbra, abbrb, scores))
        return -1, -1
    if (abbra.lower().strip() == items[0].lower().strip()):
        scorea = int(items[2])
        scoreb = int(items[6])
    else:
        scorea = int(items[6])
        scoreb = int(items[2])
    return scorea, scoreb

def GetCount(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("0")
    return int(idx[0])

def GetSchedFiles(templatename):
    file_dict = {}
    for p in Path(path).glob(templatename):
        idx = GetCount(p)
        file_dict[idx] = str(p)
    file_list = []
    for idx in range(len(file_dict)):
        file_list.append(file_dict[idx + 1])
    return file_list

def FindTeams(stats_team, fixed_team, stats_teams):
    Found = False
    for team in stats_teams:
        if (team.strip() == stats_team.strip() and fixed_team.strip() == ""):
            Found = True
            break
        if (team.strip() == fixed_team.strip()):
            Found = True
            break
    return Found

print ("Test Abbreviation spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your abbreviations are set up correctly")
print ("    Tool will compare the scraped schedule abbreviations to the abbreviations")
print ("    from the combine_merge Tool")
print (" ")

file = '{0}merge.json'.format(path)
if (not os.path.exists(file)):
    print ("merge.json file is missing, run the combine_merge tool to create")
    exit()
with open(file) as merge_file:
    dict_merge = json.load(merge_file, object_pairs_hook=OrderedDict)

now = datetime.datetime.now()
year = int(now.year)
lastyear = year - 1
scrape_schedule.year = lastyear
scrape_schedule.main(sys.argv[1:])
schedule_files = GetSchedFiles("sched*.json")
if (not os.path.exists(schedule_files[0])):
    print ("schedule files are missing, run the scrape_schedule tool to create")
    exit()

list_schedule = []
for file in schedule_files:
    with open(file) as schedule_file:
        list_schedule.append(json.load(schedule_file, object_pairs_hook=OrderedDict))
scrape_schedule.year = year
scrape_schedule.main(sys.argv[1:])
pdb.set_trace()
AllAbbr=[]
for idx in range(len(schedule_files)):
    for item in list_schedule[idx].values():
        abbra, abbrb = GetMergeAbbr(item["TeamA"], item["TeamB"], dict_merge)
        AllAbbr.append(abbra)
        AllAbbr.append(abbrb)
abbr_set = set(AllAbbr)
abbr_codes = list(abbr_set)
abbr_codes.sort()
pdb.set_trace()

found = False
for team in dict_merge:
    if (team["corrected stats team"].strip()!=""):
        found = True

if (not found):
    print ("*** Warning: Have you set up your merge_schedule? There are NO fixes entered ***")
    print ("*** Make sure all of your match-ups are correct and then re-run this script ***")
    exit()

for team in dict_merge:
    found = FindTeams(team["stats team"], team["corrected stats team"], stats_teams)
    if (not found):
        print ("warning: {0} was not found in the stats table ***".format(team["scheduled team"]))
 
print ("done.")