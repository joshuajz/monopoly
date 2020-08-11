from cs50 import SQL
import classes
import multiprocessing
import monopoly_helpers
import datetime


def setup(amount, user_id):
    # Opens the database
    global db
    db = SQL("sqlite:///database.db")

    # Session_id
    global session_id
    session_id = classes.session_id(db)

    # Roll Storing class
    global store_roll
    store_roll = classes.store_roll(db, session_id.id)

    # Location Landed Storing Class
    global store_landed
    store_landed = classes.store_landed(db, session_id.id)

    # Stat Collection
    global stats
    stats = classes.stats(db, session_id.id)

    # Cards
    global cards
    cards = classes.cards(db, session_id.id)

    # Number of rolls denoted by the user
    global num
    num = int(amount)

    # Stores the original amount of rolls
    stats.store("og_roll_amount", num)

    # Start the users at Go (id=0)
    global location
    location = 0

    # Rolls (Stores the previous 3 rolls, because of jail rules)
    global rolls
    rolls = []


def create_roll():
    # Random dice roll
    roll = monopoly_helpers.diceRoll(stats)

    # Appends to the rolls list (tracks previous 3 rolls)
    if len(rolls) < 3:
        rolls.append([roll["d1"], roll["d2"]])
    else:
        rolls.pop(0)
        rolls.append([roll["d1"], roll["d2"]])

    # Checks if they have rolled doubles, three times (If so, goto jail)
    if (
        len(rolls) == 3
        and rolls[0][0] == rolls[0][1]
        and rolls[1][0] == rolls[1][1]
        and rolls[2][0] == rolls[2][1]
    ):
        # Stores the original roll
        store_roll.store(roll, 10, datetime.datetime.now(), "3x Doubles -> Goto Jail")

        # Calls the jail function
        x = j("rolled")

        num -= x["rolls"] + 1
        location = x["location"]

        # Continues back to the beginning of the loop
        return

    # If the user has rolled doubles, they get to roll again (ie. adding an extra roll)
    if roll["d1"] == roll["d2"]:
        # Increments amount of rolls
        num += 1

        # Stores the doubles
        stats.store("doubles_rolled", "+ 1")

    # Determines the new location
    location = monopoly_helpers.move(location, roll["total"], 40)

    # "Go to Jail" via rolling
    if location == 30:
        store_roll.store(roll, 30, datetime.datetime.now(), "Landed on Jail")
        store_landed.store(30)

        x = monopoly_helpers.j("landed")
        num -= x["rolls"] + 1
        location = x["location"]
        return

    if location == 7 or location == 22 or location == 36:
        # Landed on Chance

        store_roll.store(roll, location, datetime.datetime.now(), "Chance")
        store_landed.store(location)

        location = cards.pick("Chance", location, cards, store_roll, store_landed)

        if location == 10:
            x = monopoly_helpers.j("chance")

        return

    if location == 2 or location == 17 or location == 33:
        # Landed on Community Chest

        cards.pick("Community_Chest", location, cards, store_roll, store_landed)

    # Store the roll information in the database
    store_roll.store(roll, location, datetime.datetime.now(), "N/A")

    # Update the "Landed" value in the database
    store_landed.store(location)

    # Decrements the number of rolls
    num -= 1


setup(10, 15)
# Multiprocessing Jobs
jobs = []

# Repeat for the amount of dice rolls specifided
if __name__ == "__main__":
    while num > 0:
        p = multiprocessing.Process(target=create_roll)
        jobs.append(p)
        p.start()
        num -= 1

# Write all of the stats to a log file
# write_stats(db)
