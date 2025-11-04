"""
Proper Async Database Layer with asyncpg fallback to psycopg2
Handles connection pooling, transactions, and error recovery
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/financial_db")

# Try to use asyncpg first, fallback to psycopg2 with async wrapper
try:
    import asyncpg
    USE_ASYNCPG = True
    logger.info("Using asyncpg for database connections")
except ImportError:
    import psycopg2
    import psycopg2.pool
    from psycopg2.extras import RealDictCursor
    USE_ASYNCPG = False
    logger.info("Using psycopg2 (sync) with async wrappers")


class AsyncDatabase:
    """Async database wrapper that works with both asyncpg and psycopg2"""
    
    def __init__(self):
        self.pool = None
        self._use_asyncpg = USE_ASYNCPG
        
    async def connect(self):
        """Create connection pool"""
        try:
            if self._use_asyncpg:
                print("🔄 Creating asyncpg pool...")
                self.pool = await asyncio.wait_for(
                    asyncpg.create_pool(
                        DATABASE_URL,
                        min_size=2,
                        max_size=10,
                        command_timeout=10
                    ),
                    timeout=5.0
                )
                print("✅ asyncpg pool created")
            else:
                print("🔄 Creating psycopg2 pool...")
                # Parse DATABASE_URL for psycopg2
                url = DATABASE_URL.replace('postgresql://', '')
                user_pass, host_db = url.split('@')
                user, password = user_pass.split(':')
                host_port, database = host_db.split('/')
                host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
                
                # Run sync pool creation in thread
                await asyncio.to_thread(self._create_sync_pool, user, password, host, port, database)
                print("✅ psycopg2 pool created")
                
            logger.info("✅ Database connection pool created")
            return True
            
        except asyncio.TimeoutError:
            logger.error("❌ Database connection timeout after 5s")
            print("❌ Connection timeout - check if PostgreSQL is running")
            return False
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            print(f"❌ Connection error: {e}")
            return False
    
    def _create_sync_pool(self, user, password, host, port, database):
        """Create psycopg2 connection pool (sync)"""
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
    
    async def disconnect(self):
        """Close connection pool"""
        try:
            if self.pool:
                if self._use_asyncpg:
                    await self.pool.close()
                else:
                    await asyncio.to_thread(self.pool.closeall)
                self.pool = None
                logger.info("✅ Database connection pool closed")
        except Exception as e:
            logger.error(f"❌ Error closing pool: {e}")
    
    @asynccontextmanager
    async def acquire(self):
        """Get connection from pool"""
        if self._use_asyncpg:
            async with self.pool.acquire() as conn:
                yield conn
        else:
            conn = await asyncio.to_thread(self.pool.getconn)
            try:
                yield conn
            finally:
                await asyncio.to_thread(self.pool.putconn, conn)
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row"""
        try:
            async with self.acquire() as conn:
                if self._use_asyncpg:
                    row = await conn.fetchrow(query, *args)
                    return dict(row) if row else None
                else:
                    result = await asyncio.to_thread(self._fetch_one_sync, conn, query, args)
                    return result
        except Exception as e:
            logger.error(f"fetch_one error: {e}")
            return None
    
    def _fetch_one_sync(self, conn, query, args):
        """Sync fetch one for psycopg2"""
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, args)
            row = cur.fetchone()
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> List[Dict]:
        """Fetch all rows"""
        try:
            async with self.acquire() as conn:
                if self._use_asyncpg:
                    rows = await conn.fetch(query, *args)
                    return [dict(row) for row in rows]
                else:
                    result = await asyncio.to_thread(self._fetch_all_sync, conn, query, args)
                    return result
        except Exception as e:
            logger.error(f"fetch_all error: {e}")
            return []
    
    def _fetch_all_sync(self, conn, query, args):
        """Sync fetch all for psycopg2"""
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, args)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    
    async def execute(self, query: str, *args) -> bool:
        """Execute query (INSERT/UPDATE/DELETE)"""
        try:
            async with self.acquire() as conn:
                if self._use_asyncpg:
                    await conn.execute(query, *args)
                else:
                    await asyncio.to_thread(self._execute_sync, conn, query, args)
                return True
        except Exception as e:
            logger.error(f"execute error: {e}")
            return False
    
    def _execute_sync(self, conn, query, args):
        """Sync execute for psycopg2"""
        with conn.cursor() as cur:
            cur.execute(query, args)
            conn.commit()
    
    async def execute_many(self, query: str, args_list: List[tuple]) -> bool:
        """Execute query multiple times"""
        try:
            async with self.acquire() as conn:
                if self._use_asyncpg:
                    await conn.executemany(query, args_list)
                else:
                    await asyncio.to_thread(self._execute_many_sync, conn, query, args_list)
                return True
        except Exception as e:
            logger.error(f"execute_many error: {e}")
            return False
    
    def _execute_many_sync(self, conn, query, args_list):
        """Sync execute many for psycopg2"""
        with conn.cursor() as cur:
            cur.executemany(query, args_list)
            conn.commit()
    
    # ============================================
    # HIGH-LEVEL QUERIES
    # ============================================
    
    async def get_all_assets(self) -> List[Dict]:
        """Get all assets"""
        return await self.fetch_all(
            "SELECT asset_id as id, name, symbol, asset_type as type FROM assets ORDER BY asset_id"
        )
    
    async def get_asset(self, asset_id: str) -> Optional[Dict]:
        """Get single asset"""
        return await self.fetch_one(
            "SELECT asset_id as id, name, symbol, asset_type as type FROM assets WHERE asset_id = $1",
            asset_id
        )
    
    async def insert_price(self, asset_id: str, price: float, volume: float, source: str = 'yfinance'):
        """Insert price data"""
        query = """
            INSERT INTO price_data (asset_id, price, volume, source, timestamp)
            VALUES ($1, $2, $3, $4, NOW())
        """
        return await self.execute(query, asset_id, price, volume, source)
    
    async def get_latest_price(self, asset_id: str) -> Optional[Dict]:
        """Get latest price"""
        return await self.fetch_one(
            """SELECT asset_id, price, volume, timestamp 
               FROM price_data 
               WHERE asset_id = $1 
               ORDER BY timestamp DESC 
               LIMIT 1""",
            asset_id
        )
    
    async def get_price_history(self, asset_id: str, hours: int = 24) -> List[Dict]:
        """Get price history"""
        return await self.fetch_all(
            """SELECT timestamp, price, volume
               FROM price_data
               WHERE asset_id = $1 AND timestamp > NOW() - INTERVAL '%s hours'
               ORDER BY timestamp DESC""" % hours,
            asset_id
        )
    
    async def insert_prediction(
        self, 
        asset_id: str, 
        horizon_minutes: int,
        predicted_price: float,
        predicted_change_pct: float,
        current_price: float,
        confidence: float,
        sentiment_score: Optional[float] = None,
        model_version: str = 'ml_v1'
    ):
        """Insert prediction"""
        query = """
            INSERT INTO predictions (
                asset_id, horizon_minutes, predicted_price, predicted_change_pct,
                current_price, confidence, sentiment_score, model_version, timestamp
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
        """
        return await self.execute(
            query, asset_id, horizon_minutes, predicted_price, predicted_change_pct,
            current_price, confidence, sentiment_score, model_version
        )
    
    async def get_recent_predictions(self, asset_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent predictions"""
        if asset_id:
            return await self.fetch_all(
                """SELECT * FROM predictions 
                   WHERE asset_id = $1 
                   ORDER BY timestamp DESC 
                   LIMIT $2""",
                asset_id, limit
            )
        else:
            return await self.fetch_all(
                """SELECT * FROM predictions 
                   ORDER BY timestamp DESC 
                   LIMIT $1""",
                limit
            )
    
    async def get_portfolio_positions(self, user_id: str = "default") -> List[Dict]:
        """Get all portfolio positions"""
        return await self.fetch_all(
            """SELECT p.*, a.name, a.asset_type
               FROM portfolio_positions p
               JOIN assets a ON p.asset_id = a.asset_id
               WHERE p.user_id = $1
               ORDER BY p.updated_at DESC""",
            user_id
        )
    
    async def get_position(self, asset_id: str, user_id: str = "default") -> Optional[Dict]:
        """Get specific position"""
        return await self.fetch_one(
            """SELECT * FROM portfolio_positions 
               WHERE asset_id = $1 AND user_id = $2""",
            asset_id, user_id
        )
    
    async def upsert_position(self, asset_id: str, quantity: float, average_price: float, user_id: str = "default"):
        """Insert or update portfolio position"""
        query = """
            INSERT INTO portfolio_positions (user_id, asset_id, quantity, average_price, created_at, updated_at)
            VALUES ($1, $2, $3, $4, NOW(), NOW())
            ON CONFLICT (user_id, asset_id)
            DO UPDATE SET 
                quantity = $3,
                average_price = $4,
                updated_at = NOW()
        """
        return await self.execute(query, user_id, asset_id, quantity, average_price)
    
    async def delete_position(self, asset_id: str, user_id: str = "default"):
        """Delete portfolio position"""
        return await self.execute(
            "DELETE FROM portfolio_positions WHERE asset_id = $1 AND user_id = $2",
            asset_id, user_id
        )


# Global instance
async_db = AsyncDatabase()
