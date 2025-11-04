import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Title, TextInput, Button, SegmentedButtons, HelperText } from 'react-native-paper';
import { portfolioAPI } from '../services/api';

export default function TradeScreen({ route, navigation }: any) {
  const action = route.params?.action || 'buy';
  const [selectedAction, setSelectedAction] = useState(action);
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleTrade = async () => {
    setError('');

    if (!symbol || !quantity || !price) {
      setError('Please fill in all fields');
      return;
    }

    const qty = parseFloat(quantity);
    const priceVal = parseFloat(price);

    if (isNaN(qty) || qty <= 0) {
      setError('Please enter a valid quantity');
      return;
    }

    if (isNaN(priceVal) || priceVal <= 0) {
      setError('Please enter a valid price');
      return;
    }

    setLoading(true);

    try {
      if (selectedAction === 'buy') {
        await portfolioAPI.buyAsset(symbol.toUpperCase(), qty, priceVal);
        Alert.alert('Success', `Bought ${qty} shares of ${symbol.toUpperCase()}`, [
          { text: 'OK', onPress: () => navigation.goBack() },
        ]);
      } else {
        await portfolioAPI.sellAsset(symbol.toUpperCase(), qty, priceVal);
        Alert.alert('Success', `Sold ${qty} shares of ${symbol.toUpperCase()}`, [
          { text: 'OK', onPress: () => navigation.goBack() },
        ]);
      }
    } catch (err: any) {
      console.error('Trade error:', err);
      setError(err.response?.data?.detail || 'Trade failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>Trade Asset</Title>

          <SegmentedButtons
            value={selectedAction}
            onValueChange={setSelectedAction}
            buttons={[
              { value: 'buy', label: 'Buy' },
              { value: 'sell', label: 'Sell' },
            ]}
            style={styles.segmentedButtons}
          />

          <TextInput
            label="Symbol (e.g., AAPL, BTC)"
            value={symbol}
            onChangeText={setSymbol}
            mode="outlined"
            autoCapitalize="characters"
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Quantity"
            value={quantity}
            onChangeText={setQuantity}
            mode="outlined"
            keyboardType="numeric"
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Price per Unit"
            value={price}
            onChangeText={setPrice}
            mode="outlined"
            keyboardType="numeric"
            style={styles.input}
            disabled={loading}
          />

          {quantity && price && (
            <HelperText type="info">
              Total: ${(parseFloat(quantity) * parseFloat(price)).toFixed(2)}
            </HelperText>
          )}

          {error ? <HelperText type="error">{error}</HelperText> : null}

          <Button
            mode="contained"
            onPress={handleTrade}
            loading={loading}
            disabled={loading}
            style={styles.button}
            buttonColor={selectedAction === 'buy' ? '#4caf50' : '#f44336'}
          >
            {selectedAction === 'buy' ? 'Buy' : 'Sell'} Asset
          </Button>

          <Button mode="text" onPress={() => navigation.goBack()} disabled={loading}>
            Cancel
          </Button>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  segmentedButtons: {
    marginBottom: 24,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 16,
    marginBottom: 8,
    paddingVertical: 8,
  },
});
