import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, ActivityIndicator, Chip, Surface, Text } from 'react-native-paper';
import { priceAPI, predictionAPI } from '../services/api';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

interface Metal {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  predictions?: Array<{
    horizon: string;
    predicted_price: number;
    predicted_change_pct: number;
    confidence: number;
    min_price: number;
    max_price: number;
  }>;
  sentiment?: {
    sentiment_label: string;
    sentiment_score: number;
    article_count: number;
  };
}

const METALS = [
  { symbol: 'GOLD', name: 'Gold', emoji: '🥇' },
  { symbol: 'SILVER', name: 'Silver', emoji: '🥈' },
  { symbol: 'PLATINUM', name: 'Platinum', emoji: '⚪' },
  { symbol: 'PALLADIUM', name: 'Palladium', emoji: '⚫' },
];

export default function MetalsScreen() {
  const [metals, setMetals] = useState<Metal[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadMetalsData();
  }, []);

  const loadMetalsData = async () => {
    try {
      const metalsData = await Promise.all(
        METALS.map(async (metal) => {
          try {
            // Get current price
            const priceData = await priceAPI.getPrice(metal.symbol);
            
            // Get predictions
            let predictions;
            let sentiment;
            try {
              const predictionData = await predictionAPI.predict(metal.symbol);
              predictions = predictionData.predictions;
              sentiment = predictionData.sentiment;
            } catch (err) {
              console.log(`No prediction for ${metal.symbol}`);
            }

            return {
              symbol: metal.symbol,
              name: metal.name,
              price: priceData.price,
              change: priceData.change || 0,
              changePercent: priceData.change_percent || 0,
              predictions,
              sentiment,
            };
          } catch (err) {
            console.error(`Error loading ${metal.name}:`, err);
            return {
              symbol: metal.symbol,
              name: metal.name,
              price: 0,
              change: 0,
              changePercent: 0,
            };
          }
        })
      );

      setMetals(metalsData);
    } catch (error) {
      console.error('Error loading metals:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadMetalsData();
  };

  const getMetalEmoji = (symbol: string) => {
    return METALS.find(m => m.symbol === symbol)?.emoji || '📊';
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#FFD700" />
        <Text style={styles.loadingText}>Loading precious metals data...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Surface style={styles.header}>
        <Title style={styles.headerTitle}>💎 Precious Metals Tracker</Title>
        <Paragraph style={styles.headerSubtitle}>
          Real-time prices with AI predictions
        </Paragraph>
      </Surface>

      {metals.map((metal) => (
        <Card key={metal.symbol} style={styles.card}>
          <Card.Content>
            <View style={styles.cardHeader}>
              <View style={styles.titleRow}>
                <Text style={styles.emoji}>{getMetalEmoji(metal.symbol)}</Text>
                <View>
                  <Title style={styles.metalName}>{metal.name}</Title>
                  <Paragraph style={styles.symbol}>{metal.symbol}</Paragraph>
                </View>
              </View>
              <View style={styles.priceContainer}>
                <Title style={styles.price}>${metal.price.toFixed(2)}</Title>
                <Chip
                  style={[
                    styles.changeChip,
                    metal.change >= 0 ? styles.positiveChip : styles.negativeChip,
                  ]}
                  textStyle={styles.changeText}
                >
                  {metal.change >= 0 ? '▲' : '▼'} {Math.abs(metal.changePercent).toFixed(2)}%
                </Chip>
              </View>
            </View>

            {metal.predictions && metal.predictions.length > 0 && (
              <Surface style={styles.predictionBox}>
                <View style={styles.predictionHeader}>
                  <Text style={styles.predictionLabel}>🔮 AI Predictions</Text>
                  {metal.sentiment && (
                    <Chip
                      style={[
                        styles.sentimentChip,
                        metal.sentiment.sentiment_score > 0.3 ? styles.positiveSentiment :
                        metal.sentiment.sentiment_score < -0.3 ? styles.negativeSentiment :
                        styles.neutralSentiment
                      ]}
                      textStyle={styles.sentimentText}
                    >
                      {metal.sentiment.sentiment_label}
                    </Chip>
                  )}
                </View>

                {metal.predictions.map((pred, index) => (
                  <View key={index} style={styles.predictionItem}>
                    <View style={styles.predictionTimeRow}>
                      <Text style={styles.timeHorizon}>⏱️ {pred.horizon}</Text>
                      <Chip
                        style={styles.confidenceChip}
                        textStyle={styles.confidenceText}
                      >
                        {pred.confidence.toFixed(0)}% confidence
                      </Chip>
                    </View>

                    <View style={styles.predictionDetails}>
                      <View style={styles.predictionRow}>
                        <Text style={styles.predictionKey}>Predicted:</Text>
                        <Text style={styles.predictionValue}>
                          ${pred.predicted_price.toFixed(2)}
                        </Text>
                      </View>

                      <View style={styles.predictionRow}>
                        <Text style={styles.predictionKey}>Change:</Text>
                        <View style={styles.changeContainer}>
                          <Chip
                            style={[
                              styles.changeDirectionChip,
                              pred.predicted_change_pct >= 0 ? styles.upChip : styles.downChip,
                            ]}
                            textStyle={styles.directionText}
                          >
                            {pred.predicted_change_pct >= 0 ? '📈' : '📉'} {Math.abs(pred.predicted_change_pct).toFixed(2)}%
                          </Chip>
                        </View>
                      </View>

                      <View style={styles.predictionRow}>
                        <Text style={styles.predictionKey}>Range:</Text>
                        <Text style={styles.rangeValue}>
                          ${pred.min_price.toFixed(2)} - ${pred.max_price.toFixed(2)}
                        </Text>
                      </View>
                    </View>

                    {index < (metal.predictions?.length ?? 0) - 1 && <View style={styles.divider} />}
                  </View>
                ))}
              </Surface>
            )}
          </Card.Content>
        </Card>
      ))}

      <Card style={styles.infoCard}>
        <Card.Content>
          <Paragraph style={styles.infoText}>
            💡 <Text style={styles.bold}>Tip:</Text> Pull down to refresh prices and predictions.
            Data is updated in real-time from global markets.
          </Paragraph>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a2e',
  },
  loadingText: {
    marginTop: 16,
    color: '#FFD700',
    fontSize: 16,
  },
  header: {
    padding: 20,
    backgroundColor: '#16213e',
    borderBottomWidth: 2,
    borderBottomColor: '#FFD700',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFD700',
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#aaa',
    textAlign: 'center',
    marginTop: 4,
  },
  card: {
    margin: 16,
    marginBottom: 8,
    backgroundColor: '#16213e',
    borderRadius: 12,
    elevation: 4,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  emoji: {
    fontSize: 40,
    marginRight: 12,
  },
  metalName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFD700',
  },
  symbol: {
    fontSize: 12,
    color: '#aaa',
  },
  priceContainer: {
    alignItems: 'flex-end',
  },
  price: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  changeChip: {
    marginTop: 4,
  },
  positiveChip: {
    backgroundColor: '#4caf50',
  },
  negativeChip: {
    backgroundColor: '#f44336',
  },
  changeText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  predictionBox: {
    backgroundColor: '#0f3460',
    borderRadius: 8,
    padding: 12,
    marginTop: 8,
  },
  predictionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  predictionLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFD700',
  },
  predictionItem: {
    marginBottom: 8,
  },
  predictionTimeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  timeHorizon: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#FFD700',
  },
  predictionDetails: {
    paddingLeft: 8,
    gap: 6,
  },
  divider: {
    height: 1,
    backgroundColor: '#1a1a2e',
    marginVertical: 12,
  },
  confidenceChip: {
    backgroundColor: '#533483',
    height: 26,
  },
  confidenceText: {
    color: '#fff',
    fontSize: 11,
  },
  sentimentChip: {
    height: 26,
  },
  positiveSentiment: {
    backgroundColor: '#4caf50',
  },
  negativeSentiment: {
    backgroundColor: '#f44336',
  },
  neutralSentiment: {
    backgroundColor: '#666',
  },
  sentimentText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  predictionContent: {
    gap: 8,
  },
  predictionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 3,
  },
  predictionKey: {
    fontSize: 13,
    color: '#aaa',
  },
  predictionValue: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#fff',
  },
  rangeValue: {
    fontSize: 12,
    color: '#aaa',
    fontStyle: 'italic',
  },
  changeContainer: {
    flexDirection: 'row',
  },
  changeDirectionChip: {
    height: 24,
  },
  positiveText: {
    color: '#4caf50',
  },
  negativeText: {
    color: '#f44336',
  },
  upChip: {
    backgroundColor: '#4caf50',
  },
  downChip: {
    backgroundColor: '#f44336',
  },
  neutralChip: {
    backgroundColor: '#666',
  },
  directionText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  infoCard: {
    margin: 16,
    marginTop: 8,
    backgroundColor: '#16213e',
    borderRadius: 8,
  },
  infoText: {
    color: '#aaa',
    fontSize: 13,
    lineHeight: 20,
  },
  bold: {
    fontWeight: 'bold',
    color: '#FFD700',
  },
});
