// Three-panel, silhouette-first map. No private hangar data leaves this page.
// The silhouettes were generated offline from RSI's official model URLs;
// unillustrated models get an explicitly marked generic placeholder.
function fleetMapSvg(fleet,showSecondary,publicShips=referenceModels){
 if(!fleet.length)throw Error('Import a fleet before exporting its graphic.');
 const W=3840,M=55,GAP=24,PW=(W-2*M-2*GAP)/3;
 const ROLE_W=232,INNER=16,TIER_IDS=['solo','duo','small','multi','fleet','ground','unknown'];
 const TIER_HEADS=['SOLO','PAIR','3–4','5–8','9+','GROUND','OTHER'];
 const CELL_W=(PW-ROLE_W-INNER*2)/TIER_IDS.length;
 // Sprite artwork stays smaller than its layout pitch. The transparent edge
 // around each icon leaves a visible gutter between adjacent ship hulls.
 const ICON=31,STEP_X=33,STEP_Y=34,HEAD=148,PANEL_HEAD=56,GROUP_HEAD=37,ROW_MIN=54;
 const FOOT=166,PAD_BOTTOM=24;
 // Keep related careers adjacent where practical, but distribute the densest
 // groups among panels so the image reads as a landscape, not a skyscraper.
 // FLEX contains far more hulls than any other lane; it gets its own column
 // alongside the smaller ground-vehicle category.
 const groups=[['FLEX','GROUND'],['COMBAT','INDUSTRY','RACING'],['TRANSPORT','SUPPORT','EXPLORATION']];
 const publicByKey=new Map();
 for(const p of publicShips||[]){
  if(p?.name)publicByKey.set(normalizeAlias(p.name),{...p,owned:false,count:0});
 }
 for(const s of fleet){
  const k=normalizeAlias(s.officialName||s.name);
  if(!k)continue;
  const original=publicByKey.get(k);
  if(original?.owned){original.count++;continue}
  publicByKey.set(k,{...(original||{}),...s,name:original?.name||s.officialName||s.name,owned:true,count:1});
 }
 const all=[...publicByKey.values()].sort((a,b)=>a.name.localeCompare(b.name));
 const roleEntries=(s,r)=>{
  if(s.role===r)return 'primary';
  if(!showSecondary)return '';
  if((s.secondary||[]).includes(r))return 'secondary';
  const module=(s.moduleRoles||[]).find(m=>m.role===r);
  return module?(module.status==='planned'?'planned':'module'):'';
 };
 const panelData=groups.map(group=>group.map(id=>{
  const lane=lanes.find(l=>l.id===id);
  return {id,label:lane.label,roles:lane.roles.map(role=>{
   const cells=TIER_IDS.map(t=>all.flatMap(s=>{
    const kind=roleEntries(s,role.id);
    return kind && (TIER_IDS.includes(s.tier)?s.tier:'unknown')===t?[{...s,kind}]:[];
   }));
   const perCell=Math.max(1,Math.floor((CELL_W-4)/STEP_X));
   const lines=Math.max(1,...cells.map(c=>Math.ceil(c.length/perCell)));
   return {role,cells,height:Math.max(ROW_MIN,lines*STEP_Y+17)};
  })};
 }));
 const panelHeight=lanegroups=>PANEL_HEAD+lanegroups.reduce((h,l)=>h+GROUP_HEAD+l.roles.reduce((n,r)=>n+r.height,0)+11,0)+PAD_BOTTOM;
 const maxPanelH=Math.max(...panelData.map(panelHeight));
 const H=HEAD+maxPanelH+FOOT;
 const srcAssets=BUNDLE.silhouetteAssets||{},srcNames=BUNDLE.silhouetteNames||{};
 const assetFor=name=>srcNames[normalizeName(name)]||srcNames[normalizeAlias(name)]||'';
 const assetForShip=s=>assetFor(s.officialName)||assetFor(s.name);
 const imageIds=new Set(all.map(assetForShip).filter(id=>Boolean(srcAssets[id])));
 const svgEsc=s=>String(s??'').replace(/[\u0000-\u001f\u007f]/g,' ').replace(/[&<>"']/g,
  ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[ch]));
 const nodes=[],out=s=>nodes.push(s);
 const text=(x,y,v,size=15,color='#f0f5ff',weight=500,extra='')=>
  `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-size="${size}" fill="${color}" font-weight="${weight}" ${extra}>${svgEsc(v)}</text>`;
 out(`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Inter,Segoe UI,Arial,sans-serif" role="img" aria-label="Star Citizen fleet career silhouette map">`);
 out('<defs><linearGradient id="mapBg" x2="1" y2="1"><stop stop-color="#091524"/><stop offset=".62" stop-color="#0e1b2d"/><stop offset="1" stop-color="#121833"/></linearGradient></defs>');
 for(const id of imageIds){
  out(`<defs><image id="ship-${id}" width="${ICON}" height="${ICON}" x="0" y="0" href="data:image/png;base64,${srcAssets[id]}"/></defs>`);
 }
 out(`<rect width="${W}" height="${H}" fill="url(#mapBg)"/>`);
 out(`<rect x="${M}" y="43" width="5" height="71" rx="2.5" fill="#87dbdc"/>`);
 out(text(M+23,67,'STAR CITIZEN  /  FLEET ATLAS',17,'#8cbbd0',750,'letter-spacing="2.5"'));
 out(text(M+23,113,'FLEET CAREER MAP',46,'#f6faff',800,'letter-spacing="1.4"'));
 out(text(W-M,71,'BRIGHT  =  OWNED     ·     FADED  =  NOT OWNED',18,'#b5d2dc',700,'text-anchor="end" letter-spacing="1.3"'));
 out(text(W-M,106,'All cataloged ships · career / crew layout · secondary roles optional',17,'#819eaf',480,'text-anchor="end"'));
 const tile=(s,x,y)=>{
  const asset=assetForShip(s),hasImage=Boolean(srcAssets[asset]),dim=s.owned?1:0.13;
  const module=s.kind==='module'||s.kind==='planned',muted=s.kind==='secondary';
  const opacity=(module?0.74:muted?0.83:1)*dim;
  const title=`${s.name}${s.count>1?' ×'+s.count:''} · ${s.owned?'In your fleet':'Not in imported fleet'} · ${s.kind==='primary'?'Primary':s.kind==='secondary'?'Secondary':s.kind==='planned'?'Planned module':'Module option'}${hasImage?'':' · Silhouette not yet available'}`;
  out(`<g opacity="${opacity}" aria-label="${svgEsc(title)}"><title>${svgEsc(title)}</title>`);
  if(hasImage)out(`<use xlink:href="#ship-${asset}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)})"/>`);
  else{
   out(`<path d="M${x+14} ${y+4} l10 14 -10 8 -10 -8 z" fill="none" stroke="#d4e3e8" stroke-width="2"/>`);
   out(text(x+14,y+20,'?',13,'#d4e3e8',700,'text-anchor="middle"'));
  }
  if(module)out(`<path d="M${x+2} ${y+29}h25" stroke="${s.kind==='planned'?'#edb36e':'#b29dff'}" stroke-width="3" stroke-dasharray="5 3"/>`);
  out('</g>');
 };
 panelData.forEach((panel,i)=>{
  const x=M+i*(PW+GAP);
  out(`<rect x="${x}" y="${HEAD}" width="${PW}" height="${maxPanelH}" rx="12" fill="#0d1b2a" stroke="#32516a" stroke-width="2"/>`);
  out(text(x+INNER,HEAD+35,'PROFESSION',16,'#9fbac9',750,'letter-spacing=".8"'));
  TIER_HEADS.forEach((label,j)=>out(text(x+ROLE_W+INNER+(j+.5)*CELL_W,HEAD+35,label,11.8,'#9fbac9',760,'text-anchor="middle"')));
  let y=HEAD+PANEL_HEAD;
  panel.forEach(lane=>{
   const color=colors[lane.id]||'#91c5d3';
   out(`<rect x="${x+7}" y="${y}" width="${PW-14}" height="${GROUP_HEAD}" fill="${color}" fill-opacity=".15"/>`);
   out(`<rect x="${x+7}" y="${y}" width="4" height="${GROUP_HEAD}" fill="${color}"/>`);
   out(text(x+18,y+25,lane.label.toUpperCase(),18,color,770,'letter-spacing=".7"'));
   y+=GROUP_HEAD;
   lane.roles.forEach((entry,ri)=>{
    const cellY=y+5;
    out(`<rect x="${x+7}" y="${y}" width="${PW-14}" height="${entry.height-1}" fill="${ri%2?'#0d2030':'#102537'}"/>`);
    out(`<rect x="${x+ROLE_W+INNER}" y="${cellY}" width="${PW-ROLE_W-INNER*2}" height="${entry.height-10}" rx="3" fill="#0d7779" fill-opacity=".24"/>`);
    out(text(x+18,y+30,entry.role.label,15,'#d7e9f0',520));
    const rowFill=entry.cells.reduce((n,cell)=>n+cell.length,0);
    if(!rowFill)out(text(x+PW-20,y+30,'·',18,'#557785',400,'text-anchor="end"'));
    entry.cells.forEach((cell,j)=>{
     const cX=x+ROLE_W+INNER+j*CELL_W+6;
     const count=Math.max(1,Math.floor((CELL_W-4)/STEP_X));
     if(j>0)out(`<line x1="${(cX-6).toFixed(1)}" y1="${y+7}" x2="${(cX-6).toFixed(1)}" y2="${y+entry.height-8}" stroke="#2e5661" stroke-opacity=".45"/>`);
     cell.forEach((s,n)=>tile(s,cX+(n%count)*STEP_X,y+9+Math.floor(n/count)*STEP_Y));
    });
    y+=entry.height;
   });
   y+=11;
  });
 });
 const bottom=H-FOOT;
 out(`<line x1="${M}" y1="${bottom+28}" x2="${W-M}" y2="${bottom+28}" stroke="#28485b" stroke-width="2"/>`);
 const keyLabels=[['#f6fbff','OWNED'],['#546c79','NOT OWNED'],['#c9b5ff','MODULE OPTION'],['#f1bf76','PLANNED OPTION']];
 keyLabels.forEach(([c,label],i)=>{const x=M+i*450;out(`<circle cx="${x+8}" cy="${bottom+62}" r="7" fill="${c}"/>`);out(text(x+26,bottom+67,label,15,'#bbd1df',650));});
 out(text(W-M,bottom+67,'Model unavailable? A small diamond indicates no verified silhouette yet.',14,'#879ead',450,'text-anchor="end"'));
 out(text(M,H-57,'MADE BY THE COMMUNITY · Unofficial Star Citizen fan project · Not affiliated with Cloud Imperium Games',14,'#94b1c4',650));
 out(text(M,H-29,'Star Citizen and ship designs belong to CIG/RSI · Silhouettes from available RSI Holoviewer models · Model-link index: DragonAceNL',13,'#7795a9',450));
 out(text(W-M,H-29,`${imageIds.size} distinct ship outlines in this export · no account data shared`,14,'#7795a9',480,'text-anchor="end"'));
 out('</svg>');
 return {svg:nodes.join(''),width:W,height:H};
}
