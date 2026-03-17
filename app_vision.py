import cv2
import mediapipe as mp
import serial
import time
import sys

# --- CONFIGURACIÓN DE PARÁMETROS ---
PUERTO_SERIAL = 'COM4'  # Ajustar según Administrador de Dispositivos
BAUD_RATE = 9600
UMBRAL_CONFIANZA = 0.7

def iniciar_sistema():
    # Inicializar comunicación con Arduino
    try:
        arduino = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=1)
        time.sleep(2)  # Tiempo de gracia para reset de Arduino
        print(f"[INFO] Conectado a Arduino en {PUERTO_SERIAL}")
    except Exception as e:
        print(f"[WARN] No se detectó Arduino: {e}. Iniciando en modo simulación.")
        arduino = None

    # Inicializar MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=UMBRAL_CONFIANZA,
        min_tracking_confidence=0.5
    )

    # Iniciar Captura de Video (DirectShow para rapidez en Windows)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("[ERROR] No se pudo acceder a la cámara.")
        sys.exit()

    print("[INFO] Sistema listo. Presiona ESC para salir.")

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            # Pre-procesamiento: Espejo y conversión de color
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Procesar frame con MediaPipe
            results = hands.process(rgb_frame)
            
            # Estado por defecto: todos los dedos abajo ("0")
            estado_dedos = ["0"] * 5 

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Dibujar esqueleto en pantalla
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    p = hand_landmarks.landmark
                    
                    # LÓGICA DE DETECCIÓN (Comparación de puntos clave)
                    # 1. Pulgar: Compara coordenada X de la punta (4) con la base (3)
                    estado_dedos[0] = "1" if p[4].x < p[3].x else "0"
                    
                    # 2. Otros dedos (Índice a Meñique): Compara Y de puntas con bases
                    puntas = [8, 12, 16, 20]
                    bases = [6, 10, 14, 18]
                    
                    for i in range(4):
                        # En MediaPipe, el eje Y disminuye hacia arriba
                        estado_dedos[i+1] = "1" if p[puntas[i]].y < p[bases[i]].y else "0"

                    # Convertir lista a cadena (ej: "10110") y enviar
                    msg = "".join(estado_dedos)
                    if arduino:
                        arduino.write(msg.encode())
                    
                    # Feedback visual en ventana
                    cv2.putText(frame, f'DEDOS: {msg}', (20, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('Control Gestual - Pasantias Erwin', frame)

            if cv2.waitKey(1) & 0xFF == 27: # Tecla ESC
                break
    finally:
        # Limpieza de recursos
        print("[INFO] Cerrando sistema...")
        if arduino: arduino.close()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    iniciar_sistema()