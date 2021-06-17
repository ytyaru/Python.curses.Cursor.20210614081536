#!/usr/bin/env python3
# coding: utf8
import curses
def init(scr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_GREEN)
    scr.addstr(scr.__class__.__name__, curses.color_pair(1))
    with open('putwin.txt', 'bw') as f:
        scr.putwin(f)
    scr.getkey()
curses.wrapper(init)

