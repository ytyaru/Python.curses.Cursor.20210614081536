#!/usr/bin/env python3
# coding: utf8
import os, curses, curses.panel
# cursesライブラリを使いやすくラップする。
class Curses:
    WndMgr = None
    draw = None
    main = None
    @classmethod
    def run(cls, main=None):
        if main is not None: main.pre_init()
        curses.wrapper(Curses.__main, main=main)
    @classmethod
    def __main(cls, screen, *args, **kwargs):
        cls.main = kwargs['main'] if kwargs['main'] else CursesMain()
        cls.main.Screen = screen
        Cursor.hide()
        Curses.__init_color_pair()
        cls.main.init()
        cls.__draw()
        cls.__loop()
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
        for w in cls.main.WindowManager.Windows: w.Pointer.noutrefresh(); w.Canvas.draw();
        for p in cls.main.WindowManager.Pads: p.noutrefresh(); p.Canvas.draw();
        cls.main.WindowManager.Screen.clear()
        cls.main.draw()
        curses.panel.update_panels()
        curses.doupdate()
    @classmethod
    def __loop(cls):
        cls.__draw()
        is_loop = True
        while is_loop:
            key = cls.main.WindowManager.Screen.getch()
            is_loop = cls.main.input(key)
            cls.__draw()
            curses.napms(cls.main.WaitTime)

class CursesMain:
    def __init__(self):
        self.__screen = None
        self.__wmng = None
        self.__term = Terminal()
        self.__wait_time = 5
    @property
    def Screen(self): return self.__screen
    @Screen.setter
    def Screen(self, v):
        self.__screen = v
        self.__wmng = WindowManager(self.Screen)
    @property
    def Terminal(self): return self.__term
    @property
    def WindowManager(self): return self.__wmng
    @property
    def WaitTime(self): return self.__wait_time
    @WaitTime.setter
    def WaitTime(self, v): self.__wait_time = v
    def pre_init(self): pass
    def init(self): pass
    def draw(self): self.__wmng.Screen.addstr('Hello curses !!')
    def input(self, key): pass

class Terminal:
    @property
    def Name(self): return curses.termname()
    @Name.setter
    def Name(self, v): curses.setupterm(term=v)
    @property
    def Attrs(self): return curses.termattrs()
    def get_capability(self, capname):
        flag = curses.tigetflag(capname)
        if -1 != flag: return flag
        num = curses.tigetnum(capname)
        if -2 != num : return num
        s = curses.tigetstr(capname)
        return s
    def get_parameter(self, s, *args): # tparm(tigetstr("cup"), 5, 3) -> b'\033[6;4H'
        return curses.tparm(s, *args)

class WindowManager:
    def __init__(self, screen):
        self.__screen = screen
        self.__windows = []
        self.__pads = []
    def make(self, x=0, y=0, w=-1, h=-1):
        return self.make_pad(w,h) if curses.LINES < h or curses.COLS < w else self.make_window(x,y,w,h)
    def make_window(self, x=0, y=0, w=-1, h=-1):
        self.__windows.append(Window(self.Screen, x, y, w, h))
        return self.__windows[-1]
    def make_pad(self, w=-1, h=-1):
        self.__pads.append(Pad(self.Screen, w, h))
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
        self.__canvas = Canvas(self)
    @property
    def Panel(self): return self.__panel
    @property
    def Pointer(self): return self.__window
    @property
    def Subs(self): return self.__subs
    @property
    def Cursor(self): return self.__cursor
    @property
    def Canvas(self): return self.__canvas
    @Canvas.setter
    def Canvas(self, v): self.__canvas = v

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
        self.__canvas = Canvas(self)
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
    def Canvas(self): return self.__canvas
    @Canvas.setter
    def Canvas(self, v): self.__canvas = v

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

class Pad:
    def __init__(self, screen, w=-1, h=-1):
        self.__screen = screen
        self.__make_win(w, h)
        self.__subs = []
        self.__cursor = Cursor(self.__window)
        self.__showX = 0
        self.__showY = 0
        self.__canvas = Canvas(self)
    @property
    def Pointer(self): return self.__window
    @property
    def Subs(self): return self.__subs
    @property
    def Cursor(self): return self.__cursor
    @property
    def Canvas(self): return self.__canvas
    @Canvas.setter
    def Canvas(self, v): self.__canvas = v

    @property
    def X(self): return self.__window.getbegyx()[1]
    @property
    def Y(self): return self.__window.getbegyx()[0]
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
        return self.__subs[-1]
    def noutrefresh(self):
        self.__window.noutrefresh(self.__showY, self.__showX, 0, 0, curses.LINES-1, curses.COLS-1)
    def refresh(self):
        self.__window.refresh(self.__showY, self.__showX, 0, 0, curses.LINES-1, curses.COLS-1)

class Canvas:
    WndMgr = None
    @classmethod
    def draw(cls, draw):
        for w in cls.WndMgr.Windows: w.Pointer.noutrefresh()
        for p in cls.WndMgr.Pads: p.noutrefresh()
        draw(cls.WndMgr)
        curses.panel.update_panels()
        curses.doupdate()

    def __init__(self, window): self.__window = window
    @property
    def Window(self): return self.__window
    @Window.setter
    def Window(self, v): self.__window = v

    def draw(self): pass
    def refresh(self):
        if   isinstance(self.__window, Window): self.__window.Pointer.refresh()
        elif isinstance(self.__window, Pad): self.__window.refresh()
        else: pass
    def noutrefresh(self):
        if   isinstance(self.__window, Window): self.__window.Pointer.noutrefresh()
        elif isinstance(self.__window, Pad): self.__window.noutrefresh()
        else: pass

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
    class Main(CursesMain):
        def __init__(self): super().__init__()
        def pre_init(self):
            self.Terminal.Name = 'xterm-256color'
        def init(self):
            self.WindowManager.make_window(x=2,y=2,w=100,h=10)
            self.WindowManager.make_window(x=4,y=4,w=100,h=10)
            self.WindowManager.Windows[1].W = 40
            self.WindowManager.Windows[1].H = 20
            self.WindowManager.Windows[1].make_sub(x=2, y=4, w=20, h=4)
            self.WindowManager.Windows[0].Canvas = Canvas1(self.WindowManager.Windows[0])
            self.WindowManager.Windows[1].Canvas = Canvas2(self.WindowManager.Windows[1])
        def draw(self): pass
        def input(self, key):
            if curses.KEY_UP == key: self.WindowManager.Windows[1].Y -= 1 if 0 < self.WindowManager.Windows[1].Y else 0
            elif curses.KEY_DOWN == key: self.WindowManager.Windows[1].Y += 1 if self.WindowManager.Windows[1].Y < curses.LINES-self.WindowManager.Windows[1].H else 0
            elif curses.KEY_LEFT == key: self.WindowManager.Windows[1].X -= 1 if 0 < self.WindowManager.Windows[1].X else 0
            elif curses.KEY_RIGHT == key: self.WindowManager.Windows[1].X += 1 if self.WindowManager.Windows[1].X < curses.COLS-self.WindowManager.Windows[1].W else 0
            elif ord('h') == key: self.WindowManager.Windows[1].switch()
            elif curses.KEY_NPAGE == key or curses.KEY_PPAGE == key:
                if curses.panel.top_panel() == self.WindowManager.Windows[1].Panel: self.WindowManager.Windows[0].Panel.top()
                else: self.WindowManager.Windows[1].Panel.top()
                curses.panel.update_panels()
            elif ord('w') == key: self.WindowManager.Windows[1].H -= 1 if 1 < self.WindowManager.Windows[1].H else 0
            elif ord('s') == key: self.WindowManager.Windows[1].H += 1 if self.WindowManager.Windows[1].H+self.WindowManager.Windows[1].Y < curses.LINES else 0
            elif ord('a') == key: self.WindowManager.Windows[1].W -= 1 if 1 < self.WindowManager.Windows[1].W else 0
            elif ord('d') == key: self.WindowManager.Windows[1].W += 1 if self.WindowManager.Windows[1].W+self.WindowManager.Windows[1].X < curses.COLS else 0
            else: return False
            return True

    class Canvas1(Canvas):
        def draw(self):
            self.Window.Pointer.clear()
            self.Window.Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(1))
            self.Window.Pointer.addstr(0,0,'Window-1', curses.A_REVERSE | curses.color_pair(1))
            self.Window.Pointer.addstr(1, 0, '↑↓←→:move h:hide/show PgUp/PgDn:Z-switch asdw:resize other:quit', curses.color_pair(15))
    class Canvas2(Canvas):
        def draw(self):
            self.Window.Pointer.clear()
            self.Window.Subs[0].Pointer.clear()
            self.Window.Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(2))
            self.Window.Subs[0].Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(3))

            self.Window.Pointer.addstr(0,0,'Window-2', curses.A_REVERSE | curses.color_pair(2))
            self.Window.Pointer.addstr(1, 0, '↑↓←→:move h:hide/show PgUp/PgDn:Z-switch asdw:resize other:quit', curses.color_pair(15))
            self.Window.Subs[0].Pointer.addstr(0,0,'Window-2-Sub-1', curses.A_REVERSE | curses.color_pair(3))

#    Curses.run()
    Curses.run(Main())

