# md-exam-pdf

English | [繁體中文](README.md)

Turn an exam paper written in plain Markdown into PDF, producing a student version (answer brackets left blank) and a teacher version (answers kept) in one go. Font, paper size, and font size are all configurable.


## Features

- Write the exam in plain Markdown; question numbers, figures, and choices stay together under each question
- One source, two PDFs: student version and teacher version (`--key`)
- Bring your own font: a font file path, or the name of a font installed on the system
- Paper sizes: A3, A4, A5, B4, B5, Letter, Legal, or a custom "WIDTHxHEIGHT" in mm, with optional landscape
- Default font size is 14 pt, adjustable
- Page footer "Page X of Y" in the output (the footer text itself is in Chinese: 第 X 頁/共 Y 頁)
- Missing images are reported in the terminal instead of silently dropped


## Tech Stack

Python 3, [Python-Markdown](https://python-markdown.github.io/), [WeasyPrint](https://weasyprint.org/)

Tested on: Termux (Python 3.14, WeasyPrint 70.0, Markdown 3.11).


## Project Layout

```
md-exam-pdf/
  build.py
  exam.css
  requirements.txt
  fonts/
  examples/
    exam.md
    img/
      fig1.png
```

- `build.py`: the conversion script
- `exam.css`: fixed styles for headings, the header box, and images; font, paper, and font size are generated from the options
- `fonts/`: where to put your own font file; its contents are not tracked by git
- `examples/`: a sample exam and a sample image


## Installation

WeasyPrint depends on Pango, so install the system packages first.

- macOS: `brew install pango`
- Ubuntu / Debian: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`
- Windows: install the GTK runtime as described in the WeasyPrint documentation
- Termux: see the commands below

Linux / macOS:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Notes:

1. Line 1: create a virtual environment.
2. Line 2: activate it (on Windows use `.venv\Scripts\activate`).
3. Line 3: install Markdown and WeasyPrint.

Termux:

```
pkg update && pkg upgrade -y
pkg install -y python clang make libffi pango libxml2 libxslt freetype libjpeg-turbo poppler
termux-setup-storage
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Notes:

1. Line 2: install Python, build tools, Pango and its dependencies; `poppler` provides `pdftotext` and `pdffonts` for checking output.
2. Line 3: grant shared storage access so fonts and images in the Downloads folder can be read.
3. Line 6: install Markdown, WeasyPrint, and their dependencies (including Pillow and cffi); this may take a few minutes depending on network and environment.


## Usage

```
python build.py examples/exam.md student.pdf
python build.py examples/exam.md key.pdf --key
```

Notes:

1. Line 1: build the student version with blank answer brackets.
2. Line 2: build the teacher version with answers kept.

Image paths are relative to the folder containing the `.md` file, so `img/fig1.png` in the sample means `examples/img/fig1.png`.

### Options

| Option | Default | Description |
| :--- | :--- | :--- |
| `--key` | off | Build the teacher version, keeping answers |
| `--font` | `fonts/kaiu.ttf` | Font file path, or the name of an installed font |
| `--font-size` | `14` | Body font size in pt, from 6 to 40 |
| `--paper` | `A4` | Paper size, see below |
| `--landscape` | off | Landscape orientation |

### Choosing a font

Pick one of three ways:

1. Put a font file in `fonts/` and name it `kaiu.ttf`; no option needed.
2. Point to any font file by path:

```
python build.py examples/exam.md student.pdf --font ~/fonts/MyKai.ttf
```

3. Use the name of a font installed on the system:

```
python build.py examples/exam.md student.pdf --font "Noto Serif CJK TC"
```

Notes:

1. Line 1: path mode; the extension must be `.ttf`, `.otf`, or `.ttc`. `.ttc` (font collections) is untested.
2. Line 2: name mode; the font must already be installed. Use `fc-list` to look up names.

Things to know:

- No font files are shipped with this project. Check the license of any font you use.
- If the default `fonts/kaiu.ttf` does not exist, the script falls back to the system default font and prints a notice.
- If a path you give does not exist, the script stops with an error.

### Paper size

| `--paper` | Size |
| :--- | :--- |
| `A3` | 297 x 420 mm |
| `A4` | 210 x 297 mm |
| `A5` | 148 x 210 mm |
| `B4` | 250 x 353 mm |
| `B5` | 176 x 250 mm |
| `Letter` | 8.5 x 11 in |
| `Legal` | 8.5 x 14 in |
| `WIDTHxHEIGHT` | Custom, in mm, e.g. `270x390` |

These are the CSS paper-size keywords (W3C, n.d.). B4 is the ISO size and may not match the paper your school actually uses; for that, use a custom size and verify the dimensions yourself.

```
python build.py examples/exam.md student.pdf --paper B4 --landscape
python build.py examples/exam.md student.pdf --paper 270x390
```

Notes:

1. Line 1: B4, landscape.
2. Line 2: custom 270 x 390 mm.

### Font size

```
python build.py examples/exam.md student.pdf --font-size 12
```

Notes:

1. Line 1: 12 pt body text; headings and the footer scale in proportion.


## Exam Format

See `examples/exam.md` (the sample deliberately starts at question 9 to show how two-digit numbers line up).

- Put the title and header in a `>` blockquote; it is drawn as a bordered box.
- Question lines can be written either way: `1. ( A ) question text` or `10.( A ) question text`. The script parses question lines itself and CSS lays them out at fixed widths (number 1.5 em, answer box 3 em), so the number of spaces does not change the result; dropping the space for two-digit numbers only makes the source look aligned.
- Brackets may be half-width `( )` or full-width `（ ）`, and may hold more than A to D, such as `○`, `×`, or `AB`.
- Everything after a question line, up to the next question or heading (choices, figures, notes), belongs to that question and is aligned directly under the first character of the question text; no manual indentation is needed.
- Question numbers are used as written and are never renumbered; to continue numbering across sections, just write the actual number.
- Separate choices on one line with full-width spaces, because runs of ordinary spaces collapse in the PDF.
- Image width is set globally by `img { max-width: 40%; }` in `exam.css`.


## Troubleshooting

#### Chinese characters are missing strokes

By default WeasyPrint strips hinting when embedding fonts, which makes the DFKai-SB font `kaiu.ttf` render with missing strokes. This project always enables `hinting` (WeasyPrint Contributors, 2026), so no setup is needed. In the author's tests, additionally enabling full font embedding (`full_fonts`) grew the PDF from about 150 KB to about 27.5 MB and was unnecessary. If another font still has missing glyphs, first confirm with `pdffonts` that the font is actually embedded.

#### The student version still shows answers in the brackets

A line is treated as a multiple-choice question, and its brackets are emptied in the student version, only if it starts with a number, a period, and then a bracket. Spacing and bracket style are flexible (`1.(A)` and `1. （ A ）` both work), but a line with leading spaces or other text before the number is not recognized. Spot-check after building:

```
pdftotext student.pdf - | head -n 30
```

Notes:

1. Line 1: extract the student version's text and confirm the brackets after the question numbers are empty.

#### An image does not appear

The terminal prints "找不到圖片：<path>" (image not found). Paths are relative to the folder containing the `.md` file.

#### The font was not applied and the default font is used

A failed `@font-face` load does not raise an error. Check the fonts embedded in the PDF:

```
pdffonts student.pdf
```

Notes:

1. Line 1: list embedded fonts; if the font you chose is missing, check the file path and extension.


## Known Limitations

- Not tested: `.ttc` font collections, page breaks across multi-page exams, and very large font sizes on narrow paper.
- Three-digit question numbers (100 or more) exceed the fixed number width and break the alignment.
- Questions without an answer bracket (for example short-answer questions) are not treated as multiple-choice; they go through ordinary Markdown handling and get no hanging indent.
- Text after a question line, until the next question or heading, is attributed to the previous question.


## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 HaveLight.

This project contains no font files; fonts you bring yourself carry their own licenses, which this license does not cover.


## Acknowledgements

- [WeasyPrint](https://weasyprint.org/)
- [Python-Markdown](https://python-markdown.github.io/)


## References

W3C. (n.d.). *CSS Page Module Level 3*. https://www.w3.org/TR/css-page-3/

WeasyPrint Contributors. (2026). *API reference* (Version 70.0). WeasyPrint documentation. https://doc.courtbouillon.org/weasyprint/v70.0/api_reference.html
