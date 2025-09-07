#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

String emocion = "";

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32-EMOCION"); // Nombre Bluetooth
  Serial.println("Esperando datos por Bluetooth...");
}

void loop() {
  if (SerialBT.available()) {
    char c = SerialBT.read();
    if (c == '\n') {
      Serial.print("Emoción recibida: ");
      Serial.println(emocion);

      if (emocion == "happy") {
        Serial.println("¡La persona está feliz!");
      } else if (emocion == "sad") {
        Serial.println("La persona está triste.");
      } else if (emocion == "angry") {
        Serial.println("¡Cuidado! La persona está enojada.");
      } else if (emocion == "surprise") {
        Serial.println("¡Sorpresa detectada!");
      } else if (emocion == "neutral") {
        Serial.println("La persona está neutral.");
      } else {
        Serial.println("Emoción desconocida.");
      }

      emocion = "";
    } else {
      emocion += c;
    }
  }
}

