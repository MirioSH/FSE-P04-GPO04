"""
MAQUINA EXPENDEDORA — Script Principal (Raspberry Pi 5)
Controla 2 productos con botones, servomotores de rotación continua
y un sensor de distancia compartido.
"""

import warnings
warnings.filterwarnings("ignore", message=".*PWMSoftwareFallback.*")
warnings.filterwarnings("ignore", message=".*DistanceSensorNoEcho.*")

from gpiozero import Button
from time import sleep

from config import (
    BOTON_1_PIN, MOTOR_1_PIN,
    BOTON_2_PIN, MOTOR_2_PIN,
    SENSOR_TRIGGER_PIN, SENSOR_ECHO_PIN,
    DEBOUNCE_S,
)
from motor import detener_todos, cleanup
from sensor import obtener_sensor, cleanup_sensor
from dispensador import dispensar, ENTREGADO, ERROR_MOTOR

PRODUCTOS = [
    {"nombre": "Producto 1", "boton_pin": BOTON_1_PIN, "motor_pin": MOTOR_1_PIN},
    {"nombre": "Producto 2", "boton_pin": BOTON_2_PIN, "motor_pin": MOTOR_2_PIN},
]


def main():
    """Bucle principal de la maquina expendedora."""

    botones = []
    for prod in PRODUCTOS:
        boton = Button(prod["boton_pin"], bounce_time=DEBOUNCE_S)
        botones.append(boton)
        prod["boton"] = boton

    try:
        obtener_sensor()
        sensor_ok = True
    except Exception as e:
        print(f"[AVISO] Sensor no disponible: {e}")
        sensor_ok = False

    detener_todos()

    print()
    print("=" * 50)
    print("   MAQUINA EXPENDEDORA — SISTEMA ACTIVO")
    print("=" * 50)
    for prod in PRODUCTOS:
        print(f"   {prod['nombre']}:")
        print(f"     Boton → GPIO {prod['boton_pin']}")
        print(f"     Motor → GPIO {prod['motor_pin']}")
    print(f"   Sensor compartido:")
    print(f"     Trigger → GPIO {SENSOR_TRIGGER_PIN}")
    print(f"     Echo    → GPIO {SENSOR_ECHO_PIN}")
    if not sensor_ok:
        print("   *** SENSOR NO DISPONIBLE ***")
    print("=" * 50)
    print("   Presiona un boton para dispensar.")
    print("   Ctrl+C para apagar.\n")

    dispensando = False

    try:
        while True:
            for prod in PRODUCTOS:
                if not dispensando and prod["boton"].is_pressed:
                    dispensando = True

                    print(f">> Boton presionado: {prod['nombre']}")
                    print("-" * 40)

                    resultado = dispensar(prod["motor_pin"], prod["nombre"])

                    if resultado == ENTREGADO:
                        print(f">> {prod['nombre']}: Entrega exitosa!")
                    elif resultado == ERROR_MOTOR:
                        print(f">> {prod['nombre']}: ERROR en motor!")
                    else:
                        print(f">> {prod['nombre']}: Sin stock")

                    print("-" * 40)

                    prod["boton"].wait_for_release(timeout=3)

                    sleep(DEBOUNCE_S)
                    dispensando = False
                    print("Esperando boton...\n")

            sleep(0.01)

    except KeyboardInterrupt:
        print("\n\n>> Apagando sistema...")
    finally:
        detener_todos()
        cleanup()
        cleanup_sensor()
        for prod in PRODUCTOS:
            try:
                prod["boton"].close()
            except Exception:
                pass
        print(">> Sistema apagado. GPIO limpio.")


if __name__ == "__main__":
    main()
