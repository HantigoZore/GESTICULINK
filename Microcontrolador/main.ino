#include <Adafruit_PWMServoDriver.h>
#include <Wire.h>
#include <ESP32Servo.h>

Adafruit_PWMServoDriver servos = Adafruit_PWMServoDriver(0x41);

int pos0 = 172;
int pos180 = 565;

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;

int servoPin1 = 14;
int servoPin2 = 26;
int servoPin3 = 27;
int servoPin4 = 32;
int servoPin5 = 33;
int servoPin6 = 25;

void setServo(uint8_t n_Servo, int angulo) {
  int ciclo = map(angulo, 0, 180, pos0, pos180);
  servos.setPWM(n_Servo, 0, ciclo);
}

void setup() {
  Serial.begin(115200);
  servos.begin();
  servos.setPWMFreq(60);
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo3.attach(servoPin3);
  servo4.attach(servoPin4);
  servo5.attach(servoPin5);
  servo6.attach(servoPin6);
  Serial.println("ESP32 lista para recibir emociones");
}

// ----- FUNCIONES DE EMOCIONES -----
void feliz() {
  Serial.println("Ejecutando emoción: feliz");
  servo3.write(180); delay(15);
  servo2.write(0); delay(15);
  setServo(1,0); delay(15);
  setServo(3,0); delay(15);
  setServo(2,180); delay(15);
  servo4.write(180); delay(15);
  setServo(10,20); delay(15);
  setServo(6,60); delay(15);
  setServo(9,0); delay(15);
  setServo(8,90); delay(15);
  setServo(7,90); delay(15);
  setServo(11,120); delay(15);
  setServo(15,60); delay(15);
  setServo(13,60); delay(15);
}

void triste() {
  Serial.println("Ejecutando emoción: triste");
  // Define tus movimientos de servos aquí
}

void enojado() {
  Serial.println("Ejecutando emoción: enojado");
  // Define tus movimientos de servos aquí
}

void sorprendido() {
  Serial.println("Ejecutando emoción: sorprendido");
  // Define tus movimientos de servos aquí
}

// ----- VARIABLES GLOBALES -----
String ultimaEmocion = "";  // Guarda la última emoción ejecutada

// ----- LOOP PRINCIPAL -----
void loop() {
  if (Serial.available()) {
    String emocion = Serial.readStringUntil('\n');
    emocion.trim();

    // Ejecuta la función solo si cambió la emoción
    if (emocion != ultimaEmocion) {
      Serial.println("Cambio de emoción detectado: " + emocion);
      delay(3000); // Espera 3 segundos antes de ejecutar
      if (emocion == "happy") feliz();
      else if (emocion == "sad") triste();
      else if (emocion == "angry") enojado();
      else if (emocion == "surprise") sorprendido();
      else Serial.println("Emoción desconocida recibida: " + emocion);

      ultimaEmocion = emocion; // Actualiza la última emoción
    }
  }
}
