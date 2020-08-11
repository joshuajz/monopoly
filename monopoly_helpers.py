# monopoly.py
# DISCLAIMER: The cards (chance + community chest) for this game were collected from my Canadian home version
# of monopoly, I'm hoping that they're accurate.
# ✅ TODO: Store rolls information in database
# ✅ TODO: Implement sessions to the board database, maybe a new database w/ the location_id, session_id and landed
# ✅ Could be session_id, than a list of 0-39 for every location, and then the value in that cell is the amount landed
# ✅ than remove the landed value from the board database, as it's now just for the board.
# ✅ Determine the session_id at the beginning of the codebase

# 2020-08-01: Beginning of stat collection implemented, need to refractor the jail functions

# ✅ TODO: Refractor jail functions

# ✅TODO: Adding more stat collection (Amount of rolls originally, amount of extra rolls due to doubles, amount of times sent to jail due to rolling, amount of times sent to jail)
# ✅Stats: Original amount of rolls, Amount of doubles rolled, Amount of times sent to jail because of a roll (triple doubles),
# ✅Amount of times jail was visited,


# ✅TODO: Landing on the "Go To Jail" location isn't recorded
# ✅TODO: Record for how many turns they are actually in jail??

# ✅Determined not needed: TODO: Possibly?: Make the 40 divison actually a count of all of the rows, that way if people want they can make the board larger or smaller

# ✅TODO: Doubles Rules

# ✅TODO: Text file output of only important stats, + landed stats?

# ✅TODO: Convert to Canadian monopoly

# ✅TODO: Chance + Community Chest Cards
# ✅TODO: Storing drawn cards in database

# TODO: Do I want print statements to the console??
# TODO: In the main function, do I actually need to be pulling info from the database
# Commandline argument??

# TODO: Update Comments

# TODO: Visual stat drawing

# TODO: Get out of jail free card (POSSIBLE?)

# TODO: Commandline arguments to toggle certain features


import random
from sys import argv
from cs50 import SQL
import os
import datetime
from classes import store_roll, session_id, store_landed, stats, cards
import timeit

start = timeit.default_timer()


def pullclasses(stat):
    global stats
    stats = stat


def diceRoll(*args):
    # Rolls two dice, and returns both dice as well as their total

    if args == 1:
        stats = args[0]
        print(args[0])

    # Increments amount of rolls
    stats.store("roll_amount", "+ 1")

    # Roll
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    return {"d1": d1, "d2": d2, "total": d1 + d2}


def move(currentLocation, roll, boardSpaces):
    # Takes in the current location, the roll, and total amount of board spaces and moves accordingly
    # Returns the new location
    newlocation = (currentLocation + roll) % boardSpaces
    return newlocation


def j(via, mode="roll"):
    if via == "rolled":
        stats.store("jail_via_rolling", "+ 1")
    elif via == "landed":
        stats.store("jail_via_landing", "+ 1")
    elif via == "chance":
        stats.store("jail_via_chance", "+ 1")

    if mode == "roll":
        # Roll to leave jail, if needed buyout
        rolls = 0
        for i in range(3):
            roll = diceRoll()

            if roll["d1"] == roll["d2"]:
                # Success! We rolled doubles
                rolls += 1

                store_roll.store(
                    roll,
                    10 + roll["total"],
                    datetime.datetime.now(),
                    "Success - Rolled out of Jail",
                )

                stats.store("turns_in_jail", ("+ %i" % rolls))
                return {"location": 10 + roll["total"], "rolls": rolls}
            elif i == 2:
                # Failed the last roll
                rolls += 1

                store_roll.store(
                    roll,
                    10 + roll["total"],
                    datetime.datetime.now(),
                    "Failure - Buying out of Jail",
                )

                stats.store("turns_in_jail", ("+ %i" % rolls))

                return {"location": 10 + roll["total"], "rolls": rolls}
            else:
                # Failed one of the earlier rolls
                rolls += 1
                store_roll.store(
                    roll,
                    10,
                    datetime.datetime.now(),
                    "Failure - Unsuccessful roll in Jail",
                )
    else:
        # Buying out of jail
        roll = diceRoll()

        stats.store("turns_in_jail", "+ 1")

        store_roll.store(
            roll, 10 + roll["total"], datetime.datetime.now(), "Buying out of Jail"
        )
        return {"location": 10 + roll["total"], "rolls": 1}


def location_info(database, id):
    # loc_info = (db.execute("SELECT * FROM board WHERE id=:id", id=location))[0]
    return (database.execute("SELECT * FROM board WHERE id=:id", id=id))[0]


def write_stats(database):
    f = open(
        f'logs\\{session_id.id} - {datetime.datetime.now().strftime("%Y-%m-%d")}.txt',
        "w",
    )

    x = database.execute(
        "SELECT * FROM stats WHERE session_id=:session", session=session_id.id
    )[0]

    f.write(
        f"""session_id: {session_id.id}\n\nStats:\n\troll_amount: {x['roll_amount']}\n\tog_roll_amount: {x['og_roll_amount']}\n\tdoubles_rolled: {x['doubles_rolled']}\n\tjail_via_rolling: {x['jail_via_rolling']}\n\tjail_via_landing: {x['jail_via_landing']}\n\tjail_via_chance: {x['jail_via_chance']}\n\tturns_in_jail: {x['turns_in_jail']}\n\nLanded:"""
    )

    x = database.execute(
        "SELECT * FROM landed WHERE session_id=:session", session=session_id.id
    )[0]
    data = database.execute("SELECT * FROM board")

    for i in range(40):
        f.write(f"\n\t{i}. {data[i]['name']} | {x[str(i)]}")

    f.close()


stop = timeit.default_timer()
print("Time: ", stop - start)
