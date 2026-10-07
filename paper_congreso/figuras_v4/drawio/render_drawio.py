"""Renderiza XML de draw.io a PNG con el motor de draw.io (viewer-static) en Chromium, sin red."""
import asyncio, sys, pathlib
from playwright.async_api import async_playwright
D = pathlib.Path('/tmp/claude-0/dio')
PAGE = f'''<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0;background:#fff}}#c{{position:absolute;left:0;top:0;width:4000px;height:3000px}}</style></head>
<body><div id="c"></div><script src="file://{D}/viewer-static.min.js"></script></body></html>'''
async def main(pares, escala=3):
    (D / '_r.html').write_text(PAGE, encoding='utf-8')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for xml_path, png_path in pares:
            pg = await b.new_page(device_scale_factor=escala, viewport={'width': 2400, 'height': 1600})
            pg.on('pageerror', lambda e: print('E', e))
            await pg.goto(f'file://{D}/_r.html')
            xml = pathlib.Path(xml_path).read_text(encoding='utf-8')
            bb = await pg.evaluate("""async (x)=>{var el=document.getElementById('c'); var g=new Graph(el); g.setEnabled(false);
                var d=mxUtils.parseXml(x); new mxCodec(d).decode(d.documentElement, g.getModel());
                await document.fonts.ready; await new Promise(r=>setTimeout(r,600));
                var b=g.getGraphBounds(); return [b.x,b.y,b.width,b.height]}""", xml)
            m = 14
            await pg.screenshot(path=png_path, clip={'x': max(0, bb[0] - m), 'y': max(0, bb[1] - m), 'width': bb[2] + 2 * m, 'height': bb[3] + 2 * m})
            await pg.close(); print('ok', png_path, [round(v) for v in bb])
        await b.close()
if __name__ == '__main__':
    a = sys.argv[1:]; asyncio.run(main(list(zip(a[::2], a[1::2]))))
