#!/usr/bin/env python3

import sys, getopt
import os.path
from datetime import datetime
from pathlib import Path

import settings
import pyBlitz
import scrape_schedule

def CurrentStatsFile(filename):
    if (not os.path.exists(filename)):
        return False
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if stat_date.date() < datetime.now().date():
        return False
    return True

def RefreshStats():
    import scrape_abbreviations
    import scrape_bettingtalk
    import scrape_bornpowerindex
    import scrape_teamrankings
    now = datetime.now()
    year = int(now.year)
    scrape_schedule.year = year
    scrape_schedule.main(sys.argv[1:])
    import merge_abbreviation
    import merge_schedule
    import merge_stats
    import combine_merge
    import combine_stats
    import measure_results

def main(argv):
    first = ""
    second = ""
    verbose = False
    neutral = False
    test = False
    try:
        opts, args = getopt.getopt(argv, "hf:s:vnt", ["help", "first=", "second=", "verbose", "neutral","test"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--neutral"):
            neutral = True
        elif o in ("-t", "--test"):
            test = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit
        elif o in ("-f", "--first"):
            first = a
        elif o in ("-s", "--second"):
            second = a
        else:
            assert False, "unhandled option"
    print ("Score Matchup Tool")
    print ("**************************")
    if (verbose):
        usage()
        print ("**************************")
    if (test):
        testResult = pyBlitz.Test(verbose)
        if (testResult):
            print ("Test result - pass")
        else:
            print ("Test result - fail")
    else:
        if (not first and not second):
            print ("you must input the team names to run this tool, (first and second arguments)")
            exit()

        Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
        stat_file = "{0}stats.json".format(settings.data_path)
        if (not CurrentStatsFile(stat_file)):
            RefreshStats()
        ds = {}
        ds = pyBlitz.Calculate(first, second, neutral, verbose)
        if (neutral):
            print ("{0} {1} vs {2} {3} {4}-{5}".format(ds["teama"], ds["chancea"], ds["teamb"], ds["chanceb"],
                ds["scorea"], ds["scoreb"]))
        else:
            print ("{0} {1} at {2} {3} {4}-{5}".format(ds["teama"], ds["chancea"], ds["teamb"], ds["chanceb"],
                ds["scorea"], ds["scoreb"]))

def usage():
    usage = """
    -h --help                 Prints this
    -v --verbose              Increases the information level
    -f --first                First Team  (The Away Team)
    -s --second               Second Team (The Home Team)
    -n --neutral              Playing on a neutral Field
    -t --test                 runs test routine to check calculations
    """
    print (usage) 

if __name__ == "__main__":
  main(sys.argv[1:])
