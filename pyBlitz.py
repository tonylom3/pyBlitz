#!/usr/bin/env python3

import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html5lib
import pdb
from scipy.stats import norm
from collections import OrderedDict

def findTeams(first, second, dict_stats, verbose = True):
    teama = {}
    teamb = {}
    count = 0

    for item in dict_stats.values():
        if (item["Team"].lower().strip() == first.lower().strip()):
            teama = item
            count += 1
        if (item["Team"].lower().strip() == second.lower().strip()):
            teamb = item
            count += 1
        if (count == 2):
            break
    if (verbose and count < 2):
        if (not teama):
            print ("Could not find stats for {0}".format(first))
        if (not teamb):
            print ("Could not find stats for {0}".format(second))
        return {}, {}
    return teama, teamb

def GetPercent(line, dict_percent):
    return 50, 50

def Chance(teama, teamb, dict_percent, homeAdvantage = 7.897, homeTeam = 'none', verbose = True):
    EffMgn = Line(teama, teamb, verbose = False, homeTeam = homeTeam, homeAdvantage = homeAdvantage)
    if (verbose):
        print ("Chance(efficiency margin) {0}".format(EffMgn))
    aPercent, bPercent = GetPercent(EffMgn, dict_percent)
    if (verbose):
        if "none" in homeTeam:
            print ("Chance({0}) {1}%".format(teama["Team"], aPercent),
                "vs. Chance({0}) {1}%".format(teamb["Team"], bPercent))
        else:
            print ("Chance({0}) {1}%".format(teama["Team"], aPercent),
                "at Chance({0}) {1}%".format(teamb["Team"], bPercent))
    return aPercent, bPercent

def Tempo(teama, teamb, verbose = True):
    TdiffaScore = float(teama['PLpG3']) * float(teama['PTpP3'])
    TdiffaOScore = float(teama['OPLpG3']) * float(teama['OPTpP3'])
    TdiffbScore = float(teamb['PLpG3']) * float(teamb['PTpP3'])
    TdiffbOScore = float(teamb['OPLpG3']) * float(teamb['OPTpP3'])
    Tdiff = (TdiffaScore + TdiffbScore + TdiffaOScore + TdiffbOScore)/2.0
    if (verbose):
        print ("Tempo(tempo) {0}".format(Tdiff))
    return Tdiff

def Test(verbose):
    result = 0
    # Alabama, Clemson on 1/1/18 (stats from 1/7/18)
    # Actual Score: 24-6
    # venue was: Mercedes-Benz Superdome in New Orleans, Louisiana (Neutral Field "The Sugar Bowl")

    teama = {'Team':"alabama", 'Ranking':118.5, 'PLpG3':64.7, 'PTpP3':.356, 'OPLpG3':18.7, 'OPTpP3':.246, 'Result1':50, 'Result2':17}
    teamb = {'Team':"clemson", 'Ranking':113, 'PLpG3':79.3, 'PTpP3':.328, 'OPLpG3':12.3, 'OPTpP3':.199, 'Result1':50,'Result2':11}

    with open("data/bettingtalk.json") as percent_file:
        dict_percent = json.load(percent_file, object_pairs_hook=OrderedDict)

    if (verbose):
        print ("Test #1 Alabama vs Clemson on 1/1/18")
        print ("        Neutral field, Testing Chance() routine")
    chancea, chanceb =  Chance(teama, teamb, dict_percent, homeTeam = 'none', verbose = verbose)
    if (teama['Result1'] == chancea):
        result += 1
    if (teamb['Result1'] == chanceb):
        result += 1
    if (verbose and result == 2):
        print ("Test #1 - pass")
        print ("*****************************")
    if (verbose and result != 2):
        print ("Test #1 - fail")
        print ("*****************************")
    if (verbose):
        print ("Test #2 Alabama vs Clemson on 1/1/18")
        print ("        Neutral field, testing Score() routine")
    scorea, scoreb = Score(teama, teamb, verbose = verbose, homeTeam = 'none')
    if (teama['Result2'] == scorea):
        result += 1
    if (teamb['Result2'] == scoreb):
        result += 1
    if (result == 4):
        return True
    return False

def Score(teama, teamb, verbose = True, homeAdvantage = 7.897, homeTeam = 'none'):
    tempo = Tempo(teama, teamb, False)
    if (verbose):
        print ("Score(tempo) {0}".format(tempo))
    EffMgn = Line(teama, teamb, verbose = False, homeTeam = homeTeam, homeAdvantage = homeAdvantage)
    if (verbose):
        print ("Score(efficiency margin) {0}".format(EffMgn))
    aScore = round((tempo/2.0) + (EffMgn / 2.0))
    bScore = round((tempo/2.0) - (EffMgn /2.0))
    if (verbose):
        print ("Score({0}) {1}".format(teama["Team"], aScore), "vs. Score({0}) {1}".format(teamb["Team"], bScore))
    return aScore, bScore

def Line(teama, teamb, verbose = True, homeAdvantage = 7.897, homeTeam = 'none'):
    EMdiff = (float(teama['Ranking']) - float(teamb['Ranking']))
    EffMgn = 0
    if homeTeam == teama["Team"]:
        EffMgn = EMdiff + homeAdvantage
    elif homeTeam == teamb["Team"]:
        EffMgn = EMdiff - homeAdvantage
    else:
        EffMgn = EMdiff
    if (verbose):
        print ("Line(efficiency margin) {0}".format(EffMgn))
    return EffMgn

def Calculate(first, second, neutral, verbose):
    if (verbose):
        if (neutral):
            info = "{0} verses {1} at a neutral location".format(first, second)
            print (info)
        else:
            info = "Visiting team: {0} verses Home team: {1}".format(first, second)
            print (info)

    with open("data/stats.json") as stats_file:
        dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

    with open("data/bettingtalk.json") as percent_file:
        dict_percent = json.load(percent_file, object_pairs_hook=OrderedDict)

    teama, teamb = findTeams(first, second, dict_stats, verbose = verbose)
    if (not teama or not teamb):
        return {}
    if (not neutral):
        chancea, chanceb =  Chance(teama, teamb, dict_percent, homeTeam = teamb["Team"], verbose = verbose)
        scorea, scoreb = Score(teama, teamb, verbose = verbose, homeTeam = teamb["Team"])
        line = Line(teama, teamb, verbose = verbose, homeTeam = teamb["Team"])
    else:
        chancea, chanceb =  Chance(teama, teamb, dict_percent, verbose = verbose)
        scorea, scoreb = Score(teama, teamb, verbose = verbose)
        line = Line(teama, teamb, verbose = verbose)

    tempo = Tempo(teama, teamb, verbose = verbose)

    dict_score = {'teama':first, 'scorea':"{0}".format(scorea), 'chancea':"{0}%".format(chancea) ,'teamb':second, 'scoreb':"{0}".format(scoreb), 'chanceb':"{0}%".format(chanceb), 'line':int(round(line)), 'tempo':"{0}".format(int(round(tempo * 100))) }
    if (verbose):
        print ("Calculate(dict_score) {0}".format(dict_score))
    return dict_score
