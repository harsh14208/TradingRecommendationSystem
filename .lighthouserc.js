module.exports = {
  ci: {
    collect: {
      url: ["http://localhost:8000/app"],
      numberOfRuns: 1,
      puppeteerScript: "./frontend/lighthouse/login.js",
      chromePath:
        process.env.CHROME_PATH ||
        process.env.PUPPETEER_EXECUTABLE_PATH ||
        (process.platform === "darwin"
          ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
          : undefined),
      puppeteerLaunchOptions: {
        args: ["--no-sandbox", "--disable-dev-shm-usage"],
      },
      settings: {
        disableStorageReset: true,
      },
    },
    assert: {
      assertions: {
        // These budgets are calibrated on a local dev server (M-series Mac,
        // unthrottled Lighthouse). The /app bundle is heavy and the dashboard
        // renders large data-driven charts, so the LCP budget is intentionally
        // generous. Revisit after code-splitting / lazy-loading the dashboard.
        "first-contentful-paint": ["error", { maxNumericValue: 3500 }],
        "largest-contentful-paint": ["error", { maxNumericValue: 12000 }],
        "cumulative-layout-shift": ["error", { maxNumericValue: 0.05 }],
        "total-blocking-time": ["error", { maxNumericValue: 200 }],
        "categories:performance": ["error", { minScore: 0.65 }],
        "categories:accessibility": ["error", { minScore: 0.95 }],
        "categories:best-practices": ["error", { minScore: 0.93 }],
        "categories:seo": ["off"],
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
