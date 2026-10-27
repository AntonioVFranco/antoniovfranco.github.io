/** PUBLIC settings only. Hermes fills these after deploying the backend.
 * NEVER put Supabase secret/service_role keys, Turnstile secret, API tokens or private e-mail lists here.
 */
window.HUYAWO_LEADS = Object.freeze({
  functionUrl: "https://mwrfvfbxdrkvbliyhkot.supabase.co/functions/v1/lead-intake",
  turnstileSiteKey: "0x4AAAAAAFoogOI_h7lQH_0L" // Cloudflare PUBLIC widget site key, not the private secret
});