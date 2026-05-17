/* ─── Account modal ─────────────────────────────────────────────────────────── */
function AccountModal({ open, onClose, user, setUser, onUpgrade }) {
  const [nameSaving,    setNameSaving]    = useState(false);
  const [nameEdit,      setNameEdit]      = useState(user?.full_name || "");
  const [nameError,     setNameError]     = useState("");
  const [linkCode,      setLinkCode]      = useState(user?.telegram_link_code || "");
  const [regen,         setRegen]         = useState(false);
  const [setupStatus,   setSetupStatus]   = useState(null);
  const [adminStats,    setAdminStats]    = useState(null);
  const [usersExpanded, setUsersExpanded] = useState(false);
  const [usersList,     setUsersList]     = useState([]);
  const [minConf,       setMinConf]       = useState(user?.min_confidence_override ?? "");
  const [confSaved,     setConfSaved]     = useState(false);
  const [confError,     setConfError]     = useState("");
  const [referral,      setReferral]      = useState(null);
  const [refCopied,     setRefCopied]     = useState(false);
  const [codeCopied,    setCodeCopied]    = useState(false);
  const [billingStatus, setBillingStatus] = useState(null);
  const [digestSending, setDigestSending] = useState(false);
  const [digestMsg,     setDigestMsg]     = useState("");
  const [digestStatus,  setDigestStatus]  = useState(null);
  const [webhookMsg,    setWebhookMsg]    = useState("");

  useEffect(() => {
    if (open && user) {
      setNameEdit(user.full_name || "");
      setLinkCode(user.telegram_link_code || "");
      setWebhookMsg("");
      setNameError("");
      setConfError("");
      if (user.is_owner) {
        authFetch("/api/admin/setup-status").then(r => r.json()).then(setSetupStatus).catch(() => {});
        apiFetch("/api/admin/stats").then(d => { if (d) setAdminStats(d); }).catch(() => {});
        apiFetch("/api/admin/weekly-digest/status").then(d => { if (d) setDigestStatus(d); }).catch(() => {});
      }
      apiFetch("/api/auth/referral").then(d => { if (d) setReferral(d); }).catch(() => {});
      apiFetch("/api/billing/status").then(d => { if (d) setBillingStatus(d); }).catch(() => {});
    }
  }, [open, user]);

  const copyReferral = () => {
    if (!referral?.referral_url) return;
    navigator.clipboard.writeText(referral.referral_url).then(() => {
      setRefCopied(true);
      setTimeout(() => setRefCopied(false), 2000);
    });
  };

  const saveName = async () => {
    const trimmed = nameEdit.trim();
    if (!trimmed) { setNameError("Name cannot be empty"); return; }
    if (trimmed.length > 60) { setNameError("Name must be 60 characters or fewer"); return; }
    setNameError("");
    setNameSaving(true);
    try {
      const res = await authFetch("/api/auth/me", { method:"PATCH", body: JSON.stringify({ full_name: trimmed }) });
      if (!res.ok) throw new Error("Failed to save");
      const d = await res.json();
      setUser(d);
    } catch {
      setNameError("Could not save — try again");
    } finally {
      setNameSaving(false);
    }
  };

  const regenCode = async () => {
    setRegen(true);
    const res = await authFetch("/api/auth/telegram-link-code", { method:"POST" });
    const d = await res.json();
    setLinkCode(d.link_code);
    setUser(p => ({ ...p, telegram_link_code: d.link_code }));
    setRegen(false);
  };

  const unlinkTelegram = async () => {
    await authFetch("/api/auth/telegram-unlink", { method:"DELETE" });
    setUser(p => ({ ...p, telegram_linked: false, telegram_link_code: null }));
    setLinkCode("");
  };

  const logout = () => {
    authFetch("/api/auth/logout", { method:"POST" }).finally(() => { clearToken(); window.location.replace("/login"); });
  };

  const registerWebhook = async () => {
    setWebhookMsg("Registering…");
    try {
      const res = await authFetch("/api/telegram/set-webhook", { method:"POST" });
      const d = await res.json();
      setWebhookMsg(d.telegram_response?.ok ? "✓ Webhook registered!" : "Error: " + (d.telegram_response?.description || JSON.stringify(d)));
    } catch {
      setWebhookMsg("Network error registering webhook");
    }
  };

  const loadUsers = async () => {
    const res = await authFetch("/api/admin/users");
    setUsersList(await res.json());
    setUsersExpanded(true);
  };

  const sendWeeklyDigest = async () => {
    setDigestSending(true);
    setDigestMsg("");
    try {
      const res = await authFetch("/api/admin/trigger-weekly-digest", { method: "POST" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Could not send weekly digest.");
      setDigestMsg(data.message || "Weekly digest is sending.");
    } catch (err) {
      setDigestMsg(err.message || "Could not send weekly digest.");
    } finally {
      setDigestSending(false);
    }
  };

  if (!open || !user) return null;
  const tier = user.subscription_tier || "free";
  const tierColor = TIER_COLORS[tier] || "var(--text-faint)";
  const inp = { background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:6, padding:"8px 12px", fontSize:12, color:"var(--text)", outline:"none", fontFamily:"var(--font-mono)", width:"100%", boxSizing:"border-box" };

  return (
    <div style={{ position:"fixed", inset:0, zIndex:9998, background:"rgba(0,0,0,0.6)", display:"flex", alignItems:"flex-start", justifyContent:"flex-end" }} onClick={onClose}>
      <div className="account-drawer" style={{ width:"min(380px, 92vw)", height:"100vh", background:"var(--bg-1)", borderLeft:"1px solid var(--line)", padding:"24px 28px", overflowY:"auto", display:"flex", flexDirection:"column", gap:0 }} onClick={e => e.stopPropagation()}>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:24 }}>
          <div style={{ fontWeight:700, fontSize:16 }}>Account</div>
          <button onClick={onClose} style={{ background:"none", border:"none", cursor:"pointer", color:"var(--text-faint)", fontSize:20 }}>×</button>
        </div>

        {/* Profile */}
        <div style={{ marginBottom:24 }}>
          <div style={{ fontSize:10, fontWeight:600, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:"var(--font-mono)", marginBottom:10, paddingBottom:8, borderBottom:"1px solid var(--line)" }}>Profile</div>
          <div style={{ fontSize:12, color:"var(--text-faint)", marginBottom:10 }}>{user.email}</div>
          <div style={{ display:"flex", gap:8, alignItems:"center" }}>
            <input style={{ ...inp, flex:1, borderColor: nameError ? "var(--down)" : undefined }} value={nameEdit}
              onChange={e => { setNameEdit(e.target.value); setNameError(""); }}
              maxLength={60}
              placeholder="Full name"/>
            <button className="btn ghost" style={{ fontSize:11, flexShrink:0 }} onClick={saveName} disabled={nameSaving}>{nameSaving ? "…" : "Save"}</button>
          </div>
          {nameError && <div style={{ fontSize:10, color:"var(--down)", marginTop:4, fontFamily:"var(--font-mono)" }}>{nameError}</div>}
        </div>

        {/* Subscription */}
        <div style={{ marginBottom:24 }}>
          <div style={{ fontSize:10, fontWeight:600, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:"var(--font-mono)", marginBottom:12, paddingBottom:8, borderBottom:"1px solid var(--line)" }}>Subscription</div>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
            <span style={{ fontSize:12, fontWeight:700, color:tierColor, background:tierColor+"22", padding:"3px 10px", borderRadius:20, border:`1px solid ${tierColor}44` }}>
              {tier.toUpperCase()}{user.is_owner ? " · OWNER" : ""}
            </span>
            {user.subscription_status === "past_due" && <span style={{ fontSize:10, color:"var(--warn)" }}>⚠️ Payment overdue</span>}
          </div>
          {(billingStatus?.period_end || user.subscription_period_end) && (
            <div style={{ fontSize:11, color:"var(--text-faint)", marginBottom:10 }}>
              {(billingStatus?.status || user.subscription_status) === "canceled" ? "Access until" : "Renews"}:{" "}
              {new Date((billingStatus?.period_end || user.subscription_period_end) * (billingStatus?.period_end > 1e10 ? 1 : 1000)).toLocaleDateString()}
              {billingStatus?.cancel_at_period_end && <span style={{ color:"var(--warn)", marginLeft:6 }}>· Cancels at period end</span>}
            </div>
          )}
          {billingStatus?.payment_method && (
            <div style={{ fontSize:11, color:"var(--text-faint)", marginBottom:10 }}>
              {billingStatus.payment_method.brand?.toUpperCase()} ···· {billingStatus.payment_method.last4}
              {billingStatus.payment_method.exp_month && (
                <span style={{ marginLeft:6, color:"var(--text-faint)" }}>
                  exp {billingStatus.payment_method.exp_month}/{String(billingStatus.payment_method.exp_year).slice(-2)}
                </span>
              )}
            </div>
          )}
          <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
            {(tier === "free" || user.subscription_status !== "active") && !user.is_owner && (
              <button className="btn primary" style={{ fontSize:11 }} onClick={onUpgrade}>Upgrade Plan</button>
            )}
            {user.stripe_customer_id && (
              <button className="btn ghost" style={{ fontSize:11 }} onClick={() => {
                authFetch("/api/billing/portal", { method:"POST" }).then(r => r.json()).then(d => { if (d.portal_url) window.open(d.portal_url, "_blank"); });
              }}>Manage Billing</button>
            )}
          </div>
        </div>

        {/* Telegram */}
        <div style={{ marginBottom:24 }}>
          <div style={{ fontSize:10, fontWeight:600, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:"var(--font-mono)", marginBottom:12, paddingBottom:8, borderBottom:"1px solid var(--line)" }}>Telegram Alerts</div>
          {user.telegram_linked ? (
            <div>
              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
                <div style={{ width:8, height:8, borderRadius:"50%", background:"var(--up)" }}/>
                <span style={{ fontSize:12, color:"var(--up)" }}>Telegram connected</span>
              </div>
              <button className="btn ghost" style={{ fontSize:11 }} onClick={unlinkTelegram}>Unlink Telegram</button>
            </div>
          ) : (
            <div>
              <div style={{ fontSize:12, color:"var(--text-dim)", marginBottom:10, lineHeight:1.6 }}>
                Open your Telegram bot and send:
              </div>
              <div style={{ display:"flex", gap:8, alignItems:"center", marginBottom:10 }}>
                <code style={{ ...inp, flex:1, fontSize:13, fontWeight:600, color:"var(--accent)", textAlign:"center", letterSpacing:"0.1em" }}>
                  /start {linkCode || "—"}
                </code>
                <button className="btn ghost" style={{ fontSize:11, flexShrink:0 }} disabled={!linkCode} onClick={() => {
                  navigator.clipboard.writeText(`/start ${linkCode}`).then(() => { setCodeCopied(true); setTimeout(() => setCodeCopied(false), 2000); });
                }}>{codeCopied ? "✓ Copied" : "Copy"}</button>
                <button className="btn ghost" style={{ fontSize:11, flexShrink:0 }} onClick={regenCode} disabled={regen}>{regen ? "…" : "New code"}</button>
              </div>
              {tier === "free" && !user.is_owner && (
                <div style={{ fontSize:11, color:"var(--warn)" }}>⚠️ Requires Basic plan for delivery.</div>
              )}
            </div>
          )}
        </div>

        {/* Weekly digest */}
        {user.is_owner && (
          <div style={{ marginBottom:24 }}>
            <div style={{ fontSize:10, fontWeight:600, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:"var(--font-mono)", marginBottom:12, paddingBottom:8, borderBottom:"1px solid var(--line)" }}>
              Weekly Digest
            </div>
            <div style={{ background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:8, padding:"12px 14px", marginBottom:10 }}>
              <div style={{ display:"flex", justifyContent:"space-between", gap:10, marginBottom:8 }}>
                <span style={{ fontSize:11, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.08em" }}>Schedule</span>
                <span style={{ fontSize:12, color:"var(--text)", fontFamily:"var(--font-mono)" }}>{digestStatus?.schedule || "Sunday 08:00 ET"}</span>
              </div>
              <div style={{ display:"flex", justifyContent:"space-between", gap:10 }}>
                <span style={{ fontSize:11, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.08em" }}>Delivery</span>
                <span style={{ fontSize:12, color:user.telegram_linked ? "var(--up)" : "var(--warn)", textAlign:"right" }}>
                  {user.telegram_linked ? "Owner Telegram + active subscribers" : "Server fallback chat + active subscribers"}
                </span>
              </div>
              {digestStatus && (
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:6, marginTop:10, paddingTop:10, borderTop:"1px solid var(--line)" }}>
                  {[
                    ["Bot", digestStatus.telegram_configured],
                    ["Owner TG", digestStatus.owner_telegram_linked || digestStatus.fallback_chat_configured],
                    ["Email", digestStatus.email_configured],
                    ["Fallback", digestStatus.fallback_chat_configured],
                  ].map(([label, ok]) => (
                    <span key={label} style={{ fontSize:10, color:ok ? "var(--up)" : "var(--text-faint)", fontFamily:"var(--font-mono)" }}>
                      {ok ? "✓" : "○"} {label}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div style={{ fontSize:11, color:"var(--text-faint)", lineHeight:1.55, marginBottom:10 }}>
              Sends this week&apos;s signal count, resolved win rate, average return, best/worst signal, and SPY comparison by Telegram and email.
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:8, flexWrap:"wrap" }}>
              <button className="btn primary" style={{ fontSize:11 }} onClick={sendWeeklyDigest} disabled={digestSending}>
                <Icon name="telegram" size={13}/> {digestSending ? "Sending…" : "Send Now"}
              </button>
              {digestMsg && (
                <span style={{ fontSize:11, color:digestMsg.toLowerCase().includes("could") ? "var(--down)" : "var(--up)", lineHeight:1.4 }}>
                  {digestMsg}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Admin section */}
        {user.is_owner && (setupStatus || adminStats) && (
          <div style={{ marginBottom:24 }}>
            <div style={{ fontSize:10, fontWeight:600, color:"var(--warn)", textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:"var(--font-mono)", marginBottom:12, paddingBottom:8, borderBottom:"1px solid var(--line)", display:"flex", justifyContent:"space-between" }}>
              <span>Admin</span>
              {setupStatus && <span style={{ color: setupStatus.all_critical_ok ? "var(--up)" : "var(--down)" }}>
                {setupStatus.all_critical_ok ? "✓ Ready" : "⚠ Action needed"}
              </span>}
            </div>
            {adminStats && (
              <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:8, marginBottom:12 }}>
                {[
                  ["MRR", `$${(adminStats.mrr||0).toFixed(0)}`, "var(--up)"],
                  ["ARR", `$${(adminStats.arr||0).toFixed(0)}`, "var(--up)"],
                  ["Subscribers", adminStats.active_subscriptions ?? adminStats.total_users ?? "—", "var(--accent)"],
                  ["Basic", adminStats.basic_count ?? "—", "var(--text)"],
                  ["Pro", adminStats.pro_count ?? "—", "#7c3aed"],
                  ["Signals sent", adminStats.signals_sent_today ?? adminStats.total_signals ?? "—", "var(--text)"],
                ].map(([l,v,c]) => (
                  <div key={l} style={{ background:"var(--bg-2)", borderRadius:6, padding:"8px 10px" }}>
                    <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:3 }}>{l}</div>
                    <div style={{ fontSize:15, fontWeight:700, fontFamily:"var(--font-mono)", color:c }}>{v}</div>
                  </div>
                ))}
              </div>
            )}
            {setupStatus && <div style={{ display:"flex", flexDirection:"column", gap:5, marginBottom:12 }}>
              {(setupStatus.checks||[]).filter(c => !c.ok && c.critical).map(c => (
                <div key={c.key} style={{ fontSize:11, display:"flex", gap:6 }}>
                  <span style={{ color:"var(--down)", flexShrink:0 }}>✗</span>
                  <div><span style={{ fontWeight:600, color:"var(--text)" }}>{c.label}</span><div style={{ fontSize:10, color:"var(--text-faint)" }}>{c.note}</div></div>
                </div>
              ))}
              {setupStatus.all_critical_ok && <div style={{ fontSize:11, color:"var(--up)" }}>✓ All critical config set</div>}
            </div>}
            <div style={{ display:"flex", gap:8, flexWrap:"wrap", alignItems:"center" }}>
              <button className="btn ghost" style={{ fontSize:11 }} onClick={registerWebhook}>Register TG Webhook</button>
              <button className="btn ghost" style={{ fontSize:11 }} onClick={loadUsers}>Load Users</button>
            </div>
            {webhookMsg && (
              <div style={{ fontSize:11, color: webhookMsg.startsWith("✓") ? "var(--up)" : "var(--down)", marginTop:6, fontFamily:"var(--font-mono)" }}>
                {webhookMsg}
              </div>
            )}
            {usersExpanded && usersList.length > 0 && (
              <div style={{ marginTop:10, maxHeight:120, overflowY:"auto", display:"flex", flexDirection:"column", gap:4 }}>
                {usersList.map(u => (
                  <div key={u.id} style={{ display:"flex", justifyContent:"space-between", fontSize:11, padding:"4px 8px", background:"var(--bg-2)", borderRadius:5 }}>
                    <span>{u.email}</span>
                    <span style={{ color:TIER_COLORS[u.tier], fontFamily:"var(--font-mono)", fontWeight:700 }}>{u.tier.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Signal preferences */}
        <div style={{ marginBottom:20 }}>
          <div style={{ fontSize:10, fontWeight:600, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:"var(--font-mono)", marginBottom:12, paddingBottom:8, borderBottom:"1px solid var(--line)" }}>
            Signal Preferences
          </div>
          <div style={{ fontSize:11, color:"var(--text-faint)", marginBottom:8 }}>
            Personal Telegram delivery threshold — only signals above this confidence % will be sent to you.
            Leave blank to use the server default ({user.min_confidence_override == null ? "currently using global" : `global`}).
          </div>
          <div style={{ display:"flex", gap:8, alignItems:"center" }}>
            <input
              type="number" min="0" max="100" placeholder="e.g. 65"
              value={minConf}
              onChange={e => { setMinConf(e.target.value); setConfError(""); }}
              style={{ ...inp, width:80, borderColor: confError ? "var(--down)" : undefined }}
            />
            <span style={{ fontSize:11, color:"var(--text-faint)" }}>%</span>
            <button
              onClick={async () => {
                if (minConf !== "") {
                  const v = Number(minConf);
                  if (isNaN(v) || v < 0 || v > 100) { setConfError("Must be 0–100"); return; }
                }
                setConfError("");
                const val = minConf === "" ? null : Number(minConf);
                const res = await authFetch("/api/auth/signal-prefs", {
                  method:"PATCH",
                  body: JSON.stringify({ min_confidence: val }),
                });
                if (res.ok) { setConfSaved(true); setTimeout(() => setConfSaved(false), 2000); }
              }}
              style={{ padding:"6px 14px", background:"var(--accent)", border:"none", borderRadius:6, color:"#000", fontSize:12, fontWeight:600, cursor:"pointer" }}>
              {confSaved ? "Saved ✓" : "Save"}
            </button>
            {minConf !== "" && (
              <button onClick={() => { setMinConf(""); setConfError(""); }} style={{ fontSize:11, color:"var(--text-faint)", background:"none", border:"none", cursor:"pointer" }}>
                Reset to global
              </button>
            )}
          </div>
          {confError && <div style={{ fontSize:10, color:"var(--down)", marginTop:4, fontFamily:"var(--font-mono)" }}>{confError}</div>}
        </div>

        {/* Referral */}
        <div style={{ marginBottom:20 }}>
          <div style={{ fontSize:10, fontWeight:600, color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", fontFamily:"var(--font-mono)", marginBottom:12, paddingBottom:8, borderBottom:"1px solid var(--line)" }}>
            Referral Programme
          </div>
          <div style={{ fontSize:12, color:"var(--text-dim)", marginBottom:10, lineHeight:1.6 }}>
            Share your link — earn <strong style={{ color:"var(--accent)" }}>$29 credit</strong> (1 free month of Basic) when a friend converts to a paid plan.
          </div>
          {referral ? (
            <>
              <div style={{ display:"flex", gap:6, alignItems:"center", marginBottom:10 }}>
                <input readOnly value={referral.referral_url}
                  style={{ flex:1, background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:6, padding:"6px 10px", fontSize:11, fontFamily:"var(--font-mono)", color:"var(--text-dim)", outline:"none" }}
                />
                <button onClick={copyReferral}
                  style={{ padding:"6px 12px", background: refCopied ? "var(--accent)" : "var(--bg-3)", border:"1px solid var(--line)", borderRadius:6, fontSize:11, fontWeight:600, color: refCopied ? "#000" : "var(--text)", cursor:"pointer", whiteSpace:"nowrap" }}>
                  {refCopied ? "Copied ✓" : "Copy"}
                </button>
              </div>
              <div style={{ display:"flex", gap:16, fontSize:11, fontFamily:"var(--font-mono)", color:"var(--text-faint)" }}>
                <span><strong style={{ color:"var(--text)" }}>{referral.referrals_total}</strong> referrals</span>
                <span><strong style={{ color:"var(--accent)" }}>{referral.rewards_claimed}</strong> credits earned</span>
                {referral.rewards_pending > 0 && <span><strong style={{ color:"var(--warn)" }}>{referral.rewards_pending}</strong> pending</span>}
              </div>
            </>
          ) : (
            <div style={{ fontSize:11, color:"var(--text-faint)" }}>Loading referral link…</div>
          )}
        </div>

        {/* Footer */}
        <div style={{ marginTop:"auto", paddingTop:20, borderTop:"1px solid var(--line)" }}>
          <div style={{ display:"flex", gap:8, justifyContent:"center", marginBottom:14 }}>
            {[["ToS","/tos"],["Privacy","/privacy"],["Track Record","/track-record"]].map(([l,h]) => (
              <a key={l} href={h} target="_blank" style={{ fontSize:10, color:"var(--text-faint)" }}>{l}</a>
            ))}
          </div>
          <button onClick={logout} style={{ width:"100%", padding:"10px 0", background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.3)", borderRadius:8, color:"var(--down)", fontSize:13, fontWeight:600, cursor:"pointer" }}>
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Price alert modal ─────────────────────────────────────────────────────── */
function PriceAlertModal({ open, onClose, ticker, currentPrice }) {
  const [target, setTarget]       = useState("");
  const [condition, setCondition] = useState("above");
  const [saving, setSaving]       = useState(false);
  const [message, setMessage]     = useState("");
  const [targetError, setTargetError] = useState("");

  useEffect(() => {
    if (!open) return;
    const price = Number(currentPrice);
    setTarget(Number.isFinite(price) && price > 0 ? price.toFixed(2) : "");
    setCondition("above");
    setMessage("");
    setTargetError("");
  }, [open, currentPrice, ticker]);

  if (!open) return null;

  const cleanTicker = (ticker || "").toUpperCase();
  const price = Number(currentPrice);
  const targetNum = Number(target);
  const validTarget = isFinite(targetNum) && targetNum > 0 && targetNum < 1_000_000;

  const inputStyle = {
    width:"100%",
    background:"var(--bg-2)",
    border: `1px solid ${targetError ? "var(--down)" : "var(--line)"}`,
    borderRadius:6,
    padding:"9px 12px",
    fontSize:13,
    color:"var(--text)",
    outline:"none",
    fontFamily:"var(--font-mono)",
    boxSizing:"border-box",
  };

  const validateTarget = (val) => {
    const n = Number(val);
    if (!val) { setTargetError("Price is required"); return false; }
    if (isNaN(n) || !isFinite(n)) { setTargetError("Must be a valid number"); return false; }
    if (n <= 0) { setTargetError("Price must be greater than 0"); return false; }
    if (n >= 1_000_000) { setTargetError("Price must be below $1,000,000"); return false; }
    setTargetError("");
    return true;
  };

  const save = async () => {
    if (!cleanTicker || !validateTarget(target)) return;
    setSaving(true);
    setMessage("");
    try {
      const res = await authFetch("/api/alerts/", {
        method:"POST",
        body: JSON.stringify({
          ticker: cleanTicker,
          target_price: targetNum,
          condition,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Could not create alert.");
      setMessage(data.message || "Alert created.");
      setTimeout(onClose, 700);
    } catch (err) {
      setMessage(err.message || "Could not create alert.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={{ position:"fixed", inset:0, zIndex:9999, background:"rgba(0,0,0,0.64)", display:"flex", alignItems:"center", justifyContent:"center", padding:20 }} onClick={onClose}>
      <div style={{ width:"100%", maxWidth:380, background:"var(--bg-1)", border:"1px solid var(--line)", borderRadius:10, padding:"22px 24px", boxShadow:"0 20px 70px rgba(0,0,0,0.45)" }} onClick={e => e.stopPropagation()}>
        <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:18 }}>
          <div style={{ width:34, height:34, borderRadius:8, background:"var(--bg-2)", display:"grid", placeItems:"center", color:"var(--accent)" }}>
            <Icon name="bell" size={16}/>
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontSize:16, fontWeight:700 }}>Price Alert</div>
            <div style={{ fontSize:11, color:"var(--text-faint)", marginTop:2, fontFamily:"var(--font-mono)" }}>
              {cleanTicker || "Signal"}{Number.isFinite(price) && price > 0 ? ` · current $${fmt(price)}` : ""}
            </div>
          </div>
          <button onClick={onClose} style={{ background:"none", border:"none", color:"var(--text-faint)", cursor:"pointer", fontSize:20, lineHeight:1 }}>×</button>
        </div>

        <label style={{ display:"block", fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:7 }}>
          Trigger when price is
        </label>
        <div className="seg" style={{ marginBottom:14 }}>
          <button className={condition === "above" ? "on" : ""} onClick={() => setCondition("above")}>Above</button>
          <button className={condition === "below" ? "on" : ""} onClick={() => setCondition("below")}>Below</button>
        </div>

        <label style={{ display:"block", fontSize:10, color:"var(--text-faint)", fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:7 }}>
          Target price
        </label>
        <input
          type="number"
          min="0"
          step="0.01"
          value={target}
          onChange={e => { setTarget(e.target.value); validateTarget(e.target.value); }}
          onKeyDown={e => { if (e.key === "Enter") save(); }}
          placeholder="0.00"
          style={inputStyle}
        />
        {targetError && <div style={{ fontSize:11, color:"var(--down)", marginTop:4, fontFamily:"var(--font-mono)" }}>{targetError}</div>}

        {message && (
          <div style={{ marginTop:12, fontSize:12, color:message.toLowerCase().includes("could") ? "var(--down)" : "var(--up)" }}>
            {message}
          </div>
        )}

        <div style={{ display:"flex", justifyContent:"flex-end", gap:8, marginTop:22 }}>
          <button className="btn ghost" onClick={onClose}>Cancel</button>
          <button className="btn primary" onClick={save} disabled={saving || !cleanTicker || !validTarget}>
            {saving ? "Saving…" : "Create Alert"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Watchlist overlay ─────────────────────────────────────────────────────── */
const TICKER_RE = /^[A-Z]{1,5}$/;

// quotes = tickerTape array from app.jsx ({ticker, price, change, changePct})
// histSignals = resolved sent signals array from app.jsx (for last outcome display)
function WatchlistView({ open, onClose, quotes, histSignals }) {
  const [tickers, setTickers] = useState([]);
  const [input,   setInput]   = useState("");
  const [loading, setLoading] = useState(false);
  const [adding,  setAdding]  = useState(false);
  const [error,   setError]   = useState("");
  const [sortMode, setSortMode] = useState("added");

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    apiFetch("/api/watchlist").then(d => {
      const items = Array.isArray(d) ? d : [];
      setTickers(items.map((t, i) => ({ ...t, _idx: i })));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [open]);

  const add = async () => {
    const ticker = input.trim().replace(/[^A-Z]/g, "").toUpperCase();
    if (!ticker) { setError("Enter a ticker symbol"); return; }
    if (!TICKER_RE.test(ticker)) { setError("Ticker symbols are 1–5 letters (e.g. AAPL, TSLA)"); return; }
    if (tickers.find(t => t.ticker === ticker)) { setError(`${ticker} is already on the list`); return; }
    setAdding(true); setError("");
    try {
      await authFetch("/api/watchlist", { method:"POST", body: JSON.stringify({ ticker }) });
      setTickers(prev => [...prev, { ticker, company: ticker, is_active: true, _idx: prev.length }]);
      setInput("");
    } catch { setError("Failed to add — check the ticker symbol"); }
    setAdding(false);
  };

  const remove = async (ticker) => {
    await authFetch(`/api/watchlist/${ticker}`, { method:"DELETE" });
    setTickers(prev => prev.filter(t => t.ticker !== ticker));
  };

  const sorted = useMemo(() => {
    if (sortMode === "az") return [...tickers].sort((a,b) => a.ticker.localeCompare(b.ticker));
    if (sortMode === "za") return [...tickers].sort((a,b) => b.ticker.localeCompare(a.ticker));
    return [...tickers].sort((a,b) => (a._idx ?? 0) - (b._idx ?? 0));
  }, [tickers, sortMode]);

  // Precompute quote and last-outcome lookups so each row doesn't filter arrays
  const quoteMap = useMemo(() => {
    const m = {};
    for (const q of (quotes || [])) m[q.ticker] = q;
    return m;
  }, [quotes]);

  const lastOutcomeMap = useMemo(() => {
    const m = {};
    for (const s of (histSignals || [])) {
      if (s.outcomePct == null && s.outcome14d == null) continue;
      const prev = m[s.ticker];
      const ts = s.ts || s.created_at || "";
      if (!prev || ts > (prev.ts || "")) m[s.ticker] = s;
    }
    return m;
  }, [histSignals]);

  const SORT_LABELS = { added:"Added ↓", az:"A → Z", za:"Z → A" };
  const cycleSortMode = () => setSortMode(m => m === "added" ? "az" : m === "az" ? "za" : "added");

  return (
    <div className={`overlay ${open?"open":""}`}>
      <div className="overlay-head">
        <div>
          <div className="crumb">WORKSPACE / WATCHLIST</div>
          <h2>Stocks to monitor</h2>
        </div>
        <button className="btn ghost" style={{ marginLeft:"auto" }} onClick={onClose}><Icon name="x" size={14}/> Close</button>
      </div>
      <div style={{ padding:"0 28px 28px", maxWidth:640 }}>
        <div style={{ fontSize:12, color:"var(--text-faint)", marginBottom:20, lineHeight:1.6 }}>
          The scanner only fires signals for tickers on this list. Add any US stock ticker — the engine will start watching it on the next scan cycle.
        </div>

        <div style={{ display:"flex", gap:8, marginBottom:24 }}>
          <input
            value={input}
            onChange={e => {
              const clean = e.target.value.toUpperCase().replace(/[^A-Z]/g, "").slice(0, 5);
              setInput(clean);
              setError("");
            }}
            onKeyDown={e => e.key === "Enter" && add()}
            placeholder="Enter ticker symbol e.g. AAPL"
            maxLength={5}
            style={{ flex:1, background:"var(--bg-2)", border:`1px solid ${error ? "var(--down)" : "var(--line)"}`, borderRadius:6,
              padding:"8px 12px", fontSize:13, color:"var(--text)", outline:"none",
              fontFamily:"var(--font-mono)", letterSpacing:"0.05em" }}
          />
          <button className="btn primary" onClick={add} disabled={adding || !input.trim()}>
            <Icon name="plus" size={13}/> {adding ? "Adding…" : "Add"}
          </button>
        </div>
        {error && <div style={{ fontSize:11, color:"var(--down)", marginTop:-16, marginBottom:16 }}>{error}</div>}

        {loading && <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>Loading…</div>}
        {!loading && tickers.length === 0 && (
          <div style={{ padding:"40px 0", textAlign:"center", color:"var(--text-faint)", fontSize:12 }}>
            No tickers yet. Add one above to start generating signals for it.
          </div>
        )}
        {!loading && tickers.length > 0 && (
          <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
            <div style={{ display:"flex", alignItems:"center", marginBottom:8 }}>
              <span style={{ fontSize:10, fontFamily:"var(--font-mono)", textTransform:"uppercase", letterSpacing:"0.1em", color:"var(--text-faint)" }}>
                {tickers.length} ticker{tickers.length !== 1 ? "s" : ""} monitored
              </span>
              <button onClick={cycleSortMode}
                style={{ marginLeft:"auto", fontSize:10, fontFamily:"var(--font-mono)", background:"var(--bg-2)",
                  border:"1px solid var(--line)", borderRadius:4, padding:"3px 10px", cursor:"pointer",
                  color:"var(--accent)" }}>
                Sort: {SORT_LABELS[sortMode]}
              </button>
            </div>
            {sorted.map((t, idx) => {
              const q    = quoteMap[t.ticker];
              const last = lastOutcomeMap[t.ticker];
              const ret  = last ? (last.outcome14d ?? last.outcomePct ?? null) : null;
              const retColor = ret == null ? "var(--text-faint)" : ret > 0 ? "var(--up)" : "var(--down)";
              const chgColor = q?.changePct == null ? "var(--text-faint)" : q.changePct >= 0 ? "var(--up)" : "var(--down)";
              return (
                <div key={t.ticker} style={{ display:"flex", alignItems:"center", gap:10, padding:"10px 14px",
                  background:"var(--bg-2)", border:"1px solid var(--line)", borderRadius:8 }}>
                  <div style={{ width:24, textAlign:"center", fontFamily:"var(--font-mono)", fontSize:10,
                    color:"var(--text-faint)", flexShrink:0 }}>
                    {sortMode === "added" ? (idx + 1) : null}
                  </div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:"var(--font-mono)", fontWeight:700, fontSize:13 }}>{t.ticker}</div>
                    {t.company && t.company !== t.ticker && (
                      <div style={{ fontSize:10, color:"var(--text-faint)", marginTop:1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{t.company}</div>
                    )}
                  </div>
                  {/* Live price from quotes */}
                  {q && (
                    <div style={{ textAlign:"right", flexShrink:0 }}>
                      <div className="wl-price">${q.price?.toFixed(2) ?? "—"}</div>
                      <div className="wl-change" style={{ color:chgColor }}>
                        {q.changePct != null ? `${q.changePct >= 0 ? "+" : ""}${q.changePct.toFixed(2)}%` : ""}
                      </div>
                    </div>
                  )}
                  {/* Last signal outcome */}
                  {last && ret != null && (
                    <div style={{ flexShrink:0, textAlign:"right" }} title={`Last ${last.action} → ${ret >= 0 ? "+" : ""}${ret.toFixed(2)}%`}>
                      <span style={{ fontFamily:"var(--font-mono)", fontSize:10, fontWeight:700, color:retColor }}>
                        {last.action} {ret >= 0 ? "+" : ""}{ret.toFixed(1)}%
                      </span>
                    </div>
                  )}
                  <button onClick={() => remove(t.ticker)} style={{ background:"none", border:"none", cursor:"pointer",
                    color:"var(--text-faint)", padding:"4px 6px", borderRadius:4, fontSize:11,
                    fontFamily:"var(--font-mono)", flexShrink:0 }} title={`Remove ${t.ticker}`}>
                    ✕
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Pricing overlay ───────────────────────────────────────────────────────── */
function PricingView({ open, onClose, user }) {
  const [plans, setPlans] = useState([]);
  const [checking, setChecking] = useState(null);

  useEffect(() => {
    if (!open) return;
    fetch("/api/billing/plans").then(r => r.json()).then(setPlans).catch(() => {});
  }, [open]);

  const startCheckout = async tier => {
    setChecking(tier);
    try {
      const res  = await authFetch(`/api/billing/checkout/${tier}`, { method:"POST" });
      const data = await res.json();
      if (data.checkout_url) window.location.href = data.checkout_url;
    } catch { setChecking(null); }
  };

  if (!open) return null;
  return (
    <div className={`overlay open`}>
      <div className="overlay-head">
        <div><div className="crumb">ACCOUNT / PRICING</div><h2>Choose your plan</h2></div>
        <button className="btn ghost" onClick={onClose} style={{ marginLeft:"auto" }}><Icon name="x" size={14}/> Close</button>
      </div>
      <div style={{ padding:"20px 28px 40px", overflowY:"auto", maxHeight:"calc(100vh - 120px)" }}>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(240px,1fr))", gap:16, maxWidth:860, margin:"0 auto" }}>
          {plans.map(plan => {
            const isCurrent = user?.subscription_tier === plan.id && (plan.id === "free" || user?.subscription_status === "active");
            return (
              <div key={plan.id} style={{ background:"var(--bg-2)", borderRadius:12, padding:"24px 24px 28px", border: plan.highlight ? "2px solid var(--accent)" : "1px solid var(--line)", position:"relative" }}>
                {plan.highlight && <div style={{ position:"absolute", top:-11, left:"50%", transform:"translateX(-50%)", background:"var(--accent)", color:"#fff", fontSize:10, fontWeight:700, padding:"3px 12px", borderRadius:20 }}>MOST POPULAR</div>}
                <div style={{ fontSize:14, fontWeight:700, color:"var(--text-dim)", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:10 }}>{plan.name}</div>
                <div style={{ fontSize:26, fontWeight:800, fontFamily:"var(--font-mono)", marginBottom:16 }}>
                  {plan.price === 0 ? "Free" : `$${(plan.price/100).toFixed(2)}`}
                  {plan.interval && <span style={{ fontSize:12, fontWeight:400, color:"var(--text-faint)" }}>/mo</span>}
                </div>
                <ul style={{ listStyle:"none", padding:0, margin:"0 0 20px", display:"flex", flexDirection:"column", gap:7 }}>
                  {(plan.features||[]).map((f, i) => (
                    <li key={i} style={{ fontSize:12, color:"var(--text-dim)", display:"flex", gap:8 }}>
                      <span style={{ color:"var(--up)" }}>✓</span>{f}
                    </li>
                  ))}
                </ul>
                {isCurrent
                  ? <div style={{ textAlign:"center", fontSize:12, color:"var(--text-faint)", padding:"8px 0", border:"1px solid var(--line)", borderRadius:8 }}>Current plan</div>
                  : plan.price > 0 && (
                    <button className="btn primary" style={{ width:"100%" }} disabled={checking === plan.id} onClick={() => startCheckout(plan.id)}>
                      {checking === plan.id ? "Redirecting…" : plan.cta}
                    </button>
                  )
                }
              </div>
            );
          })}
        </div>
        <div style={{ textAlign:"center", marginTop:28, fontSize:11, color:"var(--text-faint)", lineHeight:1.7 }}>
          Cancel anytime · Payments by Stripe<br/>⚠️ Not financial advice · Past performance does not guarantee future results
        </div>
      </div>
    </div>
  );
}

/* ─── Tweaks panel ─────────────────────────────────────────────────────────── */
function TweaksPanel({ open, onClose, state, set }) {
  const accents = [
    ["#10b981","emerald"],["#60a5fa","azure"],["#f59e0b","amber"],
    ["#ef4444","red"],["#a78bfa","violet"],["#e6edf7","mono"],
  ];
  return (
    <div className={`tweaks ${open?"open":""}`}>
      <h4>Tweaks <span className="cl" onClick={onClose}><Icon name="x" size={14}/></span></h4>
      <div className="tweak-row">
        <span className="l">Theme</span>
        <div className="seg">
          <button className={state.theme==="dark"?"on":""} onClick={() => set({ theme:"dark" })}>Dark</button>
          <button className={state.theme==="light"?"on":""} onClick={() => set({ theme:"light" })}>Light</button>
        </div>
      </div>
      <div className="tweak-row">
        <span className="l">Accent</span>
        <div className="swatches">
          {accents.map(([c,n]) => (
            <div key={c} title={n} className={`swatch ${state.accent===c?"on":""}`} style={{ background:c }} onClick={() => set({ accent:c })}/>
          ))}
        </div>
      </div>
      <div className="tweak-row">
        <span className="l">Density</span>
        <div className="seg">
          <button className={state.density==="comfortable"?"on":""} onClick={() => set({ density:"comfortable" })}>Comfortable</button>
          <button className={state.density==="compact"?"on":""} onClick={() => set({ density:"compact" })}>Compact</button>
        </div>
      </div>
      <div className="tweak-row">
        <span className="l">Chart</span>
        <div className="seg">
          <button className={state.chartStyle==="line"?"on":""} onClick={() => set({ chartStyle:"line" })}>Line</button>
          <button className={state.chartStyle==="area"?"on":""} onClick={() => set({ chartStyle:"area" })}>Area</button>
          <button className={state.chartStyle==="candles"?"on":""} onClick={() => set({ chartStyle:"candles" })}>Candles</button>
        </div>
      </div>
      <div className="tweak-row">
        <span className="l">Aggressiveness</span>
        <div className="seg">
          <button className={state.aggressiveness==="conservative"?"on":""} onClick={() => set({ aggressiveness:"conservative" })}>Conserv.</button>
          <button className={state.aggressiveness==="balanced"?"on":""} onClick={() => set({ aggressiveness:"balanced" })}>Balanced</button>
          <button className={state.aggressiveness==="aggressive"?"on":""} onClick={() => set({ aggressiveness:"aggressive" })}>Aggressive</button>
        </div>
      </div>
      <div className="tweak-row">
        <span className="l">Style</span>
        <div className="seg">
          <button className={state.style==="intraday"?"on":""} onClick={() => set({ style:"intraday" })}>Intraday</button>
          <button className={state.style==="swing"?"on":""} onClick={() => set({ style:"swing" })}>Swing</button>
          <button className={state.style==="position"?"on":""} onClick={() => set({ style:"position" })}>Position</button>
        </div>
      </div>
      <div className="tweak-row">
        <span className="l">Active days</span>
        <div className="seg">
          {["Mon","Tue","Wed","Thu","Fri"].map(d => (
            <button key={d} className={state.days?.includes(d)?"on":""} onClick={() => {
              const cur = state.days || [];
              set({ days: cur.includes(d) ? cur.filter(x => x !== d) : [...cur, d] });
            }}>{d}</button>
          ))}
        </div>
      </div>
      <div className="tweak-row">
        <span className="l">Time window</span>
        <div style={{ display:"flex", gap:6, alignItems:"center", fontFamily:"var(--font-mono)", fontSize:11 }}>
          <input type="time" value={state.startTime||"09:30"} onChange={e => set({ startTime:e.target.value })} style={{ background:"var(--bg-card)", border:"1px solid var(--line)", color:"var(--text)", padding:"4px 6px", borderRadius:4, fontFamily:"inherit", fontSize:11 }}/>
          <span style={{ color:"var(--text-faint)" }}>–</span>
          <input type="time" value={state.endTime||"16:00"} onChange={e => set({ endTime:e.target.value })} style={{ background:"var(--bg-card)", border:"1px solid var(--line)", color:"var(--text)", padding:"4px 6px", borderRadius:4, fontFamily:"inherit", fontSize:11 }}/>
        </div>
      </div>
      <div className="tweak-row" style={{ flexDirection:"column", alignItems:"flex-start", gap:6 }}>
        <span className="l">Confidence threshold</span>
        <div style={{ display:"flex", gap:6, alignItems:"center" }}>
          <input type="number" min={0} max={100}
            value={state.customConf != null ? state.customConf : (state.aggressiveness === "aggressive" ? 55 : state.aggressiveness === "conservative" ? 75 : 62)}
            onChange={e => {
              const v = parseFloat(e.target.value);
              if (!isNaN(v) && v >= 0 && v <= 100) set({ customConf: v });
            }}
            style={{ width:60, background:"var(--bg-card)", border:"1px solid var(--line)", borderRadius:4,
              color:"var(--text)", fontFamily:"var(--font-mono)", padding:"4px 6px", fontSize:13, outline:"none" }}/>
          <span style={{ fontFamily:"var(--font-mono)", fontSize:12, color:"var(--text-faint)" }}>%</span>
          {state.customConf != null && (
            <button onClick={() => set({ customConf: null })}
              style={{ fontSize:10, background:"none", border:"1px solid var(--line)", borderRadius:4,
                color:"var(--text-faint)", padding:"3px 7px", cursor:"pointer", fontFamily:"var(--font-mono)" }}>
              Reset
            </button>
          )}
        </div>
        <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)" }}>
          {state.customConf != null ? `Custom: ${state.customConf}% (overrides preset)` : `Preset: ${state.aggressiveness}`}
        </div>
      </div>
      <div style={{ marginTop:14, paddingTop:10, borderTop:"1px solid var(--line)" }}>
        <div style={{ fontSize:9, fontFamily:"var(--font-mono)", color:"var(--text-faint)", textTransform:"uppercase", letterSpacing:"0.1em", marginBottom:8 }}>
          Engine Bias · survives factor mining
        </div>
        {[
          { key:"cluster_boost_pct",  label:"Cluster boost %", default:0.12, min:0, max:0.30, step:0.01, fmt: v => `${(v*100).toFixed(0)}%`,
            tip:"12% by default. Halved automatically when ticker win rate < 50%. Reduce here to fix overconfidence in high-source-agreement signals." },
          { key:"orthogonality_pts",  label:"Orthogonality pts/src", default:3, min:0, max:6, step:0.5, fmt: v => `${v}`,
            tip:"Score points added per independent confirming source (max 6 sources). Default 3 → max +18. Reduce to limit the orthogonality bonus when engine runs hot." },
          { key:"orthogonality_max",  label:"Orthogonality cap", default:18, min:0, max:30, step:1, fmt: v => `${v}`,
            tip:"Hard ceiling on orthogonality bonus regardless of source count. Default 18." },
        ].map(({ key, label, default: def, min, max, step, fmt: fmtFn, tip }) => {
          const wo  = state.weight_overrides || {};
          const cur = wo[key] != null ? wo[key] : def;
          const isOverridden = wo[key] != null;
          return (
            <div key={key} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
              <span style={{ fontSize:10, fontFamily:"var(--font-mono)", color:"var(--text-faint)", flex:1 }} title={tip}>{label}</span>
              <input type="number" min={min} max={max} step={step}
                value={cur}
                onChange={e => {
                  const v = parseFloat(e.target.value);
                  if (!isNaN(v)) set({ weight_overrides: { ...wo, [key]: v } });
                }}
                style={{ width:52, background:"var(--bg-card)", border:`1px solid ${isOverridden ? "var(--accent)" : "var(--line)"}`,
                  borderRadius:4, color: isOverridden ? "var(--accent)" : "var(--text)", fontFamily:"var(--font-mono)",
                  padding:"3px 6px", fontSize:11, outline:"none" }}/>
              <span style={{ fontSize:10, fontFamily:"var(--font-mono)", color:"var(--text-faint)", width:28 }}>{fmtFn(cur)}</span>
              {isOverridden && (
                <button title="Reset to default" onClick={() => {
                  const next = { ...wo }; delete next[key];
                  set({ weight_overrides: next });
                }} style={{ fontSize:10, background:"none", border:"none", cursor:"pointer", color:"var(--text-faint)", padding:0 }}>↺</button>
              )}
            </div>
          );
        })}
        <div style={{ fontSize:9, color:"var(--text-faint)", fontFamily:"var(--font-mono)", marginTop:4 }}>
          Blue border = overriding default · ↺ resets to default
        </div>
      </div>

      <div style={{ fontSize:10, fontFamily:"var(--font-mono)", color:"var(--text-faint)", marginTop:14, paddingTop:10, borderTop:"1px solid var(--line)" }}>
        All settings apply immediately. Rules are local — they filter your feed view only.
      </div>
    </div>
  );
}
