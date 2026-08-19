import { View, Text, FlatList, Button } from "react-native";
import { useEffect, useState } from "react";
import axios from "axios";
import { useRouter } from "expo-router";
<<<<<<< HEAD
import { BASE_URL } from "../constants/api";
=======
>>>>>>> d6b66db (first commit)

export default function MarketScreen() {

  const router = useRouter();   // ✅ FIX: inside component

  const [listings, setListings] = useState([]);

  useEffect(() => {
<<<<<<< HEAD
    axios.get(`${BASE_URL}/market/listings`)
=======
    axios.get("http://192.168.1.3:5000/market/listings")
>>>>>>> d6b66db (first commit)
      .then(res => {
        console.log(res.data);
        setListings(res.data);
      })
      .catch(err => console.log(err));
  }, []);

  return (
    <View style={{ flex: 1, padding: 20, backgroundColor: "white" }}>

      {/* 🔥 ADD BUTTON HERE */}
      <Button title="View Map" onPress={() => router.push("/map")} />

      <Text style={{ fontSize: 22, fontWeight: "bold", marginVertical: 10 }}>
        Coffee Listings
      </Text>

      <FlatList
        data={listings}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={{
            marginVertical: 10,
            padding: 12,
            borderWidth: 1,
            borderRadius: 8,
            backgroundColor: "#f9f9f9"
          }}>
            <Text>Type: {item.coffee_type}</Text>
            <Text>Processing: {item.processing_type}</Text>
            <Text>Quantity: {item.quantity} kg</Text>
            <Text>Price: ₹{item.price}</Text>
          </View>
        )}
      />

    </View>
  );
}