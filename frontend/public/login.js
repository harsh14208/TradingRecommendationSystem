const params = new URLSearchParams(window.location.search);
const next   = params.get('next') || '/app';

// ── Server connectivity indicator ────────────────────────────────────────────
const statusDot  = document.getElementById('server-dot');
const statusText = document.getElementById('server-text');
let _serverUp = false;
let _checkTimer = null;

function _setServerStatus(up) {
  _serverUp = up;
  if (!statusDot || !statusText) return;
  statusDot.style.background  = up ? 'var(--up)' : 'var(--down)';
  statusDot.style.boxShadow   = up ? '0 0 5px var(--up)' : 'none';
  statusText.textContent       = up ? 'Server connected' : 'Server offline';
  statusText.style.color       = up ? 'var(--dim)' : '#fca5a5';
  document.getElementById('submit-btn').disabled = !up;
  const socialBtns = document.querySelectorAll('.social-btn');
  socialBtns.forEach(b => b.style.pointerEvents = up ? '' : 'none');
  socialBtns.forEach(b => b.style.opacity = up ? '' : '0.4');
}

async function _checkServer() {
  try {
    const r = await fetch('/api/health', { signal: AbortSignal.timeout(4000) });
    _setServerStatus(r.ok);
    if (!r.ok) _scheduleRetry();
  } catch {
    _setServerStatus(false);
    _scheduleRetry();
  }
}

function _scheduleRetry() {
  clearTimeout(_checkTimer);
  _checkTimer = setTimeout(_checkServer, 5000);
}

// Poll immediately on load, then every 10 s when server is up
_checkServer();
setInterval(() => { if (_serverUp) _checkServer(); }, 10000);

// ── OAuth error messages ─────────────────────────────────────────────────────
const oauthError = params.get('error');
if (oauthError) {
  const errMessages = {};
  const msg = errMessages[oauthError] || 'Sign-in failed. Please try again.';
  const box = document.getElementById('error');
  if (box) { box.textContent = msg; box.style.display = 'block'; }
  window.history.replaceState({}, '', window.location.pathname + (params.get('next') ? '?next=' + params.get('next') : ''));
}

// ── Pass ?ref= through OAuth buttons ────────────────────────────────────────
const ref = params.get('ref');
if (ref) {
  document.getElementById('google-btn')?.setAttribute('href', `/api/auth/google?ref=${encodeURIComponent(ref)}`);
}

// ── Load live stats for left panel ──────────────────────────────────────────
fetch('/api/public/track-record').then(r => r.json()).then(d => {
  if (d.overall?.win_rate) document.getElementById('wr-val').textContent = d.overall.win_rate.toFixed(1) + '%';
  if (d.total_signals)    document.getElementById('sig-val').textContent = d.total_signals;
}).catch(()=>{});

// ── If already logged in, redirect via refresh cookie ───────────────────────
fetch('/api/auth/refresh-cookie', { method: 'POST', credentials: 'include' })
  .then(r => r.ok ? r.json() : null)
  .then(d => { if (d?.access_token) window.location.replace(next); })
  .catch(() => {});

// ── Login form submit ────────────────────────────────────────────────────────
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('submit-btn');
  const err = document.getElementById('error');
  err.style.display = 'none';
  btn.disabled = true;
  btn.textContent = 'Signing in…';

  const email    = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include',
      signal: AbortSignal.timeout(10000),
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = data.detail;
      const code   = typeof detail === 'object' ? detail?.code : null;
      const msg    = typeof detail === 'object' ? detail?.message : (detail || 'Invalid email or password.');
      if (code === 'email_unverified') {
        err.textContent = '';
        err.appendChild(document.createTextNode(msg));
        err.appendChild(document.createElement('br'));
        err.appendChild(document.createElement('br'));
        const resendBtn = document.createElement('button');
        resendBtn.type = 'button';
        resendBtn.id = 'resend-btn';
        resendBtn.textContent = 'Resend verification email';
        resendBtn.style.cssText = 'background:none;border:1px solid rgba(239,68,68,.4);color:#fca5a5;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:12px;margin-top:2px;font-family:inherit';
        resendBtn.addEventListener('click', () => resendVerification(email));
        const resendMsg = document.createElement('span');
        resendMsg.id = 'resend-msg';
        resendMsg.style.cssText = 'display:none;font-size:12px;color:#10b981;margin-left:8px';
        err.appendChild(resendBtn);
        err.appendChild(resendMsg);
      } else {
        err.textContent = msg;
      }
      err.style.display = 'block';
      btn.disabled = false;
      btn.textContent = 'Sign In';
      return;
    }
    // access_token not persisted — the HTTP-only refresh cookie maintains the session
    window.location.replace(next);
  } catch (ex) {
    _setServerStatus(false);
    _scheduleRetry();
    err.textContent = 'Unable to reach the server. Please try again in a moment.';
    err.style.display = 'block';
    btn.disabled = false;
    btn.textContent = 'Sign In';
  }
});

async function resendVerification(email) {
  const btn = document.getElementById('resend-btn');
  const msg = document.getElementById('resend-msg');
  if (!btn) return;
  btn.disabled = true;
  btn.textContent = 'Sending…';
  try {
    const res  = await fetch('/api/auth/resend-verification', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    const data = await res.json();
    if (msg) { msg.textContent = data.message || 'Sent!'; msg.style.display = 'inline'; }
    btn.textContent = '✓ Sent';
    setTimeout(() => { if (btn) { btn.disabled = false; btn.textContent = 'Resend verification email'; } }, 30000);
  } catch {
    if (btn) { btn.disabled = false; btn.textContent = 'Resend verification email'; }
  }
}
