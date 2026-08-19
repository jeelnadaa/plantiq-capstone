import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { useEffect, useState, useCallback } from 'react';
import { useRouter, useFocusEffect } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import TopBar from '../../components/TopBar';
import { useThemedStyles } from '../../context/ThemeContext';
import { useLanguage } from '../../context/LanguageContext';
import { Palette, shadow } from '../../constants/palette';
import { BASE_URL } from '../../constants/api';

type Listing = {
  coffee_type: string;
  price: number;
  latitude: number;
  longitude: number;
};

export default function Marketplace() {
  const styles = useThemedStyles(makeStyles);
  const { t } = useLanguage();
  const [data, setData] = useState<Listing[]>([]);
  const [isFarmer, setIsFarmer] = useState(false);
  const router = useRouter();

  useEffect(() => {
    AsyncStorage.getItem('user').then((user) => {
      if (user) setIsFarmer(JSON.parse(user).role === 'farmer');
    });
  }, []);

  const loadListings = useCallback(() => {
    fetch(`${BASE_URL}/market/listings`)
      .then(res => res.json())
      .then(setData)
      .catch(err => console.log(err));
  }, []);

  useFocusEffect(useCallback(() => { loadListings(); }, [loadListings]));

  return (
    <SafeAreaView style={styles.flex} edges={['top']}>
      <TopBar />
      <View style={styles.container}>
        <Text style={styles.title}>{t.marketplace.title}</Text>

        <FlatList
          data={data}
          keyExtractor={(item, index) => index.toString()}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <Text style={styles.emptyEmoji}>☕</Text>
              <Text style={styles.emptyTitle}>{t.marketplace.emptyTitle}</Text>
              <Text style={styles.emptySubtitle}>{t.marketplace.emptySubtitle}</Text>
            </View>
          }
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.coffeeType}>{item.coffee_type}</Text>
                <Text style={styles.price}>₹{item.price}<Text style={styles.priceUnit}>/kg</Text></Text>
              </View>

              <TouchableOpacity
                style={styles.locationBtn}
                activeOpacity={0.8}
                onPress={() =>
                  router.push(
                    `/customer/map?lat=${item.latitude}&lng=${item.longitude}`
                  )
                }
              >
                <Ionicons name="location-outline" size={16} color={styles.locationBtnText.color} />
                <Text style={styles.locationBtnText}>{t.marketplace.viewLocation}</Text>
              </TouchableOpacity>
            </View>
          )}
        />

        {isFarmer && (
          <TouchableOpacity
            style={styles.fab}
            activeOpacity={0.85}
            onPress={() => router.push('/farmer/add')}
          >
            <Ionicons name="add" size={28} color="#fff" />
          </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { flex: 1, padding: 20 },
  title: { fontSize: 22, fontWeight: '800', color: colors.text, marginBottom: 16, marginTop: 4 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    ...shadow,
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  coffeeType: { fontSize: 17, fontWeight: '700', color: colors.text },
  price: { fontSize: 17, fontWeight: '800', color: colors.primary },
  priceUnit: { fontSize: 12, fontWeight: '500', color: colors.textMuted },
  locationBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    alignSelf: 'flex-start',
    backgroundColor: colors.accent,
    paddingVertical: 8, paddingHorizontal: 12,
    borderRadius: 10,
  },
  locationBtnText: { color: colors.primary, fontWeight: '600', fontSize: 13 },
  emptyState: { alignItems: 'center', justifyContent: 'center', marginTop: 60 },
  emptyEmoji: { fontSize: 44, marginBottom: 10 },
  emptyTitle: { fontSize: 16, fontWeight: '700', color: colors.text },
  emptySubtitle: { fontSize: 13, color: colors.textMuted, marginTop: 4, textAlign: 'center' },
  fab: {
    position: 'absolute',
    right: 4,
    bottom: 16,
    width: 56, height: 56, borderRadius: 28,
    backgroundColor: colors.primary,
    alignItems: 'center', justifyContent: 'center',
    ...shadow,
  },
});
