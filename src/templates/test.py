import cv2

def test_camera():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    print("Cámara abierta correctamente")
    print(f"Propiedades de la cámara: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}, FPS: {cap.get(cv2.CAP_PROP_FPS)}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar el frame")
            break

        cv2.imshow("Prueba de Cámara", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # Presiona ESC para salir
            break

    cap.release()
    cv2.destroyAllWindows()

test_camera()
