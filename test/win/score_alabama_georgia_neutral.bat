echo off
rem Test #4  Alabama vs. Georgia at a neutral venue
rem
.\scrape_bettingtalk.py
.\scrape_bornpowerindex.py
.\scrape_teamrankings.py
.\combine_stats.py 
.\score_matchup.py --first="alabama" --second="georgia" --neutral --verbose
