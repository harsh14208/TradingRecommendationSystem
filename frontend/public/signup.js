let selectedPlan = 'basic';

// Pre-select plan from URL param
const params  = new URLSearchParams(window.location.search);
const urlPlan = params.get('plan');

// Pass ?ref= + ?plan= through to OAuth providers
function googleSignup(e) {
  e.preventDefault();
  if (typeof trackClick === 'function') trackClick('oauth_google', { page: 'signup', plan: selectedPlan });
  const ref = params.get('ref');
  window.location.href = '/api/auth/google' + (ref ? `?ref=${encodeURIComponent(ref)}` : '');
}
if (urlPlan && ['free','basic','pro'].includes(urlPlan)) {
  selectedPlan = urlPlan;
  document.querySelectorAll('.plan-card').forEach(c => c.classList.remove('selected','selected-pro'));
  const card = document.querySelector(`[data-plan="${urlPlan}"]`);
  if (card) card.classList.add(urlPlan === 'pro' ? 'selected-pro' : 'selected');
  updateContinueBtn();
}

function selectPlan(plan) {
  selectedPlan = plan;
  if (typeof trackClick === 'function') trackClick('signup_select_plan', { plan });
  document.querySelectorAll('.plan-card').forEach(c => c.classList.remove('selected','selected-pro'));
  const card = document.querySelector(`[data-plan="${plan}"]`);
  if (card) card.classList.add(plan === 'pro' ? 'selected-pro' : 'selected');
  updateContinueBtn();
}

function updateContinueBtn() {
  const btn = document.getElementById('continue-btn');
  const names = { free:'Free', basic:'Basic', pro:'Pro' };
  btn.textContent = selectedPlan === 'free' ? 'Continue with Free →' : `Continue with ${names[selectedPlan]} →`;
  btn.className = 'submit-btn';
  if (selectedPlan === 'free') btn.classList.add('free');
  else if (selectedPlan === 'pro') btn.classList.add('pro-paid');
  else btn.classList.add('paid');
}

function goToAccount() {
  // Update step indicators
  document.getElementById('num-1').classList.remove('active');
  document.getElementById('num-1').classList.add('done');
  document.getElementById('num-1').textContent = '✓';
  document.getElementById('lbl-1').classList.remove('active');
  document.getElementById('conn-1').classList.add('done');
  document.getElementById('num-2').classList.add('active');
  document.getElementById('lbl-2').classList.add('active');

  // Update plan summary
  const prices = { free:'Free', basic:'$19/mo', pro:'$49/mo' };
  const names  = { free:'Free', basic:'Basic', pro:'Pro' };
  document.getElementById('summary-name').textContent = names[selectedPlan];
  document.getElementById('summary-price').textContent = prices[selectedPlan];
  if (selectedPlan === 'free') document.getElementById('plan-summary').querySelector('div div:last-child').textContent = 'No charge';

  // Update submit button
  const sbtn = document.getElementById('submit-btn');
  if (selectedPlan === 'free') { sbtn.className = 'submit-btn free'; document.getElementById('btn-text').textContent = 'Create free account'; }
  else if (selectedPlan === 'pro') { sbtn.className = 'submit-btn pro-paid'; document.getElementById('btn-text').textContent = 'Create account & pay with Stripe →'; }
  else { sbtn.className = 'submit-btn paid'; document.getElementById('btn-text').textContent = 'Create account & pay with Stripe →'; }

  document.getElementById('step-plan').style.display = 'none';
  document.getElementById('step-account').style.display = 'flex';
  window.scrollTo({top:0,behavior:'smooth'});
}

function goToPlan() {
  document.getElementById('num-1').classList.add('active');
  document.getElementById('num-1').classList.remove('done');
  document.getElementById('num-1').textContent = '1';
  document.getElementById('lbl-1').classList.add('active');
  document.getElementById('conn-1').classList.remove('done');
  document.getElementById('num-2').classList.remove('active');
  document.getElementById('lbl-2').classList.remove('active');
  document.getElementById('step-account').style.display = 'none';
  document.getElementById('step-plan').style.display = 'flex';
  window.scrollTo({top:0,behavior:'smooth'});
}

document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  if (typeof track === 'function') track('signup_submit', { plan: selectedPlan });
  const btn = document.getElementById('submit-btn');
  const err = document.getElementById('error');
  err.style.display = 'none';

  const email    = suEmail.value.trim();
  const password = suPassword.value;
  const name     = document.getElementById('name').value.trim();

  clearInlineError(suEmail);
  clearInlineError(suPassword);

  let invalid = false;
  if (!email) { showInlineError(suEmail, 'Email is required.'); invalid = true; }
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { showInlineError(suEmail, 'Please enter a valid email address.'); invalid = true; }
  if (!password) { showInlineError(suPassword, 'Password is required.'); invalid = true; }
  else if (password.length < 8) { showInlineError(suPassword, 'Password must be at least 8 characters.'); invalid = true; }
  if (invalid) return;

  btn.disabled = true;
  document.getElementById('btn-text').textContent = 'Creating account…';

  try {
    // 1. Register account
    const res  = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password, full_name: name }),
    });
    const data = await res.json();
    if (!res.ok) {
      err.textContent = data.detail || 'Could not create account. Try a different email.';
      err.style.display = 'block';
      btn.disabled = false;
      document.getElementById('btn-text').textContent = selectedPlan === 'free' ? 'Create free account' : 'Create account & pay with Stripe →';
      return;
    }

    // Advance step indicator
    document.getElementById('num-2').classList.remove('active');
    document.getElementById('num-2').classList.add('done');
    document.getElementById('num-2').textContent = '✓';
    document.getElementById('conn-2').classList.add('done');
    document.getElementById('num-3').classList.add('active');
    document.getElementById('lbl-3').classList.add('active');

    // Owner auto-verified → got access_token → go straight in
    if (data.access_token) {
      // access_token used inline only — not persisted; refresh cookie maintains session
      if (selectedPlan !== 'free') {
        document.getElementById('btn-text').textContent = 'Redirecting to Stripe…';
        const checkoutRes = await fetch(`/api/billing/checkout/${selectedPlan}`, {
          method: 'POST',
          headers: { 'Content-Type':'application/json', Authorization:`Bearer ${data.access_token}` },
          credentials: 'include',
        });
        const checkout = await checkoutRes.json();
        if (checkout.checkout_url) { window.location.href = checkout.checkout_url; return; }
      }
      setTimeout(() => window.location.replace('/app'), 600);
      return;
    }

    // Normal flow: show "Check your email" screen
    const signedUpEmail = data.email || email;
    showCheckEmail(signedUpEmail, selectedPlan);

  } catch {
    err.textContent = 'Network error — is the server running?';
    err.style.display = 'block';
    btn.disabled = false;
    document.getElementById('btn-text').textContent = selectedPlan === 'free' ? 'Create free account' : 'Create account & pay with Stripe →';
  }
});

function showCheckEmail(email, plan) {
  document.getElementById('step-plan').style.display = 'none';
  document.getElementById('step-account').style.display = 'none';

  const wrap = document.createElement('div');
  wrap.style.cssText = 'display:flex;flex-direction:column;align-items:center;max-width:460px;width:100%;text-align:center';
  const icon = document.createElement('div');
  icon.textContent = '✉️';
  icon.style.cssText = 'font-size:56px;margin-bottom:20px';
  const heading = document.createElement('h2');
  heading.textContent = 'Check your email';
  heading.style.cssText = 'font-size:24px;font-weight:800;letter-spacing:-0.03em;margin-bottom:10px';
  const sent = document.createElement('p');
  sent.style.cssText = 'font-size:14px;color:var(--dim);line-height:1.7;margin-bottom:6px';
  sent.appendChild(document.createTextNode('We sent a verification link to'));
  sent.appendChild(document.createElement('br'));
  const emailEl = document.createElement('strong');
  emailEl.textContent = email;
  emailEl.style.color = 'var(--text)';
  sent.appendChild(emailEl);
  const instructions = document.createElement('p');
  instructions.textContent = 'Click the link in the email to activate your account. The link expires in 24 hours.';
  instructions.style.cssText = 'font-size:13px;color:var(--faint);margin-bottom:28px';
  const resendBox = document.createElement('div');
  resendBox.style.cssText = 'background:var(--bg1);border:1px solid var(--line);border-radius:12px;padding:20px;width:100%;margin-bottom:20px';
  const resendHint = document.createElement('div');
  resendHint.textContent = "Didn't receive it? Check your spam folder, or";
  resendHint.style.cssText = 'font-size:12px;color:var(--dim);margin-bottom:14px';
  const resendBtn = document.createElement('button');
  resendBtn.id = 'resend-btn';
  resendBtn.type = 'button';
  resendBtn.textContent = 'Resend verification email';
  resendBtn.style.cssText = 'width:100%;padding:11px;background:var(--bg2);border:1px solid var(--line2);border-radius:8px;color:var(--text);font-size:13px;font-weight:600;cursor:pointer;font-family:var(--sans)';
  resendBtn.addEventListener('click', () => resendVerification(email));
  const resendMsg = document.createElement('div');
  resendMsg.id = 'resend-msg';
  resendMsg.style.cssText = 'font-size:12px;color:var(--up);margin-top:10px;display:none';
  resendBox.append(resendHint, resendBtn, resendMsg);
  wrap.append(icon, heading, sent, instructions, resendBox);
  if (plan !== 'free') {
    const upgrade = document.createElement('p');
    const planLabel = plan.charAt(0).toUpperCase() + plan.slice(1);
    upgrade.textContent = `After verifying your email, you'll be able to upgrade to ${planLabel}.`;
    upgrade.style.cssText = 'font-size:12px;color:var(--faint);margin-bottom:16px';
    wrap.appendChild(upgrade);
  }
  const signIn = document.createElement('a');
  signIn.href = '/login';
  signIn.textContent = 'Already verified? Sign in →';
  signIn.style.cssText = 'font-size:14px;color:var(--up);font-weight:600;text-decoration:none';
  const disclaimer = document.createElement('p');
  disclaimer.textContent = '⚠️ Not financial advice · For informational purposes only';
  disclaimer.style.cssText = 'font-size:11px;color:var(--faint);margin-top:20px';
  wrap.append(signIn, disclaimer);
  document.body.appendChild(wrap);
}

// ── Inline validation helpers ────────────────────────────────────────────────
const suEmail = document.getElementById('email');
const suPassword = document.getElementById('password');

function showInlineError(input, msg) {
  input.style.borderColor = 'var(--down)';
  let tip = input.parentNode.querySelector('.inline-error');
  if (!tip) {
    tip = document.createElement('div');
    tip.className = 'inline-error';
    tip.style.cssText = 'font-size:12px;color:var(--down);margin-top:-8px;margin-bottom:12px';
    input.parentNode.appendChild(tip);
  }
  tip.textContent = msg;
}
function clearInlineError(input) {
  input.style.borderColor = '';
  const tip = input.parentNode.querySelector('.inline-error');
  if (tip) tip.remove();
}

suEmail?.addEventListener('blur', () => {
  const v = suEmail.value.trim();
  if (v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) showInlineError(suEmail, 'Please enter a valid email address.');
  else clearInlineError(suEmail);
});
suEmail?.addEventListener('input', () => clearInlineError(suEmail));
suPassword?.addEventListener('blur', () => {
  const v = suPassword.value;
  if (v && v.length < 8) showInlineError(suPassword, 'Password must be at least 8 characters.');
  else clearInlineError(suPassword);
});
suPassword?.addEventListener('input', () => {
  if (suPassword.value.length >= 8) clearInlineError(suPassword);
});

// Wire up event listeners (replaces onclick= attributes blocked by CSP)
document.querySelectorAll('.plan-card').forEach(card => {
  card.addEventListener('click', () => selectPlan(card.dataset.plan));
});
document.getElementById('continue-btn')?.addEventListener('click', goToAccount);
document.getElementById('change-plan-btn')?.addEventListener('click', goToPlan);
document.getElementById('google-btn')?.addEventListener('click', googleSignup);

async function resendVerification(email) {
  const btn = document.getElementById('resend-btn');
  const msg = document.getElementById('resend-msg');
  btn.disabled = true;
  btn.textContent = 'Sending…';
  try {
    const res = await fetch('/api/auth/resend-verification', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
    const data = await res.json();
    msg.textContent = data.message || 'Sent!';
    msg.style.display = 'block';
    btn.textContent = '✓ Sent — check your inbox';
    setTimeout(() => { btn.disabled = false; btn.textContent = 'Resend verification email'; }, 30000);
  } catch {
    btn.disabled = false;
    btn.textContent = 'Resend verification email';
    msg.textContent = 'Network error — try again.';
    msg.style.color = 'var(--down)';
    msg.style.display = 'block';
  }
}
