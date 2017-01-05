#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import os
import urllib2
import time
import sqlite3

BASE_URL = "http://www.j-archive.com/showgame.php?game_id="
BREAK = 0.1  # wait a bit between requests, so as not to overload server
sqlite_file = "jeopardy.db"
db = sqlite3.connect(sqlite_file)
cur = db.cursor()


def main():
    current_directory = make_new_dir()
    os.chdir(current_directory)
    start = pick_start()  # which game do we start from?

    start = download_games(start)
    cur.execute("INSERT INTO start (start_index) VALUES(?)", (start,))  # insert new start
    db.commit()


# creates the sqlite database, and a table inside the table for the start point
def pick_start():
    # create and store in table
    cur.execute('CREATE TABLE IF NOT EXISTS start(start_index INTEGER)')
    cur.execute('SELECT * FROM start')
    recent = cur.fetchall()

    if len(recent) == 0:
        cur.execute('INSERT INTO start VALUES(1)')
        db.commit()
        return 1
    else:
        data = recent[len(recent) - 1]
        return data[0]


# Creates folder in which the Jeopardy HTML files will be stored
def make_new_dir():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    new_dir = os.path.join(current_directory, "game_files")
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    else:
        print "Path already exists"
    return new_dir


# loops through all the existing games and downloads them
def download_games(start_id):
    current_id = start_id
    done = False  # set to true when we run out of games
    while not done:
        current_url = BASE_URL + str(current_id)
        content = urllib2.urlopen(current_url)
        html = content.read()
        if "ERROR: No game" in html:
            done = True  # we have reached the last existing game
        else:
            save_game(current_id, html)
            current_id += 1
            print(current_id)
            time.sleep(BREAK)

    return current_id  # the last game ID for which a game existed


# saves a single game to the game_files directory
def save_game(game_id, html):
    file_name = "game_" + str(game_id)
    try:
        f = open(file_name, "w+")
        f.write(html)
    except IOError:
        print "Could not write file"


if __name__ == '__main__':
    main()
