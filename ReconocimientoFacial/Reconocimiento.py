import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(0)
emociones_permitidas = ["angry", "sad", "happy", "surprise"]
porcentaje_minimo = 10  # mínimo % para considerar una emoción detectada

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion_scores = result[0]['emotion']

        # Filtrar solo emociones permitidas
        emociones_filtradas = {k: v for k, v in emotion_scores.items() if k in emociones_permitidas}

        # Tomar la emoción con mayor porcentaje
        if emociones_filtradas:
            emotion = max(emociones_filtradas, key=lambda k: emociones_filtradas[k])
            if emociones_filtradas[emotion] < porcentaje_minimo:
                emotion = "neutral"  # Zona neutra si ningún porcentaje supera el mínimo
        else:
            emotion = "neutral"

        text = f"Emocion: {emotion} ({emociones_filtradas.get(emotion, 0):.1f}%)" \
               if emotion != "neutral" else "Emocion: neutral"

        cv2.putText(frame, text, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    except Exception as e:
        cv2.putText(frame, "Error en deteccion", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Deteccion de Emociones", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
