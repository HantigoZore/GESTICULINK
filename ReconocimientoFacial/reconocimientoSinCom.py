import cv2
import numpy as np
from deepface import DeepFace

# ---------------- Config ----------------
FAST_DETECTOR = "opencv"   # "mediapipe" (muy rápido), o "opencv" si no tienes mediapipe en DeepFace
EMO_BACKEND = "skip"          # analizamos el recorte de cara, sin re-detectar
ACTIONS = ["emotion"]

# Detectar cada N frames; entre medias reutilizamos la caja
DETECT_EVERY = 6

# Reducción para detectar (rápido) pero recorte sale del original (calidad)
DETECT_MAX_SIDE = 360

# Cuántos frames mantenemos la caja si no vuelve a detectar
TRACK_TTL = 12

# Suavizado exponencial de probabilidades
ALPHA = 0.6

# ---------------- Utils ----------------
def resize_keep_aspect(img, max_side):
    h, w = img.shape[:2]
    s = min(1.0, max_side / max(h, w))
    if s < 1.0:
        img_small = cv2.resize(img, (int(w*s), int(h*s)), interpolation=cv2.INTER_AREA)
    else:
        img_small = img
        s = 1.0
    return img_small, s

def ema(prev, cur, alpha=ALPHA):
    if prev is None: return cur.copy()
    out = {}
    for k, v in cur.items():
        out[k] = alpha * prev.get(k, 0.0) + (1 - alpha) * v
    return out

def best_label(scores):
    if not scores: return "unknown", 0.0
    k = max(scores, key=lambda x: scores[x])
    return k, scores[k]

def enhance_face(face):
    # denoise + sharpen ligero para mejorar definición sin subir costo
    face = cv2.fastNlMeansDenoisingColored(face, None, 3, 3, 7, 21)
    # sharpen kernel suave
    k = np.array([[0, -1, 0],
                  [-1, 5, -1],
                  [0, -1, 0]], dtype=np.float32)
    face = cv2.filter2D(face, -1, k)
    return face

def draw_label(img, text, x, y):
    font, scale, th = cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
    tsize = cv2.getTextSize(text, font, scale, th)[0]
    cv2.rectangle(img, (x, y - tsize[1] - 8), (x + tsize[0] + 8, y), (0, 0, 0), -1)
    cv2.putText(img, text, (x + 4, y - 6), font, scale, (255, 255, 255), th, cv2.LINE_AA)

# ---------------- Main ----------------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return

    # Bajar resolución/fps de la cámara para aliviar CPU (ajusta si quieres 720p)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("✅ Cámara abierta. Presiona 'q' para salir.")

    frame_idx = 0
    ttl = 0
    last_bbox = None        # (x,y,w,h) en coordenadas del frame original
    smooth_scores = None

    while True:
        ok, frame = cap.read()
        if not ok:
            print("❌ No pude leer frame.")
            break

        frame_idx += 1

        # ---- (A) cada N frames: detectar cara en baja resolución ----
        need_detect = (last_bbox is None) or (frame_idx % DETECT_EVERY == 0) or (ttl <= 0)
        if need_detect:
            small, scale = resize_keep_aspect(frame, DETECT_MAX_SIDE)
            try:
                # Usamos extract_faces (solo detectar) en imagen reducida para ir rápido
                faces = DeepFace.extract_faces(
                    img_path=small,
                    detector_backend=FAST_DETECTOR,
                    enforce_detection=False
                )
            except Exception as e:
                # si el detector falla, probamos opencv como fallback
                try:
                    faces = DeepFace.extract_faces(
                        img_path=small,
                        detector_backend="opencv",
                        enforce_detection=False
                    )
                except:
                    faces = []

            # Elegimos la cara más grande
            best = None
            best_area = 0
            for f in faces or []:
                reg = f.get("facial_area") or {}
                x, y, w, h = reg.get("x",0), reg.get("y",0), reg.get("w",0), reg.get("h",0)
                area = w*h
                if area > best_area:
                    best_area = area
                    best = (x, y, w, h)

            if best:
                # Escalamos bbox a frame original
                inv = 1.0/scale
                x, y, w, h = best
                x, y, w, h = int(x*inv), int(y*inv), int(w*inv), int(h*inv)
                # expandimos un poco para capturar cejas/mentón
                pad = int(0.12 * max(w, h))
                x = max(0, x - pad); y = max(0, y - pad)
                w = min(frame.shape[1]-x, w + 2*pad)
                h = min(frame.shape[0]-y, h + 2*pad)
                last_bbox = (x, y, w, h)
                ttl = TRACK_TTL
            else:
                last_bbox = None
                ttl = 0
                smooth_scores = None

        # ---- (B) si tenemos bbox, analizamos solo ese recorte (rápido y en buena calidad) ----
        label_txt = "Sin rostro"
        if last_bbox:
            x, y, w, h = last_bbox
            face = frame[y:y+h, x:x+w]
            if face.size > 0:
                # Mejora visual suave (opcional, quítalo si tu CPU va justa)
                face = enhance_face(face)

                try:
                    res = DeepFace.analyze(
                        img_path=face,            # ya es la cara
                        actions=ACTIONS,
                        detector_backend=EMO_BACKEND,  # "skip": no re-detectar
                        enforce_detection=False
                    )
                except Exception as e:
                    res = []

                if isinstance(res, dict):
                    res = [res]

                if res:
                    emo = res[0].get("emotion") or {}
                    # Nos quedamos con happy/sad/angry (o todas si quieres)
                    filtered = {k: float(v) for k, v in emo.items()}
                    smooth_scores = ema(smooth_scores, filtered)
                    k, val = best_label(smooth_scores or filtered)
                    label_txt = f"{k} ({val:.1f}%)"

                    # Dibujo y print
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    draw_label(frame, label_txt, x, y)
                    if frame_idx % 10 == 0:
                        print("🙂", label_txt)
                else:
                    label_txt = "Rostro sin emoción"
                    draw_label(frame, label_txt, x, y)
                    if frame_idx % 15 == 0:
                        print("👤 Rostro sin emoción")

                ttl -= 1
                if ttl <= 0:
                    # forzamos una nueva detección pronto
                    last_bbox = None
            else:
                last_bbox = None
                ttl = 0

        else:
            # mensaje visual cuando no hay rostro
            draw_label(frame, label_txt, 20, 40)
            if frame_idx % 15 == 0:
                print("👀 Sin rostro")

        cv2.imshow("Emociones (optimizado)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
