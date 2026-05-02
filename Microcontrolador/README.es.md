# Control de Servomotores con ESP32

## 📌 Descripción

Este módulo implementa el control de servomotores para un sistema animatrónico utilizando una **ESP32**, integrando tanto control directo por pines como mediante un controlador PWM (**PCA9685**).

El sistema recibe comandos de emociones a través de comunicación serial y ejecuta movimientos específicos en los servos para representar expresiones faciales o gestos del robot.

---

## ⚙️ Hardware requerido

* ESP32
* Módulo PCA9685 (driver PWM I2C)
* Servomotores (hasta 16 con PCA9685 + servos directos)
* Fuente de alimentación externa para servos
* Conexión I2C (SDA / SCL)

---

## 📦 Librerías necesarias

Instalar las siguientes librerías en Arduino IDE o PlatformIO:

* `Adafruit PWM Servo Driver`
* `ESP32Servo`
* `Wire` (incluida por defecto)

---

## 🔌 Configuración

### Dirección I2C del PCA9685:

```cpp
Adafruit_PWMServoDriver servos = Adafruit_PWMServoDriver(0x41);
```

### Rango de PWM para servos:

```cpp
int pos0 = 172;
int pos180 = 565;
```

Estos valores deben calibrarse dependiendo del servo.

---

## 🚀 Funcionamiento

1. La ESP32 inicia comunicación serial a **115200 baudios**
2. Espera recibir una emoción en formato texto:

   * `"happy"`
   * `"sad"`
   * `"angry"`
   * `"surprise"`
3. Ejecuta la función correspondiente de movimiento
4. Evita repetir la misma emoción consecutivamente

---

## 🔁 Comunicación Serial

Formato esperado:

```
happy
sad
angry
surprise
```

Cada emoción debe enviarse como string terminado en salto de línea (`\n`).

---

## 🧠 Lógica del sistema

* Se almacena la última emoción ejecutada (`ultimaEmocion`)
* Solo se ejecuta una nueva animación si la emoción cambia
* Se aplica un delay de 3 segundos antes de ejecutar la animación
* Se combinan dos tipos de control:

  * PCA9685 (I2C)
  * PWM directo con ESP32

---

## ⚠️ Notas importantes

* No alimentar los servos directamente desde la ESP32
* Verificar correcta conexión I2C
* Ajustar los valores `pos0` y `pos180` para evitar daños
* Completar funciones de emociones faltantes

---

## 🧪 Debug

El sistema imprime en el monitor serial:

* Emoción recibida
* Cambios de estado
* Ejecución de animaciones

---

