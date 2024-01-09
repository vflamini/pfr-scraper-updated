import player_game_log as p
import team_full_game_log as pbp
import warnings
import re
import csv
import os
import pandas as pd
import math

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# Initialize an empty list to store the strings from the second column
players = []
teams = []

player_logs = [folder for folder in os.listdir('./data/player_stats') if os.path.isdir(os.path.join('./data/player_stats', folder))]
full_game_logs = [folder for folder in os.listdir('./data/games') if os.path.isdir(os.path.join('./data/games', folder))]

# Specify the path to your CSV file
csv_file_path = "qbs2023.csv"

# Open and read the CSV file
with open(csv_file_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    
    # Skip the header row if it exists
    next(reader, None)
    
    # Iterate through the rows and extract the second column (index 1)
    for row in reader:
        if len(row) >= 2:
            second_column_value = row[1]
            players.append(second_column_value)
            teams.append(pbp.team_id[row[2].lower()])

warnings.filterwarnings("ignore")

position = "QB"
season = 2023
current_season = 2023

if not(season in full_game_logs):
    mkdir(os.path.join('./data/games', str(season)))
full_game_logs = [folder for folder in os.listdir('./data/games/' + str(season))]
# any/play = (PASS_YDS + 20*PASS_TD - 45*INT + YDS_TO_CONV_GOOD*1D + RUSH_YDS + 2*YDS_TO_RUSH_TD*RUSH_TD + 2PT_CONV - (0.5/YDS_TO_CONV_BAD)*(PUNTS+TOD+MISSED_50+_YD_FG) - SACK_YDS)/(pass_att/rush_att)

### PASS_YDS, PASS_TD, INT, RUSH_YDS, RUSH_TD ###
# Player game log stat

### 1D, YDS_TO_CONV_GOOD ###
# If not no play:
#   if play is 1 down and previous play includes player's name and not (penalty and accepted):
#       get previous play's yds to convert

### YDS_TO_RUSH_TD ###
# If not no play:
# if touchdown:
#   if play includes player's name and not pass:
#       et play's yds to go

### 2PT_CONV ###
# If not no play:
#   If play includes player's name, 2 point attempt, and succeeds:
#       add to 2 pt attempts

### YDS_TO_CONV_BAD, PUNTS, TOD, MISSED_50+_YD_FG ###
# if not no play:
#   if play includes punt or field goal no good:
#       while previous play includes no play:
#           previous play -= 1 play
#       if previous play includes player's name:
#           add to punts
#           add to yds_to_conv_bad
#   if play is 4th down:
#       if play includes players name and (incomplete or grounding or 1st instance of "for yds" < yds to go):
#           add to TOD
#           add to yds_to_conv_bad

### SACK_YDS ###
# if not no play:
#   if play includes players name and sacked:
#       get 1st instance of "for yds"

idx = 0
for player in players:
    team = teams[idx]
    idx += 1
    pass_yds = 0
    pass_tds = 0
    ints = 0
    yds_to_conv_good = 0
    yds_to_conv_bad = 0
    punts = 0
    tod = 0
    missed_fg_50 = 0
    rush_yds = 0
    sack_yds = 0
    yds_to_rush_td = 0
    rush_tds = 0
    f_downs = 0
    two_pt_conv = 0
    pass_att = 0
    rush_att = 0

    # get players in player_stats folder
    if player in player_logs:
        season_logs = [folder for folder in os.listdir('./data/player_stats/' + player) if os.path.isdir(os.path.join('./data/player_stats', player, folder))]
        if (str(season) in season_logs): #and (season != current_season):
            game_log = pd.read_csv('./data/player_stats/' + player + '/' + str(season) + '/log.csv')
        else:
            mkdir(os.path.join('./data/player_stats', player, str(season)))
            game_log = p.get_player_game_log(player = player, position = position, season = season)
            game_log.to_csv(os.path.join('./data/player_stats', player, str(season), 'log.csv'))
            
    else:
        # add player folder to player_stats
        mkdir(os.path.join('./data/player_stats', player))
        mkdir(os.path.join('./data/player_stats', player, str(season)))
        # add searched season stat file
        game_log = p.get_player_game_log(player = player, position = position, season = season)
        game_log.to_csv(os.path.join('./data/player_stats', player, str(season), 'log.csv'))
            
        # if not current season:
            # add totals row
    pass_yds = sum(game_log.pass_yds)
    pass_tds = sum(game_log.pass_td)
    ints = sum(game_log.int)
    rush_yds = sum(game_log.rush_yds)
    rush_tds = sum(game_log.rush_td)
    pass_att = sum(game_log.att)
    rush_att = sum(game_log.rush_att)

    # date_str = "202310010buf"
    # fgl = pbp.get_team_full_game_log(team = team, date = date_str)
    # print(fgl)
    player = player.lower()
    for i in game_log.index:
        date_str = game_log['date'][i].replace("-", "") + "0"
        date_str += pbp.team_hrefs[pbp.team_id[game_log['opp'][i].lower()]] if game_log['game_location'][i] == "@" else pbp.team_hrefs[pbp.team_id[game_log['team'][i].lower()]]
        full_game_logs = [folder for folder in os.listdir('./data/games/' + str(season))]
        if date_str + '.csv' in full_game_logs:
            fgl = pd.read_csv('./data/games/' + str(season) + '/' + date_str + '.csv')
        else:
            fgl = pbp.get_team_full_game_log(team = team, date = date_str)
            fgl.to_csv('./data/games/' + str(season) + '/' + date_str + '.csv')
        for j in fgl.index:
            prev_count = 1
            if 'str' in str(type(fgl['detail'][j])):
                detail = fgl['detail'][j].lower()
                down = int(fgl['down'][j])
                togo = int(fgl['togo'][j])
                prev_detail = fgl['detail'][j - prev_count].lower() if j != 0 and 'str' in str(type(fgl['detail'][j - prev_count])) else ""
                prev_down = int(fgl['down'][j - prev_count]) if j != 0 else 0
                prev_togo = int(fgl['togo'][j - prev_count]) if j != 0 else 0
                while ("no play" in prev_detail or "timeout" in prev_detail or prev_detail == "") and (j - prev_count >= 0):
                    prev_detail = fgl['detail'][j - prev_count].lower() if j != 0 else ""
                    prev_down = int(fgl['down'][j - prev_count]) if j != 0 else 0
                    prev_togo = int(fgl['togo'][j - prev_count]) if j != 0 else 0
                    prev_count += 1

                if not("no play" in detail) and not("timeout" in detail) and not ("coin" in detail):
                    if down == 1 and (player in prev_detail) and not(("penalty" in prev_detail) and ("accepted" in prev_detail)):
                        yds_to_conv_good += prev_togo
                        f_downs += 1
                    if ("touchdown" in detail) and (player in detail):
                        if not("pass" in detail):
                            yds_to_rush_td += togo
                    if (player in detail) and ("2 point attempt" in detail) and ("succeeds" in detail):
                        two_pt_conv += 1
                    pattern = r'(-?\d+) yard'
                    match = re.search(pattern, detail)
                    fg_yards = -9999
                    if match:
                        yards_str = match.group(1)
                        fg_yards = int(yards_str)
                    #if (("punt" in detail) or (("field goal no good" in detail) and (fg_yards >= 45))) and down == 4 and (player in prev_detail):
                    # if (("punt" in detail) or ("field goal" in detail)) and down == 4 and (player in prev_detail):
                    if down == 4 and (player in prev_detail) and ("field goal" in detail):
                        if ("no good" in detail) and (fg_yards >= 45):
                            punts += 1
                            yds_to_conv_bad += prev_togo
                            #print("fault punt/missed 50+ FG @ " + str(fgl['quarter'][j]) + "--" + fgl['time'][j] + " on " + game_log['date'][i])
                        else:
                            punts += 0.4
                            yds_to_conv_bad += prev_togo
                    elif down == 4 and (player in prev_detail) and ("punt" in detail):
                        punts += 1
                        yds_to_conv_bad += prev_togo
                    elif down == 4:
                        pattern = r'for (-?\d+) yards'
                        match = re.search(pattern, detail)
                        yards = -9999
                        if match:
                            yards_str = match.group(1)
                            yards = int(yards_str)
                        if (player in detail) and (("incomplete" in detail) or ("grounding" in detail) or (yards < togo)):
                            tod += 10
                            yds_to_conv_bad += togo
                            #print("TOD @ " + str(fgl['quarter'][j]) + "--" + fgl['time'][j] + " on " + game_log['date'][i])
                    if (player in detail) and ("sacked" in detail):
                        pattern = r'for (-?\d+) yards'
                        match = re.search(pattern, detail)
                        yards = 0
                        if match:
                            yards_str = match.group(1)
                            yards = int(yards_str)
                        sack_yds += yards

    # any_play = (pass_yds + 20*pass_tds - 45*ints + 0.02*yds_to_conv_good*f_downs + rush_yds + 2*yds_to_rush_td*rush_tds + two_pt_conv - (50/yds_to_conv_bad)*(punts+tod+missed_fg_50) - sack_yds)/(pass_att + rush_att)
    any_play = ((pass_yds + 20*pass_tds - 45*ints + 0.5*yds_to_conv_good + rush_yds + 4*yds_to_rush_td - sack_yds)/(pass_att + rush_att)) - 5*(punts+tod+missed_fg_50)/(pass_att + rush_att + yds_to_conv_bad)
    print(player + "," + team + "," + str(any_play))
