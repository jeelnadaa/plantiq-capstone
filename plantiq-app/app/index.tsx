<<<<<<< HEAD
import { useEffect } from "react";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";
=======
import { View, Text, Button, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
>>>>>>> d6b66db (first commit)

export default function Index() {
  const router = useRouter();

<<<<<<< HEAD
  useEffect(() => {
    // Require a fresh login on every app launch — no persisted session across restarts.
    AsyncStorage.multiRemove(["token", "user"]).then(() => {
      router.replace("/login");
    });
  }, []);

  return null;
}
=======
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to PlantiQ</Text>
      <Text style={styles.subtitle}>Choose your role:</Text>

      <Button
        title="Customer"
        onPress={() => router.push('/customer/home')}
      />

      <Button
        title="Farmer"
        onPress={() => router.push('/farmer/home')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    marginBottom: 20,
  },
});
>>>>>>> d6b66db (first commit)
