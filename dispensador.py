"""
Lógica de dispensado: coordina motor + sensor + timeout.
"""

from time import sleep, time

from config import (
    MOTOR_1_PIN,
    MOTOR_2_PIN,
    TIMEOUT_DISPENSADO_S,
    INTERVALO_LECTURA_S,
)
from motor import iniciar_giro, detener
from sensor import (
    calibrar_base,
    iniciar_monitoreo,
    detener_monitoreo,
    producto_detectado,
)

ENTREGADO = "ENTREGADO"
SIN_STOCK = "SIN_STOCK"
ERROR_MOTOR = "ERROR_MOTOR"


def dispensar(motor_pin, nombre_producto="Producto"):
    """
    Ciclo completo de dispensado.
    1. Calibra la distancia base (caja vacía)
    2. Inicia monitoreo continuo del sensor en hilo separado
    3. Enciende el motor
    4. Espera detección o timeout
    """
    print(f"  [{nombre_producto}] Iniciando dispensado...")

    calibrar_base()
    iniciar_monitoreo()

    if not iniciar_giro(motor_pin):
        print(f"  [{nombre_producto}] Motor no respondio!")
        detener_monitoreo()
        return ERROR_MOTOR

    inicio = time()

    try:
        while (time() - inicio) < TIMEOUT_DISPENSADO_S:
            if producto_detectado():
                elapsed = time() - inicio
                print(f"  [{nombre_producto}] Producto detectado! ({elapsed:.1f}s)")
                detener(motor_pin)
                detener_monitoreo()
                return ENTREGADO
            sleep(INTERVALO_LECTURA_S)

        elapsed = time() - inicio
        print(f"  [{nombre_producto}] Timeout {elapsed:.1f}s — sin stock.")
        detener(motor_pin)
        detener_monitoreo()
        return SIN_STOCK

    except Exception as e:
        print(f"  [{nombre_producto}] Error inesperado: {e}")
        detener(motor_pin)
        detener_monitoreo()
        return SIN_STOCK
