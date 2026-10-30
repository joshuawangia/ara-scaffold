from pathlib import Path
import json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
import numpy as np
O=Path(__file__).resolve().parent;D=json.loads((O/'data.json').read_text());A='#28677e';G='#aeb5ba';K='#30373c'
plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':10,'svg.fonttype':'none','svg.hashsalt':'gap-T2-analysis','axes.spines.top':False,'axes.spines.right':False})
figures=[]
def save(fig,id,caption,data):
 fig.savefig(O/'figures'/f'{id}.svg',bbox_inches='tight',metadata={'Date':None,'Creator':'Deterministic rendering of recorded data / labelled analyst reconstruction'});plt.close(fig);figures.append({'id':id,'file':f'figures/{id}.svg','caption':caption,'data':data})
fig,ax=plt.subplots(figsize=(8,3.3));y=np.arange(3);rs=D['forks'];roots=[r['open_roots'] for r in rs];partial=[r['open_partial'] for r in rs]
ax.barh(y,roots,color=G,label='OPEN: root only');ax.barh(y,partial,left=roots,color=A,label='OPEN: partial argument')
for i,r in enumerate(rs):ax.text(r['routes']+1,i,f"{r['routes']} OPEN; 0 CLOSED-derived",va='center',fontsize=9)
ax.set_yticks(y,['A · packed','B · full provenance','C · external T2']);ax.invert_yaxis();ax.set_xlim(0,80);ax.set_xlabel('Terminal polarity routes');ax.set_xticks([0,10,20,30,40,50,60]);ax.grid(axis='x',alpha=.15);ax.legend(frameon=False,ncol=2,loc='upper center',bbox_to_anchor=(.5,-.25),fontsize=9)
save(fig,'fork-outcomes','Recorded A/B/C terminal outcomes. B alone retains one partial sign argument, which is not L3 and remains OPEN. C tests the externally supplied biconditional and each direction; its six routes contain no accepted inference. Counts do not measure novelty or establish a causal effect of context length.',{'forks':rs,'source':'reports/overnight/gap1pu/handoff.md'})
fig,ax=plt.subplots(figsize=(8,5.2));ax.axis('off');ax.set(xlim=(0,10),ylim=(0,7))
def box(x,y,w,h,t,missing=False):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.04',facecolor='#edf1f3' if missing else 'white',edgecolor=A if missing else K,linestyle='--' if missing else '-'));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=9)
def arrow(x1,y1,x2,y2):ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=12,color=K))
ax.text(5,6.7,'Analyst reconstruction — not an ARA proof graph',ha='center',color=A,fontsize=12)
box(.2,4.9,2.4,.9,'Unsafe belief\n¬S');box(3.25,4.9,3.2,.9,'Missing bridge\n¬S → F (or directly R)',True);box(7.1,4.9,2.7,.9,'Assessment-relative\nuntruth F')
arrow(2.65,5.35,3.2,5.35);arrow(6.5,5.35,7.05,5.35)
box(7.1,2.7,2.7,.9,'Required retraction\nR');arrow(8.45,4.85,8.45,3.65);ax.text(6.9,4.25,'F → R\nRetraction Rule',ha='right',va='center',fontsize=9)
box(.2,2.7,5.6,.9,'K → S: safety is necessary for knowledge\n¬S → ¬K does not supply F or R')
box(.2,.6,9.6,1.05,'Necessity needs its own support: R → ¬S\nAn exhaustive account of the relevant obligation’s grounds is missing.\nA one-way trigger cannot simply be reversed.',True)
ax.text(5,.05,'Dashed boxes identify obligations for a proposed argument, not licensed steps.',ha='center',fontsize=9)
save(fig,'missing-bridge','A schematic explanation of the missing links. The complete general Retraction Rule is available in the rich extraction but absent from the old freeze; it is nominated for gap2. The diagram does not assume that the missing truth bridge is true or that it is the only possible strategy. All parameters must refer to the same belief, assertion and contexts.',{'logic':D['logic'],'sources':['Mighty Knowledge PDF5,23–24','Assessment Sensitivity printed108–111','reports/overnight/gap2/source-anchor-review.md']})
D['figures']=figures;(O/'data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');(O/'figures/manifest.json').write_text(json.dumps(figures,ensure_ascii=False,indent=2)+'\n')
print('figures',len(figures))
