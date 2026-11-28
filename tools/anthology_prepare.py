"""Create the ten selected, independently editable production briefs and SVGs."""
from pathlib import Path
import json,math,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SPECS=[
 (1,'whale-in-berth-six','Perspective builds a creature from industrial fragments. Vast scale and a single uncut reveal distinguish it from the intimate films.',
  'An abandoned dry dock of six gantries carries separate luminous whale fragments. The camera finds the one viewpoint that joins them, holds, then steps aside and loses the whale.',
  ['0–4 s: separate scuffs and gantries','4–8 s: the camera finds the whale','8–11 s: hold the complete animal','11–14 s: a lateral departure splits it again'],
  'Fourteen second cinematic instrumental. Low bowed double bass, muted brass harmonics, suspended oceanic strings. Industrial midnight harbor, solitary wonder. Build from near silence to one immense warm open chord at eight seconds, hold then dissolve. No vocals, no lyrics, no whale calls.',
  'Abandoned harbor atmosphere. Low sea swell, wind through steel cranes, a distant deep ship hull resonance. No voices or music.'),
 (3,'botanists-washing-line','Cyan blue, ivory botanical silhouettes and a tiny insect reveal give a graphic material transformation with a comic discovery.',
  'A miniature cyanotype sheet loses its pressed leaves to a gust. A wash turns the paper deep blue, leaving ivory plant impressions. A many-legged silhouette appears among the stems.',
  ['0–4 s: pressed leaves on pale paper','4–7 s: gust removes the specimens','7–11 s: blue rinse reveals the plant shadows','11–14 s: push toward the insect impression'],
  'Fourteen second instrumental miniature. Delicate prepared piano, brushed water percussion, airy marimba, clear spring sunlight. Curious first phrase, a brief rush at five seconds, luminous blue wash chord at nine seconds, tiny playful discovery at twelve. No voices, no lyrics.',
  'Close gentle paper flutter and one fresh gust through dry leaves, followed by a soft water rinse and one tiny insect scuttle. Natural quiet Foley, no music.'),
 (4,'sky-has-a-hinge','Pierced brass, engraved astronomical geometry and a star prediction combine precision with cosmic scale.',
  'A pierced astrolabe rotates against a midnight sky. A pointer marks the horizon before a single brilliant star rises into the same alignment. Brass and sky meet, then the pointer releases.',
  ['0–4 s: brass rings turn independently','4–8 s: pointer settles on the horizon','8–11 s: the predicted star rises into alignment','11–14 s: camera reveals the night beyond the instrument'],
  'Fourteen second instrumental celestial clockwork. Glass harmonica, bowed vibraphone, a low cello and warm analog air. Precise delicate pulses at first, stop the ticking at seven seconds, one bright high bell bloom at ten seconds, warm spacious ending. No singing, no speech.',
  'Fine brass astrolabe mechanism rotating with delicate ratchet clicks. A single gentle metal detent click, followed by quiet open night wind. No music or speech.'),
 (7,'dress-code-for-a-peacock','Angle-dependent emerald and violet color can produce a comic contradiction within sculptural fashion photography.',
  'A beetle-shell jacket stands motionless between two monochrome officials. As they orbit it, the jacket shifts from black to emerald and violet. One official pins a medal while the other drops an eviction arrow.',
  ['0–4 s: a black jacket passes inspection','4–9 s: observers orbit and brilliant color appears','9–12 s: medal and EXIT arrow arrive together','12–14 s: hold their contradictory verdicts'],
  'Fourteen second instrumental fashion comedy. Pizzicato bass, dry bass clarinet, brushed jazz snare, glistening harp. Stately and monochrome at first, a flamboyant color flourish at six seconds, two contradictory final accents at ten and eleven seconds, dry comic pause. No vocals.',
  'Polished shoes walking slowly around a mannequin on marble, subtle fabric rustle, two small ceremonial metal pin clicks. Dry theatrical Foley, no voice or music.'),
 (9,'his-excellency-the-spill','Surface marbling can turn portraiture into a fluid political joke, with a printed impression as an irreversible punchline.',
  'Floating pigment forms a grand ministerial profile in a gilded tray. A sneeze jolts the pigment into extra chins. The minister leans in, his caricature enlarges, and an ivory sheet lifts the incriminating print.',
  ['0–4 s: combed ceremonial portrait','4–7 s: sneeze distorts the floating profile','7–10 s: the offended minister leans over the tray','10–14 s: paper lifts the fixed caricature'],
  'Fourteen second instrumental court comedy. Harpsichord, bassoon, plucked strings. Exaggerated royal dignity, one sudden musical stumble at five seconds, mischievous descending bassoon at eight, final stamped chord at twelve. No singing, no speech.',
  'An exaggerated single adult sneeze, a small liquid splash, then wet paper peeling slowly from a shallow printmaking tray. No words, no music.'),
 (15,'last-passage-for-the-bronze','An illuminated cutaway turns casting into an interior chase between molten metal and the last trapped air pocket.',
  'Inside a stylized horse-shaped mold, luminous bronze advances around a trapped bubble. The bubble climbs the neck and escapes through the ear vent just before two metal fronts meet. The cutaway closes to reveal a bronze horse.',
  ['0–4 s: dark horse mold and first molten entry','4–9 s: bronze climbs the cavity behind the air','9–11 s: bubble escapes through the ear vent','11–14 s: the complete bronze horse emerges'],
  'Fourteen second instrumental foundry suspense. Low modular pulse, bowed metal, contrabass, rising strings. Heat and pressure build to eleven seconds, then one bright released overtone and a noble bronze chord. No vocals or speech.',
  'Hot metal flowing and soft furnace roar, increasing pressure, then a short clean air release through a small vent and a resonant cooling metal tick. No music or speech.'),
 (19,'seat-facing-backwards','A finite painted panorama can unfold into an emotionally striking absence, using warm mechanical intimacy instead of spectacle.',
  'A hand-cranked panorama box carries a painted railway past its window. At a station, the painted view runs out. A stitched edge passes and bare linen replaces the landscape. A solitary wooden viewer waits beside the empty window.',
  ['0–4 s: miniature painted railway moves','4–9 s: station passes and viewer leans closer','9–12 s: stitched end exposes blank linen','12–14 s: crank and viewer stop'],
  'Fourteen second instrumental elegy. Felt piano, muted cello, small harmonium. Tender hand-cranked motion, a remembered train journey. Let melody stop at ten seconds, leave a bare soft sustained chord and silence at the end. No voices.',
  'Quiet wooden panorama crank, soft fabric scroll moving over rollers, faint old railway rhythm in the distance. The crank slows and stops. No speech or music.'),
 (25,'second-tenant','A lenticular portrait can use viewpoint as a prison and a sliver of angle as an escape.',
  'A gilded family portrait switches between two approved poses as the camera passes. A cleaner rocks the frame slowly. Between those views, the smallest child steps out of the formal line and crosses the bottom edge of the picture.',
  ['0–4 s: approved family pose A','4–8 s: turn reveals approved pose B','8–11 s: a slow frame rock exposes the in-between view','11–14 s: the child steps out beyond the picture'],
  'Fourteen second instrumental uncanny liberation. Celesta, muted chamber strings, soft bass clarinet. Restrained repeated formal phrase, a suspended middle sliver at eight seconds, a curious free ascending melody at eleven. Warm ending. No speech or vocals.',
  'A heavy wooden picture frame gently creaks as it is tilted, cloth wiping glass, then three tiny clear wooden footsteps onto a table. No music or voices.'),
 (28,'letter-wide-enough-to-wear','A woven front and reverse can carry two different messages in one material, with the final turn revealing an intimate rebellion.',
  'A miniature loom weaves a regulation floral cuff. Copper and indigo threads cross in disciplined rows. The cuff turns over and reverse floats reveal BYE, before a second small wooden hand accepts it.',
  ['0–4 s: loom and prescribed flower pattern','4–9 s: warp and weft interlace','9–12 s: cuff rotates to show the reverse message','12–14 s: two hands meet at the cloth'],
  'Fourteen second instrumental textile farewell. Soft mechanical loom rhythm, plucked kora-like strings, breathy flute without voice, restrained cello. Orderly first half, warm bittersweet melody on the turn at ten seconds, tender final two notes. No singing or speech.',
  'Miniature wooden weaving loom. Clear shuttle strokes, delicate thread tension and soft cloth brushing over fingertips. Slow from steady work into one final gentle pull. No voice or music.'),
 (30,'water-for-last-balcony','A downhill ribbon connects miniature architecture into a collective action, ending with the bird carrying the movement uphill.',
  'In a terraced hillside, three households tilt their terracotta channels rather than keep the trickle. Water reaches a dry birdbath on the lowest balcony. A bird drinks, then flies back uphill past the opened gates.',
  ['0–4 s: trickle reaches first gate','4–9 s: three gates pass water downhill','9–11 s: lowest birdbath fills and bird drinks','11–14 s: bird returns uphill above the roofs'],
  'Fourteen second instrumental Mediterranean miniature. Nylon guitar harmonics, warm hand percussion, flute and chamber strings. A sparse trickle grows into an interconnected dancing phrase, a gentle pause for a bird at ten seconds, ascending airy final phrase. No voices.',
  'A small stream trickles through terracotta channels, three light clay tile taps, water filling a shallow stone birdbath, then one clear small bird chirp and soft wingbeats. No music or speech.')
]

def ellipse(cx,cy,rx,ry,n=48):return [(cx+rx*math.cos(i*2*math.pi/n),cy+ry*math.sin(i*2*math.pi/n)) for i in range(n)]

def profiles(cid):
    if cid==1:
        return {'whale':[(-5,.2),(-4.5,1.1),(-3.2,1.6),(-1,1.7),(1.3,1.2),(3.2,.6),(4,.6),(4.9,1.5),(4.65,.25),(5.2,-.55),(3.9,-.15),(3.1,-.25),(1,-.9),(-.5,-.9),(-1,-1.6),(-1.4,-.8),(-3.5,-.6),(-4.7,-.15),(-5,.2)],'eye':ellipse(-3.8,.45,.10,.10)}
    if cid==3:
        return {'leaf':[(-.25,0),(-1,1),(-.7,2),(0,3),(.7,2),(1,1),(.25,0),(-.25,0)],'bug':ellipse(0,0,.20,.65),'stem':[(0,-2),(0,0),(0,2.8)]}
    if cid==4:
        return {'ring':ellipse(0,0,3.2,3.2),'rete':[(-2.8,-.8),(-1.6,1.8),(-.2,1.2),(1.5,2.5),(2.8,.4),(1,-.2),(1.4,-2),(-.5,-1.3),(-2.8,-.8)],'pointer':[(-.10,-.2),(-.12,2.6),(0,3.1),(.12,2.6),(.10,-.2),(-.10,-.2)]}
    if cid==7:
        return {'jacket':[(-.5,2),(-1.5,1.6),(-1.8,-.5),(-1.1,-.7),(-.9,.4),(-.8,-2),(0,-1.7),(.8,-2),(.9,.4),(1.1,-.7),(1.8,-.5),(1.5,1.6),(.5,2),(0,1.3),(-.5,2)],'lapel':[(-.5,2),(-.8,.8),(0,1.3),(-.5,2)]}
    if cid==9:
        return {'profile':[(-1.5,-1.6),(-1.5,1.2),(-.8,2),(0,2.2),(.8,1.8),(1,1.1),(1.7,.8),(1.8,.5),(1,.3),(1.25,-.1),(.9,-.4),(.75,-1),(0,-1.3),(-.2,-2),(-1.5,-1.6)]}
    if cid==15:
        return {'horse':[(-3,-1),(-3,1),(-3.6,1.7),(-3.4,2),(-2.7,1.4),(-.5,1.5),(.6,3),(1.3,3.3),(1.1,4),(1.6,3.8),(2.1,3.5),(2.7,3.2),(2.8,2.8),(1.8,2.7),(1,1.2),(1.5,-1),(.9,-1),(0,.7),(-1,.5),(-1.4,-1),(-2,-1),(-1.7,.4),(-2.3,.3),(-2.6,-1),(-3,-1)],'vent':[(1.3,3.3),(1.4,4.5)]}
    if cid==19:
        return {'mountains':[(-9,-1),(-8,1),(-7,0),(-5,2),(-3,.5),(-1,2.2),(1,1),(3,1.7),(5,.3),(7,1),(9,-1)],'roof':[(-1,0),(0,1),(1,0)],'track':[(-10,-1.6),(10,-1.6)]}
    if cid==25:
        return {'child':[(-.3,-.7),(-.4,.3),(-.2,.7),(.2,.7),(.4,.3),(.3,-.7),(-.3,-.7)],'frame':[(-4,-3),(-4,3),(4,3),(4,-3),(-4,-3)]}
    if cid==28:
        return {'flower':[(math.cos(a)*(1+.35*math.cos(5*a)),math.sin(a)*(1+.35*math.cos(5*a))) for a in [i*2*math.pi/80 for i in range(81)]],'B':[(-1,0),(-1,2),(-.2,2),(.2,1.7),(.2,1.3),(-.2,1),(-1,1),(-.2,1),(.3,.7),(.3,.3),(-.2,0),(-1,0)],'Y':[(-1,2),(0,1),(1,2),(0,1),(0,0)],'E':[(1,2),(-1,2),(-1,0),(1,0),(-1,0),(-1,1),(0.7,1)]}
    return {'channel':[(-4,3),(-1.8,3),(-1.2,2),(1.5,2),(2,1),(-.8,1),(-1.3,0),(1.5,0),(2,-1)],'bird':[(-.7,0),(-.2,.2),(.1,.6),(.5,.5),(.8,.25),(.4,.15),(.3,-.2),(-.1,-.3),(-.7,0)],'wing':[(0,0),(-.8,1.1),(.5,.4),(0,0)]}

def main():
    board=json.loads((ROOT/'docs/concepts.json').read_text(encoding='utf8'))['concepts']
    catalog=[]
    for cid,slug,why,adaptation,beats,music,sfx in SPECS:
        concept=next(c for c in board if c['id']==cid)
        path=ROOT/'projects'/slug;path.mkdir(parents=True,exist_ok=True)
        for directory in ['receipts','previews','audio','source']:(path/directory).mkdir(exist_ok=True)
        plan={'concept_id':cid,'slug':slug,'title':concept['title'],'aat':concept['aat'],'original_pitch':concept['pitch'],
              'selection_justification':why,'adaptation':adaptation,'story_beats':beats,'duration':14,'fps':24,'width':1280,'height':720,
              'seed':1000+cid,'music_prompt':music,'sfx_prompt':sfx,'sfx_start':0,'sfx_gain':0.32,
              'key_times':[0,4,7,10,13.958333],'status':'source development','source_inputs':['source/design.svg','source/timeline.json']}
        (path/'source/timeline.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf8')
        svg=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':'-11 -7 22 14','width':'1280','height':'720'})
        ET.SubElement(svg,'title').text=concept['title']+' editable construction profiles'
        for role,points in profiles(cid).items():
            ET.SubElement(svg,'polyline',{'id':role,'data-role':role,'points':' '.join(f'{x:.5f},{-z:.5f}' for x,z in points),
                                       'fill':'none','stroke':'#d8ac61','stroke-width':'.035','stroke-linejoin':'round'})
        ET.indent(svg);ET.ElementTree(svg).write(path/'source/design.svg',encoding='utf-8',xml_declaration=True)
        (path/'README.md').write_text('# '+concept['title']+'\n\n'+adaptation+'\n\n'+why+'\n\nOriginal board concept #'+str(cid)+'. '+concept['aat']['term']+' is the Getty AAT vocabulary anchor. This short is an authored miniature adaptation, not a documentary demonstration.\n\n## Story beats\n\n'+'\n'.join('- '+b for b in beats)+'\n\n## Sources and rebuild\n\nThe Blender builder reads source/design.svg and source/timeline.json. Open source/scene.blend to edit the baked animation. The generation prompts, raw ElevenLabs music and sound effects, mix, previews and receipts are retained.\n\nBuild from this folder with Blender in background mode and source/build_scene.py. Production commands and verification receipts will be recorded as each stage completes.\n',encoding='utf8')
        catalog.append(plan)
    (ROOT/'production/anthology/selection.json').write_text(json.dumps(catalog,indent=2)+'\n',encoding='utf8')
    print('Prepared',len(catalog),'project briefs and editable SVG inputs.')

if __name__=='__main__':main()
