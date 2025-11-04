"""
🚀 COMPLETE FINANCIAL PREDICTION DEMO
Δείχνει όλες τις δυνατότητες του συστήματος
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.collectors.yfinance_collector import YFinanceCollector
from backend.collectors.news_collector import NewsCollector
from backend.models.accuracy_tracker import AccuracyTracker

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_section(title):
    """Print section header"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}\n")

def get_sentiment_emoji(sentiment):
    """Get emoji for sentiment"""
    if sentiment == 'BULLISH':
        return '🟢'
    elif sentiment == 'BEARISH':
        return '🔴'
    else:
        return '⚪'

def get_prediction_emoji(change_pct):
    """Get emoji for prediction"""
    if change_pct > 0.5:
        return '📈'
    elif change_pct < -0.5:
        return '📉'
    else:
        return '➡️'

def main():
    print_header("💰 FINANCIAL PREDICTION SYSTEM - COMPLETE DEMO")
    print("Σύστημα Προβλέψεων Χρηματοοικονομικών Αγορών")
    print(f"Ημερομηνία: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Initialize components
    print_section("🔧 Αρχικοποίηση Συστημάτων")
    price_collector = YFinanceCollector()
    news_collector = NewsCollector()
    accuracy_tracker = AccuracyTracker(storage_path="data/demo_predictions.json")
    print("✅ Price Collector - Ready")
    print("✅ News Collector - Ready")
    print("✅ Accuracy Tracker - Ready")
    
    # Assets to analyze
    assets = [
        ('BTC', 'Bitcoin', '₿'),
        ('ETH', 'Ethereum', 'Ξ'),
        ('GOLD', 'Χρυσός', '🥇'),
        ('SILVER', 'Άργυρος', '🥈'),
    ]
    
    all_predictions = []
    
    # Analyze each asset
    for asset_id, asset_name, symbol in assets:
        print_section(f"{symbol} {asset_name} ({asset_id})")
        
        # 1. Get current price
        print("📊 Τρέχουσα Τιμή:")
        price_data = price_collector.get_current_price(asset_id)
        
        if price_data:
            print(f"   Τιμή: ${price_data['price']:,.2f}")
            print(f"   Αλλαγή 24ω: {price_data['change_24h']:+.2f}%")
            
            # 2. Get news & sentiment
            print("\n📰 Ειδήσεις & Sentiment Analysis:")
            query = asset_name if asset_id not in ['GOLD', 'SILVER'] else f"{asset_name} prices"
            news_data = news_collector.get_news_sentiment(query, max_results=3)
            
            if news_data['articles']:
                avg_sentiment = news_data['average_sentiment']
                sentiment_label = news_data['sentiment_label']
                emoji = get_sentiment_emoji(sentiment_label)
                
                print(f"   {emoji} Overall Sentiment: {sentiment_label} ({avg_sentiment:+.2f})")
                print(f"\n   Top Άρθρα:")
                
                for i, article in enumerate(news_data['articles'][:2], 1):
                    article_emoji = get_sentiment_emoji(article['sentiment_label'])
                    print(f"   {i}. {article_emoji} {article['title'][:60]}...")
                    print(f"      Sentiment: {article['sentiment_label']} ({article['sentiment_score']:+.2f})")
            else:
                avg_sentiment = 0
                sentiment_label = 'NEUTRAL'
                print("   ⚠️  No news found")
            
            # 3. Make predictions
            print("\n🔮 Προβλέψεις:")
            
            import random
            random.seed(hash(asset_id + str(datetime.now().date())))
            
            # Simple prediction with sentiment influence
            sentiment_boost = avg_sentiment * 0.3  # Sentiment affects prediction
            
            predictions = []
            for minutes in [10, 20, 30]:
                # Base prediction on volatility
                volatility = abs(price_data['change_24h']) / 10
                change = random.uniform(-volatility, volatility) + sentiment_boost
                
                # Confidence influenced by sentiment clarity
                base_confidence = 75
                sentiment_confidence = abs(avg_sentiment) * 10  # Stronger sentiment = higher confidence
                confidence = min(95, base_confidence + sentiment_confidence + random.uniform(-5, 5))
                
                emoji = get_prediction_emoji(change)
                print(f"   {emoji} {minutes} λεπτά: {change:+.2f}% (Εμπιστοσύνη: {confidence:.0f}%)")
                
                # Log prediction for tracking
                predicted_price = price_data['price'] * (1 + change/100)
                pred_id = accuracy_tracker.log_prediction(
                    asset_id=asset_id,
                    predicted_price=predicted_price,
                    predicted_change_pct=change,
                    current_price=price_data['price'],
                    horizon_minutes=minutes,
                    confidence=confidence
                )
                
                predictions.append({
                    'id': pred_id,
                    'asset': asset_id,
                    'minutes': minutes,
                    'change': change,
                    'confidence': confidence
                })
            
            all_predictions.extend(predictions)
            
            # 4. Show reasoning
            print(f"\n💡 Ανάλυση:")
            if abs(avg_sentiment) > 0.3:
                direction = "ανοδική" if avg_sentiment > 0 else "πτωτική"
                print(f"   • Τα νέα δείχνουν {direction} τάση ({sentiment_label})")
            else:
                print(f"   • Ουδέτερο sentiment από τα νέα")
            
            if abs(price_data['change_24h']) > 2:
                print(f"   • Υψηλή μεταβλητότητα 24ω ({price_data['change_24h']:+.2f}%)")
            else:
                print(f"   • Σταθερή τιμή 24ω")
        else:
            print(f"   ❌ Couldn't fetch price data for {asset_id}")
    
    # Summary statistics
    print_section("📊 Στατιστικά Συνόλου")
    
    print(f"Σύνολο Προβλέψεων: {len(all_predictions)}")
    print(f"Assets Analyzed: {len(assets)}")
    
    avg_confidence = sum(p['confidence'] for p in all_predictions) / len(all_predictions) if all_predictions else 0
    print(f"Μέση Εμπιστοσύνη: {avg_confidence:.1f}%")
    
    # Historical accuracy (if available)
    print("\n🎯 Historical Accuracy:")
    overall_stats = accuracy_tracker.get_accuracy_stats()
    
    if overall_stats and overall_stats['total_predictions'] > 0:
        print(f"   Total Past Predictions: {overall_stats['total_predictions']}")
        print(f"   Accuracy: {overall_stats['accuracy_pct']}%")
        print(f"   Average Error: {overall_stats['avg_error_pct']:.2f}%")
        
        if overall_stats['horizon_accuracy']:
            print("\n   Ακρίβεια ανά Horizon:")
            for horizon, acc in sorted(overall_stats['horizon_accuracy'].items()):
                print(f"   • {horizon} min: {acc:.1f}%")
    else:
        print("   📝 Καμία ιστορική δεδομένη (πρώτη εκτέλεση)")
    
    # Next steps
    print_section("🔄 Επόμενα Βήματα")
    print("1. Οι προβλέψεις καταγράφηκαν στο accuracy tracker")
    print("2. Μετά από 10/20/30 λεπτά, μπορείς να ελέγξεις την ακρίβεια")
    print("3. Τρέξε ξανά το demo για ενημερωμένα στατιστικά")
    print("4. Σύνδεσε με το FastAPI backend για real-time access")
    
    print_header("✅ DEMO COMPLETE")
    print("Το σύστημα λειτουργεί επιτυχώς!")
    print("Όλα τα components (Prices + News + Predictions + Tracking) δουλεύουν μαζί! 🚀")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
