import cv2
from fer.fer import FER

import time

print("Inicializando FER...")

detector = FER(mtcnn=False)

print("FER listo")
print("Abriendo cámara...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    exit()

while True:

    ret, frame = cap.read()

    if not ret:
        break

    inicio = time.time()

    try:
        resultados = detector.detect_emotions(frame)

        emocion = "Sin rostro"
        confianza = 0

        if resultados:

            emociones = resultados[0]["emotions"]

            emocion = max(emociones, key=emociones.get)

            confianza = emociones[emocion] * 100

        tiempo_ms = (time.time() - inicio) * 1000

        texto1 = f"Emocion: {emocion}"
        texto2 = f"Confianza: {confianza:.1f}%"
        texto3 = f"Tiempo: {tiempo_ms:.0f} ms"

        cv2.putText(
            frame,
            texto1,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            texto2,
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            texto3,
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        print(
            f"\rEmocion: {emocion:<10} | "
            f"Confianza: {confianza:5.1f}% | "
            f"Tiempo: {tiempo_ms:5.0f} ms",
            end=""
        )

    except Exception as e:
        print("\nError:", e)

    cv2.imshow("GESTICULINK - Detector de Emociones", frame)

    tecla = cv2.waitKey(1)

    if tecla == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()