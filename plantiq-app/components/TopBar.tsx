import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme, useThemedStyles } from '../context/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { Palette } from '../constants/palette';

export default function TopBar() {
  const { mode, colors, toggleTheme } = useTheme();
  const { language, toggleLanguage, t } = useLanguage();
  const styles = useThemedStyles(makeStyles);

  return (
    <View style={styles.container}>
      <View style={styles.brand}>
        <View style={styles.logoBox}>
          <Ionicons name="leaf" size={20} color="#fff" />
        </View>
        <Text style={styles.brandText}>{t.common.brand}</Text>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity onPress={toggleLanguage} style={styles.langBtn} activeOpacity={0.8}>
          <Ionicons name="globe-outline" size={16} color={colors.text} />
          <Text style={styles.langBtnText}>{language === 'kn' ? 'ಕನ್ನಡ' : 'EN'}</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={toggleTheme} style={styles.themeBtn} activeOpacity={0.8}>
          <Ionicons name={mode === 'dark' ? 'sunny-outline' : 'moon-outline'} size={19} color={colors.text} />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 14,
    paddingBottom: 14,
    backgroundColor: colors.background,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  logoBox: {
    width: 34, height: 34, borderRadius: 10,
    backgroundColor: colors.primary,
    alignItems: 'center', justifyContent: 'center',
  },
  brandText: { fontSize: 18, fontWeight: '800', color: colors.text },
  actions: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  langBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    height: 36, paddingHorizontal: 10, borderRadius: 18,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  langBtnText: { fontSize: 12, fontWeight: '700', color: colors.text },
  themeBtn: {
    width: 36, height: 36, borderRadius: 18,
    alignItems: 'center', justifyContent: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
});
