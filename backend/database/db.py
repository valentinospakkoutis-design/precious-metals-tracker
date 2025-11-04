"""
Database connection and utilities
PostgreSQL with psycopg2 for FastAPI
"""

import psycopg2
import psycopg2.pool
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/financial_db")

class Database:
    def __init__(self):
        self.pool = None
    
    def connect_sync(self):
        """Create connection pool (sync version)"""
        if not self.pool:
            # Parse DATABASE_URL
            parts = DATABASE_URL.replace('postgresql://', '').split('@')
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')
            host_port = host_db[0].split(':')
            
            self.pool = psycopg2.pool.SimpleConnectionPool(
                minconn=2,
                maxconn=10,
                user=user_pass[0],
                password=user_pass[1],
                host=host_port[0],
                port=host_port[1] if len(host_port) > 1 else '5432',
                database=host_db[1]
            )
            print("✅ PostgreSQL connection pool created")
    
    async def connect(self):
        """Create connection pool (async wrapper)"""
        self.connect_sync()
    
    def disconnect_sync(self):
        """Close connection pool (sync version)"""
        if self.pool:
            self.pool.closeall()
            self.pool = None
            print("✅ PostgreSQL connection pool closed")
    
    async def disconnect(self):
        """Close connection pool (async wrapper)"""
        self.disconnect_sync()
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool"""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)
    
    def execute_sync(self, query: str, *args):
        """Execute a query (INSERT/UPDATE/DELETE)"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, args)
                conn.commit()
    
    async def execute(self, query: str, *args):
        """Execute a query (INSERT/UPDATE/DELETE) - async wrapper"""
        return self.execute_sync(query, *args)
    
    def fetch_one_sync(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, args)
                row = cur.fetchone()
                if row:
                    columns = [desc[0] for desc in cur.description]
                    return dict(zip(columns, row))
                return None
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row - async wrapper"""
        return self.fetch_one_sync(query, *args)
    
    def fetch_all_sync(self, query: str, *args) -> List[Dict]:
        """Fetch all rows"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, args)
                rows = cur.fetchall()
                if rows:
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in rows]
                return []
    
    async def fetch_all(self, query: str, *args) -> List[Dict]:
        """Fetch all rows - async wrapper"""
        return self.fetch_all_sync(query, *args)
    
    # Asset operations
    async def get_all_assets(self) -> List[Dict]:
        """Get all assets"""
        query = "SELECT id, name, symbol, type FROM assets ORDER BY id"
        return await self.fetch_all(query)
    
    async def get_asset(self, asset_id: str) -> Optional[Dict]:
        """Get single asset"""
        query = "SELECT id, name, symbol, type FROM assets WHERE id = $1"
        return await self.fetch_one(query, asset_id)
    
    # Price operations
    async def insert_price(self, asset_id: str, price: float, volume: float, source: str = 'yfinance'):
        """Insert price data"""
        query = """
            INSERT INTO price_data (asset_id, price, volume, source)
            VALUES ($1, $2, $3, $4)
        """
        await self.execute(query, asset_id, price, volume, source)
    
    async def get_latest_price(self, asset_id: str) -> Optional[Dict]:
        """Get latest price for asset"""
        query = """
            SELECT asset_id, time, price, volume, source
            FROM price_data
            WHERE asset_id = $1
            ORDER BY time DESC
            LIMIT 1
        """
        return await self.fetch_one(query, asset_id)
    
    async def get_price_history(self, asset_id: str, hours: int = 24) -> List[Dict]:
        """Get price history"""
        query = """
            SELECT time, price, volume
            FROM price_data
            WHERE asset_id = $1 AND time > NOW() - INTERVAL '%s hours'
            ORDER BY time DESC
        """ % hours
        return await self.fetch_all(query, asset_id)
    
    # Prediction operations
    async def insert_prediction(
        self, 
        asset_id: str, 
        horizon_minutes: int,
        predicted_price: float,
        predicted_change_pct: float,
        current_price: float,
        confidence: float,
        sentiment_score: Optional[float] = None,
        model_version: str = 'baseline_v1'
    ):
        """Insert prediction"""
        query = """
            INSERT INTO predictions (
                asset_id, horizon_minutes, predicted_price, predicted_change_pct,
                current_price, confidence, sentiment_score, model_version
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        result = await self.fetch_one(
            query, 
            asset_id, horizon_minutes, predicted_price, predicted_change_pct,
            current_price, confidence, sentiment_score, model_version
        )
        return result['id'] if result else None
    
    async def get_recent_predictions(self, asset_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent predictions"""
        if asset_id:
            query = """
                SELECT id, asset_id, predicted_at, horizon_minutes, 
                       predicted_price, predicted_change_pct, confidence
                FROM predictions
                WHERE asset_id = $1
                ORDER BY predicted_at DESC
                LIMIT $2
            """
            return await self.fetch_all(query, asset_id, limit)
        else:
            query = """
                SELECT id, asset_id, predicted_at, horizon_minutes,
                       predicted_price, predicted_change_pct, confidence
                FROM predictions
                ORDER BY predicted_at DESC
                LIMIT $1
            """
            return await self.fetch_all(query, limit)
    
    # News operations
    async def insert_news(
        self,
        asset_id: str,
        title: str,
        content: str,
        source: str,
        url: str,
        sentiment_score: float,
        sentiment_label: str
    ):
        """Insert news article"""
        query = """
            INSERT INTO news_articles (
                asset_id, title, content, source, url, 
                sentiment_score, sentiment_label
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """
        result = await self.fetch_one(
            query, asset_id, title, content, source, url,
            sentiment_score, sentiment_label
        )
        return result['id'] if result else None
    
    async def get_recent_news(self, asset_id: str, limit: int = 5) -> List[Dict]:
        """Get recent news for asset"""
        query = """
            SELECT id, title, source, sentiment_label, sentiment_score, published_at
            FROM news_articles
            WHERE asset_id = $1
            ORDER BY published_at DESC
            LIMIT $2
        """
        return await self.fetch_all(query, asset_id, limit)
    
    # Alert operations
    async def get_active_alerts(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get active alerts"""
        if user_id:
            query = """
                SELECT id, asset_id, alert_type, threshold, condition
                FROM alerts
                WHERE user_id = $1 AND is_active = true
                ORDER BY created_at DESC
            """
            return await self.fetch_all(query, user_id)
        else:
            query = """
                SELECT id, asset_id, alert_type, threshold, condition
                FROM alerts
                WHERE is_active = true
                ORDER BY created_at DESC
            """
            return await self.fetch_all(query)
    
    # Portfolio operations
    async def create_transaction(self, user_id: str, asset_id: str, transaction_type: str,
                                 quantity: float, price_per_unit: float, total_amount: float) -> int:
        """Log a buy/sell transaction and update portfolio position"""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                # Insert transaction (if we had a transactions table)
                # For now, just update portfolio_positions
                
                if transaction_type == "BUY":
                    # Check if position exists
                    cur.execute("""
                        SELECT id, quantity, avg_buy_price, total_invested 
                        FROM portfolio_positions 
                        WHERE user_id = %s AND asset_id = %s
                    """, (user_id, asset_id))
                    
                    existing = cur.fetchone()
                    
                    if existing:
                        # Update existing position (average price calculation)
                        pos_id, old_qty, old_avg, old_invested = existing
                        new_qty = old_qty + quantity
                        new_invested = old_invested + total_amount
                        new_avg = new_invested / new_qty
                        
                        cur.execute("""
                            UPDATE portfolio_positions 
                            SET quantity = %s, avg_buy_price = %s, total_invested = %s, updated_at = NOW()
                            WHERE id = %s
                        """, (new_qty, new_avg, new_invested, pos_id))
                        position_id = pos_id
                    else:
                        # Create new position
                        cur.execute("""
                            INSERT INTO portfolio_positions 
                            (user_id, asset_id, quantity, avg_buy_price, total_invested, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                            RETURNING id
                        """, (user_id, asset_id, quantity, price_per_unit, total_amount))
                        position_id = cur.fetchone()[0]
                
                elif transaction_type == "SELL":
                    # Reduce position
                    cur.execute("""
                        SELECT id, quantity, avg_buy_price, total_invested 
                        FROM portfolio_positions 
                        WHERE user_id = %s AND asset_id = %s
                    """, (user_id, asset_id))
                    
                    existing = cur.fetchone()
                    if not existing:
                        raise ValueError(f"No position found for {asset_id}")
                    
                    pos_id, old_qty, old_avg, old_invested = existing
                    
                    if quantity > old_qty:
                        raise ValueError(f"Cannot sell {quantity} units, only {old_qty} available")
                    
                    new_qty = old_qty - quantity
                    # Proportionally reduce invested amount
                    new_invested = old_invested * (new_qty / old_qty) if new_qty > 0 else 0
                    
                    if new_qty == 0:
                        # Delete position if fully sold
                        cur.execute("DELETE FROM portfolio_positions WHERE id = %s", (pos_id,))
                    else:
                        # Update position
                        cur.execute("""
                            UPDATE portfolio_positions 
                            SET quantity = %s, total_invested = %s, updated_at = NOW()
                            WHERE id = %s
                        """, (new_qty, new_invested, pos_id))
                    
                    position_id = pos_id
                
                conn.commit()
                return position_id
        finally:
            self.pool.putconn(conn)
    
    async def get_user_portfolio(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all positions for a user"""
        query = """
            SELECT p.id, p.user_id, p.asset_id, p.quantity, p.avg_buy_price, 
                   p.total_invested, p.created_at, p.updated_at,
                   a.name as asset_name, a.asset_type
            FROM portfolio_positions p
            JOIN assets a ON p.asset_id = a.symbol
            WHERE p.user_id = %s
            ORDER BY p.total_invested DESC
        """
        return await self.fetch_all(query, (user_id,))
    
    async def get_position(self, user_id: str, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get specific position"""
        query = """
            SELECT p.id, p.user_id, p.asset_id, p.quantity, p.avg_buy_price, 
                   p.total_invested, p.created_at, p.updated_at,
                   a.name as asset_name, a.asset_type
            FROM portfolio_positions p
            JOIN assets a ON p.asset_id = a.symbol
            WHERE p.user_id = %s AND p.asset_id = %s
        """
        return await self.fetch_one(query, (user_id, asset_id))

# Global database instance
db = Database()
