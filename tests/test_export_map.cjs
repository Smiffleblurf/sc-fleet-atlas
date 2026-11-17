// Synthetic-data test for the local-only share graphic. Never add real hangar data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'catalog/ship-roles.json'), 'utf8'));
const html = fs.readFileSync(path.join(root, 'src/template.html'), 'utf8');
const start = html.indexOf('const svgEsc=');
const end = html.indexOf('let shareGraphic=', start);
assert.ok(start > 0 && end > start, 'Fleet graphic implementation must be present');

const definitions = `
const lanes=${JSON.stringify(catalog.lanes)};
const roleList=lanes.flatMap(l=>l.roles.map(r=>({...r,lane:l.id,laneLabel:l.label})));
const roleById=Object.fromEntries(roleList.map(r=>[r.id,r]));
roleById.review={id:'review',label:'Needs classification',lane:'REVIEW'};
const tiers=[['solo','Solo • 1'],['duo','Pair • 2'],['small','Small • 3–4'],['multi','Multi • 5–8'],['fleet','Fleet • 9+'],['ground','Ground / suit'],['unknown','Unassigned']];
const tierLabels=Object.fromEntries(tiers);
const colors={COMBAT:'#b28afe',TRANSPORT:'#67baff',EXPLORATION:'#75c8c7',INDUSTRY:'#e4b578',SUPPORT:'#82d4bb',RACING:'#ed91ca',GROUND:'#a5b6d3',FLEX:'#b7a1ec',REVIEW:'#fa9b86'};
`;
const build = vm.runInNewContext(definitions + html.slice(start, end) + '\nfleetMapSvg;', {});
const make = (name, tier, role, secondary=[], moduleRoles=[]) => ({name,ship_code:name,tier,role,secondary,moduleRoles});
const example = [
  make('Galaxy', 'multi', 'generalist', [], [{role:'medical',status:'available'},{role:'refining',status:'planned'}]),
  make('Liberator', 'fleet', 'carrier', ['fuel','repair']),
  make('Retaliator', 'multi', 'gunship', [], [{role:'strike',status:'available'},{role:'freight',status:'available'}]),
  make('Prospector', 'solo', 'mining'),make('Vulture', 'solo', 'salvage'),
  make('Carrack', 'fleet', 'expedition'),make('Cutlass Black', 'small', 'generalist'),
  make('C8R Pisces', 'duo', 'medical'),make('Arrow', 'solo', 'fighter'),
  make('Gladius', 'solo', 'fighter'),make('Mole', 'multi', 'mining'),
  make('Hull C', 'fleet', 'heavyfreight'),make('Ursa', 'ground', 'groundutility'),
  make('Razor', 'solo', 'racing'),make('Reliant Mako', 'duo', 'reporting'),
  make('Starfarer', 'fleet', 'fuel'),make('Reclaimer', 'fleet', 'salvage'),
  make('Apollo', 'multi', 'medical'),make('Nomad', 'solo', 'courier'),
  make('Pioneer', 'fleet', 'construction'),
];
example[0].pledge_id='PRIVATE_PLEDGE_ID_MUST_NOT_APPEAR';
const {svg,width,height} = build(example, true);
assert.ok(svg.startsWith('<svg ') && svg.endsWith('</svg>'));
assert.equal(width, 2400);
assert.ok(height > 900 && height < 3000);
for(const label of ['YOUR FLEET, BY PURPOSE.','Galaxy','Liberator','COMBAT &amp; SECURITY','PL1','M1','S1']){
  assert.ok(svg.includes(label), `Missing expected label: ${label}`);
}
assert.ok(!svg.includes('PRIVATE_PLEDGE_ID_MUST_NOT_APPEAR'));
assert.ok(!svg.includes('shiplist.json'));
const withoutSecondary=build(example, false).svg;
assert.ok(!withoutSecondary.includes('PL1'));
assert.ok(!withoutSecondary.includes('M1'));
assert.ok(!withoutSecondary.includes('S1'));
assert.throws(()=>build([],true));
console.log('Fleet image generation: synthetic-data checks passed');

// Optional local visual QA. Sharp is not a runtime dependency of Fleet Atlas.
if(process.env.SCFA_PREVIEW_PATH){
  require('sharp')(Buffer.from(svg)).png().toFile(process.env.SCFA_PREVIEW_PATH).then(
    ()=>console.log('Rendered preview to',process.env.SCFA_PREVIEW_PATH),
    err=>{console.error(err);process.exitCode=1;}
  );
}
