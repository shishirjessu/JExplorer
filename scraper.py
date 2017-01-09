#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import os
import sqlite3
import func
from bs4 import BeautifulSoup


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
    # make round text or integer?;
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


def process_games(cur, db):
    cur.execute('SELECT * FROM start')
    recent = cur.fetchall()

    # start and end returned as tuples, so we need to pull integer data from them
    start = recent[len(recent) - 2][0]
    end = recent[len(recent) - 1][0]

    for x in range(5430, 5431):
        file_name = "game_" + str(x)
        f = open(file_name, "r")
        parser = BeautifulSoup(f, "html.parser")

        if not is_blank_game(parser):
            # insert id/airdate info
            page_title = parser.title.text.split()
            airdate = page_title[len(page_title) - 1]
            cur.execute("INSERT INTO airdates (game_id, date) VALUES(?, ?)", (x, airdate))
            db.commit()
            # now, process each individual round
            process_round(parser, "jeopardy_round", x, cur, db)
            process_round(parser, "double_jeopardy_round", x, cur, db)
            #process_round(parser, "final_jeopardy_round", x, cur)


def process_round(parser, round_id, game_id, cur, db):
    if not parser.find(id=round_id) is None: # the game has this round
        query = "SELECT date FROM airdates WHERE game_id=" + str(game_id)
        cur.execute(query)
        airdate = cur.fetchall()[0][0]

        round = str(parser.find(id=round_id))
        roundParser = BeautifulSoup(round, 'html.parser')

        categories = []
        # create list of categories, then match up clues later
        for name in roundParser.find_all(class_="category_name"):
            categories.append(name.text)

        counter = 0
        ans_list = roundParser.find_all("div", onmouseover=True)

        for clue in roundParser.find_all(class_="clue_text"):
            # Clue id is formatted as clue_J_categoryNumber_questionNumber
            clue_text = clue.text
            location = clue['id'].split("_") # index 2 contains category
            category_index = int(location[2]) - 1
            question_index = int(location[3])
            category = categories[category_index]

            value = -1 # for final jeopardy questions, value will be stored as -1
            if round_id == "jeopardy_round": # jeopardy round
                value = question_index * 200
            elif round_id == "double_jeopardy_round":
                value = question_index * 400

            answer = ""
            temp = str(ans_list[counter])
            if "&quot;correct_response&quot;&gt;&lt;i&gt;" in temp:
                start_pt = temp.index("&quot;correct_response&quot;&gt;&lt;i&gt;") + 41
            else:
                start_pt = temp.index("&quot;correct_response&quot;&gt;") + 32
            current = start_pt
            done = False
            while not done:
                if temp[current] == "&":
                    done = True
                else:
                    answer += temp[current]
                    current += 1

            counter += 1
            cur.execute("""INSERT INTO clues(game_id, date, round, category, value, clue, answer)
                           VALUES(?, ?, ?, ?, ?, ?, ?)""",
                           (game_id, airdate, round_id, category, value, clue_text, answer))
            db.commit()


def process_final_jeopardy(parser, game_id, cur, db):
    print "x" #tbd


#  Finds the games that have not been updated with the clues so we can skip them
def is_blank_game(parser):
    return parser.find(id="jeopardy_round") is None and\
           parser.find(id="double_jeopardy_round") is None and \
           parser.find(id="final_jeopardy_round") is None

if __name__ == '__main__':
    main()
