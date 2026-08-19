import { View, TextInput, Button, Text, TouchableOpacity, Image, Alert } from 'react-native';
import { useState } from 'react';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';

interface ImageAsset {
  uri: string;
  width: number;
  height: number;
  type?: string;
  fileName?: string;
}

export default function Chat() {
  const [msg, setMsg] = useState('');
  const [reply, setReply] = useState('');
  const [selectedImage, setSelectedImage] = useState<ImageAsset | null>(null);

  const pickImage = async () => {
    // Request permission
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permissionResult.granted === false) {
      Alert.alert('Permission required', 'Permission to access camera roll is required!');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0] as ImageAsset);
    }
  };

  const send = async () => {
    if (!msg.trim() && !selectedImage) {
      Alert.alert('Error', 'Please enter a message or select an image.');
      return;
    }

    const formData = new FormData();
    if (msg.trim()) {
      formData.append('query', msg);
    }
    if (selectedImage) {
      const localUri = selectedImage.uri;
      const filename = localUri.split('/').pop() || 'image.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : 'image/jpeg';

      formData.append('image', {
        uri: localUri,
        name: filename,
        type: type,
      } as any);
    }

    try {
      const response = await axios.post('http://YOUR_RAG_API/chat', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setReply(response.data.answer);
      setMsg('');
      setSelectedImage(null);
    } catch (error) {
      console.error('Send error:', error);
      Alert.alert('Error', 'Failed to send message. Please try again.');
    }
  };

  return (
    <View style={{ padding: 20, flex: 1 }}>
      <TextInput
        placeholder="Ask something..."
        value={msg}
        onChangeText={setMsg}
        style={{ borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 10 }}
      />

      <TouchableOpacity
        onPress={pickImage}
        style={{ backgroundColor: '#007AFF', padding: 10, borderRadius: 5, marginBottom: 10 }}
      >
        <Text style={{ color: 'white', textAlign: 'center' }}>
          {selectedImage ? 'Change Image' : 'Upload Image'}
        </Text>
      </TouchableOpacity>

      {selectedImage && (
        <Image
          source={{ uri: selectedImage.uri }}
          style={{ width: 200, height: 150, marginBottom: 10, alignSelf: 'center' }}
        />
      )}

      <Button title="Send" onPress={send} />

      <Text style={{ marginTop: 20 }}>Reply: {reply}</Text>
    </View>
  );
}