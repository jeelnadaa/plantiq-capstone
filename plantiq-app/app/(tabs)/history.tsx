import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import TopBar from '../../components/TopBar';
import { useThemedStyles } from '../../context/ThemeContext';
import { useLanguage } from '../../context/LanguageContext';
import { Palette } from '../../constants/palette';

export default function History() {
  const styles = useThemedStyles(makeStyles);
  const { t } = useLanguage();

  return (
    <SafeAreaView style={styles.flex} edges={['top']}>
      <TopBar />
      <View style={styles.container}>
        <Text style={styles.title}>{t.history.title}</Text>

        <View style={styles.emptyState}>
          <Ionicons name="time-outline" size={44} color={styles.emptyIcon.color} />
          <Text style={styles.emptyTitle}>{t.history.emptyTitle}</Text>
          <Text style={styles.emptySubtitle}>{t.history.emptySubtitle}</Text>
        </View>
      </View>
    </SafeAreaView>
  );
}

const makeStyles = (colors: Palette) => StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { flex: 1, padding: 20 },
  title: { fontSize: 22, fontWeight: '800', color: colors.text, marginBottom: 16, marginTop: 4 },
  emptyState: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 30, marginTop: -40 },
  emptyIcon: { color: colors.textMuted },
  emptyTitle: { fontSize: 16, fontWeight: '700', color: colors.text, marginTop: 14 },
  emptySubtitle: { fontSize: 13, color: colors.textMuted, marginTop: 6, textAlign: 'center', lineHeight: 19 },
});
