import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright

root=Path(__file__).parent
parser=argparse.ArgumentParser();parser.add_argument('stage');args=parser.parse_args()
if args.stage=='svg':
 with sync_playwright() as p:
  browser=p.chromium.launch(channel='msedge')
  page=browser.new_page(viewport={'width':400,'height':600},device_scale_factor=1)
  page.set_content('<style>html,body{margin:0;background:transparent}</style>'+(root/'wing-profiles.svg').read_text())
  page.locator('svg').screenshot(path=str(root/'wing-profiles.png'),omit_background=True)
  browser.close()
else:
 folder=root/'stages'/args.stage
 images=[(name,folder/f'{args.stage}-{name}.png') for name in ['hero','front','rear','side'] if (folder/f'{args.stage}-{name}.png').exists()]
 cols=2;rows=(len(images)+cols-1)//cols;w=960;h=540
 sheet=Image.new('RGB',(cols*w,rows*(h+42)),(19,23,27));draw=ImageDraw.Draw(sheet)
 font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
 for index,(name,path) in enumerate(images):
  with Image.open(path) as im:sheet.paste(im.convert('RGB').resize((w,h)),((index%cols)*w,(index//cols)*(h+42)+42))
  draw.text(((index%cols)*w+18,(index//cols)*(h+42)+5),f'{args.stage}  |  {name}',font=font,fill=(226,230,232))
 sheet.save(folder/f'{args.stage}-views.jpg',quality=93)
 print(folder/f'{args.stage}-views.jpg')
