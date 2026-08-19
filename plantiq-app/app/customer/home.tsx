import { View, Text, FlatList, Button } from 'react-native';
import { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';

type Listing = {
  coffee_type: string;
  price: number;
  latitude: number;
  longitude: number;
};

export default function CustomerHome() {
  const [data, setData] = useState<Listing[]>([]);
  const router = useRouter();

  useEffect(() => {
    fetch('http://192.168.137.235:5000/market/listings')
      .then(res => res.json())
      .then(setData)
      .catch(err => console.log(err));
  }, []);

  return (
    <View style={{ flex: 1, padding: 10 }}>
      <FlatList
        data={data}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => (
          <View
            style={{
              padding: 15,
              marginVertical: 8,
              borderWidth: 1,
              borderRadius: 10
            }}
          >
            <Text style={{ fontSize: 18 }}>
              {item.coffee_type}
            </Text>

            <Text>₹ {item.price}</Text>

            <Button
              title="View Farmer Location"
              onPress={() =>
                router.push(
                  `/customer/map?lat=${item.latitude}&lng=${item.longitude}`
                )
              }
            />
          </View>
        )}
      />
    </View>
  );
}