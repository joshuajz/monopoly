import multiprocessing
import helpers
from classes import session_id, stats
from cs50 import SQL


def roll():
    x = helpers.diceRoll()
    print(x)
    print("temp")


def main(n, user_id):
    global num
    num = n


main(10, 15)


db = SQL("sqlite:///database.db")

session_id = session_id(db)

stats = stats(db, session_id.id)

if __name__ == "__main__":
    while num > 0:
        p = multiprocessing.Process(target=roll)
        p.start()
        num -= 1

