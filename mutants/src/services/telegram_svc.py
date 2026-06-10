import aiohttp
from services.http_client import get_ssl_context, shared_session


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_format_signal__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_format_signal__mutmut)
def format_signal(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_orig(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_1(signal: dict) -> str:
    emoji = None
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_2(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(None, "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_3(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], None)
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_4(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get("⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_5(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], )
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_6(signal: dict) -> str:
    emoji = {"XXBUYXX": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_7(signal: dict) -> str:
    emoji = {"buy": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_8(signal: dict) -> str:
    emoji = {"BUY": "XX🟢XX", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_9(signal: dict) -> str:
    emoji = {"BUY": "🟢", "XXSELLXX": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_10(signal: dict) -> str:
    emoji = {"BUY": "🟢", "sell": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_11(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "XX🔴XX", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_12(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "XXHOLDXX": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_13(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "hold": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_14(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "XX🟡XX"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_15(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["XXactionXX"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_16(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["ACTION"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_17(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "XX⚪XX")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_18(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = None
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_19(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['XXconfidenceXX']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_20(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['CONFIDENCE']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_21(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = None
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_22(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get(None, "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_23(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", None)
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_24(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_25(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", )
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_26(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("XXrrXX", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_27(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("RR", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_28(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "XX—XX")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_29(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = None
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_30(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get(None, "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_31(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", None)
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_32(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_33(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", )
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_34(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("XXcompanyXX", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_35(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("COMPANY", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_36(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "XXXX")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_37(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = None
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_38(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company or company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_39(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company == signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_40(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["XXtickerXX"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_41(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["TICKER"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_42(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else "XXXX"
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_43(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = None
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_44(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['XXactionXX']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_45(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['ACTION']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_46(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['XXtickerXX']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_47(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['TICKER']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_48(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['XXpriceXX']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_49(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['PRICE']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_50(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['XXheadlineXX']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_51(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['HEADLINE']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_52(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") or signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_53(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") or signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_54(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get(None) and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_55(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("XXentryXX") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_56(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("ENTRY") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_57(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get(None) and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_58(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("XXstopXX") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_59(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("STOP") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_60(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get(None):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_61(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("XXtargetXX"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_62(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("TARGET"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_63(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(None)
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_64(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['XXentryXX']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_65(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['ENTRY']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_66(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['XXstopXX']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_67(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['STOP']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_68(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['XXtargetXX']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_69(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['TARGET']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_70(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append(None)
    return "\n".join(lines)


def x_format_signal__mutmut_71(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("XX_Not financial advice · Signal.Trade_XX")
    return "\n".join(lines)


def x_format_signal__mutmut_72(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_not financial advice · signal.trade_")
    return "\n".join(lines)


def x_format_signal__mutmut_73(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_NOT FINANCIAL ADVICE · SIGNAL.TRADE_")
    return "\n".join(lines)


def x_format_signal__mutmut_74(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(None)


def x_format_signal__mutmut_75(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    rr = signal.get("rr", "—")
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "XX\nXX".join(lines)

mutants_x_format_signal__mutmut['_mutmut_orig'] = x_format_signal__mutmut_orig # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_1'] = x_format_signal__mutmut_1 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_2'] = x_format_signal__mutmut_2 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_3'] = x_format_signal__mutmut_3 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_4'] = x_format_signal__mutmut_4 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_5'] = x_format_signal__mutmut_5 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_6'] = x_format_signal__mutmut_6 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_7'] = x_format_signal__mutmut_7 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_8'] = x_format_signal__mutmut_8 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_9'] = x_format_signal__mutmut_9 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_10'] = x_format_signal__mutmut_10 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_11'] = x_format_signal__mutmut_11 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_12'] = x_format_signal__mutmut_12 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_13'] = x_format_signal__mutmut_13 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_14'] = x_format_signal__mutmut_14 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_15'] = x_format_signal__mutmut_15 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_16'] = x_format_signal__mutmut_16 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_17'] = x_format_signal__mutmut_17 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_18'] = x_format_signal__mutmut_18 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_19'] = x_format_signal__mutmut_19 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_20'] = x_format_signal__mutmut_20 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_21'] = x_format_signal__mutmut_21 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_22'] = x_format_signal__mutmut_22 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_23'] = x_format_signal__mutmut_23 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_24'] = x_format_signal__mutmut_24 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_25'] = x_format_signal__mutmut_25 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_26'] = x_format_signal__mutmut_26 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_27'] = x_format_signal__mutmut_27 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_28'] = x_format_signal__mutmut_28 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_29'] = x_format_signal__mutmut_29 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_30'] = x_format_signal__mutmut_30 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_31'] = x_format_signal__mutmut_31 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_32'] = x_format_signal__mutmut_32 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_33'] = x_format_signal__mutmut_33 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_34'] = x_format_signal__mutmut_34 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_35'] = x_format_signal__mutmut_35 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_36'] = x_format_signal__mutmut_36 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_37'] = x_format_signal__mutmut_37 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_38'] = x_format_signal__mutmut_38 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_39'] = x_format_signal__mutmut_39 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_40'] = x_format_signal__mutmut_40 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_41'] = x_format_signal__mutmut_41 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_42'] = x_format_signal__mutmut_42 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_43'] = x_format_signal__mutmut_43 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_44'] = x_format_signal__mutmut_44 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_45'] = x_format_signal__mutmut_45 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_46'] = x_format_signal__mutmut_46 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_47'] = x_format_signal__mutmut_47 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_48'] = x_format_signal__mutmut_48 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_49'] = x_format_signal__mutmut_49 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_50'] = x_format_signal__mutmut_50 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_51'] = x_format_signal__mutmut_51 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_52'] = x_format_signal__mutmut_52 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_53'] = x_format_signal__mutmut_53 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_54'] = x_format_signal__mutmut_54 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_55'] = x_format_signal__mutmut_55 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_56'] = x_format_signal__mutmut_56 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_57'] = x_format_signal__mutmut_57 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_58'] = x_format_signal__mutmut_58 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_59'] = x_format_signal__mutmut_59 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_60'] = x_format_signal__mutmut_60 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_61'] = x_format_signal__mutmut_61 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_62'] = x_format_signal__mutmut_62 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_63'] = x_format_signal__mutmut_63 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_64'] = x_format_signal__mutmut_64 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_65'] = x_format_signal__mutmut_65 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_66'] = x_format_signal__mutmut_66 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_67'] = x_format_signal__mutmut_67 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_68'] = x_format_signal__mutmut_68 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_69'] = x_format_signal__mutmut_69 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_70'] = x_format_signal__mutmut_70 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_71'] = x_format_signal__mutmut_71 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_72'] = x_format_signal__mutmut_72 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_73'] = x_format_signal__mutmut_73 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_74'] = x_format_signal__mutmut_74 # type: ignore # mutmut generated
mutants_x_format_signal__mutmut['x_format_signal__mutmut_75'] = x_format_signal__mutmut_75 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_telegram_message__mutmut)
async def send_telegram_message(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_orig(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_1(
    chat_id: str,
    text: str,
    parse_mode: str = "XXMarkdownXX",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_2(
    chat_id: str,
    text: str,
    parse_mode: str = "markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_3(
    chat_id: str,
    text: str,
    parse_mode: str = "MARKDOWN",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_4(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 9,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_5(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = None
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_6(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token and not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_7(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_8(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_9(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return True, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_10(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "XXNot configuredXX"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_11(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_12(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "NOT CONFIGURED"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_13(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = None
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_14(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = None
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_15(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = None
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_16(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                None,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_17(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json=None,
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_18(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=None,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_19(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=None,
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_20(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_21(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_22(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_23(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_24(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"XXchat_idXX": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_25(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"CHAT_ID": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_26(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "XXtextXX": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_27(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "TEXT": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_28(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "XXparse_modeXX": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_29(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "PARSE_MODE": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_30(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=None),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_31(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = None
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_32(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get(None):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_33(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("XXokXX"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_34(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("OK"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_35(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return False, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_36(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(None)
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_37(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get(None, ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_38(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", None))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_39(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get(""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_40(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_41(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get(None, {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_42(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", None).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_43(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get({}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_44(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", ).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_45(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("XXresultXX", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_46(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("RESULT", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_47(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("XXmessage_idXX", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_48(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("MESSAGE_ID", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_49(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", "XXXX"))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_50(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return True, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_51(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get(None, "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_52(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", None)
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_53(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_54(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", )
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_55(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("XXdescriptionXX", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_56(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("DESCRIPTION", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_57(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "XXUnknown Telegram errorXX")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_58(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "unknown telegram error")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_59(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "UNKNOWN TELEGRAM ERROR")
    except Exception as e:
        return False, str(e)


async def x_send_telegram_message__mutmut_60(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return True, str(e)


async def x_send_telegram_message__mutmut_61(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(None)

mutants_x_send_telegram_message__mutmut['_mutmut_orig'] = x_send_telegram_message__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_1'] = x_send_telegram_message__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_2'] = x_send_telegram_message__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_3'] = x_send_telegram_message__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_4'] = x_send_telegram_message__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_5'] = x_send_telegram_message__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_6'] = x_send_telegram_message__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_7'] = x_send_telegram_message__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_8'] = x_send_telegram_message__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_9'] = x_send_telegram_message__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_10'] = x_send_telegram_message__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_11'] = x_send_telegram_message__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_12'] = x_send_telegram_message__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_13'] = x_send_telegram_message__mutmut_13 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_14'] = x_send_telegram_message__mutmut_14 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_15'] = x_send_telegram_message__mutmut_15 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_16'] = x_send_telegram_message__mutmut_16 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_17'] = x_send_telegram_message__mutmut_17 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_18'] = x_send_telegram_message__mutmut_18 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_19'] = x_send_telegram_message__mutmut_19 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_20'] = x_send_telegram_message__mutmut_20 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_21'] = x_send_telegram_message__mutmut_21 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_22'] = x_send_telegram_message__mutmut_22 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_23'] = x_send_telegram_message__mutmut_23 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_24'] = x_send_telegram_message__mutmut_24 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_25'] = x_send_telegram_message__mutmut_25 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_26'] = x_send_telegram_message__mutmut_26 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_27'] = x_send_telegram_message__mutmut_27 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_28'] = x_send_telegram_message__mutmut_28 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_29'] = x_send_telegram_message__mutmut_29 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_30'] = x_send_telegram_message__mutmut_30 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_31'] = x_send_telegram_message__mutmut_31 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_32'] = x_send_telegram_message__mutmut_32 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_33'] = x_send_telegram_message__mutmut_33 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_34'] = x_send_telegram_message__mutmut_34 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_35'] = x_send_telegram_message__mutmut_35 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_36'] = x_send_telegram_message__mutmut_36 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_37'] = x_send_telegram_message__mutmut_37 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_38'] = x_send_telegram_message__mutmut_38 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_39'] = x_send_telegram_message__mutmut_39 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_40'] = x_send_telegram_message__mutmut_40 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_41'] = x_send_telegram_message__mutmut_41 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_42'] = x_send_telegram_message__mutmut_42 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_43'] = x_send_telegram_message__mutmut_43 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_44'] = x_send_telegram_message__mutmut_44 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_45'] = x_send_telegram_message__mutmut_45 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_46'] = x_send_telegram_message__mutmut_46 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_47'] = x_send_telegram_message__mutmut_47 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_48'] = x_send_telegram_message__mutmut_48 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_49'] = x_send_telegram_message__mutmut_49 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_50'] = x_send_telegram_message__mutmut_50 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_51'] = x_send_telegram_message__mutmut_51 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_52'] = x_send_telegram_message__mutmut_52 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_53'] = x_send_telegram_message__mutmut_53 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_54'] = x_send_telegram_message__mutmut_54 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_55'] = x_send_telegram_message__mutmut_55 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_56'] = x_send_telegram_message__mutmut_56 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_57'] = x_send_telegram_message__mutmut_57 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_58'] = x_send_telegram_message__mutmut_58 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_59'] = x_send_telegram_message__mutmut_59 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_60'] = x_send_telegram_message__mutmut_60 # type: ignore # mutmut generated
mutants_x_send_telegram_message__mutmut['x_send_telegram_message__mutmut_61'] = x_send_telegram_message__mutmut_61 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_telegram__mutmut)
async def send_telegram(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_orig(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_1(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = None
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_2(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token and not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_3(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_4(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_5(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return True, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_6(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "XXTelegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .envXX"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_7(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "telegram not configured — set telegram_bot_token and telegram_chat_id in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_8(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "TELEGRAM NOT CONFIGURED — SET TELEGRAM_BOT_TOKEN AND TELEGRAM_CHAT_ID IN .ENV"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))


async def x_send_telegram__mutmut_9(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(None, format_signal(signal))


async def x_send_telegram__mutmut_10(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, None)


async def x_send_telegram__mutmut_11(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(format_signal(signal))


async def x_send_telegram__mutmut_12(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, )


async def x_send_telegram__mutmut_13(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(None))

mutants_x_send_telegram__mutmut['_mutmut_orig'] = x_send_telegram__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_1'] = x_send_telegram__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_2'] = x_send_telegram__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_3'] = x_send_telegram__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_4'] = x_send_telegram__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_5'] = x_send_telegram__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_6'] = x_send_telegram__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_7'] = x_send_telegram__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_8'] = x_send_telegram__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_9'] = x_send_telegram__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_10'] = x_send_telegram__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_11'] = x_send_telegram__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_12'] = x_send_telegram__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_telegram__mutmut['x_send_telegram__mutmut_13'] = x_send_telegram__mutmut_13 # type: ignore # mutmut generated
