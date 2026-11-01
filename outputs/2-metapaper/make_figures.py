"""Generate the v8 methods diagrams with fixed geometry and no random inputs."""
from pathlib import Path
from html import escape
import json,re
O=Path(__file__).resolve().parent;F=O/'figures';F.mkdir(exist_ok=True)
D=json.loads((O/'data.json').read_text())
TEAL='#255a67';INK='#24363c';GRAY='#849399';PALE='#edf4f5';RUST='#94613e';CREAM='#faf3eb'
class Diagram:
 def __init__(self,w,h):
  self.w=w;self.h=h;self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">', '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9" fill="'+TEAL+'"/></marker></defs>',f'<rect width="{w}" height="{h}" fill="white"/>'];self.texts=[]
 def text(self,x,y,lines,fs=18,color=INK,weight='normal',anchor='middle',leading=None):
  lines=lines.split('\n');leading=leading or fs*1.35
  self.parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{fs}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">')
  for i,line in enumerate(lines):self.parts.append(f'<tspan x="{x}" dy="{0 if i==0 else leading}">{escape(line)}</tspan>')
  self.parts.append('</text>');self.texts.extend(lines)
 def box(self,x,y,w,h,lines,fill=PALE,dashed=False,fs=18,color=TEAL):
  n=len(lines.split('\n'));lead=fs*1.35;assert n*lead<=h-10,(lines,h)
  self.parts.append(f'<g data-box="true"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{color}" stroke-width="1.6"'+(' stroke-dasharray="7 5"' if dashed else '')+'/>')
  self.text(x+w/2,y+h/2-(n-1)*lead/2+fs*.34,lines,fs=fs);self.parts.append('</g>')
 def arrow(self,points,dashed=False):
  path='M'+' L'.join(f'{x},{y}' for x,y in points)
  self.parts.append(f'<path d="{path}" fill="none" stroke="{TEAL}" stroke-width="2" marker-end="url(#arrow)"'+(' stroke-dasharray="7 5"' if dashed else '')+'/>')
 def rule(self,y):self.parts.append(f'<path d="M20,{y} H{self.w-20}" stroke="#cbd6da" stroke-width="1"/>')
 def save(self,id,caption,evidence,status='method diagram'):
  (F/(id+'.svg')).write_text('\n'.join(self.parts+['</svg>'])+'\n')
  return {'id':id,'file':'figures/'+id+'.svg','caption':caption,'evidence':evidence,'status':status,'width':self.w,'height':self.h,'labels':self.texts}
figs=[]
a=Diagram(900,470)
a.box(20,20,270,110,'L · licensed moves\nDeductive forms\nDefeasible schemes')
a.box(315,20,270,110,'T · frozen source theory\nFormulas and stance\nPassages and provenance')
a.box(610,20,270,110,'H · proposals\nTargets to investigate\nDisclosed premises')
for x in [155,450,745]:a.arrow([(x,130),(x,184)])
a.box(70,195,760,100,'Runtime checks the proposed move\nBank form · solver entailment · source authority · critical questions')
a.arrow([(290,295),(290,347)]);a.arrow([(610,295),(610,347)])
a.box(70,360,400,85,'Recorded argument\nLicensed steps and open obligations')
a.box(510,360,320,85,'Grounded paper\nStatus and citations retained')
a.arrow([(470,403),(503,403)])
figs.append(a.save('architecture','Models propose targets, interpretations and arguments. L supplies the permitted moves, T fixes source commitments, and any admitted H remains explicitly proposed. Runtime checks govern the argument; writing preserves its status.',['E1']))

a=Diagram(900,470)
for x,lines in [(20,'Papers\nLocal full texts\nSource identity'),(325,'Extraction\nClaims and dependencies\nPassage locations'),(630,'Construction\nFormulas and symbols\nRecorded stance')]:a.box(x,25,250,110,lines,fs=17)
a.arrow([(270,80),(317,80)]);a.arrow([(575,80),(622,80)])
a.arrow([(755,135),(755,205)])
a.box(630,215,250,105,'Alignment\nCross-paper comparisons\nProvenance retained',fs=17)
a.box(325,215,250,105,'Freeze T once\nAccepted theory\nFixed evidence boundary',fs=17)
a.arrow([(630,268),(583,268)])
a.box(20,215,250,105,'Search forks\nNew targets and requests\nSame frozen theory',fs=17)
a.arrow([(325,268),(278,268)])
a.rule(350)
a.box(95,375,710,72,'Consolidation or admitted H → new lifecycle and new freeze',fill=CREAM,fs=18,color=RUST)
a.text(450,165,'Source text, stance and page provenance travel with the commitment',fs=16)
figs.append(a.save('lifecycle','Construction turns grounded passages into a source theory with stance and provenance. Search forks preserve the freeze. Consolidation and hypothesis admission create a new lifecycle rather than rewriting the premises of an earlier experiment.',['E2']))

a=Diagram(900,470)
a.box(25,20,395,90,'Backward investigation\nWhat connection is missing?',fs=20)
a.box(480,20,395,90,'Forward investigation\nWhat follows jointly?',fs=20)
a.arrow([(222,110),(222,151)]);a.arrow([(677,110),(677,151)])
a.box(25,165,395,105,'Conflicts · stance tensions\nOpen problems · unclosed obligations\nCheck context and later literature',fs=17)
a.box(480,165,395,105,'Combine endorsed source premises\nInstantiate licensed moves\nTest each paper; reject padding',fs=17)
a.arrow([(222,270),(222,310),(450,310),(450,337)]);a.arrow([(677,270),(677,310),(450,310)])
a.box(130,350,640,95,'A precise candidate and its literature comparison\nThen search the thesis and its negation',fs=19)
figs.append(a.save('gaps','Backward investigation specifies the missing connection. Forward search tests joint consequences against individual papers. Both produce candidates for argument search and a separate, bounded comparison with the literature.',['E1','E3','E4']))

a=Diagram(900,480)
a.box(25,25,390,105,'Egan source leaf\nResponse to the\ncommunicative objection',fs=18)
a.box(485,25,390,105,'MacFarlane source leaf\nCriticism concerning\ngenuine disputes',fs=18)
a.arrow([(220,130),(220,174),(450,174),(450,202)]);a.arrow([(680,130),(680,174),(450,174)])
a.box(215,215,470,110,'Relativism better supported than\nSolipsistic Contextualism\nSign inference accepted; route OPEN',fs=19)
a.box(25,365,390,80,'Critical question 1\nSupported',fs=18)
a.box(485,365,390,80,'Critical question 2\nUnsupported: obligation remains',fill=CREAM,dashed=True,fs=18,color=RUST)
a.arrow([(330,325),(220,357)]);a.arrow([(570,325),(680,357)],dashed=True)
figs.append(a.save('route','An actual partial route, distinct from the safety–retraction proposals: two source leaves support one accepted sign inference, while an unsupported critical question keeps the target OPEN. The recorded route has three argument nodes; the lower boxes display obligations attached to its scheme.',['E4'],'recorded partial OPEN route'))

a=Diagram(900,500)
a.box(25,25,395,105,'Conditional derivation\nSource theory T + disclosed H\nA new lifecycle freezes both',fs=19)
a.box(480,25,395,105,'Proposal paper\nState and defend the bridge\nKeep its proposed status',fs=19)
a.arrow([(222,130),(222,187)]);a.arrow([(677,130),(677,187)])
a.box(25,200,395,110,'Licensed search\nSource support remains necessary\nH receives no paper credit',fs=18)
a.box(480,200,395,110,'Philosophical argument\nReasons, objections and replies\nFaithful attributed source claims',fs=18)
a.arrow([(222,310),(222,367)]);a.arrow([(677,310),(677,367)])
a.box(25,380,395,90,'Result, if obtained:\nGiven T and H, the route supports C',fs=18)
a.box(480,380,395,90,'Result, if accepted:\nAn audited argument for the proposal',fs=18)
figs.append(a.save('hypothesis','Two ways to develop a missing bridge. An H-based derivation remains conditional on its admitted premise. Proposal mode supports a paper arguing for the bridge without claiming a completed mechanical derivation. These are different result types.',['E5','E6']))

a=Diagram(900,485)
a.box(25,20,395,90,'Route or authorized proposal\nSource evidence and result status',fs=19)
a.box(480,20,395,90,'Outline and sectioned writing\nExplain the argument and objections',fs=19)
a.arrow([(420,65),(472,65)]);a.arrow([(677,110),(677,162)])
a.box(480,175,395,110,'Typed sentence audit\nSource claim · step · proposal\nFraming · objection · reply',fs=18)
a.box(25,175,395,110,'Local source verification\nIdentity · locator · quotation\nAttributed claim support',fs=18)
a.arrow([(480,230),(428,230)])
a.arrow([(222,285),(222,335),(450,335),(450,362)]);a.arrow([(677,285),(677,335),(450,335)])
a.box(105,375,690,90,'Fresh k = 3 audit union and delivery decision\nEditing preserves evidence; changed meaning returns to audit',fs=19)
figs.append(a.save('publication','The paper inherits its candidate’s mode and evidence. Typed auditing, local citation verification and fresh repeated audits address different responsibilities. Editing does not transfer an accepted verdict to unsupported new wording.',['E6','E7','E8']))

a=Diagram(900,650)
a.text(450,25,'RECORDED EXACT-T2 SEARCH',fs=17,weight='bold')
a.box(80,45,330,75,'T2: obligation iff safety failure\nOne OPEN root; no inference',fs=17)
a.box(490,45,330,75,'Negation of T2\nOne OPEN root; no inference',fs=17)
a.rule(145);a.text(450,175,'PROPOSED CONDITIONAL EXPANSION · NOT AN ADMITTED ROUTE',fs=17,weight='bold')
a.box(300,205,300,70,'T2: R ↔ S',dashed=True,fill=CREAM,fs=23,color=RUST)
a.box(90,325,330,75,'Sufficient direction: S → R',dashed=True,fill=CREAM,fs=20,color=RUST)
a.box(490,325,330,75,'Necessary direction: R → S',dashed=True,fill=CREAM,fs=20,color=RUST)
a.arrow([(255,325),(355,283)],dashed=True);a.arrow([(655,325),(545,283)],dashed=True)
a.box(20,455,255,85,'Proposed H_suff\nS → F',dashed=True,fill=CREAM,fs=21,color=RUST)
a.box(315,455,255,85,'Retraction Rule\nF → R',fs=21)
a.box(610,455,270,85,'H_nec: exhaustiveness\nof retraction grounds',dashed=True,fill=CREAM,fs=18,color=RUST)
a.arrow([(147,455),(220,408)],dashed=True);a.arrow([(442,455),(300,408)],dashed=True);a.arrow([(745,455),(690,408)],dashed=True)
a.text(450,585,'S: specified safety failure · F: the Retraction Rule’s antecedent',fs=17)
a.text(450,613,'R: obligation to retract the same assertion, with use fixed',fs=17)
figs.append(a.save('worked-example','The upper panel shows the actual exact-T2 routes. The lower panel is an explanatory schema for a possible combined argument, not accepted formulas or a completed proof. Beddor–Goldstein supplies the safety account used to specify S; the proposed H premises supply additional connections. Dashed edges denote proposed dependencies. The delivered exact-T2 paper instead argues for a direct safety-to-obligation bridge in proposal mode.',['E3','E4','E5','E7'],'actual OPEN roots plus explicitly uncompleted conditional design'))
ids=re.findall(r'\{\{fig:([^}]+)\}\}',(O/'metapaper.md').read_text());assert len(ids)==len(set(ids))==7
byid={f['id']:f for f in figs};D['figures']=[byid[id] for id in ids]
D['numerical_claim_index']=[];section=''
for line in (O/'metapaper.md').read_text().splitlines():
 if line.startswith('#'):section=line
 if re.search(r'\d',line):D['numerical_claim_index'].append({'section':section,'statement':line,'citations':re.findall(r'E\d+',line)})
(O/'data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');(F/'manifest.json').write_text(json.dumps(D['figures'],ensure_ascii=False,indent=2)+'\n')
print(f'{len(figs)} deterministic SVG diagrams generated')
