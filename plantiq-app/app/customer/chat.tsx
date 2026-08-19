import { View, TextInput, Button, Text } from 'react-native';
import { useState } from 'react';

export default function Chat() {
  const [msg, setMsg] = useState('');
  const [reply, setReply] = useState('');

  const send = async () => {
    const res = await fetch('http://YOUR_RAG_API/chat', {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({ query: msg })
    });

    const data = await res.json();
    setReply(data.answer);
  };

  return (
    <View style={{ padding:20 }}>
      <TextInput placeholder="Ask something..."
        onChangeText={setMsg} />

      <Button title="Send" onPress={send} />

      <Text>Reply: {reply}</Text>
    </View>
  );
}