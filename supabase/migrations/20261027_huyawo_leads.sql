-- Huyawo Solutions lead intake; no client-side DB access.
-- Apply ONLY to a verified Supabase project. Test grants/RLS before going live.
create extension if not exists pgcrypto;

create table if not exists public.huyawo_leads (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  source text not null check (source in ('bottom_bar', 'assessment', 'hero', 'contact')),
  topic text not null check (topic in ('general','quantization','distillation','finetuning','agents','benchmarks')),
  locale text not null check (locale in ('en','pt','es','zh')),
  consent_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint leads_email_size check (length(email) between 3 and 254)
);

create table if not exists public.huyawo_lead_rate_limits (
  fingerprint text not null,
  window_bucket bigint not null,
  attempts integer not null default 0,
  last_attempt_at timestamptz not null default now(),
  primary key (fingerprint, window_bucket),
  constraint fingerprint_length check (length(fingerprint)=64),
  constraint attempts_valid check (attempts >= 0)
);

alter table public.huyawo_leads enable row level security;
alter table public.huyawo_lead_rate_limits enable row level security;
-- RESTRICTIVE: no RLS policies for anon/authenticated; table cannot be read or written publicly.
revoke all on table public.huyawo_leads from public, anon, authenticated;
revoke all on table public.huyawo_lead_rate_limits from public, anon, authenticated;
grant select, insert, update, delete on table public.huyawo_leads to service_role;
grant select, insert, update, delete on table public.huyawo_lead_rate_limits to service_role;

create or replace function public.huyawo_claim_lead_attempt(p_fingerprint text, p_max_attempts integer default 5)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  current_attempts integer;
  current_bucket bigint;
begin
  if p_fingerprint !~ '^[a-f0-9]{64}$' or p_max_attempts < 1 or p_max_attempts > 10 then
    return false;
  end if;
  current_bucket := floor(extract(epoch from now()) / 900)::bigint;
  insert into public.huyawo_lead_rate_limits (fingerprint, window_bucket, attempts)
    values (p_fingerprint, current_bucket, 1)
  on conflict (fingerprint, window_bucket)
    do update set attempts = public.huyawo_lead_rate_limits.attempts + 1,
                  last_attempt_at = now()
  returning attempts into current_attempts;
  return current_attempts <= p_max_attempts;
end;
$$;
revoke all on function public.huyawo_claim_lead_attempt(text, integer) from public, anon, authenticated;
grant execute on function public.huyawo_claim_lead_attempt(text, integer) to service_role;

-- Daily cleanup should be configured separately:
-- DELETE FROM public.huyawo_lead_rate_limits WHERE last_attempt_at < now() - interval '2 days';
-- Personal-data retention must follow the approved privacy policy (e.g. periodic pruning).

-- Private contact archive. Only the Edge Function's service role can access it.
create table if not exists public.huyawo_contact_messages (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  name text not null,
  subject text not null,
  message text not null,
  locale text not null check (locale in ('en','pt','es','zh')),
  consent_at timestamptz not null,
  created_at timestamptz not null default now(),
  constraint contact_email_size check (length(email) between 3 and 254),
  constraint contact_message_size check (length(message) between 1 and 4000)
);
alter table public.huyawo_contact_messages enable row level security;
revoke all on table public.huyawo_contact_messages from public, anon, authenticated;
grant select, insert, update, delete on table public.huyawo_contact_messages to service_role;
-- Establish and implement a documented retention/deletion schedule before launch.
