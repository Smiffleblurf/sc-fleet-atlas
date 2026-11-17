// Synthetic-only fleet fixtures; never check in an actual HangarXPLOR export.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'catalog/ship-roles.json'), 'utf8'));
const modelIndex = JSON.parse(fs.readFileSync(path.join(root, 'catalog/holoviewer-models.json'), 'utf8'));
const packed = JSON.parse(fs.readFileSync(path.join(root, 'assets/ship-silhouettes.json'), 'utf8'));
const code = fs.readFileSync(path.join(root, 'src/share-map.js'), 'utf8');
const aliases = x=>String(x||'').toLowerCase().normalize('NFKD').replace(/[^a-z0-9]/g,'');
const normalizeAlias = x=>aliases(String(x||'').replace(/^Constellation Mk IV /i,'Constellation '));
const assets=packed.images, names={};
for(const item of modelIndex.models){
  const id=crypto.createHash('sha256').update(item.url).digest('hex').slice(0,20);
  if(assets[id]){
    names[aliases(item.name)]=id;
  }
}
const lanes=catalog.lanes, roleList=lanes.flatMap(l=>l.roles.map(r=>({...r,lane:l.id})));
const context={
  BUNDLE:{silhouetteAssets:assets,silhouetteNames:names},
  lanes,roleList,normalizeName:aliases,normalizeAlias,
  colors:{COMBAT:'#b28afe',TRANSPORT:'#67baff',EXPLORATION:'#75c8c7',INDUSTRY:'#e4b578',SUPPORT:'#82d4bb',RACING:'#ed91ca',GROUND:'#a5b6d3',FLEX:'#b7a1ec'},
};
const build=vm.runInNewContext(code+'\nfleetMapSvg;',context);
const make=(name,tier,role,secondary=[],moduleRoles=[])=>({name,ship_code:name,tier,role,secondary,moduleRoles});
const example=[
  make('Galaxy','multi','generalist',[],[{role:'medical',status:'available'},{role:'refining',status:'planned'}]),
  make('Liberator','fleet','carrier',['fuel','repair']),
  make('Retaliator','multi','gunship',[],[{role:'strike',status:'available'},{role:'freight',status:'available'}]),
  make('Prospector','solo','mining'),make('Vulture','solo','salvage'),
  make('Carrack','fleet','expedition'),make('Cutlass Black','small','generalist'),
  make('C8R Pisces','duo','medical'),make('Arrow','solo','fighter'),
  make('Gladius','solo','fighter'),make('Mole','multi','mining'),
  make('Hull C','fleet','heavyfreight'),make('Ursa','ground','groundutility'),
  make('Razor','solo','racing'),make('Reliant Mako','duo','reporting'),
  make('Starfarer','fleet','fuel'),make('Reclaimer','fleet','salvage'),
  make('Apollo','multi','medical'),make('Nomad','solo','courier'),
  make('Pioneer','fleet','construction'),
];
const refs=fs.readFileSync(path.join(root,'catalog/reference-ships.txt'),'utf8').split('\n')
  .filter(line=>line.includes('|')).map(line=>{
    const name=line.split('|')[0];
    return {name,...(catalog.rulebook[name]||{role:'generalist',tier:'solo',secondary:[]})};
  });
example[0].pledge_id='PRIVATE_PLEDGE_ID_MUST_NOT_APPEAR';
const {svg,width,height}=build(example,true,refs);
assert.ok(svg.startsWith('<svg ')&&svg.endsWith('</svg>'));
assert.equal(width,3840);
assert.ok(height>1300&&height<6500);
for(const label of ['FLEET CAREER MAP','Galaxy','Liberator','COMBAT &amp; SECURITY','Planned module','NOT OWNED']){
  assert.ok(svg.includes(label),'Missing expected text: '+label);
}
assert.ok(svg.includes('<use xlink:href="#ship-'),'Images from RSI models should be embedded');
assert.ok(svg.includes('opacity="0.13"'),'Unowned craft need a clear visual fade');
assert.ok(svg.includes('Gladius'),'Hover information must identify silhouettes');
assert.ok(!svg.includes('other models'),'No truncated +N blocks');
assert.ok(!svg.includes('PRIVATE_PLEDGE_ID_MUST_NOT_APPEAR'));
assert.ok(!svg.includes('shiplist.json'));
const primaryOnly=build(example,false,refs).svg;
assert.ok(!primaryOnly.includes('Planned module'));
assert.ok(!primaryOnly.includes('Module option'));
assert.throws(()=>build([],true));
console.log('Silhouette career map: synthetic fixtures passed.');

// Optional visual proof, using a synthetic fleet. Sharp is not a runtime dependency.
if(process.env.SCFA_PREVIEW_PATH){
  require('sharp')(Buffer.from(svg)).resize({width:2200}).png().toFile(process.env.SCFA_PREVIEW_PATH).then(
    ()=>console.log('Rendered preview to',process.env.SCFA_PREVIEW_PATH),
    err=>{console.error(err);process.exitCode=1;}
  );
}
