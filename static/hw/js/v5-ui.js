/* Accessible tabs and motion. Content remains available without JS. */
(function(){'use strict';const $=(q,r=document)=>r.querySelector(q),$$=(q,r=document)=>[...r.querySelectorAll(q)];const d=window.HW_V5;if(!d)return;
const tabs=$$('[data-found-tab]');if(!tabs.length)return;let current=0;
function lang(){let v=new URL(location.href).searchParams.get('lang');return d.panels[v]?v:(d.panels[document.documentElement.lang.split('-')[0]]?document.documentElement.lang.split('-')[0]:'en');}
function render(){const row=d.panels[lang()][current],p=$('#hw-found-intro'),list=$('#hw-found-items');if(!p||!list)return;p.textContent=row[1];list.replaceChildren(...row[2].map(t=>{const el=document.createElement('p');const dot=document.createElement('i');dot.setAttribute('aria-hidden','true');const span=document.createElement('span');span.textContent=t;el.append(dot,span);return el}));tabs.forEach((b,i)=>{b.classList.toggle('is-active',i===current);b.setAttribute('aria-selected',i===current?'true':'false');b.tabIndex=i===current?0:-1;});}
tabs.forEach((b,i)=>{b.addEventListener('click',()=>{current=i;render()});b.addEventListener('keydown',e=>{let n=e.key==='ArrowRight'?(i+1)%tabs.length:e.key==='ArrowLeft'?(i+tabs.length-1)%tabs.length:-1;if(n!==-1){e.preventDefault();current=n;render();tabs[n].focus()}})});render();
$('#language-picker')?.addEventListener('click',()=>{requestAnimationFrame(render);setTimeout(render,20)});
document.addEventListener('click',e=>{if(e.target.closest('[data-lang]'))setTimeout(render,0)});
})();