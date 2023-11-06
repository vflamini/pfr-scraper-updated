import player_game_log as p
import team_full_game_log  as pbp
import warnings
import re
import csv

# Initialize an empty list to store the strings from the second column
players = []
teams = []

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
    if player in player_logs
        # player_log = df of csv file
        if season != current_season:
            # game_log = games where season = season from player csv
            # add games to player's csv
        else:
            
    else:
        # add player folder to player_stats
        # add searched season stat file
        game_log = p.get_player_game_log(player = player, position = position, season = season)
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
        fgl = pbp.get_team_full_game_log(team = team, date = date_str)
        for j in fgl.index:
            prev_count = 1
            detail = fgl['detail'][j].lower()
            down = int(fgl['down'][j])
            togo = int(fgl['togo'][j])
            prev_detail = fgl['detail'][j - prev_count].lower() if j != 0 else ""
            prev_down = int(fgl['down'][j - prev_count]) if j != 0 else 0
            prev_togo = int(fgl['togo'][j - prev_count]) if j != 0 else 0
            while ("no play" in prev_detail or "timeout" in prev_detail) and (j - prev_count >= 0):
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
                if (("punt" in detail) or (("field goal no good" in detail) and (fg_yards >= 45))) and down == 4 and (player in prev_detail):
                    punts += 1
                    yds_to_conv_bad += prev_togo
                    #print("fault punt/missed 50+ FG @ " + str(fgl['quarter'][j]) + "--" + fgl['time'][j] + " on " + game_log['date'][i])
                elif down == 4:
                    pattern = r'for (-?\d+) yards'
                    match = re.search(pattern, detail)
                    yards = -9999
                    if match:
                        yards_str = match.group(1)
                        yards = int(yards_str)
                    if (player in detail) and (("incomplete" in detail) or ("grounding" in detail) or (yards < togo)):
                        tod += 1
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

    any_play = (pass_yds + 20*pass_tds - 45*ints + 0.02*yds_to_conv_good*f_downs + rush_yds + 2*yds_to_rush_td*rush_tds + two_pt_conv - (50/yds_to_conv_bad)*(punts+tod+missed_fg_50) - sack_yds)/(pass_att + rush_att)
    print(player + "," + team + "," + str(any_play))
