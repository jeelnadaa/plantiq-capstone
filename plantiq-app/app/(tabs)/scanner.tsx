import { View, Text, TextInput, TouchableOpacity, Image, Alert, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { useState } from 'react';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import * as Linking from 'expo-linking';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  ExpoSpeechRecognitionModule,
  useSpeechRecognitionEvent,
} from 'expo-speech-recognition';
import TopBar from '../../components/TopBar';
import { translateText } from '../../utils/translate';
import { useThemedStyles } from '../../context/ThemeContext';
import { useLanguage } from '../../context/LanguageContext';
import { Palette, shadow } from '../../constants/palette';
import { BASE_URL } from '../../constants/api';

interface ImageAsset {
  uri: string;
  width: number;
  height: number;
  type?: string;
  fileName?: string;
}

export default function Scanner() {
  const styles = useThemedStyles(makeStyles);
  const { t } = useLanguage();

  const [image, setImage] = useState<ImageAsset | null>(null);
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [locStatus, setLocStatus] = useState<'idle' | 'fetching' | 'done' | 'error'>('idle');
  const [manualEntry, setManualEntry] = useState(false);
  const [question, setQuestion] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [recognizing, setRecognizing] = useState(false);
  const [translating, setTranslating] = useState(false);
  const [spokenLang, setSpokenLang] = useState<'en' | 'kn'>('en');

  useSpeechRecognitionEvent('start', () => setRecognizing(true));
  useSpeechRecognitionEvent('end', () => setRecognizing(false));
  useSpeechRecognitionEvent('result', (event) => {
    const transcript = event.results[0]?.transcript ?? '';
    setQuestion(transcript);

    if (event.isFinal && spokenLang === 'kn' && transcript.trim()) {
      setTranslating(true);
      translateText(transcript, 'kn', 'en')
        .then((translated) => setQuestion(translated))
        .finally(() => setTranslating(false));
    }
  });
  useSpeechRecognitionEvent('error', (event) => {
    setRecognizing(false);
    Alert.alert('Speech recognition error', event.message);
  });

  const toggleVoiceInput = async () => {
    if (recognizing) {
      ExpoSpeechRecognitionModule.stop();
      return;
    }
    const permissions = await ExpoSpeechRecognitionModule.requestPermissionsAsync();
    if (!permissions.granted) {
      Alert.alert('Permission required', 'Microphone and speech recognition permissions are required.');
      return;
    }
    ExpoSpeechRecognitionModule.start({
      lang: spokenLang === 'kn' ? 'kn-IN' : 'en-US',
      interimResults: true,
      continuous: false,
    });
  };

  const fetchLocation = async () => {
    try {
      setLocStatus('fetching');
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setLocStatus('error');
        Alert.alert('Permission needed', 'Location access is required for microclimate data.');
        return;
      }
      const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
      setLatitude(loc.coords.latitude.toFixed(4));
      setLongitude(loc.coords.longitude.toFixed(4));
      setLocStatus('done');
    } catch (err) {
      setLocStatus('error');
      Alert.alert('Error', 'Could not get your location.');
    }
  };

  const openGMapsGuide = () => {
    Alert.alert(
      'Finding coordinates manually',
      'Open Google Maps, long-press your farm location on the map, and copy the latitude/longitude shown at the bottom to enter here.',
      [
        { text: 'Open Google Maps', onPress: () => Linking.openURL('https://maps.google.com') },
        { text: 'Cancel', style: 'cancel' },
      ]
    );
  };

  const pickImage = () => {
    Alert.alert('Add a leaf photo', 'Choose a source', [
      { text: 'Take Photo', onPress: takePhoto },
      { text: 'Choose from Gallery', onPress: chooseFromGallery },
      { text: 'Cancel', style: 'cancel' },
    ]);
  };

  const takePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission required', 'Camera access is required to take a photo.');
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.9,
    });
    if (!result.canceled) setImage(result.assets[0] as ImageAsset);
  };

  const chooseFromGallery = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission required', 'Photo library access is required.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.9,
    });
    if (!result.canceled) setImage(result.assets[0] as ImageAsset);
  };

  const analyzeLeaf = async () => {
    if (!image) {
      Alert.alert('Photo required', 'Please take or upload a photo of the coffee leaf first.');
      return;
    }
    if (!latitude || !longitude) {
      Alert.alert('Location required', 'Please set a location (Auto GPS or Manual Entry) so we can factor in live weather conditions.');
      return;
    }

    const formData = new FormData();
    const filename = image.uri.split('/').pop() || 'leaf.jpg';
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';
    formData.append('image', { uri: image.uri, name: filename, type } as any);
    formData.append('latitude', latitude);
    formData.append('longitude', longitude);
    if (question.trim()) formData.append('question', question.trim());

    setAnalyzing(true);
    try {
      const response = await axios.post(`${BASE_URL}/scan`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      Alert.alert('Advisory', response.data?.answer || 'No advisory returned.');
    } catch (error) {
      console.error('Analyze error:', error);
      Alert.alert('Error', 'Could not reach the advisory service. Please try again later.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <SafeAreaView style={styles.flex} edges={['top']}>
      <TopBar />
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Text style={styles.title}>{t.scanner.title}</Text>
        <Text style={styles.subtitle}>{t.scanner.subtitle}</Text>

        <TouchableOpacity style={styles.uploadCard} onPress={pickImage} activeOpacity={0.8}>
          {image ? (
            <Image source={{ uri: image.uri }} style={styles.uploadedImage} />
          ) : (
            <>
              <View style={styles.cameraIconWrap}>
                <Ionicons name="camera-outline" size={26} color="white" />
              </View>
              <Text style={styles.uploadTitle}>{t.scanner.uploadTitle}</Text>
              <Text style={styles.uploadSubtitle}>{t.scanner.uploadSubtitle}</Text>
            </>
          )}
        </TouchableOpacity>

        <View style={styles.card}>
          <View style={styles.locationHeader}>
            <View style={styles.locationTitleRow}>
              <Ionicons name="location-outline" size={16} color={styles.locationTitle.color} />
              <Text style={styles.locationTitle}>{t.scanner.locationTitle}</Text>
            </View>
            <TouchableOpacity style={styles.guideBtn} onPress={openGMapsGuide}>
              <Ionicons name="help-circle-outline" size={14} color={styles.guideBtnText.color} />
              <Text style={styles.guideBtnText}>{t.scanner.gmapsGuide}</Text>
            </TouchableOpacity>
          </View>

          {locStatus === 'fetching' ? (
            <View style={styles.row}>
              <ActivityIndicator size="small" />
              <Text style={styles.locValue}>  {t.scanner.gettingLocation}</Text>
            </View>
          ) : (
            <Text style={styles.locValue}>
              {latitude && longitude ? `${latitude}, ${longitude} (${t.scanner.autoGps})` : t.scanner.noLocation}
            </Text>
          )}

          {manualEntry && (
            <View style={styles.manualRow}>
              <TextInput
                placeholder={t.scanner.latitude}
                placeholderTextColor={styles.placeholderColor.color}
                value={latitude}
                onChangeText={setLatitude}
                keyboardType="numeric"
                style={[styles.input, { flex: 1 }]}
              />
              <TextInput
                placeholder={t.scanner.longitude}
                placeholderTextColor={styles.placeholderColor.color}
                value={longitude}
                onChangeText={setLongitude}
                keyboardType="numeric"
                style={[styles.input, { flex: 1 }]}
              />
            </View>
          )}

          <View style={styles.locBtnRow}>
            <TouchableOpacity style={styles.autoGpsBtn} onPress={fetchLocation} activeOpacity={0.85}>
              <Ionicons name="locate-outline" size={16} color="#fff" />
              <Text style={styles.autoGpsBtnText}>{t.scanner.autoGps}</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.manualBtn}
              onPress={() => setManualEntry((prev) => !prev)}
              activeOpacity={0.85}
            >
              <Ionicons name="create-outline" size={16} color={styles.manualBtnText.color} />
              <Text style={styles.manualBtnText}>{t.scanner.manualEntry}</Text>
            </TouchableOpacity>
          </View>
        </View>

        <Text style={styles.label}>{t.scanner.questionLabel}</Text>
        <View style={styles.questionRow}>
          <TextInput
            placeholder={t.scanner.questionPlaceholder}
            placeholderTextColor={styles.placeholderColor.color}
            value={question}
            onChangeText={setQuestion}
            style={styles.questionInput}
            multiline
          />
          <TouchableOpacity
            onPress={toggleVoiceInput}
            disabled={translating}
            style={[styles.micBtn, recognizing && styles.recording, translating && styles.disabled]}
          >
            <Ionicons name={recognizing ? 'stop' : 'mic-outline'} size={18} color={styles.micBtnIcon.color} />
          </TouchableOpacity>
        </View>
        {translating && <Text style={styles.translatingText}>{t.scanner.translating}</Text>}

        <TouchableOpacity
          style={[styles.analyzeBtn, analyzing && styles.disabled]}
          onPress={analyzeLeaf}
          disabled={analyzing}
          activeOpacity={0.88}
        >
          {analyzing ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="sparkles" size={18} color="#fff" />
              <Text style={styles.analyzeBtnText}>{t.scanner.analyzeLeaf}</Text>
            </>
          )}
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { padding: 20, paddingBottom: 40 },
  title: { fontSize: 22, fontWeight: '800', color: colors.text, marginTop: 4 },
  subtitle: { fontSize: 14, color: colors.textMuted, marginTop: 8, lineHeight: 20 },
  uploadCard: {
    marginTop: 20,
    borderWidth: 1.5,
    borderColor: colors.border,
    borderStyle: 'dashed',
    borderRadius: 16,
    paddingVertical: 36,
    alignItems: 'center',
    backgroundColor: colors.surface,
  },
  cameraIconWrap: {
    width: 56, height: 56, borderRadius: 28,
    backgroundColor: colors.primary,
    alignItems: 'center', justifyContent: 'center',
    marginBottom: 14,
  },
  uploadTitle: { fontSize: 15, fontWeight: '700', color: colors.text },
  uploadSubtitle: { fontSize: 12, color: colors.textMuted, marginTop: 4 },
  uploadedImage: { width: '100%', height: 180, borderRadius: 12 },
  card: {
    marginTop: 18,
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  locationHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  locationTitleRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  locationTitle: { fontSize: 14, fontWeight: '700', color: colors.text },
  guideBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    borderWidth: 1, borderColor: colors.border, borderRadius: 20,
    paddingHorizontal: 10, paddingVertical: 6,
  },
  guideBtnText: { fontSize: 11, fontWeight: '600', color: colors.textMuted },
  row: { flexDirection: 'row', alignItems: 'center', marginTop: 10 },
  locValue: { fontSize: 13, color: colors.textMuted, marginTop: 10 },
  manualRow: { flexDirection: 'row', gap: 10, marginTop: 12 },
  input: {
    borderWidth: 1.5, borderColor: colors.border, borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 10, fontSize: 13,
    backgroundColor: colors.background, color: colors.text,
  },
  locBtnRow: { flexDirection: 'row', gap: 10, marginTop: 14 },
  autoGpsBtn: {
    flex: 1, flexDirection: 'row', gap: 6, alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.primary, borderRadius: 12, paddingVertical: 12,
  },
  autoGpsBtnText: { color: '#fff', fontWeight: '700', fontSize: 13 },
  manualBtn: {
    flex: 1, flexDirection: 'row', gap: 6, alignItems: 'center', justifyContent: 'center',
    borderWidth: 1.5, borderColor: colors.border, borderRadius: 12, paddingVertical: 12,
  },
  manualBtnText: { color: colors.text, fontWeight: '700', fontSize: 13 },
  label: { fontSize: 14, fontWeight: '700', color: colors.text, marginTop: 20, marginBottom: 8 },
  questionRow: { flexDirection: 'row', alignItems: 'flex-end', gap: 8 },
  questionInput: {
    flex: 1, borderWidth: 1.5, borderColor: colors.border, borderRadius: 12,
    paddingHorizontal: 14, paddingVertical: 12, maxHeight: 100,
    backgroundColor: colors.surface, color: colors.text, fontSize: 14,
  },
  micBtn: {
    width: 42, height: 42, borderRadius: 21,
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 1.5, borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  micBtnIcon: { color: colors.text },
  recording: { backgroundColor: colors.danger, borderColor: colors.danger },
  translatingText: { color: colors.textMuted, fontSize: 12, marginTop: 6 },
  analyzeBtn: {
    flexDirection: 'row', gap: 8, alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.primary, borderRadius: 14, paddingVertical: 16,
    marginTop: 24, ...shadow,
  },
  analyzeBtnText: { color: '#fff', fontWeight: '800', fontSize: 16 },
  disabled: { opacity: 0.6 },
  placeholderColor: { color: colors.placeholder },
});
