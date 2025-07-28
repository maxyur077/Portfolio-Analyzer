# utils/news_fetcher.py
import requests
import logging
from datetime import datetime, timedelta

class NewsFetcher:
    def __init__(self):
        # Your actual API key
        self.api_key = "39f68a23270241e09975199fd6399f6e"
        self.base_url = "https://newsapi.org/v2/everything"
    
    def get_stock_news(self, symbol, days_back=7):
        """Fetch recent news for a stock symbol"""
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            params = {
                'q': f'{symbol} stock OR {symbol} earnings OR {symbol} company',
                'from': from_date,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'language': 'en',
                'pageSize': 5
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Clean and format articles
                cleaned_articles = []
                for article in articles:
                    cleaned_articles.append({
                        'title': article.get('title', 'No title'),
                        'description': article.get('description', 'No description'),
                        'url': article.get('url', ''),
                        'publishedAt': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'urlToImage': article.get('urlToImage', '')
                    })
                
                return cleaned_articles
            else:
                logging.error(f"News API error: {response.status_code}")
                return self._get_mock_news(symbol)
                
        except Exception as e:
            logging.error(f"Error fetching news for {symbol}: {e}")
            return self._get_mock_news(symbol)
    
    def _get_mock_news(self, symbol):
        """Return mock news data when API fails"""
        return [
            {
                'title': f'{symbol} Stock Analysis: Recent Performance Update',
                'description': f'Latest analysis and market performance insights for {symbol} stock.',
                'url': '#',
                'publishedAt': datetime.now().isoformat(),
                'source': 'Portfolio Analyzer',
                'urlToImage': ''
            },
            {
                'title': f'{symbol} Quarterly Earnings Report',
                'description': f'Key highlights from {symbol}\'s recent quarterly earnings and future outlook.',
                'url': '#',
                'publishedAt': (datetime.now() - timedelta(days=1)).isoformat(),
                'source': 'Financial News',
                'urlToImage': ''
            }
        ]
    
    def get_portfolio_news(self, symbols, max_articles_per_symbol=3):
        """Get news for multiple symbols"""
        all_news = {}
        
        for symbol in symbols[:10]:  # Limit to top 10 holdings to avoid rate limits
            try:
                news = self.get_stock_news(symbol, days_back=7)
                if news:
                    all_news[symbol] = news[:max_articles_per_symbol]
                    
                # Add small delay to avoid hitting rate limits
                import time
                time.sleep(0.1)
                
            except Exception as e:
                logging.error(f"Error getting news for {symbol}: {e}")
                continue
        
        return all_news
    
    def get_market_news(self):
        """Get general market news"""
        try:
            from_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
            
            params = {
                'q': 'stock market OR investing OR portfolio OR finance',
                'from': from_date,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'language': 'en',
                'pageSize': 8
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Clean and format articles
                cleaned_articles = []
                for article in articles[:8]:
                    cleaned_articles.append({
                        'title': article.get('title', 'No title'),
                        'description': article.get('description', 'No description'),
                        'url': article.get('url', ''),
                        'publishedAt': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'urlToImage': article.get('urlToImage', '')
                    })
                
                return cleaned_articles
            else:
                logging.error(f"Market news API error: {response.status_code}")
                return self._get_mock_market_news()
                
        except Exception as e:
            logging.error(f"Error fetching market news: {e}")
            return self._get_mock_market_news()
    
    def _get_mock_market_news(self):
        """Return mock market news when API fails"""
        return [
            {
                'title': 'Market Analysis: Portfolio Diversification Strategies',
                'description': 'Expert insights on building a well-diversified investment portfolio.',
                'url': '#',
                'publishedAt': datetime.now().isoformat(),
                'source': 'Investment Weekly',
                'urlToImage': ''
            },
            {
                'title': 'Stock Market Update: Key Trends to Watch',
                'description': 'Latest market trends and investment opportunities for informed investors.',
                'url': '#',
                'publishedAt': (datetime.now() - timedelta(hours=6)).isoformat(),
                'source': 'Market Watch',
                'urlToImage': ''
            },
            {
                'title': 'Quarterly Earnings Season: What to Expect',
                'description': 'Analysis of upcoming earnings reports and their potential market impact.',
                'url': '#',
                'publishedAt': (datetime.now() - timedelta(hours=12)).isoformat(),
                'source': 'Financial Times',
                'urlToImage': ''
            },
            {
                'title': 'Investment Tips: Building Long-term Wealth',
                'description': 'Strategic advice for creating sustainable investment portfolios.',
                'url': '#',
                'publishedAt': (datetime.now() - timedelta(days=1)).isoformat(),
                'source': 'Wealth Management',
                'urlToImage': ''
            }
        ]
    
    def get_symbol_sentiment(self, symbol):
        """Get sentiment analysis for a specific symbol (basic implementation)"""
        try:
            news = self.get_stock_news(symbol, days_back=3)
            if not news:
                return {'sentiment': 'neutral', 'confidence': 0.5}
            
            # Simple sentiment analysis based on keywords
            positive_keywords = ['rise', 'up', 'gain', 'profit', 'growth', 'increase', 'bull', 'strong']
            negative_keywords = ['fall', 'down', 'loss', 'decline', 'drop', 'bear', 'weak', 'crash']
            
            positive_count = 0
            negative_count = 0
            total_articles = len(news)
            
            for article in news:
                text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                
                for keyword in positive_keywords:
                    if keyword in text:
                        positive_count += 1
                        
                for keyword in negative_keywords:
                    if keyword in text:
                        negative_count += 1
            
            if positive_count > negative_count:
                sentiment = 'positive'
                confidence = min(0.9, 0.5 + (positive_count - negative_count) / (total_articles * 2))
            elif negative_count > positive_count:
                sentiment = 'negative'
                confidence = min(0.9, 0.5 + (negative_count - positive_count) / (total_articles * 2))
            else:
                sentiment = 'neutral'
                confidence = 0.5
            
            return {
                'sentiment': sentiment,
                'confidence': round(confidence, 2),
                'positive_mentions': positive_count,
                'negative_mentions': negative_count,
                'total_articles': total_articles
            }
            
        except Exception as e:
            logging.error(f"Error analyzing sentiment for {symbol}: {e}")
            return {'sentiment': 'neutral', 'confidence': 0.5}
