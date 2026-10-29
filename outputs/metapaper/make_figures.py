import json,hashlib,datetime,textwrap
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch,Polygon
import numpy as np
O=Path(__file__).resolve().parent;D=json.loads((O/'data.json').read_text());F=O/'figures'
plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'ara-metapaper','axes.titleweight':'normal'})
ACC='#28677e'; DARK='#30373c';GRAY='#aeb5ba';PALE='#edf1f3'
figures=[]
def save(fig,id,caption,data):
 fig.savefig(F/(id+'.svg'),bbox_inches='tight',metadata={'Date':None,'Creator':'Deterministic matplotlib rendering from data.json'})
 plt.close(fig); item={'id':id,'file':'figures/'+id+'.svg','caption':caption,'data':data};figures.append(item)
def box(ax,x,y,w,h,text,accent=False):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012,rounding_size=.015',fc=PALE if accent else 'white',ec=ACC if accent else DARK,lw=1.2))
 ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9)
def arrow(ax,a,b):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,lw=1.2,color=DARK))
fig,ax=plt.subplots(figsize=(8.4,5.5));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
box(ax,.04,.80,.25,.16,'L: versioned move bank\nRule forms +\ncritical questions',True)
box(ax,.37,.80,.25,.16,'T: frozen commitments\nContent +\ncited provenance',True)
box(ax,.70,.80,.25,.16,'H: model proposals\nTargets, cuts,\nCQ answers',True)
box(ax,.06,.49,.23,.15,'Literature → extraction\nImmutable\nrich evidence')
box(ax,.37,.49,.25,.15,'Deterministic engine\nBank shape + Z3\n+ scope')
box(ax,.70,.49,.25,.15,'Runtime boundary\nSchema, isolation,\nbudgets')
box(ax,.37,.23,.25,.15,'Search both polarities\nClosed / open\nroute records')
box(ax,.16,.015,.68,.13,'Human selection → writing → audit → retrieval → re-audit → export\nRejected calls, omissions and decisions remain\nin append-only logs')
for a,b in [((.165,.80),(.42,.64)),((.495,.80),(.495,.64)),((.825,.80),(.825,.64)),((.70,.565),(.62,.565)),((.18,.64),(.40,.80)),((.495,.49),(.495,.38)),((.495,.23),(.495,.145))]:arrow(ax,a,b)
save(fig,'architecture','ARA separates the source of a license (L), the premises available to a run (T), and model-suggested hypotheses or cuts (H). Models propose; the deterministic engine decides formal admissibility. The final export path remains gated.',{'source':['scaffold/PLAN.md','scaffold/CLAUDE.md','scaffold/SOURCE_MAP.md'],'nodes':['L','T','H','extraction','engine','runtime','search','selection-writing-verification']})
# Shared evidence funnel followed by two explicitly separate run histories.
gap=D['gap_pilot_1']
fig,ax=plt.subplots(figsize=(8.4,7.4));ax.set(xlim=(0,10),ylim=(0,10));ax.axis('off')
funnel=[('Chosen works',53),('Original PDFs / rich graphs',26),('Extracted items',5659),('Eligible items after quarantine',5296)]
for i,(label,n) in enumerate(funnel):
 y=9.45-i*.76;w=8.7-i*.43;x=(10-w)/2
 ax.add_patch(Polygon([[x,y+.26],[x+w,y+.26],[x+w-.15,y-.26],[x+.15,y-.26]],closed=True,fc=PALE,ec=GRAY))
 ax.text(x+.3,y,label,ha='left',va='center',fontsize=10)
 ax.text(x+w-.3,y,f'{n:,}',ha='right',va='center',fontsize=12,color=ACC)
ax.text(5,6.65,'363 quarantined: 312 direct + 51 dependent',ha='center',fontsize=9,color=DARK)
ax.text(2.55,5.95,'Earlier writing lineage',ha='center',fontsize=11,color=ACC)
ax.text(7.5,5.95,'Gap pilot 1 — fresh construction',ha='center',fontsize=11,color=ACC)
for x in [2.55,7.5]:
 ax.add_patch(FancyArrowPatch((5,6.5),(x,6.13),arrowstyle='-|>',mutation_scale=12,color=DARK))
left=[('Pilot 5 frozen T','169 commitments / 22 papers'),('Fork 3 targets → searches','3 targets → 6 polarity searches'),('Selected closed routes','2, supported by one paper'),('Verified essay exports','0')]
right=[('Construction completed',f"{gap['windows']} windows: {gap['accepted_windows']} accepted / {gap['skipped_windows']} skipped"),('Working set — UNFROZEN',f"{gap['working_commitments']} commitments / {gap['represented_papers']} of {gap['available_papers']} papers"),('STOP: alignment 36/150','35 accepted judgments; 3 invalid replies'),('NOT REACHED','Freeze → targets → search → essays')]
for col,items in enumerate([left,right]):
 x=.35 if col==0 else 5.3;w=4.35
 for i,(title,detail) in enumerate(items):
  y=5.15-i*1.15;accent=(col==1 and i==2)
  ax.add_patch(FancyBboxPatch((x,y-.37),w,.77,boxstyle='round,pad=.03,rounding_size=.05',fc=PALE if accent else 'white',ec=ACC if accent else GRAY,lw=1.5 if accent else 1))
  ax.text(x+w/2,y+.11,title,ha='center',va='center',fontsize=10,color=ACC if accent else DARK,weight='bold' if accent else 'normal')
  ax.text(x+w/2,y-.15,detail,ha='center',va='center',fontsize=9.3)
  if i<3:
   ax.add_patch(FancyArrowPatch((x+w/2,y-.40),(x+w/2,y-.71),arrowstyle='-|>',mutation_scale=10,color=GRAY,linestyle='--' if col==1 and i==2 else '-'))
ax.text(5,.65,'Later acquisition: 54 local PDFs; new texts outside these pilot inputs',ha='center',fontsize=9)
save(fig,'funnel','Common source evidence, then separate run histories; box area is not proportional to counts. The historical writing lineage used a frozen T. Gap pilot 1 completed construction but stopped at alignment candidate 36/150 after three altered-ID replies; 35 accepted judgments were not applied bridges. Its working set was never frozen, and downstream stages were not reached. Later acquisitions do not enlarge either pilot retrospectively.',{'stages':funnel,'historical_path':left,'gap_pilot_path':right,'gap_pilot_facts':gap,'quarantine':{'direct':312,'dependent':51,'total':363},'later_pdfs':54,'source':['reports/zeta-full26-part7.md','reports/zeta-codex-pilot-5.md','reports/zeta-fork3.md','reports/nu4-writer.md','reports/eps2-methodology-supplement.md','reports/overnight/gap1/handoff.md']})
# Iteration timeline: timestamped episodes, one row per engineering class.
timeline=[('Extraction', '2026-10-21T00:26:58Z','2026-10-22T23:59:23Z','Rich graph → grounded union'),('Construction','2026-10-21T03:37:29Z','2026-10-23T19:39:01Z','Closure budgets → soft shares'),('Providers / isolation','2026-10-23T10:02:43Z','2026-10-26T06:23:00Z','Credit stop → Claude → Codex'),('Structure / vocabulary','2026-10-26T15:09:34Z','2026-10-27T14:05:42Z','Atomic T → conditionals + stance'),('Novelty / cross-paper','2026-10-26T23:07:41Z','2026-10-29T06:19:53Z','Trivial closure → per-paper gate'),('Writing / audit','2026-10-28T16:52:30Z','2026-10-28T21:39:35Z','Short drafts → sections + repairs'),('Literature currency','2026-10-28T21:03:17Z','2026-10-29T06:17:05Z','Historical gaps → qualified L3')]
timeline.append(('Gap pilot 1',gap['started_utc'],gap['stopped_utc'],'STOP: alignment 36/150; no freeze'))
start=datetime.datetime.fromisoformat(D['scope']['correspondence_start'].replace('Z','+00:00'))
hours=lambda t:(datetime.datetime.fromisoformat(t.replace('Z','+00:00'))-start).total_seconds()/3600
fig,ax=plt.subplots(figsize=(8.4,5.2))
for i,(label,a,b,text) in enumerate(timeline):
 ax.barh(i,hours(b)-hours(a),left=hours(a),color=ACC if i>3 else GRAY,height=.42)
 ax.text(hours(b) if hours(a)>170 else hours(a),i-.29,text,fontsize=8.4,va='bottom',ha='right' if hours(a)>170 else 'left')
 if label=='Gap pilot 1':ax.plot(hours(b),i,marker='D',color=ACC,markersize=5)
ax.set_yticks(range(len(timeline)),[x[0] for x in timeline]);ax.invert_yaxis();ax.set_xticks([0,24,48,72,96,120,144,168,192,216],['21','22','23','24','25','26','27','28','29','30']);ax.set_xlabel('October 2026 (UTC); bars span logged episodes, not continuous labor');ax.set_xlim(-1,217);ax.grid(axis='x',alpha=.2)
a=hours('2026-10-28T12:33:41Z');b=hours('2026-10-28T16:49:21Z');ax.axvspan(a,b,facecolor='none',edgecolor=ACC,hatch='////',lw=.5)
ax.set_title('Pending: sigma r12 and nu4 r5 — no repair results credited',fontsize=10,pad=20)
save(fig,'iterations','Overlapping logged repair episodes, with gap pilot 1 timed from its supervisor receipt. The diamond marks the correctly refused alignment stop on October 29, before freeze. The hatched band is the acknowledged October 28 idle interval, not labor. Sigma r12 and nu4 r5 are pending requests, not completed repairs or successful continuations.',{'episodes':timeline,'idle_start':'2026-10-28T12:33:41Z','idle_end':'2026-10-28T16:49:21Z','pending':D['pending_work'],'source':['correspondence/log.txt','reports/overnight/gap1/pilot-exit.json','briefs/sigma-round-12.md','briefs/nu4-round-5.md']})
# Gate incidences: candidates can have multiple reasons; no false stacked total.
ps=D['pilots'][2:];reasons=['attributed_report','own_thesis_not_established','single_commitment_entailment','target_content_not_established','gap_resolution_not_established','duplicate_retained_target']
labels=['Attribution screen','Own-thesis classifier','Single-support entailment','Content / restatement','Gap not resolved','Duplicate retained ID']
mat=[]
for p in ps:
 mat.append([len({(x['attempt'],x['id']) for x in p['candidate_rows'] if r in x['reasons']}) for r in reasons])
fig,ax=plt.subplots(figsize=(8.4,4.8));arr=np.array(mat);im=ax.imshow(arr,cmap=matplotlib.colors.LinearSegmentedColormap.from_list('mono',['#f4f5f5',ACC]),aspect='auto',vmin=0,vmax=18)
for (i,j),v in np.ndenumerate(arr):ax.text(j,i,str(v),ha='center',va='center',color='white' if v>9 else DARK)
ax.set_xticks(range(6),labels,rotation=30,ha='right',fontsize=9);ax.set_yticks(range(len(ps)),[p['name'].replace('codex','Pilot ').replace('fork','Fork ') for p in ps]);ax.tick_params(length=0);fig.colorbar(im,ax=ax,label='Candidate-attempt reason incidences',shrink=.7,pad=.03)
save(fig,'gates','Native rejection reasons across pilot generations. The same candidate-attempt can occur in more than one column; columns must not be summed into a rejection total. “Attribution screen” includes lexical false positives, especially before that screen became advisory. Repeated proposal attempts count separately. Zero means no recorded rejection under that reason, not proof of semantic novelty.',{'pilots':[p['name'] for p in ps],'reasons':reasons,'values':mat,'source':'data.json/pilots/*/candidate_rows'})
# Outcome census with retrospective qualifications.
run_names=['Pilot 2 resumed','Pilot 3','Pilot 5','Fork 2','Fork 3','Fork 5','Fork 6']; open_counts=[20,11,10,4,4,12,20];closed_counts=[0,10,4,0,2,0,0]
fig,ax=plt.subplots(figsize=(8.4,3.8));y=np.arange(len(run_names));ax.barh(y,open_counts,color=GRAY,label='OPEN');ax.barh(y,closed_counts,left=open_counts,color=ACC,label='Native CLOSED (qualified below)')
for i,(a,b) in enumerate(zip(open_counts,closed_counts)):
 if a:ax.text(a/2,i,str(a),ha='center',va='center')
 if b:ax.text(a+b/2,i,str(b),ha='center',va='center',color='white')
ax.set_yticks(y,run_names);ax.invert_yaxis();ax.set_xlabel('Published terminal routes (not search jobs)');ax.set_xticks(range(0,23,2));ax.legend(loc='upper center',bbox_to_anchor=(.5,-.24),ncol=2,frameon=False,fontsize=8);ax.grid(axis='x',alpha=.15)
save(fig,'routes','Closed is a formal outcome. Pilot 3’s ten closed routes were trivial restatements; pilot 5’s four were conjunction packaging; fork 3’s two derived routes used a single paper. None met the complete accepted cross-paper criterion. Pilot 3 published twenty-one routes from twenty polarity searches.',{'runs':run_names,'open':open_counts,'native_closed':closed_counts,'source':['reports/zeta-codex-pilot-2-resumed.md','reports/zeta-codex-pilot-3.md','reports/zeta-codex-pilot-5.md','reports/zeta-fork2.md','reports/zeta-fork3.md','reports/zeta-fork5.md','reports/zeta-fork6.md']})
acct=D['accounting'];stages=['extract_paper','select_t_roots','build_t_batch'];usd=[[acct['by_stage'][s][cl]['cost_usd'] for s in stages] for cl in ['measured','unknown_at_reservation']]
fig,ax=plt.subplots(figsize=(8.4,3));y=np.arange(3);ax.barh(y,usd[0],color=ACC,label='Measured API USD');ax.barh(y,usd[1],left=usd[0],color='white',edgecolor=DARK,hatch='///',label='Unknown actual; reservation')
for i in range(3):ax.text(usd[0][i]+usd[1][i]+1,i,f'{usd[0][i]:.6f} + {usd[1][i]:.6f}',va='center',fontsize=9)
ax.set_yticks(y,['Extraction','Root selection','T formalization']);ax.invert_yaxis();ax.set_xlim(0,155);ax.set_xlabel('USD in deduplicated fork-6 lineage');ax.legend(loc='lower right',fontsize=8);ax.grid(axis='x',alpha=.15)
save(fig,'api-cost','Measured API cost is $131.785270; unknown-at-reservation is $1.844820. The sum, $133.630090, is a budget-accounting figure, not an invoice. Subscription calls contribute no API USD here. Earlier development/smoke work and later writing/polish are outside this report’s lineage.',{'stages':stages,'measured':usd[0],'unknown_at_reservation':usd[1],'source':'reports/overnight/fork6/accounting.json'})
# Measured subscription tokens by provider and grouped stage, retaining native token components.
groups={'Construction':['select_t_roots','build_t_batch','build_t'],'Targets':['propose_targets','classify_target'],'Search':['map_leaf','propose_cuts','formalise','formalise_slots','answer_cq','tier1_repair'],'Summaries':['route_summary'],'Checks / other':[]}
values={}
for provider in ['claude_code','codex_cli']:
 vv={g:0 for g in groups}
 for st,b in D['provider_stage_accounting'][provider]['by_stage'].items():
  g=next((g for g,ss in groups.items() if st in ss),'Checks / other');vv[g]+=sum(b['measured'][k] for k in ['input_tokens','output_tokens','cache_read_tokens','cache_write_tokens'])
 values[provider]=vv
fig,ax=plt.subplots(figsize=(8.4,3.6));colors=[DARK,'#68767e',GRAY,ACC,'#dce5e9'];left=[0.,0.]
for j,g in enumerate(groups):
 v=[values[p][g]/1e6 for p in values];ax.barh([0,1],v,left=left,label=g,color=colors[j],edgecolor='white');left=[left[i]+v[i] for i in range(2)]
ax.set_yticks([0,1],['Claude Code','Codex CLI']);ax.set_xlabel('Millions of measured tokens, including cache components');ax.set_xlim(0,65);ax.invert_yaxis();ax.legend(loc='upper center',bbox_to_anchor=(.5,-.24),ncol=3,frameon=False,fontsize=8);ax.grid(axis='x',alpha=.15)
for i,total in enumerate(left):ax.text(total+.5,i,f'{total:.3f}M',va='center',fontsize=9)
save(fig,'subscription-tokens','Measured subscription usage in the same deduplicated lineage, grouped by native stage. Cache reads and writes are retained; these are accounting components, not unique prose tokens. Unknown reservations and an unclassified-provider legacy receipt are shown in the accompanying table, not these bars. Coding-agent and orchestration conversations are outside this ledger.',{'groups':groups,'measured_values':values,'source':'data.json/provider_stage_accounting; reconciled to reports/overnight/fork6/accounting.json'})
D['figures']=figures
D['accounting_reconciliation']={}
for cls in ['measured','unknown_at_reservation','unclassified']:
 native=acct[cls];buckets=[x[cls] for x in D['provider_stage_accounting'].values()]
 assert abs(sum(x['cost_usd'] for x in buckets)-native['cost_usd'])<1e-8
 for k,v in native['tokens'].items():assert sum(x[k] for x in buckets)==v,(cls,k)
 assert sum(x['model_receipts'] for x in buckets)==native['model_calls']
 D['accounting_reconciliation'][cls]='provider/stage aggregates match native accounting.json'
D['supplemental_report_facts']={'source':['reports/nu4-writer.md','reports/pi3-publication.md','reports/xi-round27.md','reports/eps2-methodology-supplement.md'],'writer_round2':{'words':4604,'input_tokens':143996,'cache_read_tokens':5888,'output_tokens':35228,'actual_responses':8,'exported':False},'writer_round4':{'route1_words':4714,'route2_words':4619,'route1_initial_flags':75,'route2_initial_flags':25,'final_flags':[0,0],'exports':0,'retrieval_error':'cli_tool_event'},'forward_round27':{'commitments':169,'papers':22,'depth':2,'consequence_cap':500,'qualifying_candidates':0,'superseded_candidates':6,'local_revision':'5557e9a7da15413071b25932413d2f9fac30f797'},'coverage':{'chosen':53,'original_pdfs':26,'initial_new_pdfs':20,'followup_pdfs':8,'local_total':54,'modern_candidates':44,'modern_fulltexts':25,'originals_recovered':3,'modern_unavailable':19,'original_unavailable':24,'requests':43,'initial_gaps':3,'addressed':1,'partial':2,'certified_open':0}}
(O/'data.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
(O/'figures/manifest.json').write_text(json.dumps(figures,ensure_ascii=False,indent=2)+'\n')
print('figures',len(figures),'accounting checks passed')
