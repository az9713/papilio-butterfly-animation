from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

root=Path(__file__).parent
items=[
 ('1  GPT Image initial reference','concept-v01.png'),
 ('2  GPT Image pedestal refinement','concept-v02.png'),
 ('3  Blender first framing review','stages/blockout-v01/blockout-v01-hero.png'),
 ('4  Blender corrected framing','stages/blockout-v02/blockout-v02-hero.png'),
 ('5  Blender constructed geometry','stages/geometry-v01/geometry-v01-hero.png'),
 ('6  Cycles first material review','stages/lookdev-v01/lookdev-v01-hero.png'),
 ('7  Cycles revised materials','stages/lookdev-v02/lookdev-v02-hero.png'),
 ('8  Cycles 1080p production pilot','stages/final-v01/final-v01-hero.png')
]
w=800;h=450;label=44
sheet=Image.new('RGB',(w*2,(h+label)*4),(15,19,23));draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
for i,(title,name) in enumerate(items):
 x=(i%2)*w;y=(i//2)*(h+label)
 draw.text((x+16,y+8),title,font=font,fill=(229,233,235))
 with Image.open(root/name) as image:
  image=image.convert('RGB');image.thumbnail((w,h))
  sheet.paste(image,(x+(w-image.width)//2,y+label+(h-image.height)//2))
sheet.save(root/'production-recap.jpg',quality=94)
print(root/'production-recap.jpg')
