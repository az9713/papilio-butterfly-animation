import json
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).parent
html=root/'final-quality-excerpt-player.html'
html.write_text('<!doctype html><html><body style="margin:0;background:#101418"><video controls muted playsinline style="width:100%" src="final-quality-excerpt-3s.mp4"></video></body></html>',encoding='utf-8')
with sync_playwright() as p:
 browser=p.chromium.launch(channel='msedge')
 page=browser.new_page(viewport={'width':1280,'height':760})
 page.goto(html.as_uri())
 page.wait_for_function('document.querySelector("video").readyState>=2')
 page.locator('video').evaluate('v=>v.play()')
 page.wait_for_function('document.querySelector("video").ended',timeout=10000)
 report=page.locator('video').evaluate('v=>({ended:v.ended,duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error?.message??null})')
 assert report['ended'] and report['duration']==3 and report['width']==1920 and report['height']==1080 and report['error'] is None
 browser.close()
(root/'hd-excerpt-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
