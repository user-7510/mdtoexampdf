import argparse, html, os, pathlib, re, sys
import markdown
from weasyprint import HTML

scriptDir = os.path.dirname(os.path.abspath(__file__))
paperNames = {"a3", "a4", "a5", "b4", "b5", "letter", "legal"}
fontExts = (".ttf", ".otf", ".ttc")

questionRe = re.compile(r"^(\d+)\.\s*[(（]\s*([^()（）]*?)\s*[)）]\s?(.*)$")
breakRe = re.compile(r"^(#{1,6}\s|>)")
mdExtensions = ["nl2br", "tables", "sane_lists"]

def mdToHtml(text):
    return markdown.markdown(text, extensions=mdExtensions)

def renderQuestion(num, answer, stem, bodyLines, showKey):
    shown = "( " + html.escape(answer) + " )" if showKey else "(   )"
    prefix = '<span class="no">' + num + '.</span><span class="ans">' + shown + "</span>"
    stemHtml = mdToHtml(stem)
    if stemHtml.startswith("<p>"):
        stemHtml = '<p class="stem">' + prefix + stemHtml[3:]
    else:
        stemHtml = '<p class="stem">' + prefix + "</p>" + stemHtml
    return '<div class="q">' + stemHtml + mdToHtml("\n".join(bodyLines)) + "</div>\n"

def renderBody(text, showKey):
    parts, chunk, question = [], [], None
    def flushChunk():
        nonlocal chunk
        if chunk:
            parts.append(mdToHtml("\n".join(chunk)))
        chunk = []
    def flushQuestion():
        nonlocal question
        if question:
            parts.append(renderQuestion(*question[0], question[1], showKey))
        question = None
    for line in text.splitlines():
        found = questionRe.match(line)
        if found:
            flushChunk()
            flushQuestion()
            question = (found.groups(), [])
        elif breakRe.match(line):
            flushQuestion()
            chunk.append(line)
        elif question:
            question[1].append(line.lstrip())
        else:
            chunk.append(line)
    flushChunk()
    flushQuestion()
    return "".join(parts)

def checkImages(text, baseDir):
    for path in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text):
        if not os.path.exists(os.path.join(baseDir, path)):
            print("找不到圖片：" + path, file=sys.stderr)

def parsePaper(value, landscape):
    custom = re.fullmatch(r"(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)", value.lower())
    if custom:
        w, h = float(custom.group(1)), float(custom.group(2))
        if landscape and w < h:
            w, h = h, w
        return "%gmm %gmm" % (w, h)
    if value.lower() in paperNames:
        return value.upper() + (" landscape" if landscape else "")
    sys.exit("不支援的紙張：%s（可用 A3 A4 A5 B4 B5 Letter Legal，或 寬x高 單位 mm，例如 270x390）" % value)

def resolveFont(value):
    if value is None:
        defaultPath = os.path.join(scriptDir, "fonts", "kaiu.ttf")
        if os.path.isfile(defaultPath):
            value = defaultPath
        else:
            print("找不到 fonts/kaiu.ttf，改用系統預設字型；可用 --font 指定字型", file=sys.stderr)
            return "", "serif"
    if os.path.isfile(value):
        uri = pathlib.Path(value).resolve().as_uri()
        return '@font-face { font-family: examFont; src: url("%s"); }' % uri, "examFont"
    if value.lower().endswith(fontExts) or os.sep in value:
        sys.exit("找不到字型檔：" + value)
    return "", '"%s", serif' % value

def buildCss(font, fontSize, paper):
    fontFace, family = resolveFont(font)
    footerSize = round(fontSize * 0.8, 1)
    return (
        fontFace + "\n"
        "@page { size: " + paper + "; margin: 15mm; @bottom-center { font-family: " + family + "; font-size: " + str(footerSize) + "pt; content: \"第\" counter(page) \"頁/共\" counter(pages) \"頁\"; } }\n"
        "body { font-family: " + family + "; font-size: " + str(fontSize) + "pt; line-height: 1.6; }\n"
    )

def buildPdf(src, out, showKey, font, fontSize, paper):
    baseDir = os.path.dirname(os.path.abspath(src))
    text = open(src, encoding="utf-8").read()
    checkImages(text, baseDir)
    page = "<style>" + buildCss(font, fontSize, paper) + "</style>" + renderBody(text, showKey)
    baseUrl = pathlib.Path(baseDir).as_uri() + "/"
    HTML(string=page, base_url=baseUrl).write_pdf(out, stylesheets=[os.path.join(scriptDir, "exam.css")], hinting=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Markdown 考卷轉 PDF")
    parser.add_argument("src")
    parser.add_argument("out")
    parser.add_argument("--key", action="store_true")
    parser.add_argument("--font", default=None)
    parser.add_argument("--font-size", dest="fontSize", type=float, default=14)
    parser.add_argument("--paper", default="A4")
    parser.add_argument("--landscape", action="store_true")
    args = parser.parse_args()
    if not 6 <= args.fontSize <= 40:
        sys.exit("--font-size 需介於 6 到 40（單位 pt）")
    buildPdf(args.src, args.out, args.key, args.font, args.fontSize, parsePaper(args.paper, args.landscape))
