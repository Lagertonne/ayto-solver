import json
import argparse
import pprint
import collections

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description="Try to solve Are you the one")
parser.add_argument("file", help="The file where the relevant data stored")

args = parser.parse_args()


def sanitize_data(data):
    # Sort lists of men and women
    data["men"] = sorted(data["men"])
    data["women"] = sorted(data["women"])

    # Sort matching nights by women
    for matching_night in data["matching_nights"]:
        mn_id = matching_night["id"]
        data["matching_nights"][mn_id]["pairs"] = dict(sorted(matching_night["pairs"].items()))

def check_matching_nights(data):
    for matching_night in data["matching_nights"]:
        if not (data["women"] == list(sorted(data["matching_nights"][0]["pairs"].keys()))):
           print("Matching night does not match.")
           return False

        if not (data["men"] == list(sorted(data["matching_nights"][0]["pairs"].values()))):
           print("Matching night does not match.")
           return False
    return True


with open(args.file) as json_file:
    data = json.load(json_file)

sanitize_data(data)
if check_matching_nights(data):
    print("Matching nights seem legit")
else:
    print("There is something wrong with the matching nights.")
    exit(1)

# Steps to solve the riddle:
# 1. From every matching night, remove the matches we already know from truth booths
# 2. If number of matches in matching night matches the remaining matches: Add to final list
# 3. All other matches from this night: Mark as false. 
# 4. Remove all false matches from every matching night
# Jump to 1.
