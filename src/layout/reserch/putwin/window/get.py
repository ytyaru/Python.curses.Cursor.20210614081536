#!/usr/bin/env python3
# coding: utf8
import curses
def init(scr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_GREEN)
    with open('putwin.txt', 'br') as f:
        window = curses.getwin(f)
    window.getkey()
curses.wrapper(init)

