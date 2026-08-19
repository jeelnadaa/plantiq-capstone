import React, { useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, Alert, ActivityIndicator, KeyboardAvoidingView,
  Platform, ScrollView
} from "react-native";
import axios from "axios";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { shadow } from "../constants/palette";
import { useTheme, useThemedStyles } from "../context/ThemeContext";
import { useLanguage } from "../context/LanguageContext";
import { BASE_URL } from "../constants/api";

export default function LoginScreen() {
  const router = useRouter();
  const styles = useThemedStyles(makeStyles);
  const { colors } = useTheme();
  const { language, toggleLanguage, t } = useLanguage();

  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    phone: "",
    role: "farmer"
  });

  const handleSubmit = async () => {
    if (!form.email || !form.password) {
      Alert.alert("Error", "Email and password are required.");
      return;
    }
    if (isRegister && !form.name) {
      Alert.alert("Error", "Name is required.");
      return;
    }

    setLoading(true);
    try {
      const endpoint = isRegister ? "/auth/register" : "/auth/login";
      const payload = isRegister
        ? { name: form.name, email: form.email, password: form.password, role: form.role, phone: form.phone }
        : { email: form.email, password: form.password };

      const res = await axios.post(`${BASE_URL}${endpoint}`, payload);
      const { token, user } = res.data;

      await AsyncStorage.setItem("token", token);
      await AsyncStorage.setItem("user", JSON.stringify(user));

      router.replace("/scanner");

    } catch (err) {
      console.log("FULL ERROR:", JSON.stringify(err.response?.data));
      console.log("STATUS:", err.response?.status);
      const msg = err.response?.data?.error || err.message;
      Alert.alert("Error", msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.flex} edges={["top"]}>
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <TouchableOpacity onPress={toggleLanguage} style={styles.langBtn} activeOpacity={0.8}>
          <Ionicons name="globe-outline" size={16} color={colors.text} />
          <Text style={styles.langBtnText}>{language === "kn" ? "ಕನ್ನಡ" : "EN"}</Text>
        </TouchableOpacity>

        <Text style={styles.logo}>🌱</Text>
        <Text style={styles.title}>{t.common.brand}</Text>
        <Text style={styles.subtitle}>{isRegister ? t.login.createAccount : t.login.welcomeBack}</Text>

        <View style={styles.card}>
          {isRegister && (
            <View style={styles.roleRow}>
              <TouchableOpacity
                style={[styles.roleBtn, form.role === "farmer" && styles.roleActive]}
                onPress={() => setForm({ ...form, role: "farmer" })}
              >
                <Text style={[styles.roleText, form.role === "farmer" && styles.roleTextActive]}>
                  {t.login.farmer}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.roleBtn, form.role === "customer" && styles.roleActive]}
                onPress={() => setForm({ ...form, role: "customer" })}
              >
                <Text style={[styles.roleText, form.role === "customer" && styles.roleTextActive]}>
                  {t.login.customer}
                </Text>
              </TouchableOpacity>
            </View>
          )}

          {isRegister && (
            <TextInput
              placeholder={t.login.fullName}
              placeholderTextColor={styles.placeholderColor.color}
              style={styles.input}
              onChangeText={(val) => setForm({ ...form, name: val })}
              value={form.name}
            />
          )}

          <TextInput
            placeholder={t.login.email}
            placeholderTextColor={styles.placeholderColor.color}
            style={styles.input}
            keyboardType="email-address"
            autoCapitalize="none"
            onChangeText={(val) => setForm({ ...form, email: val })}
            value={form.email}
          />

          <TextInput
            placeholder={t.login.password}
            placeholderTextColor={styles.placeholderColor.color}
            style={styles.input}
            secureTextEntry
            onChangeText={(val) => setForm({ ...form, password: val })}
            value={form.password}
          />

          {isRegister && (
            <TextInput
              placeholder={t.login.phone}
              placeholderTextColor={styles.placeholderColor.color}
              style={styles.input}
              keyboardType="phone-pad"
              onChangeText={(val) => setForm({ ...form, phone: val })}
              value={form.phone}
            />
          )}

          <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit} disabled={loading} activeOpacity={0.85}>
            {loading
              ? <ActivityIndicator color="#fff" />
              : <Text style={styles.submitText}>{isRegister ? t.login.register : t.login.login}</Text>
            }
          </TouchableOpacity>

          <TouchableOpacity onPress={() => setIsRegister(!isRegister)}>
            <Text style={styles.toggleText}>
              {isRegister ? t.login.toggleToLogin : t.login.toggleToRegister}
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const makeStyles = (colors) => StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  container: { flexGrow: 1, padding: 24, justifyContent: "center" },
  logo: { fontSize: 44, textAlign: "center", marginBottom: 4 },
  title: { fontSize: 30, fontWeight: "800", color: colors.primary, textAlign: "center" },
  subtitle: { fontSize: 15, color: colors.textMuted, textAlign: "center", marginTop: 4, marginBottom: 24 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 18,
    padding: 20,
    ...shadow,
  },
  roleRow: { flexDirection: "row", marginBottom: 16, gap: 12 },
  roleBtn: {
    flex: 1, padding: 12, borderWidth: 1.5, borderColor: colors.border,
    borderRadius: 12, alignItems: "center", backgroundColor: colors.surface
  },
  roleActive: { borderColor: colors.primary, backgroundColor: colors.accent },
  roleText: { fontSize: 15, color: colors.textMuted, fontWeight: "600" },
  roleTextActive: { color: colors.primary },
  input: {
    borderWidth: 1.5, borderColor: colors.border, borderRadius: 12,
    paddingHorizontal: 14, paddingVertical: 12, marginVertical: 6,
    backgroundColor: colors.surface, fontSize: 15, color: colors.text
  },
  submitBtn: {
    backgroundColor: colors.primary, paddingVertical: 15, borderRadius: 12,
    alignItems: "center", marginTop: 14
  },
  submitText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  toggleText: { marginTop: 18, textAlign: "center", color: colors.primary, fontSize: 14, fontWeight: "600" },
  placeholderColor: { color: colors.placeholder },
  langBtn: {
    flexDirection: "row", alignItems: "center", gap: 5,
    alignSelf: "center",
    height: 32, paddingHorizontal: 10, borderRadius: 16,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 10,
  },
  langBtnText: { fontSize: 12, fontWeight: "700", color: colors.text },
});
