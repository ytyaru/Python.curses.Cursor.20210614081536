#!/usr/bin/env python3
# coding: utf8
import os, curses, curses.panel

# windowにてカーソル関係のAPIを使う。
class Curses:
    Screen = None
    Windows = []
    Pads = []
    WndMgr = None
    init = None
    draw = None
    loop = None
    @classmethod
    def run(cls, init=None, draw=None, loop=None):
        curses.wrapper(Curses.__main, init=init, draw=draw, loop=loop)
    @classmethod
    def __main(cls, screen, *args, **kwargs):
        Curses.Screen = screen
        cls.WndMgr = WindowManager(screen)
        """
        b = lambda cls.WndMgr: None
        a = lambda cls: None
        a = lambda cls: print()
        a = lambda cls: pass
        b = lambda cls.WndMgr: pass
        cls.init = kwargs['init'] if kwargs['init'] is not None else lambda cls.WndMgr: pass
        cls.draw = kwargs['draw'] if kwargs['draw'] is not None else lambda cls.WndMgr: cls.WndMgr.Screen.addstr('Hello curses !!')
        cls.loop = kwargs['loop'] if kwargs['loop'] is not None else lambda cls.WndMgr: cls.WndMgr.Screen.getkey()

#        cls.init = kwargs['init'] if kwargs['init'] is not None else lambda cls.WndMgr: pass
#        cls.draw = kwargs['draw'] if kwargs['draw'] is not None else lambda cls.WndMgr: cls.WndMgr.Screen.addstr('Hello curses !!')
#        cls.loop = kwargs['loop'] if kwargs['loop'] is not None else lambda cls.WndMgr: cls.WndMgr.Screen.getkey()

#        cls.init = init if init is not None else lambda cls.WndMgr: pass
#        cls.draw = draw if init is not None else lambda cls.WndMgr: cls.WndMgr.Screen.addstr('Hello curses !!')
#        cls.loop = loop if init is not None else lambda cls.WndMgr: cls.WndMgr.Screen.getkey()
        """
        Curses.__init_cursor()
        Curses.__init_color_pair()
        """
        cls.init(cls.WndMgr)
        cls.draw(cls.WndMgr)
        cls.loop(cls.WndMgr)
        """

        if kwargs['init'] is None: pass
        else: kwargs['init'](cls.WndMgr)
        if kwargs['draw'] is None: cls.WndMgr.Screen.addstr('Hello curses !!')
        else: kwargs['draw'](cls.WndMgr)
        if kwargs['loop'] is None: cls.WndMgr.Screen.getkey()
        else: kwargs['loop'](cls.WndMgr)


#        Curses.__make_window(x=2,y=2,w=100,h=10)
#        Curses.__make_window(x=4,y=4,w=100,h=10)
#        cls.Windows[0].Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(1))
#        cls.Windows[1].Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(2))
#        cls.Windows[0].draw(y=0, msg='Window-1', attr=curses.A_REVERSE | curses.color_pair(1))
#        cls.Windows[1].draw(y=1, msg='Window-2', attr=curses.A_REVERSE | curses.color_pair(2))
#        curses.panel.update_panels()

#        Curses.__draw()
#        Curses.__input()
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

class WindowManager:
    def __init__(self, screen):
        self.__screen = screen
        self.__windows = []
        self.__pads = []
    def make(self, x=0, y=0, w=-1, h=-1):
        return self.__make_pad(x,y,w,h) if curses.LINES < h or curses.COLS < w else self.__make_window(x,y,w,h)
    def make_window(self, x=0, y=0, w=-1, h=-1):
        self.__windows.append(Window(Curses.Screen, x, y, w, h))
        return self.__windows[-1]
    def make_pad(self, x=0, y=0, w=-1, h=-1):
        self.__pads.append(Pad(Curses.Screen, x, y, w, h))
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
    def init(windowManager):
        windowManager.make_window(x=2,y=2,w=100,h=10)
        windowManager.make_window(x=4,y=4,w=100,h=10)

    def draw(windowManager):
        windowManager.Windows[0].Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(1))
        windowManager.Windows[1].Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(2))
        windowManager.Windows[0].draw(y=0, msg='Window-1', attr=curses.A_REVERSE | curses.color_pair(1))
        windowManager.Windows[1].draw(y=1, msg='Window-2', attr=curses.A_REVERSE | curses.color_pair(2))
        curses.panel.update_panels()
        
    Curses.run(init=init, draw=draw)
#    Curses.run()
