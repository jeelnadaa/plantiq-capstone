import { Stack } from "expo-router";
<<<<<<< HEAD
import { SafeAreaProvider } from "react-native-safe-area-context";
import { ThemeProvider } from "../context/ThemeContext";
import { LanguageProvider } from "../context/LanguageContext";

export default function Layout() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <LanguageProvider>
          <Stack screenOptions={{ headerShown: false }} />
        </LanguageProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
=======

export default function Layout() {
  return <Stack />;
>>>>>>> d6b66db (first commit)
}