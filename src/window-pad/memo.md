# Pad

## 問題1：[newpad][]で得たPadが[mvwin][]で座標設定できない

### 対策1：[subpad][]で[mvwin][]する
### 対策2：[newwin][]で得たインスタンスをもつPadクラスを自作する

### 調査

　実行するとエラーになる。このせいで次のようなAPIにする予定だったが、断念せざるを得ない。

```python
class Window:
    @X.setter
    def X(self, v): self.__panel.move(self.Y, v); curses.panel.update_panels();
    @Y.setter
    def Y(self, v): self.__panel.move(v, self.X); curses.panel.update_panels();
class SubWindow:
    @X.setter
    def ScreenX(self, v): self.__window.mvwin(self.Y, v)
    @Y.setter
    def ScreenY(self, v): self.__window.mvwin(v, self.X)
    @X.setter
    def X(self, v): self.__window.derwin(self.Y, v)
    @Y.setter
    def Y(self, v): self.__window.derwin(v, self.X)
class Pad:
    @X.setter
    def X(self, v): self.__window.mvwin(self.Y, v)
    @Y.setter
    def Y(self, v): self.__window.mvwin(v, self.X)
class SubPad:
    @X.setter
    def ScreenX(self, v): self.__window.mvwin(self.Y, v)
    @Y.setter
    def ScreenY(self, v): self.__window.mvwin(v, self.X)
    @X.setter
    def X(self, v): self.__window.derwin(self.Y, v)
    @Y.setter
    def Y(self, v): self.__window.derwin(v, self.X)
```

　Window/Padをつくるときは次のように座標指定をする。だがPadはできない。Windowとの違いである。

```python
def init():
    pad_w = int(curses.COLS/3)
    pad = Pad1(w=pad_w, h=curses.LINES*3)
    subpad = SubPad1(pad, x=2, y=2, w=int(pad_w/2), h=int(curses.LINES*3/3))
    win = Window1(x=pad_w+1, y=0, w=curses.COLS-(pad_w+1), h=curses.LINES)
    subwin = SubWindow1(win, x=2, y=2, w=20, h=5)
    KeyInput()

Curses.run(init=init, wait_time=5)
```

　Window/Padの違いは次のようなツリー構造になることだ。

* Screen
	* Window1 `(0,0)`
		* SubWindow11 `(0,10)`
		* SubWindow12 `(0,20)`
	* Window2 `(10,0)`
		* SubWindow21 `(10,10)`
		* SubWindow22 `(10,20)`
	* Window3 `(20,0)`
		* SubWindow31 `(20,10)`
		* SubWindow32 `(20,20)`

　[newwin][]によりWindowは複数つくって座標を変更できる。それに対して、[newpad][]は複数つくれても座標は`(0,0)`固定である。よって複数つくっても最上層にあるPadしか見えない。このことから必然的に、1つのPadに複数のSubPadをつくる構造をもちいることになる。

* Screen
	* Pad `(0,0)`
		* SubPad1 `(0,0)`
			* SubPad11 `(0,10)`
			* SubPad12 `(0,20)`
		* SubPad2 `(10,0)`
			* SubPad21 `(10,10)`
			* SubPad21 `(10,20)`
		* SubPad3 `(20,0)`
			* SubPad31 `(20,10)`
			* SubPad31 `(20,20)`

　WindowかPadか。その違いを意識せずに実装したい。

　ならばWindowをPadに合わせて[newwin][]を１つだけ作るようにすればよいだろう。

　さらに、エンドユーザはWindow/Padの区別を意識することなく作りたい。するとAPIは以下のようになるか。

```python
window = Area(w=端末Wより大きい, h=端末Hより大きい)
pad    = Area(w=端末W以下, h=端末H以下)
```

　端末サイズ以下ならWindowになる。端末サイズよりも大きなサイズを指定したときはPadになる。ただ、環境や設定によっては端末サイズが異なる。どんな環境でもWindow/Padで固定したいときもあるはずだ。そんなときは上位互換であるPadのほうを使えばよい。

　だったら、もうWindowは使わず、すべてPadをもちいるようにすればよいのでは？　いちいち端末サイズと比較してWindow/Padどちらを返すか判定したり、Window/Padどちらも併用するようにしたら複雑になってしまう。それならPadをWindowのように使うこともできるようにすればいいだけの話だ。

　というわけで、Padの使い方をより詳細にしらべたい。

* Padの用法確認
	* 正常系
		* 端末サイズより小さいとき、エラーなく固定領域(Window)のように表示されること
		* [newpad][]だけでなく[subpad][]の表示領域も動的変更できること
	* 異常系
		* [newpad][]を複数つくれること
		* [newpad][]を複数つくっても座標は`(0,0)`固定であること（[mvwin][]するとエラーになること）
		* [newpad][]を複数つくったとき座標は`(0,0)`固定であるため描画した順で上書きされること
		* [newpad][]のZ軸を管理すべくPanelを使いたいが、Padには使えないこと
		* [subpad][]を複数つくったとき座標は[mvwin][]で移動できること
		* [subpad][]を複数つくったとき座標を[mvwin][]で移動し、ほかの[subpad][]と重なり合う位置にセットできること
		* [subpad][]を複数つくり、ほかの[subpad][]と重なり合う位置にセットしたとき、描画した順で上書きされること
		* [subpad][]のZ軸を管理すべくPanelを使いたいが、Padには使えないこと

　残念ながら、すでにPadにはPanelが使えないことがわかっている。このせいでポップアップなど重ね合わせを簡単に切替たり、実装を分割することが難しくなってしまう。Padのほうが上位互換だといったが、じつはPanelが使えないという欠点がある。むしろ下位互換とさえいえるだろう。

　だったら逆に、Windowから派生クラスをつくってPadのようにスクロール表示できるようにしたほうがよいのでは？　それならPanelも使える。

　Window/Padのちがいをまとめてみる。

項目|Window|Pad
----|------|---
`*.keypad(True)`|不|要
`*.getch()`|`Screen`|`Pad`
[new*][]で座標指定|○|☓
[mvwin][]で座標変更|○|☓
`curses.panel`使用|○|☓
[refresh][],[noutrefresh][]引数|0|6

　これだけの差を吸収することは不可能である。とくにPanelが使えないのはどうしようもない。

　やはり差分を吸収するには、Windowを継承してPadのように動くクラスを自作するしかない。

　curses.windowクラスを継承するにはどうしたらいいか？　残念ながらできない。cursesのwindowは公開されたクラスではないため。よって、[newwin][]でインスタンス生成したものをメンバ変数として持たせたクラスを自作するしかない。

* [how-to-extend-the-curses-window-class-in-python3](https://stackoverflow.com/questions/45050864/how-to-extend-the-curses-window-class-in-python3)

### 対策：[subpad][]で[mvwin][]する

[newpad]:https://docs.python.org/ja/3/library/curses.html#curses.newpad
[newwin]:https://docs.python.org/ja/3/library/curses.html#curses.newwin
[mvwin]:https://docs.python.org/ja/3/library/curses.html#curses.window.mvwin
[mvderwin]:https://docs.python.org/ja/3/library/curses.html#curses.window.mvderwin
[refresh]:https://docs.python.org/ja/3/library/curses.html#curses.window.refresh
[noutrefresh]:https://docs.python.org/ja/3/library/curses.html#curses.window.noutrefresh
[subpad]:https://docs.python.org/ja/3/library/curses.html#curses.window.subpad

