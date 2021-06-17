import curses
def init(scr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_GREEN)
#    scr.addstr(scr.__class__.__name__, curses.color_pair(1))
    with open('/tmp/work/putwin.txt', 'br') as f:
        window = curses.getwin(f)
#        window.refresh()
#        scr.putwin(f)
#    scr.getkey()
    window.getkey()
curses.wrapper(init)

