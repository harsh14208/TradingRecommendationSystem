"""
Sector relative strength: compare ticker vs its SPDR sector ETF (1-month).
"""

import time as _time
from typing import Optional

import pandas as pd

from services.market_data import get_history

# Ticker → SPDR sector ETF — top 50+ per sector by market cap
SECTOR_MAP: dict[str, str] = {
    # ── Technology (XLK) — 65 stocks ─────────────────────────────────────────
    "AAPL": "XLK",
    "MSFT": "XLK",
    "NVDA": "XLK",
    "AVGO": "XLK",
    "ASML": "XLK",
    "TSM": "XLK",
    "ORCL": "XLK",
    "CRM": "XLK",
    "AMD": "XLK",
    "QCOM": "XLK",
    "TXN": "XLK",
    "ARM": "XLK",
    "INTC": "XLK",
    "AMAT": "XLK",
    "MU": "XLK",
    "CSCO": "XLK",
    "NOW": "XLK",
    "INTU": "XLK",
    "ADBE": "XLK",
    "KLAC": "XLK",
    "LRCX": "XLK",
    "ADI": "XLK",
    "SNPS": "XLK",
    "CDNS": "XLK",
    "PANW": "XLK",
    "CRWD": "XLK",
    "ACN": "XLK",
    "MRVL": "XLK",
    "PLTR": "XLK",
    "FTNT": "XLK",
    "NET": "XLK",
    "ZS": "XLK",
    "DELL": "XLK",
    "HPQ": "XLK",
    "HPE": "XLK",
    "STX": "XLK",
    "WDC": "XLK",
    "NTAP": "XLK",
    "CTSH": "XLK",
    "IT": "XLK",
    "ANET": "XLK",
    "KEYS": "XLK",
    "DDOG": "XLK",
    "SNOW": "XLK",
    "SMCI": "XLK",
    "TEAM": "XLK",
    "ADSK": "XLK",
    "ANSS": "XLK",
    "IBM": "XLK",
    "VEEV": "XLK",
    "OKTA": "XLK",
    "TWLO": "XLK",
    "DOCU": "XLK",
    "ZM": "XLK",
    "SHOP": "XLK",
    "SQ": "XLK",
    "PYPL": "XLK",
    "COIN": "XLK",
    "MSTR": "XLK",
    "HOOD": "XLK",
    "GLW": "XLK",
    "JNPR": "XLK",
    "FFIV": "XLK",
    "AKAM": "XLK",
    "VRSK": "XLK",
    "EPAM": "XLK",
    "FSLR": "XLK",
    "ENPH": "XLK",
    "SEDG": "XLK",
    "TQQQ": "XLK",
    "QQQ": "XLK",
    "SSNLF": "XLK",
    "PSTG": "XLK",
    "HUBS": "XLK",
    "APP": "XLK",
    "WDAY": "XLK",
    "TTD": "XLK",  # ad-tech / enterprise SaaS
    # Tech/Nasdaq leveraged — tracks QQQ/XLK/SOX
    "SQQQ": "XLK",
    "UPRO": "XLK",
    "SPXL": "XLK",
    "SPXS": "XLK",
    "SPXU": "XLK",
    "SOXL": "XLK",
    "SOXS": "XLK",
    "TECL": "XLK",
    "TECS": "XLK",
    "WEBL": "XLK",
    "FNGU": "XLK",
    "FNGD": "XLK",
    "SSO": "XLK",
    "SDS": "XLK",
    "QLD": "XLK",
    "QID": "XLK",
    "ROM": "XLK",
    "REW": "XLK",
    # ── Communication Services (XLC) — 52 stocks ─────────────────────────────
    "GOOGL": "XLC",
    "GOOG": "XLC",
    "META": "XLC",
    "NFLX": "XLC",
    "DIS": "XLC",
    "CMCSA": "XLC",
    "T": "XLC",
    "VZ": "XLC",
    "TMUS": "XLC",
    "CHTR": "XLC",
    "SPOT": "XLC",
    "RBLX": "XLC",
    "EA": "XLC",
    "TTWO": "XLC",
    "WBD": "XLC",
    "PARA": "XLC",
    "FOXA": "XLC",
    "FOX": "XLC",
    "NWSA": "XLC",
    "NWS": "XLC",
    "OMC": "XLC",
    "IPG": "XLC",
    "SNAP": "XLC",
    "PINS": "XLC",
    "MTCH": "XLC",
    "BIDU": "XLC",
    "NTES": "XLC",
    "SIRI": "XLC",
    "LBRDK": "XLC",
    "LYV": "XLC",
    "NYT": "XLC",
    "ZG": "XLC",
    "DISH": "XLC",
    "LUMN": "XLC",
    "AMC": "XLC",
    "TME": "XLC",
    "BILI": "XLC",
    "HUYA": "XLC",
    "IQ": "XLC",
    "GRAB": "XLC",
    "SE": "XLC",
    "YY": "XLC",
    "MOMO": "XLC",
    "IAC": "XLC",
    "IACI": "XLC",
    "ANGI": "XLC",
    "YELP": "XLC",
    "CARS": "XLC",
    "FWONA": "XLC",
    "FWONK": "XLC",
    "SBGI": "XLC",
    # ── Consumer Discretionary (XLY) — 65 stocks ─────────────────────────────
    "AMZN": "XLY",
    "TSLA": "XLY",
    "HD": "XLY",
    "LOW": "XLY",
    "MCD": "XLY",
    "SBUX": "XLY",
    "NKE": "XLY",
    "TJX": "XLY",
    "BKNG": "XLY",
    "MAR": "XLY",
    "HLT": "XLY",
    "GM": "XLY",
    "F": "XLY",
    "RIVN": "XLY",
    "LCID": "XLY",
    "CMG": "XLY",
    "YUM": "XLY",
    "DRI": "XLY",
    "QSR": "XLY",
    "WYNN": "XLY",
    "MGM": "XLY",
    "CZR": "XLY",
    "LVS": "XLY",
    "ABNB": "XLY",
    "UBER": "XLY",
    "LYFT": "XLY",
    "DASH": "XLY",
    "ETSY": "XLY",
    "EBAY": "XLY",
    "W": "XLY",
    "RH": "XLY",
    "WSM": "XLY",
    "BBY": "XLY",
    "KMX": "XLY",
    "AN": "XLY",
    "AZO": "XLY",
    "ORLY": "XLY",
    "BURL": "XLY",
    "ROST": "XLY",
    "LULU": "XLY",
    "DECK": "XLY",
    "VFC": "XLY",
    "PVH": "XLY",
    "HBI": "XLY",
    "RL": "XLY",
    "TPR": "XLY",
    "CPRI": "XLY",
    "UAA": "XLY",
    "PHM": "XLY",
    "DHI": "XLY",
    "LEN": "XLY",
    "TOL": "XLY",
    "NVR": "XLY",
    "POOL": "XLY",
    "EXPE": "XLY",
    "TRIP": "XLY",
    "HGV": "XLY",
    "TNL": "XLY",
    "PENN": "XLY",
    "DKNG": "XLY",
    "RCL": "XLY",
    "CCL": "XLY",
    "NCLH": "XLY",
    "VAC": "XLY",
    "CNK": "XLY",
    "SEAS": "XLY",
    "SIX": "XLY",
    "BLMN": "XLY",
    "TXRH": "XLY",
    "PLAY": "XLY",
    # ── Consumer Staples (XLP) — 55 stocks ───────────────────────────────────
    "WMT": "XLP",
    "COST": "XLP",
    "PG": "XLP",
    "KO": "XLP",
    "PEP": "XLP",
    "MO": "XLP",
    "PM": "XLP",
    "MDLZ": "XLP",
    "GIS": "XLP",
    "K": "XLP",
    "CPB": "XLP",
    "HRL": "XLP",
    "SJM": "XLP",
    "MKC": "XLP",
    "CLX": "XLP",
    "CL": "XLP",
    "KHC": "XLP",
    "HSY": "XLP",
    "MNST": "XLP",
    "STZ": "XLP",
    "BF-B": "XLP",
    "TAP": "XLP",
    "EL": "XLP",
    "CHD": "XLP",
    "KMB": "XLP",
    "SYY": "XLP",
    "CASY": "XLP",
    "KR": "XLP",
    "SFM": "XLP",
    "GO": "XLP",
    "ACI": "XLP",
    "CAG": "XLP",
    "LW": "XLP",
    "INGR": "XLP",
    "POST": "XLP",
    "TSN": "XLP",
    "PPC": "XLP",
    "JJSF": "XLP",
    "LANC": "XLP",
    "UTZ": "XLP",
    "NOMD": "XLP",
    "SMPL": "XLP",
    "FRPT": "XLP",
    "VITL": "XLP",
    "PSMT": "XLP",
    "WBA": "XLP",
    "DG": "XLP",
    "DLTR": "XLP",
    "CVS": "XLP",
    "TGT": "XLP",
    "PMTS": "XLP",
    "SENEA": "XLP",
    "CELH": "XLP",
    "HAIN": "XLP",
    "SPTN": "XLP",
    # ── Healthcare (XLV) — 62 stocks ─────────────────────────────────────────
    "LLY": "XLV",
    "UNH": "XLV",
    "JNJ": "XLV",
    "ABBV": "XLV",
    "MRK": "XLV",
    "PFE": "XLV",
    "TMO": "XLV",
    "ABT": "XLV",
    "MDT": "XLV",
    "BMY": "XLV",
    "AMGN": "XLV",
    "GILD": "XLV",
    "ISRG": "XLV",
    "BSX": "XLV",
    "SYK": "XLV",
    "EW": "XLV",
    "ZBH": "XLV",
    "BDX": "XLV",
    "BAX": "XLV",
    "IQV": "XLV",
    "VRTX": "XLV",
    "REGN": "XLV",
    "BIIB": "XLV",
    "MRNA": "XLV",
    "BNTX": "XLV",
    "CI": "XLV",
    "HUM": "XLV",
    "MOH": "XLV",
    "CNC": "XLV",
    "HCA": "XLV",
    "THC": "XLV",
    "DGX": "XLV",
    "LH": "XLV",
    "IDXX": "XLV",
    "ZTS": "XLV",
    "PODD": "XLV",
    "DXCM": "XLV",
    "ALGN": "XLV",
    "HOLX": "XLV",
    "TFX": "XLV",
    "GEHC": "XLV",
    "RGEN": "XLV",
    "SRPT": "XLV",
    "ALNY": "XLV",
    "EXEL": "XLV",
    "RMD": "XLV",
    "NVCR": "XLV",
    "MASI": "XLV",
    "HSIC": "XLV",
    "PDCO": "XLV",
    "INCY": "XLV",
    "HALO": "XLV",
    "JAZZ": "XLV",
    "IOVA": "XLV",
    "NKTR": "XLV",
    "ARVN": "XLV",
    "BEAM": "XLV",
    "CRSP": "XLV",
    "NTLA": "XLV",
    "EDIT": "XLV",
    "BLUE": "XLV",
    "FATE": "XLV",
    "RARE": "XLV",
    "RCKT": "XLV",
    "VKTX": "XLV",
    # Healthcare/biotech leveraged
    "LABU": "XLV",
    "LABD": "XLV",
    # ── Financials (XLF) — 68 stocks ─────────────────────────────────────────
    "JPM": "XLF",
    "BAC": "XLF",
    "WFC": "XLF",
    "GS": "XLF",
    "MS": "XLF",
    "C": "XLF",
    "BLK": "XLF",
    "BK": "XLF",
    "STT": "XLF",
    "SCHW": "XLF",
    "AXP": "XLF",
    "V": "XLF",
    "MA": "XLF",
    "COF": "XLF",
    "DFS": "XLF",
    "SYF": "XLF",
    "AIG": "XLF",
    "MET": "XLF",
    "PRU": "XLF",
    "AFL": "XLF",
    "TRV": "XLF",
    "HIG": "XLF",
    "CB": "XLF",
    "ALL": "XLF",
    "PGR": "XLF",
    "CINF": "XLF",
    "BRK-B": "XLF",
    "ICE": "XLF",
    "CME": "XLF",
    "NDAQ": "XLF",
    "CBOE": "XLF",
    "SPGI": "XLF",
    "MCO": "XLF",
    "MSCI": "XLF",
    "FDS": "XLF",
    "USB": "XLF",
    "PNC": "XLF",
    "TFC": "XLF",
    "KEY": "XLF",
    "RF": "XLF",
    "HBAN": "XLF",
    "CFG": "XLF",
    "MTB": "XLF",
    "FITB": "XLF",
    "ZION": "XLF",
    "CMA": "XLF",
    "WBS": "XLF",
    "FHN": "XLF",
    "SNV": "XLF",
    "ALLY": "XLF",
    "SLM": "XLF",
    "SOFI": "XLF",
    "LC": "XLF",
    "AFRM": "XLF",
    "UPST": "XLF",
    "NU": "XLF",
    "MELI": "XLF",
    "PAGS": "XLF",
    "STNE": "XLF",
    "BR": "XLF",
    "FI": "XLF",
    "FIS": "XLF",
    "FISV": "XLF",
    "GPN": "XLF",
    "WEX": "XLF",
    "FOUR": "XLF",
    "EVTC": "XLF",
    "RJF": "XLF",
    "LPLA": "XLF",
    "SF": "XLF",
    "EVR": "XLF",
    "HLI": "XLF",
    "JEF": "XLF",
    "LAZ": "XLF",
    "MC": "XLF",
    # Financials leveraged
    "FAS": "XLF",
    "FAZ": "XLF",
    "DPST": "XLF",
    # Small-cap leveraged (IWM proxy — map to XLI as closest sector)
    "TNA": "XLI",
    "TZA": "XLI",
    "UWM": "XLI",
    "TWM": "XLI",
    "SRTY": "XLI",
    "MIDU": "XLI",
    "HIBL": "XLK",
    "HIBS": "XLK",
    "NAIL": "XLI",
    # ── Energy (XLE) — 55 stocks ─────────────────────────────────────────────
    "XOM": "XLE",
    "CVX": "XLE",
    "COP": "XLE",
    "EOG": "XLE",
    "SLB": "XLE",
    "PSX": "XLE",
    "MPC": "XLE",
    "VLO": "XLE",
    "OXY": "XLE",
    "DVN": "XLE",
    "FANG": "XLE",
    "MRO": "XLE",
    "APA": "XLE",
    "HAL": "XLE",
    "BKR": "XLE",
    "NOV": "XLE",
    "CTRA": "XLE",
    "SM": "XLE",
    "MTDR": "XLE",
    "RRC": "XLE",
    "EQT": "XLE",
    "AR": "XLE",
    "OVV": "XLE",
    "CNX": "XLE",
    "SWN": "XLE",
    "KMI": "XLE",
    "WMB": "XLE",
    "OKE": "XLE",
    "LNG": "XLE",
    "CQP": "XLE",
    "TRGP": "XLE",
    "ENB": "XLE",
    "TRP": "XLE",
    "CVE": "XLE",
    "SU": "XLE",
    "IMO": "XLE",
    "CNQ": "XLE",
    "BTU": "XLE",
    "ARCH": "XLE",
    "AMR": "XLE",
    "CEIX": "XLE",
    "ET": "XLE",
    "EPD": "XLE",
    "MPLX": "XLE",
    "PAA": "XLE",
    "PAGP": "XLE",
    "NS": "XLE",
    "DKL": "XLE",
    "CAPL": "XLE",
    "HES": "XLE",
    "CPE": "XLE",
    "PR": "XLE",
    "MTUS": "XLE",
    "PTEN": "XLE",
    "HP": "XLE",
    # Energy leveraged
    "GUSH": "XLE",
    "DRIP": "XLE",
    "UCO": "XLE",
    "SCO": "XLE",
    # ── Industrials (XLI) — 65 stocks ────────────────────────────────────────
    "GE": "XLI",
    "HON": "XLI",
    "MMM": "XLI",
    "CAT": "XLI",
    "DE": "XLI",
    "RTX": "XLI",
    "LMT": "XLI",
    "NOC": "XLI",
    "GD": "XLI",
    "BA": "XLI",
    "UPS": "XLI",
    "FDX": "XLI",
    "UNP": "XLI",
    "CSX": "XLI",
    "NSC": "XLI",
    "DAL": "XLI",
    "UAL": "XLI",
    "AAL": "XLI",
    "LUV": "XLI",
    "ALK": "XLI",
    "JBLU": "XLI",
    "EXPD": "XLI",
    "CHRW": "XLI",
    "XPO": "XLI",
    "KNX": "XLI",
    "ODFL": "XLI",
    "SAIA": "XLI",
    "WERN": "XLI",
    "EMR": "XLI",
    "ETN": "XLI",
    "PH": "XLI",
    "ITW": "XLI",
    "IR": "XLI",
    "OTIS": "XLI",
    "CARR": "XLI",
    "JCI": "XLI",
    "AME": "XLI",
    "CTAS": "XLI",
    "RSG": "XLI",
    "WM": "XLI",
    "GFL": "XLI",
    "CWST": "XLI",
    "URI": "XLI",
    "FAST": "XLI",
    "GWW": "XLI",
    "AXON": "XLI",
    "LDOS": "XLI",
    "LHX": "XLI",
    "KTOS": "XLI",
    "TDG": "XLI",
    "HWM": "XLI",
    "TXT": "XLI",
    "HII": "XLI",
    "MOOG": "XLI",
    "CPRT": "XLI",
    "TREX": "XLI",
    "AYI": "XLI",
    "FLS": "XLI",
    "GTLS": "XLI",
    "GNRC": "XLI",
    "XYL": "XLI",
    "TRMB": "XLI",
    "AGCO": "XLI",
    "CNH": "XLI",
    "ITT": "XLI",
    "RRX": "XLI",
    "BAH": "XLI",
    "SAIC": "XLI",
    "MRCY": "XLI",
    "BWXT": "XLI",
    # ── Materials (XLB) — 55 stocks ──────────────────────────────────────────
    "APD": "XLB",
    "LIN": "XLB",
    "SHW": "XLB",
    "NEM": "XLB",
    "FCX": "XLB",
    "NUE": "XLB",
    "STLD": "XLB",
    "CLF": "XLB",
    "X": "XLB",
    "CMC": "XLB",
    "AA": "XLB",
    "ALB": "XLB",
    "CE": "XLB",
    "DD": "XLB",
    "DOW": "XLB",
    "LYB": "XLB",
    "PPG": "XLB",
    "RPM": "XLB",
    "IFF": "XLB",
    "ECL": "XLB",
    "EMN": "XLB",
    "MOS": "XLB",
    "CF": "XLB",
    "NTR": "XLB",
    "CTVA": "XLB",
    "FMC": "XLB",
    "IP": "XLB",
    "PKG": "XLB",
    "WRK": "XLB",
    "SEE": "XLB",
    "AMCR": "XLB",
    "BLL": "XLB",
    "AVY": "XLB",
    "BG": "XLB",
    "ADM": "XLB",
    "GOLD": "XLB",
    "AEM": "XLB",
    "WPM": "XLB",
    "KGC": "XLB",
    "AG": "XLB",
    "CDE": "XLB",
    "HL": "XLB",
    "PAAS": "XLB",
    "MAG": "XLB",
    "SA": "XLB",
    "EQX": "XLB",
    "OR": "XLB",
    "RGLD": "XLB",
    "SCCO": "XLB",
    "TECK": "XLB",
    "MT": "XLB",
    "VALE": "XLB",
    "RIO": "XLB",
    "BHP": "XLB",
    "ATI": "XLB",
    # Gold miners leveraged (GDX/GDXJ proxies)
    "NUGT": "XLB",
    "DUST": "XLB",
    "JNUG": "XLB",
    "JDST": "XLB",
    # ── Real Estate (XLRE) — 55 stocks ───────────────────────────────────────
    "AMT": "XLRE",
    "PLD": "XLRE",
    "EQIX": "XLRE",
    "CCI": "XLRE",
    "PSA": "XLRE",
    "DLR": "XLRE",
    "WELL": "XLRE",
    "VTR": "XLRE",
    "O": "XLRE",
    "NNN": "XLRE",
    "WPC": "XLRE",
    "SPG": "XLRE",
    "MAC": "XLRE",
    "SKT": "XLRE",
    "BXP": "XLRE",
    "SLG": "XLRE",
    "VNO": "XLRE",
    "EQR": "XLRE",
    "AVB": "XLRE",
    "ESS": "XLRE",
    "MAA": "XLRE",
    "CPT": "XLRE",
    "UDR": "XLRE",
    "NLY": "XLRE",
    "AGNC": "XLRE",
    "TWO": "XLRE",
    "PMT": "XLRE",
    "SBAC": "XLRE",
    "IRM": "XLRE",
    "CBRE": "XLRE",
    "JLL": "XLRE",
    "CSGP": "XLRE",
    "Z": "XLRE",
    "ARE": "XLRE",
    "PEAK": "XLRE",
    "HR": "XLRE",
    "INVH": "XLRE",
    "AMH": "XLRE",
    "NHI": "XLRE",
    "STAG": "XLRE",
    "COLD": "XLRE",
    "IIPR": "XLRE",
    "MPW": "XLRE",
    "OHI": "XLRE",
    "LTC": "XLRE",
    "HTA": "XLRE",
    "SITC": "XLRE",
    "REG": "XLRE",
    "KIM": "XLRE",
    "TRNO": "XLRE",
    "REXR": "XLRE",
    "ELS": "XLRE",
    "SUI": "XLRE",
    "ADC": "XLRE",
    "EPRT": "XLRE",
    # Real estate leveraged
    "DRN": "XLRE",
    "DRV": "XLRE",
    # China leveraged (no direct sector ETF — use XLC as closest)
    "YINN": "XLC",
    "YANG": "XLC",
    # Treasury leveraged (bond proxies — use XLU as most rate-sensitive)
    "TMF": "XLU",
    "TMV": "XLU",
    # ── Utilities (XLU) — 55 stocks ──────────────────────────────────────────
    "NEE": "XLU",
    "DUK": "XLU",
    "SO": "XLU",
    "D": "XLU",
    "AEP": "XLU",
    "EXC": "XLU",
    "SRE": "XLU",
    "PCG": "XLU",
    "ED": "XLU",
    "XEL": "XLU",
    "ES": "XLU",
    "PPL": "XLU",
    "FE": "XLU",
    "AES": "XLU",
    "ETR": "XLU",
    "CNP": "XLU",
    "WEC": "XLU",
    "CMS": "XLU",
    "NI": "XLU",
    "AWK": "XLU",
    "AWR": "XLU",
    "SWX": "XLU",
    "SR": "XLU",
    "PNW": "XLU",
    "EVRG": "XLU",
    "NWE": "XLU",
    "BKH": "XLU",
    "OGE": "XLU",
    "ATO": "XLU",
    "LNT": "XLU",
    "MGEE": "XLU",
    "OTTR": "XLU",
    "POR": "XLU",
    "AVA": "XLU",
    "IDA": "XLU",
    "EE": "XLU",
    "AEE": "XLU",
    "DTE": "XLU",
    "NRG": "XLU",
    "VST": "XLU",
    "CWEN": "XLU",
    "BEP": "XLU",
    "NEP": "XLU",
    "ARRY": "XLU",
    "NOVA": "XLU",
    "PLUG": "XLU",
    "FCEL": "XLU",
    "BLDP": "XLU",
    "BE": "XLU",
    "RUN": "XLU",
    "MAXN": "XLU",
    "SPWR": "XLU",
    "SHLS": "XLU",
    "HASI": "XLU",
    "AY": "XLU",
}

# yfinance sector name → SPDR ETF
YFINANCE_TO_ETF: dict[str, str] = {
    "Technology": "XLK",
    "Information Technology": "XLK",
    "Financial Services": "XLF",
    "Financials": "XLF",
    "Consumer Cyclical": "XLY",
    "Consumer Discretionary": "XLY",
    "Communication Services": "XLC",
    "Healthcare": "XLV",
    "Health Care": "XLV",
    "Consumer Defensive": "XLP",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Basic Materials": "XLB",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
}

_etf_cache: dict[str, tuple[pd.DataFrame, float]] = {}
CACHE_TTL = 3600 * 4  # 4 hours


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_get_sector_relative_strength__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_sector_relative_strength__mutmut)
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_orig(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_1(
    ticker: str,
    ticker_df: Optional[pd.DataFrame] = None,
    lookback: int = 22,
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_2(
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
    etf = None
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_3(
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
    etf = SECTOR_MAP.get(None)
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_4(
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
    etf = SECTOR_MAP.get(ticker.lower())
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_5(
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
    if etf:
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_6(
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
        cached = None
        if cached and _time.time() - cached[1] < CACHE_TTL:
            etf_df = cached[0]
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_7(
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
        cached = _etf_cache.get(None)
        if cached and _time.time() - cached[1] < CACHE_TTL:
            etf_df = cached[0]
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_8(
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
        if cached or _time.time() - cached[1] < CACHE_TTL:
            etf_df = cached[0]
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_9(
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
        if cached and _time.time() + cached[1] < CACHE_TTL:
            etf_df = cached[0]
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_10(
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
        if cached and _time.time() - cached[2] < CACHE_TTL:
            etf_df = cached[0]
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_11(
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
        if cached and _time.time() - cached[1] <= CACHE_TTL:
            etf_df = cached[0]
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_12(
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
            etf_df = None
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_13(
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
            etf_df = cached[1]
        else:
            etf_df = await get_history(etf, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_14(
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
            etf_df = None
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_15(
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
            etf_df = await get_history(None, period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_16(
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
            etf_df = await get_history(etf, period=None, interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_17(
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
            etf_df = await get_history(etf, period="3mo", interval=None)
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_18(
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
            etf_df = await get_history(period="3mo", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_19(
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
            etf_df = await get_history(etf, interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_20(
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
            etf_df = await get_history(etf, period="3mo", )
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_21(
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
            etf_df = await get_history(etf, period="XX3moXX", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_22(
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
            etf_df = await get_history(etf, period="3MO", interval="1d")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_23(
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
            etf_df = await get_history(etf, period="3mo", interval="XX1dXX")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_24(
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
            etf_df = await get_history(etf, period="3mo", interval="1D")
            if etf_df is None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_25(
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
            if etf_df is None and len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_26(
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
            if etf_df is not None or len(etf_df) < lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_27(
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
            if etf_df is None or len(etf_df) <= lookback:
                return None
            _etf_cache[etf] = (etf_df, _time.time())

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_28(
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
            _etf_cache[etf] = None

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_29(
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

        etf_1m = None
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_30(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) / 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_31(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) + 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_32(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) * float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_33(
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

        etf_1m = (float(None) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_34(
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

        etf_1m = (float(etf_df["XXCloseXX"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_35(
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

        etf_1m = (float(etf_df["close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_36(
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

        etf_1m = (float(etf_df["CLOSE"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_37(
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

        etf_1m = (float(etf_df["Close"].iloc[+1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_38(
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

        etf_1m = (float(etf_df["Close"].iloc[-2]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_39(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(None) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_40(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["XXCloseXX"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_41(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_42(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["CLOSE"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_43(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[+lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_44(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 2) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_45(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 101
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_46(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = None

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_47(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) / 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_48(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) + 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_49(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) * float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_50(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(None) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_51(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["XXCloseXX"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_52(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_53(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["CLOSE"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_54(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[+1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_55(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-2]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_56(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(None) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_57(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["XXCloseXX"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_58(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_59(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["CLOSE"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_60(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[+5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_61(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-6]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_62(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 2) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_63(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 101 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_64(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) > 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_65(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 6 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_66(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 1.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_67(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None or len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_68(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_69(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) > lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_70(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = None
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_71(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = None
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_72(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(None, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_73(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period=None, interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_74(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval=None)
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_75(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_76(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_77(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", )
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_78(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="XX3moXX", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_79(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3MO", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_80(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="XX1dXX")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_81(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1D")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_82(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None and len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_83(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is not None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_84(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) <= lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_85(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = None

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_86(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) / 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_87(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) + 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_88(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) * float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_89(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(None) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_90(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["XXCloseXX"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_91(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_92(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["CLOSE"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_93(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[+1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_94(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-2]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_95(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(None) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_96(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["XXCloseXX"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_97(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_98(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["CLOSE"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_99(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[+lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_100(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 2) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_101(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 101

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_102(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "XXsector_etfXX": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_103(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "SECTOR_ETF": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_104(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "XXsector_1m_retXX": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_105(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "SECTOR_1M_RET": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_106(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(None, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_107(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, None),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_108(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_109(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, ),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_110(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 3),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_111(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "XXsector_5d_retXX": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_112(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "SECTOR_5D_RET": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_113(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(None, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_114(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, None),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_115(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_116(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, ),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_117(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 3),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_118(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "XXrs_vs_sectorXX": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_119(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "RS_VS_SECTOR": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_120(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(None, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_121(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, None),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_122(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_123(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, ),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_124(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m + etf_1m, 2),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_125(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 3),
        }

    except Exception as e:
        print(f"[sector] {ticker}/{etf}: {e}")
        return None


async def x_get_sector_relative_strength__mutmut_126(
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

        etf_1m = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-lookback]) - 1) * 100
        etf_5d = (float(etf_df["Close"].iloc[-1]) / float(etf_df["Close"].iloc[-5]) - 1) * 100 if len(etf_df) >= 5 else 0.0

        # ── Ticker data ────────────────────────────────────────────────
        if ticker_df is not None and len(ticker_df) >= lookback:
            df = ticker_df
        else:
            df = await get_history(ticker, period="3mo", interval="1d")
            if df is None or len(df) < lookback:
                return None

        ticker_1m = (float(df["Close"].iloc[-1]) / float(df["Close"].iloc[-lookback]) - 1) * 100

        return {
            "sector_etf": etf,
            "sector_1m_ret": round(etf_1m, 2),
            "sector_5d_ret": round(etf_5d, 2),
            "rs_vs_sector": round(ticker_1m - etf_1m, 2),
        }

    except Exception as e:
        print(None)
        return None

mutants_x_get_sector_relative_strength__mutmut['_mutmut_orig'] = x_get_sector_relative_strength__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_1'] = x_get_sector_relative_strength__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_2'] = x_get_sector_relative_strength__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_3'] = x_get_sector_relative_strength__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_4'] = x_get_sector_relative_strength__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_5'] = x_get_sector_relative_strength__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_6'] = x_get_sector_relative_strength__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_7'] = x_get_sector_relative_strength__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_8'] = x_get_sector_relative_strength__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_9'] = x_get_sector_relative_strength__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_10'] = x_get_sector_relative_strength__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_11'] = x_get_sector_relative_strength__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_12'] = x_get_sector_relative_strength__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_13'] = x_get_sector_relative_strength__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_14'] = x_get_sector_relative_strength__mutmut_14 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_15'] = x_get_sector_relative_strength__mutmut_15 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_16'] = x_get_sector_relative_strength__mutmut_16 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_17'] = x_get_sector_relative_strength__mutmut_17 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_18'] = x_get_sector_relative_strength__mutmut_18 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_19'] = x_get_sector_relative_strength__mutmut_19 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_20'] = x_get_sector_relative_strength__mutmut_20 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_21'] = x_get_sector_relative_strength__mutmut_21 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_22'] = x_get_sector_relative_strength__mutmut_22 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_23'] = x_get_sector_relative_strength__mutmut_23 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_24'] = x_get_sector_relative_strength__mutmut_24 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_25'] = x_get_sector_relative_strength__mutmut_25 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_26'] = x_get_sector_relative_strength__mutmut_26 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_27'] = x_get_sector_relative_strength__mutmut_27 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_28'] = x_get_sector_relative_strength__mutmut_28 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_29'] = x_get_sector_relative_strength__mutmut_29 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_30'] = x_get_sector_relative_strength__mutmut_30 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_31'] = x_get_sector_relative_strength__mutmut_31 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_32'] = x_get_sector_relative_strength__mutmut_32 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_33'] = x_get_sector_relative_strength__mutmut_33 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_34'] = x_get_sector_relative_strength__mutmut_34 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_35'] = x_get_sector_relative_strength__mutmut_35 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_36'] = x_get_sector_relative_strength__mutmut_36 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_37'] = x_get_sector_relative_strength__mutmut_37 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_38'] = x_get_sector_relative_strength__mutmut_38 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_39'] = x_get_sector_relative_strength__mutmut_39 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_40'] = x_get_sector_relative_strength__mutmut_40 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_41'] = x_get_sector_relative_strength__mutmut_41 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_42'] = x_get_sector_relative_strength__mutmut_42 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_43'] = x_get_sector_relative_strength__mutmut_43 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_44'] = x_get_sector_relative_strength__mutmut_44 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_45'] = x_get_sector_relative_strength__mutmut_45 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_46'] = x_get_sector_relative_strength__mutmut_46 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_47'] = x_get_sector_relative_strength__mutmut_47 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_48'] = x_get_sector_relative_strength__mutmut_48 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_49'] = x_get_sector_relative_strength__mutmut_49 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_50'] = x_get_sector_relative_strength__mutmut_50 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_51'] = x_get_sector_relative_strength__mutmut_51 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_52'] = x_get_sector_relative_strength__mutmut_52 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_53'] = x_get_sector_relative_strength__mutmut_53 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_54'] = x_get_sector_relative_strength__mutmut_54 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_55'] = x_get_sector_relative_strength__mutmut_55 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_56'] = x_get_sector_relative_strength__mutmut_56 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_57'] = x_get_sector_relative_strength__mutmut_57 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_58'] = x_get_sector_relative_strength__mutmut_58 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_59'] = x_get_sector_relative_strength__mutmut_59 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_60'] = x_get_sector_relative_strength__mutmut_60 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_61'] = x_get_sector_relative_strength__mutmut_61 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_62'] = x_get_sector_relative_strength__mutmut_62 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_63'] = x_get_sector_relative_strength__mutmut_63 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_64'] = x_get_sector_relative_strength__mutmut_64 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_65'] = x_get_sector_relative_strength__mutmut_65 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_66'] = x_get_sector_relative_strength__mutmut_66 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_67'] = x_get_sector_relative_strength__mutmut_67 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_68'] = x_get_sector_relative_strength__mutmut_68 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_69'] = x_get_sector_relative_strength__mutmut_69 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_70'] = x_get_sector_relative_strength__mutmut_70 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_71'] = x_get_sector_relative_strength__mutmut_71 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_72'] = x_get_sector_relative_strength__mutmut_72 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_73'] = x_get_sector_relative_strength__mutmut_73 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_74'] = x_get_sector_relative_strength__mutmut_74 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_75'] = x_get_sector_relative_strength__mutmut_75 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_76'] = x_get_sector_relative_strength__mutmut_76 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_77'] = x_get_sector_relative_strength__mutmut_77 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_78'] = x_get_sector_relative_strength__mutmut_78 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_79'] = x_get_sector_relative_strength__mutmut_79 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_80'] = x_get_sector_relative_strength__mutmut_80 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_81'] = x_get_sector_relative_strength__mutmut_81 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_82'] = x_get_sector_relative_strength__mutmut_82 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_83'] = x_get_sector_relative_strength__mutmut_83 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_84'] = x_get_sector_relative_strength__mutmut_84 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_85'] = x_get_sector_relative_strength__mutmut_85 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_86'] = x_get_sector_relative_strength__mutmut_86 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_87'] = x_get_sector_relative_strength__mutmut_87 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_88'] = x_get_sector_relative_strength__mutmut_88 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_89'] = x_get_sector_relative_strength__mutmut_89 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_90'] = x_get_sector_relative_strength__mutmut_90 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_91'] = x_get_sector_relative_strength__mutmut_91 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_92'] = x_get_sector_relative_strength__mutmut_92 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_93'] = x_get_sector_relative_strength__mutmut_93 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_94'] = x_get_sector_relative_strength__mutmut_94 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_95'] = x_get_sector_relative_strength__mutmut_95 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_96'] = x_get_sector_relative_strength__mutmut_96 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_97'] = x_get_sector_relative_strength__mutmut_97 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_98'] = x_get_sector_relative_strength__mutmut_98 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_99'] = x_get_sector_relative_strength__mutmut_99 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_100'] = x_get_sector_relative_strength__mutmut_100 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_101'] = x_get_sector_relative_strength__mutmut_101 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_102'] = x_get_sector_relative_strength__mutmut_102 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_103'] = x_get_sector_relative_strength__mutmut_103 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_104'] = x_get_sector_relative_strength__mutmut_104 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_105'] = x_get_sector_relative_strength__mutmut_105 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_106'] = x_get_sector_relative_strength__mutmut_106 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_107'] = x_get_sector_relative_strength__mutmut_107 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_108'] = x_get_sector_relative_strength__mutmut_108 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_109'] = x_get_sector_relative_strength__mutmut_109 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_110'] = x_get_sector_relative_strength__mutmut_110 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_111'] = x_get_sector_relative_strength__mutmut_111 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_112'] = x_get_sector_relative_strength__mutmut_112 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_113'] = x_get_sector_relative_strength__mutmut_113 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_114'] = x_get_sector_relative_strength__mutmut_114 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_115'] = x_get_sector_relative_strength__mutmut_115 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_116'] = x_get_sector_relative_strength__mutmut_116 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_117'] = x_get_sector_relative_strength__mutmut_117 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_118'] = x_get_sector_relative_strength__mutmut_118 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_119'] = x_get_sector_relative_strength__mutmut_119 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_120'] = x_get_sector_relative_strength__mutmut_120 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_121'] = x_get_sector_relative_strength__mutmut_121 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_122'] = x_get_sector_relative_strength__mutmut_122 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_123'] = x_get_sector_relative_strength__mutmut_123 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_124'] = x_get_sector_relative_strength__mutmut_124 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_125'] = x_get_sector_relative_strength__mutmut_125 # type: ignore # mutmut generated
mutants_x_get_sector_relative_strength__mutmut['x_get_sector_relative_strength__mutmut_126'] = x_get_sector_relative_strength__mutmut_126 # type: ignore # mutmut generated
