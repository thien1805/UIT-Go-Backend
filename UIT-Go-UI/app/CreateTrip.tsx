// app/index.tsx
import React, { useState } from "react";
import { View, Text, TextInput, Button, ScrollView, StyleSheet, SafeAreaView } from "react-native";

export default function Home() {
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [greeting, setGreeting] = useState("");


  const handlePress = () => {
    const ageNum =parseInt(age);
    const FutureAge=ageNum + 10;
    setGreeting(`Bạn sẽ  ${FutureAge} tuổi vào 10 năm sau !!`);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>React Native Mobile Playground</Text>

   

        <TextInput
          style={styles.input}
          placeholder="Nhập tuổi hiện tại của bạn"
          value={age}
          onChangeText={setAge}
          keyboardType="numeric"
        />

        <Button title="Chào tôi!" onPress={handlePress} />

        {greeting ? <Text style={styles.greeting}>{greeting}</Text> : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f0f4f7",
  },
  container: {
    flexGrow: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
    width: "100%",
    maxWidth: 400,        // Giới hạn chiều rộng kiểu mobile
    marginHorizontal: "auto",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    width: "100%",
    marginBottom: 15,
    borderRadius: 5,
  },
  greeting: {
    marginTop: 10,
    fontSize: 20,
    fontWeight: "500",
    color: "#e31cddff",
    textAlign: "center",
  },
});
