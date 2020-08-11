import random


def diceRoll():
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    return {"d1": d1, "d2": d2, "total": d1 + d2, "stats": '''"roll_amount", "+ 1"'''}
