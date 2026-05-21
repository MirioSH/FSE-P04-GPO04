"""
Lectura del sensor de distancia HC-SR04 via gpiozero.
Monitoreo continuo ultra-sensible con debug.
"""

import warnings
warnings.filterwarnings("ignore", message=".*PWMSoftwareFallback.*")
warnings.filterwarnings("ignore", message=".*DistanceSensorNoEcho.*")

from gpiozero import DistanceSensor
from time import sleep
from threading import Thread, Event

from config import SENSOR_TRIGGER_PIN, SENSOR_ECHO_PIN

_sensor = None
_distancia_base = None
_deteccion_flag = Event()
_hilo_activo = Event()
_hilo = None

# Ultra-sensible: cualquier cambio de 0.5 cm dispara detección
CAMBIO_MINIMO_CM = 0.5

# Un solo error de lectura = detección
ERRORES_PARA_DETECCION = 1

# Mostrar lecturas en tiempo real para debug
DEBUG = True


def obtener_sensor():
    """Obtiene o crea la instancia del sensor de distancia."""
    global _sensor
    if _sensor is None:
        _sensor = DistanceSensor(
            echo=SENSOR_ECHO_PIN,
            trigger=SENSOR_TRIGGER_PIN,
            max_distance=2,
        )
    return _sensor


def medir_distancia_cm():
    """Mide la distancia en centímetros. Retorna -1 en caso de error."""
    try:
        sensor = obtener_sensor()
        distancia_m = sensor.distance
        return round(distancia_m * 100, 1)
    except Exception:
        return -1


def calibrar_base():
    """Mide la distancia base (sin producto)."""
    global _distancia_base
    lecturas = []
    for _ in range(8):
        d = medir_distancia_cm()
        if d > 0:
            lecturas.append(d)
        sleep(0.02)

    if len(lecturas) >= 3:
        _distancia_base = sum(lecturas) / len(lecturas)
        print(f"  [SENSOR] Base: {_distancia_base:.1f} cm")
    else:
        _distancia_base = None
        print("  [SENSOR] No se pudo calibrar")


def _monitoreo_continuo():
    """Hilo que lee el sensor sin parar con máxima sensibilidad."""
    contador = 0

    while _hilo_activo.is_set():
        d = medir_distancia_cm()
        contador += 1

        # Debug: mostrar cada lectura
        if DEBUG and contador % 3 == 0:
            if d < 0:
                print(f"    sensor: ERROR")
            elif _distancia_base:
                diff = _distancia_base - d
                print(f"    sensor: {d:.1f} cm (diff: {diff:+.1f})")

        # Criterio 1: error de eco = algo interrumpió la señal
        if d < 0:
            if DEBUG:
                print(f"    >>> DETECCION: error de eco")
            _deteccion_flag.set()
            return

        # Criterio 2: cualquier cambio respecto a la base
        if _distancia_base is not None:
            diferencia = abs(_distancia_base - d)
            if diferencia >= CAMBIO_MINIMO_CM:
                if DEBUG:
                    print(f"    >>> DETECCION: cambio de {diferencia:.1f} cm (base={_distancia_base:.1f}, actual={d:.1f})")
                _deteccion_flag.set()
                return


def iniciar_monitoreo():
    """Inicia el hilo de monitoreo continuo del sensor."""
    global _hilo
    _deteccion_flag.clear()
    _hilo_activo.set()
    _hilo = Thread(target=_monitoreo_continuo, daemon=True)
    _hilo.start()


def detener_monitoreo():
    """Detiene el hilo de monitoreo."""
    global _hilo
    _hilo_activo.clear()
    if _hilo is not None:
        _hilo.join(timeout=1)
        _hilo = None


def producto_detectado():
    """Retorna True si el hilo de monitoreo detectó un objeto."""
    return _deteccion_flag.is_set()


def cleanup_sensor():
    """Libera recursos del sensor."""
    global _sensor, _distancia_base
    detener_monitoreo()
    if _sensor is not None:
        try:
            _sensor.close()
        except Exception:
            pass
        _sensor = None
    _distancia_base = None
