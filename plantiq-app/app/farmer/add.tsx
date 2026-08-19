<<<<<<< HEAD
import { View, Text, TextInput, TouchableOpacity, Alert, StyleSheet, ActivityIndicator, ScrollView } from 'react-native';
import { useState, useEffect } from 'react';
import * as Location from 'expo-location';
import axios from 'axios';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useThemedStyles } from '../../context/ThemeContext';
import { useLanguage } from '../../context/LanguageContext';
import { Palette, shadow } from '../../constants/palette';
import { BASE_URL } from '../../constants/api';

type LocStatus = 'idle' | 'fetching' | 'done' | 'denied' | 'error';

export default function AddProduct() {
  const router = useRouter();
  const styles = useThemedStyles(makeStyles);
  const { t } = useLanguage();
=======
import { View, TextInput, Button, Alert, StyleSheet } from 'react-native';
import { useState } from 'react';
import axios from 'axios';

export default function AddProduct() {
>>>>>>> d6b66db (first commit)

  const [form, setForm] = useState({
    coffee_type: '',
    price: '',
    latitude: '',
    longitude: ''
  });

<<<<<<< HEAD
  const [locStatus, setLocStatus] = useState<LocStatus>('idle');
  const [submitting, setSubmitting] = useState(false);

  const fetchLocation = async () => {
    try {
      setLocStatus('fetching');

      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setLocStatus('denied');
        Alert.alert('Permission needed', 'Location access is required to tag your farm.');
        return;
      }

      const loc = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      setForm((prev) => ({
        ...prev,
        latitude: loc.coords.latitude.toString(),
        longitude: loc.coords.longitude.toString(),
      }));

      setLocStatus('done');
    } catch (err: any) {
      console.log('LOCATION ERROR:', err.message);
      setLocStatus('error');
      Alert.alert('Error', 'Could not get your location. Try again.');
    }
  };

  useEffect(() => {
    fetchLocation();
  }, []);

  const submit = async () => {
    try {
      if (!form.coffee_type || !form.price) {
        Alert.alert('Error', 'Fill all fields');
        return;
      }

      if (!form.latitude || !form.longitude) {
        Alert.alert('Error', 'Location not captured yet. Tap "Use my location".');
        return;
      }

      setSubmitting(true);

      const res = await axios.post(
        `${BASE_URL}/market/add`,
=======
  const submit = async () => {
    try {
      console.log("Submitting:", form);

      if (!form.coffee_type || !form.price || !form.latitude || !form.longitude) {
        Alert.alert("Error", "Fill all fields");
        return;
      }

      const res = await axios.post(
        'http://192.168.137.235:5000/market/add',
>>>>>>> d6b66db (first commit)
        {
          coffee_type: form.coffee_type,
          price: parseInt(form.price),
          latitude: parseFloat(form.latitude),
          longitude: parseFloat(form.longitude)
        }
      );

<<<<<<< HEAD
      console.log('SUCCESS:', res.data);

      Alert.alert('Success', 'Product added!');
=======
      console.log("SUCCESS:", res.data);

      Alert.alert("Success", "Product added!");
>>>>>>> d6b66db (first commit)

      setForm({
        coffee_type: '',
        price: '',
        latitude: '',
        longitude: ''
      });
<<<<<<< HEAD
      setLocStatus('idle');
      fetchLocation();

    } catch (err: any) {
      console.log('ERROR:', err.message);
      Alert.alert('Error', 'Backend not reachable');
    } finally {
      setSubmitting(false);
=======

    } catch (err: any) {
      console.log("ERROR:", err.message);
      Alert.alert("Error", "Backend not reachable");
>>>>>>> d6b66db (first commit)
    }
  };

  return (
<<<<<<< HEAD
    <SafeAreaView style={styles.flex} edges={['top']}>
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color={styles.backBtnIcon.color} />
        </TouchableOpacity>
        <Text style={styles.title}>{t.addProduct.title}</Text>
        <View style={{ width: 36 }} />
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>{t.addProduct.coffeeType}</Text>
        <TextInput
          placeholder={t.addProduct.coffeeTypePlaceholder}
          placeholderTextColor={styles.placeholderColor.color}
          value={form.coffee_type}
          onChangeText={(v) => setForm({ ...form, coffee_type: v })}
          style={styles.input}
        />

        <Text style={styles.label}>{t.addProduct.price}</Text>
        <TextInput
          placeholder={t.addProduct.pricePlaceholder}
          placeholderTextColor={styles.placeholderColor.color}
          keyboardType="numeric"
          value={form.price}
          onChangeText={(v) => setForm({ ...form, price: v })}
          style={styles.input}
        />

        <View style={styles.locationBox}>
          {locStatus === 'fetching' && (
            <View style={styles.row}>
              <ActivityIndicator color={styles.spinner.color} />
              <Text style={styles.locText}>  {t.scanner.gettingLocation}</Text>
            </View>
          )}

          {locStatus === 'done' && (
            <Text style={styles.locText}>
              📍 Location captured{'\n'}
              Lat: {parseFloat(form.latitude).toFixed(5)}{'\n'}
              Lng: {parseFloat(form.longitude).toFixed(5)}
            </Text>
          )}

          {(locStatus === 'denied' || locStatus === 'error') && (
            <Text style={[styles.locText, styles.locError]}>
              Location not available. Tap below to retry.
            </Text>
          )}

          <TouchableOpacity style={styles.secondaryBtn} onPress={fetchLocation} activeOpacity={0.8}>
            <Text style={styles.secondaryBtnText}>
              {locStatus === 'done' ? t.addProduct.refreshLocation : t.addProduct.useMyLocation}
            </Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.submitBtn} onPress={submit} disabled={submitting} activeOpacity={0.85}>
          {submitting
            ? <ActivityIndicator color="#fff" />
            : <Text style={styles.submitText}>{t.addProduct.submit}</Text>
          }
        </TouchableOpacity>
      </View>
    </ScrollView>
    </SafeAreaView>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { flexGrow: 1, padding: 20, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    marginBottom: 20, marginTop: 8,
  },
  backBtn: {
    width: 36, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.surface, ...shadow,
  },
  backBtnIcon: { color: colors.text },
  title: { fontSize: 20, fontWeight: '800', color: colors.text },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 18,
    padding: 20,
    ...shadow,
  },
  label: { fontSize: 13, fontWeight: '600', color: colors.textMuted, marginBottom: 6, marginTop: 10 },
  input: {
    borderWidth: 1.5,
    borderColor: colors.border,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    backgroundColor: colors.surface,
    fontSize: 15,
    color: colors.text,
  },
  locationBox: {
    borderWidth: 1.5,
    borderColor: colors.border,
    borderRadius: 12,
    padding: 14,
    marginTop: 16,
    backgroundColor: colors.background,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  locText: {
    fontSize: 14,
    lineHeight: 20,
    color: colors.text,
  },
  locError: {
    color: colors.danger
  },
  secondaryBtn: {
    marginTop: 10,
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
    backgroundColor: colors.accent,
  },
  secondaryBtnText: { color: colors.primary, fontWeight: '700', fontSize: 14 },
  submitBtn: {
    backgroundColor: colors.primary,
    paddingVertical: 15,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
  },
  submitText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  placeholderColor: { color: colors.placeholder },
  spinner: { color: colors.primary },
});
=======
    <View style={styles.container}>

      <TextInput
        placeholder="Coffee Type"
        value={form.coffee_type}
        onChangeText={(v) => setForm({ ...form, coffee_type: v })}
        style={styles.input}
      />

      <TextInput
        placeholder="Price"
        keyboardType="numeric"
        value={form.price}
        onChangeText={(v) => setForm({ ...form, price: v })}
        style={styles.input}
      />

      <TextInput
        placeholder="Latitude"
        keyboardType="numeric"
        value={form.latitude}
        onChangeText={(v) => setForm({ ...form, latitude: v })}
        style={styles.input}
      />

      <TextInput
        placeholder="Longitude"
        keyboardType="numeric"
        value={form.longitude}
        onChangeText={(v) => setForm({ ...form, longitude: v })}
        style={styles.input}
      />

      <Button title="SUBMIT" onPress={submit} />

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff'
  },
  input: {
    borderWidth: 1,
    marginVertical: 8,
    padding: 10,
    borderRadius: 8
  }
});
>>>>>>> d6b66db (first commit)
