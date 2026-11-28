from pathlib import Path
import base64
import json

root = Path(__file__).resolve().parent
files = ['The Tooth - reclaimed.mp4'] + [f'Pass-{n}.mp4' for n in range(1,4)]
sources = ['data:video/mp4;base64,'+base64.b64encode((root/name).read_bytes()).decode() for name in files]
template = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Tooth That Didn’t Sing — screening</title>
<style>*{box-sizing:border-box}body{margin:0;background:#161b1b;color:#f5e9d6;font:17px/1.4 system-ui,sans-serif}main{max-width:1000px;margin:3vh auto;padding:0 14px}h1{font:normal clamp(26px,5vw,46px)/1.12 Georgia,serif;margin:0 0 14px}video{width:100%;display:block;border-radius:5px;background:black}nav{display:flex;flex-wrap:wrap;gap:7px;margin:14px 0}button{cursor:pointer;border:1px solid #8c8171;padding:8px 13px;background:#262e2e;border-radius:4px;color:#f5e9d6;font:inherit}button[aria-pressed=true]{background:#efd7ae;color:#201910}p{margin:9px 0}button:focus-visible{outline:3px solid #a4d8de}</style>
<main><h1>The Tooth That Didn’t Sing</h1><video controls playsinline preload="auto" aria-label="Screening player"></video>
<nav aria-label="Choose screening"><button>Full film</button><button>The gap</button><button>The repair</button><button>The choice</button></nav>
<p aria-live="polite"></p></main><script>
const sources=SOURCE_ARRAY, video=document.querySelector('video'), buttons=[...document.querySelectorAll('button')];
const labels=['Full film · 16 seconds','Pass 1 · His note · 4.75 seconds','Pass 2 · Interrupted · 4.917 seconds','Pass 3 · Reclaimed · 6.333 seconds'];
function select(n,play){buttons.forEach((b,i)=>b.setAttribute('aria-pressed',i===n));document.querySelector('p').textContent=labels[n];
video.src=sources[n];video.load();if(play)video.play().catch(()=>{});}
buttons.forEach((b,n)=>b.onclick=()=>select(n,true));select(0,false);</script></html>"""
(root/'Screening.html').write_text(template.replace('SOURCE_ARRAY',json.dumps(sources)),encoding='utf-8')
