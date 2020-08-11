import random
import datetime


class store_roll:
    # Initalizes database + session_id
    def __init__(self, database, session_id):
        self.session_id = session_id
        self.database = database

    def store(self, roll, location_id, datetime, other):
        # Stores all of the information for the roll
        self.database.execute(
            "INSERT INTO rolls (session_id, d1, d2, dice_total, location_id, datetime, other) VALUES (?, ?, ?, ?, ?, ?, ?)",
            self.session_id,
            int(roll["d1"]),
            int(roll["d2"]),
            int(roll["total"]),
            location_id,
            datetime.strftime("%Y-%m-%d %I:%M:%S %p"),
            other,
        )


class store_landed:
    # Initalizes database + session_id + creates blank table for landed locations
    def __init__(self, database, session_id):
        self.session_id = session_id
        self.database = database

        self.database.execute(
            "INSERT INTO landed (session_id) VALUES (:session)", session=self.session_id
        )

    def store(self, location_id):
        # Determines the current amount for the location
        current = self.database.execute(
            "SELECT * FROM landed WHERE session_id=:session", session=self.session_id,
        )[0][str(location_id)]

        current += 1

        # Updates amount in the database
        self.database.execute(
            "UPDATE landed SET :id = :val WHERE session_id=:session",
            id=str(location_id),
            val=current,
            session=self.session_id,
        )


class session_id:
    # Determines the current session_id
    def __init__(self, database):
        count = database.execute("SELECT count(session_id) FROM landed")[0][
            "count(session_id)"
        ]
        if count == 0:
            self.id = 0
        else:
            self.id = count + 1


class stats:
    # Initalizes database + session_id + creates blank table for stats
    def __init__(self, database, session_id):
        self.database = database
        self.session_id = session_id

        self.database.execute(
            "INSERT INTO stats (session_id) VALUES (:session)", session=self.session_id
        )

    def store(self, stat, value):
        # Stores a stat
        # Provide "+1" into the value to increment by 1, or provide a value

        # Increment by 1
        if isinstance(value, int):
            # Sets it to the provided value
            self.database.execute(
                "UPDATE stats SET :stat = :val WHERE session_id=:session",
                stat=stat,
                val=value,
                session=self.session_id,
            )

        elif str(value).split(" ")[0] == "+":
            # determine the current amount
            addition_amnt = int(str(value).split(" ")[1])

            db = self.database.execute(
                "SELECT * FROM stats WHERE session_id=:session", session=self.session_id
            )[0]

            # Stores it + value
            self.database.execute(
                "UPDATE stats SET :stat = :val WHERE session_id=:session",
                stat=stat,
                val=db[stat] + addition_amnt,
                session=self.session_id,
            )


class cards:
    def __init__(self, database, session_id):
        self.database = database
        self.session_id = session_id

        self.pull_chance()
        self.pull_community()

        self.database.execute(
            "INSERT INTO drawn_chance (session_id) VALUES (:session)",
            session=self.session_id,
        )
        self.database.execute(
            "INSERT INTO drawn_community (session_id) VALUES (:session)",
            session=self.session_id,
        )

    def pull_chance(self):
        self.chance = self.database.execute(
            "SELECT card_number, effect FROM chance_cards"
        )

    def pull_community(self):
        self.community_chest = self.database.execute(
            "SELECT card_number, effect FROM community_cards"
        )

    def pick(self, t, current_location, cards, store_roll, store_landed):
        if t == "Chance":
            if len(self.chance) == 0:
                cards.pull_chance()

            x = random.randint(0, len(self.chance) - 1)

            card = self.chance.pop(x)

            blank_roll = {"d1": 0, "d2": 0, "total": 0}

            amnt = (
                self.database.execute(
                    "SELECT * FROM drawn_chance WHERE session_id=:session",
                    session=self.session_id,
                )[0][str(card["card_number"])]
                + 1
            )

            self.database.execute(
                "UPDATE drawn_chance SET :id = :val WHERE session_id=:session",
                id=str(card["card_number"]),
                val=amnt,
                session=self.session_id,
            )

            if card["effect"] == "Advance to Nearest Airport":
                if current_location == 7:
                    airport = 15
                elif current_location == 22:
                    airport = 25
                elif current_location == 36:
                    airport = 5

                store_roll.store(
                    blank_roll,
                    airport,
                    datetime.datetime.now(),
                    "Chance Redirect (Nearest Airport)",
                )
                store_landed.store(airport)

                # Returns new location
                return airport

            elif card["effect"] == "Advance to Chatam-Kent":
                store_roll.store(
                    blank_roll,
                    39,
                    datetime.datetime.now(),
                    "Chance Redirect (Chatam-Kent)",
                )
                store_landed.store(39)

                return 39

            elif card["effect"] == "Advance to Nearest Service Provider":
                if current_location == 7:
                    service = 12
                elif current_location == 22:
                    service = 28
                elif current_location == 36:
                    service = 12

                store_roll.store(
                    blank_roll,
                    service,
                    datetime.datetime.now(),
                    "Chance Redirect (Nearest Service)",
                )
                store_landed.store(service)
                return service
            elif card["effect"] == "Advance to St.John's International Airport":
                store_roll.store(
                    blank_roll,
                    5,
                    datetime.datetime.now(),
                    "Chance Redirect (St.John's Airport",
                )
                store_landed.store(5)
                return 5

            elif card["effect"] == "Advance to Medicine Hat":
                store_roll.store(
                    blank_roll,
                    24,
                    datetime.datetime.now(),
                    "Chance Redirect (Medicine Hat)",
                )
                store_landed.store(24)
                return 24

            elif card["effect"] == "Advance to Jail":
                store_roll.store(
                    blank_roll, 10, datetime.datetime.now(), "Chance Redirect (Jail)"
                )
                store_landed.store(10)
                return 10

            elif card["effect"] == "Advance to St.John's":
                store_roll.store(
                    blank_roll,
                    11,
                    datetime.datetime.now(),
                    "Chance Redirect (St.John's)",
                )
                store_landed.store(11)
                return 11
            else:
                store_roll.store(
                    blank_roll,
                    current_location,
                    datetime.datetime.now(),
                    "Chance had no Effect",
                )
                return current_location

        elif t == "Community_Chest":
            if len(self.community_chest) == 0:
                cards.pull_community()

            x = random.randint(0, len(self.community_chest) - 1)

            card = self.community_chest.pop(x)

            amnt = (
                self.database.execute(
                    "SELECT * FROM drawn_community WHERE session_id=:session",
                    session=self.session_id,
                )[0][str(card["card_number"])]
                + 1
            )

            self.database.execute(
                "UPDATE drawn_community SET :id = :val WHERE session_id=:session",
                id=str(card["card_number"]),
                val=amnt,
                session=self.session_id,
            )

            return current_location
