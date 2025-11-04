import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl, Alert } from 'react-native';
import { Card, Title, Paragraph, Button, ActivityIndicator, Text } from 'react-native-paper';
import { portfolioAPI } from '../services/api';

interface Position {
  symbol: string;
  quantity: number;
  average_price: number;
  current_value: number;
  profit_loss: number;
  profit_loss_percentage: number;
}

export default function PortfolioScreen({ navigation }: any) {
  const [portfolio, setPortfolio] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [totalValue, setTotalValue] = useState(0);
  const [totalProfitLoss, setTotalProfitLoss] = useState(0);

  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    try {
      const data = await portfolioAPI.getPortfolio();
      setPortfolio(data.positions || []);
      setTotalValue(data.total_value || 0);
      setTotalProfitLoss(data.total_profit_loss || 0);
    } catch (error: any) {
      console.error('Error loading portfolio:', error);
      // Don't show error for empty portfolio - just set empty state
      setPortfolio([]);
      setTotalValue(0);
      setTotalProfitLoss(0);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadPortfolio();
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Card style={styles.summaryCard}>
        <Card.Content>
          <Title>Portfolio Value</Title>
          <Paragraph style={styles.valueText}>${totalValue.toFixed(2)}</Paragraph>
          <Paragraph
            style={[
              styles.profitLossText,
              { color: totalProfitLoss >= 0 ? '#4caf50' : '#f44336' },
            ]}
          >
            {totalProfitLoss >= 0 ? '+' : ''}${totalProfitLoss.toFixed(2)}
          </Paragraph>
        </Card.Content>
      </Card>

      <View style={styles.actionsContainer}>
        <Button
          mode="contained"
          onPress={() => navigation.navigate('Trade', { action: 'buy' })}
          style={styles.actionButton}
        >
          Buy Asset
        </Button>
        <Button
          mode="outlined"
          onPress={() => navigation.navigate('Trade', { action: 'sell' })}
          style={styles.actionButton}
        >
          Sell Asset
        </Button>
      </View>

      <Title style={styles.sectionTitle}>Your Positions</Title>

      {portfolio.length === 0 ? (
        <Card style={styles.emptyCard}>
          <Card.Content>
            <Paragraph style={styles.emptyText}>
              No positions yet. Start by buying your first asset!
            </Paragraph>
          </Card.Content>
        </Card>
      ) : (
        portfolio.map((position, index) => (
          <Card key={index} style={styles.positionCard}>
            <Card.Content>
              <View style={styles.positionHeader}>
                <Title>{position.symbol}</Title>
                <Text style={styles.quantityText}>{position.quantity} shares</Text>
              </View>
              <View style={styles.positionDetails}>
                <View style={styles.detailRow}>
                  <Paragraph>Avg Price:</Paragraph>
                  <Paragraph>${position.average_price.toFixed(2)}</Paragraph>
                </View>
                <View style={styles.detailRow}>
                  <Paragraph>Current Value:</Paragraph>
                  <Paragraph>${position.current_value.toFixed(2)}</Paragraph>
                </View>
                <View style={styles.detailRow}>
                  <Paragraph>Profit/Loss:</Paragraph>
                  <Paragraph
                    style={{
                      color: position.profit_loss >= 0 ? '#4caf50' : '#f44336',
                      fontWeight: 'bold',
                    }}
                  >
                    {position.profit_loss >= 0 ? '+' : ''}${position.profit_loss.toFixed(2)} (
                    {position.profit_loss_percentage.toFixed(2)}%)
                  </Paragraph>
                </View>
              </View>
            </Card.Content>
          </Card>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  summaryCard: {
    margin: 16,
    elevation: 4,
  },
  valueText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1a237e',
    marginTop: 8,
  },
  profitLossText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 4,
  },
  actionsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    gap: 12,
  },
  actionButton: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginHorizontal: 16,
    marginTop: 24,
    marginBottom: 12,
  },
  emptyCard: {
    margin: 16,
  },
  emptyText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 16,
  },
  positionCard: {
    marginHorizontal: 16,
    marginBottom: 12,
    elevation: 2,
  },
  positionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  quantityText: {
    fontSize: 14,
    color: '#666',
  },
  positionDetails: {
    gap: 8,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
});
