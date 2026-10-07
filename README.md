# 小美操場跑步動畫

使用 Python 和 Pygame 製作的操場跑步動畫。小美沿橢圓形跑道移動，依照跑道位置呈現遠小近大的效果，並可播放背景音樂。程式提供無限跑步和跑完三圈兩種模式。

## 功能

- 繪製草地、橢圓跑道與小美角色。
- 依跑道上的位置調整角色大小，遠處約為原尺寸的 60%，近處恢復為原尺寸。
- 提供 `run()` 無限跑步模式，以及跑完三圈後停止的 `run_three_laps()` 模式。
- 支援以 `ESC` 或關閉視窗結束動畫。
- 啟動時檢查 `assets/` 素材：缺少角色圖片時以 Pygame 繪製替代角色；若沒有可用的音樂檔，則嘗試下載符合授權條件的音訊，並在無法下載時產生約五秒的 WAV 音樂。

## 環境需求

- Python 3.10 或更新版本
- `requirements.txt` 列出的套件：Pygame、Requests

## 安裝

在專案根目錄建立並啟用虛擬環境，再安裝依賴套件。

**Windows（PowerShell）**

```powershell
py -m venv .env
.\.env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .env
source .env/bin/activate
python -m pip install -r requirements.txt
```

## 執行

```bash
python main.py
```

在命令列選擇模式：

1. **無限跑步 (`run`)**：小美持續跑步，按 `ESC` 或關閉視窗結束。
2. **跑三圈 (`run_three_laps`)**：顯示目前圈數；完成三圈後小美停在終點，按 `ESC` 或關閉視窗結束。
3. **離開**：結束程式。

直接按 Enter 會啟動無限跑步模式。動畫視窗大小為 800 × 600。

也可以從其他 Python 程式呼叫其中一種模式：

```python
from main import run, run_three_laps

run()
# 或：run_three_laps()
```

## 專案檔案

```text
.
├── assets/
│   ├── girl.png
│   └── music.wav
├── main.py
├── PRD.md
├── Prompts.md
└── requirements.txt
```

素材會由 `main.py` 中的 `prepare_assets()` 檢查與準備。音樂可能使用 `assets/music.mp3` 或 `assets/music.wav`；若音訊下載不可用，程式會產生 WAV 替代音樂。
