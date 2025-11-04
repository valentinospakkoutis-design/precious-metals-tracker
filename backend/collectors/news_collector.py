"""
News & Sentiment Collector
Fetches news articles and analyzes sentiment
"""

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

class NewsCollector:
    def __init__(self):
        self.api_key = NEWSAPI_KEY
        self.base_url = "https://newsapi.org/v2/everything"
    
    def get_news(self, query, max_results=5):
        """Fetch news articles for a query"""
        if not self.api_key:
            return []
        
        params = {
            'q': query,
            'apiKey': self.api_key,
            'pageSize': max_results,
            'language': 'en',
            'sortBy': 'publishedAt'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                results = []
                for article in articles:
                    results.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                    })
                
                return results
            else:
                print(f"News API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def simple_sentiment(self, text):
        """Simple sentiment analysis based on keywords"""
        if not text:
            return 0, 'neutral'
        
        text_lower = text.lower()
        
        # Positive keywords
        positive_words = [
            'surge', 'soar', 'rally', 'gain', 'rise', 'up', 'bull', 'bullish',
            'growth', 'profit', 'success', 'breakthrough', 'positive', 'optimistic',
            'record', 'high', 'boom', 'recovery', 'strong'
        ]
        
        # Negative keywords
        negative_words = [
            'crash', 'plunge', 'fall', 'drop', 'decline', 'down', 'bear', 'bearish',
            'loss', 'failure', 'negative', 'pessimistic', 'concern', 'risk',
            'low', 'weak', 'recession', 'crisis'
        ]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0, 'neutral'
        
        score = (pos_count - neg_count) / total
        
        if score > 0.3:
            label = 'bullish'
        elif score < -0.3:
            label = 'bearish'
        else:
            label = 'neutral'
        
        return round(score, 2), label
    
    def get_news_sentiment(self, query, max_results=5):
        """Get news with sentiment analysis"""
        articles = self.get_news(query, max_results)
        
        if not articles:
            return {
                'articles': [],
                'average_sentiment': 0,
                'sentiment_label': 'NEUTRAL'
            }
        
        # Analyze sentiment for each article
        analyzed_articles = []
        all_scores = []
        
        for article in articles:
            text = f"{article['title']} {article['description']}"
            score, label = self.simple_sentiment(text)
            
            article['sentiment_score'] = score
            article['sentiment_label'] = label.upper()
            analyzed_articles.append(article)
            all_scores.append(score)
        
        # Calculate average
        avg_sentiment = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Determine overall label
        if avg_sentiment > 0.2:
            overall_label = 'BULLISH'
        elif avg_sentiment < -0.2:
            overall_label = 'BEARISH'
        else:
            overall_label = 'NEUTRAL'
        
        return {
            'articles': analyzed_articles,
            'average_sentiment': round(avg_sentiment, 2),
            'sentiment_label': overall_label
        }


def demo_news_sentiment():
    """Demo news collection and sentiment"""
    print("=" * 70)
    print("📰 NEWS & SENTIMENT ANALYSIS - Demo")
    print("=" * 70)
    print()
    
    collector = NewsCollector()
    
    assets = {
        'Bitcoin': '🪙',
        'Ethereum': '⟠',
        'Gold': '🥇',
    }
    
    for asset, emoji in assets.items():
        print(f"\n{emoji} {asset}")
        print("-" * 70)
        
        articles = collector.get_news(asset, max_results=3)
        
        if articles:
            all_scores = []
            
            for i, article in enumerate(articles, 1):
                text = f"{article['title']} {article['description']}"
                score, label = collector.simple_sentiment(text)
                all_scores.append(score)
                
                # Emoji for sentiment
                if label == 'bullish':
                    emoji_sent = '🔼'
                elif label == 'bearish':
                    emoji_sent = '🔽'
                else:
                    emoji_sent = '➖'
                
                print(f"\n   {i}. {emoji_sent} {label.upper()} ({score:+.2f})")
                print(f"      {article['title'][:60]}...")
                print(f"      {article['source']} • {article['published_at'][:10]}")
            
            # Overall sentiment
            if all_scores:
                avg_score = sum(all_scores) / len(all_scores)
                if avg_score > 0.2:
                    overall = "🔼 BULLISH"
                elif avg_score < -0.2:
                    overall = "🔽 BEARISH"
                else:
                    overall = "➖ NEUTRAL"
                
                print(f"\n   📊 Overall Sentiment: {overall} ({avg_score:+.2f})")
        else:
            print("   ❌ No articles found")
    
    print("\n" + "=" * 70)
    print("✅ News & Sentiment Analysis Complete!")
    print("\n💡 Sentiment Score:")
    print("   +1.0 = Very Bullish")
    print("    0.0 = Neutral")
    print("   -1.0 = Very Bearish")
    print("=" * 70)


if __name__ == "__main__":
    demo_news_sentiment()
