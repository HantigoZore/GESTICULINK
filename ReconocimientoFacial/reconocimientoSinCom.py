import cv2
from deepface import DeepFace

DETECTOR = "retinaface"  # cambia a "mtcnn" o "opencv" si falla
ACTIONS = ["emotion"]

def draw_label(img, text, x, y):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    th = 2
    tsize = cv2.getTextSize(text, font, scale, th)[0]
    cv2.rectangle(img, (x, y - tsize[1] - 8), (x + tsize[0] + 8, y), (0, 0, 0), -1)
    cv2.putText(img, text, (x + 4, y - 6), font, scale, (255, 255, 255), th, cv2.LINE_AA)

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return

    print("✅ Cámara abierta. Presiona 'q' para salir.", flush=True)

    while True:
        ok, frame = cap.read()
        if not ok:
            print("❌ No pude leer frame de la cámara.", flush=True)
            break

        try:
            # quitamos el parámetro 'prog_bar' que tu versión no acepta
            results = DeepFace.analyze(
                img_path=frame,
                actions=ACTIONS,
                detector_backend=DETECTOR,
                enforce_detection=False
            )
        except Exception as e:
            print(f"⚠️ Error en DeepFace.analyze: {e}", flush=True)
            results = []

        # A veces devuelve dict, a veces lista
        if isinstance(results, dict):
            results = [results]

        if not results:
            draw_label(frame, "Sin rostro", 20, 40)
            print("👀 Sin rostro detectado.", flush=True)
        else:
            for r in results:
                region = r.get("region") or {}
                x, y, w, h = region.get("x", 0), region.get("y", 0), region.get("w", 0), region.get("h", 0)
                emo = r.get("emotion") or {}
                if emo:
                    key = max(emo, key=lambda k: emo[k])
                    score = emo[key]
                    print(f"🙂 Emoción detectada: {key} ({score:.1f}%)", flush=True)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    draw_label(frame, f"{key} ({score:.1f}%)", x, y)
                else:
                    draw_label(frame, "Rostro sin emoción", 20, 40)
                    print("👤 Rostro sin emoción detectada.", flush=True)

        cv2.imshow("Emociones (DeepFace)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
