"""
Email service — sends transactional emails via SMTP (aiosmtplib).
Falls back to console logging if SMTP is not configured.
"""
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger("signal.trade.email")


def _settings():
    from config import get_settings
    return get_settings()


async def _send(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"]      = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password,
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


_BASE_STYLE = """
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0d1117;color:#e6edf3;margin:0;padding:0}
.wrap{max-width:560px;margin:40px auto;padding:32px;background:#161b22;border-radius:12px;border:1px solid #30363d}
h1{font-size:22px;font-weight:700;margin:0 0 8px;color:#fff}
p{font-size:14px;line-height:1.7;color:#8b949e;margin:0 0 16px}
.btn{display:inline-block;padding:12px 24px;background:#10b981;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px}
.pill{display:inline-block;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:600;background:#1f6feb;color:#fff}
.pill.pro{background:#7c3aed}
.footer{margin-top:32px;padding-top:16px;border-top:1px solid #30363d;font-size:11px;color:#484f58;text-align:center}
"""


async def send_welcome(to: str, full_name: str):
    name = full_name or to.split("@")[0]
    html = f"""
<html><head><style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
  <h1>Welcome to Signal.Trade 🎉</h1>
  <p>Hey {name}, your account is live.</p>
  <p>You're on the <strong>Free plan</strong> right now. You can view signals in the dashboard. To enable Telegram delivery and advanced features, upgrade to Basic or Pro.</p>
  <p><a class="btn" href="{_settings().app_url}">Open Signal.Trade →</a></p>
  <p style="font-size:12px;color:#484f58">⚠️ Signal.Trade is not financial advice. All signals are for informational purposes only.</p>
  <div class="footer">Signal.Trade · Not financial advice · You received this because you created an account.</div>
</div>
</body></html>"""
    plain = f"Welcome to Signal.Trade, {name}!\n\nYou're on the Free plan. Upgrade to unlock Telegram signals and advanced features.\n\nNot financial advice."
    await _send(to, "Welcome to Signal.Trade", html, plain)


async def send_subscription_confirmed(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "pill pro" if tier == "pro" else "pill"
    html = f"""
<html><head><style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
  <h1>Subscription confirmed ✅</h1>
  <p>Hey {name}, you're now on the <span class="{pill_class}">{tier_cap}</span> plan.</p>
  <p>Your subscription renews on <strong>{period_end}</strong>. You can manage or cancel anytime from Account Settings.</p>
  <p><a class="btn" href="{_settings().app_url}">Open Signal.Trade →</a></p>
  <p style="font-size:12px;color:#484f58">⚠️ Not financial advice. Past performance does not guarantee future results.</p>
  <div class="footer">Signal.Trade · Manage subscription in Account Settings.</div>
</div>
</body></html>"""
    plain = f"Subscription confirmed!\n\nYou're now on the {tier_cap} plan, renewing on {period_end}.\n\nNot financial advice."
    await _send(to, f"Signal.Trade — {tier_cap} plan activated", html, plain)


async def send_payment_failed(to: str, full_name: str):
    name = full_name or to.split("@")[0]
    html = f"""
<html><head><style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
  <h1>Payment failed ⚠️</h1>
  <p>Hey {name}, we couldn't process your subscription payment.</p>
  <p>Your access will remain active for a short grace period. Please update your payment method to avoid interruption.</p>
  <p><a class="btn" href="{_settings().app_url}/api/billing/portal">Update Payment Method →</a></p>
  <div class="footer">Signal.Trade · Manage billing in Account Settings.</div>
</div>
</body></html>"""
    plain = f"Hey {name}, we couldn't process your Signal.Trade payment. Please update your payment method."
    await _send(to, "Signal.Trade — Payment failed", html, plain)


async def send_subscription_canceled(to: str, full_name: str, period_end: str):
    name = full_name or to.split("@")[0]
    html = f"""
<html><head><style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
  <h1>Subscription canceled</h1>
  <p>Hey {name}, your subscription has been canceled. You'll keep Pro/Basic access until <strong>{period_end}</strong>, then revert to Free.</p>
  <p>You can resubscribe anytime from Account Settings.</p>
  <div class="footer">Signal.Trade · We're sorry to see you go.</div>
</div>
</body></html>"""
    plain = f"Hey {name}, your Signal.Trade subscription is canceled. Access continues until {period_end}."
    await _send(to, "Signal.Trade — Subscription canceled", html, plain)


async def send_weekly_digest(
    to: str,
    week_ending: str,
    sent: int,
    win_rate: int | None,
    wins: int,
    resolved: int,
    avg_ret: float | None,
    best_ticker: str | None,
    best_ret: float | None,
    worst_ticker: str | None,
    worst_ret: float | None,
    spy_ret: float | None = None,
):
    wr_row = f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>" if win_rate is not None else ""
    spy_str = f" <span style=\"color:#6b7280;font-size:12px\">(vs SPY {spy_ret:+.2f}%)</span>" if spy_ret is not None else ""
    ar_row = f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    best_row = f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    worst_row = f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>" if worst_ticker else ""
    no_data = "<p>No resolved outcomes yet — check back next week.</p>" if win_rate is None else ""
    html = f"""
<html><head><style>{_BASE_STYLE}
table{{width:100%;border-collapse:collapse;margin:16px 0}}
td{{padding:10px 12px;border-bottom:1px solid #e8ebee;font-size:14px;color:#374151}}
td:first-child{{color:#6b7280;width:40%}}
</style></head><body>
<div class="wrap">
  <h1>📊 Weekly Signal Digest</h1>
  <p style="color:#6b7280">Week ending {week_ending}</p>
  <table>
    <tr><td>Signals sent</td><td><strong>{sent}</strong></td></tr>
    {wr_row}{ar_row}{best_row}{worst_row}
  </table>
  {no_data}
  <p><a class="btn" href="https://signal.trade/track-record">View Full Track Record →</a></p>
  <div class="footer">Signal.Trade · <a href="{{{{unsubscribe}}}}">Unsubscribe</a></div>
</div>
</body></html>"""
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n",
                   f"Signals sent: {sent}"]
    if win_rate is not None: plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else ""))
    if best_ticker:          plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:         plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def send_verification_email(to: str, full_name: str, verify_link: str):
    name = full_name or to.split("@")[0]
    html = f"""
<html><head><style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
  <h1>Verify your email ✉️</h1>
  <p>Hey {name}, thanks for signing up! Click the button below to verify your email address and activate your Signal.Trade account.</p>
  <p><a class="btn" href="{verify_link}">Verify Email →</a></p>
  <p style="font-size:12px;color:#484f58">This link expires in 24 hours. If you didn't create an account, ignore this email.</p>
  <p style="font-size:11px;color:#484f58;word-break:break-all">Or copy this link: {verify_link}</p>
  <div class="footer">Signal.Trade · Not financial advice · You received this because you created an account.</div>
</div>
</body></html>"""
    plain = f"Hey {name},\n\nVerify your Signal.Trade email:\n{verify_link}\n\nExpires in 24 hours."
    await _send(to, "Signal.Trade — Verify your email", html, plain)


async def send_password_reset(to: str, reset_link: str):
    html = f"""
<html><head><style>{_BASE_STYLE}</style></head><body>
<div class="wrap">
  <h1>Reset your password</h1>
  <p>Someone requested a password reset for this account. If that wasn't you, ignore this email.</p>
  <p><a class="btn" href="{reset_link}">Reset Password →</a></p>
  <p style="font-size:12px;color:#484f58">This link expires in 1 hour.</p>
  <div class="footer">Signal.Trade</div>
</div>
</body></html>"""
    plain = f"Reset your Signal.Trade password: {reset_link}\n\nExpires in 1 hour."
    await _send(to, "Signal.Trade — Password reset", html, plain)
