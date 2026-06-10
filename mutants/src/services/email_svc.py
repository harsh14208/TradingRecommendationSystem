"""
Email service — sends transactional emails via SMTP (aiosmtplib).
Falls back to console logging if SMTP is not configured.
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger("signal.trade.email")


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


def _settings():
    from config import get_settings

    return get_settings()
mutants_x__send__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__send__mutmut)
async def _send(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_orig(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_1(to: str, subject: str, html: str, plain: str):
    s = None
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_2(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host and not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_3(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_4(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_5(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(None)
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_6(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = None
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_7(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart(None)
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_8(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("XXalternativeXX")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_9(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("ALTERNATIVE")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_10(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = None
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_11(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["XXSubjectXX"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_12(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_13(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["SUBJECT"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_14(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = None
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_15(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["XXFromXX"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_16(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["from"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_17(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["FROM"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_18(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = None
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_19(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["XXToXX"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_20(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["to"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_21(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["TO"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_22(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(None)
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_23(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(None, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_24(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, None))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_25(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText("plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_26(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, ))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_27(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "XXplainXX"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_28(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "PLAIN"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_29(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(None)
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_30(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(None, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_31(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, None))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_32(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText("html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_33(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, ))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_34(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "XXhtmlXX"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_35(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "HTML"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_36(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            None,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_37(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=None,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_38(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=None,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_39(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=None,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_40(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=None,
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_41(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=None,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_42(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_43(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_44(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_45(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_46(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_47(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_48(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=False,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_49(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(None)
    except Exception as e:
        log.warning(f"[email] failed TO={to}: {e}")


async def x__send__mutmut_50(to: str, subject: str, html: str, plain: str):
    s = _settings()
    if not s.smtp_host or not s.smtp_user:
        log.info(f"[email] (SMTP not configured) TO={to} SUBJECT={subject}")
        return

    try:
        import aiosmtplib

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.smtp_from_name} <{s.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=s.smtp_host,
            port=s.smtp_port,
            username=s.smtp_user,
            password=s.smtp_password.get_secret_value(),
            start_tls=True,
        )
        log.info(f"[email] sent TO={to} SUBJECT={subject}")
    except Exception as e:
        log.warning(None)

mutants_x__send__mutmut['_mutmut_orig'] = x__send__mutmut_orig # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_1'] = x__send__mutmut_1 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_2'] = x__send__mutmut_2 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_3'] = x__send__mutmut_3 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_4'] = x__send__mutmut_4 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_5'] = x__send__mutmut_5 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_6'] = x__send__mutmut_6 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_7'] = x__send__mutmut_7 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_8'] = x__send__mutmut_8 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_9'] = x__send__mutmut_9 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_10'] = x__send__mutmut_10 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_11'] = x__send__mutmut_11 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_12'] = x__send__mutmut_12 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_13'] = x__send__mutmut_13 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_14'] = x__send__mutmut_14 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_15'] = x__send__mutmut_15 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_16'] = x__send__mutmut_16 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_17'] = x__send__mutmut_17 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_18'] = x__send__mutmut_18 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_19'] = x__send__mutmut_19 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_20'] = x__send__mutmut_20 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_21'] = x__send__mutmut_21 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_22'] = x__send__mutmut_22 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_23'] = x__send__mutmut_23 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_24'] = x__send__mutmut_24 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_25'] = x__send__mutmut_25 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_26'] = x__send__mutmut_26 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_27'] = x__send__mutmut_27 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_28'] = x__send__mutmut_28 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_29'] = x__send__mutmut_29 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_30'] = x__send__mutmut_30 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_31'] = x__send__mutmut_31 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_32'] = x__send__mutmut_32 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_33'] = x__send__mutmut_33 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_34'] = x__send__mutmut_34 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_35'] = x__send__mutmut_35 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_36'] = x__send__mutmut_36 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_37'] = x__send__mutmut_37 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_38'] = x__send__mutmut_38 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_39'] = x__send__mutmut_39 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_40'] = x__send__mutmut_40 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_41'] = x__send__mutmut_41 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_42'] = x__send__mutmut_42 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_43'] = x__send__mutmut_43 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_44'] = x__send__mutmut_44 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_45'] = x__send__mutmut_45 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_46'] = x__send__mutmut_46 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_47'] = x__send__mutmut_47 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_48'] = x__send__mutmut_48 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_49'] = x__send__mutmut_49 # type: ignore # mutmut generated
mutants_x__send__mutmut['x__send__mutmut_50'] = x__send__mutmut_50 # type: ignore # mutmut generated


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
mutants_x_send_welcome__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_welcome__mutmut)
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


async def x_send_welcome__mutmut_orig(to: str, full_name: str):
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


async def x_send_welcome__mutmut_1(to: str, full_name: str):
    name = None
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


async def x_send_welcome__mutmut_2(to: str, full_name: str):
    name = full_name and to.split("@")[0]
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


async def x_send_welcome__mutmut_3(to: str, full_name: str):
    name = full_name or to.split(None)[0]
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


async def x_send_welcome__mutmut_4(to: str, full_name: str):
    name = full_name or to.split("XX@XX")[0]
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


async def x_send_welcome__mutmut_5(to: str, full_name: str):
    name = full_name or to.split("@")[1]
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


async def x_send_welcome__mutmut_6(to: str, full_name: str):
    name = full_name or to.split("@")[0]
    html = None
    plain = f"Welcome to Signal.Trade, {name}!\n\nYou're on the Free plan. Upgrade to unlock Telegram signals and advanced features.\n\nNot financial advice."
    await _send(to, "Welcome to Signal.Trade", html, plain)


async def x_send_welcome__mutmut_7(to: str, full_name: str):
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
    plain = None
    await _send(to, "Welcome to Signal.Trade", html, plain)


async def x_send_welcome__mutmut_8(to: str, full_name: str):
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
    await _send(None, "Welcome to Signal.Trade", html, plain)


async def x_send_welcome__mutmut_9(to: str, full_name: str):
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
    await _send(to, None, html, plain)


async def x_send_welcome__mutmut_10(to: str, full_name: str):
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
    await _send(to, "Welcome to Signal.Trade", None, plain)


async def x_send_welcome__mutmut_11(to: str, full_name: str):
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
    await _send(to, "Welcome to Signal.Trade", html, None)


async def x_send_welcome__mutmut_12(to: str, full_name: str):
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
    await _send("Welcome to Signal.Trade", html, plain)


async def x_send_welcome__mutmut_13(to: str, full_name: str):
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
    await _send(to, html, plain)


async def x_send_welcome__mutmut_14(to: str, full_name: str):
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
    await _send(to, "Welcome to Signal.Trade", plain)


async def x_send_welcome__mutmut_15(to: str, full_name: str):
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
    await _send(to, "Welcome to Signal.Trade", html, )


async def x_send_welcome__mutmut_16(to: str, full_name: str):
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
    await _send(to, "XXWelcome to Signal.TradeXX", html, plain)


async def x_send_welcome__mutmut_17(to: str, full_name: str):
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
    await _send(to, "welcome to signal.trade", html, plain)


async def x_send_welcome__mutmut_18(to: str, full_name: str):
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
    await _send(to, "WELCOME TO SIGNAL.TRADE", html, plain)

mutants_x_send_welcome__mutmut['_mutmut_orig'] = x_send_welcome__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_1'] = x_send_welcome__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_2'] = x_send_welcome__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_3'] = x_send_welcome__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_4'] = x_send_welcome__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_5'] = x_send_welcome__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_6'] = x_send_welcome__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_7'] = x_send_welcome__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_8'] = x_send_welcome__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_9'] = x_send_welcome__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_10'] = x_send_welcome__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_11'] = x_send_welcome__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_12'] = x_send_welcome__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_13'] = x_send_welcome__mutmut_13 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_14'] = x_send_welcome__mutmut_14 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_15'] = x_send_welcome__mutmut_15 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_16'] = x_send_welcome__mutmut_16 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_17'] = x_send_welcome__mutmut_17 # type: ignore # mutmut generated
mutants_x_send_welcome__mutmut['x_send_welcome__mutmut_18'] = x_send_welcome__mutmut_18 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_subscription_confirmed__mutmut)
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


async def x_send_subscription_confirmed__mutmut_orig(to: str, full_name: str, tier: str, period_end: str):
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


async def x_send_subscription_confirmed__mutmut_1(to: str, full_name: str, tier: str, period_end: str):
    name = None
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


async def x_send_subscription_confirmed__mutmut_2(to: str, full_name: str, tier: str, period_end: str):
    name = full_name and to.split("@")[0]
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


async def x_send_subscription_confirmed__mutmut_3(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split(None)[0]
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


async def x_send_subscription_confirmed__mutmut_4(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("XX@XX")[0]
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


async def x_send_subscription_confirmed__mutmut_5(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[1]
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


async def x_send_subscription_confirmed__mutmut_6(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = None
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


async def x_send_subscription_confirmed__mutmut_7(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = None
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


async def x_send_subscription_confirmed__mutmut_8(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "XXpill proXX" if tier == "pro" else "pill"
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


async def x_send_subscription_confirmed__mutmut_9(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "PILL PRO" if tier == "pro" else "pill"
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


async def x_send_subscription_confirmed__mutmut_10(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "pill pro" if tier != "pro" else "pill"
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


async def x_send_subscription_confirmed__mutmut_11(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "pill pro" if tier == "XXproXX" else "pill"
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


async def x_send_subscription_confirmed__mutmut_12(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "pill pro" if tier == "PRO" else "pill"
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


async def x_send_subscription_confirmed__mutmut_13(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "pill pro" if tier == "pro" else "XXpillXX"
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


async def x_send_subscription_confirmed__mutmut_14(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "pill pro" if tier == "pro" else "PILL"
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


async def x_send_subscription_confirmed__mutmut_15(to: str, full_name: str, tier: str, period_end: str):
    name = full_name or to.split("@")[0]
    tier_cap = tier.capitalize()
    pill_class = "pill pro" if tier == "pro" else "pill"
    html = None
    plain = f"Subscription confirmed!\n\nYou're now on the {tier_cap} plan, renewing on {period_end}.\n\nNot financial advice."
    await _send(to, f"Signal.Trade — {tier_cap} plan activated", html, plain)


async def x_send_subscription_confirmed__mutmut_16(to: str, full_name: str, tier: str, period_end: str):
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
    plain = None
    await _send(to, f"Signal.Trade — {tier_cap} plan activated", html, plain)


async def x_send_subscription_confirmed__mutmut_17(to: str, full_name: str, tier: str, period_end: str):
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
    await _send(None, f"Signal.Trade — {tier_cap} plan activated", html, plain)


async def x_send_subscription_confirmed__mutmut_18(to: str, full_name: str, tier: str, period_end: str):
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
    await _send(to, None, html, plain)


async def x_send_subscription_confirmed__mutmut_19(to: str, full_name: str, tier: str, period_end: str):
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
    await _send(to, f"Signal.Trade — {tier_cap} plan activated", None, plain)


async def x_send_subscription_confirmed__mutmut_20(to: str, full_name: str, tier: str, period_end: str):
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
    await _send(to, f"Signal.Trade — {tier_cap} plan activated", html, None)


async def x_send_subscription_confirmed__mutmut_21(to: str, full_name: str, tier: str, period_end: str):
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
    await _send(f"Signal.Trade — {tier_cap} plan activated", html, plain)


async def x_send_subscription_confirmed__mutmut_22(to: str, full_name: str, tier: str, period_end: str):
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
    await _send(to, html, plain)


async def x_send_subscription_confirmed__mutmut_23(to: str, full_name: str, tier: str, period_end: str):
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
    await _send(to, f"Signal.Trade — {tier_cap} plan activated", plain)


async def x_send_subscription_confirmed__mutmut_24(to: str, full_name: str, tier: str, period_end: str):
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
    await _send(to, f"Signal.Trade — {tier_cap} plan activated", html, )

mutants_x_send_subscription_confirmed__mutmut['_mutmut_orig'] = x_send_subscription_confirmed__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_1'] = x_send_subscription_confirmed__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_2'] = x_send_subscription_confirmed__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_3'] = x_send_subscription_confirmed__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_4'] = x_send_subscription_confirmed__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_5'] = x_send_subscription_confirmed__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_6'] = x_send_subscription_confirmed__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_7'] = x_send_subscription_confirmed__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_8'] = x_send_subscription_confirmed__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_9'] = x_send_subscription_confirmed__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_10'] = x_send_subscription_confirmed__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_11'] = x_send_subscription_confirmed__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_12'] = x_send_subscription_confirmed__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_13'] = x_send_subscription_confirmed__mutmut_13 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_14'] = x_send_subscription_confirmed__mutmut_14 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_15'] = x_send_subscription_confirmed__mutmut_15 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_16'] = x_send_subscription_confirmed__mutmut_16 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_17'] = x_send_subscription_confirmed__mutmut_17 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_18'] = x_send_subscription_confirmed__mutmut_18 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_19'] = x_send_subscription_confirmed__mutmut_19 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_20'] = x_send_subscription_confirmed__mutmut_20 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_21'] = x_send_subscription_confirmed__mutmut_21 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_22'] = x_send_subscription_confirmed__mutmut_22 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_23'] = x_send_subscription_confirmed__mutmut_23 # type: ignore # mutmut generated
mutants_x_send_subscription_confirmed__mutmut['x_send_subscription_confirmed__mutmut_24'] = x_send_subscription_confirmed__mutmut_24 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_payment_failed__mutmut)
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


async def x_send_payment_failed__mutmut_orig(to: str, full_name: str):
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


async def x_send_payment_failed__mutmut_1(to: str, full_name: str):
    name = None
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


async def x_send_payment_failed__mutmut_2(to: str, full_name: str):
    name = full_name and to.split("@")[0]
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


async def x_send_payment_failed__mutmut_3(to: str, full_name: str):
    name = full_name or to.split(None)[0]
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


async def x_send_payment_failed__mutmut_4(to: str, full_name: str):
    name = full_name or to.split("XX@XX")[0]
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


async def x_send_payment_failed__mutmut_5(to: str, full_name: str):
    name = full_name or to.split("@")[1]
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


async def x_send_payment_failed__mutmut_6(to: str, full_name: str):
    name = full_name or to.split("@")[0]
    html = None
    plain = f"Hey {name}, we couldn't process your Signal.Trade payment. Please update your payment method."
    await _send(to, "Signal.Trade — Payment failed", html, plain)


async def x_send_payment_failed__mutmut_7(to: str, full_name: str):
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
    plain = None
    await _send(to, "Signal.Trade — Payment failed", html, plain)


async def x_send_payment_failed__mutmut_8(to: str, full_name: str):
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
    await _send(None, "Signal.Trade — Payment failed", html, plain)


async def x_send_payment_failed__mutmut_9(to: str, full_name: str):
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
    await _send(to, None, html, plain)


async def x_send_payment_failed__mutmut_10(to: str, full_name: str):
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
    await _send(to, "Signal.Trade — Payment failed", None, plain)


async def x_send_payment_failed__mutmut_11(to: str, full_name: str):
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
    await _send(to, "Signal.Trade — Payment failed", html, None)


async def x_send_payment_failed__mutmut_12(to: str, full_name: str):
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
    await _send("Signal.Trade — Payment failed", html, plain)


async def x_send_payment_failed__mutmut_13(to: str, full_name: str):
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
    await _send(to, html, plain)


async def x_send_payment_failed__mutmut_14(to: str, full_name: str):
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
    await _send(to, "Signal.Trade — Payment failed", plain)


async def x_send_payment_failed__mutmut_15(to: str, full_name: str):
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
    await _send(to, "Signal.Trade — Payment failed", html, )


async def x_send_payment_failed__mutmut_16(to: str, full_name: str):
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
    await _send(to, "XXSignal.Trade — Payment failedXX", html, plain)


async def x_send_payment_failed__mutmut_17(to: str, full_name: str):
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
    await _send(to, "signal.trade — payment failed", html, plain)


async def x_send_payment_failed__mutmut_18(to: str, full_name: str):
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
    await _send(to, "SIGNAL.TRADE — PAYMENT FAILED", html, plain)

mutants_x_send_payment_failed__mutmut['_mutmut_orig'] = x_send_payment_failed__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_1'] = x_send_payment_failed__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_2'] = x_send_payment_failed__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_3'] = x_send_payment_failed__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_4'] = x_send_payment_failed__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_5'] = x_send_payment_failed__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_6'] = x_send_payment_failed__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_7'] = x_send_payment_failed__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_8'] = x_send_payment_failed__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_9'] = x_send_payment_failed__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_10'] = x_send_payment_failed__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_11'] = x_send_payment_failed__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_12'] = x_send_payment_failed__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_13'] = x_send_payment_failed__mutmut_13 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_14'] = x_send_payment_failed__mutmut_14 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_15'] = x_send_payment_failed__mutmut_15 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_16'] = x_send_payment_failed__mutmut_16 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_17'] = x_send_payment_failed__mutmut_17 # type: ignore # mutmut generated
mutants_x_send_payment_failed__mutmut['x_send_payment_failed__mutmut_18'] = x_send_payment_failed__mutmut_18 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_subscription_canceled__mutmut)
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


async def x_send_subscription_canceled__mutmut_orig(to: str, full_name: str, period_end: str):
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


async def x_send_subscription_canceled__mutmut_1(to: str, full_name: str, period_end: str):
    name = None
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


async def x_send_subscription_canceled__mutmut_2(to: str, full_name: str, period_end: str):
    name = full_name and to.split("@")[0]
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


async def x_send_subscription_canceled__mutmut_3(to: str, full_name: str, period_end: str):
    name = full_name or to.split(None)[0]
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


async def x_send_subscription_canceled__mutmut_4(to: str, full_name: str, period_end: str):
    name = full_name or to.split("XX@XX")[0]
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


async def x_send_subscription_canceled__mutmut_5(to: str, full_name: str, period_end: str):
    name = full_name or to.split("@")[1]
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


async def x_send_subscription_canceled__mutmut_6(to: str, full_name: str, period_end: str):
    name = full_name or to.split("@")[0]
    html = None
    plain = f"Hey {name}, your Signal.Trade subscription is canceled. Access continues until {period_end}."
    await _send(to, "Signal.Trade — Subscription canceled", html, plain)


async def x_send_subscription_canceled__mutmut_7(to: str, full_name: str, period_end: str):
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
    plain = None
    await _send(to, "Signal.Trade — Subscription canceled", html, plain)


async def x_send_subscription_canceled__mutmut_8(to: str, full_name: str, period_end: str):
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
    await _send(None, "Signal.Trade — Subscription canceled", html, plain)


async def x_send_subscription_canceled__mutmut_9(to: str, full_name: str, period_end: str):
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
    await _send(to, None, html, plain)


async def x_send_subscription_canceled__mutmut_10(to: str, full_name: str, period_end: str):
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
    await _send(to, "Signal.Trade — Subscription canceled", None, plain)


async def x_send_subscription_canceled__mutmut_11(to: str, full_name: str, period_end: str):
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
    await _send(to, "Signal.Trade — Subscription canceled", html, None)


async def x_send_subscription_canceled__mutmut_12(to: str, full_name: str, period_end: str):
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
    await _send("Signal.Trade — Subscription canceled", html, plain)


async def x_send_subscription_canceled__mutmut_13(to: str, full_name: str, period_end: str):
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
    await _send(to, html, plain)


async def x_send_subscription_canceled__mutmut_14(to: str, full_name: str, period_end: str):
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
    await _send(to, "Signal.Trade — Subscription canceled", plain)


async def x_send_subscription_canceled__mutmut_15(to: str, full_name: str, period_end: str):
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
    await _send(to, "Signal.Trade — Subscription canceled", html, )


async def x_send_subscription_canceled__mutmut_16(to: str, full_name: str, period_end: str):
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
    await _send(to, "XXSignal.Trade — Subscription canceledXX", html, plain)


async def x_send_subscription_canceled__mutmut_17(to: str, full_name: str, period_end: str):
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
    await _send(to, "signal.trade — subscription canceled", html, plain)


async def x_send_subscription_canceled__mutmut_18(to: str, full_name: str, period_end: str):
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
    await _send(to, "SIGNAL.TRADE — SUBSCRIPTION CANCELED", html, plain)

mutants_x_send_subscription_canceled__mutmut['_mutmut_orig'] = x_send_subscription_canceled__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_1'] = x_send_subscription_canceled__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_2'] = x_send_subscription_canceled__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_3'] = x_send_subscription_canceled__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_4'] = x_send_subscription_canceled__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_5'] = x_send_subscription_canceled__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_6'] = x_send_subscription_canceled__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_7'] = x_send_subscription_canceled__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_8'] = x_send_subscription_canceled__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_9'] = x_send_subscription_canceled__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_10'] = x_send_subscription_canceled__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_11'] = x_send_subscription_canceled__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_12'] = x_send_subscription_canceled__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_13'] = x_send_subscription_canceled__mutmut_13 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_14'] = x_send_subscription_canceled__mutmut_14 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_15'] = x_send_subscription_canceled__mutmut_15 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_16'] = x_send_subscription_canceled__mutmut_16 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_17'] = x_send_subscription_canceled__mutmut_17 # type: ignore # mutmut generated
mutants_x_send_subscription_canceled__mutmut['x_send_subscription_canceled__mutmut_18'] = x_send_subscription_canceled__mutmut_18 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_weekly_digest__mutmut)
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_orig(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_1(
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
    wr_row = None
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_2(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_3(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else "XXXX"
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_4(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = None
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_5(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_6(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else "XXXX"
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_7(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = None
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_8(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_9(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else "XXXX"
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_10(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = None
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_11(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else "XXXX"
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_12(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = None
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_13(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else "XXXX"
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_14(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
    no_data = None
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_15(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
    no_data = "XX<p>No resolved outcomes yet — check back next week.</p>XX" if win_rate is None else ""
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_16(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
    no_data = "<p>no resolved outcomes yet — check back next week.</p>" if win_rate is None else ""
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_17(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
    no_data = "<P>NO RESOLVED OUTCOMES YET — CHECK BACK NEXT WEEK.</P>" if win_rate is None else ""
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_18(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
    no_data = "<p>No resolved outcomes yet — check back next week.</p>" if win_rate is not None else ""
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_19(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
    no_data = "<p>No resolved outcomes yet — check back next week.</p>" if win_rate is None else "XXXX"
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_20(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
    no_data = "<p>No resolved outcomes yet — check back next week.</p>" if win_rate is None else ""
    html = None
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_21(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = None
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_22(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_23(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(None)
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_24(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_25(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            None
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_26(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" - (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_27(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_28(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "XXXX")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_29(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(None)
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_30(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(None)
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_31(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(None, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_32(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, None, html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_33(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", None, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_34(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, None)


async def x_send_weekly_digest__mutmut_35(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_36(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, html, "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_37(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", "\n".join(plain_lines))


async def x_send_weekly_digest__mutmut_38(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, )


async def x_send_weekly_digest__mutmut_39(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "\n".join(None))


async def x_send_weekly_digest__mutmut_40(
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
    wr_row = (
        f"<tr><td>Win rate</td><td><strong>{win_rate}%</strong> ({wins}/{resolved} resolved)</td></tr>"
        if win_rate is not None
        else ""
    )
    spy_str = (
        f' <span style="color:#6b7280;font-size:12px">(vs SPY {spy_ret:+.2f}%)</span>' if spy_ret is not None else ""
    )
    ar_row = (
        f"<tr><td>Avg return</td><td><strong>{avg_ret:+.2f}%</strong>{spy_str}</td></tr>" if avg_ret is not None else ""
    )
    best_row = (
        f"<tr><td>Best signal</td><td><strong>{best_ticker}</strong> +{best_ret:.1f}%</td></tr>" if best_ticker else ""
    )
    worst_row = (
        f"<tr><td>Worst signal</td><td><strong>{worst_ticker}</strong> {worst_ret:.1f}%</td></tr>"
        if worst_ticker
        else ""
    )
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
    plain_lines = [f"Signal.Trade — Weekly Digest\nWeek ending {week_ending}\n", f"Signals sent: {sent}"]
    if win_rate is not None:
        plain_lines.append(f"Win rate: {win_rate}% ({wins}/{resolved} resolved)")
    if avg_ret is not None:
        plain_lines.append(
            f"Avg return: {avg_ret:+.2f}%" + (f" (vs SPY {spy_ret:+.2f}%)" if spy_ret is not None else "")
        )
    if best_ticker:
        plain_lines.append(f"Best: {best_ticker} +{best_ret:.1f}%")
    if worst_ticker:
        plain_lines.append(f"Worst: {worst_ticker} {worst_ret:.1f}%")
    await _send(to, f"Signal.Trade — Weekly Digest ({week_ending})", html, "XX\nXX".join(plain_lines))

mutants_x_send_weekly_digest__mutmut['_mutmut_orig'] = x_send_weekly_digest__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_1'] = x_send_weekly_digest__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_2'] = x_send_weekly_digest__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_3'] = x_send_weekly_digest__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_4'] = x_send_weekly_digest__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_5'] = x_send_weekly_digest__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_6'] = x_send_weekly_digest__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_7'] = x_send_weekly_digest__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_8'] = x_send_weekly_digest__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_9'] = x_send_weekly_digest__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_10'] = x_send_weekly_digest__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_11'] = x_send_weekly_digest__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_12'] = x_send_weekly_digest__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_13'] = x_send_weekly_digest__mutmut_13 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_14'] = x_send_weekly_digest__mutmut_14 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_15'] = x_send_weekly_digest__mutmut_15 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_16'] = x_send_weekly_digest__mutmut_16 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_17'] = x_send_weekly_digest__mutmut_17 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_18'] = x_send_weekly_digest__mutmut_18 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_19'] = x_send_weekly_digest__mutmut_19 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_20'] = x_send_weekly_digest__mutmut_20 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_21'] = x_send_weekly_digest__mutmut_21 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_22'] = x_send_weekly_digest__mutmut_22 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_23'] = x_send_weekly_digest__mutmut_23 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_24'] = x_send_weekly_digest__mutmut_24 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_25'] = x_send_weekly_digest__mutmut_25 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_26'] = x_send_weekly_digest__mutmut_26 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_27'] = x_send_weekly_digest__mutmut_27 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_28'] = x_send_weekly_digest__mutmut_28 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_29'] = x_send_weekly_digest__mutmut_29 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_30'] = x_send_weekly_digest__mutmut_30 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_31'] = x_send_weekly_digest__mutmut_31 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_32'] = x_send_weekly_digest__mutmut_32 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_33'] = x_send_weekly_digest__mutmut_33 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_34'] = x_send_weekly_digest__mutmut_34 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_35'] = x_send_weekly_digest__mutmut_35 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_36'] = x_send_weekly_digest__mutmut_36 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_37'] = x_send_weekly_digest__mutmut_37 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_38'] = x_send_weekly_digest__mutmut_38 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_39'] = x_send_weekly_digest__mutmut_39 # type: ignore # mutmut generated
mutants_x_send_weekly_digest__mutmut['x_send_weekly_digest__mutmut_40'] = x_send_weekly_digest__mutmut_40 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_verification_email__mutmut)
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


async def x_send_verification_email__mutmut_orig(to: str, full_name: str, verify_link: str):
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


async def x_send_verification_email__mutmut_1(to: str, full_name: str, verify_link: str):
    name = None
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


async def x_send_verification_email__mutmut_2(to: str, full_name: str, verify_link: str):
    name = full_name and to.split("@")[0]
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


async def x_send_verification_email__mutmut_3(to: str, full_name: str, verify_link: str):
    name = full_name or to.split(None)[0]
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


async def x_send_verification_email__mutmut_4(to: str, full_name: str, verify_link: str):
    name = full_name or to.split("XX@XX")[0]
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


async def x_send_verification_email__mutmut_5(to: str, full_name: str, verify_link: str):
    name = full_name or to.split("@")[1]
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


async def x_send_verification_email__mutmut_6(to: str, full_name: str, verify_link: str):
    name = full_name or to.split("@")[0]
    html = None
    plain = f"Hey {name},\n\nVerify your Signal.Trade email:\n{verify_link}\n\nExpires in 24 hours."
    await _send(to, "Signal.Trade — Verify your email", html, plain)


async def x_send_verification_email__mutmut_7(to: str, full_name: str, verify_link: str):
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
    plain = None
    await _send(to, "Signal.Trade — Verify your email", html, plain)


async def x_send_verification_email__mutmut_8(to: str, full_name: str, verify_link: str):
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
    await _send(None, "Signal.Trade — Verify your email", html, plain)


async def x_send_verification_email__mutmut_9(to: str, full_name: str, verify_link: str):
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
    await _send(to, None, html, plain)


async def x_send_verification_email__mutmut_10(to: str, full_name: str, verify_link: str):
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
    await _send(to, "Signal.Trade — Verify your email", None, plain)


async def x_send_verification_email__mutmut_11(to: str, full_name: str, verify_link: str):
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
    await _send(to, "Signal.Trade — Verify your email", html, None)


async def x_send_verification_email__mutmut_12(to: str, full_name: str, verify_link: str):
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
    await _send("Signal.Trade — Verify your email", html, plain)


async def x_send_verification_email__mutmut_13(to: str, full_name: str, verify_link: str):
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
    await _send(to, html, plain)


async def x_send_verification_email__mutmut_14(to: str, full_name: str, verify_link: str):
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
    await _send(to, "Signal.Trade — Verify your email", plain)


async def x_send_verification_email__mutmut_15(to: str, full_name: str, verify_link: str):
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
    await _send(to, "Signal.Trade — Verify your email", html, )


async def x_send_verification_email__mutmut_16(to: str, full_name: str, verify_link: str):
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
    await _send(to, "XXSignal.Trade — Verify your emailXX", html, plain)


async def x_send_verification_email__mutmut_17(to: str, full_name: str, verify_link: str):
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
    await _send(to, "signal.trade — verify your email", html, plain)


async def x_send_verification_email__mutmut_18(to: str, full_name: str, verify_link: str):
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
    await _send(to, "SIGNAL.TRADE — VERIFY YOUR EMAIL", html, plain)

mutants_x_send_verification_email__mutmut['_mutmut_orig'] = x_send_verification_email__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_1'] = x_send_verification_email__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_2'] = x_send_verification_email__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_3'] = x_send_verification_email__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_4'] = x_send_verification_email__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_5'] = x_send_verification_email__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_6'] = x_send_verification_email__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_7'] = x_send_verification_email__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_8'] = x_send_verification_email__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_9'] = x_send_verification_email__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_10'] = x_send_verification_email__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_11'] = x_send_verification_email__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_12'] = x_send_verification_email__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_13'] = x_send_verification_email__mutmut_13 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_14'] = x_send_verification_email__mutmut_14 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_15'] = x_send_verification_email__mutmut_15 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_16'] = x_send_verification_email__mutmut_16 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_17'] = x_send_verification_email__mutmut_17 # type: ignore # mutmut generated
mutants_x_send_verification_email__mutmut['x_send_verification_email__mutmut_18'] = x_send_verification_email__mutmut_18 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_send_password_reset__mutmut)
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


async def x_send_password_reset__mutmut_orig(to: str, reset_link: str):
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


async def x_send_password_reset__mutmut_1(to: str, reset_link: str):
    html = None
    plain = f"Reset your Signal.Trade password: {reset_link}\n\nExpires in 1 hour."
    await _send(to, "Signal.Trade — Password reset", html, plain)


async def x_send_password_reset__mutmut_2(to: str, reset_link: str):
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
    plain = None
    await _send(to, "Signal.Trade — Password reset", html, plain)


async def x_send_password_reset__mutmut_3(to: str, reset_link: str):
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
    await _send(None, "Signal.Trade — Password reset", html, plain)


async def x_send_password_reset__mutmut_4(to: str, reset_link: str):
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
    await _send(to, None, html, plain)


async def x_send_password_reset__mutmut_5(to: str, reset_link: str):
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
    await _send(to, "Signal.Trade — Password reset", None, plain)


async def x_send_password_reset__mutmut_6(to: str, reset_link: str):
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
    await _send(to, "Signal.Trade — Password reset", html, None)


async def x_send_password_reset__mutmut_7(to: str, reset_link: str):
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
    await _send("Signal.Trade — Password reset", html, plain)


async def x_send_password_reset__mutmut_8(to: str, reset_link: str):
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
    await _send(to, html, plain)


async def x_send_password_reset__mutmut_9(to: str, reset_link: str):
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
    await _send(to, "Signal.Trade — Password reset", plain)


async def x_send_password_reset__mutmut_10(to: str, reset_link: str):
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
    await _send(to, "Signal.Trade — Password reset", html, )


async def x_send_password_reset__mutmut_11(to: str, reset_link: str):
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
    await _send(to, "XXSignal.Trade — Password resetXX", html, plain)


async def x_send_password_reset__mutmut_12(to: str, reset_link: str):
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
    await _send(to, "signal.trade — password reset", html, plain)


async def x_send_password_reset__mutmut_13(to: str, reset_link: str):
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
    await _send(to, "SIGNAL.TRADE — PASSWORD RESET", html, plain)

mutants_x_send_password_reset__mutmut['_mutmut_orig'] = x_send_password_reset__mutmut_orig # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_1'] = x_send_password_reset__mutmut_1 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_2'] = x_send_password_reset__mutmut_2 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_3'] = x_send_password_reset__mutmut_3 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_4'] = x_send_password_reset__mutmut_4 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_5'] = x_send_password_reset__mutmut_5 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_6'] = x_send_password_reset__mutmut_6 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_7'] = x_send_password_reset__mutmut_7 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_8'] = x_send_password_reset__mutmut_8 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_9'] = x_send_password_reset__mutmut_9 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_10'] = x_send_password_reset__mutmut_10 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_11'] = x_send_password_reset__mutmut_11 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_12'] = x_send_password_reset__mutmut_12 # type: ignore # mutmut generated
mutants_x_send_password_reset__mutmut['x_send_password_reset__mutmut_13'] = x_send_password_reset__mutmut_13 # type: ignore # mutmut generated
