import { View, Text, TouchableOpacity, StyleSheet, Switch } from 'react-native';
import { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import TopBar from '../../components/TopBar';
import { useTheme, useThemedStyles } from '../../context/ThemeContext';
import { useLanguage } from '../../context/LanguageContext';
import { Palette, shadow } from '../../constants/palette';

type User = { name?: string; email?: string; role?: string };

export default function Profile() {
  const styles = useThemedStyles(makeStyles);
  const { mode, toggleTheme } = useTheme();
  const { language, toggleLanguage, t } = useLanguage();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    AsyncStorage.getItem('user').then((stored) => {
      if (stored) setUser(JSON.parse(stored));
    });
  }, []);

  const handleLogout = async () => {
    await AsyncStorage.removeItem('token');
    await AsyncStorage.removeItem('user');
    router.replace('/login');
  };

  return (
    <SafeAreaView style={styles.flex} edges={['top']}>
      <TopBar />
      <View style={styles.container}>
        <Text style={styles.title}>{t.profile.title}</Text>

        <View style={styles.card}>
          <View style={styles.avatar}>
            <Ionicons name="person" size={28} color="#fff" />
          </View>
          <Text style={styles.name}>{user?.name || t.common.brand + ' User'}</Text>
          <Text style={styles.email}>{user?.email || '—'}</Text>
          {user?.role && (
            <View style={styles.roleBadge}>
              <Text style={styles.roleBadgeText}>
                {user.role === 'farmer' ? t.login.farmer : t.login.customer}
              </Text>
            </View>
          )}
        </View>

        <View style={styles.settingRow}>
          <View style={styles.settingLabelRow}>
            <Ionicons name="globe-outline" size={18} color={styles.settingIcon.color} />
            <Text style={styles.settingLabel}>{language === 'kn' ? 'ಕನ್ನಡ' : 'English'}</Text>
          </View>
          <Switch value={language === 'kn'} onValueChange={toggleLanguage} />
        </View>

        <View style={styles.settingRow}>
          <View style={styles.settingLabelRow}>
            <Ionicons name={mode === 'dark' ? 'moon' : 'sunny'} size={18} color={styles.settingIcon.color} />
            <Text style={styles.settingLabel}>{t.profile.darkMode}</Text>
          </View>
          <Switch value={mode === 'dark'} onValueChange={toggleTheme} />
        </View>

        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout} activeOpacity={0.85}>
          <Ionicons name="log-out-outline" size={18} color="#fff" />
          <Text style={styles.logoutBtnText}>{t.profile.logout}</Text>
        </TouchableOpacity>
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
    borderRadius: 18,
    padding: 24,
    alignItems: 'center',
    ...shadow,
  },
  avatar: {
    width: 64, height: 64, borderRadius: 32,
    backgroundColor: colors.primary,
    alignItems: 'center', justifyContent: 'center',
    marginBottom: 12,
  },
  name: { fontSize: 18, fontWeight: '700', color: colors.text },
  email: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  roleBadge: {
    marginTop: 10, backgroundColor: colors.accent,
    paddingHorizontal: 12, paddingVertical: 5, borderRadius: 20,
  },
  roleBadgeText: { fontSize: 12, fontWeight: '600', color: colors.primary },
  settingRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    backgroundColor: colors.surface,
    borderRadius: 14,
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginTop: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  settingLabelRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  settingIcon: { color: colors.text },
  settingLabel: { fontSize: 15, fontWeight: '600', color: colors.text },
  logoutBtn: {
    flexDirection: 'row', gap: 8, alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.danger,
    borderRadius: 14,
    paddingVertical: 15,
    marginTop: 24,
  },
  logoutBtnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
});
