/* global React, ReactDOM */
const DesignCanvas = window.DesignCanvas;
const DCSection = window.DCSection;
const DCArtboard = window.DCArtboard;

function Phone({ children }) {
  return (
    <div style={{
      width: 390, height: 800,
      borderRadius: 44,
      background: "#000",
      padding: 8,
      boxShadow: "0 30px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05)",
      overflow: "hidden",
      position: "relative",
    }}>
      <div style={{
        position: "absolute", top: 14, left: "50%", transform: "translateX(-50%)",
        width: 110, height: 28, borderRadius: 16, background: "#000", zIndex: 100,
      }}/>
      <div style={{
        width: "100%", height: "100%",
        borderRadius: 36, overflow: "hidden",
        background: "#0a0f1a",
      }}>
        {children}
      </div>
    </div>
  );
}

function MobileApp() {
  return (
    <DesignCanvas title="SIGNAL.TRADE Mobile App" subtitle="iOS · Dark · 8 screens">
      <DCSection id="screens" title="Core screens" subtitle="Tap any artboard to focus full-screen">
        <DCArtboard id="feed" label="01 · Live signal feed" width={406} height={816}>
          <Phone><window.FeedScreen/></Phone>
        </DCArtboard>
        <DCArtboard id="detail" label="02 · Signal detail" width={406} height={816}>
          <Phone><window.DetailScreen/></Phone>
        </DCArtboard>
        <DCArtboard id="portfolio" label="03 · Paper portfolio" width={406} height={816}>
          <Phone><window.PortfolioScreen/></Phone>
        </DCArtboard>
        <DCArtboard id="account" label="04 · Account & settings" width={406} height={816}>
          <Phone><window.AccountScreen/></Phone>
        </DCArtboard>
      </DCSection>
      <DCSection id="auxiliary" title="Auxiliary screens" subtitle="Onboarding, watchlist, activity & paywall">
        <DCArtboard id="onboard" label="05 · Onboarding" width={406} height={816}>
          <Phone><window.OnboardScreen/></Phone>
        </DCArtboard>
        <DCArtboard id="watchlist" label="06 · Watchlist" width={406} height={816}>
          <Phone><window.WatchlistScreen/></Phone>
        </DCArtboard>
        <DCArtboard id="notifs" label="07 · Activity / notifications" width={406} height={816}>
          <Phone><window.NotifScreen/></Phone>
        </DCArtboard>
        <DCArtboard id="paywall" label="08 · Paywall / upgrade" width={406} height={816}>
          <Phone><window.PaywallScreen/></Phone>
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

ReactDOM.createRoot(document.getElementById("canvas-root")).render(<MobileApp/>);
