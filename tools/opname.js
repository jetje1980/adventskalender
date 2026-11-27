// Neemt het waslijnspelletje en de wasbon op uit de echte app (rondleiding), en maakt maskers van raampje 2 en 20.
const {chromium}=require('playwright'); const fs=require('fs');
const UIT=process.argv[2]; fs.mkdirSync(UIT+'/spel',{recursive:true});
(async()=>{const b=await chromium.launch();
 // 1. het spelletje
 let p=await (await b.newContext({viewport:{width:400,height:820},deviceScaleFactor:3})).newPage();
 await p.goto('file:///home/user/adventskalender/index.html#gast'); await p.waitForTimeout(800);
 await p.evaluate(()=>{ demoDag=2; teken(); }); await p.evaluate(()=>{ klaar=(d,w)=>{ markeer(d); window.__klaar=()=>onthul(d,true); }; });
 await p.addStyleTag({content:'.kledje{transition:left 1.2s ease-in-out,top 1.2s ease-in-out!important}'});
 await p.click('.raam[data-dag="2"]',{force:true}); await p.waitForTimeout(500);
 const lijn=await p.$('#lijn'); const lb=await lijn.boundingBox(); let n=0; const tikken=[];
 const foto=async()=>{ await lijn.screenshot({path:`${UIT}/spel/${String(n++).padStart(3,'0')}.png`}); };
 for(let i=0;i<6;i++){ await foto(); await p.waitForTimeout(40); }
 for(let i=0;i<3;i++){
   const k=await p.$(`.kledje[data-i="${i}"]`); const kb=await k.boundingBox();
   tikken.push({frame:n, x:(kb.x+kb.width/2-lb.x)/lb.width, y:(kb.y+kb.height/2-lb.y)/lb.height});
   await k.click({force:true});
   for(let j=0;j<14;j++){ await foto(); await p.waitForTimeout(20); }
 }
 for(let i=0;i<8;i++){ await foto(); await p.waitForTimeout(60); }
 await p.evaluate(()=>window.__klaar()); await p.waitForTimeout(1500);
 const bon=await p.$('.bon'); await bon.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
 await bon.screenshot({path:UIT+'/bon1.png'});
 const knop=await p.$('[data-inwissel]'); const bb=await bon.boundingBox(), kb=await knop.boundingBox();
 const tikBon={x:(kb.x+kb.width/2-bb.x)/bb.width, y:(kb.y+kb.height/2-bb.y)/bb.height};
 await knop.click(); await p.waitForTimeout(300); await (await p.$('.bon')).screenshot({path:UIT+'/bon2.png'});
 fs.writeFileSync(UIT+'/spel.json', JSON.stringify({tikken, tikBon, frames:n}));
 // 2. maskers: glas van raampje 2 en 20 magenta maken
 p=await (await b.newContext({viewport:{width:400,height:900},deviceScaleFactor:6})).newPage();
 await p.route('https://kjvufjkhfjbuxnuqdeev.supabase.co/**',r=>r.abort());
 await p.goto('file:///home/user/adventskalender/index.html'); await p.waitForTimeout(1500);
 const huis=await p.$('#starthuis'); const hb=await huis.boundingBox(); const ramen={};
 for(const d of [2,20]){ const g=await (await p.$(`#starthuis .raam[data-dag="${d}"] .glas`)).boundingBox(); ramen[d]=[(g.x-hb.x)*6,(g.y-hb.y)*6,g.width*6,g.height*6]; }
 await p.addStyleTag({content:'#starthuis .raam[data-dag="2"] .glas,#starthuis .raam[data-dag="20"] .glas{background:#ff00ff!important}#starthuis .raam[data-dag="2"] .glas *,#starthuis .raam[data-dag="20"] .glas *,#starthuis .raam[data-dag="2"] .nr,#starthuis .raam[data-dag="20"] .nr{visibility:hidden}'});
 await huis.screenshot({path:UIT+'/huis-masker.png'});
 fs.writeFileSync(UIT+'/ramen.json', JSON.stringify(ramen));
 console.log(JSON.stringify({ramen, tikken, tikBon, frames:n}));
 await b.close();})();
