"""C4-based architecture views. Standard-library source, SVG and diagrams.net."""
from pathlib import Path
from html import escape as E
import json, textwrap, xml.etree.ElementTree as X

OUT=Path(__file__).resolve().parent
evidence_path=OUT/'evidence-data.json'
if not evidence_path.exists(): evidence_path=OUT.parent/'architecture/architecture-data.json'
OLD=json.loads(evidence_path.read_text(encoding='utf-8'))
COLORS={'person':'#25394c','client':'#70549c','app':'#1d6196','store':'#16766f','external':'#687583','planned':'#a56e22'}
ICONS={
 'person':'M12 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8 M4 22v-4c0-6 16-6 16 0v4',
 'client':'M3 3h18v18H3z M3 8h18 M6 5.5h1m3 0h1 M7 12h4v5H7z M14 12h4m-4 4h4',
 'app':'M3 3h18v7H3z M3 14h18v7H3z M6 6h1m3 0h7 M6 17h1m3 0h7',
 'store':'M2 6h8l2 3h10v12H2z M2 10h20',
 'external':'M4 8l8-5 8 5v11H4z M9 22v-7h6v7 M7 9h1m3 0h1m3 0h1',
 'planned':'M4 4h16v16H4z M8 8l3 3-3 3m5 0h4',
}
VIEWS=[]

class View:
 def __init__(self,key,title,subtitle,height=1120):
  self.key=key;self.title=title;self.subtitle=subtitle;self.w=1800;self.h=height;self.nodes=[];self.edges=[];self.groups=[];self.notes=[]
 def group(self,x,y,w,h,title,detail='',planned=False):self.groups.append(dict(x=x,y=y,w=w,h=h,title=title,detail=detail,planned=planned))
 def n(self,id,x,y,w,h,title,kind,tech,desc,role='app',ref=None,notes=''):
  self.nodes.append(dict(id=id,x=x,y=y,w=w,h=h,title=title,kind=kind,tech=tech,desc=desc,role=role,ref=ref,notes=notes));return id
 def edge(self,a,b,points,lines,pos,planned=False):self.edges.append(dict(a=a,b=b,points=points,lines=lines,pos=pos,planned=planned))
 def note(self,x,y,s):self.notes.append((x,y,s))

v=View('01-system','System architecture — SoilMate','C4 container view | Current implementation | Nasa Petani | 15 Nov 2026')
v.group(320,390,1425,505,'SoilMate','Software system boundary')
v.n('grower',40,565,220,235,'Grower','Person','Web browser',['Checks local conditions','and crop-related risk'],'person','browser')
v.n('ui',380,560,320,240,'Dashboard UI','Client container','HTML · CSS · JavaScript',['Overview, maps and trends','Plotly.js · Leaflet · Bootstrap'],'client','browser', 'Browser code is delivered by the server. This is a server-rendered dashboard, not an independently deployed single-page app.')
v.n('web',900,560,320,240,'Web application','Server container','Python · FastAPI · Jinja2',['Reads selected data and','renders pages, maps and charts'],'app','server','One application process; the overview, map and analysis modules are internal components, not separate services. Uvicorn is listed as the ASGI runner; production process configuration is not supplied.')
v.n('files',1400,560,285,240,'Project data','Data store','Local CSV + GeoJSON',['Weather, risk and daily history','Malaysia state boundaries'],'store','snapshots','A filesystem data store, not a SQL database. The application reads supplied CSVs; upstream NASA lineage is not established by the code.')
v.n('providers',380,170,320,170,'Map and asset providers','External systems','HTTPS providers',['Map tiles and browser libraries','Bootstrap CSS and Inter font'],'external',notes='The application base template uses external Bootstrap and Google Fonts. Generated Folium output can load Leaflet, supporting assets and map tiles from external providers. Plotly.js Basic is served locally by FastAPI.')
v.edge('grower','ui',[(260,680),(380,680)],['Sets filters','[Browser]'],(320,637))
v.edge('ui','web',[(700,620),(900,620)],['Requests selected view','[HTTP GET]'],(800,572))
v.edge('web','ui',[(900,740),(700,740)],['Returns HTML + JSON','[HTTP response]'],(800,694))
v.edge('web','files',[(1220,680),(1400,680)],['Reads CSV + shapes','[File access]'],(1310,630))
v.edge('ui','providers',[(540,560),(540,340)],['Loads map tiles and assets','[HTTPS]'],(715,475))
v.note(50,937,'Runtime: one Python web application, browser code, and a local file store. Deployment environment is not specified in source.')
v.note(50,968,'Detail: Overview uses HTML fragments; Analysis receives chart JSON embedded in HTML; maps are displayed in an iframe.')
VIEWS.append(v)

v=View('02-components','Backend architecture — SoilMate','C4 component view | Scope: the Python web application | Current implementation',1260)
v.group(335,200,1025,865,'Web application','Single FastAPI process · Python')
v.group(1460,200,285,865,'Project data','Local filesystem')
v.n('client',40,570,225,230,'Dashboard UI','Client container','HTML · JavaScript',['Sends selected state,','date and chart window'],'client','browser')
v.n('routes',380,570,290,230,'HTTP / page handlers','Component','FastAPI · Jinja2',['Validate request values,','call readers and render HTML'],'app','server')
v.n('overview',925,270,390,205,'Overview data reader','Component','pandas',['Select weather and risk rows;','choose historical soil scene'],'app','snapshots')
v.n('analysis',925,555,390,230,'Analysis builder','Component','pandas · Plotly Python',['Build daily series and chart JSON;','cache reads by file change time'],'app','analysis','functools.lru_cache is in-memory and part of this Python process; it is not a Redis service. Missing observations stay as gaps. Rain summaries remain 14-day totals.')
v.n('maps',925,865,390,170,'Map builder','Component','pandas · Folium',['Join categories to state shapes;','return Leaflet map HTML'],'app','mapengine')
v.n('snapshots',1485,270,235,205,'Snapshot files','Data store subset','CSV',['Weather values','Risk and scene values'],'store','snapshots')
v.n('history',1485,555,235,230,'History files','Data store subset','Four graph CSVs',['Daily observations','and summary values'],'store','history')
v.n('geodata',1485,865,235,170,'Map inputs','Data store subset','CSV + GeoJSON',['State categories','Malaysia boundaries'],'store','geodata')
v.edge('client','routes',[(265,680),(380,680)],['Requests','[HTTP GET]'],(322,630))
v.edge('routes','overview',[(670,620),(790,620),(790,372),(925,372)],['Calls overview functions','[Python call]'],(785,316))
v.edge('routes','analysis',[(670,680),(925,680)],['Calls get_analysis()','[Python call]'],(797,627))
v.edge('routes','maps',[(670,740),(790,740),(790,950),(925,950)],['Calls map functions','[Python call]'],(790,1005))
v.edge('overview','snapshots',[(1315,372),(1485,372)],['Reads rows','[File access]'],(1400,320))
v.edge('analysis','history',[(1315,670),(1485,670)],['Reads daily data','[File access]'],(1400,615))
v.edge('maps','geodata',[(1315,950),(1485,950)],['Reads + joins','[File access]'],(1400,900))
v.note(50,1115,'Response path: the handlers return a rendered page or HTML fragment to the dashboard. StaticFiles serves local assets; GZip compresses large responses.')
v.note(50,1148,'Routes: / and /risk-layers · /weather · /simulation · /analysis · /maps/{alert, rain, humid, soil, plants}')
VIEWS.append(v)

v=View('03-data-design','Data architecture — NASA to dashboard','Proposed integration design | Amber = planned pipeline | Blue / purple = current runtime | Green = existing file interface',1360)
v.group(365,185,975,810,'Data preparation','Proposed offline / batch pipeline',True)
v.group(1390,185,360,810,'Serving layer','Current runtime')
v.n('nasa',40,400,260,310,'NASA data products','External systems','Product access to be selected',['POWER: weather','GPM IMERG: rain','SMAP L4: soil','ECOSTRESS ESI: plant stress'],'external','sources','These names appear in supplied data and notes. The diagram proposes an integration; product versions, temporal coverage, source lineage and scientific interpretation need validation.')
v.n('import',415,300,310,220,'Data importer','Planned process','earthaccess · httpx',['Retrieve selected products;','record source dates and units'],'planned','ingest')
v.n('raw',415,710,310,220,'Raw product store','Planned data store','NetCDF / HDF5, as required',['Keep original measurements','and retrieval metadata'],'planned',notes='Proposed file-based raw zone. Choose storage paths and readers after confirming the exact products. No raw-download pipeline is implemented.')
v.n('prepare',960,300,320,220,'Data preparation','Planned process','pandas · xarray · geospatial tools',['Align state and date; check gaps,','units, coverage and risk rules'],'planned','clean')
v.n('ready',960,710,320,220,'Prepared data store','Data store / planned writer','CSV + GeoJSON interface',['Weather, risk, map categories','and daily history for the app'],'store','snapshots','The current app already reads local CSV and GeoJSON. The automated writer and reproducible NASA lineage shown here are proposed. Preserve the interface while validating the data pipeline.')
v.n('server',1420,300,300,220,'Web application','Current server container','FastAPI · Jinja2 · pandas',['Read prepared records; render','cards, maps and chart data'],'app','server')
v.n('browser',1420,710,300,220,'Dashboard UI','Current client container','HTML · JS · Leaflet · Plotly.js',['Show selected conditions,','maps and historical trends'],'client','browser')
v.n('ml',415,1085,310,175,'Forecasting model','Optional planned process','Prophet · scikit-learn',['Evaluate forecasts before','connecting them to the app'],'planned','forecast')
v.edge('nasa','import',[(300,450),(415,450)],['Fetch','[HTTPS]'],(357,385),True)
v.edge('import','raw',[(570,520),(570,710)],['Store raw files','[File write]'],(690,620),True)
v.edge('raw','prepare',[(725,820),(840,820),(840,410),(960,410)],['Load measurements','[File read]'],(843,560),True)
v.edge('prepare','ready',[(1120,520),(1120,710)],['Publish checked tables','[File write]'],(1120,618),True)
v.edge('ready','server',[(1280,820),(1365,820),(1365,410),(1420,410)],['Supplies app records','[Local file read]'],(1365,610))
v.edge('server','browser',[(1570,520),(1570,710)],['Serve pages and results','[HTTP response]'],(1570,615))
v.edge('ready','ml',[(1120,930),(1120,1170),(725,1170)],['Provide historical series','[Future file interface]'],(951,1122),True)
v.note(40,1035,'The current dashboard uses supplied local files. Automatic NASA ingestion, preparation and forecasting are proposed here.')
v.note(780,1235,'The model has no current serving connection. The existing Simulation panel displays earlier stored conditions.')
VIEWS.append(v)

def t(x,y,s,size=18,fill='#20354a',weight=400,anchor='start'):
 return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{E(s)}</text>'

def render(v):
 p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{v.w}" height="{v.h}" viewBox="0 0 {v.w} {v.h}" role="img" aria-labelledby="title-{v.key} desc-{v.key}">',f'<title id="title-{v.key}">{E(v.title)}</title><desc id="desc-{v.key}">{E(v.subtitle)}. Every directional relationship states what it carries or calls. Click nodes in the interactive explorer for details.</desc>',
 '<defs><marker id="arr" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#526579"/></marker><marker id="arr-plan" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#a56e22"/></marker></defs>',
 '<style>text{font-family:Segoe UI,Arial,sans-serif}.arch-node{cursor:pointer;outline:none}.arch-node:focus .node-shape,.arch-node:hover .node-shape{stroke:#12273a;stroke-width:4}.arch-node.selected .node-shape{stroke:#e29a30;stroke-width:5}.muted{opacity:.16}</style>',
 f'<rect x="0" y="0" width="{v.w}" height="{v.h}" fill="#ffffff"/>',t(45,68,v.title,36,weight=650),t(47,108,v.subtitle,17,'#586a7c')]
 for g in v.groups:
  p+=[f'<rect x="{g["x"]}" y="{g["y"]}" width="{g["w"]}" height="{g["h"]}" rx="4" fill="{"#fffaf0" if g["planned"] else "#f8fafc"}" stroke="{"#b38c48" if g["planned"] else "#91a2b3"}" stroke-width="1.7" stroke-dasharray="9 6"/>',t(g['x']+18,g['y']+31,g['title'],20,weight=650),t(g['x']+18,g['y']+57,g['detail'],14,'#586a7c')]
 # Relationships behind nodes, with explicit labels in reserved whitespace.
 for i,e in enumerate(v.edges):
  d='M'+' L'.join(f'{x} {y}' for x,y in e['points']);color='#a56e22' if e['planned'] else '#526579'
  dash=' stroke-dasharray="7 5"' if e['planned'] else ''
  p.append(f'<g class="relationship" data-from="{e["a"]}" data-to="{e["b"]}"><path d="{d}" fill="none" stroke="{color}" stroke-width="2"{dash} marker-end="url(#{"arr-plan" if e["planned"] else "arr"})"/>')
  x,y=e['pos'];width=max(len(s) for s in e['lines'])*8.3+18;h=len(e['lines'])*23+9
  p.append(f'<rect x="{x-width/2}" y="{y-18}" width="{width}" height="{h}" fill="#ffffff"/>')
  for k,line in enumerate(e['lines']):p.append(t(x,y+k*23,line,15.5,color,anchor='middle'))
  p.append('</g>')
 for n in v.nodes:
  x,y,w,h=[n[k] for k in ['x','y','w','h']];cx=x+w/2;color=COLORS[n['role']];plan=n['role']=='planned'
  p.append(f'<g class="arch-node" data-node="{n["id"]}" role="button" tabindex="0" aria-label="{E(n["title"])}. {E(n["kind"])}. Show details."><title>{E(n["title"])} — {E(n["kind"])}: {E(" ".join(n["desc"]))}</title>')
  p.append(f'<rect class="node-shape" x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{color}" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="5 4"' if plan else '')+'/>')
  p.append(f'<g transform="translate({cx-15} {y+16}) scale(1.25)" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="{ICONS[n["role"]]}"/></g>')
  short=h<200
  p.extend([t(cx,y+(60 if short else 70),n['title'],22 if w>=280 else 20,'#ffffff',650,'middle'),t(cx,y+(82 if short else 96),'['+n['kind']+']',13.5,'#ffffff',400,'middle')])
  # A short explicit technology line, wrapped only when needed.
  tech=textwrap.wrap(n['tech'],width=max(24,int(w/8)))
  for i,line in enumerate(tech):p.append(t(cx,y+(106 if short else 122)+i*20,line,15,'#ffffff',500,'middle'))
  start=y+(132 if short else 151)+(len(tech)-1)*20
  for i,line in enumerate(n['desc']):p.append(t(cx,start+i*24,line,17 if w>=280 else 15.5,'#ffffff',400,'middle'))
  p.append('</g>')
 for x,y,s in v.notes:p.append(t(x,y,s,17,'#465e72'))
 ly=v.h-62
 p.append(f'<path d="M45 {ly-25}H1755" fill="none" stroke="#dbe3eb"/>')
 for x,(role,label) in zip([45,240,470,690,900,1160],[('person','Person'),('client','Browser UI'),('app','Server / component'),('store','File data store'),('external','External system'),('planned','Planned process')]):
  p.append(f'<rect x="{x}" y="{ly-2}" width="16" height="16" fill="{COLORS[role]}"/>');p.append(t(x+25,ly+12,label,14,'#465e72'))
 p.append(t(1755,ly+12,'→ Label = action + protocol',14,'#465e72',anchor='end'))
 p.append(t(45,v.h-15,'Notation: C4-informed views · dashed outer line = scope boundary · amber dashed arrow = proposed integration',13,'#657789'))
 p.append('</svg>');return ''.join(p)

svgs={v.key:render(v) for v in VIEWS}
for k,s in svgs.items():(OUT/(k+'.svg')).write_text(s,encoding='utf-8')

# Editable industry-standard diagrams.net document: one page per view.
doc=X.Element('mxfile',host='app.diagrams.net',version='24.7.17',type='device')
for v in VIEWS:
 page=X.SubElement(doc,'diagram',id=v.key,name=v.title)
 model=X.SubElement(page,'mxGraphModel',dx='1800',dy=str(v.h),grid='1',gridSize='10',page='1',pageWidth='1800',pageHeight=str(v.h))
 root=X.SubElement(model,'root');X.SubElement(root,'mxCell',id='0');X.SubElement(root,'mxCell',id='1',parent='0')
 def cell(id,value,x,y,w,h,style):
  c=X.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent='1');X.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
 cell('heading',v.title+'\n'+v.subtitle,40,35,1700,90,'text;html=0;fontSize=24;align=left;whiteSpace=wrap;')
 for i,g in enumerate(v.groups):cell('group'+str(i),g['title']+'\n'+g['detail'],g['x'],g['y'],g['w'],g['h'],'rounded=0;dashed=1;fillColor=#f8fafc;strokeColor=#91a2b3;verticalAlign=top;align=left;spacing=15;fontSize=18;')
 for n in v.nodes:
  label=n['title']+'\n['+n['kind']+']\n'+n['tech']+'\n\n'+'\n'.join(n['desc'])
  cell(n['id'],label,n['x'],n['y'],n['w'],n['h'],f'rounded=0;whiteSpace=wrap;html=0;fillColor={COLORS[n["role"]]};strokeColor={COLORS[n["role"]]};fontColor=#ffffff;fontSize=17;spacing=15;')
 for i,e in enumerate(v.edges):
  c=X.SubElement(root,'mxCell',id='edge'+str(i),value='\n'.join(e['lines']),style='edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;html=0;fontSize=14;labelBackgroundColor=#ffffff;strokeColor='+('#a56e22;dashed=1;' if e['planned'] else '#526579;'),edge='1',parent='1',source=e['a'],target=e['b'])
  geo=X.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'});arr=X.SubElement(geo,'Array',**{'as':'points'})
  for x,y in e['points'][1:-1]:X.SubElement(arr,'mxPoint',x=str(x),y=str(y))
 for i,(x,y,s) in enumerate(v.notes):cell('note'+str(i),s,x,y-20,1690,50,'text;html=0;align=left;fontSize=16;whiteSpace=wrap;')
X.ElementTree(doc).write(OUT/'soilmate-architecture.drawio',encoding='utf-8',xml_declaration=True)

metadata={v.key:{'title':v.title,'subtitle':v.subtitle,'nodes':v.nodes,'edges':v.edges} for v in VIEWS}
(OUT/'architecture-model.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')

HTML='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SoilMate — Architecture</title><style>
*{box-sizing:border-box}body{margin:0;font:15px/1.55 'Segoe UI',Arial,sans-serif;color:#20354a;background:#f3f6fa}button,input{font:inherit}button{cursor:pointer;background:#fff;border:1px solid #becbd8;border-radius:4px;padding:9px 13px;color:#20354a}button[aria-pressed=true]{background:#25394c;color:#fff}button:focus-visible,a:focus-visible{outline:3px solid #b97822;outline-offset:3px}header{padding:20px 25px;background:white;border-bottom:1px solid #d9e2eb}h1{margin:0;font-size:24px}header p{margin:4px 0;color:#5a6d7e}nav{padding:14px 25px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;background:#fff;border-bottom:1px solid #d9e2eb}.spacer{flex:1}.layout{display:grid;grid-template-columns:minmax(0,1fr) 310px}main{padding:16px;min-width:0}.canvas{overflow:auto;max-height:calc(100vh - 180px);background:white;border:1px solid #d9e2eb}.paper{width:100%;min-width:1080px}.paper>svg{display:block;width:100%;height:auto}aside{padding:22px;background:#fff;border-left:1px solid #d9e2eb;overflow-wrap:anywhere}aside h2{font-size:21px;margin:8px 0}h3{font-size:13px;text-transform:uppercase;letter-spacing:.8px;margin-top:22px;color:#5a6d7e}ul{padding-left:20px}li{margin-bottom:7px}.badge{padding:4px 8px;background:#edf2f7;display:inline-block;border-radius:3px;font-size:12px}.tech{font-weight:600}.file{display:block;font:12px/1.5 Consolas,monospace;background:#f4f6f8;padding:7px;margin:6px 0}.tip{font-size:13px;color:#5a6d7e;margin:10px 2px}.notice{background:#fff7e7;border-left:3px solid #a56e22;padding:12px}.sources{padding:20px 25px;background:white;border-top:1px solid #d9e2eb;font-size:13px}.sources a{color:#205f91;margin-right:20px}.tools{padding:24px;max-width:1200px;margin:auto}.search{display:block;border:1px solid #becbd8;padding:9px;width:min(480px,100%);margin:10px 0 20px}table{width:100%;border-collapse:collapse;background:#fff}th,td{padding:12px;border-bottom:1px solid #d9e2eb;text-align:left;vertical-align:top}th{background:#eaf0f5}td:first-child{font-weight:600}.scroll{overflow:auto}[hidden]{display:none!important}@media(max-width:1000px){.layout{grid-template-columns:minmax(0,1fr)}aside{border-left:0;border-top:1px solid #d9e2eb}.canvas{max-height:65vh}nav{padding:12px}.paper{min-width:1200px}header{padding:16px}.tools{padding:16px}}
</style></head><body><header><h1>SoilMate system architecture</h1><p>Three focused views: system structure, backend components, and the proposed NASA data pipeline.</p></header>
<nav aria-label="Architecture views"><button data-view="01-system" aria-pressed="true">1 · System</button><button data-view="02-components" aria-pressed="false">2 · Backend</button><button data-view="03-data-design" aria-pressed="false">3 · Data design</button><button id="tools-tab" aria-pressed="false">Tool register</button><span class="spacer"></span><button id="back" disabled>Previous flow</button><button id="next">Trace relationships</button><button id="zoomout" aria-label="Zoom out">−</button><button id="fit">Fit</button><button id="zoomin" aria-label="Zoom in">+</button><button id="clear">Clear selection</button></nav>
<div class="layout" id="layout"><main><div class="canvas" tabindex="0" aria-label="Scrollable diagram"><div class="paper" id="paper"></div></div><p class="tip" id="status" role="status" aria-live="polite">Click a node to see its responsibility, technology, and connected components.</p></main><aside id="detail" aria-live="polite"></aside></div>
<section id="tools" class="tools" hidden><h2>Technology and tool register</h2><p>Tools are attached to their role in the architecture. Unused alternatives are identified rather than presented as running services.</p><label for="search">Find a tool or responsibility</label><input id="search" class="search" type="search" placeholder="NASA, maps, database, chart…"><p id="count"></p><div class="scroll"><table><thead><tr><th>Tool</th><th>Evidence / status</th><th>Role</th></tr></thead><tbody id="rows"></tbody></table></div></section>
<footer class="sources">Method references: <a href="https://c4model.com/diagrams/container">C4 containers</a><a href="https://c4model.com/diagrams/component">C4 components</a><a href="https://c4model.com/diagrams/notation">C4 notation</a><a href="https://learn.microsoft.com/en-us/azure/well-architected/architect-role/design-diagrams">Microsoft architecture guidance</a><p>Source review: 15 Nov 2026. System and Backend reflect the inspected code. Data design is a proposal. Each scope boundary and relationship is labelled. Hosting is not inferred. This explorer works offline; reference links need internet access.</p></footer>
<script>const diagrams=__SVGS__,model=__MODEL__,evidence=__EVIDENCE__,tools=__TOOLS__;
const $=id=>document.getElementById(id), esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let current='01-system',flow=-1,scale=100;
function lists(title,values,cls=''){if(!values?.length)return '';return '<h3>'+title+'</h3>'+(cls?values.map(s=>'<span class="'+cls+'">'+esc(s)+'</span>').join(''):'<ul>'+values.map(s=>'<li>'+esc(s)+'</li>').join('')+'</ul>')}
function overview(){const m=model[current];$('detail').innerHTML='<span class="badge">'+(current==='03-data-design'?'Proposed integration design':'Current implementation')+'</span><h2>'+esc(m.title)+'</h2><p>'+esc(m.subtitle)+'</p><h3>Reading the diagram</h3><ul><li>Each box names an architectural element, its type, technology, and responsibility.</li><li>Arrows show one labelled action in one direction.</li><li>A dashed outer boundary groups elements by system or process.</li><li>Amber marks planned work.</li></ul><p>Select a node to highlight its direct relationships, or trace each relationship in order.</p>'+(current==='03-data-design'?'<p class="notice">The current NASA importer, data-cleaning script and forecasting script are empty. This view proposes their interfaces; it does not claim a working live pipeline.</p>':'<p class="notice">The application is one server-rendered Python web app. Its internal modules are not separate deployed services.</p>')}
function clear(){document.querySelectorAll('.arch-node,.relationship').forEach(el=>{el.classList.remove('muted','selected')});flow=-1;$('back').disabled=true;$('next').textContent='Trace relationships';$('status').textContent='Click a node to see its responsibility, technology, and connected components.';overview()}
function focusNode(id){const m=model[current],n=m.nodes.find(n=>n.id===id),d=n.ref?evidence[n.ref]:null,related=m.edges.filter(e=>e.a===id||e.b===id),near=new Set([id,...related.flatMap(e=>[e.a,e.b])]);document.querySelectorAll('.arch-node').forEach(el=>{el.classList.toggle('muted',!near.has(el.dataset.node));el.classList.toggle('selected',el.dataset.node===id)});document.querySelectorAll('.relationship').forEach(el=>el.classList.toggle('muted',el.dataset.from!==id&&el.dataset.to!==id));$('detail').innerHTML='<span class="badge">'+esc(n.kind)+'</span><h2>'+esc(n.title)+'</h2><p class="tech">'+esc(n.tech)+'</p><p>'+esc(n.desc.join(' '))+'</p>'+(n.notes?'<p class="notice">'+esc(n.notes)+'</p>':'')+(d?lists('Inputs',d.inputs)+lists('Outputs',d.outputs)+lists('Source evidence',d.files,'file'):'')+lists('Connected relationships',related.map(e=>m.nodes.find(n=>n.id===e.a).title+' → '+m.nodes.find(n=>n.id===e.b).title+': '+e.lines.join(' ')));$('status').textContent=n.title+' — showing direct relationships.'}
function openView(k){current=k;$('layout').hidden=false;$('tools').hidden=true;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.view===k));$('tools-tab').setAttribute('aria-pressed','false');$('paper').innerHTML=diagrams[k];document.querySelectorAll('.arch-node').forEach(el=>{el.addEventListener('click',()=>focusNode(el.dataset.node));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();focusNode(el.dataset.node)}})});clear()}
function trace(index){const m=model[current];flow=(index+m.edges.length)%m.edges.length;const e=m.edges[flow];document.querySelectorAll('.arch-node').forEach(el=>{el.classList.toggle('muted',![e.a,e.b].includes(el.dataset.node));el.classList.remove('selected')});document.querySelectorAll('.relationship').forEach(el=>el.classList.toggle('muted',el.dataset.from!==e.a||el.dataset.to!==e.b));const a=m.nodes.find(n=>n.id===e.a),b=m.nodes.find(n=>n.id===e.b);$('detail').innerHTML='<span class="badge">Relationship '+(flow+1)+' / '+m.edges.length+'</span><h2>'+esc(a.title)+' → '+esc(b.title)+'</h2><p>'+esc(e.lines.join(' '))+'</p><h3>Relationship type</h3><p>'+(e.planned?'Proposed integration':'Current runtime relationship')+'</p><p>This follows the arrow direction. It is one connection in the architecture, not a claim that every connection runs in sequence.</p>';$('status').textContent='Connection '+(flow+1)+' / '+m.edges.length+': '+e.lines.join(' ');$('back').disabled=false;$('next').textContent='Next relationship'}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>openView(b.dataset.view));$('next').onclick=()=>{if($('layout').hidden)openView(current);trace(flow+1)};$('back').onclick=()=>trace(flow-1);$('clear').onclick=clear;
function zoom(v){scale=Math.max(70,Math.min(200,v));$('paper').style.width=scale+'%';$('fit').textContent=scale===100?'Fit':scale+'%'}$('zoomin').onclick=()=>zoom(scale+20);$('zoomout').onclick=()=>zoom(scale-20);$('fit').onclick=()=>zoom(100);
function renderTools(){const q=$('search').value.toLowerCase(),rows=tools.filter(t=>t.join(' ').toLowerCase().includes(q));$('rows').innerHTML=rows.map(t=>'<tr>'+t.map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('');$('count').textContent=rows.length+' / '+tools.length+' tool entries'}
$('tools-tab').onclick=()=>{$('layout').hidden=true;$('tools').hidden=false;document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed','false'));$('tools-tab').setAttribute('aria-pressed','true')};$('search').oninput=renderTools;renderTools();openView(current);
</script></body></html>'''
HTML=HTML.replace('__SVGS__',json.dumps(svgs)).replace('__MODEL__',json.dumps(metadata)).replace('__EVIDENCE__',json.dumps(OLD['nodes'])).replace('__TOOLS__',json.dumps(OLD['tools']))
(OUT/'soilmate-architecture.html').write_text(HTML,encoding='utf-8')
(OUT/'README.md').write_text('''# SoilMate architecture — revision 2

The architecture was redrawn using separate structural and data views, following the C4 model and Microsoft architecture diagram guidance. Source reviewed on 15 November 2026.

## Files

- `01-system.svg` / `.png`: main C4-informed container diagram. It shows the grower, browser-delivered dashboard, single Python web application, local file store, external asset providers, system boundary and labelled relationships.
- `02-components.svg` / `.png`: zoom into the one Python application. The route/page handlers call Overview readers, the Analysis builder and the map builder. All are in the same application process. Local datasets appear outside that process boundary.
- `03-data-design.svg` / `.png`: proposed NASA acquisition and preparation architecture. Raw files, checked tables, the current serving interface and an optional unconnected forecast branch are distinguished.
- `soilmate-architecture.html`: offline interactive explorer. Switch views, click nodes, highlight their neighbours, trace labelled connections, zoom and search the full tool register.
- `soilmate-architecture.drawio`: editable diagrams.net source with three pages.
- `architecture-model.json`: structured nodes and relationships.
- `build.py` and `render_svg.ps1`: reproducible vector generation and offline Windows PNG renderer. The generator reuses the repository evidence inventory in `../architecture/architecture-data.json`. A copy is included as `evidence-data.json` for standalone use.

## Scope and interpretation

The System and Backend views represent the inspected source. Data design is a proposal, not a claim that live NASA ingestion is implemented. No hosting provider, SQL database, queue, authentication service or notification service is invented. Technologies are labelled on architectural elements instead of represented as separate services. In C4, a container is an application or a data store; it does not mean a Docker container.

The client container represents browser-executed HTML/CSS/JavaScript delivered by the server. It is not an independently hosted SPA. Pages are rendered with Jinja2. Overview uses fetch to obtain HTML fragments. Analysis receives chart JSON inside HTML and uses the local Plotly.js bundle. Maps are built on request with Folium and displayed in a Leaflet iframe. The server reads a filesystem store, not a database. Analysis uses an in-process file-change-aware cache, not Redis. Uvicorn is declared as a runner; no production process configuration is supplied.

The current Simulation panel selects earlier stored conditions and changes imagery; it is not a future prediction. The forecasting script is empty and no models are present. NASA products appear as source names in the supplied data; their precise versions, coverage, quality rules and lineage remain to be validated before integration. The ESI scale and thresholds need domain review, as recorded in `docs/analysis.md`. The starter manifest includes unused alternatives, which are separated in the tool register.

## Diagram conventions

- A coloured block is a typed architectural element with a technology and a short responsibility.
- A dashed outer rectangle is a scope boundary, not a network or deployment assertion.
- A solid directional arrow is a current relationship. Its label states the action and protocol/interface.
- An amber dashed arrow is a proposed integration. Amber blocks are proposed processes or stores. The Data design view mixes the existing file-reader interface with proposed upstream writers; its title explicitly marks this scope.
- File access and Python calls are labelled as such; they are not presented as HTTP or separate services.
- Request and response relationships in the main view are separate arrows. Connection tracing explores individual relationships; it is not an execution sequence.

## Sources used for the redraw

- https://c4model.com/diagrams/container — applications/data stores, technology, responsibilities and communication.
- https://c4model.com/diagrams/component — decomposition within one application container.
- https://c4model.com/diagrams/notation — element types, labels, technologies, direction and diagram keys.
- https://learn.microsoft.com/en-us/azure/well-architected/architect-role/design-diagrams — progressive detail, clear scope, meaningful arrows and accurate notation.

Original wording and drawings are used; the reference pages informed the approach.

## Project evidence

`backend/main.py`, `backend/analysis.py`, `backend/*_map.py`, `dashboard/templates/`, `dashboard/static/`, `data/processed/`, `data/Geo/`, `docs/analysis.md`, `analytics/`, `models/`, and `requirements.txt`. No credentials are included.
''',encoding='utf-8')
(OUT/'evidence-data.json').write_text(json.dumps(OLD,indent=2),encoding='utf-8')
print('Built three architecture views, interactive explorer, editable diagrams.net source and evidence notes.')
