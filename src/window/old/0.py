#!/usr/bin/env python3
# coding: utf8
import os, curses

# curses.wrapper()によって生成されたwindowを使う
class Main:
    def __init__(self, screen, msg, color_index=1):
        self.__screen = screen
        self.__msg = msg
        self.__color_index = color_index
        self.__init_cursor()
        self.__init_color_pair()
        self.__draw()
        self.__input()
    def __init_cursor(self): curses.curs_set(0)
    def __init_color_pair(self):
        if not curses.has_colors(): raise Exception('このターミナルは色を表示できません。')
        if not curses.can_change_color(): raise Exception('このターミナルは色を変更できません。')
        curses.use_default_colors()
        for i in range(1, curses.COLORS):
            curses.init_pair(i, i, curses.COLOR_BLACK)
    def __draw(self):
        try:
            for i in range(1, curses.COLORS):
                self.__screen.addstr(str(i).rjust(3), curses.A_REVERSE | curses.color_pair(i))
        except curses.ERR: pass
        self.__screen.addstr(7, 0, self.__msg, curses.A_REVERSE | curses.color_pair(self.__color_index))
    def __input(self):
        self.__screen.getkey()


if __name__ == "__main__":
    curses.wrapper(Main, 'Hello', color_index=2)

