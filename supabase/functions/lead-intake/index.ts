/**
 * Public Huyawo Solutions lead ingestion endpoint; Supabase Edge Function.
 * Do not log raw emails, request bodies, Turnstile tokens, IPs, or secrets.
 * Deploy with verify_jwt=false: this endpoint uses bot checks, rate limits and origin verification,
 * not user JWT authentication. Requests have no direct privileges on the leads table.
 */
import { createClient } from 'npm:@supabase/supabase-js@2';

const allowedOrigins = new Set(['https://antoniovfranco.com', 'https://www.antoniovfranco.com']);
const allowedHostnames = new Set(['antoniovfranco.com', 'www.antoniovfranco.com']);
const jsonHeaders = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer' };
const sources = new Set(['bottom_bar', 'assessment', 'hero', 'contact']);
const topics = new Set(['general', 'quantization', 'distillation', 'finetuning', 'agents', 'benchmarks']);
const locales = new Set(['en','pt','es','zh']);

type Payload = Record<string, unknown>;
const env = (name: string) => Deno.env.get(name)?.trim() ?? '';

function response(status: number, origin: string, body: Record<string, string>) {
  return new Response(status===204 ? null : JSON.stringify(body), {status, headers: {...jsonHeaders,
    'access-control-allow-origin': origin,
    'access-control-allow-methods': 'POST, OPTIONS',
    'access-control-allow-headers': 'content-type',
    'access-control-max-age': '3600',
    'vary': 'Origin',
  }});
}

async function fingerprint(ip: string, secret: string): Promise<string> {
  const key = await crypto.subtle.importKey('raw',new TextEncoder().encode(secret),{name:'HMAC',hash:'SHA-256'},false,['sign']);
  const signed=await crypto.subtle.sign('HMAC',key,new TextEncoder().encode(ip));
  return [...new Uint8Array(signed)].map(b=>b.toString(16).padStart(2,'0')).join('');
}

async function verifyTurnstile(token:string, origin:string):Promise<boolean> {
  const secret=env('TURNSTILE_SECRET_KEY');
  if(!secret || token.length>2048 || token.length<5)return false;
  const payload = new URLSearchParams({secret, response:token});
  let result:Response;
  try {result=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{
    method:'POST',headers:{'content-type':'application/x-www-form-urlencoded'},body:payload,signal:AbortSignal.timeout(8000),
  });}catch{return false;}
  if(!result.ok)return false;
  try {const check=await result.json(); return check?.success===true && allowedHostnames.has(String(check?.hostname||'')) && new URL(origin).hostname===check.hostname;}
  catch{return false;}
}

async function notifyOwner(email:string,source:string,topic:string):Promise<void>{
  // Optional and disabled until all three secrets are supplied by Hermes.
  const key=env('RESEND_API_KEY'),to=env('LEAD_NOTIFICATION_TO'),from=env('LEAD_NOTIFICATION_FROM');
  if(!key || !to || !from)return;
  try{
    const result=await fetch('https://api.resend.com/emails',{
      method:'POST',headers:{authorization:`Bearer ${key}`,'content-type':'application/json'},
      body:JSON.stringify({from,to:[to],subject:'New Huyawo Solutions contact request',text:`New lead captured.\nContact: ${email}\nSource: ${source}\nTopic: ${topic}\nReply manually after checking the request.`}),
      signal:AbortSignal.timeout(9000),
    });
    if(!result.ok)console.error('Huyawo lead notification failed with status',result.status);
  }catch{console.error('Huyawo lead notification unavailable');}
}

// Private contact delivery: destination and credentials are server-side secrets only.
async function deliverContact(email:string,name:string,subject:string,message:string):Promise<boolean>{
 const key=env('RESEND_API_KEY'),to=env('LEAD_NOTIFICATION_TO'),from=env('LEAD_NOTIFICATION_FROM');
 if(!key||!to||!from)return false;
 try{
  const result=await fetch('https://api.resend.com/emails',{method:'POST',headers:{authorization:`Bearer ${key}`,'content-type':'application/json'},body:JSON.stringify({from,to:[to],reply_to:email,subject:`Huyawo contact: ${subject}`,text:`Name: ${name}\nEmail: ${email}\nTopic: ${subject}\n\n${message}`}),signal:AbortSignal.timeout(9000)});
  if(!result.ok)console.error('Huyawo contact mail failed with status',result.status);
  return result.ok;
 }catch{console.error('Huyawo contact mail unavailable');return false;}
}

Deno.serve(async (req:Request) => {
  const origin=req.headers.get('origin') ?? '';
  // Missing/forged Origin must not be the only gate: Turnstile and rate limiting are mandatory too.
  if(!allowedOrigins.has(origin))return new Response('Forbidden',{status:403,headers:jsonHeaders});
  if(req.method==='OPTIONS')return response(204,origin,{});
  if(req.method!=='POST')return response(405,origin,{ok:'false'});
  if(!req.headers.get('content-type')?.toLowerCase().startsWith('application/json'))return response(415,origin,{ok:'false'});
  if(Number(req.headers.get('content-length')||'0')>8192)return response(413,origin,{ok:'false'});

  const project=env('SUPABASE_URL');
  let secret=env('SUPABASE_SECRET_KEY') || env('SUPABASE_SERVICE_ROLE_KEY');
  if(!secret){try{secret=JSON.parse(env('SUPABASE_SECRET_KEYS')||'{}').default||'';}catch{/* fail closed */}}
  const pepper=env('LEAD_RATE_LIMIT_PEPPER');
  if(!project||!secret||!pepper||!env('TURNSTILE_SECRET_KEY'))return response(503,origin,{ok:'false'});

  let payload:Payload;
  try {const raw=await req.text();if(raw.length>8192)return response(413,origin,{ok:'false'});payload=JSON.parse(raw);if(!payload||Array.isArray(payload)||typeof payload!=='object')throw Error('invalid');}
  catch{return response(400,origin,{ok:'false'});}
  const rawEmail=payload.email,rawToken=payload.turnstileToken;
  if(typeof rawEmail!=='string'||typeof rawToken!=='string'||payload.consent!==true || !sources.has(String(payload.source)) || !topics.has(String(payload.topic)) || !locales.has(String(payload.locale)))return response(400,origin,{ok:'false'});
  const email=rawEmail.trim().toLowerCase();
  if(email.length<3||email.length>254||/[\r\n\u0000-\u001f]/.test(email)|| !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))return response(400,origin,{ok:'false'});

  // This header is used for defense-in-depth rate limiting; it is not an authentication factor.
  // Only the hosting provider may be trusted to populate its forwarded client IP headers.
  const ipHeader=req.headers.get('x-forwarded-for')??req.headers.get('x-real-ip')??'';
  const ip=ipHeader.split(',')[0]?.trim()||'unknown';
  const ipHash=await fingerprint(ip,pepper);
  const client=createClient(project,secret,{auth:{autoRefreshToken:false,persistSession:false},global:{headers:{'x-application-name':'huyawo-lead-intake'}}});
  try{
    const {data:allowed,error:rateError}=await client.rpc('huyawo_claim_lead_attempt',{p_fingerprint:ipHash,p_max_attempts:5});
    if(rateError)return response(503,origin,{ok:'false'});
    if(allowed!==true)return response(429,origin,{ok:'false'});
    if(!await verifyTurnstile(rawToken,origin))return response(400,origin,{ok:'false'});
    if(payload.source==='contact'){
      const name=payload.name,subject=payload.subject,message=payload.message;
      if(typeof name!=='string'||typeof subject!=='string'||typeof message!=='string'||name.trim().length<1||name.length>120||message.trim().length<1||message.length>4000||!['AI engineering','Research collaboration','Other'].includes(subject)||/[\u0000-\u001f]/.test(name)||/[\u0000-\u001f]/.test(subject))return response(400,origin,{ok:'false'});
      if(!await deliverContact(email,name.trim(),subject,message.trim()))return response(503,origin,{ok:'false'});
      const {error:contactSaveError}=await client.from('huyawo_contact_messages').insert({email,name:name.trim(),subject,message:message.trim(),locale:payload.locale,consent_at:new Date().toISOString()});
      if(contactSaveError)console.error('Contact message archive failed without logging personal data');
      return response(200,origin,{ok:'true'});
    }
    // Upsert returns no lead rows to the public caller; DB SELECT remains impossible for anon.
    const {error:saveError}=await client.from('huyawo_leads').upsert({email,source:payload.source,topic:payload.topic,locale:payload.locale,consent_at:new Date().toISOString(),updated_at:new Date().toISOString()},{onConflict:'email',ignoreDuplicates:false});
    if(saveError){console.error('Huyawo lead write failed; no personal data logged');return response(503,origin,{ok:'false'});}
    await notifyOwner(email,String(payload.source),String(payload.topic));
    return response(200,origin,{ok:'true'});
  }catch{console.error('Huyawo lead request failed without a complete response');return response(503,origin,{ok:'false'});}
});
