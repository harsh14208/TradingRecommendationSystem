#!/usr/bin/env python3
"""
Stripe product + price setup script for Signal.Trade.

Run ONCE after adding STRIPE_SECRET_KEY to backend/.env:
  cd TradingRecommendationSystem
  python3 stripe_setup.py

The script creates Basic and Pro products/prices in Stripe, then
prints the exact lines to paste into backend/.env.

Step 1 — Open Stripe Dashboard
Go to dashboard.stripe.com/test/webhooks (make sure you're in test mode).

Step 2 — Add an endpoint
Click "Add endpoint" and fill in:

Endpoint URL: http://localhost:8000/api/billing/webhook

Note: Stripe can't reach localhost directly. You'll need a tunnel. See Step 3.

Step 3 — Expose localhost with Stripe CLI (recommended)
If you have the Stripe CLI installed:


stripe listen --forward-to localhost:8000/api/billing/webhook
This will print a webhook signing secret like whsec_... — use that secret instead of creating one in the dashboard. It only works while the CLI is running.

Or use ngrok:


ngrok http 8000
Then use the https://xxxx.ngrok.io/api/billing/webhook URL in the dashboard.

Step 4 — Select events to listen for
In the dashboard endpoint form, select these 4 events:

checkout.session.completed
customer.subscription.updated
customer.subscription.deleted
invoice.payment_failed
Step 5 — Copy the signing secret
After saving the endpoint, click "Reveal" under Signing secret → copy the whsec_... value.

Step 6 — Update backend/.env
Replace line 21:


STRIPE_WEBHOOK_SECRET=whsec_your_actual_secret_here
Step 7 — Restart the server

# kill the running server, then:
cd backend && python app.py
Quickest path: Use stripe listen from the CLI — it gives you the secret immediately without needing ngrok or a public URL.
"""
import os, sys
import subprocess
import tempfile

# Load .env
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
env_vars: dict[str, str] = {}
if os.path.exists(env_path):
    try:
        from dotenv import dotenv_values

        env_vars = dict(dotenv_values(env_path))
    except Exception:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env_vars[k.strip()] = v.strip()

secret_key = env_vars.get("STRIPE_SECRET_KEY", "").strip()
if not secret_key or secret_key.startswith("sk_test_...") or not secret_key.startswith("sk_"):
    print("❌  STRIPE_SECRET_KEY not set in backend/.env")
    print("    1. Go to https://dashboard.stripe.com/apikeys")
    print("    2. Copy 'Secret key' (starts with sk_live_ or sk_test_)")
    print("    3. Add to backend/.env:  STRIPE_SECRET_KEY=sk_live_...")
    print("    4. Re-run this script")
    sys.exit(1)

try:
    import stripe
except ImportError:
    print("Installing stripe…")
    subprocess.run([sys.executable, "-m", "pip", "install", "stripe", "-q"], check=False)
    import stripe

stripe.api_key = secret_key
mode = "TEST" if "test" in secret_key else "LIVE"
print(f"\n🔑  Using Stripe {mode} mode key: {secret_key[:4]}…{'*' * 12}\n")

PLANS = [
    {
        "key":         "STRIPE_PRICE_BASIC",
        "name":        "Signal.Trade Basic",
        "description": (
            "65+ signal blocks · Polygon.io primary data · 13F institutional flow · "
            "Telegram + Discord + Web Push delivery · Backtest analytics (1d/3d/7d/14d) · "
            "Price alerts · Excel signal export · 164-ticker watchlist. "
            "7-day free trial."
        ),
        "amount":      2900,   # $29/mo
        "tier":        "basic",
    },
    {
        "key":         "STRIPE_PRICE_PRO",
        "name":        "Signal.Trade Pro",
        "description": (
            "Everything in Basic + Alpaca paper trading · Signal correlation matrix · "
            "Bayesian predictive confidence intervals · Portfolio volatility targeting · "
            "Cross-asset risk dashboard · Sector heatmap drill-down · "
            "Weekly performance digest · Simulated backtest with slippage. "
            "7-day free trial."
        ),
        "amount":      7900,  # $79/mo
        "tier":        "pro",
    },
]

results = {}
for plan in PLANS:
    print(f"Creating product: {plan['name']} …")
    # Check if product already exists
    safe_name = plan["name"].replace("'", "").strip()
    existing = stripe.Product.search(query=f"name:'{safe_name}'", limit=1)
    if existing.data:
        product = existing.data[0]
        print(f"  ✓ Product already exists: {product.id}")
    else:
        product = stripe.Product.create(
            name=plan["name"],
            description=plan["description"],
            metadata={"tier": plan["tier"]},
        )
        print(f"  ✓ Created product: {product.id}")

    # Check for existing active recurring price
    prices = stripe.Price.list(product=product.id, active=True, limit=10)
    monthly = [p for p in prices.data if p.recurring and p.recurring.interval == "month"]
    if monthly:
        price = monthly[0]
        print(f"  ✓ Price already exists: {price.id}  (${price.unit_amount/100:.2f}/mo)")
    else:
        price = stripe.Price.create(
            product=product.id,
            unit_amount=plan["amount"],
            currency="usd",
            recurring={"interval": "month"},
            metadata={"tier": plan["tier"]},
        )
        print(f"  ✓ Created price: {price.id}  (${price.unit_amount/100:.2f}/mo)")

    results[plan["key"]] = price.id

print("\n" + "─"*60)
print("✅  Done! Add these lines to backend/.env:\n")
for k, v in results.items():
    print(f"  {k}={v}")

print("\nAlso set up the Stripe webhook:")
app_url = env_vars.get("APP_URL", "https://yourdomain.com").rstrip("/")
print(f"  Endpoint URL: {app_url}/api/billing/webhook")
print("  Events to listen for:")
print("    • checkout.session.completed")
print("    • customer.subscription.updated")
print("    • customer.subscription.deleted")
print("    • invoice.payment_failed")
print("\nThen add the webhook signing secret to backend/.env:")
print("  STRIPE_WEBHOOK_SECRET=whsec_...")
print("\nDone! Restart the server after updating .env.\n")

# Optionally patch .env automatically
if results:
    import re

    with open(env_path) as f:
        content = f.read()
    for k, v in results.items():
        content = re.sub(rf"^{k}=.*$", f"{k}={v}", content, flags=re.MULTILINE)
    dir_name = os.path.dirname(env_path)
    fd, tmp_path = tempfile.mkstemp(prefix=".env.tmp.", dir=dir_name)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp_path, env_path)
    except Exception:
        os.unlink(tmp_path)
        raise
    print(f"✓  Also patched {env_path} automatically.")
