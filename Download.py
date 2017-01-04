#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import os
import urllib2
import time
import sqlite3

BASE_URL = "http://www.j-archive.com/showgame.php?game_id="
BREAK = 1 # wait a bit between requests, so as not to overload server

def main():
    current_directory = makeNewDir()
    os.chdir(current_directory)
    start = pickStart()
    downloadGames(5493)

def pickStart():
    return 1

#Creates folder in which the Jeopardy HTML files will be stored
def makeNewDir():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    new_dir = os.path.join(current_directory, "game_files")
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    else:
        print "Path already exists"
    return new_dir


#loops through all the present games and downloads them
def downloadGames(start_id):
    current_id = start_id
    done = False # set to true when we run out of games
    while not done:
        current_url = BASE_URL + str(current_id)
        content = urllib2.urlopen(current_url)
        html = content.read()
        if "ERROR: No game" in html:
            done = True # we have reached the last existing game
        else:
            saveGame(current_id, html)
            current_id += 1
            time.sleep(BREAK)

    return current_id # the last game ID for which a game existed

# saves a single game to the game_files directory
def saveGame(game_id, html):
    current_url = BASE_URL + str(game_id)
    file_name = "game_" + str(game_id)
    try:
        file = open(file_name, "w+")
        file.write(html)
    except IOError:
        print "Could not write file"


if __name__ == '__main__':
    main()
