/**
 * Web Worker for Monte Carlo Simulated Returns
 * Offloads heavy path simulation from the main UI thread.
 */

self.addEventListener("message", (e) => {
  const { startingCapital, riskPct, trades, winRate, rr, paths = 500 } = e.data;

  let maxDrawdown = 0;
  let finalCapitalSum = 0;
  let allPaths = [];

  for (let i = 0; i < paths; i++) {
    let currentCapital = startingCapital;
    let peakCapital = startingCapital;
    let path = [startingCapital];

    for (let j = 0; j < trades; j++) {
      const riskAmount = currentCapital * (riskPct / 100);
      const isWin = Math.random() < winRate;

      if (isWin) {
        currentCapital += riskAmount * rr;
      } else {
        currentCapital -= riskAmount;
      }

      if (currentCapital > peakCapital) peakCapital = currentCapital;
      const drawdown = (peakCapital - currentCapital) / peakCapital;
      if (drawdown > maxDrawdown) maxDrawdown = drawdown;

      path.push(currentCapital);
    }
    finalCapitalSum += currentCapital;
    if (i < 50) allPaths.push(path); // Send a subset of paths for chart rendering
  }

  self.postMessage({
    avgFinalCapital: finalCapitalSum / paths,
    maxDrawdown: maxDrawdown * 100,
    samplePaths: allPaths
  });
});
