import numpy as np
import matplotlib.pyplot as plt

plt.rcdefaults()

"""Sources:
https://pythonspot.com/matplotlib-bar-chart/
https://stackoverflow.com/questions/6774086/why-is-my-xlabel-cut-off-in-my-matplotlib-plot
"""

# Saves a graph as the session_id file.
def graph(values, session_id):
    locations = (
        "Go",
        "Banff",
        "Community Chest",
        "Beauceville",
        "Income Tax",
        "St. John's International Airport",
        "Vancouver",
        "Chance",
        "Toronto",
        "Ottawa",
        "Jail",
        "St.John's",
        "Cell Phone Service",
        "North Bay",
        "Kelowna",
        "Vancover International Airport",
        "Montreal",
        "Community Chest",
        "Chilliwack",
        "Kawartha Lakes",
        "Free Parking",
        "Shawinigan",
        "Chance",
        "Gatineau",
        "Medicine Hat",
        "Montreal Trudeau International Airport",
        "Trois-Rivieres",
        "Quebec City",
        "Internet Service",
        "Windsor",
        "Go To Jail",
        "Edmonton",
        "Sarnia",
        "Community Chest",
        "Calgary",
        "Toronto Pearson International Airport",
        "Chance",
        "Saint-Jean-Sur-Richelieu",
        "Luxury Tax",
        "Chatham-Kent",
    )

    y_pos = np.arange(len(locations))
    print(y_pos)
    plt.bar(
        y_pos,
        values,
        align="center",
        figure=plt.figure(figsize=(12, 10)),
        color=[
            "black",
            "brown",
            "grey",
            "brown",
            "grey",
            "aqua",
            "cyan",
            "grey",
            "cyan",
            "cyan",
            "black",
            "purple",
            "grey",
            "purple",
            "purple",
            "aqua",
            "orange",
            "grey",
            "orange",
            "orange",
            "black",
            "red",
            "grey",
            "red",
            "red",
            "aqua",
            "yellow",
            "yellow",
            "grey",
            "yellow",
            "black",
            "green",
            "green",
            "grey",
            "green",
            "aqua",
            "grey",
            "blue",
            "black",
            "blue",
        ],
    )

    # TODO: Colour the graph

    plt.xticks(y_pos, locations, rotation="vertical")
    plt.ylabel("Landed Amount")
    plt.xlabel("Location")
    plt.title("Monopoly")

    plt.tight_layout()

    plt.savefig(str(session_id) + ".png")

    # DEBUGGING: Shows the graph
    plt.show()

