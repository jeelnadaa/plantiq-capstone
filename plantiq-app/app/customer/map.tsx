<<<<<<< HEAD
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { useLocalSearchParams, useRouter } from 'expo-router';
import * as Linking from 'expo-linking';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useThemedStyles } from '../../context/ThemeContext';
import { useLanguage } from '../../context/LanguageContext';
import { Palette, shadow } from '../../constants/palette';

export default function MapScreen() {
  const { lat, lng } = useLocalSearchParams();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const styles = useThemedStyles(makeStyles);
  const { t } = useLanguage();
=======
import { View, StyleSheet, Button } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { useLocalSearchParams } from 'expo-router';
import * as Linking from 'expo-linking';

export default function MapScreen() {
  const { lat, lng } = useLocalSearchParams();
>>>>>>> d6b66db (first commit)

  const latitude = parseFloat(lat as string);
  const longitude = parseFloat(lng as string);

  const openNavigation = () => {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
    Linking.openURL(url);
  };

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: latitude || 12.9716,
          longitude: longitude || 77.5946,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01
        }}
        showsUserLocation
      >
<<<<<<< HEAD
        <Marker coordinate={{ latitude, longitude }} title="Farmer" />
      </MapView>

      <TouchableOpacity onPress={() => router.back()} style={[styles.backBtn, { top: insets.top + 12 }]}>
        <Ionicons name="arrow-back" size={22} color={styles.backBtnIcon.color} />
      </TouchableOpacity>

      <View style={styles.bottomBar}>
        <TouchableOpacity style={styles.navigateBtn} onPress={openNavigation} activeOpacity={0.85}>
          <Ionicons name="navigate" size={18} color="#fff" />
          <Text style={styles.navigateBtnText}>{t.map.navigate}</Text>
        </TouchableOpacity>
      </View>
=======
        <Marker coordinate={{ latitude, longitude }} />
      </MapView>

      <Button title="Navigate to Farmer" onPress={openNavigation} />
>>>>>>> d6b66db (first commit)
    </View>
  );
}

<<<<<<< HEAD
const makeStyles = (colors: Palette) => StyleSheet.create({
  container: { flex: 1 },
  map: { flex: 1 },
  backBtn: {
    position: 'absolute',
    left: 16,
    width: 40, height: 40, borderRadius: 20,
    alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.surface,
    ...shadow,
  },
  backBtnIcon: { color: colors.text },
  bottomBar: {
    position: 'absolute',
    bottom: 24,
    left: 16,
    right: 16,
  },
  navigateBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: colors.primary,
    paddingVertical: 15,
    borderRadius: 14,
    ...shadow,
  },
  navigateBtnText: { color: '#fff', fontSize: 15, fontWeight: '700' },
});
=======
const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { flex: 1 }
});
>>>>>>> d6b66db (first commit)
