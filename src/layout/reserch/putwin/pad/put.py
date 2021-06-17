#!/usr/bin/env python3
# coding: utf8
import curses
def init(scr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_GREEN)
    pad = curses.newpad(curses.LINES*3, curses.COLS*3)
    pad.bkgd(' ', curses.A_REVERSE | curses.color_pair(1))
    pad.addstr(pad.__class__.__name__, curses.color_pair(1))
    pad.refresh(0,0,0,0,curses.LINES-1,curses.COLS-1)
    with open('putwin.txt', 'bw') as f:
        pad.putwin(f)
    pad.keypad(True)
    pad.getkey()
curses.wrapper(init)

