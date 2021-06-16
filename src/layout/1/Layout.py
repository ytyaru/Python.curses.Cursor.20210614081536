#!/usr/bin/env python3
# coding: utf8
import curses, Curses
# 複数のwindow/padをつくるときの配置を簡略化する。
#   始点座標、サイズを画面比率で調整する。
#   pad, win = LeftRightLayout(Pad, Window, 50%, 50%)
#   レイアウトタイプは以下のとおり。
#   * 横方向（左から右へ）
#   * 縦方向（上から下へ）

#def flow_layout_h(targets=None, rates=None, values=None, w=-1, h=-1):
# wr: width-rate, hr: height-rate, mw:max-width, mh:max-height
def flow_layout_h(targets=None, wr=None, hr=None, mw=-1, mh=-1, x=0, y=0):
    if len(targets) == len(wr) == len(hr):
        nx = 0
        for i, target in enumerate(targets):
            targets[i].X = nx
            targets[i].Y = y
            targets[i].W = (mw if 0 < mw else curses.COLS) * wr[i]
            targets[i].H = (mh if 0 < mh else curses.LINES) * hr[i]
            nx += targets[i].W

