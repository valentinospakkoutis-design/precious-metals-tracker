import 'react-native-gesture-handler';
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider, Card, Title, Button, Text } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import PortfolioScreen from './src/screens/PortfolioScreen';
import MetalsScreen from './src/screens/MetalsScreen';
import ChartScreen from './src/screens/ChartScreen';
import { MaterialCommunityIcons } from '@expo/vector-icons';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

function SettingsScreen() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.title}>⚙️ Settings</Title>
          
          {user ? (
            <>
              <Text style={styles.userInfo}>Email: {user?.email}</Text>
              {user?.full_name && <Text style={styles.userInfo}>Name: {user.full_name}</Text>}
              <Text style={styles.userInfo}>
                2FA: {user?.two_factor_enabled ? 'Enabled ✓' : 'Disabled'}
              </Text>
              
              <Button
                mode="contained"
                onPress={handleLogout}
                style={styles.logoutButton}
                icon="logout"
              >
                Logout
              </Button>
            </>
          ) : (
            <>
              <Text style={styles.infoText}>
                💎 Precious Metals Tracker
              </Text>
              <Text style={styles.infoTextSmall}>
                Track real-time prices of Gold, Silver, Platinum, and Palladium with AI-powered predictions.
              </Text>
              <Text style={styles.versionText}>
                Version 1.0.0
              </Text>
            </>
          )}
        </Card.Content>
      </Card>
    </View>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#FFD700',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: { backgroundColor: '#16213e' },
        headerStyle: { backgroundColor: '#16213e' },
        headerTintColor: '#FFD700',
      }}
    >
      <Tab.Screen
        name="Metals"
        component={MetalsScreen}
        options={{
          title: 'Precious Metals',
          tabBarIcon: ({ color, size }: any) => (
            <MaterialCommunityIcons name="gold" size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Charts"
        component={ChartScreen}
        options={{
          title: 'Price Charts',
          tabBarIcon: ({ color, size }: any) => (
            <MaterialCommunityIcons name="chart-line" size={size} color={color} />
          ),
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarIcon: ({ color, size }: any) => (
            <MaterialCommunityIcons name="cog" size={size} color={color} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}

function MainStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="Home"
        component={MainTabs}
        options={{ headerShown: false }}
      />
    </Stack.Navigator>
  );
}

function RootNavigator() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return null;
  }

  return (
    <NavigationContainer>
      {/* Always show main app - no login required for metals tracker */}
      <MainStack />
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <PaperProvider>
      <StatusBar style="auto" />
      <AuthProvider>
        <RootNavigator />
      </AuthProvider>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    padding: 16,
  },
  card: {
    marginTop: 16,
    backgroundColor: '#16213e',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 24,
    textAlign: 'center',
    color: '#FFD700',
  },
  userInfo: {
    fontSize: 16,
    marginBottom: 12,
    color: '#fff',
  },
  logoutButton: {
    marginTop: 24,
    paddingVertical: 8,
    backgroundColor: '#f44336',
  },
  infoText: {
    fontSize: 18,
    color: '#FFD700',
    textAlign: 'center',
    marginBottom: 16,
    fontWeight: 'bold',
  },
  infoTextSmall: {
    fontSize: 14,
    color: '#aaa',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 24,
  },
  versionText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    marginTop: 16,
  },
});
