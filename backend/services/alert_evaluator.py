import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import PriceAlert, User
from services.market_data import get_info
from services.telegram_svc import send_telegram

log = logging.getLogger("signal.trade.alerts")

async def evaluate_price_alerts(db: AsyncSession):
    """
    Evaluates all active price alerts against current market prices.
    Should be called periodically via background task in main.py.
    """
    # Fetch all active alerts
    result = await db.execute(select(PriceAlert).where(PriceAlert.is_active == True))
    alerts = result.scalars().all()
    
    if not alerts:
        return
        
    # Group by ticker to minimize API calls
    tickers = list(set(a.ticker for a in alerts))
    
    for ticker in tickers:
        try:
            info = await get_info(ticker)
            current_price = info.get("price")
            if not current_price:
                continue
                
            # Check alerts for this ticker
            ticker_alerts = [a for a in alerts if a.ticker == ticker]
            for alert in ticker_alerts:
                triggered = False
                if alert.condition == "above" and current_price >= alert.target_price:
                    triggered = True
                elif alert.condition == "below" and current_price <= alert.target_price:
                    triggered = True
                    
                if triggered:
                    user = await db.get(User, alert.user_id)
                    if user and user.telegram_chat_id:
                        msg = f"🔔 *PRICE ALERT* 🔔\n\n{ticker} has crossed your target of ${alert.target_price:.2f}. Current price: ${current_price:.2f}."
                        # Logic to trigger Telegram or push notification here
                    alert.is_active = False # Deactivate after triggering
        except Exception as e:
            log.error(f"Failed to evaluate alert for {ticker}: {e}")
            
    await db.commit()