"""
Sector relative strength: compare ticker vs its SPDR sector ETF (1-month).
"""
import asyncio
import time as _time
from typing import Optional

import pandas as pd

from services.market_data import get_history

# Ticker → SPDR sector ETF — top 50+ per sector by market cap
SECTOR_MAP: dict[str, str] = {
    # ── Technology (XLK) — 65 stocks ─────────────────────────────────────────
    "AAPL":"XLK","MSFT":"XLK","NVDA":"XLK","AVGO":"XLK","ASML":"XLK",
    "TSM":"XLK","ORCL":"XLK","CRM":"XLK","AMD":"XLK","QCOM":"XLK",
    "TXN":"XLK","ARM":"XLK","INTC":"XLK","AMAT":"XLK","MU":"XLK",
    "MU":"XLK","CSCO":"XLK","NOW":"XLK","INTU":"XLK","ADBE":"XLK",
    "KLAC":"XLK","LRCX":"XLK","ADI":"XLK","SNPS":"XLK","CDNS":"XLK",
    "PANW":"XLK","CRWD":"XLK","ACN":"XLK","MRVL":"XLK","PLTR":"XLK",
    "FTNT":"XLK","NET":"XLK","ZS":"XLK","DELL":"XLK","HPQ":"XLK",
    "HPE":"XLK","STX":"XLK","WDC":"XLK","NTAP":"XLK","CTSH":"XLK",
    "IT":"XLK","ANET":"XLK","KEYS":"XLK","DDOG":"XLK","SNOW":"XLK",
    "SMCI":"XLK","TEAM":"XLK","ADSK":"XLK","ANSS":"XLK","IBM":"XLK",
    "VEEV":"XLK","OKTA":"XLK","TWLO":"XLK","DOCU":"XLK","ZM":"XLK",
    "SHOP":"XLK","SQ":"XLK","PYPL":"XLK","COIN":"XLK","MSTR":"XLK",
    "HOOD":"XLK","GLW":"XLK","JNPR":"XLK","FFIV":"XLK","AKAM":"XLK",
    "VRSK":"XLK","EPAM":"XLK","FSLR":"XLK","ENPH":"XLK","SEDG":"XLK",
    "TQQQ":"XLK","QQQ":"XLK","SSNLF":"XLK","PSTG":"XLK","HUBS":"XLK",
    "APP":"XLK","WDAY":"XLK","TTD":"XLK",  # ad-tech / enterprise SaaS
    # Tech/Nasdaq leveraged — tracks QQQ/XLK/SOX
    "SQQQ":"XLK","UPRO":"XLK","SPXL":"XLK","SPXS":"XLK","SPXU":"XLK",
    "SOXL":"XLK","SOXS":"XLK","TECL":"XLK","TECS":"XLK",
    "WEBL":"XLK","FNGU":"XLK","FNGD":"XLK",
    "SSO":"XLK","SDS":"XLK","QLD":"XLK","QID":"XLK","ROM":"XLK","REW":"XLK",
    # ── Communication Services (XLC) — 52 stocks ─────────────────────────────
    "GOOGL":"XLC","GOOG":"XLC","META":"XLC","NFLX":"XLC","DIS":"XLC",
    "CMCSA":"XLC","T":"XLC","VZ":"XLC","TMUS":"XLC","CHTR":"XLC",
    "SPOT":"XLC","RBLX":"XLC","EA":"XLC","TTWO":"XLC","WBD":"XLC",
    "PARA":"XLC","FOXA":"XLC","FOX":"XLC","NWSA":"XLC","NWS":"XLC",
    "OMC":"XLC","IPG":"XLC","SNAP":"XLC","PINS":"XLC","MTCH":"XLC",
    "BIDU":"XLC","NTES":"XLC","SIRI":"XLC","LBRDK":"XLC","LYV":"XLC",
    "NYT":"XLC","ZG":"XLC","Z":"XLC","DISH":"XLC","LUMN":"XLC",
    "AMC":"XLC","TME":"XLC","BILI":"XLC","HUYA":"XLC","IQ":"XLC",
    "GRAB":"XLC","SE":"XLC","YY":"XLC","MOMO":"XLC","IAC":"XLC",
    "IACI":"XLC","ANGI":"XLC","YELP":"XLC","CARS":"XLC","FWONA":"XLC",
    "FWONK":"XLC","SBGI":"XLC",
    # ── Consumer Discretionary (XLY) — 65 stocks ─────────────────────────────
    "AMZN":"XLY","TSLA":"XLY","HD":"XLY","LOW":"XLY","MCD":"XLY",
    "SBUX":"XLY","NKE":"XLY","TJX":"XLY","BKNG":"XLY","MAR":"XLY",
    "HLT":"XLY","GM":"XLY","F":"XLY","RIVN":"XLY","LCID":"XLY",
    "CMG":"XLY","YUM":"XLY","DRI":"XLY","QSR":"XLY","WYNN":"XLY",
    "MGM":"XLY","CZR":"XLY","LVS":"XLY","ABNB":"XLY","UBER":"XLY",
    "LYFT":"XLY","DASH":"XLY","ETSY":"XLY","EBAY":"XLY","W":"XLY",
    "RH":"XLY","WSM":"XLY","BBY":"XLY","KMX":"XLY","AN":"XLY",
    "AZO":"XLY","ORLY":"XLY","BURL":"XLY","ROST":"XLY","LULU":"XLY",
    "DECK":"XLY","VFC":"XLY","PVH":"XLY","HBI":"XLY","RL":"XLY",
    "TPR":"XLY","CPRI":"XLY","UAA":"XLY","PHM":"XLY","DHI":"XLY",
    "LEN":"XLY","TOL":"XLY","NVR":"XLY","POOL":"XLY","EXPE":"XLY",
    "TRIP":"XLY","HGV":"XLY","TNL":"XLY","PENN":"XLY","DKNG":"XLY",
    "RCL":"XLY","CCL":"XLY","NCLH":"XLY","VAC":"XLY","CNK":"XLY",
    "SEAS":"XLY","SIX":"XLY","BLMN":"XLY","TXRH":"XLY","PLAY":"XLY",
    # ── Consumer Staples (XLP) — 55 stocks ───────────────────────────────────
    "WMT":"XLP","COST":"XLP","PG":"XLP","KO":"XLP","PEP":"XLP",
    "MO":"XLP","PM":"XLP","MDLZ":"XLP","GIS":"XLP","K":"XLP",
    "CPB":"XLP","HRL":"XLP","SJM":"XLP","MKC":"XLP","CLX":"XLP",
    "CL":"XLP","KHC":"XLP","HSY":"XLP","MNST":"XLP","STZ":"XLP",
    "BF-B":"XLP","TAP":"XLP","EL":"XLP","CHD":"XLP","KMB":"XLP",
    "SYY":"XLP","CASY":"XLP","KR":"XLP","SFM":"XLP","GO":"XLP",
    "ACI":"XLP","CAG":"XLP","LW":"XLP","INGR":"XLP","POST":"XLP",
    "TSN":"XLP","PPC":"XLP","JJSF":"XLP","LANC":"XLP","UTZ":"XLP",
    "NOMD":"XLP","SMPL":"XLP","FRPT":"XLP","VITL":"XLP","PSMT":"XLP",
    "WBA":"XLP","DG":"XLP","DLTR":"XLP","CVS":"XLP","TGT":"XLP",
    "PMTS":"XLP","SENEA":"XLP","CELH":"XLP","HAIN":"XLP","SPTN":"XLP",
    # ── Healthcare (XLV) — 62 stocks ─────────────────────────────────────────
    "LLY":"XLV","UNH":"XLV","JNJ":"XLV","ABBV":"XLV","MRK":"XLV",
    "PFE":"XLV","TMO":"XLV","ABT":"XLV","MDT":"XLV","BMY":"XLV",
    "AMGN":"XLV","GILD":"XLV","ISRG":"XLV","BSX":"XLV","SYK":"XLV",
    "EW":"XLV","ZBH":"XLV","BDX":"XLV","BAX":"XLV","IQV":"XLV",
    "VRTX":"XLV","REGN":"XLV","BIIB":"XLV","MRNA":"XLV","BNTX":"XLV",
    "CI":"XLV","HUM":"XLV","MOH":"XLV","CNC":"XLV","HCA":"XLV",
    "THC":"XLV","DGX":"XLV","LH":"XLV","IDXX":"XLV","ZTS":"XLV",
    "PODD":"XLV","DXCM":"XLV","ALGN":"XLV","HOLX":"XLV","TFX":"XLV",
    "GEHC":"XLV","RGEN":"XLV","SRPT":"XLV","ALNY":"XLV","EXEL":"XLV",
    "RMD":"XLV","NVCR":"XLV","MASI":"XLV","HSIC":"XLV","PDCO":"XLV",
    "INCY":"XLV","HALO":"XLV","JAZZ":"XLV","IOVA":"XLV","NKTR":"XLV",
    "ARVN":"XLV","BEAM":"XLV","CRSP":"XLV","NTLA":"XLV","EDIT":"XLV",
    "BLUE":"XLV","FATE":"XLV","RARE":"XLV","RCKT":"XLV","VKTX":"XLV",
    # Healthcare/biotech leveraged
    "LABU":"XLV","LABD":"XLV",
    # ── Financials (XLF) — 68 stocks ─────────────────────────────────────────
    "JPM":"XLF","BAC":"XLF","WFC":"XLF","GS":"XLF","MS":"XLF",
    "C":"XLF","BLK":"XLF","BK":"XLF","STT":"XLF","SCHW":"XLF",
    "AXP":"XLF","V":"XLF","MA":"XLF","COF":"XLF","DFS":"XLF",
    "SYF":"XLF","AIG":"XLF","MET":"XLF","PRU":"XLF","AFL":"XLF",
    "TRV":"XLF","HIG":"XLF","CB":"XLF","ALL":"XLF","PGR":"XLF",
    "CINF":"XLF","BRK-B":"XLF","ICE":"XLF","CME":"XLF","NDAQ":"XLF",
    "CBOE":"XLF","SPGI":"XLF","MCO":"XLF","MSCI":"XLF","FDS":"XLF",
    "USB":"XLF","PNC":"XLF","TFC":"XLF","KEY":"XLF","RF":"XLF",
    "HBAN":"XLF","CFG":"XLF","MTB":"XLF","FITB":"XLF","ZION":"XLF",
    "CMA":"XLF","WBS":"XLF","FHN":"XLF","SNV":"XLF","ALLY":"XLF",
    "SLM":"XLF","SOFI":"XLF","LC":"XLF","AFRM":"XLF","UPST":"XLF",
    "NU":"XLF","MELI":"XLF","PAGS":"XLF","STNE":"XLF","BR":"XLF",
    "FI":"XLF","FIS":"XLF","FISV":"XLF","GPN":"XLF","WEX":"XLF",
    "FOUR":"XLF","EVTC":"XLF","RJF":"XLF","LPLA":"XLF","SF":"XLF",
    "EVR":"XLF","HLI":"XLF","JEF":"XLF","LAZ":"XLF","MC":"XLF",
    # Financials leveraged
    "FAS":"XLF","FAZ":"XLF","DPST":"XLF",
    # Small-cap leveraged (IWM proxy — map to XLI as closest sector)
    "TNA":"XLI","TZA":"XLI","UWM":"XLI","TWM":"XLI","SRTY":"XLI","MIDU":"XLI",
    # Broad-market leveraged (S&P 500 proxies — map to SPY universe via XLK as lead sector)
    "UPRO":"XLK","SPXL":"XLK","SPXS":"XLK","SPXU":"XLK","SSO":"XLK","SDS":"XLK",
    "HIBL":"XLK","HIBS":"XLK","NAIL":"XLI",
    # ── Energy (XLE) — 55 stocks ─────────────────────────────────────────────
    "XOM":"XLE","CVX":"XLE","COP":"XLE","EOG":"XLE","SLB":"XLE",
    "PSX":"XLE","MPC":"XLE","VLO":"XLE","OXY":"XLE","DVN":"XLE",
    "FANG":"XLE","MRO":"XLE","APA":"XLE","HAL":"XLE","BKR":"XLE",
    "NOV":"XLE","CTRA":"XLE","SM":"XLE","MTDR":"XLE","RRC":"XLE",
    "EQT":"XLE","AR":"XLE","OVV":"XLE","CNX":"XLE","SWN":"XLE",
    "KMI":"XLE","WMB":"XLE","OKE":"XLE","LNG":"XLE","CQP":"XLE",
    "TRGP":"XLE","ENB":"XLE","TRP":"XLE","CVE":"XLE","SU":"XLE",
    "IMO":"XLE","CNQ":"XLE","BTU":"XLE","ARCH":"XLE","AMR":"XLE",
    "CEIX":"XLE","ET":"XLE","EPD":"XLE","MPLX":"XLE","PAA":"XLE",
    "PAGP":"XLE","NS":"XLE","DKL":"XLE","CAPL":"XLE","HES":"XLE",
    "CPE":"XLE","PR":"XLE","MTUS":"XLE","PTEN":"XLE","HP":"XLE",
    # Energy leveraged
    "GUSH":"XLE","DRIP":"XLE","UCO":"XLE","SCO":"XLE",
    # ── Industrials (XLI) — 65 stocks ────────────────────────────────────────
    "GE":"XLI","HON":"XLI","MMM":"XLI","CAT":"XLI","DE":"XLI",
    "RTX":"XLI","LMT":"XLI","NOC":"XLI","GD":"XLI","BA":"XLI",
    "UPS":"XLI","FDX":"XLI","UNP":"XLI","CSX":"XLI","NSC":"XLI",
    "DAL":"XLI","UAL":"XLI","AAL":"XLI","LUV":"XLI","ALK":"XLI",
    "JBLU":"XLI","EXPD":"XLI","CHRW":"XLI","XPO":"XLI","KNX":"XLI",
    "ODFL":"XLI","SAIA":"XLI","WERN":"XLI","EMR":"XLI","ETN":"XLI",
    "PH":"XLI","ITW":"XLI","IR":"XLI","OTIS":"XLI","CARR":"XLI",
    "JCI":"XLI","AME":"XLI","CTAS":"XLI","RSG":"XLI","WM":"XLI",
    "GFL":"XLI","CWST":"XLI","URI":"XLI","FAST":"XLI","GWW":"XLI",
    "AXON":"XLI","LDOS":"XLI","LHX":"XLI","KTOS":"XLI","TDG":"XLI",
    "HWM":"XLI","TXT":"XLI","HII":"XLI","MOOG":"XLI","CPRT":"XLI",
    "TREX":"XLI","AYI":"XLI","FLS":"XLI","GTLS":"XLI","GNRC":"XLI",
    "XYL":"XLI","TRMB":"XLI","AGCO":"XLI","CNH":"XLI","ITT":"XLI",
    "RRX":"XLI","BAH":"XLI","SAIC":"XLI","MRCY":"XLI","BWXT":"XLI",
    # ── Materials (XLB) — 55 stocks ──────────────────────────────────────────
    "APD":"XLB","LIN":"XLB","SHW":"XLB","NEM":"XLB","FCX":"XLB",
    "NUE":"XLB","STLD":"XLB","CLF":"XLB","X":"XLB","CMC":"XLB",
    "AA":"XLB","ALB":"XLB","CE":"XLB","DD":"XLB","DOW":"XLB",
    "LYB":"XLB","PPG":"XLB","RPM":"XLB","IFF":"XLB","ECL":"XLB",
    "EMN":"XLB","MOS":"XLB","CF":"XLB","NTR":"XLB","CTVA":"XLB",
    "FMC":"XLB","IP":"XLB","PKG":"XLB","WRK":"XLB","SEE":"XLB",
    "AMCR":"XLB","BLL":"XLB","AVY":"XLB","BG":"XLB","ADM":"XLB",
    "GOLD":"XLB","AEM":"XLB","WPM":"XLB","KGC":"XLB","AG":"XLB",
    "CDE":"XLB","HL":"XLB","PAAS":"XLB","MAG":"XLB","SA":"XLB",
    "EQX":"XLB","OR":"XLB","RGLD":"XLB","SCCO":"XLB","TECK":"XLB",
    "MT":"XLB","VALE":"XLB","RIO":"XLB","BHP":"XLB","ATI":"XLB",
    # Gold miners leveraged (GDX/GDXJ proxies)
    "NUGT":"XLB","DUST":"XLB","JNUG":"XLB","JDST":"XLB",
    # ── Real Estate (XLRE) — 55 stocks ───────────────────────────────────────
    "AMT":"XLRE","PLD":"XLRE","EQIX":"XLRE","CCI":"XLRE","PSA":"XLRE",
    "DLR":"XLRE","WELL":"XLRE","VTR":"XLRE","O":"XLRE","NNN":"XLRE",
    "WPC":"XLRE","SPG":"XLRE","MAC":"XLRE","SKT":"XLRE","BXP":"XLRE",
    "SLG":"XLRE","VNO":"XLRE","EQR":"XLRE","AVB":"XLRE","ESS":"XLRE",
    "MAA":"XLRE","CPT":"XLRE","UDR":"XLRE","NLY":"XLRE","AGNC":"XLRE",
    "TWO":"XLRE","PMT":"XLRE","SBAC":"XLRE","IRM":"XLRE","CBRE":"XLRE",
    "JLL":"XLRE","CSGP":"XLRE","Z":"XLRE","ARE":"XLRE","PEAK":"XLRE",
    "HR":"XLRE","INVH":"XLRE","AMH":"XLRE","NHI":"XLRE","STAG":"XLRE",
    "COLD":"XLRE","IIPR":"XLRE","MPW":"XLRE","OHI":"XLRE","LTC":"XLRE",
    "HTA":"XLRE","SITC":"XLRE","REG":"XLRE","KIM":"XLRE","TRNO":"XLRE",
    "REXR":"XLRE","ELS":"XLRE","SUI":"XLRE","ADC":"XLRE","EPRT":"XLRE",
    # Real estate leveraged
    "DRN":"XLRE","DRV":"XLRE",
    # China leveraged (no direct sector ETF — use XLC as closest)
    "YINN":"XLC","YANG":"XLC",
    # Treasury leveraged (bond proxies — use XLU as most rate-sensitive)
    "TMF":"XLU","TMV":"XLU",
    # ── Utilities (XLU) — 55 stocks ──────────────────────────────────────────
    "NEE":"XLU","DUK":"XLU","SO":"XLU","D":"XLU","AEP":"XLU",
    "EXC":"XLU","SRE":"XLU","PCG":"XLU","ED":"XLU","XEL":"XLU",
    "ES":"XLU","PPL":"XLU","FE":"XLU","AES":"XLU","ETR":"XLU",
    "CNP":"XLU","WEC":"XLU","CMS":"XLU","NI":"XLU","AWK":"XLU",
    "AWR":"XLU","SWX":"XLU","SR":"XLU","PNW":"XLU","EVRG":"XLU",
    "NWE":"XLU","BKH":"XLU","OGE":"XLU","ATO":"XLU","LNT":"XLU",
    "MGEE":"XLU","OTTR":"XLU","POR":"XLU","AVA":"XLU","IDA":"XLU",
    "EE":"XLU","AEE":"XLU","DTE":"XLU","NRG":"XLU","VST":"XLU",
    "CWEN":"XLU","BEP":"XLU","NEP":"XLU","ARRY":"XLU","NOVA":"XLU",
    "PLUG":"XLU","FCEL":"XLU","BLDP":"XLU","BE":"XLU","RUN":"XLU",
    "MAXN":"XLU","SPWR":"XLU","SHLS":"XLU","HASI":"XLU","AY":"XLU",
}

# yfinance sector name → SPDR ETF
YFINANCE_TO_ETF: dict[str, str] = {
    "Technology": "XLK", "Information Technology": "XLK",
    "Financial Services": "XLF", "Financials": "XLF",
    "Consumer Cyclical": "XLY", "Consumer Discretionary": "XLY",
    "Communication Services": "XLC",
    "Healthcare": "XLV", "Health Care": "XLV",
    "Consumer Defensive": "XLP", "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Basic Materials": "XLB", "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
}

_etf_cache: dict[str, tuple[pd.DataFrame, float]] = {}
CACHE_TTL = 3600 * 4  # 4 hours


async def get_sector_relative_strength(
    ticker: str,
    ticker_df: Optional[pd.DataFrame] = None,
    lookback: int = 21,
) -> Optional[dict]:
    """
    Returns:
      sector_etf    : str   — e.g. "XLK"
      sector_1m_ret : float — sector ETF 1-month % return
      rs_vs_sector  : float — ticker 1m return minus sector 1m return
    Returns None if the ticker isn't in SECTOR_MAP or data is unavailable.
    """
    etf = SECTOR_MAP.get(ticker.upper())
    if not etf:
        return None

    try:
        # ── Sector ETF data ────────────────────────────────────────────
        cached = _etf_cache.get(etf)
        if cached and _time.time() - cached[1] < CACHE_TTL:
            etf_df = cached[0]
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (
            float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1
        ) * 100

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (
            float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1
        ) * 100

        return {
            "sector_etf":    etf,
            "sector_1m_ret": round(etf_1m, 2),
            "rs_vs_sector":  round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None
