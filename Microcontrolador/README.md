# Servo Control with ESP32

## 📌 Description

This module implements servo motor control for an animatronic system using an **ESP32**, integrating both direct pin control and an external PWM controller (**PCA9685**).

The system receives emotion commands via serial communication and executes specific servo movements to represent facial expressions or gestures.

---

## ⚙️ Hardware Requirements

* ESP32
* PCA9685 PWM driver (I2C)
* Servo motors (up to 16 via PCA9685 + direct servos)
* External power supply for servos
* I2C connection (SDA / SCL)

---

## 📦 Required Libraries

Install the following libraries in Arduino IDE or PlatformIO:

* `Adafruit PWM Servo Driver`
* `ESP32Servo`
* `Wire` (built-in)

---

## 🔌 Configuration

### PCA9685 I2C Address:

```cpp
Adafruit_PWMServoDriver servos = Adafruit_PWMServoDriver(0x41);
```

### Servo PWM range:

```cpp
int pos0 = 172;
int pos180 = 565;
```

These values must be calibrated depending on your servos.

---

## 🚀 Operation

1. ESP32 initializes serial communication at **115200 baud**
2. Waits for an emotion string:

   * `"happy"`
   * `"sad"`
   * `"angry"`
   * `"surprise"`
3. Executes the corresponding movement function
4. Prevents repeating the same emotion consecutively

---

## 🔁 Serial Communication

Expected format:

```
happy
sad
angry
surprise
```

Each emotion must be sent as a string ending with a newline (`\n`).

---

## 🧠 System Logic

* Stores the last executed emotion (`ultimaEmocion`)
* Executes a new animation only if the emotion changes
* Applies a 3-second delay before execution
* Uses two control methods:

  * PCA9685 (I2C)
  * Direct ESP32 PWM

---

## ⚠️ Important Notes

* Do NOT power servos directly from the ESP32
* Verify proper I2C connections
* Calibrate `pos0` and `pos180` values to avoid damage
* Complete missing emotion functions

---

## 🧪 Debug

The system outputs via serial monitor:

* Received emotion
* State changes
* Animation execution

---

