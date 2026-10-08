export const SIZES = {'1:1':[1200,1200],'16:9':[1920,1080],'9:16':[1080,1920],'1.19:1':[1190,1000],'4:5':[1080,1350]};
export const TEMPLATES = [{id:'photo',name:'포토 임팩트',desc:'실사 사진 · 선명한 헤드라인',color:'#08d5df'},{id:'thread',name:'스레드 스토리',desc:'일상 사진 · 소셜 포스트 구성',color:'#a5b4fc'},{id:'card',name:'클린 카드',desc:'화이트 프레임 · 컬러 포인트',color:'#7945d5'}];
export const clone = o => structuredClone(o);
export const uid = () => crypto.randomUUID();
const layer = (role,type,x,y,w,h,extra={}) => ({id:uid(),role,name:role,type,x:Math.round(x),y:Math.round(y),w:Math.round(w),h:Math.round(h),visible:true,locked:role==='배경'||type==='gradient',opacity:1,rotation:0,...extra});
const txt = (role,text,x,y,w,h,size,extra={}) => layer(role,'text',x,y,w,h,{text,fontSize:size,fontFamily:'Arial, "Malgun Gothic", sans-serif',weight:800,color:'#ffffff',align:'left',lineHeight:1.17,...extra});
export function createBanner(brief,ratio='1:1',template='photo') {
 const [W,H]=SIZES[ratio]||SIZES['1:1']; const wide=W/H>1.5; const tall=H/W>1.5; const s=Math.min(W,H); const p=s*.055; const accent=brief.accent||TEMPLATES.find(t=>t.id===template)?.color||'#08d5df'; const layers=[];
 const image=(x,y,w,h,r=0)=>layer('사진','image',x,y,w,h,{src:brief.photo||'',fit:'cover',cropX:50,cropY:50,radius:r});
 const logo=(x,y,w)=>brief.logo?layer('로고','image',x,y,w,s*.07,{src:brief.logo,fit:'contain',cropX:50,cropY:50}):txt('브랜드',brief.brand||'CLS · 쿠팡알바',x,y,w,s*.055,s*.025);
 const main=brief.main||'[단순분류]\n원하는 날 출근해요'; const sub=brief.sub||'단기 · 주말 근무 모집'; const cta=brief.cta||'지금 바로 지원'; const foot=brief.footnote||'';
 const button=(x,y,w,h)=>layer('CTA','button',x,y,w,h,{text:cta,color:template==='card'?'#ffffff':'#08181c',fill:accent,fontSize:s*.035,weight:800,radius:s*.016});
 if(template==='thread') {
   layers.push(layer('배경','rect',0,0,W,H,{fill:'#101114'}));
   layers.push(logo(p,p,s*.30));
   if(wide){layers.push(image(W*.53,p,W*.42,H*.78,s*.025)); layers.push(txt('메인 카피',main,p,H*.2,W*.43,H*.31,s*.058));layers.push(txt('서브 카피',sub,p,H*.54,W*.42,H*.14,s*.028,{weight:400,color:'#c5c8d0'}));layers.push(button(p,H*.78,W*.42,H*.12));}
   else {layers.push(txt('메인 카피',main,p,H*.12,W-2*p,H*.17,s*.055)); layers.push(image(p,H*.31,W-2*p,H*(tall?.42:.36),s*.025)); layers.push(txt('소셜 아이콘','♡   ◯   ↗',p,H*(tall?.745:.685),W*.5,H*.045,s*.039));layers.push(txt('서브 카피',sub,p,H*(tall?.80:.75),W-2*p,H*.08,s*.026,{weight:400,color:'#c5c8d0'}));layers.push(button(p,H*.885,W-2*p,H*.065));}
 } else if(template==='card') {
   layers.push(layer('배경','rect',0,0,W,H,{fill:'#eee8f5'})); layers.push(layer('카드','rect',p*.55,p*.55,W-p*1.1,H-p*1.1,{fill:'#ffffff',radius:s*.04}));
   layers.push(image(wide?W*.51:W*.46,H*.06,wide?W*.43:W*.48,H*.68,s*.035));
   layers.push(txt('브랜드',brief.brand||'CLS · 쿠팡알바',p,H*.09,W*.4,s*.06,s*.022,{color:'#625578'}));
   if(brief.logo) layers.push(layer('로고','image',p,H*.065,W*.32,s*.055,{src:brief.logo,fit:'contain',cropX:50,cropY:50}));
   layers.push(txt('메인 카피',main,p,H*.22,W*.38,H*.37,s*.065,{color:accent})); layers.push(txt('서브 카피',sub,p,H*.61,W*.37,H*.1,s*.027,{color:'#40394e',weight:600})); layers.push(button(p,H*.78,W-2*p,H*.105));
 } else {
   layers.push(layer('배경','rect',0,0,W,H,{fill:'#203b48'}),image(0,0,W,H),layer('명암','gradient',0,0,W,H,{fill:'#050e1d',opacity:.88}));
   layers.push(logo(p,tall?H*.12:p,W*.7)); const mw=wide?W*.65:W-2*p;
   layers.push(txt('서브 카피',sub,p,H*.53,mw,H*.07,s*.032,{color:accent,weight:800})); layers.push(txt('메인 카피',main,p,H*.625,mw,H*.20,s*.069)); layers.push(button(p,H*.855,wide?W*.52:W-2*p,H*.073));
 }
 if(foot)layers.push(txt('안내 문구',foot,p,H*.955,W-2*p,H*.036,s*.013,{color:template==='card'?'#55505c':'#e0e1e6',weight:400,lineHeight:1.2}));
 return {id:uid(),name:brief.name||'새 배너',ratio,width:W,height:H,template,brief:clone(brief),layers};
}
export function variation(source,ratio){
 const b=clone(source.brief); const roleText={'메인 카피':'main','서브 카피':'sub','CTA':'cta','안내 문구':'footnote','브랜드':'brand'};
 for(const l of source.layers){if(roleText[l.role])b[roleText[l.role]]=l.text;if(l.role==='사진')b.photo=l.src;if(l.role==='로고')b.logo=l.src;if(l.role==='CTA')b.accent=l.fill;}
 const target=createBanner(b,ratio,source.template); const sourceRoles=new Set(source.layers.map(l=>l.role));target.layers=target.layers.filter(l=>sourceRoles.has(l.role)); const baseRoles=new Set(target.layers.map(l=>l.role));
 for(const t of target.layers){const a=source.layers.find(l=>l.role===t.role);if(a){for(const key of ['color','fill','fontFamily','weight','align','opacity','visible','locked','cropX','cropY','rotation'])if(a[key]!==undefined)t[key]=a[key];}}
 for(const a of source.layers){if(!baseRoles.has(a.role)){const l=clone(a);l.id=uid();l.x*=target.width/source.width;l.y*=target.height/source.height;l.w*=target.width/source.width;l.h*=target.height/source.height;if(l.fontSize)l.fontSize*=Math.min(target.width,target.height)/Math.min(source.width,source.height);target.layers.push(l);}}
 target.name=source.name;return target;
}
export function wrapText(ctx,text,maxWidth){
 const lines=[];for(const para of String(text).split('\n')){let line='';for(const ch of [...para]){if(line && ctx.measureText(line+ch).width>maxWidth){lines.push(line.trimEnd());line=ch.trimStart();}else line+=ch;}lines.push(line);}return lines;
}
export function textLayout(ctx,l){let size=l.fontSize||40;let lines=[];for(let i=0;i<80;i++){ctx.font=`${l.weight||700} ${size}px ${l.fontFamily||'Arial, "Malgun Gothic", sans-serif'}`;lines=wrapText(ctx,l.text||'',Math.max(1,l.w));if(lines.length*size*(l.lineHeight||1.17)<=l.h || size<=8)break;size=Math.max(8,size-1);}return{size,lines};}
const cache=new Map();
export async function loadImage(src){if(!src)return null;if(!cache.has(src)){cache.set(src,new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>{cache.delete(src);reject(new Error('이미지를 읽지 못했습니다. 다시 업로드해 주세요.'));};im.src=src;}));}return cache.get(src);}
function rounded(ctx,x,y,w,h,r=0){ctx.beginPath();ctx.roundRect(x,y,Math.max(1,w),Math.max(1,h),Math.min(r,w/2,h/2));}
export async function render(canvas,banner,{selected=null,scale=1}={}){
 const images=await Promise.all(banner.layers.map(l=>l.type==='image'?loadImage(l.src):null));
 canvas.width=Math.round(banner.width*scale);canvas.height=Math.round(banner.height*scale);const ctx=canvas.getContext('2d');ctx.scale(scale,scale);ctx.fillStyle='#fff';ctx.fillRect(0,0,banner.width,banner.height);
 banner.layers.forEach((l,index)=>{if(!l.visible)return;ctx.save();ctx.globalAlpha=l.opacity??1;ctx.translate(l.x+l.w/2,l.y+l.h/2);ctx.rotate((l.rotation||0)*Math.PI/180);ctx.translate(-l.w/2,-l.h/2);
  if(l.type==='rect'||l.type==='button'){ctx.fillStyle=l.fill||'#ffffff';rounded(ctx,0,0,l.w,l.h,l.radius||0);ctx.fill();}
  if(l.type==='gradient'){const g=ctx.createLinearGradient(0,l.h*.15,0,l.h);g.addColorStop(0,'transparent');g.addColorStop(1,l.fill||'#000000');ctx.fillStyle=g;ctx.fillRect(0,0,l.w,l.h);}
  if(l.type==='image'){
   rounded(ctx,0,0,l.w,l.h,l.radius||0);ctx.clip();const im=images[index];
   if(im){const z=l.fit==='contain'?Math.min(l.w/im.width,l.h/im.height):Math.max(l.w/im.width,l.h/im.height);const dw=im.width*z,dh=im.height*z;ctx.drawImage(im,(l.w-dw)*(l.cropX??50)/100,(l.h-dh)*(l.cropY??50)/100,dw,dh);}
   else {const g=ctx.createLinearGradient(0,0,l.w,l.h);g.addColorStop(0,'#416974');g.addColorStop(1,'#152331');ctx.fillStyle=g;ctx.fillRect(0,0,l.w,l.h);ctx.strokeStyle='#ffffff18';ctx.lineWidth=3;for(let n=1;n<9;n++){ctx.strokeRect(l.w*n/10,l.h*.08,l.w*.09,l.h*.72);}ctx.fillStyle='#d9edf0';ctx.textAlign='center';ctx.font=`500 ${Math.min(l.w,l.h)*.045}px Arial, "Malgun Gothic", sans-serif`;ctx.fillText('사진을 업로드해 주세요',l.w/2,l.h*.4);}
  }
  if(l.type==='text'||l.type==='button'){const t=l.type==='button'?{...l,w:l.w*.88,h:l.h*.8,align:'center'}:l;const {size,lines}=textLayout(ctx,t);ctx.fillStyle=l.color||'#fff';ctx.textBaseline='top';ctx.textAlign=t.align||'left';const x=l.type==='button'?l.w/2:t.align==='center'?l.w/2:t.align==='right'?l.w:0;const y=l.type==='button'?(l.h-lines.length*size*(l.lineHeight||1.17))/2:0;lines.forEach((line,i)=>ctx.fillText(line,x,y+i*size*(l.lineHeight||1.17)));}
  ctx.restore();
 });
 if(selected){const l=banner.layers.find(l=>l.id===selected);if(l&&l.visible){ctx.save();ctx.strokeStyle='#7c5cff';ctx.lineWidth=2/scale;ctx.setLineDash([6/scale,3/scale]);ctx.strokeRect(l.x,l.y,l.w,l.h);ctx.setLineDash([]);ctx.fillStyle='#7c5cff';ctx.fillRect(l.x+l.w-5/scale,l.y+l.h-5/scale,10/scale,10/scale);ctx.restore();}}
 return canvas;
}
export function validateProject(p){
 if(!p||p.version!==1||!Array.isArray(p.banners)||p.banners.length>50)throw new Error('지원하지 않는 프로젝트 파일입니다.');
 const finite=(x,a,b)=>Number.isFinite(x)&&x>=a&&x<=b;
 const safeImage=src=>!src||(typeof src==='string'&&/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(src));
 for(const b of [...p.banners,p.draft?{brief:p.draft}:{}]){for(const k of ['photo','logo','reference'])if(!safeImage(b.brief?.[k]))throw new Error('프로젝트의 이미지는 내장 이미지 형식이어야 합니다.');}
 for(const b of p.banners){if(!SIZES[b.ratio]||!TEMPLATES.some(t=>t.id===b.template)||!finite(b.width,100,4096)||!finite(b.height,100,4096)||!Array.isArray(b.layers)||b.layers.length>100)throw new Error('배너 규격이 올바르지 않습니다.');
  for(const l of b.layers){if(!['text','image','rect','button','gradient'].includes(l.type)||!finite(l.x,-8192,8192)||!finite(l.y,-8192,8192)||!finite(l.w,1,8192)||!finite(l.h,1,8192))throw new Error('레이어가 올바르지 않습니다.');if(l.src&&!/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(l.src))throw new Error('이미지는 PNG, JPEG, WebP 형식만 지원합니다.');if(l.text&&String(l.text).length>5000)throw new Error('텍스트가 너무 깁니다.');}
 }return p;
}
