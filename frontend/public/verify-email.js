// Email verification flow — external (not inline) to satisfy CSP script-src 'self'.
const token = new URLSearchParams(window.location.search).get('token');
const card    = document.getElementById('card');
const spinner = document.getElementById('spinner');
const title   = document.getElementById('title');
const message = document.getElementById('message');

async function verify() {
  if (!token) {
    showError('No verification token found. Check that you copied the full link from your email.');
    return;
  }
  try {
    const res  = await fetch(`/api/auth/verify-email?token=${encodeURIComponent(token)}`);
    const data = await res.json();

    if (res.ok && data.access_token) {
      // Success — refresh cookie is set by the server; redirect to dashboard
      showSuccess(data.user?.email || '');
      return;
    }
    // Already verified or invalid token
    const msg = (typeof data.detail === 'string' ? data.detail : data.detail?.message) || 'Verification failed.';
    if (msg.toLowerCase().includes('already verified')) {
      showAlreadyVerified();
    } else {
      showError(msg);
    }
  } catch {
    showError('Network error — please try again or request a new link.');
  }
}

function showSuccess(email) {
  spinner.style.display = 'none';
  card.replaceChildren();
  const icon = document.createElement('div');
  icon.className = 'icon';
  icon.textContent = '✅';
  const heading = document.createElement('h2');
  heading.textContent = 'Email verified!';
  const body = document.createElement('p');
  body.textContent = `Your account${email ? ' (' + email + ')' : ''} is now active. You're being redirected to the dashboard…`;
  const link = document.createElement('a');
  link.href = '/app';
  link.className = 'btn';
  link.textContent = 'Open Dashboard →';
  const disclaimer = document.createElement('p');
  disclaimer.textContent = '⚠️ Not financial advice · For informational purposes only';
  disclaimer.style.cssText = 'margin-top:14px;font-size:11px;color:var(--faint)';
  card.append(icon, heading, body, link, disclaimer);
  setTimeout(() => window.location.replace('/app'), 1800);
}

function showAlreadyVerified() {
  spinner.style.display = 'none';
  card.replaceChildren();
  const icon = document.createElement('div');
  icon.className = 'icon';
  icon.textContent = '✅';
  const heading = document.createElement('h2');
  heading.textContent = 'Already verified';
  const body = document.createElement('p');
  body.textContent = 'This email address has already been verified. Sign in to access your dashboard.';
  const link = document.createElement('a');
  link.href = '/login';
  link.className = 'btn';
  link.textContent = 'Sign in →';
  card.append(icon, heading, body, link);
}

function showError(msg) {
  spinner.style.display = 'none';
  title.textContent = 'Verification failed';
  title.classList.add('error');
  message.textContent = '';
  message.appendChild(document.createTextNode(msg));
  message.appendChild(document.createElement('br'));
  message.appendChild(document.createElement('br'));
  message.appendChild(document.createTextNode('Request a new verification link:'));

  const emailInput = document.createElement('input');
  emailInput.type = 'email';
  emailInput.placeholder = 'your@email.com';
  emailInput.id = 'resend-email';
  emailInput.style.cssText = 'width:100%;background:var(--bg2);border:1px solid var(--line);border-radius:7px;padding:11px 14px;font-size:14px;color:var(--text);outline:none;margin:12px 0 8px;font-family:var(--sans)';

  const resendBtn = document.createElement('button');
  resendBtn.textContent = 'Resend verification email';
  resendBtn.className = 'btn secondary';
  resendBtn.style.marginTop = '0';
  resendBtn.onclick = resend;

  const resendMsg = document.createElement('p');
  resendMsg.id = 'resend-msg';
  resendMsg.style.marginTop = '10px';

  const signIn = document.createElement('a');
  signIn.href = '/login';
  signIn.className = 'btn';
  signIn.textContent = 'Sign in instead →';
  signIn.style.marginTop = '12px';

  card.appendChild(emailInput);
  card.appendChild(resendBtn);
  card.appendChild(resendMsg);
  card.appendChild(signIn);
}

async function resend() {
  const emailInput = document.getElementById('resend-email');
  const resendMsg  = document.getElementById('resend-msg');
  const email = emailInput?.value?.trim();
  if (!email) { resendMsg.textContent = 'Enter your email first.'; resendMsg.style.color = 'var(--down)'; return; }
  resendMsg.textContent = 'Sending…';
  resendMsg.style.color = 'var(--dim)';
  try {
    const res  = await fetch('/api/auth/resend-verification', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    const data = await res.json();
    resendMsg.textContent = data.message || 'Sent!';
    resendMsg.style.color = 'var(--up)';
  } catch {
    resendMsg.textContent = 'Network error — try again.';
    resendMsg.style.color = 'var(--down)';
  }
}

verify();
