"""Modèles des pages web de CAT.EXE (cartes, triangulation, graphe d'enquête). Données seulement, aucun code Python."""

VANTAGE_TPL = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cat.exe · Position du photographe</title>
__LEAFLET__
<style>
:root{--bg:#07081a;--p:#0e1028;--l:#2b3158;--t:#e4e9ff;--m:#7480a8;--g:#00e5ff;--k:#b388ff;--y:#ffc861}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--t);font-family:system-ui,-apple-system,sans-serif}
header{padding:12px 16px;border-bottom:1px solid var(--l);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header b{font-family:monospace;color:var(--g);font-size:16px}header span{color:var(--m);font-size:13px}header a{margin-left:auto;color:#8a8cff;font:13px monospace}
.wrap{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;padding:12px}
@media(max-width:900px){.wrap{grid-template-columns:1fr}}
.card{background:var(--p);border:1px solid var(--l);border-radius:12px;padding:12px;min-width:0}
#ph{position:relative;cursor:crosshair;user-select:none}#ph img{width:100%;display:block;border-radius:8px}
.vl{position:absolute;top:0;bottom:0;width:2px;margin-left:-1px;background:var(--k);pointer-events:none;box-shadow:0 0 6px var(--k)}
.vl i{position:absolute;top:6px;left:5px;background:var(--k);color:#fff;font:700 11px monospace;padding:2px 6px;border-radius:4px;font-style:normal;white-space:nowrap}
.vl.pend{background:var(--y);box-shadow:0 0 6px var(--y)}.vl.pend i{background:var(--y);color:#000}
#map{height:560px;border-radius:8px}
.steps{font-size:13px;color:var(--m);line-height:1.6}.steps b{color:var(--g)}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}
input,select{background:#14173a;border:1px solid var(--l);color:var(--t);padding:8px 10px;border-radius:8px;font:13px monospace}
button{background:var(--g);color:#000d1a;border:0;padding:9px 14px;border-radius:8px;font-weight:700;cursor:pointer}
button.gh{background:transparent;color:var(--t);border:1px solid var(--l)}
#lm div{display:flex;justify-content:space-between;gap:8px;padding:6px 8px;border:1px solid var(--l);border-radius:8px;margin-top:6px;font:12px monospace}
#lm a{color:#ff5c7a;text-decoration:none}
#sr div{padding:7px 8px;border-bottom:1px solid var(--l);cursor:pointer;font-size:13px}#sr div:hover{color:var(--g)}
#out{font-size:14px;line-height:1.65;margin-top:6px}#out a{color:var(--g)}
#out .big{font-size:20px;font-weight:700;color:var(--k);font-family:monospace}
#out .note{color:var(--y);font-size:13px}
.st{font:13px monospace;color:var(--y);margin-top:8px}
.leg{font:12px monospace;color:var(--m);margin-top:6px;display:flex;gap:12px;flex-wrap:wrap}
</style></head><body>
<header><b>CAT.exe // POSITION DU PHOTOGRAPHE</b><span>où se tenait la personne qui a pris la photo</span><a id="dc" target="_blank"></a></header>
<div class="wrap">
 <div class="card">
  <div id="ph"><img id="img" src="data:image/jpeg;base64,__IMG__" alt=""></div>
  <div class="st" id="st"></div>
  <div class="steps" style="margin-top:8px">
   <b>1.</b> Clique le sommet d'un repère reconnaissable dans la photo (tour, clocher, antenne…).<br>
   <b>2.</b> Indique où il se trouve : cherche son nom à droite, ou clique dessus sur la carte.<br>
   <b>3.</b> 3 repères minimum (4 c'est mieux), bien répartis de gauche à droite, puis <b>Calculer</b>.
  </div>
  <div id="lm"></div>
  <div class="row"><span style="font-size:13px;color:var(--m)">Focale</span>
   <select id="fovm"><option value="auto">inconnue (calcul auto)</option><option value="fix">je la connais</option></select>
   <input id="f35" type="number" min="8" max="800" placeholder="mm éq. 35 mm" style="width:140px"></div>
  <div class="row"><button id="calc">📷 Calculer la position</button><button class="gh" id="reset">Effacer les repères</button></div>
  <div id="out"></div>
 </div>
 <div class="card">
  <div class="row"><input id="q" placeholder="chercher un repère (ex. Tour Eiffel)" style="flex:1"><button class="gh" id="go">Chercher</button></div>
  <div id="sr"></div>
  <div id="map"></div>
  <div class="leg"><span style="color:#00e5ff">● GPS du fichier</span><span style="color:#b388ff">● GeoCLIP n°1</span><span style="color:#ffc861">● autres pistes</span><span style="color:#b388ff">▦ zone du photographe</span></div>
 </div>
</div>
<script>
const D=__DATA__;
const $=s=>document.querySelector(s), esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const R2D=180/Math.PI, D2R=Math.PI/180;
const wrap=a=>{a=(a+Math.PI)%(2*Math.PI);if(a<0)a+=2*Math.PI;return a-Math.PI;};
const CARD=d=>['nord','nord-est','est','sud-est','sud','sud-ouest','ouest','nord-ouest'][Math.floor(((d%360+360)%360+22.5)/45)%8];
$('#dc').href=D.discord;$('#dc').textContent='discord Cat.exe';
const img=$('#img'), ph=$('#ph');
let pts=(D.prefill||[]).slice(), pend=null;
const map=catMap('map',{center:D.center||[46.6,2.4],zoom:D.center?13:5,clickCoords:false});
const base=L.featureGroup().addTo(map), lmL=L.layerGroup().addTo(map), resL=L.layerGroup().addTo(map);
(D.layers||[]).forEach(p=>{L.circleMarker([p.lat,p.lon],{radius:7,color:p.c,fillOpacity:.85}).bindPopup(esc(p.label)).addTo(base);if(p.r)L.circle([p.lat,p.lon],{radius:p.r,color:p.c,fillOpacity:.05,weight:1,dashArray:'4 4'}).addTo(base);});
if(D.gps&&D.exifDir!=null)cone(D.gps[0],D.gps[1],D.exifDir*D2R,(D.fov||60)*D2R,700,'#00e5ff',base);
const fitAll=()=>{const g=L.featureGroup([...base.getLayers(),...lmL.getLayers()]);if(g.getLayers().length)map.fitBounds(g.getBounds(),{padding:[40,40],maxZoom:15});else if(D.center)map.setView(D.center,13);else map.setView([46.6,2.4],5);};
if(D.f35){$('#fovm').value='fix';$('#f35').value=Math.round(D.f35);}

function cone(lat,lon,h,f,len,color,layer){const kx=111320*Math.cos(lat*D2R),ky=110540,P=[[lat,lon]];
 for(let a=h-f/2;a<=h+f/2+1e-9;a+=f/24)P.push([lat+Math.cos(a)*len/ky,lon+Math.sin(a)*len/kx]);
 L.polygon(P,{color,weight:1,fillOpacity:.12}).addTo(layer);}
function draw(){
 ph.querySelectorAll('.vl').forEach(e=>e.remove());
 pts.forEach((p,i)=>vline(p.x,String(i+1),false));
 if(pend!=null)vline(pend,'? → place-le sur la carte',true);
 lmL.clearLayers();
 pts.forEach((p,i)=>L.marker([p.lat,p.lon],{icon:L.divIcon({className:'',iconSize:null,html:`<div style="background:#b388ff;color:#fff;font:700 11px monospace;padding:2px 6px;border-radius:5px;white-space:nowrap;transform:translate(-50%,-50%)">${i+1} ${esc((p.name||'').split(',')[0])}</div>`})}).addTo(lmL));
 $('#lm').innerHTML=pts.map((p,i)=>`<div><span>${i+1}. ${esc((p.name||'repère').split(',')[0])} · x ${(p.x*100).toFixed(1)}% · ${p.lat.toFixed(5)}, ${p.lon.toFixed(5)}</span><a href="#" data-del="${i}">✕</a></div>`).join('');
 document.querySelectorAll('[data-del]').forEach(a=>a.onclick=e=>{e.preventDefault();pts.splice(+a.dataset.del,1);draw();});
 $('#st').textContent=pend!=null?'→ Indique maintenant ce repère sur la carte : recherche son nom ou clique dessus':pts.length<3?`→ Clique un repère dans la photo (${pts.length}/3 minimum)`:`✓ ${pts.length} repères : clique sur Calculer (ou ajoute-en un autre)`;
}
function vline(x,label,pending){const d=document.createElement('div');d.className='vl'+(pending?' pend':'');d.style.left=(x*100)+'%';d.innerHTML=`<i style="${x>.7?'left:auto;right:5px':''}">${esc(label)}</i>`;ph.appendChild(d);}
ph.addEventListener('click',e=>{const r=img.getBoundingClientRect();pend=Math.min(1,Math.max(0,(e.clientX-r.left)/r.width));draw();$('#q').focus();});
map.on('click',e=>{if(pend==null)return;pts.push({x:pend,lat:e.latlng.lat,lon:e.latlng.lng,name:$('#q').value.trim()||('repère '+(pts.length+1))});pend=null;$('#q').value='';draw();});
async function search(){const q=$('#q').value.trim();if(!q)return;$('#sr').innerHTML='<div>Recherche…</div>';
 const b=map.getBounds(),vb=[b.getWest(),b.getNorth(),b.getEast(),b.getSouth()].join(',');
 try{const j=await catGeocode(q,vb);
  $('#sr').innerHTML=j.length?j.map((x,i)=>`<div data-i="${i}">📍 ${esc(x.name)}</div>`).join(''):'<div>Aucun résultat : clique directement sur la carte.</div>';
  document.querySelectorAll('#sr [data-i]').forEach(el=>el.onclick=()=>{const x=j[+el.dataset.i],lat=+x.lat,lon=+x.lon;
   if(pend!=null){pts.push({x:pend,lat,lon,name:q});pend=null;$('#q').value='';draw();}else map.setView([lat,lon],16);$('#sr').innerHTML='';});
 }catch(e){$('#sr').innerHTML='<div>Recherche indisponible : clique sur la carte.</div>';}}
$('#go').onclick=search;$('#q').addEventListener('keydown',e=>{if(e.key==='Enter')search();});
$('#reset').onclick=()=>{pts=[];pend=null;resL.clearLayers();$('#out').innerHTML='';draw();};

// ---- résolution : trouve le point d'où les repères apparaissent à ces positions dans l'image
function solve(P,fovFix){
 const n=P.length,lat0=P.reduce((s,p)=>s+p.lat,0)/n,lon0=P.reduce((s,p)=>s+p.lon,0)/n,kx=111320*Math.cos(lat0*D2R),ky=110540;
 const Lm=P.map(p=>({X:(p.lon-lon0)*kx,Y:(p.lat-lat0)*ky,x:p.x}));
 let spread=0;Lm.forEach(a=>Lm.forEach(b=>spread=Math.max(spread,Math.hypot(a.X-b.X,a.Y-b.Y))));
 const Rm=Math.min(40000,Math.max(2500,spread*14));
 const mk=fs=>fs.map(f=>({f,a:Lm.map(l=>Math.atan((l.x-.5)*2*Math.tan(f*D2R/2)))}));
 const coarseF=mk(fovFix?[fovFix]:Array.from({length:52},(_,i)=>8+i*2));
 function ev(cx,cy,FS){const be=[];for(const l of Lm){if(Math.hypot(l.X-cx,l.Y-cy)<60)return null;be.push(Math.atan2(l.X-cx,l.Y-cy));}
  let best=null;for(const F of FS){let s=0,c=0;for(let i=0;i<n;i++){const d=be[i]-F.a[i];s+=Math.sin(d);c+=Math.cos(d);}const h=Math.atan2(s,c);let e=0;for(let i=0;i<n;i++){const r=wrap(be[i]-F.a[i]-h);e+=r*r;}e=Math.sqrt(e/n);if(!best||e<best.e)best={e,h,f:F.f};}return best;}
 const N=150,step=2*Rm/N,cells=[];let best=null;
 for(let i=0;i<=N;i++)for(let j=0;j<=N;j++){const cx=-Rm+i*step,cy=-Rm+j*step,r=ev(cx,cy,coarseF);if(!r)continue;r.cx=cx;r.cy=cy;cells.push(r);if(!best||r.e<best.e)best=r;}
 if(!best)return null;
 let s=step;for(let k=0;k<3;k++){const FS=fovFix?coarseF:mk(Array.from({length:25},(_,i)=>Math.max(4,best.f-3+i*.25)));const b0=best,M=24,st=2*s/M;
  for(let i=0;i<=M;i++)for(let j=0;j<=M;j++){const cx=b0.cx-s+i*st,cy=b0.cy-s+j*st,r=ev(cx,cy,FS);if(r&&r.e<best.e){r.cx=cx;r.cy=cy;best=r;}}s=st*2;}
 const thr=Math.max(best.e*2.5,.006*best.f*D2R),zone=cells.filter(c=>c.e<=thr);
 const toLL=(x,y)=>[lat0+y/ky,lon0+x/kx];
 const d95=zone.map(c=>Math.hypot(c.cx-best.cx,c.cy-best.cy)).sort((a,b)=>a-b);
 return{best,ll:toLL(best.cx,best.cy),zone:zone.map(c=>({b:[toLL(c.cx-step/2,c.cy-step/2),toLL(c.cx+step/2,c.cy+step/2)],w:1-c.e/thr})),
  prec:d95.length?d95[Math.floor(d95.length*.9)]:0,step,dist:Lm.map(l=>Math.hypot(l.X-best.cx,l.Y-best.cy)),Rm};
}
$('#calc').onclick=async()=>{
 if(pts.length<3){$('#out').innerHTML='<span class="note">Il faut au moins 3 repères.</span>';return;}
 const fix=$('#fovm').value==='fix'&&+$('#f35').value?2*Math.atan(((img.naturalWidth>=img.naturalHeight)?36:24)/(2*+$('#f35').value))*R2D:null;
 $('#out').innerHTML='Calcul…';await new Promise(r=>setTimeout(r,30));
 const R=solve(pts,fix);resL.clearLayers();
 if(!R){$('#out').innerHTML='<span class="note">Pas de solution : vérifie les repères.</span>';return;}
 R.zone.slice(0,5000).forEach(z=>L.rectangle(z.b,{stroke:false,fillColor:'#b388ff',fillOpacity:.08+.35*z.w}).addTo(resL));
 const [la,lo]=R.ll,h=(R.best.h*R2D+360)%360,f=R.best.f,f35=18/Math.tan(f*D2R/2),far=Math.max(...R.dist);
 cone(la,lo,R.best.h,f*D2R,far*1.15,'#b388ff',resL);
 pts.forEach(p=>L.polyline([[la,lo],[p.lat,p.lon]],{color:'#ffc861',weight:1,dashArray:'3 5'}).addTo(resL));
 L.marker([la,lo],{icon:L.divIcon({className:'',iconSize:null,html:'<div style="font-size:26px;transform:translate(-50%,-50%);filter:drop-shadow(0 0 4px #000)">📷</div>'})}).addTo(resL);
 map.fitBounds(L.featureGroup([...resL.getLayers()]).getBounds(),{padding:[30,30]});
 const errD=R.best.e*R2D,prec=Math.max(R.prec,R.step/2),amb=pts.length===3&&!fix;
 let adr='';try{const a=await catReverse(la,lo)||{};adr=[[a.house_number,a.road].filter(Boolean).join(' '),a.neighbourhood,a.quarter,a.suburb,a.city||a.town||a.village].filter(x=>x&&!/community board/i.test(x)).filter((x,i,A)=>A.indexOf(x)===i).join(', ');}catch(e){}
 $('#out').innerHTML=`<div class="big">📷 ${la.toFixed(5)}, ${lo.toFixed(5)}</div>
 ${adr?`<div>Le photographe était vers : <b>${esc(adr)}</b></div>`:''}
 <div>Regard vers : <b>${h.toFixed(0)}° (${CARD(h)})</b> · champ ≈ <b>${f.toFixed(0)}°</b> (≈ ${f35.toFixed(0)} mm éq.)</div>
 <div>Précision : ± ${prec<1000?Math.round(prec)+' m':(prec/1000).toFixed(1)+' km'} · erreur angulaire ${errD.toFixed(2)}° · ${pts.length} repères</div>
 <div>Distances : ${pts.map((p,i)=>`${i+1}. ${esc((p.name||'').split(',')[0])} ${R.dist[i]<1000?Math.round(R.dist[i])+' m':(R.dist[i]/1000).toFixed(2)+' km'}`).join(' · ')}</div>
 ${errD>1.5?'<div class="note">⚠ Erreur élevée : un repère est peut-être mal placé (photo ou carte).</div>':''}
 ${amb?'<div class="note">Avec 3 repères et une focale inconnue, plusieurs positions collent (zone rose). Ajoute un 4e repère ou la focale pour trancher.</div>':''}
 <div style="margin-top:6px">Vérifier : <a target="_blank" href="https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${la},${lo}&heading=${h.toFixed(0)}">Street View dans cette direction</a> · <a target="_blank" href="https://earth.google.com/web/@${la},${lo},60a,0d,35y,${h.toFixed(0)}h,88t,0r">Google Earth 3D</a> · <a target="_blank" href="https://www.google.com/maps?q=${la},${lo}">Google Maps</a></div>`;
};
draw();fitAll();
if(pts.length>=3)setTimeout(()=>$('#calc').click(),300);
</script></body></html>"""


LEAFLET_HEAD = r"""<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" onerror="this.onerror=null;this.href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'">
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>window.L||document.write('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"><\/script>')</script>
<script>window.L||document.write('<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"><\/script>')</script>
<style>
.cat-toast{position:absolute;z-index:1000;left:50%;top:10px;transform:translateX(-50%);background:#141b20ee;color:#ffc861;border:1px solid #ffb84a55;font:12px monospace;padding:6px 12px;border-radius:8px;pointer-events:none;transition:opacity .4s}
.cat-xy{background:#07090bcc;color:#00e5ff;font:11px monospace;padding:3px 8px;border-radius:6px;border:1px solid #2b3158}
.cat-btn{background:#fff;width:34px;height:34px;line-height:34px;text-align:center;font-size:17px;cursor:pointer;color:#111;display:block;text-decoration:none}
.cat-err{padding:30px;font:14px/1.6 monospace;color:#ffc861;background:#0e1028;height:100%;box-sizing:border-box}
.leaflet-container{background:#0b0d22;font-family:system-ui,-apple-system,sans-serif}
.cat-pop{font:12px/1.6 monospace}.cat-pop a{color:#0a7;margin-right:8px}
</style>
<script>
function catMap(id,o){
 o=o||{};const el=document.getElementById(id);
 if(!window.L){el.innerHTML='<div class="cat-err">⚠ La carte n\'a pas pu se charger.<br>Vérifie la connexion Internet, le pare-feu ou le bloqueur de pub (autorise cdnjs.cloudflare.com / unpkg.com), puis recharge la page (F5).</div>';return null;}
 const map=L.map(id,{preferCanvas:true,worldCopyJump:true});
 const T=(u,a,z,s)=>L.tileLayer(u,{maxZoom:z||19,attribution:a,subdomains:s||'abc'});
 const labels=T('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}','',19);
 const E=p=>'https://server.arcgisonline.com/ArcGIS/rest/services/'+p+'/MapServer/tile/{z}/{y}/{x}';
 const B={'Plan':T(E('World_Street_Map'),'© Esri, HERE, Garmin, OpenStreetMap',19),
  'Satellite':L.layerGroup([T(E('World_Imagery'),'© Esri, Maxar, Earthstar',19),labels]),
  'Sombre':L.layerGroup([T(E('Canvas/World_Dark_Gray_Base'),'© Esri',16),T(E('Canvas/World_Dark_Gray_Reference'),'',16)]),
  'Relief':T(E('World_Topo_Map'),'© Esri',19),
  'OpenStreetMap':T('https://tile.openstreetmap.org/{z}/{x}/{y}.png','© OpenStreetMap',19),
  'OSM humanitaire':T('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png','© OpenStreetMap, HOT',19),
  'OpenTopoMap':T('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png','© OpenTopoMap',17)};
 const order=['Plan','OpenStreetMap','OSM humanitaire','Satellite','Relief','OpenTopoMap','Sombre'];let cur=o.base&&B[o.base]?o.base:'Plan';
 const toast=t=>{let d=el.querySelector('.cat-toast');if(!d){d=document.createElement('div');d.className='cat-toast';el.appendChild(d);}d.textContent=t;d.style.opacity=1;clearTimeout(d._t);d._t=setTimeout(()=>d.style.opacity=0,4500);};
 Object.entries(B).forEach(([n,l])=>{const tl=l.getLayers?l.getLayers()[0]:l;tl._ok=0;tl._ko=0;
  tl.on('tileload',()=>tl._ok++);
  tl.on('tileerror',()=>{tl._ko++;if(n===cur&&tl._ok===0&&tl._ko>=4){const nx=order[(order.indexOf(n)+1)%order.length];if(nx===o.base)return;toast('Fond « '+n+' » bloqué → bascule sur « '+nx+' »');map.removeLayer(l);cur=nx;B[nx].addTo(map);}});});
 B[cur].addTo(map);map.on('baselayerchange',e=>{cur=Object.keys(B).find(k=>B[k]===e.layer)||cur;});
 L.control.layers(B,null,{position:'topright'}).addTo(map);
 L.control.scale({imperial:false}).addTo(map);
 const XY=L.Control.extend({onAdd(){const d=L.DomUtil.create('div','cat-xy');d.textContent='—';map.on('mousemove',e=>d.textContent=e.latlng.lat.toFixed(5)+', '+e.latlng.lng.toFixed(5));return d;}});
 new XY({position:'bottomleft'}).addTo(map);
 const FS=L.Control.extend({onAdd(){const a=L.DomUtil.create('a','leaflet-bar cat-btn');a.title='Plein écran';a.textContent='⛶';
  L.DomEvent.on(a,'click',ev=>{L.DomEvent.stop(ev);document.fullscreenElement?document.exitFullscreen():el.requestFullscreen&&el.requestFullscreen();});return a;}});
 new FS({position:'topleft'}).addTo(map);document.addEventListener('fullscreenchange',()=>setTimeout(()=>map.invalidateSize(),200));
 if(o.clickCoords!==false)map.on('click',e=>{const la=e.latlng.lat.toFixed(6),lo=e.latlng.lng.toFixed(6);
  L.popup().setLatLng(e.latlng).setContent(`<div class="cat-pop"><b>${la}, ${lo}</b><br><a target="_blank" href="https://www.google.com/maps?q=${la},${lo}">Google Maps</a><a target="_blank" href="https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${la},${lo}">Street View</a><a target="_blank" href="https://earth.google.com/web/@${la},${lo},300a,800d,35y,0h,45t,0r">Earth 3D</a><a target="_blank" href="https://www.openstreetmap.org/?mlat=${la}&mlon=${lo}#map=18/${la}/${lo}">OSM</a></div>`).openOn(map);});
 map.setView(o.center||[20,0],o.zoom||2);return map;}
async function catGeocode(q,vb){
 try{const j=await (await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&limit=6&accept-language=fr${vb?'&viewbox='+vb:''}&q=${encodeURIComponent(q)}`)).json();
  if(Array.isArray(j))return j.map(x=>({name:x.display_name,lat:+x.lat,lon:+x.lon}));}catch(e){}
 const j=await (await fetch(`https://photon.komoot.io/api/?limit=6&q=${encodeURIComponent(q)}`)).json();
 return (j.features||[]).map(f=>{const p=f.properties||{};return {name:[p.name,p.street,p.city,p.state,p.country].filter(Boolean).join(', '),lat:f.geometry.coordinates[1],lon:f.geometry.coordinates[0]};});}
async function catReverse(la,lo){
 try{const j=await (await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${la}&lon=${lo}&zoom=18&accept-language=fr`)).json();if(j&&j.address)return j.address;}catch(e){}
 const j=await (await fetch(`https://photon.komoot.io/reverse?lat=${la}&lon=${lo}`)).json();const p=((j.features||[])[0]||{}).properties||{};
 return {house_number:p.housenumber,road:p.street||p.name,suburb:p.district,city:p.city,country:p.country};}
</script>"""


QUICK_TPL = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
__LEAFLET__
<style>:root{--bg:#07081a;--p:#0e1028;--l:#2b3158;--t:#e4e9ff;--m:#7480a8;--g:#00e5ff;--k:#b388ff}
body{margin:0;font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--t)}
header{padding:12px 18px;border-bottom:1px solid var(--l);display:flex;gap:14px;align-items:center;flex-wrap:wrap;background:linear-gradient(110deg,#0b1630,#07081a 55%,#1a0b30)}
header b{font:800 15px monospace;color:var(--g);letter-spacing:.5px}header .n{font:12px monospace;color:var(--m);background:#14173a;border:1px solid var(--l);padding:3px 9px;border-radius:20px}
header a{margin-left:auto;color:#8a8cff;font:13px monospace;text-decoration:none}header a:hover{color:var(--g)}
#map{height:calc(100vh - 52px)}body.ex-on #map{height:70vh}.ex{padding:14px 18px;font-size:14px;line-height:1.6;max-width:1100px}.ex a{color:var(--g)}
.ex table{border-collapse:collapse;font:12px monospace;width:100%;background:var(--p);border:1px solid var(--l);border-radius:10px;overflow:hidden}
.ex td,.ex th{border-bottom:1px solid var(--l);padding:6px 8px;text-align:left}.ex th{color:var(--g)}.leaflet-popup-content{font:13px/1.5 system-ui}.leaflet-popup-content a{color:#0a7}</style></head>
<body><header><b>CAT.exe // __TITLE__</b><span class="n" id="cnt"></span><a href="__DISCORD__" target="_blank">◆ discord Cat.exe</a></header><div id="map"></div><div class="ex">__EXTRA__</div>
<script>const D=__DATA__;const map=catMap('map',{base:D.base});const g=L.featureGroup().addTo(map);
D.c.forEach(c=>L.circle([c.lat,c.lon],{radius:c.r,color:c.c||'#b388ff',weight:1,fillOpacity:.15}).addTo(g));
D.l.forEach(l=>L.polyline(l,{color:'#ffc861',weight:2}).addTo(g));
D.m.forEach(m=>(m.icon?L.marker([m.lat,m.lon],{icon:L.divIcon({className:'',iconSize:null,html:`<div style="transform:translate(-50%,-50%) rotate(${m.rot||0}deg);font-size:${m.s||20}px;color:${m.c||'#b388ff'};text-shadow:0 0 3px #000">${m.icon}</div>`})})
 :L.circleMarker([m.lat,m.lon],{radius:m.s||7,color:m.c||'#b388ff',fillOpacity:.85,weight:1})).bindPopup(m.label||'').addTo(g));
if(g.getLayers().length)map.fitBounds(g.getBounds(),{padding:[30,30],maxZoom:16});
document.getElementById('cnt').textContent=D.m.length+' point(s)';if(document.querySelector('.ex').textContent.trim()){document.body.classList.add('ex-on');map.invalidateSize();}</script></body></html>"""


GRAPH_TPL = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CAT.exe · Dossier d'enquête</title>
<style>
:root{--bg:#07081a;--p1:#0e1028;--p2:#14173a;--p3:#1a1f40;--bd:#2b3158;--tx:#e4e9ff;--mu:#7480a8;--c:#00e5ff;--v:#b388ff;--r:#ff5c7a;--ok:#4caf7a;--ck:#e0a83a;--no:#6b7079}
*{box-sizing:border-box}html,body{margin:0;height:100%;background:var(--bg);color:var(--tx);font:13.5px/1.5 "Segoe UI",system-ui,-apple-system,Roboto,sans-serif;overflow:hidden}
.mono{font-family:ui-monospace,"Cascadia Code",Consolas,monospace}
svg.i{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;vertical-align:-3px;flex:none}
/* ---------- barre du haut */
header{position:absolute;top:0;left:0;right:0;height:58px;display:flex;align-items:center;gap:10px;padding:0 14px;background:linear-gradient(180deg,var(--p2),var(--p1));border-bottom:1px solid var(--bd);z-index:10}
.case{display:flex;align-items:center;gap:10px;min-width:0;padding-right:12px;border-right:1px solid var(--bd)}
.case .ic{width:34px;height:34px;border-radius:8px;display:grid;place-items:center;background:var(--p3);border:1px solid var(--bd);color:var(--c)}
.case .ic svg{width:20px;height:20px}
.case b{display:block;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:190px}.case small{color:var(--mu);font-size:11px;letter-spacing:.04em}
#addf{display:flex;gap:6px;flex:1;max-width:780px}
.inp{display:flex;align-items:center;gap:8px;flex:1;background:var(--bg);border:1px solid var(--bd);border-radius:7px;padding:0 10px}
.inp:focus-within{border-color:var(--c)}.inp svg{color:var(--mu)}
input,select,button,textarea{font:inherit;color:var(--tx)}
.inp input{flex:1;border:0;background:transparent;padding:8px 0;outline:0;min-width:80px}
select{background:var(--bg);border:1px solid var(--bd);border-radius:7px;padding:7px 8px}
button{display:inline-flex;align-items:center;gap:6px;justify-content:center;padding:7px 12px;cursor:pointer;background:var(--p3);border:1px solid var(--bd);border-radius:7px;white-space:nowrap}
button:hover{border-color:var(--mu)}button.pri{background:var(--c);color:var(--bg);border-color:var(--c);font-weight:600}button.pri:hover{filter:brightness(1.08)}
button.ghost{background:transparent}button.danger:hover{border-color:var(--r);color:var(--r)}button.sm{padding:4px 9px;font-size:12px}
.tools{display:flex;gap:4px;margin-left:auto}.tools button{padding:7px 9px}
.dd{position:relative}.menu{position:absolute;right:0;top:42px;width:260px;background:var(--p1);border:1px solid var(--bd);border-radius:9px;padding:6px;display:none;box-shadow:0 12px 32px rgba(0,0,0,.5);z-index:30}
.menu .h{color:var(--mu);font-size:10.5px;text-transform:uppercase;letter-spacing:.09em;padding:8px 9px 4px}
.menu div.i{display:flex;gap:9px;align-items:center;padding:7px 9px;border-radius:6px;cursor:pointer}.menu div.i:hover{background:var(--p3)}
/* ---------- zone graphe */
#stage{position:absolute;top:58px;left:0;right:360px;bottom:36px;background:radial-gradient(ellipse at center,var(--p1) 0%,var(--bg) 75%)}
#stage:after{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(600px 420px at 18% 12%,rgba(0,229,255,.07),transparent 70%),radial-gradient(700px 500px at 88% 92%,rgba(179,136,255,.08),transparent 70%)}
#stage:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(116,128,168,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(116,128,168,.06) 1px,transparent 1px);background-size:40px 40px;pointer-events:none}
#net{position:absolute;inset:0}
#filters{position:absolute;top:12px;left:12px;display:flex;flex-direction:column;gap:4px;z-index:4;max-height:calc(100% - 24px);overflow:auto}
.chip{display:flex;gap:8px;align-items:center;padding:5px 10px 5px 6px;backdrop-filter:blur(6px);transition:transform .12s,border-color .12s;background:rgba(14,16,40,.82);border:1px solid var(--bd);border-radius:7px;cursor:pointer;user-select:none;font-size:12px}
.chip .dot{width:22px;height:22px;border-radius:50%;display:grid;place-items:center;border:1.5px solid}.chip .dot.fb{color:#07081a;font:700 11px system-ui}#fstat{white-space:nowrap}#fsel{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:22vw}.leg{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--mu);padding:10px 4px 2px}.chip.mode{margin-top:6px}
.fbar{display:flex;height:12px;border-radius:6px;overflow:hidden;background:var(--bg);border:1px solid var(--bd)}.fbar i{display:block;height:100%}.fleg{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:8px;font-size:12px;color:var(--mu)}.fleg span{display:flex;align-items:center;gap:6px}.fleg i{width:9px;height:9px;border-radius:50%;display:inline-block}.fleg b{color:var(--tx);font-weight:600}.chip .dot svg{width:12px;height:12px}
.chip b{margin-left:auto;padding-left:8px;color:var(--mu);font-weight:500}.chip:hover{transform:translateX(3px);border-color:var(--mu)}.chip.off{opacity:.35}
#zoom{position:absolute;right:12px;bottom:12px;display:flex;flex-direction:column;gap:4px;z-index:4}#zoom button{width:34px;height:34px;padding:0}
#empty{position:absolute;inset:0;display:none;align-items:center;justify-content:center;text-align:center;color:var(--mu);pointer-events:none;padding:30px}
#empty .box{max-width:470px}#empty .big{width:64px;height:64px;margin:0 auto 14px;border-radius:16px;display:grid;place-items:center;background:var(--p2);border:1px solid var(--bd);color:var(--c)}#empty .big svg{width:32px;height:32px}
#empty b{color:var(--tx);font-size:18px;display:block;margin-bottom:6px}
.ex{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-top:12px}.ex span{border:1px solid var(--bd);border-radius:6px;padding:3px 8px;font-size:12px}
/* ---------- panneau droit */
aside{position:absolute;top:58px;right:0;width:360px;bottom:0;background:var(--p1);border-left:1px solid var(--bd);display:flex;flex-direction:column}
.tabs{display:flex;border-bottom:1px solid var(--bd);padding:0 8px;flex:none}
.tabs div{padding:11px 10px;cursor:pointer;color:var(--mu);border-bottom:2px solid transparent;font-size:12.5px;display:flex;gap:6px;align-items:center}.tabs div.on{color:var(--tx);border-color:var(--c)}
.tabs div em{font-style:normal;background:var(--p3);border-radius:8px;padding:0 6px;font-size:11px}
#body{flex:1;overflow:auto;padding:16px 16px 24px}
.ent{display:flex;gap:12px;align-items:flex-start}.ent .av{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;border:2px solid;flex:none;background:var(--p2)}.ent .av svg{width:22px;height:22px}
.ent h2{margin:0;font-size:16px;word-break:break-all;line-height:1.3}.ent .meta{color:var(--mu);font-size:12px;margin-top:3px}
h3{margin:20px 0 8px;font-size:10.5px;letter-spacing:.09em;color:var(--mu);text-transform:uppercase;font-weight:600;display:flex;align-items:center;gap:8px}h3:after{content:"";flex:1;height:1px;background:var(--bd)}
.seg{display:grid;grid-template-columns:repeat(3,1fr);gap:4px}.seg button{font-size:12px;padding:6px 4px}
.seg button.on[data-s=ok]{border-color:var(--ok);color:var(--ok);background:rgba(76,175,122,.1)}.seg button.on[data-s=check]{border-color:var(--ck);color:var(--ck);background:rgba(224,168,58,.1)}.seg button.on[data-s=faux]{border-color:var(--no);color:var(--tx);background:rgba(107,112,121,.15)}
.row2{display:flex;gap:6px;margin-top:6px}.row2 button{flex:1}
button.star.on{border-color:var(--ck);color:var(--ck)}
table{width:100%;border-collapse:collapse;font-size:12.5px}td{border-top:1px solid var(--bd);padding:6px 4px;vertical-align:top;word-break:break-word}td:first-child{color:var(--mu);width:36%}
a{color:var(--c);text-decoration:none}a:hover{text-decoration:underline}
.tf{display:flex;align-items:center;gap:10px;width:100%;text-align:left;margin:5px 0;background:var(--bg);padding:9px 11px;justify-content:flex-start}
.tf span{flex:1}.tf small{color:var(--mu);font-size:11px}.tf.done small{color:var(--ok)}
textarea{width:100%;min-height:84px;padding:9px;resize:vertical;background:var(--bg);border:1px solid var(--bd);border-radius:7px}
.kpi{display:grid;grid-template-columns:1fr 1fr;gap:8px}.kpi div{background:var(--bg);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;color:var(--mu);font-size:11.5px}.kpi b{display:block;font-size:22px;color:var(--tx);font-weight:600}
.bar{display:flex;align-items:center;gap:8px;margin:5px 0;font-size:12px}.bar .lab{width:96px;color:var(--mu);display:flex;gap:6px;align-items:center}.bar .tr{flex:1;height:6px;background:var(--p3);border-radius:3px;overflow:hidden}.bar .tr i{display:block;height:100%}.bar b{width:28px;text-align:right;font-weight:500}
.lk{display:flex;align-items:center;gap:9px;padding:7px 4px;border-top:1px solid var(--bd);cursor:pointer}.lk:hover{background:var(--p2)}.lk .d{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;border:1.5px solid;flex:none}.lk .d svg{width:12px;height:12px}
.lk .n{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.lk .st{flex:none}.lk small{color:var(--mu);font-size:11px}
.st{font-size:10.5px;padding:1px 6px;border-radius:5px;border:1px solid}.st.ok{color:var(--ok);border-color:var(--ok)}.st.check{color:var(--ck);border-color:var(--ck)}.st.faux{color:var(--no);border-color:var(--no)}
.log{border-left:2px solid var(--bd);margin-left:6px;padding-left:12px}.log div{position:relative;padding:5px 0;font-size:12.5px}.log div:before{content:"";position:absolute;left:-17px;top:11px;width:8px;height:8px;border-radius:50%;background:var(--bd)}
.log div.k:before{background:var(--c)}.log time{color:var(--mu);font-size:11px;display:block}
.hint{color:var(--mu);font-size:12px}ol.steps{padding-left:18px;margin:0;color:var(--mu)}ol.steps li{margin:5px 0}ol.steps b{color:var(--tx)}
kbd{border:1px solid var(--bd);border-bottom-width:2px;border-radius:4px;padding:0 5px;font-size:11px;background:var(--p2)}
/* ---------- bas, toast, menu contextuel */
footer{position:absolute;left:0;right:360px;bottom:0;height:36px;display:flex;align-items:center;gap:14px;padding:0 14px;border-top:1px solid var(--bd);background:var(--p1);font-size:12px;color:var(--mu)}
footer .live{display:flex;align-items:center;gap:6px}footer .live i{width:7px;height:7px;border-radius:50%;background:var(--ok)}footer .live.off i{background:var(--r)}
footer .sp{margin-left:auto}
#toast{position:absolute;left:calc(50% - 180px);top:72px;transform:translateX(-50%);background:var(--p1);border:1px solid var(--bd);border-left:3px solid var(--c);padding:9px 16px;border-radius:7px;z-index:40;display:none;box-shadow:0 8px 24px rgba(0,0,0,.45);max-width:560px}
#ctx{position:absolute;display:none;z-index:50;width:250px;background:var(--p1);border:1px solid var(--bd);border-radius:9px;padding:5px;box-shadow:0 12px 32px rgba(0,0,0,.55)}
#ctx .h{padding:7px 9px;color:var(--mu);font-size:11px;border-bottom:1px solid var(--bd);margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#ctx div.i{display:flex;gap:9px;align-items:center;padding:6px 9px;border-radius:6px;cursor:pointer}#ctx div.i:hover{background:var(--p3)}#ctx hr{border:0;border-top:1px solid var(--bd);margin:4px 0}
#err{position:absolute;inset:0;display:none;align-items:center;justify-content:center;color:var(--mu);text-align:center;padding:40px;z-index:60;background:var(--bg)}
.spin{display:inline-block;width:12px;height:12px;border:2px solid var(--mu);border-top-color:var(--c);border-radius:50%;animation:sp .8s linear infinite;vertical-align:-2px;margin-right:6px}@keyframes sp{to{transform:rotate(360deg)}}
@media(max-width:860px){#stage,footer{right:0}aside{display:none}aside.show{display:flex;width:100%;top:auto;height:58%;border-left:0;border-top:1px solid var(--bd)}.case b{max-width:110px}.tools .hide-s{display:none}}
</style></head><body>
<header>
 <div class="case"><div class="ic" id="caseic"></div><div><b id="casename"></b><small id="caseno"></small></div></div>
 <form id="addf" autocomplete="off"><div class="inp"><span id="addic"></span><input id="addv" placeholder="Nouvelle cible : pseudo, email, IP, domaine, lien, Prénom Nom…"></div>
  <select id="addt" title="Type (détecté tout seul)"></select><button type="submit" title="Ajouter au dossier">Ajouter</button><button type="button" id="addall" class="pri" title="Ajouter puis lancer toutes les recherches"></button></form>
 <div class="tools">
  <div class="inp hide-s" style="width:170px;flex:none"><span id="qic"></span><input id="q" placeholder="Filtrer  /"></div>
  <div class="dd"><button id="more" class="ghost" title="Options"></button><div class="menu" id="menu">
   <div class="h">Disposition</div><div class="i" data-m="force">Libre (physique)</div><div class="i" data-m="hier">Arbre hiérarchique</div><div class="i" data-m="circle">Cercle</div><div class="i" data-m="type">Colonnes par type</div>
   <div class="h">Analyse</div><div class="i" data-m="path">Chemin entre 2 éléments (Ctrl + clic)</div><div class="i" data-m="clu">Regrouper / dégrouper par type</div><div class="i" data-m="keys">Ne montrer que les pistes clés</div><div class="i" data-m="nofaux">Masquer les fausses pistes</div><div class="i" data-m="phys">Figer / animer</div>
   <div class="h">Dossier</div><div class="i" data-m="report">Rapport d'enquête (imprimable / PDF)</div><div class="i" data-m="png">Exporter l'image (PNG)</div><div class="i" data-m="json">Exporter les données (JSON)</div><div class="i" data-m="csv">Exporter pour Excel (CSV)</div><div class="i" data-m="imp">Importer un JSON</div>
  </div></div></div>
 <input type="file" id="imp" accept=".json" style="display:none">
</header>
<div id="stage"><div id="net"></div><div id="filters"></div>
 <div id="zoom"><button id="zin" title="Zoom +">+</button><button id="zout" title="Zoom −">−</button><button id="zfit" title="Tout voir (F)"></button></div>
 <div id="empty"><div class="box"><div class="big" id="emptyic"></div><b>Dossier vide</b>Tape une première cible dans la barre du haut, puis <b style="display:inline;font-size:13.5px">Ajouter + chercher</b>.<br>Les modules lancés dans le terminal alimentent aussi ce dossier en direct.
  <div class="ex"><span>pseudo</span><span>prenom.nom@gmail.com</span><span>8.8.8.8</span><span>exemple.fr</span><span>Jean Dupont</span></div></div></div>
</div>
<aside id="side"><div class="tabs" id="tabs"></div><div id="body"></div></aside>
<footer><span class="live" id="live"><i></i>synchro avec Cat.exe</span><span id="fstat"></span><span id="fsel"></span><span class="sp"><kbd>clic droit</kbd> actions · <kbd>/</kbd> filtrer · <kbd>F</kbd> tout voir · <kbd>Suppr</kbd> supprimer</span></footer>
<div id="toast"></div><div id="ctx"></div><div id="err"></div>
<script>
const NAME=new URLSearchParams(location.search).get('e')||'mon_enquete',TYPES=__TYPES__,TRANS=__TRANS__,ROOT='enquete:'+NAME;
const SRC=['https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.9/standalone/umd/vis-network.min.js','https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js','https://cdn.jsdelivr.net/npm/vis-network@9.1.9/standalone/umd/vis-network.min.js'];
function load(i){if(i>=SRC.length){err('Impossible de charger le moteur du graphe (pas de connexion internet ?).');return}const s=document.createElement('script');s.src=SRC[i];s.onload=start;s.onerror=()=>load(i+1);document.head.appendChild(s)}
const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function err(t){$('err').style.display='flex';$('err').textContent=t}
/* ---------- icônes (traits, 24×24) */
const P={pseudo:'<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
compte:'<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.2"/><path d="M5.8 16.5c.6-1.6 1.8-2.4 3.2-2.4s2.6.8 3.2 2.4M14 10h4M14 13.5h4"/>',
personne:'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.8 2.9-6 6.5-6s6.5 2.2 6.5 6"/><circle cx="17" cy="9" r="2.6"/><path d="M16 14.2c3 .2 5.5 2 5.5 5.3"/>',
email:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>',telephone:'<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M10.5 18.5h3"/>',
ip:'<rect x="3.5" y="4" width="17" height="7" rx="1.5"/><rect x="3.5" y="13" width="17" height="7" rx="1.5"/><path d="M7 7.5h.01M7 16.5h.01M11 7.5h6M11 16.5h6"/>',
domaine:'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/>',
url:'<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1.2 1.2"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1.2-1.2"/>',
lieu:'<path d="M12 21.5s-7-7.2-7-12.2a7 7 0 0 1 14 0c0 5-7 12.2-7 12.2z"/><circle cx="12" cy="9.3" r="2.6"/>',
image:'<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="9.5" r="1.8"/><path d="M3.5 18l5.5-5.5 4 4 3-3 4.5 4.5"/>',
crypto:'<circle cx="12" cy="12" r="9"/><path d="M9.5 7.5h4a2.2 2.2 0 0 1 0 4.4h-4zM9.5 11.9h4.6a2.3 2.3 0 0 1 0 4.6H9.5zM9.5 7.5v9M11 6v1.5M11 16.5V18"/>',
discord:'<path d="M4 5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1h-9l-5 4v-4H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/><path d="M8 11h.01M12 11h.01M16 11h.01"/>',
fuite:'<path d="M12 2.8s-6.5 7.4-6.5 12a6.5 6.5 0 0 0 13 0c0-4.6-6.5-12-6.5-12z"/><path d="M9 15.5a3 3 0 0 0 3 3"/>',
organisation:'<rect x="4" y="3" width="11" height="18" rx="1"/><path d="M15 9h4a1 1 0 0 1 1 1v11M7.5 7h4M7.5 11h4M7.5 15h4M9.5 21v-2.5"/>',
note:'<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 12h7M9 16h7"/>',
enquete:'<path d="M3 7a1 1 0 0 1 1-1h5l2 2h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M3 11h18"/>',autre:'<path d="M12 3l9 9-9 9-9-9z"/>',
search:'<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',plus:'<path d="M12 5v14M5 12h14"/>',bolt:'<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',dots:'<path d="M5 12h.01M12 12h.01M19 12h.01"/>',
fit:'<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',star:'<path d="M12 3l2.8 5.8 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.3l1-6.2L3 9.7l6.2-.9z"/>',
open:'<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',link2:'<path d="M9 17H7a5 5 0 0 1 0-10h2M15 7h2a5 5 0 0 1 0 10h-2M8 12h8"/>',
trash:'<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>',check:'<path d="M5 12.5l4.5 4.5L19 7.5"/>',google:'<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4M8.5 11h5"/>',
doc:'<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 13h6M9 17h4"/>'};
const ico=(k,c)=>`<svg class="i" viewBox="0 0 24 24"${c?` style="color:${c}"`:''}>${P[k]||P.autre}</svg>`;
const ST={ok:['Confirmé','#4caf7a'],check:['À vérifier','#e0a83a'],faux:['Fausse piste','#6b7079']};
const FB={A:['Vérifié à la source','#4caf7a','A'],B:['Existe · lien à confirmer','#5b9dff','B'],C:['Estimation · à vérifier','#e0a83a','C'],'?':['Sans niveau','#6b7079','–']};
let hidFb=new Set(),colorBy=(()=>{try{return localStorage.getItem('cat_colorby')||'type'}catch(e){return 'type'}})();
const fbOf=n=>{const d=n.data||{};return d._statut=='ok'&&d._statut_user?'A':(d._fiab||'?')};
let G={nodes:{},edges:[],rev:-1},net,N,E,hidden=new Set(),sel=null,linkFrom=null,saving=false,busy=0,clustered=false,pathSet=null,manualType=false,REAL=0,childOf=null,tab='dossier',onlyKeys=false,noFaux=false,PH='';
const T=t=>TYPES[t]||TYPES.autre,col=t=>T(t)[0],tn=t=>T(t)[1];
function toast(h,ms){const t=$('toast');t.innerHTML=h;t.style.display='block';clearTimeout(t._t);if(ms)t._t=setTimeout(()=>t.style.display='none',ms)}
function now(){return new Date().toLocaleString('fr-FR',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'})}
function logp(txt,id){G.log=G.log||[];G.log.push({t:now(),txt,id:id||null});if(G.log.length>400)G.log=G.log.slice(-400)}
function deg(id){let d=0;for(const e of G.edges)if(e.from==id||e.to==id)d++;return d}
function caseNo(){let h=0;for(const c of NAME)h=(h*31+c.charCodeAt(0))>>>0;return 'DOSSIER CAT-'+new Date().getFullYear()+'-'+String(h%10000).padStart(4,'0')}
function svgNode(t,stc,key){const c=col(t);return 'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"><circle cx="48" cy="48" r="48" fill="#0e1028"/><circle cx="48" cy="48" r="48" fill="${c}" fill-opacity=".16"/><g transform="translate(24 24) scale(2)" fill="none" stroke="${c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${P[t]||P.autre}</g></svg>`)}
/* ---------- ajout */
function ttype(v){v=v.trim();if(/^[\w.+-]+@[\w-]+\.[\w.-]+$/.test(v))return'email';if(/^\d{1,3}(\.\d{1,3}){3}$/.test(v)||/^[0-9a-f:]{6,}$/i.test(v)&&v.includes(':'))return'ip';
 if(/^https?:\/\//i.test(v))return'url';if(/^-?\d{1,3}\.\d+\s*,\s*-?\d{1,3}\.\d+$/.test(v))return'lieu';if(/^\+?[\d\s.()-]{9,}$/.test(v))return'telephone';
 if(/^(0x[0-9a-f]{40}|(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62})$/i.test(v))return'crypto';if(/^([\w-]+\.)+[a-z]{2,}$/i.test(v))return'domaine';if(/\s/.test(v))return'personne';return'pseudo'}
function setAddIcon(){$('addic').innerHTML=ico($('addt').value,col($('addt').value))}
function addNode(v,t,parent){const id=t+':'+v.toLowerCase();if(!G.nodes[ROOT])G.nodes[ROOT]={type:'enquete',label:NAME.replace(/_/g,' '),data:{}};
 if(!G.nodes[id]){G.nodes[id]={type:t,label:v,data:{},t:now()};logp('Ajout : '+tn(t)+' « '+v+' »',id)}
 const p=parent&&parent!=id?parent:ROOT;if(!G.edges.some(e=>e.from==p&&e.to==id))G.edges.push({from:p,to:id,label:''});return id}
async function submitAdd(all){const v=$('addv').value.trim();if(!v)return $('addv').focus();const id=addNode(v,$('addt').value,childOf);
 childOf=null;$('addv').placeholder=PH;$('addv').value='';manualType=false;render();await save();focusN(id);if(all)runAll(id)}
/* ---------- rendu */
function vnode(id,n){const d=deg(id),root=n.type=='enquete',lb=n.short||n.label,inP=pathSet&&pathSet.has(id),dt=n.data||{},st=dt._statut,key=dt._cle;
 const fb=fbOf(n),bc=inP?'#e4e9ff':st?ST[st][1]:key?'#e0a83a':colorBy=='fiab'&&!root?FB[fb][1]:col(n.type),sz=root?24:Math.min(16+d*1.4,34)+(key?6:0);
 const hide=hidden.has(n.type)||(root&&!REAL)||(onlyKeys&&!key&&!root)||(noFaux&&st=='faux')||(!root&&hidFb.has(fb));
 return {id,label:(lb.length>26?lb.slice(0,24)+'…':lb)+(st&&st!='faux'?'\n'+ST[st][0]:''),shape:'circularImage',image:svgNode(n.type),size:sz,group:n.type,
  color:{border:bc,background:'#0e1028',highlight:{border:'#00e5ff',background:'#0e1028'},hover:{border:'#e4e9ff',background:'#0e1028'}},
  borderWidth:st=='ok'||key||inP?3:1.5,borderWidthSelected:4,shapeProperties:{borderDashes:st=='faux'?[5,4]:false,interpolation:false},
  font:{color:st=='faux'?'#7480a8':'#e4e9ff',size:root?15:13,face:'Segoe UI,system-ui,sans-serif',strokeWidth:0,background:'rgba(7,8,26,.78)',vadjust:4,multi:false},shadow:{enabled:st!='faux',color:(key?'#e0a83a':st=='ok'?'#4caf7a':colorBy=='fiab'&&!root?FB[fb][1]:col(n.type))+(key||st=='ok'?'cc':'77'),size:key?36:st=='ok'?26:16,x:0,y:0},
  hidden:hide,opacity:pathSet&&!inP?.15:(st=='faux'?.5:1)}}
function render(){const ids=new Set(Object.keys(G.nodes));REAL=[...ids].filter(i=>!i.startsWith('enquete:')).length;
 N.update(Object.entries(G.nodes).map(([id,n])=>vnode(id,n)));N.getIds().forEach(i=>{if(!ids.has(i))N.remove(i)});
 const ek=new Set();E.update(G.edges.filter(e=>G.nodes[e.from]&&G.nodes[e.to]).map(e=>{const id=e.from+'→'+e.to;ek.add(id);const inP=pathSet&&pathSet.has(e.from)&&pathSet.has(e.to);
  return {id,from:e.from,to:e.to,label:e.label||'',font:{color:'#7480a8',size:10,strokeWidth:3,strokeColor:'#07081a',align:'middle'},color:{color:inP?'#00e5ff':colorBy=='fiab'?FB[e.conf||'?'][1]:col((G.nodes[e.to]||{}).type),highlight:'#00e5ff',hover:'#e4e9ff',opacity:pathSet&&!inP?.12:(inP?1:colorBy=='fiab'?.7:.42)},
   width:inP?3.5:1.4,dashes:e.conf=='C'?[5,5]:false,hoverWidth:1.6,selectionWidth:2.2,arrows:{to:{enabled:true,scaleFactor:.4}},smooth:{type:'continuous',roundness:.35}}}));
 E.getIds().forEach(i=>{if(!ek.has(i))E.remove(i)});
 $('empty').style.display=REAL?'none':'flex';filters();head();panel()}
function head(){$('casename').textContent=NAME.replace(/_/g,' ');$('caseno').textContent=caseNo();
 const c={};Object.values(G.nodes).forEach(n=>{const s=(n.data||{})._statut;if(s)c[s]=(c[s]||0)+1});
 const f={A:0,B:0,C:0,'?':0};Object.values(G.nodes).forEach(n=>{if(n.type!='enquete')f[fbOf(n)]++});
 $('fstat').innerHTML=`${REAL} entités · ${G.edges.length} liens · ${c.ok||0} confirmées · ${c.check||0} à vérifier · `+['A','B','C'].map(k=>`<b style="color:${FB[k][1]}">${k} ${f[k]}</b>`).join(' ')}
function filters(){const F=$('filters'),cnt={};Object.values(G.nodes).forEach(n=>{if(n.type!='enquete')cnt[n.type]=(cnt[n.type]||0)+1});
 F.innerHTML=Object.keys(cnt).sort((a,b)=>cnt[b]-cnt[a]).map(t=>`<div class="chip ${hidden.has(t)?'off':''}" data-t="${t}" title="Clic : masquer / afficher"><span class="dot" style="border-color:${col(t)};color:${col(t)}">${ico(t)}</span>${esc(tn(t))}<b>${cnt[t]}</b></div>`).join('');
 const fc={A:0,B:0,C:0,'?':0};Object.values(G.nodes).forEach(n=>{if(n.type!='enquete')fc[fbOf(n)]++});
 if(REAL)F.innerHTML+=`<div class="leg">Fiabilité</div>`+Object.keys(FB).filter(k=>fc[k]).map(k=>`<div class="chip fbc ${hidFb.has(k)?'off':''}" data-f="${k}" title="Clic : masquer / afficher ce niveau"><span class="dot fb" style="background:${FB[k][1]};border-color:${FB[k][1]}">${FB[k][2]}</span>${FB[k][0]}<b>${fc[k]}</b></div>`).join('')
  +`<div class="chip mode" id="cmode" title="Changer ce que montrent les couleurs"><span class="dot" style="border-color:var(--c);color:var(--c)">${ico('fit')}</span>Couleurs : ${colorBy=='fiab'?'fiabilité':'type'}</div>`;
 F.querySelectorAll('.chip[data-t]').forEach(c=>c.onclick=()=>{const t=c.dataset.t;hidden.has(t)?hidden.delete(t):hidden.add(t);render()});
 F.querySelectorAll('.chip[data-f]').forEach(c=>c.onclick=()=>{const k=c.dataset.f;hidFb.has(k)?hidFb.delete(k):hidFb.add(k);render()});
 const cm=$('cmode');if(cm)cm.onclick=()=>{colorBy=colorBy=='fiab'?'type':'fiab';try{localStorage.setItem('cat_colorby',colorBy)}catch(e){}render();toast(colorBy=='fiab'?'Couleurs : niveau de fiabilité':'Couleurs : type d\'élément',2500)}}
/* ---------- panneau */
function tabsFor(){return sel&&G.nodes[sel]?[['fiche','Fiche'],['rech','Recherches',(TRANS[G.nodes[sel].type]||[]).length],['liens','Liens',G.edges.filter(e=>e.from==sel||e.to==sel).length]]:[['dossier','Dossier'],['journal','Journal',(G.log||[]).length],['pistes','Pistes']]}
function panel(){const TB=tabsFor();if(!TB.some(t=>t[0]==tab))tab=TB[0][0];
 $('tabs').innerHTML=TB.map(([k,l,n])=>`<div data-k="${k}" class="${k==tab?'on':''}">${l}${n!=null?` <em>${n}</em>`:''}</div>`).join('');
 $('tabs').querySelectorAll('div').forEach(d=>d.onclick=()=>{tab=d.dataset.k;panel()});
 const B=$('body');$('side').classList.toggle('show',!!sel);
 if(!sel||!G.nodes[sel]){sel=null;B.innerHTML=tab=='journal'?journal():tab=='pistes'?pistes():dossier()}
 else{const n=G.nodes[sel];B.innerHTML=entHead(sel,n)+(tab=='rech'?rech(sel,n):tab=='liens'?liens(sel):fiche(sel,n))}
 bind(B);$('fsel').textContent=sel?'· sélection : '+(G.nodes[sel].short||G.nodes[sel].label).slice(0,40):''}
function entHead(id,n){const st=(n.data||{})._statut,nb=deg(id);return `<div class="ent"><div class="av" style="border-color:${col(n.type)};color:${col(n.type)}">${ico(n.type)}</div><div style="min-width:0">
 <h2 class="mono">${esc(n.label)}</h2><div class="meta">${esc(tn(n.type))} · ${nb} lien(s)${n.t?' · '+esc(n.t):''} ${st?`<span class="st ${st}">${ST[st][0]}</span>`:''}</div>${id.startsWith('enquete:')?'':`<div class="meta" style="margin-top:6px"><span class="st" style="white-space:nowrap;color:${FB[fbOf(n)][1]};border-color:${FB[fbOf(n)][1]}">${FB[fbOf(n)][2]} · ${FB[fbOf(n)][0]}</span></div>`}</div></div>`}
function fiche(id,n){const dt=n.data||{},u=urlOf(n),st=dt._statut;
 const link=v=>/^https?:\/\//.test(v)?`<a href="${esc(v)}" target="_blank">${esc(v)}</a>`:esc(v).replace(/\n/g,'<br>');
 const det=Object.entries(dt).filter(([k,v])=>!['note'].includes(k)&&!k.startsWith('_')&&v!==''&&v!=null);
 return `<h3>Évaluation</h3><div class="seg">${Object.entries(ST).map(([k,[l]])=>`<button data-s="${k}" class="${st==k?'on':''}">${l}</button>`).join('')}</div>
 <div class="row2"><button data-a="star" class="star ${dt._cle?'on':''}">${ico('star')} ${dt._cle?'Piste clé':'Marquer piste clé'}</button></div>
 ${(TRANS[n.type]||[]).length?`<h3>Recherches</h3><button class="pri" data-a="all" style="width:100%">${ico('bolt')} Tout chercher (${TRANS[n.type].length})</button>`:''}
 <h3>Actions</h3><div class="row2">${u?`<button data-a="open">${ico('open')} Ouvrir</button>`:''}<button data-a="google">${ico('google')} Google</button></div>
 <div class="row2"><button data-a="link">${ico('link2')} Relier à…</button><button data-a="child">${ico('plus')} Élément lié</button></div>
 ${id.startsWith('enquete:')?'':`<div class="row2"><button data-a="del" class="danger">${ico('trash')} Supprimer</button></div>`}
 <h3>Informations</h3><table>${det.map(([k,v])=>`<tr><td>${esc(k)}</td><td>${link(String(v))}</td></tr>`).join('')||'<tr><td colspan=2 class="hint">aucune information pour l\'instant : lance une recherche</td></tr>'}</table>
 <h3>Note de l'enquêteur</h3><textarea id="note" placeholder="Ce que tu as remarqué, ce qu'il reste à vérifier…">${esc(dt.note||'')}</textarea>`}
function rech(id,n){const tr=TRANS[n.type]||[],done=new Set((n.data||{})._faits||[]);if(!tr.length)return '<h3>Recherches</h3><div class="hint">Pas de recherche automatique pour ce type. Utilise Google ou ajoute des éléments liés.</div>';
 return `<h3>Recherches automatiques</h3><button class="pri" data-a="all" style="width:100%">${ico('bolt')} Tout chercher (${tr.length})</button>
 ${tr.map(([k,l])=>`<button class="tf ${done.has(k)?'done':''}" data-t="${k}">${ico('search')}<span>${esc(l)}</span><small>${done.has(k)?'✓ fait':'lancer'}</small></button>`).join('')}
 <h3>Recherches manuelles</h3><button class="tf" data-a="google">${ico('google')}<span>Google : « ${esc((n.short||n.label).slice(0,30))} »</span></button>`}
function lkRow(x,l){const m=G.nodes[x]||{},st=(m.data||{})._statut;return `<div class="lk" data-id="${esc(x)}"><span class="d" style="border-color:${col(m.type)};color:${col(m.type)}">${ico(m.type)}</span><span class="n">${esc(m.short||m.label||x)}</span>${st?`<span class="st ${st}">${ST[st][0]}</span>`:''}<small>${esc(l||tn(m.type))}</small></div>`}
function liens(id){const nb=G.edges.filter(e=>e.from==id||e.to==id).map(e=>[e.from==id?e.to:e.from,e.label]);return `<h3>Relié à (${nb.length})</h3>${nb.map(([x,l])=>lkRow(x,l)).join('')||'<div class="hint">aucun lien</div>'}`}
function dossier(){const ns=Object.entries(G.nodes).filter(([,n])=>n.type!='enquete'),cnt={},stc={};ns.forEach(([,n])=>{cnt[n.type]=(cnt[n.type]||0)+1;const s=(n.data||{})._statut;if(s)stc[s]=(stc[s]||0)+1});
 const mx=Math.max(1,...Object.values(cnt)),keys=ns.filter(([,n])=>(n.data||{})._cle);
 return `<div class="ent"><div class="av" style="border-color:var(--c);color:var(--c)">${ico('enquete')}</div><div><h2>${esc(NAME.replace(/_/g,' '))}</h2><div class="meta">${caseNo()}${G.created?' · ouvert le '+esc(G.created):''}</div></div></div>
 <h3>Vue d'ensemble</h3><div class="kpi"><div><b>${ns.length}</b>entités</div><div><b>${G.edges.length}</b>liens</div><div><b style="color:var(--ok)">${stc.ok||0}</b>confirmées</div><div><b style="color:var(--ck)">${stc.check||0}</b>à vérifier</div></div>
 <h3>Fiabilité du dossier</h3>${(()=>{const f={A:0,B:0,C:0,'?':0};ns.forEach(([,n])=>f[fbOf(n)]++);const tot=ns.length||1;return `<div class="fbar">${Object.keys(FB).filter(k=>f[k]).map(k=>`<i style="width:${f[k]/tot*100}%;background:${FB[k][1]}" title="${FB[k][0]} : ${f[k]}"></i>`).join('')}</div><div class="fleg">${Object.keys(FB).filter(k=>f[k]).map(k=>`<span><i style="background:${FB[k][1]}"></i>${FB[k][0]} <b>${f[k]}</b></span>`).join('')}</div>${ns.length?'':'<div class="hint">aucune entité</div>'}`})()}
 <h3>Répartition</h3>${Object.keys(cnt).sort((a,b)=>cnt[b]-cnt[a]).map(t=>`<div class="bar"><span class="lab">${ico(t,col(t))}${esc(tn(t))}</span><span class="tr"><i style="width:${cnt[t]/mx*100}%;background:${col(t)}"></i></span><b>${cnt[t]}</b></div>`).join('')||'<div class="hint">aucune entité</div>'}
 <h3>Pistes clés (${keys.length})</h3>${keys.map(([id])=>lkRow(id,'')).join('')||'<div class="hint">Marque les éléments importants comme « piste clé » depuis leur fiche.</div>'}
 <h3>Méthode</h3><ol class="steps"><li>Ajoute une cible en haut, puis <b>Ajouter + chercher</b>.</li><li>Clique une entité : <b>Fiche</b>, <b>Recherches</b>, <b>Liens</b>.</li><li>Évalue chaque piste : <b>Confirmé</b>, <b>À vérifier</b> ou <b>Fausse piste</b>.</li><li><b>Options → Rapport d'enquête</b> pour sortir le dossier en PDF.</li></ol>`}
function pistes(){const ns=Object.entries(G.nodes).filter(([,n])=>n.type!='enquete').map(([id,n])=>[id,n,deg(id)]).sort((a,b)=>b[2]-a[2]).slice(0,25);
 return `<h3>Entités les plus reliées</h3>${ns.map(([id,,d])=>lkRow(id,d+' liens')).join('')||'<div class="hint">rien pour l\'instant</div>'}`}
function journal(){const ev=(G.log||[]).slice().reverse();const added=Object.entries(G.nodes).filter(([id,n])=>n.t&&n.type!='enquete'&&!(G.log||[]).some(l=>l.id==id)).length;
 return `<h3>Journal de l'enquête</h3><div class="log">${ev.slice(0,150).map(l=>`<div class="${/Recherche|Évaluation/.test(l.txt)?'k':''}"><time>${esc(l.t)}</time>${l.id&&G.nodes[l.id]?`<a href="#" data-id="${esc(l.id)}">${esc(l.txt)}</a>`:esc(l.txt)}</div>`).join('')||'<div>Rien pour l\'instant.</div>'}</div>
 ${added?`<div class="hint" style="margin-top:10px">+ ${added} entité(s) ajoutée(s) par les modules du terminal.</div>`:''}`}
function bind(B){B.querySelectorAll('[data-id]').forEach(a=>a.onclick=ev=>{ev.preventDefault();focusN(a.dataset.id)});
 B.querySelectorAll('button[data-t]').forEach(b=>b.onclick=()=>transform(sel,b.dataset.t,b.querySelector('span').textContent));
 B.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>action(sel,b.dataset.a));
 B.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>setStatus(sel,b.dataset.s));
 const no=$('note');if(no)no.onchange=ev=>{const n=G.nodes[sel];n.data=n.data||{};n.data.note=ev.target.value;logp('Note modifiée : '+(n.short||n.label),sel);save()}}
function setStatus(id,s){const n=G.nodes[id];n.data=n.data||{};n.data._statut=n.data._statut==s?undefined:s;if(!n.data._statut)delete n.data._statut;n.data._statut_user=1;
 logp('Évaluation : '+(n.short||n.label)+' → '+(n.data._statut?ST[s][0]:'aucune'),id);render();save()}
function urlOf(n){return (n.data||{}).url||(/^https?:/.test(n.label)?n.label:null)||(n.type=='domaine'?'https://'+n.label:null)}
function action(id,a){const n=G.nodes[id];if(!n)return;
 if(a=='open')window.open(urlOf(n),'_blank');else if(a=='google')window.open('https://www.google.com/search?q='+encodeURIComponent('"'+(n.short||n.label)+'"'),'_blank');
 else if(a=='all')runAll(id);else if(a=='star'){n.data=n.data||{};n.data._cle=!n.data._cle;if(!n.data._cle)delete n.data._cle;logp((n.data._cle?'Piste clé : ':'Plus piste clé : ')+(n.short||n.label),id);render();save()}
 else if(a=='link'){linkFrom=id;toast(ico('link2')+' Clique maintenant l\'entité à relier… (Échap pour annuler)')}
 else if(a=='child'){childOf=id;$('addv').placeholder='Nouvelle entité liée à « '+(n.short||n.label).slice(0,30)+' »…';$('addv').focus()}
 else if(a=='del'&&confirm('Supprimer « '+(n.short||n.label)+' » du dossier ?')){delete G.nodes[id];G.edges=G.edges.filter(e=>e.from!=id&&e.to!=id);logp('Supprimé : '+(n.short||n.label));sel=null;render();save()}
 else if(a.startsWith('s:'))setStatus(id,a.slice(2))}
/* ---------- recherches (serveur Cat.exe) */
const SCAN=new Set();
async function transform(id,t,label,quiet){busy++;SCAN.add(id);if(!quiet)toast('<span class="spin"></span>'+esc(label)+' …');let added=0;
 try{const r=await fetch('/api/transform',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({e:NAME,id,t})});const j=await r.json();
  await poll(true);added=j.ok?j.added:0;const n=G.nodes[id];if(n)logp('Recherche « '+label+' » sur '+(n.short||n.label)+' : '+(j.ok?added+' résultat(s)':'échec'),id);
  if(!quiet){save();toast(j.ok?`${ico('check','#4caf7a')} ${added} élément(s) ajouté(s)${j.msg?' · '+esc(j.msg):''}`:`Échec : ${esc(j.error||'?')}`,4000)}}
 catch(e){toast('L\'outil Cat.exe doit rester ouvert pour lancer les recherches.',5000);$('live').classList.add('off')}busy--;SCAN.delete(id);if(sel==id)panel();return added}
async function runAll(id){const n=G.nodes[id];if(!n)return;const tr=TRANS[n.type]||[];if(!tr.length){toast('Pas de recherche automatique pour ce type.',3000);return}let tot=0;
 for(let k=0;k<tr.length;k++){toast(`<span class="spin"></span>Recherche ${k+1}/${tr.length} : ${esc(tr[k][1])} …`);tot+=await transform(id,tr[k][0],tr[k][1],true)}
 await save();toast(`${ico('check','#4caf7a')} Terminé : ${tot} élément(s) ajouté(s)`,5000);if(tot)setTimeout(()=>net.fit({animation:true}),300)}
async function save(){G.rev=(G.rev||0)+1;if(!G.created)G.created=now();saving=true;try{await fetch('/api/enquete/'+NAME,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(G)});$('live').classList.remove('off')}catch(e){$('live').classList.add('off')}saving=false}
async function poll(force){if(saving&&!force)return;try{const r=await fetch('enquetes/'+NAME+'.json?'+Date.now());$('live').classList.remove('off');if(!r.ok){if(G.rev==-1){G.rev=0;render()}return}const g=await r.json();
 if(g.rev!==G.rev){const first=G.rev==-1;G=g;render();if(first)setTimeout(()=>net.fit({animation:true}),600)}}catch(e){$('live').classList.add('off');if(G.rev==-1){G.rev=0;render()}}}
/* ---------- graphe */
function focusN(id){if(!N.get(id))return;net.selectNodes([id]);net.focus(id,{scale:1.05,animation:true});sel=id;if(!['fiche','rech','liens'].includes(tab))tab='fiche';panel();dim(id)}
function dim(id){if(pathSet)return;if(!id){N.update(N.get().map(n=>({id:n.id,opacity:(G.nodes[n.id]?.data||{})._statut=='faux'?.5:1})));return}const keep=new Set([id,...net.getConnectedNodes(id)]);N.update(N.get().map(n=>({id:n.id,opacity:keep.has(n.id)?1:.18})))}
function bfs(a,b){const adj={};G.edges.forEach(e=>{(adj[e.from]=adj[e.from]||[]).push(e.to);(adj[e.to]=adj[e.to]||[]).push(e.from)});const prev={[a]:null},q=[a];
 while(q.length){const x=q.shift();if(x==b)break;for(const y of adj[x]||[])if(!(y in prev)){prev[y]=x;q.push(y)}}if(!(b in prev))return null;const p=[];for(let x=b;x!=null;x=prev[x])p.push(x);return p.reverse()}
function layout(m){const ids=Object.keys(G.nodes);net.setOptions({layout:{hierarchical:m=='hier'?{enabled:true,direction:'UD',sortMethod:'hubsize',nodeSpacing:150,levelSeparation:140}:{enabled:false}},physics:{enabled:m=='force'||m=='hier'}});
 if(m=='circle'){const R=Math.max(260,ids.length*14);N.update(ids.map((id,i)=>({id,x:R*Math.cos(2*Math.PI*i/ids.length),y:R*Math.sin(2*Math.PI*i/ids.length)})))}
 if(m=='type'){const ty=[...new Set(ids.map(i=>G.nodes[i].type))],pos={};ids.forEach(id=>{const t=ty.indexOf(G.nodes[id].type);pos[t]=(pos[t]||0)+1;N.update({id,x:t*250,y:pos[t]*70})})}
 setTimeout(()=>net.fit({animation:true}),300)}
function report(){const ns=Object.entries(G.nodes).filter(([,n])=>n.type!='enquete'),by={};ns.forEach(([id,n])=>(by[n.type]=by[n.type]||[]).push([id,n]));
 const rel=id=>G.edges.filter(e=>e.to==id||e.from==id).map(e=>{const o=G.nodes[e.from==id?e.to:e.from];return o&&o.type!='enquete'?(o.short||o.label):null}).filter(Boolean).slice(0,6).join(', ');
 const stc={};ns.forEach(([,n])=>{const s=(n.data||{})._statut;if(s)stc[s]=(stc[s]||0)+1});
 const keys=ns.filter(([,n])=>(n.data||{})._cle);
 const h=`<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Rapport · ${esc(NAME)}</title><style>body{font:13px/1.5 "Segoe UI",system-ui,sans-serif;color:#1b1d21;margin:32px auto;max-width:960px;padding:0 20px}
h1{font-size:22px;margin:0}h2{font-size:15px;border-bottom:2px solid #1b1d21;padding-bottom:4px;margin-top:28px}.m{color:#666}table{width:100%;border-collapse:collapse;margin-top:8px}th,td{border:1px solid #ccc;padding:5px 7px;text-align:left;vertical-align:top}th{background:#f1f2f4}
.k{display:inline-block;border:1px solid #ccc;border-radius:6px;padding:8px 14px;margin:4px 6px 0 0}.k b{display:block;font-size:18px}.ok{color:#23874f}.check{color:#a86e00}.faux{color:#777}button{margin-top:14px;padding:8px 14px}@media print{button{display:none}}</style></head><body>
<div class="m">${caseNo()} · généré le ${now()} · CAT.exe</div><h1>Rapport d'enquête : ${esc(NAME.replace(/_/g,' '))}</h1>
<div><span class="k"><b>${ns.length}</b>entités</span><span class="k"><b>${G.edges.length}</b>liens</span><span class="k ok"><b>${stc.ok||0}</b>confirmées</span><span class="k check"><b>${stc.check||0}</b>à vérifier</span><span class="k faux"><b>${stc.faux||0}</b>fausses pistes</span></div>
<button onclick="print()">Imprimer / Enregistrer en PDF</button>
${keys.length?`<h2>Pistes clés</h2><ul>${keys.map(([,n])=>`<li><b>${esc(n.label)}</b> (${esc(tn(n.type))})${(n.data||{}).note?' : '+esc(n.data.note):''}</li>`).join('')}</ul>`:''}
${Object.keys(by).map(t=>`<h2>${esc(tn(t))} (${by[t].length})</h2><table><tr><th>Valeur</th><th>Évaluation</th><th>Relié à</th><th>Informations / note</th></tr>${by[t].map(([id,n])=>{const d=n.data||{};
 return `<tr><td>${esc(n.label)}</td><td class="${d._statut||''}">${d._statut?ST[d._statut][0]:'—'}</td><td>${esc(rel(id))}</td><td>${Object.entries(d).filter(([k,v])=>!k.startsWith('_')&&k!='note'&&v).slice(0,6).map(([k,v])=>esc(k)+' : '+esc(String(v).slice(0,140))).join('<br>')}${d.note?'<br><i>Note : '+esc(d.note)+'</i>':''}</td></tr>`}).join('')}</table>`).join('')}
${(G.log||[]).length?`<h2>Journal</h2><table><tr><th>Date</th><th>Événement</th></tr>${G.log.slice(-120).map(l=>`<tr><td>${esc(l.t)}</td><td>${esc(l.txt)}</td></tr>`).join('')}</table>`:''}</body></html>`;
 const w=window.open('','_blank');if(w){w.document.write(h);w.document.close()}else dl('rapport_'+NAME+'.html',h,'text/html')}
function menu(m){$('menu').style.display='none';
 if(['force','hier','circle','type'].includes(m))layout(m);else if(m=='report')report();
 else if(m=='phys'){const on=!net.physics.options.enabled;net.setOptions({physics:{enabled:on}});toast(on?'Animation activée':'Positions figées',2000)}
 else if(m=='keys'){onlyKeys=!onlyKeys;render();toast(onlyKeys?'Seules les pistes clés sont affichées':'Tout est affiché',2500)}
 else if(m=='nofaux'){noFaux=!noFaux;render();toast(noFaux?'Fausses pistes masquées':'Fausses pistes affichées',2500)}
 else if(m=='clu'){clustered=!clustered;if(!clustered){net.setData({nodes:N,edges:E});render();return}
  Object.keys(TYPES).forEach(t=>{const c=Object.values(G.nodes).filter(n=>n.type==t).length;if(c>2&&t!='enquete')net.cluster({joinCondition:o=>o.group==t,clusterNodeProperties:{id:'cl:'+t,label:tn(t)+' ×'+c,shape:'circularImage',image:svgNode(t),size:22+Math.min(c,30),color:{border:col(t),background:'#0e1028'},borderWidth:2,font:{color:'#e4e9ff',size:13,strokeWidth:4,strokeColor:'#07081a'}}})})}
 else if(m=='path'){const s=net.getSelectedNodes();if(s.length!=2){toast('Ctrl + clic sur 2 entités, puis relance « Chemin ».',4000);return}const p=bfs(s[0],s[1]);if(!p){toast('Aucun lien entre ces deux entités.',4000);return}
  pathSet=new Set(p);render();toast(p.map(i=>esc((G.nodes[i].short||G.nodes[i].label).slice(0,20))).join(' → '),9000)}
 else if(m=='png'){const c=document.querySelector('#net canvas'),o=document.createElement('canvas');o.width=c.width;o.height=c.height;const x=o.getContext('2d');x.fillStyle='#07081a';x.fillRect(0,0,o.width,o.height);x.drawImage(c,0,0);
  x.fillStyle='#7480a8';x.font='14px sans-serif';x.fillText(caseNo()+' · '+NAME+' · '+now(),16,o.height-16);dl('graphe_'+NAME+'.png',null,null,o.toDataURL())}
 else if(m=='json')dl('enquete_'+NAME+'.json',JSON.stringify(G,null,1),'application/json');
 else if(m=='csv')dl('enquete_'+NAME+'.csv','﻿type;valeur;évaluation;relié à;note;détails\n'+Object.entries(G.nodes).map(([id,n])=>[tn(n.type),n.label,((n.data||{})._statut&&ST[n.data._statut][0])||'',G.edges.filter(e=>e.to==id).map(e=>(G.nodes[e.from]||{}).label).join(' | '),(n.data||{}).note||'',JSON.stringify(n.data||{})].map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(';')).join('\n'),'text/csv');
 else if(m=='imp')$('imp').click()}
function dl(name,txt,type,href){const a=document.createElement('a');a.download=name;a.href=href||URL.createObjectURL(new Blob([txt],{type}));a.click()}
function ctx(x,y,id){const n=G.nodes[id],C=$('ctx');if(!n)return;const tr=TRANS[n.type]||[],u=urlOf(n),st=(n.data||{})._statut;
 C.innerHTML=`<div class="h">${esc(tn(n.type))} · ${esc((n.short||n.label).slice(0,36))}</div>`+(tr.length?`<div class="i" data-a="all">${ico('bolt')} Tout chercher</div>`+tr.map(([k,l])=>`<div class="i" data-t="${k}">${ico('search')} ${esc(l)}</div>`).join('')+'<hr>':'')+
  Object.entries(ST).map(([k,[l,c]])=>`<div class="i" data-a="s:${k}">${st==k?ico('check',c):`<svg class="i" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5" style="color:${c}" stroke="${c}"/></svg>`} ${l}</div>`).join('')+
  `<div class="i" data-a="star">${ico('star')} ${(n.data||{})._cle?'Retirer des pistes clés':'Piste clé'}</div><hr>`+
  (u?`<div class="i" data-a="open">${ico('open')} Ouvrir le lien</div>`:'')+`<div class="i" data-a="google">${ico('google')} Rechercher sur Google</div><div class="i" data-a="link">${ico('link2')} Relier à…</div><div class="i" data-a="child">${ico('plus')} Ajouter un élément lié</div>`+
  (id.startsWith('enquete:')?'':`<hr><div class="i" data-a="del">${ico('trash')} Supprimer</div>`);
 C.style.display='block';C.style.left=Math.min(x,innerWidth-260)+'px';C.style.top=Math.max(8,Math.min(y,innerHeight-C.offsetHeight-8))+'px';
 C.querySelectorAll('.i').forEach(it=>it.onclick=()=>{C.style.display='none';if(it.dataset.t)transform(id,it.dataset.t,it.textContent.trim());else action(id,it.dataset.a)})}
function start(){N=new vis.DataSet();E=new vis.DataSet();
 net=new vis.Network($('net'),{nodes:N,edges:E},{interaction:{hover:true,multiselect:true,keyboard:false,tooltipDelay:300},
  physics:{solver:'forceAtlas2Based',forceAtlas2Based:{gravitationalConstant:-70,springLength:130,springConstant:.05,damping:.6,avoidOverlap:.4},stabilization:{iterations:180}}});
 net.on('click',p=>{$('ctx').style.display='none';const id=p.nodes[0];
  if(linkFrom&&id&&id!=linkFrom){const l=prompt('Nature du lien (facultatif, ex : même photo, même email…)','')||'';G.edges.push({from:linkFrom,to:id,label:l});logp('Lien : '+(G.nodes[linkFrom].short||G.nodes[linkFrom].label)+' ↔ '+(G.nodes[id].short||G.nodes[id].label)+(l?' ('+l+')':''),id);linkFrom=null;$('toast').style.display='none';render();save();focusN(id);return}
  if(pathSet){pathSet=null;render()}if(id&&net.isCluster&&net.isCluster(id)){net.openCluster(id);return}
  if(id){focusN(id)}else{sel=null;tab='dossier';panel();dim(null)}});
 net.on('afterDrawing',c=>{const t=Date.now()/1000;
  for(const id of Object.keys(G.nodes)){const n=G.nodes[id];if(n.type=='enquete')continue;const v=N.get(id);if(!v||v.hidden)continue;const fb=fbOf(n);if(fb=='?')continue;const bb=net.getBoundingBox(id);if(!bb)continue;
   const r0=Math.min(bb.right-bb.left,90)/2,cx=(bb.left+bb.right)/2,cy=bb.top+r0,px=cx+r0*.72,py=cy-r0*.72;c.save();c.globalAlpha=(n.data||{})._statut=='faux'?.4:1;
   c.beginPath();c.arc(px,py,6.5,0,7);c.fillStyle=FB[fb][1];c.fill();c.lineWidth=2;c.strokeStyle='#07081a';c.stroke();
   c.fillStyle='#07081a';c.font='bold 8.5px system-ui,sans-serif';c.textAlign='center';c.textBaseline='middle';c.fillText(fb,px,py+.5);c.restore()}
  for(const id of Object.keys(G.nodes)){const n=G.nodes[id],d=n.data||{},scan=SCAN.has(id);if(!(d._cle||scan||id==sel))continue;const bb=net.getBoundingBox(id);if(!bb||!N.get(id)||N.get(id).hidden)continue;
   const cx=(bb.left+bb.right)/2,r0=Math.min(bb.right-bb.left,90)/2,cy=bb.top+r0;c.save();
   if(scan){for(let k=0;k<2;k++){const ph=(t*1.1+k*.5)%1;c.beginPath();c.arc(cx,cy,r0+6+ph*46,0,7);c.strokeStyle='#00e5ff';c.globalAlpha=(1-ph)*.75;c.lineWidth=3;c.stroke()}}
   else if(d._cle){const ph=(Math.sin(t*2.4)+1)/2;c.beginPath();c.arc(cx,cy,r0+9+ph*5,0,7);c.strokeStyle='#e0a83a';c.globalAlpha=.35+ph*.4;c.lineWidth=2.5;c.setLineDash([7,6]);c.lineDashOffset=-t*18;c.stroke()}
   if(id==sel&&!scan){c.beginPath();c.arc(cx,cy,r0+7,0,7);c.strokeStyle='#00e5ff';c.globalAlpha=.9;c.lineWidth=2;c.setLineDash([3,5]);c.lineDashOffset=t*14;c.stroke()}c.restore()}});
 setInterval(()=>{if(SCAN.size||sel||Object.values(G.nodes).some(n=>(n.data||{})._cle))net.redraw()},70);
 net.on('doubleClick',p=>{const n=G.nodes[p.nodes[0]];if(n&&urlOf(n))window.open(urlOf(n),'_blank')});
 net.on('oncontext',p=>{p.event.preventDefault();const id=net.getNodeAt(p.pointer.DOM);if(id&&G.nodes[id]){net.selectNodes([id]);ctx(p.event.clientX,p.event.clientY,id)}});
 poll();setInterval(()=>{if(!busy)poll()},2000)}
/* ---------- interface */
PH=$('addv').placeholder;$('addt').innerHTML=Object.keys(TYPES).filter(k=>k!='enquete').map(k=>`<option value="${k}">${esc(tn(k))}</option>`).join('');
$('caseic').innerHTML=ico('enquete');$('emptyic').innerHTML=ico('enquete');$('qic').innerHTML=ico('search');$('addall').innerHTML=ico('bolt')+' Ajouter + chercher';$('more').innerHTML=ico('dots')+' Options';$('zfit').innerHTML=ico('fit');setAddIcon();
$('addv').oninput=ev=>{if(!manualType)$('addt').value=ttype(ev.target.value)||'pseudo';setAddIcon()};$('addt').onchange=()=>{manualType=true;setAddIcon()};
$('addf').onsubmit=ev=>{ev.preventDefault();submitAdd(false)};$('addall').onclick=()=>submitAdd(true);
$('more').onclick=ev=>{ev.stopPropagation();const M=$('menu');M.style.display=M.style.display=='block'?'none':'block'};
$('menu').querySelectorAll('.i').forEach(i=>i.onclick=()=>menu(i.dataset.m));
$('zin').onclick=()=>net.moveTo({scale:net.getScale()*1.25,animation:true});$('zout').onclick=()=>net.moveTo({scale:net.getScale()/1.25,animation:true});$('zfit').onclick=()=>net.fit({animation:true});
$('imp').onchange=async ev=>{const f=ev.target.files[0];if(!f)return;try{const g=JSON.parse(await f.text());Object.assign(G.nodes,g.nodes||{});(g.edges||[]).forEach(e=>G.edges.push(e));logp('Import : '+f.name);render();save();toast('Importé',3000)}catch(e){toast('Fichier invalide',3000)}};
$('q').oninput=ev=>{const q=ev.target.value.toLowerCase();if(!q){dim(null);return}const hit=Object.keys(G.nodes).filter(id=>(G.nodes[id].label+JSON.stringify(G.nodes[id].data||{})).toLowerCase().includes(q));
 N.update(N.get().map(n=>({id:n.id,opacity:hit.includes(n.id)?1:.1})));if(hit.length==1)focusN(hit[0])};
document.addEventListener('keydown',ev=>{if(['INPUT','TEXTAREA','SELECT'].includes(ev.target.tagName)){if(ev.key=='Escape')ev.target.blur();return}
 if(ev.key=='/'){ev.preventDefault();$('q').focus()}else if(ev.key=='f'||ev.key=='F')net.fit({animation:true});
 else if(ev.key=='Escape'){linkFrom=null;childOf=null;$('addv').placeholder=PH;pathSet=null;$('toast').style.display='none';$('ctx').style.display='none';net.unselectAll();sel=null;tab='dossier';render();dim(null)}
 else if(ev.key=='Delete'){const ids=net.getSelectedNodes().filter(i=>!i.startsWith('enquete:'));if(ids.length&&confirm('Supprimer '+ids.length+' entité(s) ?')){ids.forEach(i=>delete G.nodes[i]);G.edges=G.edges.filter(e=>G.nodes[e.from]&&G.nodes[e.to]);logp('Supprimé : '+ids.length+' entité(s)');sel=null;render();save()}}});
document.addEventListener('click',ev=>{if(!ev.target.closest('.dd'))$('menu').style.display='none';if(!ev.target.closest('#ctx'))$('ctx').style.display='none'});
load(0);
</script></body></html>"""
