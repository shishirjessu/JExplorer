#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import os


# Creates and returns folder in which the Jeopardy HTML files will be stored
def make_new_dir():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    new_dir = os.path.join(current_directory, "game_files")
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    return new_dir
