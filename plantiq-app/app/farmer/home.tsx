import { View, Button, Text } from 'react-native';
import { useRouter } from 'expo-router';

export default function FarmerHome() {
  const router = useRouter();

  return (
    <View style={{ padding:20 }}>
      <Text>Farmer Dashboard</Text>

      <Button title="Add Product" onPress={() => router.push('/farmer/add')} />
      <Button title="Chatbot" onPress={() => router.push('/farmer/chat')} />
    </View>
  );
}