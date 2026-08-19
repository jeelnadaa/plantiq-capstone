import { View, TextInput, Text, TouchableOpacity, Image, Alert, FlatList, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { useState } from 'react';
import * as ImagePicker from 'expo-image-picker';
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
import { Palette } from '../../constants/palette';
import { BASE_URL } from '../../constants/api';

interface ImageAsset {
  uri: string;
  width: number;
  height: number;
  type?: string;
  fileName?: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'bot';
  text: string;
}

export default function Chatbot() {
  const styles = useThemedStyles(makeStyles);
  const { t } = useLanguage();
  const [msg, setMsg] = useState('');
  const [selectedImage, setSelectedImage] = useState<ImageAsset | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [recognizing, setRecognizing] = useState(false);
  const [translating, setTranslating] = useState(false);
  const [spokenLang, setSpokenLang] = useState<'en' | 'kn'>('en');
  const [sending, setSending] = useState(false);

  useSpeechRecognitionEvent('start', () => setRecognizing(true));
  useSpeechRecognitionEvent('end', () => setRecognizing(false));
  useSpeechRecognitionEvent('result', (event) => {
    const transcript = event.results[0]?.transcript ?? '';
    setMsg(transcript);

    if (event.isFinal && spokenLang === 'kn' && transcript.trim()) {
      setTranslating(true);
      translateText(transcript, 'kn', 'en')
        .then((translated) => setMsg(translated))
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

  const pickImage = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permissionResult.granted === false) {
      Alert.alert('Permission required', 'Permission to access camera roll is required!');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0] as ImageAsset);
    }
  };

  const send = async () => {
    if (!msg.trim() && !selectedImage) {
      Alert.alert('Error', 'Please enter a message or select an image.');
      return;
    }

    const sentText = msg.trim();
    const formData = new FormData();
    if (sentText) {
      formData.append('query', sentText);
    }
    if (selectedImage) {
      const localUri = selectedImage.uri;
      const filename = localUri.split('/').pop() || 'image.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : 'image/jpeg';

      formData.append('image', {
        uri: localUri,
        name: filename,
        type: type,
      } as any);
    }

    if (sentText) {
      setMessages((prev) => [...prev, { id: `${Date.now()}-user`, role: 'user', text: sentText }]);
    }
    setMsg('');
    setSending(true);

    try {
      const response = await axios.post(`${BASE_URL}/chatbot/chat`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessages((prev) => [...prev, { id: `${Date.now()}-bot`, role: 'bot', text: response.data.answer }]);
      setSelectedImage(null);
    } catch (error) {
      console.error('Send error:', error);
      Alert.alert('Error', 'Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  return (
    <SafeAreaView style={styles.flex} edges={['top']}>
      <TopBar />
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        {messages.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyEmoji}>🌾</Text>
            <Text style={styles.emptyTitle}>{t.chatbot.emptyTitle}</Text>
            <Text style={styles.emptySubtitle}>{t.chatbot.emptySubtitle}</Text>
          </View>
        ) : (
          <FlatList
            data={messages}
            keyExtractor={(item) => item.id}
            style={styles.flex}
            contentContainerStyle={{ padding: 16 }}
            renderItem={({ item }) => (
              <View
                style={[
                  styles.bubble,
                  item.role === 'user' ? styles.bubbleUser : styles.bubbleBot,
                ]}
              >
                <Text style={item.role === 'user' ? styles.bubbleTextUser : styles.bubbleTextBot}>
                  {item.text}
                </Text>
              </View>
            )}
          />
        )}

        {translating && (
          <Text style={styles.translatingText}>{t.chatbot.translating}</Text>
        )}

        {selectedImage && (
          <View style={styles.imagePreviewWrap}>
            <Image source={{ uri: selectedImage.uri }} style={styles.imagePreview} />
            <TouchableOpacity style={styles.removeImageBtn} onPress={() => setSelectedImage(null)}>
              <Ionicons name="close" size={16} color="#fff" />
            </TouchableOpacity>
          </View>
        )}

        <View style={styles.inputBar}>
          <TouchableOpacity onPress={pickImage} style={styles.iconBtn}>
            <Ionicons name="image-outline" size={22} color={styles.iconBtnIcon.color} />
          </TouchableOpacity>

          <TextInput
            placeholder={t.chatbot.inputPlaceholder}
            placeholderTextColor={styles.placeholderColor.color}
            value={msg}
            onChangeText={setMsg}
            style={styles.input}
            multiline
          />

          <TouchableOpacity
            onPress={() => setSpokenLang((prev) => (prev === 'en' ? 'kn' : 'en'))}
            disabled={recognizing}
            style={[styles.langBtn, recognizing && styles.disabled]}
          >
            <Text style={styles.langBtnText}>{spokenLang === 'kn' ? 'ಕ' : 'EN'}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={toggleVoiceInput}
            disabled={translating}
            style={[styles.iconBtnFilled, recognizing && styles.recording, translating && styles.disabled]}
          >
            <Ionicons name={recognizing ? 'stop' : 'mic'} size={18} color="#fff" />
          </TouchableOpacity>

          <TouchableOpacity
            onPress={send}
            disabled={sending}
            style={[styles.sendBtn, sending && styles.disabled]}
          >
            <Ionicons name="send" size={18} color="#fff" />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  emptyState: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 30 },
  emptyEmoji: { fontSize: 48, marginBottom: 12 },
  emptyTitle: { fontSize: 18, fontWeight: '700', color: colors.text },
  emptySubtitle: { fontSize: 14, color: colors.textMuted, textAlign: 'center', marginTop: 6 },
  bubble: {
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginVertical: 5,
    maxWidth: '80%',
  },
  bubbleUser: { alignSelf: 'flex-end', backgroundColor: colors.bubbleUser, borderBottomRightRadius: 4 },
  bubbleBot: { alignSelf: 'flex-start', backgroundColor: colors.bubbleBot, borderBottomLeftRadius: 4 },
  bubbleTextUser: { color: '#fff', fontSize: 15 },
  bubbleTextBot: { color: colors.text, fontSize: 15 },
  translatingText: { color: colors.textMuted, textAlign: 'center', marginBottom: 4, fontSize: 13 },
  imagePreviewWrap: { alignSelf: 'flex-start', marginLeft: 16, marginBottom: 8, position: 'relative' },
  imagePreview: { width: 90, height: 70, borderRadius: 10 },
  removeImageBtn: {
    position: 'absolute', top: -6, right: -6, backgroundColor: colors.danger,
    width: 22, height: 22, borderRadius: 11, alignItems: 'center', justifyContent: 'center',
  },
  inputBar: {
    flexDirection: 'row', alignItems: 'flex-end', gap: 8,
    paddingHorizontal: 12, paddingVertical: 10,
    backgroundColor: colors.surface,
    borderTopWidth: 1, borderTopColor: colors.border,
  },
  iconBtn: {
    width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.accent,
  },
  iconBtnIcon: { color: colors.primary },
  input: {
    flex: 1, borderWidth: 1.5, borderColor: colors.border, borderRadius: 20,
    paddingHorizontal: 14, paddingVertical: 10, maxHeight: 100,
    backgroundColor: colors.surface, color: colors.text, fontSize: 15,
  },
  langBtn: {
    width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.primaryLight,
  },
  langBtnText: { color: '#fff', fontWeight: '700', fontSize: 13 },
  iconBtnFilled: {
    width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.primary,
  },
  recording: { backgroundColor: colors.danger },
  sendBtn: {
    width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.primaryDark,
  },
  disabled: { opacity: 0.5 },
  placeholderColor: { color: colors.placeholder },
});
