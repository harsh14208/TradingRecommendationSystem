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
  statusText.style.color       = up ? 'var(--dim)' : 'var(--down)';
  // Don't block submission on server-down; let the request fail naturally with a clear error.
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

document.getElementById('google-btn')?.addEventListener('click', () => {
  if (typeof trackClick === 'function') trackClick('oauth_google', { page: 'login' });
});

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

// ── Forgot password ──────────────────────────────────────────────────────────
const forgotBtn = document.getElementById('forgot-btn');
const forgotForm = document.getElementById('forgot-form');
const forgotEmail = document.getElementById('forgot-email');
const forgotSubmit = document.getElementById('forgot-submit');
const forgotMsg = document.getElementById('forgot-msg');

forgotBtn?.addEventListener('click', () => {
  const show = !forgotForm.classList.contains('show');
  forgotForm.classList.toggle('show', show);
  forgotBtn.textContent = show ? 'Back to sign in' : 'Forgot password?';
  if (show) setTimeout(() => forgotEmail.focus(), 50);
});

forgotSubmit?.addEventListener('click', async () => {
  if (typeof track === 'function') track('forgot_password_submit');
  const email = forgotEmail.value.trim();
  if (!email || !email.includes('@')) {
    forgotMsg.textContent = 'Please enter a valid email address.';
    forgotMsg.style.color = 'var(--down)';
    forgotMsg.classList.add('show');
    return;
  }
  forgotSubmit.disabled = true;
  forgotSubmit.textContent = 'Sending…';
  try {
    const res = await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
      credentials: 'include',
      signal: AbortSignal.timeout(10000),
    });
    const data = await res.json();
    if (res.ok) {
      forgotMsg.textContent = 'If that email is registered, a reset link has been sent.';
      forgotMsg.style.color = 'var(--up)';
    } else {
      forgotMsg.textContent = data.detail || 'Could not send reset link. Please try again.';
      forgotMsg.style.color = 'var(--down)';
    }
  } catch {
    forgotMsg.textContent = 'Network error. Please try again in a moment.';
    forgotMsg.style.color = 'var(--down)';
  }
  forgotMsg.classList.add('show');
  forgotSubmit.disabled = false;
  forgotSubmit.textContent = 'Send reset link';
});

// ── Inline validation helpers ────────────────────────────────────────────────
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const errBox = document.getElementById('error');

function showInlineError(input, msg) {
  input.style.borderColor = 'var(--down)';
  let tip = input.parentNode.querySelector('.inline-error');
  if (!tip) {
    tip = document.createElement('div');
    tip.className = 'inline-error';
    tip.style.cssText = 'font-size:12px;color:var(--down);margin-top:-10px;margin-bottom:12px';
    input.parentNode.appendChild(tip);
  }
  tip.textContent = msg;
}
function clearInlineError(input) {
  input.style.borderColor = '';
  const tip = input.parentNode.querySelector('.inline-error');
  if (tip) tip.remove();
}

emailInput?.addEventListener('blur', () => {
  const v = emailInput.value.trim();
  if (v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) showInlineError(emailInput, 'Please enter a valid email address.');
  else clearInlineError(emailInput);
});
emailInput?.addEventListener('input', () => clearInlineError(emailInput));
passwordInput?.addEventListener('input', () => clearInlineError(passwordInput));

// ── Login form submit ────────────────────────────────────────────────────────
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  if (typeof track === 'function') track('login_submit');
  const btn = document.getElementById('submit-btn');
  const err = document.getElementById('error');
  err.style.display = 'none';

  const email    = emailInput.value.trim();
  const password = passwordInput.value;

  clearInlineError(emailInput);
  clearInlineError(passwordInput);

  let invalid = false;
  if (!email) { showInlineError(emailInput, 'Email is required.'); invalid = true; }
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { showInlineError(emailInput, 'Please enter a valid email address.'); invalid = true; }
  if (!password) { showInlineError(passwordInput, 'Password is required.'); invalid = true; }
  if (invalid) return;

  btn.disabled = true;
  btn.textContent = 'Signing in…';

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
        resendBtn.style.cssText = 'background:none;border:1px solid rgba(251,77,109,.4);color:var(--down);padding:6px 14px;border-radius:6px;cursor:pointer;font-size:12px;margin-top:2px;font-family:inherit';
        resendBtn.addEventListener('click', () => resendVerification(email));
        const resendMsg = document.createElement('span');
        resendMsg.id = 'resend-msg';
        resendMsg.style.cssText = 'display:none;font-size:12px;color:var(--up);margin-left:8px';
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
