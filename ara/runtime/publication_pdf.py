"""Safe Markdown to academic HTML to local Chromium PDF, with print checks."""
from __future__ import annotations

from html import escape
from hashlib import sha256
from pathlib import Path
import re

from markdown_it import MarkdownIt
from pypdf import PdfReader

from ara.runtime.cache import digest

CSS = '''
@page { size: A4; margin: 22mm 22mm 23mm; }
body { font-family: "Liberation Serif", "Times New Roman", serif; color: #222; font-size: 11.5pt; line-height: 1.44; margin: 0; }
main { max-width: 166mm; margin: auto; }
h1 { font-size: 23pt; line-height: 1.2; text-align: center; margin: 0 0 24pt; }
h2 { font-size: 14pt; margin: 20pt 0 8pt; break-after: avoid; }
h3 { font-size: 12pt; break-after: avoid; }
p { text-align: justify; orphans: 3; widows: 3; overflow-wrap: anywhere; }
figure { margin: 18pt 0; break-inside: avoid; }
figure svg { display: block; max-width: 100%; max-height: 215mm; width: 100%; height: auto; }
figcaption { font-size: 10pt; line-height: 1.3; margin-top: 7pt; text-align: left; }
a { color: #345b70; text-decoration: none; overflow-wrap: anywhere; }
'''


def paper_html(markdown, manifest, directory):
    renderer = MarkdownIt('commonmark', {'html': False})
    clean = re.sub(r'\[\[node:[^\]]+\]\]', '', markdown)
    items = {item['id']: item for item in manifest}
    used = []
    fragments = []
    for index, block in enumerate(re.split(r'(\{\{fig:[^}]+\}\})', clean)):
        if index % 2 == 0:
            fragments.append(renderer.render(block))
            continue
        id = block[6:-2]
        if id not in items or id in used:
            raise ValueError('unknown or duplicate figure reference')
        item = items[id]
        if item['file'] != id + '.svg' or not re.fullmatch('[a-z][a-z0-9-]*', id):
            raise ValueError('invalid figure path')
        svg = (directory / item['file']).read_text()
        if item.get('sha256') and digest(svg) != item['sha256']:
            raise ValueError('figure digest mismatch')
        import xml.etree.ElementTree as ET
        root = ET.fromstring(svg)
        allowed = {'svg','title','defs','marker','path','style','rect','text','g'}
        for node in root.iter():
            if node.tag.split('}')[-1] not in allowed or any(k.lower().startswith('on') or 'href' in k.lower() for k in node.attrib):
                raise ValueError('unsafe figure SVG')
            if node.tag.split('}')[-1] == 'style' and re.search(r'url\s*\(|@import',node.text or '', re.I):
                raise ValueError('unsafe figure style')
        used.append(id)
        fragments.append(f'<figure data-figure="{id}">{svg}<figcaption>Figure {len(used)}. {escape(item["caption"])}</figcaption></figure>')
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>Research paper</title><style>' + CSS + '</style><main>' + ''.join(fragments) + '</main></html>'


def _embedded_fonts(reader):
    fonts = {}
    for page in reader.pages:
        for font in page['/Resources'].get('/Font', {}).values():
            font = font.get_object()
            for child in font.get('/DescendantFonts', [font]):
                child = child.get_object()
                descriptor = child.get('/FontDescriptor')
                embedded = bool(descriptor and any(key in descriptor.get_object() for key in ('/FontFile','/FontFile2','/FontFile3')))
                fonts[str(child.get('/BaseFont', 'unknown'))] = embedded
    return fonts


def render_pdf(markdown, manifest, directory, output, *, chromium=None):
    from playwright.sync_api import sync_playwright
    chromium = Path(chromium or Path.home()/'.cache/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-linux64/chrome-headless-shell')
    if not chromium.is_file():
        raise ValueError('local Chromium headless shell is unavailable')
    html = paper_html(markdown, manifest, directory)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix('.html').write_text(html)
    expected = re.findall(r'\{\{fig:([^}]+)\}\}', markdown)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=str(chromium), headless=True, args=['--no-sandbox'])
        try:
            page = browser.new_page(viewport={'width': 794, 'height': 1123})
            page.route('**/*', lambda route: route.abort())
            page.set_content(html, wait_until='load')
            page.emulate_media(media='print')
            page.evaluate('document.fonts.ready')
            overflow = page.evaluate('''() => [...document.querySelectorAll('main *')].filter(e => {
                const r=e.getBoundingClientRect(), m=document.querySelector('main').getBoundingClientRect();
                return r.width && (r.left < m.left-1 || r.right > m.right+1);
            }).map(e => e.tagName)''')
            actual = page.locator('figure').evaluate_all('(es) => es.map(e => e.dataset.figure)')
            if overflow or actual != expected:
                raise ValueError('print overflow or figure inventory mismatch')
            page.pdf(path=str(output), format='A4', print_background=True, prefer_css_page_size=True,
                display_header_footer=True, header_template='<span></span>',
                footer_template='<div style="font-family:serif;font-size:9px;width:100%;text-align:center"><span class="pageNumber"></span></div>')
        finally:
            browser.close()
    reader = PdfReader(output)
    fonts = _embedded_fonts(reader)
    text = '\n'.join(p.extract_text() or '' for p in reader.pages)
    captions_present = all(f'Figure {i}.' in text for i in range(1, len(expected)+1))
    if not reader.pages or not fonts or not all(fonts.values()) or not captions_present:
        raise ValueError('PDF page/font/figure check failed')
    import pypdfium2 as pdfium
    glyph_overflow = []
    with pdfium.PdfDocument(output) as document:
        for number in range(len(document)):
            page = document[number]
            textpage = page.get_textpage()
            try:
                width, height = page.get_size()
                for index in range(textpage.count_chars()):
                    left,bottom,right,top = textpage.get_charbox(index)
                    if right > left and top > bottom and (left < 0 or bottom < 0 or right > width or top > height):
                        glyph_overflow.append(dict(page=number+1,character=index))
            finally:
                textpage.close()
                page.close()
    if glyph_overflow:
        raise ValueError('PDF glyphs overflow page bounds')
    return dict(pages=len(reader.pages), glyph_overflow=glyph_overflow, embedded_fonts=fonts, figures=len(expected),
                captions_present=captions_present, horizontal_overflow=overflow, pdf_sha256=sha256(output.read_bytes()).hexdigest())
