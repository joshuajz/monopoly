import sqlite3
import csv


connect = sqlite3.connect("database.db")
c = connect.cursor()

with open("board.csv") as csvfile:
    reader = csv.reader(csvfile)
    x = 0
    for row in reader:
        if x == 0:
            x += 1
            continue

        row[0] = int(row[0])
        row[4] = int(row[4])
        print(row)
        c.execute(
            "INSERT INTO board VALUES (?, ?, ?, ?, ?)", row,
        )
