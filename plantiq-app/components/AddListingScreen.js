import { View, Text, TextInput, Button } from "react-native";
import { useState } from "react";
import axios from "axios";
import { useRouter } from "expo-router";
<<<<<<< HEAD
import { BASE_URL } from "../constants/api";
=======
>>>>>>> d6b66db (first commit)

export default function AddListingScreen() {

  const router = useRouter();

  const [form, setForm] = useState({
    farmer_id: 1,
    coffee_type: "",
    processing_type: "",
    quantity: "",
    price: "",
    latitude: "",
    longitude: ""
  });

  const handleSubmit = async () => {
    try {

      const formattedData = {
        farmer_id: 1,
        coffee_type: form.coffee_type,
        processing_type: form.processing_type,
        quantity: parseInt(form.quantity),
        price: parseInt(form.price),
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude)
      };

      console.log("SENDING:", formattedData);

      await axios.post(
<<<<<<< HEAD
        `${BASE_URL}/market/add`,
=======
        "http://192.168.1.3:5000/market/add",
>>>>>>> d6b66db (first commit)
        formattedData,
        {
          headers: {
            "Content-Type": "application/json"
          }
        }
      );

      alert("Listing Added!");

    } catch (err) {
      console.log("ERROR:", err.response?.data || err.message);
    }
  };

  return (
    <View style={{ flex: 1, padding: 20, backgroundColor: "white" }}>

      <Text style={{ fontSize: 20, marginBottom: 10 }}>
        Add Coffee Listing
      </Text>

      {/* Inputs */}
      <TextInput
        placeholder="Coffee Type"
        onChangeText={(val) => setForm({ ...form, coffee_type: val })}
        style={{ borderWidth: 1, marginVertical: 5, padding: 8 }}
      />

      <TextInput
        placeholder="Processing Type"
        onChangeText={(val) => setForm({ ...form, processing_type: val })}
        style={{ borderWidth: 1, marginVertical: 5, padding: 8 }}
      />

      <TextInput
        placeholder="Quantity"
        keyboardType="numeric"
        onChangeText={(val) => setForm({ ...form, quantity: val })}
        style={{ borderWidth: 1, marginVertical: 5, padding: 8 }}
      />

      <TextInput
        placeholder="Price"
        keyboardType="numeric"
        onChangeText={(val) => setForm({ ...form, price: val })}
        style={{ borderWidth: 1, marginVertical: 5, padding: 8 }}
      />

      <TextInput
        placeholder="Latitude (e.g. 12.9716)"
        keyboardType="numeric"
        onChangeText={(val) => setForm({ ...form, latitude: val })}
        style={{ borderWidth: 1, marginVertical: 5, padding: 8 }}
      />

      <TextInput
        placeholder="Longitude (e.g. 77.5946)"
        keyboardType="numeric"
        onChangeText={(val) => setForm({ ...form, longitude: val })}
        style={{ borderWidth: 1, marginVertical: 5, padding: 8 }}
      />

      <Button title="Submit" onPress={handleSubmit} />

      {/* ✅ TEST MAP BUTTON (AFTER ENTERING LAT/LONG) */}
      <View style={{ marginTop: 20 }}>
        <Button
          title="Preview Location on Map"
          onPress={() =>
            router.push({
              pathname: "/map",
              params: {
                latitude: form.latitude,
                longitude: form.longitude
              }
            })
          }
        />
      </View>

    </View>
  );
}