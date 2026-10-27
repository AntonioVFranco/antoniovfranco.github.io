/* Motion and direct email composition. No external library or network requests. */
(()=>{'use strict';
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const sections=[...document.querySelectorAll('.hw-home-hero,.hw-found-section,.hw-services-section,.hw-approach,.hw-editorial,.hw-shansu,.hw-preview-section,.hw-ecosystem,.hw-contact-section')];
if(!reduced&&'IntersectionObserver' in window){
 const obs=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){e.target.classList.add('is-visible');obs.unobserve(e.target)}},{threshold:.09,rootMargin:'0px 0px -30px 0px'});
 sections.forEach(el=>{el.classList.add('hw-reveal');obs.observe(el)});
}
const form=document.getElementById('contact-mail-form');
form?.addEventListener('submit',async e=>{e.preventDefault();if(!form.reportValidity())return;
 const status=form.querySelector('.hw-formstatus'),button=form.querySelector('[type="submit"]');
 const lang=document.documentElement.lang.split('-')[0],messages={en:['Secure delivery is not active yet.','Message received.','Delivery failed. Please try again.'],pt:['O envio seguro ainda não está ativo.','Mensagem recebida.','Falha no envio. Tente novamente.'],es:['El envío seguro aún no está activo.','Mensaje recibido.','Error de envío. Inténtalo de nuevo.'],zh:['安全发送功能尚未启用。','已收到消息。','发送失败，请重试。']}[lang]||window.HW_STATUS?.[lang]?.slice(4,7)||['Secure delivery is not active yet.','Message received.','Delivery failed. Please try again.'];
 const config=window.HUYAWO_LEADS||{};
 if(location.protocol==='file:'||!/^https:\/\/[a-z0-9-]+\.supabase\.co\/functions\/v1\/lead-intake$/.test(config.functionUrl||'')||!config.turnstileSiteKey){status.textContent=messages[0];return;}
 button.disabled=true;status.textContent='';
 try{const token=await window.HUYAWO_TURNSTILE_TOKEN();const data=new FormData(form);if(data.get('consent')!=='on')return;
  const ctrl=new AbortController(),timeout=setTimeout(()=>ctrl.abort(),12000);let res;
  try{res=await fetch(config.functionUrl,{method:'POST',headers:{'content-type':'application/json'},mode:'cors',cache:'no-store',referrerPolicy:'no-referrer',signal:ctrl.signal,body:JSON.stringify({source:'contact',email:String(data.get('email')||'').trim(),name:String(data.get('name')||'').trim(),subject:String(data.get('topic')||'').trim(),message:String(data.get('message')||'').trim(),topic:'general',locale:lang,consent:true,turnstileToken:token})});}finally{clearTimeout(timeout);}
  if(!res.ok)throw Error('delivery');status.textContent=messages[1];status.classList.add('success');form.reset();
 }catch{status.textContent=messages[2];status.classList.remove('success');}finally{button.disabled=false;}
});
})();
