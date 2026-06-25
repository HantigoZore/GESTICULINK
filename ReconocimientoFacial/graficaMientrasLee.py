import cv2
from fer.fer import FER
import time
import collections
import threading

import matplotlib
matplotlib.use("TkAgg")  # Cambia a "Qt5Agg" si usas Qt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation

# ──────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────
VENTANA_SEGUNDOS = 10          # ventana visible en el eje X
MIN_SEGUNDOS     = 10          # mínimo mostrado al arrancar
FPS_ESTIMADO     = 10
MAX_PUNTOS       = VENTANA_SEGUNDOS * FPS_ESTIMADO

# Solo las 5 emociones de interés
EMOCIONES = ["angry", "sad", "neutral", "happy", "surprise"]

COLORES = {
    "angry":    "#e74c3c",   # rojo
    "sad":      "#3498db",   # azul
    "neutral":  "#95a5a6",   # gris
    "happy":    "#f1c40f",   # amarillo
    "surprise": "#e67e22",   # naranja
}

ETIQUETAS_ES = {
    "angry":    "Enojo",
    "sad":      "Triste",
    "neutral":  "Neutral",
    "happy":    "Feliz",
    "surprise": "Sorpresa",
}

# Emociones que FER puede devolver pero no graficamos → las mapeamos a neutral
MAPA_FALLBACK = {
    "disgust": "neutral",
    "fear":    "neutral",
}

EMOCION_IDX = {e: i for i, e in enumerate(EMOCIONES)}

# Historial compartido entre hilos
lock        = threading.Lock()
historial_t = collections.deque()
historial_e = collections.deque()
t_inicio    = time.time()

# ──────────────────────────────────────────────
# Gráfico — un solo panel
# ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor("white")
fig.suptitle("GESTICULINK · Emoción vs Tiempo", color="#222222",
             fontsize=14, fontweight="bold", y=0.98)

ax.set_facecolor("#fafafa")
ax.set_xlim(0, VENTANA_SEGUNDOS)
ax.set_ylim(-0.7, len(EMOCIONES) - 0.3)

ax.set_yticks(range(len(EMOCIONES)))
ax.set_yticklabels(
    [ETIQUETAS_ES[e] for e in EMOCIONES],
    color="#333333", fontsize=12, fontweight="bold"
)

ax.set_xlabel("Tiempo (s)", color="#444444", fontsize=10)
ax.tick_params(axis="x", colors="#444444")
ax.tick_params(axis="y", length=0)

for spine in ax.spines.values():
    spine.set_edgecolor("#dddddd")

# Bandas de color de fondo por emoción (muy sutiles)
for i, e in enumerate(EMOCIONES):
    ax.axhspan(i - 0.45, i + 0.45, color=COLORES[e], alpha=0.08, zorder=0)
    ax.axhline(i, color=COLORES[e], alpha=0.15, linewidth=1, linestyle="--", zorder=1)

linea, = ax.plot([], [], color="#444444", linewidth=1, alpha=0.7, zorder=2)
scatter = ax.scatter([], [], s=35, zorder=4)
punto_actual = ax.scatter([], [], s=110, zorder=5, edgecolors="#222222", linewidths=1.2)

# Leyenda
parches = [
    mpatches.Patch(color=COLORES[e], label=ETIQUETAS_ES[e])
    for e in EMOCIONES
]
ax.legend(
    handles=parches,
    loc="upper right",
    fontsize=9,
    ncol=5,
    framealpha=0.95,
    labelcolor="#333333",
    facecolor="white",
    edgecolor="#dddddd",
)

plt.tight_layout(rect=[0, 0, 1, 0.95])


def actualizar_grafico(_frame):
    with lock:
        if not historial_t:
            return linea, scatter, punto_actual

        ts = list(historial_t)
        idxs = list(historial_e)

    t_actual = ts[-1]
    t_min = max(0, t_actual - VENTANA_SEGUNDOS)

    # Mantener solo los puntos dentro de los últimos 10 segundos
    while historial_t and historial_t[0] < t_min:
        with lock:
            historial_t.popleft()
            historial_e.popleft()

    with lock:
        ts = list(historial_t)
        idxs = list(historial_e)

    if not ts:
        return linea, scatter, punto_actual

    x_max = max(ts[-1], MIN_SEGUNDOS)
    if x_max <= VENTANA_SEGUNDOS:
        ax.set_xlim(0, VENTANA_SEGUNDOS)
    else:
        ax.set_xlim(x_max - VENTANA_SEGUNDOS, x_max)

    colores_puntos = [COLORES[EMOCIONES[i]] for i in idxs]

    linea.set_data(ts, idxs)
    scatter.set_offsets(list(zip(ts, idxs)))
    scatter.set_color(colores_puntos)

    punto_actual.set_offsets([[ts[-1], idxs[-1]]])
    punto_actual.set_color(COLORES[EMOCIONES[idxs[-1]]])

    return linea, scatter, punto_actual


ani = FuncAnimation(fig, actualizar_grafico, interval=150, blit=False)

# ──────────────────────────────────────────────
# Hilo de captura
# ──────────────────────────────────────────────
def captura():
    print("Inicializando FER...")
    detector = FER(mtcnn=False)
    print("FER listo — Abriendo cámara...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        inicio = time.time()

        try:
            resultados = detector.detect_emotions(frame)

            emocion = "neutral"

            if resultados:
                emociones = resultados[0]["emotions"]
                raw       = max(emociones, key=emociones.get)
                # Si FER devuelve disgust/fear, lo tratamos como neutral
                emocion   = MAPA_FALLBACK.get(raw, raw)

                x, y, w, h = resultados[0]["box"]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (0, 255, 150), 2)

            t_rel = time.time() - t_inicio
            with lock:
                historial_t.append(t_rel)
                historial_e.append(EMOCION_IDX[emocion])

            tiempo_ms = (time.time() - inicio) * 1000
            etiqueta  = ETIQUETAS_ES[emocion]

            cv2.putText(frame, f"Emocion: {etiqueta}",
                        (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 100), 2)
            cv2.putText(frame, f"Tiempo: {tiempo_ms:.0f} ms",
                        (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 80), 2)

            print(f"\rEmocion: {etiqueta:<10} | Tiempo: {tiempo_ms:5.0f} ms", end="")

        except Exception as e:
            print("\nError:", e)

        cv2.imshow("GESTICULINK - Detector de Emociones", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    plt.close("all")


hilo = threading.Thread(target=captura, daemon=True)
hilo.start()

plt.show()