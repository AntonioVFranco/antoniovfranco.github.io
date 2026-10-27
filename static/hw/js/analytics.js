/* GA4 basic consent mode: the Google tag is loaded only after explicit consent. */
(()=>{'use strict';
const id=window.HUYAWO_GA4?.measurementId?.trim()||'';
if(!/^G-[A-Z0-9]+$/.test(id))return;
const key='hw-ga4-consent-v1';
const lang=location.pathname.match(/\/(en|pt|es|zh|ar|ru|it|fr|de|ja|ko)\/(?:index\.html)?$/)?.[1]||'en';
const copy={
 en:['Site analytics','May we use Google Analytics to understand visits? It is optional.','Allow analytics','Decline','Analytics preferences','Your analytics choice has been reset.'],
 pt:['Medição de visitas','Podemos usar o Google Analytics para entender as visitas? Isso é opcional.','Aceitar análise','Recusar','Preferências de análise','Sua escolha foi redefinida.'],
 es:['Análisis de visitas','¿Podemos usar Google Analytics para entender las visitas? Es opcional.','Permitir análisis','Rechazar','Preferencias de análisis','Se restableció su elección.'],
 zh:['访问统计','我们可以使用 Google Analytics 了解网站访问情况吗？这是可选的。','允许统计','拒绝','统计偏好','您的选择已重置。'],
 ar:['تحليل الزيارات','هل تسمح باستخدام Google Analytics لفهم زيارات الموقع؟ هذا اختياري.','السماح بالتحليل','رفض','تفضيلات التحليل','أُعيد ضبط اختيارك.'],
 ru:['Аналитика посещений','Можно использовать Google Analytics для анализа посещений? Это необязательно.','Разрешить','Отказаться','Настройки аналитики','Ваш выбор сброшен.'],
 it:['Analisi delle visite','Possiamo usare Google Analytics per capire le visite? È facoltativo.','Consenti analisi','Rifiuta','Preferenze analisi','La tua scelta è stata reimpostata.'],
 fr:['Analyse des visites','Pouvons-nous utiliser Google Analytics pour comprendre les visites ? C’est facultatif.','Autoriser','Refuser','Préférences d’analyse','Votre choix a été réinitialisé.'],
 de:['Besuchsanalyse','Dürfen wir Google Analytics zur Auswertung der Besuche verwenden? Dies ist freiwillig.','Zulassen','Ablehnen','Analyse-Einstellungen','Ihre Auswahl wurde zurückgesetzt.'],
 ja:['アクセス解析','訪問状況を把握するために Google Analytics を使用してもよろしいですか？ 任意です。','許可する','拒否する','解析の設定','選択をリセットしました。'],
 ko:['방문 분석','방문 현황을 파악하기 위해 Google Analytics를 사용해도 될까요? 선택 사항입니다.','허용','거부','분석 설정','선택을 초기화했습니다.']
}[lang];
function stored(){try{return localStorage.getItem(key)}catch{return null}}
function save(value){try{localStorage.setItem(key,value)}catch{}}
function load(){if(window.__huyawoGa4Loaded)return;window.__huyawoGa4Loaded=true;
 window.dataLayer=window.dataLayer||[];window.gtag=function(){window.dataLayer.push(arguments)};
 window.gtag('js',new Date());window.gtag('config',id,{anonymize_ip:true});
 const tag=document.createElement('script');tag.async=true;tag.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(id);document.head.append(tag);
}
function prompt(){if(document.getElementById('hw-analytics-consent'))return;
 const box=document.createElement('aside');box.id='hw-analytics-consent';box.className='hw-analytics-consent';box.setAttribute('aria-label',copy[0]);
 const title=document.createElement('strong');title.textContent=copy[0];
 const body=document.createElement('p');body.textContent=copy[1];
 const actions=document.createElement('div');
 for(const [value,label] of [['yes',copy[2]],['no',copy[3]]]){const button=document.createElement('button');button.type='button';button.textContent=label;button.className=value==='yes'?'hw-analytics-allow':'hw-analytics-decline';button.onclick=()=>{save(value);box.remove();if(value==='yes')load()};actions.append(button)}
 box.append(title,body,actions);document.body.append(box);
}
if(stored()==='yes')load();else if(stored()!=='no')prompt();
const privacy=document.querySelector('.hw-privacy');if(privacy){const button=document.createElement('button');button.type='button';button.className='hw-analytics-reset';button.textContent=copy[4];button.onclick=()=>{save('');if(window.__huyawoGa4Loaded){location.reload();return}prompt()};privacy.append(button)}
})();
