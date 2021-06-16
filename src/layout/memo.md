# Layout

　複数のWindow/Padをつくるときの配置を簡略化する。

　始点座標、サイズを画面比率で調整する。

```python
pad, win = LeftRightLayout(Pad, Window, 50%, 50%)
```

　レイアウトタイプは以下のとおり。

* flow
	* 横方向（左から右へ）
	* 縦方向（上から下へ）

　リサイズするかどうかでLayoutクラスの寿命をどうするか判断する。

* リサイズしない：Window/Pad生成時、一度だけLayoutメソッドを実行すればよい
* リサイズする：Window/PadインスタンスにLayoutインスタンスを保持する。アクセス可能にし、`window.resize()`と連動させる

　cursesでは端末のリサイズに反応できない。なのでユーザのキーイベントなどを契機にしてWindow/Padのリサイズをする。このときLayoutはリサイズに応じて比率を保ったまま拡大・縮小するよう実装したい。

