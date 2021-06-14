#!/usr/bin/env python3
# coding: utf8
import os, curses, curses.panel

# windowにてカーソル関係のAPIを使う。
class Curses:
    Screen = None
    Windows = []
    Pads = []
    @classmethod
    def run(cls):
        curses.wrapper(Curses.__main)
    @classmethod
    def __main(cls, screen, *args, **kwargs):
        Curses.Screen = screen
        Curses.__init_cursor()
        Curses.__init_color_pair()

        Curses.__make_window()
        Curses.__make_window()
        cls.Windows[0].Pointer.clear()
#        cls.Windows[1].Pointer.clear()
        cls.Windows[0].draw(y=0, msg='Window-1', attr=curses.A_REVERSE | curses.color_pair(1))
        cls.Windows[1].draw(y=1, msg='Window-2', attr=curses.A_REVERSE | curses.color_pair(2))
#        cls.Windows[1].switch()
#        cls.Windows[0].hide()
#        cls.Windows[1].hide()
#        cls.Windows[1].show()
#        cls.Windows[0].Panel.hide()
#        cls.Windows[1].Panel.hide()
        curses.panel.update_panels()

#        Curses.__draw()
        Curses.__input()
    @classmethod
    def __make_window(cls, x=0, y=0, w=-1, h=-1):
        cls.Windows.append(Window(Curses.Screen, x, y, w, h))
        return cls.Windows[-1]
#    def make_window(cls, x=0, y=0, w=-1, h=-1): return Window(Curses.Screen, x, y, w, h)
    @classmethod
    def __make_pad(cls, x=0, y=0, w=-1, h=-1):
        cls.Pads.append(Pad(Curses.Screen, x, y, w, h))
        return cls.pads[-1]
#    def make_pad(cls, x=0, y=0, w=-1, h=-1): return Pad(Curses.Screen, x, y, w, h)
    @classmethod
    def __init_cursor(cls): curses.curs_set(0)
    @classmethod
    def __init_color_pair(cls):
        curses.setupterm('xterm-256color')
        if not curses.has_colors(): raise Exception('このターミナルは色を表示できません。')
        if not curses.can_change_color(): raise Exception('このターミナルは色を変更できません。')
        curses.use_default_colors()
        for i in range(1, curses.COLORS):
            curses.init_pair(i, i, curses.COLOR_BLACK)
    @classmethod
    def __draw(cls):
        pass
#        cls.Screen.refresh()
#        try:
#            for i in range(1, curses.COLORS):
#                self.__screen.addstr(str(i).rjust(3), curses.A_REVERSE | curses.color_pair(i))
#        except curses.ERR: pass
#        self.__screen.addstr(7, 0, self.__msg, curses.A_REVERSE | curses.color_pair(self.__color_index))
    @classmethod
    def __input(cls):
        cls.Screen.getkey()
#        cls.Windows[0].Pointer.getkey()
#        cls.Windows[1].Pointer.getkey()

class Window:
    def __init__(self, screen, x=0, y=0, w=-1, h=-1):
        self.__screen = screen
        self.__make_win(x, y, w, h)
        self.__subs = []
        self.draw()
    @property
    def Panel(self): return self.__panel
    @property
    def Pointer(self): return self.__window
    @property
    def X(self): return self.__window.getbegyx()[1]
    @property
    def Y(self): return self.__window.getbegyx()[0]
    @X.setter
    def X(self, v): self.__panel.move(self.Y, v); curses.panel.update_panels();
#    def X(self, v): self.__window.mvwin(self.Y, v)
    @Y.setter
    def Y(self, v): self.__panel.move(v, self.X); curses.panel.update_panels();
#    def Y(self, v): self.__window.mvwin(v, self.X)
    @property
    def W(self): return self.__window.getmaxyx()[1]
    @property
    def H(self): return self.__window.getmaxyx()[0]

    def __make_win(self, x=0, y=0, w=-1, h=-1):
#        self.__window = curses.newwin(h, w, y, x)
#        self.__window = curses.newwin(
#                            h if 0 < h and h <= curses.LINES else curses.LINES, 
#                            w if 0 < w and w <= curses.COLS else curses.COLS, 
#                            y if 0 <= y and y < curses.LINES - h else 0, 
#                            x if 0 <= x and x < curses.COLS - w else 0)
        h = h if 0 < h and h <= curses.LINES else curses.LINES
        w = w if 0 < w and w <= curses.COLS else curses.COLS
        y = y if 0 <= y else 0
        y = y if y <= curses.LINES - h else curses.LINES - h - 1
        x = x if 0 <= x else 0
        x = x if x <= curses.COLS - w else curses.COLS - w - 1
#        print(f'{h},{w},{y},{x}')
#        self.__screen.addstr(0,0,f'{h},{w},{y},{x}')
        self.__window = curses.newwin(h, w, y, x)
#        self.__window = curses.newwin(10, 10, 0, 0)
        self.__panel = curses.panel.new_panel(self.__window)
    def make_sub(self, x=0, y=0, w=-1, h=-1):
#        self.__window.subwin(h, w, y, x)
#        sub = self.__window.subwin(
#                        h if 0 < h and h <= self.H else self.H,
#                        w if 0 < w and w <= self.W else self.W, 
#                        y if 0 <= y and y < self.H - h else 0, 
#                        x if 0 <= x and x < self.W - w else 0)
        h = h if 0 < h and h <= self.H else self.H
        w = w if 0 < w and w <= self.W else self.W
        y = y if 0 <= y else 0
        y = y if 0 <= y and y < self.H - h else self.H - h - 1
        x = x if 0 <= x else 0
        x = x if 0 <= x and x < self.W - w else self.W - w - 1
        sub = self.__window.subwin(h, w, y, x)
        self.__subs.append(sub)
        return sub
    def draw(self, x=0, y=0, msg='Hello curses Window !!', attr=None):
#        self.Pointer.erase()
#        self.Pointer.clear()
        if attr is None: self.Pointer.addstr(y, x, msg)
        else: self.Pointer.addstr(y, x, msg, attr)
        self.Pointer.refresh()
#        curses.panel.update_panels()
    def show(self): self.__panel.show(); curses.panel.update_panels();
    def hide(self): self.__panel.hide(); curses.panel.update_panels();
    def switch(self):
        if self.__panel.hidden(): self.__panel.show()
        else: self.__panel.hide()
        curses.panel.update_panels()

class Pad: pass
class Canvas: pass
class Cursor: pass



if __name__ == "__main__":
    Curses.run()

