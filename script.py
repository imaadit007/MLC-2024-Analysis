import os
import json
import pandas as pd

# Files
file_ids = range(1432726, 1432751)
output_file = "mlc.csv"

# List to store all deliveries
all_deliveries = []

# Process each JSON file
for file_id in file_ids:
    filename = f"{file_id}.json"
    
    if not os.path.exists(filename):
        print(f"File {filename} not found, skipping.")
        continue
    
    # Load JSON data
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract match-level details
    match_id = file_id
    season = data["info"]["season"]
    start_date = data["info"]["dates"][0]
    venue = data["info"]["venue"]
    teams = data["info"]["teams"]
    
    # Process innings and deliveries
    for innings_index, innings_data in enumerate(data["innings"]):
        batting_team = innings_data["team"]
        bowling_team = teams[1] if teams[0] == batting_team else teams[0]
        
        over_counter = 0  # This tracks the over number (0, 1, 2, ...)
        ball_counter = 1  # This tracks the ball in the over (1, 2, 3, 4, 5, 6)

        for over_index, over_data in enumerate(innings_data["overs"]):
            for delivery_index, delivery in enumerate(over_data["deliveries"]):
                # Check if the delivery is an extra (wide or no-ball)
                if "extras" in delivery:
                    if "wides" in delivery["extras"] or "noballs" in delivery["extras"]:
                        # No ball or wide: Ball number doesn't change
                        if ball_counter == 6:
                            ball_number = f"{over_counter + 1}"  # Reset to 1 after 6 balls
                        else:
                            ball_number = f"{over_counter}.{ball_counter}"
                    else:
                        # Extras but not wide/noball: Add to the ball counter
                        if ball_counter == 6:
                            ball_number = f"{over_counter + 1}"
                            over_counter += 1
                            ball_counter = 1  # Reset ball counter for new over
                        else:
                            ball_number = f"{over_counter}.{ball_counter}"
                            ball_counter += 1
                else:
                    # Normal delivery: Increment ball counter
                    if ball_counter == 6:
                        ball_number = f"{over_counter + 1}"
                        over_counter += 1
                        ball_counter = 1  # Reset ball counter for new over
                    else:
                        ball_number = f"{over_counter}.{ball_counter}"
                        ball_counter += 1

                # Extract delivery details
                striker = delivery["batter"]
                non_striker = delivery["non_striker"]
                bowler = delivery["bowler"]
                runs_off_bat = delivery["runs"]["batter"]
                extras = delivery["runs"]["extras"]
                
                # Extract extras breakdown
                wides = delivery.get("extras", {}).get("wides", 0)
                noballs = delivery.get("extras", {}).get("noballs", 0)
                byes = delivery.get("extras", {}).get("byes", 0)
                legbyes = delivery.get("extras", {}).get("legbyes", 0)
                penalty = delivery.get("extras", {}).get("penalty", 0)

                # Handle wickets
                wicket_type = None
                player_dismissed = None
                other_wicket_type = None
                other_player_dismissed = None

                if "wickets" in delivery:
                    for wicket in delivery["wickets"]:
                        wicket_type = wicket.get("kind")
                        player_dismissed = wicket.get("player_out")

                # Append data to the list
                all_deliveries.append([ 
                    match_id, season, start_date, venue, innings_index + 1,
                    ball_number, batting_team, bowling_team, striker, non_striker,
                    bowler, runs_off_bat, extras, wides, noballs, byes, legbyes,
                    penalty, wicket_type, player_dismissed, other_wicket_type, 
                    other_player_dismissed
                ])

# Create DataFrame
columns = [
    "match_id", "season", "start_date", "venue", "innings", "ball",
    "batting_team", "bowling_team", "striker", "non_striker", "bowler",
    "runs_off_bat", "extras", "wides", "noballs", "byes", "legbyes", 
    "penalty", "wicket_type", "player_dismissed", "other_wicket_type", 
    "other_player_dismissed"
]

df = pd.DataFrame(all_deliveries, columns=columns)

# Save to CSV
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"Deliveries data saved to {output_file}")
