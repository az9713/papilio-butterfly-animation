"""Exercise the generated studio navigation, catalog, layouts and media."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import hashlib,json,threading,sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
class QuietServer(ThreadingHTTPServer):
    def handle_error(self,*args):
        if issubclass(sys.exc_info()[0],(ConnectionResetError,BrokenPipeError)):return
        super().handle_error(*args)

def main():
    server=QuietServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT/'_site')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_address[1]}/'
    report={'layouts':[],'catalog':{},'playback':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge')
        report['browser']=browser.version
        page=browser.new_page()
        for width in (1440,390):
            page.set_viewport_size({'width':width,'height':950})
            for path in ['','docs/getty-aat.html','docs/rubric.html','docs/workflow.html','docs/discussion.html','docs/concepts.html','projects/tooth/','projects/tooth/README.html','projects/butterfly/','projects/butterfly/development/']:
                response=page.goto(base+path,wait_until='domcontentloaded')
                assert response.status==200,path
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,path)
                report['layouts'].append({'width':width,'path':path,'passed':True})
            page.goto(base+'docs/concepts.html')
            assert page.locator('.concept:visible').count()==30
            page.locator('#front').select_option('1')
            assert page.locator('.concept:visible').count()==6
            page.locator('#experience').select_option('Elegy')
            assert page.locator('.concept:visible').count()==2
            report['catalog'][str(width)]={'all':30,'first_front':6,'first_front_elegy':2}
        page.set_viewport_size({'width':1440,'height':1000})
        page.goto(base)
        page.screenshot(path=str(ROOT/'.publication-work/studio-desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        page.screenshot(path=str(ROOT/'.publication-work/studio-mobile.png'),full_page=True)
        page.goto(base+'projects/tooth/')
        for i in range(4):
            page.locator('.player-tabs a').nth(i).click()
            page.wait_for_function('document.querySelector("video").currentTime>.1')
            page.wait_for_function('document.querySelector("video").ended',timeout=30000)
            state=page.locator('video').evaluate('v=>({duration:v.duration,ended:v.ended,muted:v.muted,error:v.error?.message??null})')
            assert state['ended'] and not state['muted'] and state['error'] is None
            report['playback'].append({'choice':i,**state})
        page.goto(base+'#sources')
        page.wait_for_url('**/projects/butterfly/#sources')
        report['legacy_anchor_redirect']=True
        browser.close()
    server.shutdown()
    report['passed']=True
    report['tooth_sha256']=hashlib.sha256((ROOT/'projects/tooth/film.mp4').read_bytes()).hexdigest()
    (ROOT/'publication/browser-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('PASS: twenty responsive layouts, catalog filters, four full sound-on clips and legacy anchor redirect.')

if __name__=='__main__':main()
