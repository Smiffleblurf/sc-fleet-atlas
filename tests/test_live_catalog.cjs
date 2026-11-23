// Public ship classification regression tests; no private hangar data.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const src=fs.readFileSync(path.join(root,'src/template.html'),'utf8');
const cat=JSON.parse(fs.readFileSync(path.join(root,'catalog/ship-roles.json'),'utf8'));
const a=src.indexOf('function englishLabel(value)'),b=src.indexOf('function rebuildReferenceModels(',a);
assert.ok(a>=0&&b>a);
const roleById=Object.fromEntries(cat.lanes.flatMap(l=>l.roles.map(r=>[r.id,r])));
const context={roleById,KNOWN_GROUND:/^(roc|ursa|nox)/i,validRole:id=>Boolean(roleById[id]),
 tierForCount:(crew,ground)=>ground?'ground':crew===null?'unknown':crew<=1?'solo':crew===2?'duo':crew<=4?'small':crew<=8?'multi':'fleet'};
const classify=vm.runInNewContext(src.slice(a,b)+'\nclassifyPublicShip;',context);
const hyun=classify({name:'Hyun',type:{en_EN:'Multi'},foci:[{en_EN:'Generalist'}],
 description:{en_EN:'Industrial vessel coming standard with equipment for both mining and salvaging.'},
 crew:{min:1,max:1},manufacturer:{name:'Gatac Manufacture'}});
assert.equal(hyun.role,'mining');assert.equal(hyun.tier,'solo');assert.deepEqual(Array.from(hyun.secondary),['salvage']);
const focusHybrid=classify({name:'Future Industry Hybrid',type:'Industrial',foci:[{en_EN:'Mining / Salvage'}],crew:{max:2}});
assert.equal(focusHybrid.role,'mining');assert.deepEqual(Array.from(focusHybrid.secondary),['salvage']);
const generalist=classify({name:'Cargo Generalist',type:'Multi',foci:[{en_EN:'Generalist'}],
 description:'Carries mined ore and salvaged goods, with future modular upgrades.',crew:{max:1}});
assert.equal(generalist.role,'generalist');assert.deepEqual(Array.from(generalist.secondary),[]);
assert.deepEqual(cat.rulebook['Hyūn'],cat.codeRules['GAMA_Hyun']);
console.log('Hyūn and hybrid-role inference pass.');
