#!/usr/bin/env python3
# coding: utf8
import os, curses, curses.panel
# cursesライブラリを使いやすくラップする。
class Curses:
    WndMgr = None
    @classmethod
    def run(cls, init=None, draw=None, loop=None, ms=5):
        curses.wrapper(Curses.__main, init=init, draw=draw, loop=loop, ms=ms)
    @classmethod
    def __main(cls, screen, *args, **kwargs):
        cls.WndMgr = WindowManager(screen)
        Cursor.hide()
        Curses.__init_color_pair()
        if kwargs['init'] is None: pass
        else: kwargs['init'](cls.WndMgr)
        if kwargs['draw'] is None: cls.WndMgr.Screen.addstr('Hello curses !!')
        else: cls.__draw(kwargs['draw'])
        if kwargs['loop'] is None: cls.WndMgr.Screen.getkey()
        else: cls.__loop(kwargs['loop'], ms=kwargs['ms'])
    @classmethod
    def __init_color_pair(cls):
        curses.setupterm('xterm-256color')
        if not curses.has_colors(): raise Exception('このターミナルは色を表示できません。')
        if not curses.can_change_color(): raise Exception('このターミナルは色を変更できません。')
        curses.use_default_colors()
        for i in range(1, curses.COLORS):
            curses.init_pair(i, i, curses.COLOR_BLACK)
    @classmethod
    def __draw(cls, draw):
        for w in cls.WndMgr.Windows: w.Pointer.noutrefresh()
#        for p in cls.WndMgr.Pads: p.Pointer.noutrefresh()
        for p in cls.WndMgr.Pads: p.noutrefresh()
        draw(cls.WndMgr)
        curses.panel.update_panels()
        curses.doupdate()
    @classmethod
    def __loop(cls, loop, ms=5):
        use_pad = True if 0 < len(cls.WndMgr.Pads) else False
        if use_pad: cls.WndMgr.Pads[0].Pointer.keypad(True)
        is_loop = True
        while is_loop:
            key = cls.WndMgr.Pads[0].Pointer.getch() if use_pad else cls.WndMgr.Screen.getch()
#            key = cls.WndMgr.Screen.getch()
            is_loop = loop(cls.WndMgr, key)
            if use_pad: cls.WndMgr.Pads[0].refresh()
            else: cls.WndMgr.Screen.refresh()
            curses.napms(ms)

class WindowManager:
    def __init__(self, screen):
        self.__screen = screen
        self.__windows = []
        self.__pads = []
    def make(self, x=0, y=0, w=-1, h=-1):
#        return self.__make_pad(x,y,w,h) if curses.LINES < h or curses.COLS < w else self.__make_window(x,y,w,h)
        return self.make_pad(w,h) if curses.LINES < h or curses.COLS < w else self.make_window(x,y,w,h)
    def make_window(self, x=0, y=0, w=-1, h=-1):
        self.__windows.append(Window(self.Screen, x, y, w, h))
        return self.__windows[-1]
    def make_pad(self, w=-1, h=-1):
#    def make_pad(self, x=0, y=0, w=-1, h=-1):
        self.__pads.append(Pad(self.Screen, w, h))
#        self.__pads.append(Pad(self.Screen, x, y, w, h))
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
        self.__cursor = Cursor(self.__window)
    @property
    def Panel(self): return self.__panel
    @property
    def Pointer(self): return self.__window
    @property
    def Subs(self): return self.__subs
    @property
    def Cursor(self): return self.__cursor
    @property
    def X(self): return self.__window.getbegyx()[1]
    @property
    def Y(self): return self.__window.getbegyx()[0]
    @X.setter
    def X(self, v): self.__panel.move(self.Y, v); curses.panel.update_panels();
    @Y.setter
    def Y(self, v): self.__panel.move(v, self.X); curses.panel.update_panels();
    @property
    def W(self): return self.__window.getmaxyx()[1]
    @property
    def H(self): return self.__window.getmaxyx()[0]
    @W.setter
    def W(self, v): self.__window.resize(self.H, v); curses.panel.update_panels();
    @H.setter
    def H(self, v): self.__window.resize(v, self.W); curses.panel.update_panels();
    def __make_win(self, x=0, y=0, w=-1, h=-1):
        h = h if 0 < h and h <= curses.LINES else curses.LINES
        w = w if 0 < w and w <= curses.COLS else curses.COLS
        y = y if 0 <= y else 0
        y = y if y <= curses.LINES - h else curses.LINES - h
        x = x if 0 <= x else 0
        x = x if x <= curses.COLS - w else curses.COLS - w
        self.__window = curses.newwin(h, w, y, x)
        self.__panel = curses.panel.new_panel(self.__window)
    def make_sub(self, x=0, y=0, w=-1, h=-1, is_derwin=True):
        self.__subs.append(SubWindow(self.Pointer,x=x,y=y,w=w,h=h,is_derwin=is_derwin))
        return self.__subs[-1]
    def show(self): self.__panel.show(); curses.panel.update_panels();
    def hide(self): self.__panel.hide(); curses.panel.update_panels();
    def switch(self):
        if self.__panel.hidden(): self.__panel.show()
        else: self.__panel.hide()
        curses.panel.update_panels()

class SubWindow:
    def __init__(self, parent, x=0, y=0, w=-1, h=-1, is_derwin=True):
        self.__parent = parent
        self.__window = self.__make(x=x, y=y, w=w, h=h, is_derwin=is_derwin)
        self.__cursor = Cursor(self.__window)
    def __make(self, x=0, y=0, w=-1, h=-1, is_derwin=True):
        ph, pw = self.__parent.getmaxyx()
        h = h if 0 < h and h <= ph else ph
        w = w if 0 < w and w <= pw else pw
        y = y if 0 <= y else 0
        y = y if 0 <= y and y < ph - h else ph - h
        x = x if 0 <= x else 0
        x = x if 0 <= x and x < pw - w else pw - w
        return self.__parent.derwin(h, w, y, x) if is_derwin else self.__parent.subwin(h, w, y, x)
    @property
    def Pointer(self): return self.__window
    @property
    def Cursor(self): return self.__cursor
    @property
    def X(self): return self.__window.getbegyx()[1]
    @property
    def Y(self): return self.__window.getbegyx()[0]
    @X.setter
    def X(self, v): self.__window.mvwin(self.Y, v)
    @Y.setter
    def Y(self, v): self.__window.mvwin(v, self.X)

    @property
    def FromParentX(self): return self.__window.getparyx()[1]
    @property
    def FromParentY(self): return self.__window.getparyx()[0]
    @FromParentX.setter
    def FromParentX(self, v): self.__window.mvderwin(self.Y, v)
    @FromParentY.setter
    def FromParentY(self, v): self.__window.mvderwin(v, self.X)

    @property
    def W(self): return self.__window.getmaxyx()[1]
    @property
    def H(self): return self.__window.getmaxyx()[0]
    @W.setter
    def W(self, v): self.__window.resize(self.H, v)
    @H.setter
    def H(self, v): self.__window.resize(v, self.W)

# padはpanelを使えない
class Pad:
    def __init__(self, screen, w=-1, h=-1):
#    def __init__(self, screen, x=0, y=0, w=-1, h=-1):
        self.__screen = screen
        self.__make_win(w, h)
#        self.__make_win(x, y, w, h)
        self.__subs = []
        self.__cursor = Cursor(self.__window)
        self.__showX = 0
        self.__showY = 0
    @property
    def Pointer(self): return self.__window
    @property
    def Subs(self): return self.__subs
    @property
    def Cursor(self): return self.__cursor

    @property
    def X(self): return self.__window.getbegyx()[1]
    @property
    def Y(self): return self.__window.getbegyx()[0]
#    @X.setter
#    def X(self, v): self.__panel.move(self.Y, v); curses.panel.update_panels();
#    @Y.setter
#    def Y(self, v): self.__panel.move(v, self.X); curses.panel.update_panels();
    @X.setter
    def X(self, v): self.__window.mvwin(self.Y, v)
    @Y.setter
    def Y(self, v): self.__window.mvwin(v, self.X)

    @property
    def ShowX(self): return self.__showX
    @property
    def ShowY(self): return self.__showY
    @ShowX.setter
    def ShowX(self, v): self.__showX = v
    @ShowY.setter
    def ShowY(self, v): self.__showY = v

    @property
    def W(self): return self.__window.getmaxyx()[1]
    @property
    def H(self): return self.__window.getmaxyx()[0]
    @W.setter
    def W(self, v): self.__window.resize(self.H, v); curses.panel.update_panels();
    @H.setter
    def H(self, v): self.__window.resize(v, self.W); curses.panel.update_panels();
    def __make_win(self, w=-1, h=-1):
        h = h if 0 < h else curses.LINES
        w = w if 0 < w else curses.COLS
        self.__window = curses.newpad(h, w)
    def make_sub(self, x=0, y=0, w=-1, h=-1, is_derwin=True):
        self.__subs.append(self.__window.subpad(h, w, y, x))
#        self.__subs.append(SubPad(self.Pointer,x=x,y=y,w=w,h=h,is_derwin=is_derwin))
        return self.__subs[-1]
    def noutrefresh(self):
#        self.__window.noutrefresh(0, 0, 0, 0, 1, 1)
#        self.__window.noutrefresh(0, 0, 0, 0, curses.LINES, curses.COLS)
#        self.__window.noutrefresh(0, 0, 0, 0, self.H-1, self.W-1)
#        self.__window.noutrefresh(self.__showY, self.__showX, 0, 0, self.H-1, self.W-1)
#        self.__window.noutrefresh(self.__showY, self.__showX, 0, 0, self.H, self.W)
#        self.__window.noutrefresh(self.__showY, self.__showX, self.Y, self.X, self.H, self.W)
#        self.__window.noutrefresh(self.__showY, self.__showX, self.Y, self.X, 5, 5)
        self.__window.noutrefresh(self.__showY, self.__showX, 0, 0, curses.LINES-1, curses.COLS-1)
    def refresh(self):
        self.__window.refresh(self.__showY, self.__showX, 0, 0, curses.LINES-1, curses.COLS-1)
#        self.__window.refresh(self.__showY, self.__showX, 0, 0, self.H, self.W)
#        self.__window.refresh(self.__showY, self.__showX, self.Y, self.X, self.H, self.W)
    """
    def show(self): self.__panel.show(); curses.panel.update_panels();
    def hide(self): self.__panel.hide(); curses.panel.update_panels();
    def switch(self):
        if self.__panel.hidden(): self.__panel.show()
        else: self.__panel.hide()
        curses.panel.update_panels()
    """

class Canvas: pass


class Cursor:
    @classmethod
    def hide(cls): curses.curs_set(0)
    @classmethod
    def show(cls, is_underline=False):
        if is_underline: curses.curs_set(1)
        else: curses.curs_set(2)
    def __init__(self, window):
        self.__window = window
    @property
    def X(self): return self.__window.getsyx()[1]
    @property
    def Y(self): return self.__window.getsyx()[0]
    @X.setter
    def X(self, v): self.__window.move(self.Y, v)
    @Y.setter
    def Y(self, v): self.__window.move(v, self.X)
    def synchronize(self): self.__window.cursyncup()

if __name__ == "__main__":
    def init(wndMgr):
        wndMgr.make_pad(w=curses.COLS*3,h=curses.LINES*3)
#        wndMgr.Pads[0].make_sub(x=40, y=2, w=20, h=4)
#        wndMgr.Pads[0].make_sub(x=40, y=0, w=curses.COLS-40, h=curses.LINES)
        wndMgr.Pads[0].make_sub(x=40, y=0, w=curses.COLS-40, h=wndMgr.Pads[0].H)
    def draw(wndMgr):
        wndMgr.Pads[0].Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(4))
        for i in range(0, wndMgr.Pads[0].H):
            wndMgr.Pads[0].Pointer.addstr(i, 0, f'Pad-1 {i} {wndMgr.Pads[0].ShowX},{wndMgr.Pads[0].ShowY} ({wndMgr.Pads[0].X},{wndMgr.Pads[0].Y}) {wndMgr.Pads[0].W},{wndMgr.Pads[0].H}', curses.A_REVERSE | curses.color_pair(4))
        wndMgr.Pads[0].Subs[0].clear()
#        wndMgr.Pads[0].Subs[0].box()
        wndMgr.Pads[0].Subs[0].bkgd(' ', curses.A_REVERSE | curses.color_pair(5))
#        wndMgr.Pads[0].Subs[0].addstr(0, 0, f'Pad-1-Sub-1', curses.A_REVERSE | curses.color_pair(5))
        wndMgr.Pads[0].Subs[0].addstr(
            wndMgr.Pads[0].ShowY, 
            wndMgr.Pads[0].ShowX, 
            f'Pad-1-Sub-1', 
            curses.A_REVERSE | curses.color_pair(5))
        wndMgr.Pads[0].refresh()
    def loop(wndMgr, key):
        if curses.KEY_UP == key: wndMgr.Pads[0].ShowY -= 1 if 0 < wndMgr.Pads[0].ShowY else 0
        elif curses.KEY_DOWN == key: wndMgr.Pads[0].ShowY += 1 if wndMgr.Pads[0].ShowY < wndMgr.Pads[0].H-curses.LINES else 0
        elif curses.KEY_LEFT == key: wndMgr.Pads[0].ShowX -= 1 if 0 < wndMgr.Pads[0].ShowX else 0
        elif curses.KEY_RIGHT == key: wndMgr.Pads[0].ShowX += 1 if wndMgr.Pads[0].ShowX < wndMgr.Pads[0].W-curses.COLS else 0
        else: return False
        draw(wndMgr)
        return True
        
    Curses.run(init=init, draw=draw, loop=loop)
#    Curses.run()
