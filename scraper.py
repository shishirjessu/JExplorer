#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import os
import urllib2
import sqlite3
import func
import bs4
from bs4 import BeautifulSoup



def main():
    create_tables()
    current_directory = func.make_new_dir()
    os.chdir(current_directory)  # change the current directory to game_files
    # process_games()


# f = open("game_1", "r")
# parser = BeautifulSoup(f.read(), 'html.parser')
# round = str(parser.find(id = "jeopardy_round"))
# roundParser = BeautifulSoup(round, 'html.parser')
# print roundParser.prettify()


def create_tables():
    db = sqlite3.connect("jeopardy.db")
    cur = db.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS airdates (
                   game_id INTEGER,
                   date TEXT
                )""")
    # make round text or integer?;
    cur.execute("""CREATE TABLE IF NOT EXISTS clues(
                       game_id INTEGER,
                       date TEXT,
                       round INTEGER,
                       category TEXT,
                       value REAL,
                       clue TEXT,
                       daily_double INTEGER,
                       answer TEXT
                    )""")
    db.commit()
    cur.close()
    db.close()
    print "done"


def process_games():
    print "x"

def process_round():
    print "x"


if __name__ == '__main__':
    main()