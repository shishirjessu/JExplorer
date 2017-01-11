#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import os
import sqlite3
import func
from bs4 import BeautifulSoup
import HTMLParser


def main():
    games_directory = func.make_new_dir()
    os.chdir(games_directory)
    db = sqlite3.connect("jeopardy.db")
    cur = db.cursor()
    create_tables(cur, db)
    process_games(cur, db)


# create tables in which to insert clues and airdates
def create_tables(cur, db):
    cur.execute("""CREATE TABLE IF NOT EXISTS airdates (
                   game_id INTEGER,
                   date TEXT
                )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS clues(
                       game_id INTEGER,
                       date TEXT,
                       round TEXT,
                       category TEXT,
                       value REAL,
                       clue TEXT,
                       answer TEXT
                    )""")
    db.commit()


# processes all games that have recently been downloaded
def process_games(cur, db):
    cur.execute('SELECT * FROM start')
    recent = cur.fetchall()

    # start and end returned as tuples, so we need to pull integer data from them
    start = recent[len(recent) - 2][0]
    end = recent[len(recent) - 1][0]

    for x in range(5410, 5430):  # iterate through every file we have after downloading
        print (x)  # print current iteration
        file_name = "game_" + str(x)
        f = open(file_name, "r")
        try:
            parser = BeautifulSoup(f, "html.parser")
        except HTMLParser.HTMLParseError:
            continue

        if not is_blank_game(parser):
            # insert id/airdate info
            page_title = parser.title.text.split()
            airdate = page_title[len(page_title) - 1]
            cur.execute("INSERT INTO airdates (game_id, date) VALUES(?, ?)", (x, airdate))
            # now, process each individual round
            process_round(parser, "jeopardy_round", x, cur)
            process_round(parser, "double_jeopardy_round", x, cur)
            process_final_round(parser, x, cur)

    db.commit()

# processes the Jeopardy and Double Jeopardy rounds
def process_round(parser, round_id, game_id, cur):
    if not parser.find(id=round_id) is None:  # the game has this round
        query = "SELECT date FROM airdates WHERE game_id=" + str(game_id)
        cur.execute(query)
        airdate = cur.fetchall()[0][0]

        current_round = str(parser.find(id=round_id))
        round_parser = BeautifulSoup(current_round, 'html.parser')

        categories = []
        # create list of categories, then match up clues later
        for name in round_parser.find_all(class_="category_name"):
            categories.append(name.text)

        counter = 0
        ans_list = round_parser.find_all("div", onmouseover=True)

        for clue in round_parser.find_all(class_="clue_text"):
            # Clue id is formatted as clue_J_categoryNumber_questionNumber
            clue_text = clue.text
            location = clue['id'].split("_")  # index 2 contains category
            category_index = int(location[2]) - 1
            question_index = int(location[3])
            category = categories[category_index]

            value = 0
            if round_id == "jeopardy_round":  # jeopardy round
                value = question_index * 200
            elif round_id == "double_jeopardy_round":  # values are double in second round
                value = question_index * 400

            try:
                temp = str(ans_list[counter].get("onmouseover"))
            except UnicodeEncodeError:
                counter += 1
                continue

            soup = BeautifulSoup(temp, "html5lib")  # we need the html5lib parser to get the answer
            answer = soup.find("em", class_="correct_response").text

            counter += 1

            cur.execute("""INSERT INTO clues(game_id, date, round, category, value, clue, answer)
                           VALUES(?, ?, ?, ?, ?, ?, ?)""",
                        (game_id, airdate, round_id, category, value, clue_text, answer))


# processes the final jeopardy round, does not have to loop through clues
def process_final_round(parser, game_id, cur):
    if not parser.find(id="final_jeopardy_round") is None:  # there is a final round
        query = "SELECT date FROM airdates WHERE game_id=" + str(game_id)
        cur.execute(query)
        airdate = cur.fetchall()[0][0]

        current_round = str(parser.find(id="final_jeopardy_round"))
        round_parser = BeautifulSoup(current_round, 'html.parser')
        category = round_parser.find(class_="category_name").text

        value = -1  # we will use -1 as the value of final clues for consistency

        clue_text = round_parser.find(class_="clue_text").text

        temp = round_parser.find("div", onmouseover=True).get("onmouseover")
        try:
            soup = BeautifulSoup(str(temp), "html5lib")
        except UnicodeEncodeError:
            return

        answer = soup.find("em").text

        cur.execute("""INSERT INTO clues(game_id, date, round, category, value, clue, answer)
                                   VALUES(?, ?, ?, ?, ?, ?, ?)""",
                    (game_id, airdate, "final_jeopardy_round", category, value, clue_text, answer))


# Finds the games that have not been updated with the clues so we can skip them
def is_blank_game(parser):
    return parser.find(id="jeopardy_round") is None and\
           parser.find(id="double_jeopardy_round") is None and \
           parser.find(id="final_jeopardy_round") is None

if __name__ == '__main__':
    main()
