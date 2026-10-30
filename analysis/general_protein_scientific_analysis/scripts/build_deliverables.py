"""Publication figures and concise scientific report from newly analyzed CSVs."""
from pathlib import Path
import html
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak,Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from PIL import Image as PI

ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results';F=ROOT/'figures';F.mkdir(exist_ok=True)
S=pd.read_csv(R/'scientific_summary.csv').set_index('task');P=pd.read_csv(R/'prevalence_by_structure.csv');C=pd.read_csv(R/'subgroup_class_recall.csv').query('model=="fine_tuned"')
GROUPS=['alpha-helix','beta-sheet','coil'];GL=['Alpha-helix\n(n = 158)','Beta-sheet\n(n = 95)','Coil\n(n = 449)']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.titlesize':14,'axes.labelsize':13,'xtick.labelsize':12,'ytick.labelsize':12,'legend.fontsize':13,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(12,5.2),sharey=True,layout='constrained')
for ax,t,title,panel in zip(axes,['stability','hydrophobicity','pI'],['Stable (instability index ≤ 40)','Hydrophobic (GRAVY > 0)','Acidic (pI < 7)'],['A','B','C']):
 d=P[P.task==t].set_index('structure').loc[GROUPS];x=np.arange(3)
 for off,pre,color,marker,name in [(-.12,'gold','#24658D','o','Reference labels'),(.12,'ft','#B64C39','s','Fine-tuned predictions')]:
  y=d[pre+'_prevalence'].to_numpy()*100;lo=d[pre+'_ci_low'].to_numpy()*100;hi=d[pre+'_ci_high'].to_numpy()*100
  ax.errorbar(x+off,y,yerr=np.maximum(0,np.array([y-lo,hi-y])),fmt=marker,color=color,markersize=7,capsize=4,elinewidth=1.6,label=name)
  for xx,yy in zip(x+off,y):ax.annotate(f'{yy:.1f}',(xx,yy),xytext=(-9 if pre=='gold' else 9,0),textcoords='offset points',ha='right' if pre=='gold' else 'left',va='center',fontsize=11,color=color)
 ax.set_title(f'{panel}  {title}',loc='left',pad=17);ax.set_xticks(x,GL);ax.set_xlim(-.65,2.65);ax.set_ylim(-6,102);ax.set_yticks(np.arange(0,101,20));ax.grid(axis='y',alpha=.17);ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('Proteins assigned to the indicated class (%)')
handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=2,frameon=False)
for ext in ['png','pdf','svg']:fig.savefig(F/f'Figure_1_Structure_Property_Distributions.{ext}',dpi=300,bbox_inches='tight')
plt.close(fig)

rows=[('stability','yes','Stable'),('stability','no','Unstable'),('hydrophobicity','yes','Hydrophobic'),('hydrophobicity','no','Non-hydrophobic'),('pI','acidic','Acidic'),('pI','basic','Basic')]
vals=np.array([[C[(C.task==t)&(C.label==c)&(C.structure==g)].iloc[0].recall*100 for g in GROUPS] for t,c,_ in rows])
fig,ax=plt.subplots(figsize=(9.5,7),layout='constrained');im=ax.imshow(vals,cmap='cividis',vmin=0,vmax=100,aspect='auto')
ax.set_xticks(range(3),GL);ax.xaxis.tick_top();ax.tick_params(axis='x',pad=10,length=0);ax.set_yticks(range(6),[x[2] for x in rows]);ax.tick_params(axis='y',length=0,pad=10)
for i,(t,c,_) in enumerate(rows):
 for j,g in enumerate(GROUPS):
  v=C[(C.task==t)&(C.label==c)&(C.structure==g)].iloc[0]
  ax.text(j,i,f'{100*v.recall:.1f}%\n{int(v.true_positive)}/{int(v.support)}',ha='center',va='center',fontsize=15,color='white' if v.recall<.5 else '#151515',linespacing=1.5)
for y in [1.5,3.5]:ax.axhline(y,color='white',lw=5)
for spine in ax.spines.values():spine.set_visible(False)
cb=fig.colorbar(im,ax=ax,fraction=.045,pad=.05);cb.set_label('Class recall (%)')
ax.set_xlabel('Cell counts: correct predictions / proteins with the reference class',labelpad=16,fontsize=12)
for ext in ['png','pdf','svg']:fig.savefig(F/f'Figure_2_Class_Recall_by_Structure.{ext}',dpi=300,bbox_inches='tight')
plt.close(fig)

styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='B',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=9,textColor=colors.HexColor('#243849')));styles.add(ParagraphStyle(name='Small',fontName='Helvetica',fontSize=8.5,leading=11.5,spaceAfter=8));styles.add(ParagraphStyle(name='Cell',fontName='Helvetica',fontSize=8.2,leading=11))
styles['Title'].fontSize=22;styles['Title'].leading=26;styles['Title'].textColor=colors.HexColor('#123D58');styles['Heading1'].fontSize=16;styles['Heading1'].leading=20;styles['Heading1'].textColor=colors.HexColor('#123D58');styles['Heading2'].fontSize=12;styles['Heading2'].leading=16
flow=[];md=[]
def para(text,style='B'):
 flow.append(Paragraph(html.escape(text),styles[style]));md.append(text+'\n')
def heading(text,level=1):
 flow.append(Paragraph(html.escape(text),styles['Heading'+str(level)]));md.append('#'*(level+1)+' '+text+'\n')
def page():flow.append(PageBreak())
def image(name,width=510):
 with PI.open(F/name) as im:w,h=im.size
 flow.append(Image(str(F/name),width=width,height=width*h/w));flow.append(Spacer(1,9));md.append(f'![{name}](figures/{name})\n')
def table(headers,rows,widths):
 data=[[Paragraph(html.escape(str(v)),styles['Cell']) for v in row] for row in [headers]+rows];tab=Table(data,colWidths=widths,repeatRows=1)
 tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E3EDF4')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F6F8')]),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]));flow.append(tab);flow.append(Spacer(1,10));md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n')

flow.append(Paragraph('What the general-protein benchmark establishes',styles['Title']));md.append('# What the general-protein benchmark establishes\n')
para('Cephalo-Silk | 702 held-out proteins | Scientific follow-up to frozen semantic evaluation | October 30, 2026','Small')
heading('Strong structural-label prediction; modest, uneven physicochemical associations')
para('The existing data support a clearer contribution than a fine-tuning workflow: a property-resolved assessment of predictive capability and its limits. Structural annotations are recovered with strong discrimination across represented classes. Sequence-derived labels show smaller but measurable predictive associations, and their errors depend strongly on predominant secondary structure. These results do not identify which image features cause the predictions.')
headers=['Task','Accuracy / majority (%)','Gain over majority, pp [95% CI]','Balanced accuracy (%) [95% CI]','Minority recall (%) [95% CI]; support']
names={'alpha_presence':'Alpha-helix presence','beta_presence':'Beta-sheet presence','coil_presence':'Coil presence','predominant':'Predominant structure','stability':'Predicted stability','hydrophobicity':'Hydrophobicity','pI':'pI category'}
display=[]
for t,r in S.iterrows():
 minority=f'{100*r.minority_recall:.1f} [{100*r.minority_recall_ci_low:.1f}, {100*r.minority_recall_ci_high:.1f}]; n={int(r.minority_n)}' if r.minority_n else 'Not evaluable: no negative examples'
 ba=f'{100*r.balanced_accuracy:.1f} [{100*r.ba_ci_low:.1f}, {100*r.ba_ci_high:.1f}]' if r.represented_classes>1 else 'Not discriminative (one class)'
 display.append([names[t],f'{100*r.accuracy:.1f} / {100*r.majority_reference:.1f}',f'{r.accuracy_above_majority_pp:.2f} [{r.majority_gain_ci_low_pp:.2f}, {r.majority_gain_ci_high_pp:.2f}]',ba,minority])
table(headers,display,[100,78,105,108,121])
pd.DataFrame(display,columns=headers).to_csv(ROOT/'Scientific_Summary_Table.csv',index=False)
para('Table 1. Fine-tuned predictions, all 702 proteins per task. Existing accuracy, balanced accuracy and macro-F1 points were reused and verified unchanged; the table adds absolute uncertainty and comparisons with the largest held-out gold class. Majority references are descriptive, not independently trained baselines. Minority classes are no alpha-helix, no beta-sheet, beta-sheet predominant, unstable, hydrophobic, and basic, respectively. Intervals are pointwise; gain/BA intervals use 20,000 protein bootstrap samples, and recall intervals use Wilson scores.','Small')
para('The physicochemical macro-F1 values are 63.3% (stability), 68.9% (hydrophobicity), and 66.9% (pI). Hydrophobicity is the clearest warning against using accuracy alone: 91.17% accuracy exceeds the 88.18% majority reference by only 2.99 pp, and hydrophobic recall is 23/83. Coil presence offers no discrimination test because every reference is yes. Neutral pI is absent.','Small')

page();heading('Structure and physicochemical labels are associated, but not deterministically linked')
image('Figure_1_Structure_Property_Distributions.png')
para('Figure 1. Existing reference-class frequencies and fine-tuned prediction frequencies, grouped by the reference predominant secondary structure. Bars are marginal 95% Wilson intervals; they are not paired difference tests. Groups contain 158 alpha-helix-, 95 beta-sheet-, and 449 coil-predominant proteins. Each panel shows one class of its binary task; complementary classes sum to 100%.','Small')
para('Hydrophobic labels occur in 24/158 alpha-helix-predominant proteins (15.2%), 29/95 beta-sheet-predominant proteins (30.5%), and 30/449 coil-predominant proteins (6.7%). The association is stronger than for the other two properties: Cramer\'s V=0.253, compared with 0.122 for stability and 0.106 for pI. Three Pearson tests, each with 2 degrees of freedom, give Holm-adjusted p-values of 5.13e-10, 0.0105, and 0.0191, respectively. These are associations in this selected test set, not causal effects of structure.')
para('Predicted class frequencies exaggerate several patterns. The model predicts hydrophobicity for 3/158 alpha-helix and 0/449 coil proteins, compared with 24 and 30 positive references. It predicts acidic pI for 139/158 alpha-helix proteins (88.0%), compared with 105/158 acidic references (66.5%). Stability predictions favor stable labels in the coil group: 292/449 predicted versus 249/449 reference positives.')
para('A coarse structural-class lookup cannot explain all predictive success. The algebraically best single constant prediction within each reference structure group has the same empirical accuracy as the global majority reference: 56.27% for stability, 88.18% for hydrophobicity, and 56.70% for pI. All three model accuracies exceed these deliberately optimistic, in-sample ceilings. The alpha-helix stability group is tied; stable remains a modal choice. This comparison rules out only a deterministic lookup on the three coarse labels, not more complex biases or non-image information.','Small')

page();heading('Physicochemical discrimination varies sharply across structural groups')
image('Figure_2_Class_Recall_by_Structure.png',width=490)
para('Figure 2. Fine-tuned class recall, with correct/reference-class counts. Each cell denominator is the number of proteins in that structural group with that gold physicochemical label. Predominant groups use reference labels, not the model\'s structural predictions. All cell-specific Wilson intervals and full subgroup accuracy, balanced accuracy, macro-F1 and coverage appear in the downloadable CSVs.','Small')
para('Hydrophobicity recognition is concentrated in the beta-sheet group: 22/29 positives recovered (75.9%; 95% CI 57.9-87.8%), compared with 1/24 in the alpha-helix group (4.2%; 0.7-20.2%) and 0/30 in the coil group (0%; 0-11.4%). Thus 22 of 23 correctly identified hydrophobic proteins belong to the beta-sheet group. Coil-group accuracy is 93.3% despite zero hydrophobic recall: it exactly matches an always-non-hydrophobic prediction.','Small')
para('For pI, basic-class recall is 10/53 in the alpha-helix group (18.9%; 10.6-31.4%), versus 28/44 in beta-sheet and 125/207 in coil. Alpha-helix-group balanced accuracy is 55.1% [49.4, 61.3], leaving weak evidence for discrimination there. Stability is less concentrated: balanced accuracy is 63.3%, 73.6%, and 60.4% in the three groups, with pointwise intervals above 50%, although unstable-coil recall is only 93/200.','Small')

page();heading('What the within-group test adds, and what generalization remains untested')
para('A conditional randomization check preserves each structure group\'s reference-class counts and prediction-class counts, then randomly reallocates predictions among proteins within that group. This tests label matching beyond the observed group composition and model prediction bias; it does not use a newly trained model.')
para('Observed accuracy exceeds that conditional-independence expectation by 12.22 pp for stability (95% bootstrap CI 8.70-15.59), 4.51 pp for hydrophobicity (2.98-5.93), and 15.18 pp for pI (11.87-18.31). No randomization matched or exceeded observed accuracy in 20,000 draws for any property; the finite-simulation one-sided p-values are 1/20,001, and Holm-adjusted values are approximately 0.00015. This supports within-structure predictive association. It does not show broad utility in every group: the hydrophobic association is largely concentrated in the beta-sheet group.')
heading('Scope of generalization',2)
para('The evaluation supports performance on 702 held-out protein records from the archived general-protein dataset under its existing split, rendering protocol, label construction and saved inference settings. The available files verify the held-out record IDs and paired predictions, but do not independently establish family novelty, sequence novelty or distribution-shift robustness. Distinct protein IDs must not be treated as independent protein families.')
para('The inspected repository and frozen analysis contain no amino-acid sequences, family annotations, sequence-similarity assignments, or full training-ID roster. Repository documentation explicitly says sequences were excluded from this compact export. The linked ForceGen image-QA dataset was identified through Hugging Face metadata, but that metadata response supplied no usable family or similarity fields. No upstream sequence retrieval, family assignment or similarity calculation was undertaken. Their absence from these inputs is not a claim that such information cannot exist upstream.','Small')
heading('Limits on molecular interpretation',2)
para('Secondary-structure annotations are structurally defined and potentially visible in the renderings; success may amount to reading visual geometry or annotation cues. Instability-index, GRAVY and pI classes are sequence-derived reference labels. Their prediction does not validate thermodynamic or experimental stability, solubility, membrane status, mechanical performance, or charge at an unspecified pH.')
para('Neither accuracy nor within-structure association proves image dependence. The saved data lack image-removal/shuffle controls, sequence-only controls, and matched alternative renderings. The models may exploit render-specific cues, dataset correlations, memorization, or other information not isolated here. A three-way predominant structure label also discards continuous composition and fold details; coil-predominant is not equivalent to intrinsically disordered.','Small')

page();heading('A sharper scientific question and manuscript contribution')
heading('Central question',2)
para('Which structurally annotated and sequence-derived protein categories can an image-conditioned VLM predict on held-out protein records, and how do class imbalance and predominant secondary structure delimit that performance?')
para('The existing data support a bounded scientific contribution without new experiments: strong discrimination of represented structural labels, modest physicochemical associations beyond class proportions, and identifiable structural subgroups in which those associations fail. Frame this as an empirical capability-and-limitation study; the archive does not yet establish what information is causally extracted from images.')
heading('Results revisions',2)
para('1. Separate structural-label recognition from sequence-derived property prediction. Use Table 1 to contextualize accuracy with majority references, balanced accuracy, minority recall and uncertainty. Treat coil presence as a degenerate test and exclude it from claims about broad class discrimination.')
para('2. Add a subsection on structure-conditioned property associations and errors, using the two new figures. Lead with the 22/29 versus 1/24 versus 0/30 hydrophobic recalls and the weak basic-class recall in alpha-helix proteins. Report group sizes and reference labels used for grouping.')
para('3. Explain that performance exceeds a coarse predominant-structure lookup and a within-group randomization reference, while avoiding a causal inference. Keep the previously validated FT-versus-zero-shot comparisons as separate evidence of adaptation effects; do not conflate them with the new majority and randomization references.')
heading('Discussion revisions and remaining evidence gaps',2)
para('Replace uniform claims of molecular-property inference with property- and subgroup-specific conclusions. State that physicochemical discrimination is limited, particularly for hydrophobic alpha-helix/coil proteins and basic alpha-helix proteins. High accuracy on majority-dominated groups is not broad molecular insight.')
para('The two most important unresolved evidence gaps are (i) controlled image dependence and (ii) train-test sequence/family separation. The former requires an image-removal or image-shuffle control with comparable decoding; the latter requires reliable sequences and a pinned training/test roster. Neither can be established by further recombining these saved labels. Experimental property validation and independent-domain testing remain separate, later questions. No additional experiment was performed in this analysis.')
heading('Suggested concluding sentence',2)
para('The benchmark demonstrates strong recognition of represented structural annotations and modest, structure-dependent predictive associations for sequence-derived physicochemical categories; these associations extend beyond coarse structural-class frequencies but do not establish causal image dependence, molecular physical understanding, or transfer to unseen protein families.')

page();heading('Methods, provenance, and reproducibility')
para('Inputs: the completed semantic-label evaluation at repository source commit ef4f2945b8673d98b77f8fbfca862175b0c87a3d. The frozen extraction CSV, parser and per-property results were checked against the current GitHub archive at ea81fa7d44bb57463e65ad904fbc4b76b225e8a8 and match byte-level Git blob identities. Original package SHA-256 checks passed. No extraction was rerun or edited. The general-only annotated files were joined by protein ID to create one row per protein containing only existing labels and predictions.')
para('All new primary analyses concern the fine-tuned general-only model. Zero-shot subgroup metrics are retained in CSV for audit, with unresolved outputs counted as errors and coverage reported. They are not compared as if they had equal answer coverage. Existing paired FT-versus-zero-shot intervals were copied unchanged rather than recomputed. Fine-tuned coverage is 100% for every task.')
para('Uncertainty: 20,000 protein bootstrap samples, fixed seed 20261030, for overall absolute metrics, paired accuracy minus a fixed observed majority label, and conditional-reference excess. For individual subgroup metrics, proteins are resampled within that structure group, with deterministic documented seeds. Each protein carries all seven labels. Wilson 95% intervals are used for individual class recall and prevalence; paired prevalence-bias intervals are also provided in CSV. The majority class is chosen from the original held-out distribution and kept fixed across bootstrap samples; it is an exploratory descriptive reference, not a separately validated baseline.')
para('Association tests: each physicochemical label forms a 3-by-2 contingency table against gold predominant structure. All expected cell counts exceed 11, so Pearson chi-square tests are used; Cramer\'s V is sqrt(chi-square/702). Holm correction is applied across the three property tests. Conditional randomization uses a hypergeometric draw of true positives within each structure stratum, exactly matching uniformly permuting binary predicted labels at fixed class margins. One-sided p=(1+number of draws with accuracy at least observed)/(20,001); Holm correction is applied separately to these three tests.')
para('Bootstrap and Wilson intervals are pointwise and do not cover extraction uncertainty, correlated homologous proteins, training-seed variability, label uncertainty or multiple exploratory subgroup comparisons. A constant prediction can yield a degenerate empirical balanced-accuracy interval; the 0/30 recall Wilson interval is preferable to claiming certainty of zero population recall. Conditional randomization assumes exchangeability within structure groups; unknown family dependence is not modeled. Subgroup findings are exploratory and require independent validation before broad generalization.')
para('Verification: original fine-tuned per-property accuracy, balanced accuracy and macro-F1 points match the prior validated outputs. All subgroup support and correct counts reconcile to the 702-protein totals. Paired gold labels match across models. Source input hashes are checked before and after analysis. The script never imports or executes the semantic extractor, trains a classifier, invokes model inference, or computes new biochemical properties.')
para('Source links: https://github.com/wlululu/cephalo-silk-protein-qa and https://huggingface.co/datasets/wlululu/forcegen_image_QA.hf. The package includes input hashes, the unchanged reused prediction/metric tables, source-discovery notes, one protein-level table of existing labels, all new subgroup and uncertainty results, reproduction scripts, and publication figures in vector PDF/SVG and 300-dpi PNG. Figure fonts are embedded DejaVu Sans in PDF; SVG text remains editable.','Small')

def footer(c,d):
 c.saveState();c.setStrokeColor(colors.HexColor('#BBCBD8'));c.line(50,43,562,43);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#526575'));c.drawString(50,30,'Cephalo-Silk | General-protein scientific analysis | 2026-10-30');c.drawRightString(562,30,str(d.page));c.restoreState()
doc=SimpleDocTemplate(str(ROOT/'General_Protein_Scientific_Analysis.pdf'),pagesize=letter,leftMargin=50,rightMargin=50,topMargin=45,bottomMargin=55,title='Cephalo-Silk: Scientific Interpretation of the General-Protein Benchmark')
doc.build(flow,onFirstPage=footer,onLaterPages=footer)
(ROOT/'General_Protein_Scientific_Analysis.md').write_text('\n'.join(md)+'\n')
print('Created scientific summary, report, and two figures in PNG/PDF/SVG.')

if __name__=='__main__':pass
