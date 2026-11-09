# A-Maze-ing — Bonus

## English

A Python program for generating and exploring random mazes in the terminal. Display the shortest route, watch a maze being built, or move through it to reach the exit.

Set the size and entrance/exit in a configuration file, then use menu numbers to interact. The maze and shortest route are also saved as text.

### Run

Requires Python 3.10 or newer. No additional packages are needed.

```sh
python3 a_maze_ing.py config.txt
```

The supplied `config.txt` generates a 20-by-15 maze, saves it to `maze.txt`, and opens the menu. Enter `4` or `q` to quit.

### Menu

| Number | Action |
| --- | --- |
| 1 | Regenerate the maze |
| 2 | Show or hide the shortest route |
| 3 | Change wall colors |
| 4 | Quit |
| 5 | Play a rainbow animation |
| 6 | Switch between Kruskal and depth-first search (DFS) |
| 7 | Animate maze generation |
| 8 | Explore the maze using WASD keys |
| 9 | Change wall characters |

### Configuration and output

`config.txt` uses `KEY=value` lines.

| Key | Meaning |
| --- | --- |
| `WIDTH` / `HEIGHT` | Maze width and height |
| `ENTRY` / `EXIT` | Coordinates `x,y`, with `0,0` at the top left |
| `OUTPUT_FILE` | Output file path |
| `PERFECT` | `True` gives a single route; `False` adds passages |
| `SEED` | Random initial value for reproducibility; defaults to 42 |
| `ALGORITHM` | `Kruskal` or `DFS`; defaults to `Kruskal` |

All keys except `SEED` and `ALGORITHM` are required. Choose different open cells for the entrance and exit. A central “42” pattern is included when there is enough space.

The output starts with one hexadecimal character per cell. Its wall value is the sum of north=1, east=2, south=4, and west=8. A blank line is followed by the entrance coordinates, exit coordinates, and shortest route. `N`, `E`, `S`, and `W` mean one step north, east, south, and west.

Generation, solving, parsing, and display are separated under `src/mazegen/`. Package metadata is in [pyproject.toml](pyproject.toml).

### Tests

```sh
make test
```

Checks both Kruskal and DFS for invalid configuration, minimal size, reproducibility, regeneration, and wall, connectivity, and route consistency.

## 日本語

ランダムな迷路を作り、端末に壁や通路を描いて操作できるPythonのプログラムです。入口から出口への最短経路を表示したり、迷路の作られる過程を見たり、自分で移動して脱出したりできます。

設定ファイルで大きさや入口・出口を指定し、起動後はメニューの番号で操作します。迷路と最短経路はテキストファイルにも保存します。

### 実行

Python 3.10以降を使用します。追加パッケージは不要です。

```sh
python3 a_maze_ing.py config.txt
```

付属の `config.txt` で20×15の迷路を生成し、`maze.txt` へ保存した後にメニューを表示します。`4` または `q` で終了します。

### メニュー

| 番号 | 操作 |
| --- | --- |
| 1 | 迷路を再生成 |
| 2 | 最短経路の表示・非表示 |
| 3 | 壁の色を変更 |
| 4 | 終了 |
| 5 | 虹色のアニメーション |
| 6 | Kruskal法と深さ優先探索（DFS）を切り替え |
| 7 | 生成過程のアニメーション |
| 8 | WASD入力で迷路を進む脱出ゲーム |
| 9 | 壁に使う文字を変更 |

### 設定と出力

`config.txt` は `項目=値` の形式です。

| 項目 | 意味 |
| --- | --- |
| `WIDTH` / `HEIGHT` | 迷路の幅と高さ |
| `ENTRY` / `EXIT` | 入口と出口の座標 `x,y`（左上が `0,0`） |
| `OUTPUT_FILE` | 出力先ファイル |
| `PERFECT` | `True` で経路が1通りになる迷路、`False` で通路を追加 |
| `SEED` | 同じ迷路を再現するための乱数の初期値（省略時は42） |
| `ALGORITHM` | `Kruskal` または `DFS`（省略時は `Kruskal`） |

`SEED`・`ALGORITHM` 以外は必須です。入口と出口は異なる通行可能なマスに指定します。十分な大きさがある場合は、中央に「42」の形を配置します。

出力ファイルの先頭は、各マスの壁を16進数1文字で表した格子です。壁は北=1・東=2・南=4・西=8を足した値で記録します。空行の後に入口の座標、出口の座標、最短経路が続きます。経路の `N`・`E`・`S`・`W` は、北・東・南・西へ1マス進むことを表します。

`src/mazegen/` に生成・探索・設定読み込み・表示を分けています。Pythonパッケージの定義は [pyproject.toml](pyproject.toml) にあります。

### テスト

```sh
make test
```

Kruskal・DFS両方について、設定エラー、最小サイズ、再現性、再生成、壁・連結性・経路の整合性を確認します。
