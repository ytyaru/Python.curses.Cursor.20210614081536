import curses
def init(scr):
#    scr.addstr(dir(scr))
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_GREEN)
    scr.addstr(scr.__class__.__name__, curses.color_pair(1))
    with open('/tmp/work/putwin.txt', 'bw') as f:
        scr.putwin(f)
    scr.getkey()
curses.wrapper(init)

