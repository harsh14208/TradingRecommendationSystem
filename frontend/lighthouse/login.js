/**
 * Lighthouse CI Puppeteer login script.
 *
 * The /app route requires an authenticated session. The frontend keeps the
 * access token in module memory only, but the HTTP-only refresh cookie
 * (st_refresh) provides persistence. This script seeds the refresh cookie so
 * the audit page can silently refresh and render the dashboard.
 *
 * Required env:
 *   ST_REFRESH  - value of the st_refresh HTTP-only cookie from /api/auth/login
 */
module.exports = async (browser) => {
  const token = process.env.ST_REFRESH || "";
  if (!token) {
    console.warn("[lighthouse-login] ST_REFRESH not set; skipping auth");
    return;
  }

  try {
    const page = await browser.newPage();
    await page.goto("http://localhost:8000/login", { waitUntil: "domcontentloaded" });

    await page.setCookie({
      name: "st_refresh",
      value: token,
      domain: "localhost",
      path: "/",
      httpOnly: true,
      sameSite: "Lax",
    });

    const cookies = await page.cookies("http://localhost:8000/");
    console.log("[lighthouse-login] cookies set:", cookies.map((c) => `${c.name}=${c.value.slice(0, 8)}...`).join(", "));
    await page.close();
  } catch (err) {
    console.error("[lighthouse-login] failed:", err.message);
    throw err;
  }
};
