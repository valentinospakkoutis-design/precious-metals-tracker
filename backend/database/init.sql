-- Financial Prediction App - Database Schema
-- TimescaleDB Initialization Script
-- Created: October 28, 2025

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================
-- ASSETS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS assets (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    asset_type VARCHAR(20) NOT NULL, -- 'metal', 'crypto', 'shitcoin'
    category VARCHAR(50),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert initial 10 assets
INSERT INTO assets (id, name, symbol, asset_type, category) VALUES
-- Metals
('GOLD', 'Gold', 'GC=F', 'metal', 'Precious Metals'),
('SILVER', 'Silver', 'SI=F', 'metal', 'Precious Metals'),
('PLATINUM', 'Platinum', 'PL=F', 'metal', 'Precious Metals'),

-- Crypto
('BTC', 'Bitcoin', 'BTC-USD', 'crypto', 'Cryptocurrency'),
('ETH', 'Ethereum', 'ETH-USD', 'crypto', 'Cryptocurrency'),
('BNB', 'Binance Coin', 'BNB-USD', 'crypto', 'Cryptocurrency'),
('ADA', 'Cardano', 'ADA-USD', 'crypto', 'Cryptocurrency'),

-- Shitcoins
('DOGE', 'Dogecoin', 'DOGE-USD', 'shitcoin', 'Meme Coins'),
('SHIB', 'Shiba Inu', 'SHIB-USD', 'shitcoin', 'Meme Coins'),
('PEPE', 'Pepe', 'PEPE-USD', 'shitcoin', 'Meme Coins')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- PRICE DATA TABLE (Time-series)
-- ============================================
CREATE TABLE IF NOT EXISTS price_data (
    time TIMESTAMPTZ NOT NULL,
    asset_id VARCHAR(10) NOT NULL REFERENCES assets(id),
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8),
    bid DECIMAL(20, 8),
    ask DECIMAL(20, 8),
    spread DECIMAL(20, 8),
    source VARCHAR(50), -- 'binance', 'yfinance', 'coingecko'
    PRIMARY KEY (time, asset_id)
);

-- Convert to hypertable (TimescaleDB magic!)
SELECT create_hypertable('price_data', 'time', if_not_exists => TRUE);

-- Create index for fast queries
CREATE INDEX IF NOT EXISTS idx_price_asset_time ON price_data (asset_id, time DESC);

-- ============================================
-- PREDICTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(10) NOT NULL REFERENCES assets(id),
    predicted_at TIMESTAMPTZ NOT NULL,
    prediction_horizon VARCHAR(10) NOT NULL, -- '10min', '20min', '30min', '1h', '4h', '1d'
    predicted_price DECIMAL(20, 8) NOT NULL,
    predicted_change_pct DECIMAL(10, 4) NOT NULL,
    confidence DECIMAL(5, 2) NOT NULL, -- 0-100
    min_price DECIMAL(20, 8), -- Lower confidence bound
    max_price DECIMAL(20, 8), -- Upper confidence bound
    features JSONB, -- Store feature values used
    model_version VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pred_asset_time ON predictions (asset_id, predicted_at DESC);

-- ============================================
-- PREDICTION HISTORY (Actual vs Predicted)
-- ============================================
CREATE TABLE IF NOT EXISTS prediction_history (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER REFERENCES predictions(id),
    asset_id VARCHAR(10) NOT NULL REFERENCES assets(id),
    predicted_at TIMESTAMPTZ NOT NULL,
    prediction_horizon VARCHAR(10) NOT NULL,
    predicted_value DECIMAL(20, 8) NOT NULL,
    predicted_change_pct DECIMAL(10, 4) NOT NULL,
    confidence DECIMAL(5, 2) NOT NULL,
    actual_value DECIMAL(20, 8),
    actual_change_pct DECIMAL(10, 4),
    was_correct BOOLEAN,
    error_pct DECIMAL(10, 4),
    checked_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_pred_hist_asset ON prediction_history (asset_id, predicted_at DESC);

-- ============================================
-- NEWS & SENTIMENT TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(10) REFERENCES assets(id),
    title TEXT NOT NULL,
    description TEXT,
    url TEXT,
    source VARCHAR(100),
    author VARCHAR(200),
    published_at TIMESTAMPTZ NOT NULL,
    sentiment_score DECIMAL(5, 4), -- -1 to +1
    sentiment_label VARCHAR(20), -- 'bullish', 'neutral', 'bearish'
    sentiment_confidence DECIMAL(5, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_asset_time ON news_articles (asset_id, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_sentiment ON news_articles (sentiment_score);

-- ============================================
-- ALERTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(10) NOT NULL REFERENCES assets(id),
    alert_type VARCHAR(50) NOT NULL, -- 'price_spike', 'prediction', 'volume_spike', 'news'
    threshold DECIMAL(10, 4),
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info', -- 'info', 'warning', 'critical'
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_alerts_asset ON alerts (asset_id, triggered_at DESC);

-- ============================================
-- MODEL PERFORMANCE METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(10) REFERENCES assets(id),
    metric_date DATE NOT NULL,
    prediction_horizon VARCHAR(10),
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy_pct DECIMAL(5, 2),
    mae DECIMAL(10, 4), -- Mean Absolute Error
    rmse DECIMAL(10, 4), -- Root Mean Square Error
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(asset_id, metric_date, prediction_horizon)
);

-- ============================================
-- PORTFOLIO TRACKING (Phase 3)
-- ============================================
CREATE TABLE IF NOT EXISTS portfolio_positions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER, -- Will add users table later
    asset_id VARCHAR(10) NOT NULL REFERENCES assets(id),
    quantity DECIMAL(20, 8) NOT NULL,
    avg_buy_price DECIMAL(20, 8) NOT NULL,
    current_price DECIMAL(20, 8),
    pnl DECIMAL(20, 8),
    pnl_pct DECIMAL(10, 4),
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ
);

-- ============================================
-- VIEWS FOR QUICK QUERIES
-- ============================================

-- Latest prices view
CREATE OR REPLACE VIEW latest_prices AS
SELECT DISTINCT ON (asset_id)
    asset_id,
    price,
    volume,
    time,
    source
FROM price_data
ORDER BY asset_id, time DESC;

-- Today's accuracy view
CREATE OR REPLACE VIEW today_accuracy AS
SELECT 
    asset_id,
    prediction_horizon,
    COUNT(*) as total,
    SUM(CASE WHEN was_correct THEN 1 ELSE 0 END) as correct,
    ROUND(100.0 * SUM(CASE WHEN was_correct THEN 1 ELSE 0 END) / COUNT(*), 2) as accuracy_pct,
    ROUND(AVG(ABS(error_pct)), 2) as avg_error_pct
FROM prediction_history
WHERE DATE(predicted_at) = CURRENT_DATE
GROUP BY asset_id, prediction_horizon;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to calculate price change percentage
CREATE OR REPLACE FUNCTION calculate_price_change(
    p_asset_id VARCHAR(10),
    p_minutes INTEGER DEFAULT 30
)
RETURNS DECIMAL(10, 4) AS $$
DECLARE
    current_price DECIMAL(20, 8);
    old_price DECIMAL(20, 8);
BEGIN
    -- Get current price
    SELECT price INTO current_price
    FROM price_data
    WHERE asset_id = p_asset_id
    ORDER BY time DESC
    LIMIT 1;
    
    -- Get price from N minutes ago
    SELECT price INTO old_price
    FROM price_data
    WHERE asset_id = p_asset_id
    AND time <= NOW() - (p_minutes || ' minutes')::INTERVAL
    ORDER BY time DESC
    LIMIT 1;
    
    -- Calculate percentage change
    IF old_price IS NOT NULL AND old_price > 0 THEN
        RETURN ((current_price - old_price) / old_price) * 100;
    ELSE
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- CLEANUP & MAINTENANCE
-- ============================================

-- Auto-delete old news (keep 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_news()
RETURNS void AS $$
BEGIN
    DELETE FROM news_articles
    WHERE published_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- COMPLETION MESSAGE
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✅ Database initialized successfully!';
    RAISE NOTICE '📊 Tables created: 9';
    RAISE NOTICE '📈 Assets loaded: 10';
    RAISE NOTICE '🚀 Ready for development!';
END $$;
