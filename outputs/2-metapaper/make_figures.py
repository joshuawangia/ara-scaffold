"""Deterministic v6 figures. Historical panels retain their scoped source data."""
from pathlib import Path
import json, subprocess, sys, textwrap
O=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(O/'historical_figures.py')],check=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
D=json.loads((O/'data.json').read_text());F=O/'figures';figures={x['id']:x for x in D['figures']}
plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':10,'svg.fonttype':'none','svg.hashsalt':'ara-meta-v6','axes.spines.top':False,'axes.spines.right':False})
ACC='#28677e';DARK='#30373c';GRAY='#aeb5ba';PALE='#edf1f3'
def save(fig,id,caption,data):
 fig.savefig(F/(id+'.svg'),bbox_inches='tight',metadata={'Date':None,'Creator':'Deterministic v6 figure from recorded evidence'})
 plt.close(fig);figures[id]={'id':id,'file':'figures/'+id+'.svg','caption':caption,'data':data}
def canvas(h=6,w=9):
 fig,ax=plt.subplots(figsize=(w,h));ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off');return fig,ax
def box(ax,x,y,w,h,s,accent=False,dashed=False,fs=10):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.4,rounding_size=.8',facecolor=PALE if accent else 'white',edgecolor=ACC if accent else GRAY,linestyle='--' if dashed else '-',lw=1.1))
 ax.text(x+w/2,y+h/2,s,ha='center',va='center',fontsize=fs,color=DARK)
def arrow(ax,a,b,dashed=False):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,color=ACC,lw=1.1,linestyle='--' if dashed else '-'))
def matrix(id,headers,rows,caption,widths=None,fontsize=11):
 fig,ax=plt.subplots(figsize=(8.4,max(2.2,len(rows)*.60+.6)));ax.axis('off')
 widths=widths or [1/len(headers)]*len(headers)
 wrapped=[[textwrap.fill(str(v),max(10,int(60*widths[i]))) for i,v in enumerate(row)] for row in rows]
 t=ax.table(cellText=wrapped,colLabels=headers,colWidths=widths,cellLoc='left',loc='center',bbox=[0,0,1,1]);t.auto_set_font_size(False);t.set_fontsize(fontsize)
 for (r,c),cell in t.get_celld().items():
  cell.set_edgecolor(GRAY);cell.set_linewidth(.5);cell.set_facecolor(PALE if r==0 else 'white');cell.set_height((.75 if r==0 else max(1,len(wrapped[r-1][c].splitlines()))*.50+.6)/(len(rows)*2.6+2))
 # Equalize each row to the maximum wrapped cell height.
 for r in range(len(rows)+1):
  height=max(t[r,c].get_height() for c in range(len(headers)))
  for c in range(len(headers)):t[r,c].set_height(height)
 save(fig,id,caption,{'headers':headers,'rows':rows})
# Architecture: three independent authorities and two paper paths.
fig,ax=canvas(6.7)
for x,s in [(2,'L: licensed move bank\nDeductive forms + Z3\nDefeasible schemes + CQs'),(36,'T: source theory\nCited, stance-bound\nOne freeze per lifecycle'),(70,'H: proposals\nTargets / cuts / premises\nNo source-paper credit')]:box(ax,x,77,28,19,s,True)
box(ax,18,48,64,16,'Runtime: counted requests, immutable IDs, isolated providers\nModel proposes → schema + provenance + full-T gates decide')
for x in [16,50,84]:arrow(ax,(x,77),(50,64))
box(ax,2,23,44,14,'Licensed polarity search\nCLOSED / OPEN / conditional on H',True)
box(ax,54,23,44,14,'Proposal writing\nBridge defended, not mechanically derived',dashed=True)
arrow(ax,(38,48),(24,37));arrow(ax,(64,48),(76,37))
box(ax,9,1,82,12,'Candidate → typed audit → local citations → k=3 union → verified export\nOptional polish has its own gates → PDF → operator selection',True,fs=9)
arrow(ax,(24,23),(36,13));arrow(ax,(76,23),(64,13))
save(fig,'architecture','Authority is separated at each boundary. Proposal mode has its own authorization and disclosure; it is not an alternate way to claim a CLOSED route. PDF production follows the status of its input.',{'source_refs':['R3','R52','R55','R57']})
# Lifecycle snake, with explicitly separate reuse paths.
fig,ax=canvas(6)
stages=['Extract\nimmutable evidence','Construct\nstance + provenance','Consolidate (opt-in)\nnew formula history','Align\nmodel judgments','Freeze once\nT + disclosed H','Fork\nauthenticated T','Target\nper-paper gates','Search ±\nlicenses + CQs','Candidate\nroute or proposal','Audit / verify\nthen PDF']
positions=[(2,77),(36,77),(70,77),(70,53),(36,53),(2,53),(2,29),(36,29),(70,29),(36,4)]
for (x,y),s in zip(positions,stages):box(ax,x,y,28,16,s,accent=s.startswith(('Freeze','Audit')))
for i in range(9):
 x,y=positions[i];xx,yy=positions[i+1]
 if y==yy:arrow(ax,(x+28 if xx>x else x,y+8),(xx if xx>x else xx+28,yy+8))
 else:arrow(ax,(x+14,y),(xx+14,yy+16))
save(fig,'lifecycle','Consolidation or H admission reuses completed construction in a new lifecycle before its own freeze. A search fork instead preserves the existing freeze. Valid completed stages survive later failure; neither path silently edits the source experiment.',{'stages':stages,'sources':['R18','R50','R52']})
# Funnel: distinct lineages and stops.
rows=[['Original corpus','53 chosen → 26 PDFs → 5,659 items','363 quarantined → 5,296 eligible'],['Gap1','74 windows → 159 commitments / 22 papers','STOP: echoed ID, alignment 36/150'],['Gap1r','150 accepted judgments → frozen T 160','STOP: target input 311,785 > 200,000 bound'],['A / B / C forks','27 / 20 / 3 targets → 100 routes','100 OPEN; one partial B inference'],['Gap2','3/13 accepted windows → 57 commitments','STOP before freeze; required safety lost'],['Gap3 → gap3p','243 commitments → 23 targets → 46 routes','46 OPEN; zero inferences; basis omitted'],['Gap3v r20','22/30 batches → 181 partial commitments','STOP batch 23; no freeze / after metric'],['Gap3h','243-source reuse plan accepted','STOP before H formalization; no live route'],['Proposal output','B/2 and T2 original k=3 [0,0,0]','Two verified original PDFs; no derived claim']]
fig,ax=canvas(8.4,8.4)
for j,row in enumerate(rows):
 y=91-j*10
 box(ax,0,y,17,8,textwrap.fill(row[0],16),True,fs=10)
 box(ax,21,y,38,8,textwrap.fill(row[1],36),fs=9.5)
 box(ax,64,y,35,8,textwrap.fill(row[2],32),accent=True,fs=9.5)
 arrow(ax,(17,y+4),(21,y+4));arrow(ax,(59,y+4),(64,y+4))
save(fig,'funnel','Branched gate funnel: recorded progression ends at an explicit stop or output. Rows are distinct lineages, not successive denominators. Proposal PDFs are not CLOSED gap derivations.',{'rows':rows,'sources':['R16','R18','R28','R35','R51','R53','R56','R61']})
# Vocabulary counts and absent after-values.
v=D['v6'];fig,axes=plt.subplots(1,2,figsize=(9,3.3));names=['gap1r freeze','gap3 freeze','gap4a pre-alignment'];totals=[160,243,308];atoms=[141,212,263]
for i,(a,t) in enumerate(zip(atoms,totals)):
 axes[0].barh(i,a,color=GRAY);axes[0].barh(i,t-a,left=a,color=ACC);axes[0].text(t+4,i,f'{a}/{t}',va='center',fontsize=9)
axes[0].set_yticks(range(3),names);axes[0].invert_yaxis();axes[0].set_xlim(0,390);axes[0].set_title('Bare atoms / all commitments');axes[0].set_xlabel('Grey: atoms   Accent: structured syntax')
axes[1].set(xlim=(0,3),ylim=(-.6,3.3));axes[1].set_yticks(range(3),names);axes[1].invert_yaxis();axes[1].set_xticks([0,1,2]);axes[1].set_title('Symbols shared across source papers')
for i in range(3):axes[1].plot(0,i,'o',color=ACC);axes[1].text(.13,i,'0 source-shared',va='center',fontsize=9)
axes[1].text(.05,2.8,'Consolidation after: unavailable\nNo completed replacement freeze',fontsize=9,color=ACC)
fig.tight_layout();save(fig,'vocabulary-after','No before/after gain is established. Gap1r has two bridge-linked symbols but zero source-only sharing. Gap4a is completed construction before alignment, not a frozen after-treatment. Structured syntax and source-independent names do not establish faithful shared semantics.',{'runs':names,'commitments':totals,'atoms':atoms,'shared_source_symbols':[0,0,0],'consolidation_after':None,'sources':['R46','R48','R51','R60']})
# Token ranges: only same-stage replay comparison shares causal identity.
fig,axes=plt.subplots(1,2,figsize=(9,3.4))
labels=['Gap1r refused input','A actual input estimate','B actual input estimate','Old search replay upper','Packed replay upper'];vals=[311785,105722,312084,733092,49558]
axes[0].barh(labels,[x/1000 for x in vals],color=[GRAY,ACC,GRAY,GRAY,ACC]);axes[0].invert_yaxis();axes[0].set_xlabel('Estimated input tokens (thousands)');axes[0].set_xlim(0,850)
for i,x in enumerate(vals):axes[0].text(x/1000+8,i,f'{x/1000:.1f}k',va='center',fontsize=8)
axes[1].bar(['Before: maps','Replay: maps','Replay: cuts'],[0,46,92],color=[GRAY,ACC,ACC]);axes[1].set_ylim(0,110);axes[1].set_ylabel('Requests with complete declared basis');axes[1].tick_params(axis='x',labelsize=8)
for i,s in enumerate(['0/46','46/46','92/92']):axes[1].text(i,[0,46,92][i]+3,s,ha='center',fontsize=9)
fig.tight_layout();save(fig,'packing','Token reductions and evidence coverage are different achievements. Left: input estimates exclude the 16,384 output allowance, with distinct experiments explicitly named; old-versus-packed search is a replay comparison. Right: packing2 offline replay repairs full basis visibility. No later live derivation is inferred.',{'input_labels':labels,'input_tokens':vals,'complete_basis':[0,46,92],'denominators':[46,46,92],'sources':['R18','R28','R53','R54']})
# Proposal family tree.
fig,ax=canvas(7.2)
box(ax,20,84,60,12,'Frozen gap1r T → target proposals / external T2\nAll corresponding polarity routes remain OPEN',True)
props=[('B/1','ARA-proposed; near T2 necessity\nChanged subject / normative force','[5,4,0] → union 6\nREFUSED'),('B/2','ARA-proposed; near T2 necessity\nWarranted withdrawal ≠ obligation','Original [0,0,0]\nVerified original PDF'),('A/3','ARA-proposed; thematic T5\nPartially anticipated comparison','[4,7,4] → union 9\nREFUSED'),('T2','eps2-proposed exact iff\nNot found in bounded dossier','Original [0,0,0]\nVerified original PDF')]
for i,(title,meaning,result) in enumerate(props):
 y=63-i*18;box(ax,2,y,12,12,title,True);box(ax,19,y,45,12,meaning,fs=9);box(ax,70,y,28,12,result,accent='PDF' in result,fs=9);arrow(ax,(14,y+6),(19,y+6));arrow(ax,(64,y+6),(70,y+6))
arrow(ax,(50,84),(50,77));save(fig,'proposal-routes','Four proposal candidates retain distinct origins and bounded literature comparisons. B/1 and B/2 only partially match exact T2; A/3 is thematic T5. The T2 sufficiency direction alone is closest to partially anticipated T1. Clean original writer gates do not imply polished acceptance or mechanical derivation.',{'proposals':props,'sources':['R28','R38','R55','R56']})
# Central requested combination: explicitly not a proof.
fig,ax=canvas(7.2)
box(ax,2,77,44,18,'Frozen source: Beddor–Goldstein\nInformation-sensitive safety\nWhole-claim atom',True)
box(ax,54,77,44,18,'Frozen source: MacFarlane\nRetraction Rule\nWhole-claim atom',True)
box(ax,2,48,44,17,'Proposed H_suff\nSafety failure → norm antecedent\nNot a source endorsement',dashed=True,fs=9)
box(ax,54,48,44,17,'Proposed H_nec\nNecessity / exhaustiveness\nNot reversal of a sufficient rule',dashed=True,fs=9)
for x in [24,76]:arrow(ax,(x,77),(x,65),True)
box(ax,10,24,80,14,'STOP BEFORE FORMALIZATION · 22:29:29 UTC\nFaithful H over existing whole-claim atoms not established',True,fs=10)
for x in [24,76]:arrow(ax,(x,48),(50,38),True)
box(ax,15,1,70,12,'Intended: conditional T2, only if native licensing succeeds\n0 H admitted · no new freeze · 0 live calls / derived routes',dashed=True,fs=9)
arrow(ax,(50,24),(50,13),True)
save(fig,'combined-route','Featured gap3 + T2 conditional design, not an executed derivation. Source reuse is verified; the worker semantic preflight blocks H before model or solver execution. Dashed edges are intended dependencies, not bank licenses. H must be defended and source meanings preserved. A completed route was unavailable at the inspected checkpoint.',D['v6']['gap3h'])
# Audit graph no conflation different stages.
fig,axes=plt.subplots(1,4,figsize=(10,3.2))
series=[('Identical prompt\nR5 route 1',[44,0],['sample 1','sample 2']),('B/1 final gate',[5,4,0],['1','2','3']),('T2 polish gates',[7,14,13,0,0,0],['a1','a2','a3','b1','b2','b3']),('T2 title-only final',[9,6,0],['1','2','3'])]
for ax,(title,y,x) in zip(axes,series):
 ax.bar(x,y,color=[GRAY if i==0 else ACC for i in range(len(y))]);ax.set_title(title,fontsize=10);ax.set_ylim(0,max(y)*1.25+2);ax.set_ylabel('Flags',fontsize=9)
 for i,n in enumerate(y):ax.text(i,n+.7,str(n),ha='center',fontsize=9)
fig.tight_layout();save(fig,'audit-flags','These are separate observed audits, not a quality trend or independent trials. R5 changed 44→0 without text repair. B/1 still refused with six union findings despite a clean sample. T2 had a clean earlier polished gate but failed quotation fidelity; after exact title repair its final [9,6,0] union refused again. The delivered PDF remains its verified original.',{'series':series,'sources':['R20','R55','R56','R66']})
# Candidate publication pipeline.
fig,ax=canvas(6)
for x,s in [(2,'CLOSED route\nor OPEN with inference'),(36,'Authorized proposal\nBridge argued as proposal'),(70,'Analysis of outputs\nNo native derived claim')]:box(ax,x,78,28,18,s,True,fs=9)
box(ax,8,49,56,15,'Writer → typed audit → local citation verification\nFresh k=3 union + persistent adverse history',True,fs=9)
arrow(ax,(16,78),(25,64));arrow(ax,(50,78),(47,64))
box(ax,8,25,56,13,'Verified export → optional polish + own gates\nCarry-over / inline repair → final verification',fs=9);arrow(ax,(36,49),(36,38))
box(ax,72,25,26,13,'Analysis PDF\nSeparate status',fs=9);arrow(ax,(84,78),(85,38))
box(ax,8,2,90,13,'Delivered PDFs: B/2 original + T2 original + fallback analysis\nRefused revisions remain refused · submission selection belongs to operator',True,fs=9)
arrow(ax,(36,25),(40,15));arrow(ax,(85,25),(77,15))
save(fig,'candidate-pipeline','Distinct entry paths and output claims. The current two proposal PDFs reproduce verified originals. Native generation/audit was not claimed for meta’s fallback analysis. A refused polished revision is never replaced in the ledger with a rendering pass.',{'sources':['R33','R55','R56','R57']})
# Review and timeline.
matrix('review-ledger',['Boundary','Failure found','Disposition / limit'],[
['Identity','S12: fixture drift; gap1 echoed IDs','Runtime binding / resume; semantics separate'],['Output evidence','NP-F1–3; R2-F1/F2; DLV-F1','Screening, titles, occurrence IDs, citations and retry dissent retained'],['Novelty','R28-F1/F2: padding / inconsistent union','Closed in reviewed xi29; real novelty still unproved'],['Context','S13-F1/F2: stage/provider mismatch','Normalized before cache/admission'],['H disclosure','X32-F1–3: padding / negation / hidden H','Runtime disclosure; gap3h not derived'],['Retrieval','PACK-F1/F2: missing vocabulary / bases','Packing2 offline basis coverage restored'],['Proof quality','PACK-F3; N4-F1: unrelated failure','Pass retracted; causal controls repaired'],['Inline output','Combined 3a365a5: 6/6 seam tests','Reviewed; live publication verdict pending']],
'Review findings are attached to exact revisions and exercised boundaries. “Closed” refers to a software finding, not to an argument route or philosophical question.',[.17,.40,.43])
matrix('iterations',['Concept / iteration','Observed failure','Response / outcome'],[
['21–25 Oct: extraction','Small summaries; malformed ranges/inferences','Rich evidence, grounding, disclosed omissions'],['Construction bounds','86k singleton / 70k; false 70–90-token claim','Window metadata, bounded closure; ~233-token correction'],['29 Oct: gap1 / r12','74 windows; alignment ID mismatch at 36/150','ID-free recovery → frozen T160; target admission then stops'],['Novelty / R28','Whole-T exclusion; padding / inconsistent union','Per-paper gate; zero qualifying real-source census'],['29–30 Oct: forks','141/160 atoms; zero source sharing','100 OPEN, only one partial B sign inference'],['30 Oct: gap3 / packing','243 commitments; admission / unknown CLI exits','Gap3p fits but omits bases; 46 OPEN'],['30 Oct: r17 / gap4a','Prompt delivered; 0/292 source-shared symbols','Consolidation added; alignment still pending'],['30 Oct: r18–r21','Echoed IDs, attribution, cardinality regression','r19 binding; r20 22/30 batches; r21 pending'],['Writing / audits','44→0; bibliography zero; refused polish','k=3 union, local citations, verified originals'],['Review / operation','Basis omission, unrelated mutation failure, empty jobs','Packing2, corrected proof, native ten-job pause']],
'Iterations grouped by the core mechanism they changed. The alignment refusal, cardinality stop, invalid pass retraction and pending repairs remain visible; this is not a monotonic success timeline.',[.20,.40,.40])
# Compact credit architecture, exhaustive names in data and paper.
groups=[['Sources / extraction','alpha, beta, epsilon, gamma, delta, theta, eta, iota, mu'],['Pilots / source review','zeta, kappa, lambda, omicron, rho, tau, upsilon'],['Construction / search','sigma, xi, xi2, omega, fwd; phi, psi, chi'],['Integration / independent review','kappa2, kappa3, kappa4, kappa5; rho2, rho3, tau2, upsilon2, phi2, omicron3, chi2, lambda2'],['Writing / publication / literature','nu, nu4, pi, pi3, eps2, meta'],['Operations / direction','janitor; orchestrator; anonymised human operator']]
matrix('credits',['Contribution cluster','Recorded identifiers'],groups,'Compact role map; §10 retains individual histories and evidence paths for all 43 workers plus the orchestrator. Agent identifiers are credits, not human identities. Model/version uncertainty is retained.',[.28,.72],9)
# Complete route atlas: target label branches to +/- OPEN.
for arm,rows in D['v6']['route_atlas'].items():
 for part,start in enumerate(range(0,len(rows),14),1):
  chunk=rows[start:start+14];n=len(chunk)
  fig,ax=plt.subplots(figsize=(8.4,n*.46+1.1));ax.set(xlim=(0,100),ylim=(0,n+1.5));ax.axis('off')
  ax.text(0,n+1.2,f'{arm}: retained targets → polarity routes',fontsize=12,color=ACC,va='top')
  for j,row in enumerate(chunk):
   y=n-j-.1;label=textwrap.shorten(row['text'],width=116,placeholder='…')
   ax.text(0,y,row['atlas_id'],va='center',fontsize=9,color=ACC)
   ax.text(8,y,'\n'.join(textwrap.wrap(label,62)),va='center',fontsize=9)
   for dy,sign in [(.20,'+'),(-.20,'−')]:arrow(ax,(73,y),(79,y+dy));ax.text(80,y+dy,sign+' OPEN',va='center',fontsize=9)
   if any(r.get('nodes',1)>1 for r in row['routes']):ax.text(96,y,'partial',va='center',ha='center',fontsize=8,color=ACC)
  save(fig,f'atlas-{arm}-{part}',f'Every retained {arm} target in this panel has both polarity routes. Labels are abbreviated; exact text/formulas and route IDs are retained in the figure data. These rows are records, not a count of distinct novel theses.',{'rows':chunk,'sources':['R28' if arm!='gap3p' else 'R53']})
fig,ax=canvas(4.5)
box(ax,2,72,44,21,'Egan: relativism survives\ncommunicative objection\nFrozen source leaf',True)
box(ax,54,72,44,21,'MacFarlane: Solipsistic Contextualism\ncannot explain genuine disputes\nFrozen source leaf',True,fs=9)
box(ax,15,35,70,21,'Sign scheme: comparative support for relativism\nOne licensed defeasible inference\nCQ1 supported · CQ2 unsupported',True,fs=10)
arrow(ax,(24,72),(38,56));arrow(ax,(76,72),(62,56))
box(ax,15,3,70,17,'OPEN partial route: three nodes\nDoes not establish safety–retraction L3 or T2',dashed=True);arrow(ax,(50,35),(50,20))
save(fig,'partial-B','The sole inference-bearing B route is a comparative sign argument. Its unanswered critical question keeps it OPEN. Its attempted sign essays were refused; it is not the B/1 or B/2 proposal route.',{'sources':['R28','R42'],'nodes':3,'accepted_inferences':1,'status':'OPEN'})
# Save only panels actually embedded; no stale unreferenced figures enter the count.
import re
ids=re.findall(r'\{\{fig:([^}]+)\}\}',(O/'metapaper.md').read_text());assert len(ids)==len(set(ids));assert set(ids)<=set(figures)
D['figures']=[figures[i] for i in ids]
(O/'data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');(F/'manifest.json').write_text(json.dumps(D['figures'],ensure_ascii=False,indent=2)+'\n')
print('v6 figures',len(ids))
