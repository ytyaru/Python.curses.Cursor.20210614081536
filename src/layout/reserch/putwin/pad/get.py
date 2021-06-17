#!/usr/bin/env python3
# coding: utf8
import curses
def init(scr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_GREEN)
    with open('putwin.txt', 'br') as f:
        pad = curses.getwin(f)
        pad.refresh(0,0,0,0,curses.LINES-1,curses.COLS-1)
    pad.keypad(True)
    pad.getkey()
curses.wrapper(init)

