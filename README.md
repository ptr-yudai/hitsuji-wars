# Hitsuji-Wars

## TBD
TBD

## ゲームの追加方法
ゲームを追加するには`game`フォルダに新しくフォルダ（以降ゲームフォルダと呼ぶ）を追加し、その中でゲームを定義します。
`game/tictactoe`を例に見てみましょう。

### game.json
まずゲームに関する情報をJSONフォーマットで書き、ゲームフォルダ中の`game.json`に保存します。
`game.json`は次のようなJSONファイルです。
```json

```

次のキーと値が設定できます。（*が付いている項目は必須です。）

| キー          | 値                           |
|:-------------:|:---------------------------:|
| *`title`       | ゲームのタイトル。 |
| *`min_players` | プレイヤーの最低人数。（正の整数値） |
| *`max_players` | プレイヤーの最大人数。（正の整数値） |
| `timeout`     | デフォルトのタイムアウト時間（ミリ秒）。指定しない場合1手10秒。 |

### game.py
ゲームの進行役を定義します。


