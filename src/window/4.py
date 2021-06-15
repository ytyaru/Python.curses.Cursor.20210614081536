#!/usr/bin/env python3
# coding: utf8
import os, curses, curses.panel

# cursesライブラリを使いやすくラップする。
class Curses:
    WndMgr = None
    init = None
    draw = None
    loop = None
    @classmethod
    def run(cls, init=None, draw=None, loop=None):
        curses.wrapper(Curses.__main, init=init, draw=draw, loop=loop)
    @classmethod
    def __main(cls, screen, *args, **kwargs):
        cls.WndMgr = WindowManager(screen)
        Curses.__init_cursor()
        Curses.__init_color_pair()
        if kwargs['init'] is None: pass
        else: kwargs['init'](cls.WndMgr)
        if kwargs['draw'] is None: cls.WndMgr.Screen.addstr('Hello curses !!')
        else: kwargs['draw'](cls.WndMgr)
        if kwargs['loop'] is None: cls.WndMgr.Screen.getkey()
        else: kwargs['loop'](cls.WndMgr)
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

class WindowManager:
    def __init__(self, screen):
        self.__screen = screen
        self.__windows = []
        self.__pads = []
    def make(self, x=0, y=0, w=-1, h=-1):
        return self.__make_pad(x,y,w,h) if curses.LINES < h or curses.COLS < w else self.__make_window(x,y,w,h)
    def make_window(self, x=0, y=0, w=-1, h=-1):
        self.__windows.append(Window(self.Screen, x, y, w, h))
        return self.__windows[-1]
    def make_pad(self, x=0, y=0, w=-1, h=-1):
        self.__pads.append(Pad(self.Screen, x, y, w, h))
        return self.__pads[-1]
    @property
    def Screen(self): return self.__screen
    @property
    def Windows(self): return self.__windows
    @property
    def Pads(self): return self.__pads

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
        h = h if 0 < h and h <= curses.LINES else curses.LINES
        w = w if 0 < w and w <= curses.COLS else curses.COLS
        y = y if 0 <= y else 0
        y = y if y <= curses.LINES - h else curses.LINES - h
        x = x if 0 <= x else 0
        x = x if x <= curses.COLS - w else curses.COLS - w
        self.__window = curses.newwin(h, w, y, x)
        self.__panel = curses.panel.new_panel(self.__window)
    def make_sub(self, x=0, y=0, w=-1, h=-1):
        h = h if 0 < h and h <= self.H else self.H
        w = w if 0 < w and w <= self.W else self.W
        y = y if 0 <= y else 0
        y = y if 0 <= y and y < self.H - h else self.H - h
        x = x if 0 <= x else 0
        x = x if 0 <= x and x < self.W - w else self.W - w
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
    def init(wndMgr):
        wndMgr.make_window(x=2,y=2,w=100,h=10)
        wndMgr.make_window(x=4,y=4,w=100,h=10)
    def draw(wndMgr):
        wndMgr.Windows[0].Pointer.noutrefresh()
        wndMgr.Windows[1].Pointer.noutrefresh()

        wndMgr.Windows[0].Pointer.clear()
        wndMgr.Windows[1].Pointer.clear()
        wndMgr.Windows[0].Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(1))
        wndMgr.Windows[1].Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(2))
        wndMgr.Windows[0].Pointer.addstr(0,0,'Window-1', curses.A_REVERSE | curses.color_pair(1))
        wndMgr.Windows[0].Pointer.addstr(1, 0, '↑↓←→:move h:hide/show PgUp/PgDn:Z-switch other:quit', curses.color_pair(15))
        wndMgr.Windows[1].Pointer.addstr(0,0,'Window-2', curses.A_REVERSE | curses.color_pair(2))
        wndMgr.Windows[1].Pointer.addstr(1, 0, '↑↓←→:move h:hide/show PgUp/PgDn:Z-switch other:quit', curses.color_pair(15))

#        wndMgr.Windows[0].Pointer.refresh()
#        wndMgr.Windows[1].Pointer.refresh()
        curses.panel.update_panels()
        curses.doupdate()
    def loop(wndMgr):
        while True:
            key = wndMgr.Screen.getch()
            if curses.KEY_UP == key: wndMgr.Windows[1].Y -= 1 if 0 < wndMgr.Windows[1].Y else 0
            elif curses.KEY_DOWN == key: wndMgr.Windows[1].Y += 1 if wndMgr.Windows[1].Y < curses.LINES-wndMgr.Windows[1].H else 0
            elif curses.KEY_LEFT == key: wndMgr.Windows[1].X -= 1 if 0 < wndMgr.Windows[1].X else 0
            elif curses.KEY_RIGHT == key: wndMgr.Windows[1].X += 1 if wndMgr.Windows[1].X < curses.COLS-wndMgr.Windows[1].W else 0
            elif ord('h') == key: wndMgr.Windows[1].switch()
            elif curses.KEY_NPAGE == key or curses.KEY_PPAGE == key:
                if curses.panel.top_panel() == wndMgr.Windows[1].Panel: wndMgr.Windows[0].Panel.top()
                else: wndMgr.Windows[1].Panel.top()
                curses.panel.update_panels()
            else: break
            wndMgr.Screen.refresh()
            curses.napms(5)
        
    Curses.run(init=init, draw=draw, loop=loop)
#    Curses.run()
