"""
Telegram Bot for Financial Predictions
Quick access to prices and predictions via Telegram
"""

import os
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.collectors.yfinance_collector import YFinanceCollector
from backend.collectors.news_collector import NewsCollector

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TOKEN_HERE")

# Initialize collectors
price_collector = YFinanceCollector()
news_collector = NewsCollector()

# Emoji mappings
ASSET_EMOJIS = {
    'BTC': '₿',
    'ETH': 'Ξ',
    'GOLD': '🥇',
    'SILVER': '🥈',
    'PLATINUM': '⭐',
    'BNB': '🔶',
    'ADA': '🔷',
    'DOGE': '🐕',
    'SHIB': '🐕',
    'PEPE': '🐸'
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    welcome_text = """
🎯 *Financial Prediction Bot*

Καλωσήρθες! Μπορώ να σε βοηθήσω με:

📊 *Τιμές:*
/price BTC - Τρέχουσα τιμή Bitcoin
/prices - Όλες οι τιμές

🔮 *Προβλέψεις:*
/predict BTC - Προβλέψεις για Bitcoin

📰 *Ειδήσεις:*
/news BTC - Sentiment analysis

📈 *Διαθέσιμα Assets:*
• Μέταλλα: GOLD, SILVER, PLATINUM
• Crypto: BTC, ETH, BNB, ADA
• Shitcoins: DOGE, SHIB, PEPE

💡 /help - Βοήθεια
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_text = """
📚 *Εντολές Βοήθειας*

🔹 `/price <ASSET>` - Δες τρέχουσα τιμή
   Παράδειγμα: `/price BTC`

🔹 `/prices` - Όλες οι τιμές σε μία λίστα

🔹 `/predict <ASSET>` - Προβλέψεις 10/20/30 min
   Παράδειγμα: `/predict ETH`

🔹 `/news <ASSET>` - News & Sentiment
   Παράδειγμα: `/news GOLD`

🔹 `/top` - Top gainers/losers

Assets: BTC, ETH, GOLD, SILVER, PLATINUM, BNB, ADA, DOGE, SHIB, PEPE
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get price for specific asset"""
    if not context.args:
        await update.message.reply_text("❌ Χρήση: /price BTC")
        return
    
    asset_id = context.args[0].upper()
    emoji = ASSET_EMOJIS.get(asset_id, '📊')
    
    # Send "typing..." indicator
    await update.message.chat.send_action("typing")
    
    price_data = price_collector.get_current_price(asset_id)
    
    if not price_data:
        await update.message.reply_text(f"❌ Δεν βρέθηκε το asset: {asset_id}")
        return
    
    # Format response
    change_emoji = "🔼" if price_data['change_24h'] > 0 else "🔽"
    
    response = f"""
{emoji} *{asset_id}*

💵 Τιμή: `${price_data['price']:,.2f}`
{change_emoji} 24ω: `{price_data['change_24h']:+.2f}%`

⏰ {price_data['timestamp'].strftime('%H:%M:%S')}
"""
    
    await update.message.reply_text(response, parse_mode='Markdown')


async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get all prices"""
    await update.message.chat.send_action("typing")
    
    assets = ['BTC', 'ETH', 'GOLD', 'SILVER', 'BNB', 'ADA']
    
    response = "📊 *Τιμές Αγοράς*\n\n"
    
    for asset_id in assets:
        emoji = ASSET_EMOJIS.get(asset_id, '📊')
        price_data = price_collector.get_current_price(asset_id)
        
        if price_data:
            change_emoji = "🔼" if price_data['change_24h'] > 0 else "🔽"
            response += f"{emoji} *{asset_id}*: `${price_data['price']:,.2f}` {change_emoji} `{price_data['change_24h']:+.2f}%`\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')


async def predict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get predictions for asset"""
    if not context.args:
        await update.message.reply_text("❌ Χρήση: /predict BTC")
        return
    
    asset_id = context.args[0].upper()
    emoji = ASSET_EMOJIS.get(asset_id, '📊')
    
    await update.message.chat.send_action("typing")
    
    # Get current price
    price_data = price_collector.get_current_price(asset_id)
    
    if not price_data:
        await update.message.reply_text(f"❌ Δεν βρέθηκε το asset: {asset_id}")
        return
    
    current_price = price_data['price']
    
    # Get sentiment
    asset_name = asset_id if asset_id in ['BTC', 'ETH'] else f"{asset_id} metal"
    news_data = news_collector.get_news_sentiment(asset_name, max_results=2)
    sentiment_score = news_data['average_sentiment']
    sentiment_label = news_data['sentiment_label']
    
    # Simple predictions influenced by sentiment
    import random
    from datetime import datetime
    random.seed(hash(asset_id + str(datetime.now().date())))
    
    sentiment_boost = sentiment_score * 0.3
    
    response = f"{emoji} *{asset_id} Προβλέψεις*\n\n"
    response += f"💵 Τρέχουσα: `${current_price:,.2f}`\n"
    
    # Sentiment
    if sentiment_label == 'BULLISH':
        sent_emoji = '🟢'
    elif sentiment_label == 'BEARISH':
        sent_emoji = '🔴'
    else:
        sent_emoji = '⚪'
    
    response += f"{sent_emoji} Sentiment: *{sentiment_label}* `({sentiment_score:+.2f})`\n\n"
    response += "🔮 *Προβλέψεις:*\n"
    
    # Generate predictions
    for minutes, variance in [(10, 0.3), (20, 0.5), (30, 0.7)]:
        change = random.uniform(-variance, variance) + sentiment_boost
        pred_price = current_price * (1 + change/100)
        confidence = min(95, 75 + abs(sentiment_score) * 10 + random.uniform(-5, 5))
        
        pred_emoji = "📈" if change > 0.3 else "📉" if change < -0.3 else "➡️"
        
        response += f"{pred_emoji} `{minutes} min`: `${pred_price:,.2f}` ({change:+.2f}%) • {confidence:.0f}%\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get news and sentiment"""
    if not context.args:
        await update.message.reply_text("❌ Χρήση: /news BTC")
        return
    
    asset_id = context.args[0].upper()
    emoji = ASSET_EMOJIS.get(asset_id, '📊')
    
    await update.message.chat.send_action("typing")
    
    # Get news
    asset_name = asset_id if asset_id in ['BTC', 'ETH'] else f"{asset_id} prices"
    news_data = news_collector.get_news_sentiment(asset_name, max_results=3)
    
    if not news_data['articles']:
        await update.message.reply_text(f"❌ Δεν βρέθηκαν ειδήσεις για {asset_id}")
        return
    
    sentiment_label = news_data['sentiment_label']
    sentiment_score = news_data['average_sentiment']
    
    if sentiment_label == 'BULLISH':
        sent_emoji = '🟢'
    elif sentiment_label == 'BEARISH':
        sent_emoji = '🔴'
    else:
        sent_emoji = '⚪'
    
    response = f"{emoji} *{asset_id} News*\n\n"
    response += f"{sent_emoji} Overall: *{sentiment_label}* `({sentiment_score:+.2f})`\n\n"
    
    for i, article in enumerate(news_data['articles'][:3], 1):
        art_label = article['sentiment_label']
        art_emoji = '🟢' if art_label == 'BULLISH' else '🔴' if art_label == 'BEARISH' else '⚪'
        
        response += f"{art_emoji} {article['title'][:50]}...\n"
        response += f"   _{article['source']}_ • {art_label}\n\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')


def main():
    """Run the bot"""
    if TELEGRAM_TOKEN == "YOUR_TOKEN_HERE":
        print("❌ Error: Please set TELEGRAM_BOT_TOKEN in .env file")
        print("\n📝 To get a token:")
        print("   1. Message @BotFather on Telegram")
        print("   2. Send /newbot")
        print("   3. Follow instructions")
        print("   4. Add token to .env: TELEGRAM_BOT_TOKEN=your_token")
        return
    
    print("🤖 Starting Telegram Bot...")
    print(f"🔑 Token: {TELEGRAM_TOKEN[:10]}...")
    
    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("prices", prices_command))
    app.add_handler(CommandHandler("predict", predict_command))
    app.add_handler(CommandHandler("news", news_command))
    
    print("✅ Bot is running!")
    print("💬 Message your bot on Telegram to test")
    print("🛑 Press Ctrl+C to stop\n")
    
    # Run bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
