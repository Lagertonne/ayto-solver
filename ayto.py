import json
import argparse
import pprint
import collections
from termcolor import colored

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description="Try to solve Are you the one")
parser.add_argument("file", help="The file where the relevant data stored")

args = parser.parse_args()

pairs = {}

# Order alphabetically blabla
def sanitize_data(data):
    # Sort lists of men and women
    data["men"] = sorted(data["men"])
    data["women"] = sorted(data["women"])

    # Sort matching nights by women
    for matching_night in data["matching_nights"]:
        mn_id = matching_night["id"]
        data["matching_nights"][mn_id]["pairs"] = dict(sorted(matching_night["pairs"].items()))

    return data

# Writes the matches known from the truth booths
def parse_truth_booths(data):
    for woman,man in data["truth_booth"]["true"].items():
        set_pair_true(data, woman, man)
    
    for woman,man in data["truth_booth"]["false"].items():
        set_pair_false(data, woman, man)

def set_pair_true(data, woman, man):
    pairs[woman][man] = True
    
    # Set all that are no-match to False
    for man_2 in data["men"]:
        if man_2 != man:
            set_pair_false(data, woman, man_2)
    
    # Set the man for all womans to false
    for woman_2 in data["women"]:
        if woman_2 != woman:
            set_pair_false(data, woman_2, man)

def set_pair_false(data, woman, man):
    pairs[woman][man] = False


# Remove the already known matches from every matching night.
# Returns a new data-object
def remove_already_known_from_mn(data):
    for matching_night in data["matching_nights"]:
        mn_id = matching_night["id"]
        # Python cannot delete from dict while iterating over it, so we need to split this up
        to_delete_true = []
        to_delete_false = []
        for woman,man in matching_night["pairs"].items():
            if pairs[woman][man] is True:
                to_delete_true.append(woman)
            if pairs[woman][man] is False:
                to_delete_false.append(woman)
        for del_woman in to_delete_true:
            #print("Delete " + del_woman + " from MN " + str(mn_id) + " cause MATCH")
            del data["matching_nights"][mn_id]["pairs"][del_woman]
            data["matching_nights"][mn_id]["matches"] = matching_night["matches"] - 1

        for del_woman in to_delete_false:
            #print("Delete " + del_woman + " from MN " + str(mn_id) + " cause NO MATCH")
            del data["matching_nights"][mn_id]["pairs"][del_woman]
    return data

# Parse Matching-Nights for blackouts or "constructed" blackouts
def get_relevant_from_mn(data):
    for matching_night in data["matching_nights"]:
        mn_id = matching_night["id"]
        if matching_night["matches"] == 0:
            #print(str(mn_id) + " is a blackout. Writing information to pairs...")
            for woman,man in matching_night["pairs"].items():
                set_pair_false(data, woman, man)

        if matching_night["matches"] == len(matching_night["pairs"]):
            #print(str(mn_id) + " has only matches remaining...")
            for woman,man in matching_night["pairs"].items():
                #print("Setting " + woman + " + " + man + " to true")
                set_pair_true(data, woman, man)

def get_relevant_from_pairs(data):
    for woman in pairs:
        none_counter = 0
        none_man = None
        for man in pairs[woman]:
            if pairs[woman][man] is None:
                none_counter = none_counter + 1
                none_man = man
            if pairs[woman][man] is True:
                continue 

        if none_counter == 1:
            print("Found " + woman + " and " + none_man)
            set_pair_true(data, woman, none_man)

def print_pairs():
    for woman in pairs:
        print(woman + ": ")
        for man in pairs[woman]:
            if pairs[woman][man] is None:
                print(colored("  " + man, 'yellow'))
            if pairs[woman][man] is True:
                print(colored("  " + man, 'green'))
            #if pairs[woman][man] is False:
            #    print(colored("  " + man, 'red'))

def print_matching_night(data, mn_id):
    matching_night = data["matching_nights"][mn_id]
    mn_id = matching_night["id"]
    print(colored("==== Matching Night " + str(mn_id) + " ====", 'green'))
    print("------------------")
    print("Pending Pairs: " + str(len(matching_night["pairs"])))
    print("------------------")
    print("Pending Matches: " + str(matching_night["matches"]))
    print("------------------")
    for woman,man in matching_night["pairs"].items():
        print(woman + " + " + man)
    print("")
    print("")

def print_matching_nights(data):
    for matching_night in data["matching_nights"]:
        mn_id = matching_night["id"]
        print(colored("==== Matching Night " + str(mn_id) + " ====", 'green'))
        print("------------------")
        print("Pending Pairs: " + str(len(matching_night["pairs"])))
        print("------------------")
        print("Pending Matches: " + str(matching_night["matches"]))
        print("------------------")
        for woman,man in matching_night["pairs"].items():
            print(woman + " + " + man)
        print("")
        print("")


with open(args.file) as json_file:
    data = json.load(json_file)

data = sanitize_data(data)

# Create a big 2d-matrix
for woman in data["women"]:
    pairs[woman] = {}
    for man in data["men"]:
        pairs[woman][man] = None

parse_truth_booths(data)
for i in range(1,10):
    print("Iteration: " + str(i))
    data = remove_already_known_from_mn(data)
    get_relevant_from_mn(data)
    get_relevant_from_pairs(data)
    print_matching_nights(data)
    print_pairs()


# Steps to solve the riddle:
# 1. From every matching night, remove the matches we already know from truth booths
# 2. If number of matches in matching night matches the remaining matches: Add to pairs-dict
# 3. If number of matching in matching night is 0: Add to pairs-dict
# 3. All other matches from this night: Mark as false. 
# 4. Remove all false matches from every matching night
# Jump to 1.
