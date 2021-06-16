#!/usr/bin/env python3
# coding: utf8
if __name__ == "__main__":
    import curses, Curses, Layout
    class Pad1(Curses.Pad):
        def init(self):
            self.Pointer.clear()
            self.Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(4))
            for i in range(0, self.H):
                self.Pointer.addstr(i, 0, f'Pad-1 {i} {self.ShowX},{self.ShowY} ({self.X},{self.Y}) {self.W},{self.H}', curses.A_REVERSE | curses.color_pair(4))
    class SubPad1(Curses.SubPad):
        def init(self):
            self.Pointer.clear()
            self.Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(7))
            self.Pointer.addstr(
                0,0,
                f'SubPad-1', 
                curses.A_REVERSE | curses.color_pair(7))
    class Window1(Curses.Window):
        def draw(self):
            self.Pointer.clear()
            self.Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(5))
            self.Pointer.addstr(
                0,0,
                f'Window-1', 
                curses.A_REVERSE | curses.color_pair(5))
            self.Pointer.addstr(
                1,0,
                f'{Curses.Pad.Pads[0].ShowX},{Curses.Pad.Pads[0].ShowY} ({self.X},{self.Y}) {self.W},{self.H}', 
                curses.A_REVERSE | curses.color_pair(5))
    class SubWindow1(Curses.SubWindow):
        def draw(self):
            self.Pointer.clear()
            self.Pointer.bkgd(' ', curses.A_REVERSE | curses.color_pair(6))
            self.Pointer.addstr(
                0,0,
                f'SubWindow-1', 
                curses.A_REVERSE | curses.color_pair(6))
    class KeyInput(Curses.Input):
        def input(self, key):
            if curses.KEY_UP == key: Curses.Pad.Pads[0].ShowY -= 1 if 0 < Curses.Pad.Pads[0].ShowY else 0
            elif curses.KEY_DOWN == key: Curses.Pad.Pads[0].ShowY += 1 if Curses.Pad.Pads[0].ShowY < Curses.Pad.Pads[0].H-curses.LINES else 0
            elif curses.KEY_LEFT == key: Curses.Pad.Pads[0].ShowX -= 1 if 0 < Curses.Pad.Pads[0].ShowX else 0
            elif curses.KEY_RIGHT == key: Curses.Pad.Pads[0].ShowX += 1 if Curses.Pad.Pads[0].ShowX < Curses.Pad.Pads[0].W-curses.COLS else 0
            else: return False
            return True
    def init():
        pad_w = int(curses.COLS/3)
        pad = Pad1(w=pad_w, h=curses.LINES*3)
        subpad = SubPad1(pad, x=2, y=2, w=int(pad_w/2), h=int(curses.LINES*3/3))
        win = Window1(x=pad_w+1, y=0, w=curses.COLS-(pad_w+1), h=curses.LINES)
        subwin = SubWindow1(win, x=2, y=2, w=20, h=5)

        win.X = 2
        pad.X = 2

#        Layout.flow_layout_h(targets=[pad, win], wr=[30, 70], hr=[100,100])

#        flow_layout_h(targets=[pad, win], rates=[30, 70])
#        flow_layout_h(targets=[pad, win], value=[pad_w, -2])
#        flow_layout_v()
        KeyInput()

    Curses.Terminal.Name = 'xterm-256color'
    Curses.Curses.run(init=init, wait_time=5)
#    Curses.run()

