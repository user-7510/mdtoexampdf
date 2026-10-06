# mdtoexampdf

[English](README.en.md) | 繁體中文

把純 Markdown 寫的考卷轉成 PDF，一次產生「學生版」（答案括號留空）與「教師版」（保留答案）。字型、紙張大小、字級都可以自行指定。


## 功能

- 以純 Markdown 撰寫考卷，題號、圖片、選項自動排在同一題內
- 一份原稿產生兩種 PDF：學生版與教師版（`--key`）
- 自選字型：字型檔路徑，或系統已安裝的字型名稱
- 自選紙張：A3、A4、A5、B4、B5、Letter、Legal，或自訂「寬x高」（mm），可橫向
- 字級預設 14 pt，可調整
- 頁尾自動加上「第 X 頁/共 Y 頁」
- 找不到圖片時在終端機提示，不會悄悄漏圖


## 技術堆疊

Python 3、[Python-Markdown](https://python-markdown.github.io/)、[WeasyPrint](https://weasyprint.org/)

測試環境：Termux（Python 3.14、WeasyPrint 70.0、Markdown 3.11）。


## 專案結構

```
mdtoexampdf/
  build.py
  exam.css
  requirements.txt
  fonts/
  examples/
    exam.md
    img/
      fig1.png
```

- `build.py`：轉換腳本
- `exam.css`：標題、外框、圖片等固定樣式；字型、紙張、字級由腳本依選項產生
- `fonts/`：放自備字型檔的位置，內容不會被 git 追蹤
- `examples/`：範例考卷與範例圖片


## 安裝

WeasyPrint 依賴 Pango，需先安裝系統套件。

- macOS：`brew install pango`
- Ubuntu／Debian：`sudo apt install libpango-1.0-0 libpangoft2-1.0-0`
- Windows：需另裝 GTK 執行環境，請依 WeasyPrint 官方文件操作
- Termux：見下方指令

Linux／macOS：

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

說明：

1. 第 1 行：建立虛擬環境。
2. 第 2 行：啟用虛擬環境（Windows 改用 `.venv\Scripts\activate`）。
3. 第 3 行：安裝 Markdown 與 WeasyPrint。

Termux：

```
pkg update && pkg upgrade -y
pkg install -y python clang make libffi pango libxml2 libxslt freetype libjpeg-turbo poppler
termux-setup-storage
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

說明：

1. 第 2 行：安裝 Python、編譯工具、Pango 與依賴；`poppler` 提供檢查用的 `pdftotext`、`pdffonts`。
2. 第 3 行：取得共用儲存空間權限，用來讀取放在「下載」資料夾的字型與圖片。
3. 第 6 行：安裝 Markdown、WeasyPrint 與其依賴（含 Pillow、cffi），視網路與環境可能需要數分鐘。


## 使用方式

```
python build.py examples/exam.md student.pdf
python build.py examples/exam.md key.pdf --key
```

說明：

1. 第 1 行：產生學生版，答案括號留空。
2. 第 2 行：產生教師版，保留答案。

圖片路徑以 `.md` 檔所在資料夾為基準，所以範例中的 `img/fig1.png` 指的是 `examples/img/fig1.png`。

### 選項

| 選項 | 預設 | 說明 |
| :--- | :--- | :--- |
| `--key` | 關 | 產生教師版，保留答案 |
| `--font` | `fonts/kaiu.ttf` | 字型檔路徑，或系統已安裝的字型名稱 |
| `--font-size` | `14` | 內文字級，單位 pt，範圍 6 至 40 |
| `--paper` | `A4` | 紙張大小，見下方 |
| `--landscape` | 關 | 橫向 |

### 自選字型

三種方式，擇一即可：

1. 把字型檔放進 `fonts/`，並命名為 `kaiu.ttf`，不必加任何選項。
2. 用路徑指定任意字型檔：

```
python build.py examples/exam.md student.pdf --font ~/fonts/MyKai.ttf
```

3. 用系統已安裝的字型名稱：

```
python build.py examples/exam.md student.pdf --font "Noto Serif CJK TC"
```

說明：

1. 第 1 行：路徑方式，副檔名需為 `.ttf`、`.otf` 或 `.ttc`；`.ttc`（字型集合）尚未測試。
2. 第 2 行：名稱方式，字型需已安裝在系統上，名稱可用 `fc-list` 查詢。

注意事項：

- 專案不附任何字型檔，字型授權請自行確認。
- 預設的 `fonts/kaiu.ttf` 不存在時，會改用系統預設字型並在終端機提示。
- 指定的路徑不存在時，腳本會停止並顯示錯誤。

### 考卷大小

| `--paper` | 尺寸 |
| :--- | :--- |
| `A3` | 297 x 420 mm |
| `A4` | 210 x 297 mm |
| `A5` | 148 x 210 mm |
| `B4` | 250 x 353 mm |
| `B5` | 176 x 250 mm |
| `Letter` | 8.5 x 11 in |
| `Legal` | 8.5 x 14 in |
| `寬x高` | 自訂，單位 mm，例如 `270x390` |

以上為 CSS 紙張關鍵字（W3C, n.d.）。B4 是 ISO 規格，不一定等於各校實際使用的八開紙，需要時請用自訂尺寸並自行確認規格。

```
python build.py examples/exam.md student.pdf --paper B4 --landscape
python build.py examples/exam.md student.pdf --paper 270x390
```

說明：

1. 第 1 行：B4 橫向。
2. 第 2 行：自訂 270 x 390 mm。

### 字級

```
python build.py examples/exam.md student.pdf --font-size 12
```

說明：

1. 第 1 行：內文 12 pt；標題與頁尾依內文字級等比例縮放。


## 考卷格式

見 `examples/exam.md`（範例刻意從第 9 題開始，用來示範兩位數題號的對齊）。

- 標題與表頭放在 `>` 引用區塊內，會被畫成外框。
- 題號行兩種寫法皆可：`1. ( A ) 題幹`、`10.( A ) 題幹`。腳本自行解析題號行，版面由 CSS 以固定寬度對齊（題號 1.5 em、填答框 3 em），空格多寡不影響結果；兩位數題號省略空格，只是讓原稿看起來對齊。
- 括號可用半形 `( )` 或全形 `（ ）`，內容不限於 A 至 D，例如 `○`、`×`、`AB`。
- 題號之後、下一題或標題之前的所有內容（選項、圖片、說明文字）都屬於該題，會對齊在題幹第一個字的正下方，不必自己縮排。
- 題號以原稿所寫為準，不會自動重新編號；跨大題連續編號時，直接寫實際題號即可。
- 同一行的選項用全形空格隔開，因為連續的半形空格在 PDF 中會被合併。
- 圖片寬度統一由 `exam.css` 的 `img { max-width: 40%; }` 控制。


## 疑難排解

#### 中文字缺筆畫

WeasyPrint 預設會在嵌入字型時移除 hinting，標楷體 `kaiu.ttf` 會因此缺筆畫。本專案已固定啟用 `hinting`（WeasyPrint Contributors, 2026），不需另外設定。作者測試時，另外開啟完整嵌入字型（`full_fonts`）會讓 PDF 從約 150 KB 變成約 27.5 MB，且沒有必要。換用其他字型若仍有缺字，請先用 `pdffonts` 確認字型確實嵌入。

#### 學生版括號裡還看得到答案

題號行必須以「數字、句點、括號」開頭，才會被視為選擇題並在學生版清空括號。括號與空格的寫法不拘（`1.(A)`、`1. （ A ）` 都可以），但題號前若有空格或其他文字就不會被辨識。產生後請抽查：

```
pdftotext student.pdf - | head -n 30
```

說明：

1. 第 1 行：抽出學生版文字，確認題號後的括號是空的。

#### 圖片沒有出現

終端機會印出「找不到圖片：路徑」。路徑以 `.md` 檔所在資料夾為基準。

#### 字型沒有套用，變成預設字型

`@font-face` 載入失敗時不會報錯。請用 `pdffonts` 檢查 PDF 內嵌字型：

```
pdffonts student.pdf
```

說明：

1. 第 1 行：列出嵌入字型；若看不到你指定的字型，請確認檔案路徑與副檔名。


## 已知限制

- 尚未測試：`.ttc` 字型集合、整份考卷超過一頁的換頁效果、很大的字級搭配很窄的紙張。
- 三位數題號（100 題以上）會超出固定的題號寬度，對齊會跑掉。
- 沒有填答括號的題目（例如問答題）不會被視為選擇題，改由 Markdown 一般處理，沒有懸掛縮排。
- 題號行之後的說明文字，在遇到下一題或標題之前，都會被歸入前一題。


## 授權

本專案以 [MIT License](LICENSE) 授權，著作權 (c) 2026 HaveLight。

專案不包含任何字型檔，使用者自備的字型各有其授權，不受本授權涵蓋。


## 致謝

- [WeasyPrint](https://weasyprint.org/)
- [Python-Markdown](https://python-markdown.github.io/)


## 參考資料

W3C. (n.d.). *CSS Page Module Level 3*. https://www.w3.org/TR/css-page-3/

WeasyPrint Contributors. (2026). *API reference* (Version 70.0). WeasyPrint documentation. https://doc.courtbouillon.org/weasyprint/v70.0/api_reference.html
