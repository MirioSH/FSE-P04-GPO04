"""
Control de servomotor MG90S (rotación continua) — hardware PWM sysfs.
Usa hardware PWM del Pi 5 (sysfs) + pinctrl para forzar el modo del pin.
"""

import os
import subprocess
from time import sleep

from config import MOTOR_1_PIN, MOTOR_2_PIN

_PIN_A_CANAL = {
    MOTOR_1_PIN: 0,   # GPIO 12 → pwm0
    MOTOR_2_PIN: 1,   # GPIO 13 → pwm1
}

PWM_CHIP = "/sys/class/pwm/pwmchip0"

PERIODO_NS     = 20_000_000    # 20ms = 50Hz
PULSO_PARAR_NS = 1_500_000     # 1.5ms = motor parado
GIRO_NS        = 1_650_000     # 1.65ms = giro lento

_PINES_MOTOR = [MOTOR_1_PIN, MOTOR_2_PIN]


def _escribir(path, valor):
    """Escribe un valor a un archivo sysfs."""
    with open(path, "w") as f:
        f.write(str(valor))


def _pwm_path(canal):
    """Retorna la ruta del canal PWM."""
    return os.path.join(PWM_CHIP, f"pwm{canal}")


def _forzar_modo_pwm(pin):
    """Fuerza el pin GPIO a modo PWM usando pinctrl."""
    subprocess.run(
        ["pinctrl", "set", str(pin), "a0"],
        capture_output=True, timeout=2,
    )


def _exportar(canal):
    """Exporta un canal PWM si no existe."""
    pwm_dir = _pwm_path(canal)

    if not os.path.exists(pwm_dir):
        try:
            _escribir(os.path.join(PWM_CHIP, "export"), canal)
            sleep(0.3)
        except Exception as e:
            print(f"[ERROR MOTOR] No se pudo exportar PWM canal {canal}: {e}")
            return False

    if not os.path.exists(pwm_dir):
        print(f"[ERROR MOTOR] Canal PWM {canal} no disponible.")
        return False

    return True


def iniciar_giro(pin):
    """Inicia giro continuo 360°. Retorna True si se inició correctamente."""
    canal = _PIN_A_CANAL.get(pin)
    if canal is None:
        print(f"[ERROR MOTOR] Pin {pin} no tiene canal PWM.")
        return False

    if not _exportar(canal):
        return False

    pwm_dir = _pwm_path(canal)
    duty_path = os.path.join(pwm_dir, "duty_cycle")
    enable_path = os.path.join(pwm_dir, "enable")
    period_path = os.path.join(pwm_dir, "period")

    try:
        try:
            _escribir(enable_path, "0")
        except Exception:
            pass
        sleep(0.05)

        try:
            _escribir(duty_path, "0")
        except Exception:
            pass

        _escribir(period_path, str(PERIODO_NS))
        _escribir(duty_path, str(GIRO_NS))
        _escribir(enable_path, "1")
        _forzar_modo_pwm(pin)

        return True

    except Exception as e:
        print(f"[ERROR MOTOR] No se pudo iniciar giro GPIO {pin}: {e}")
        try:
            _escribir(enable_path, "0")
        except Exception:
            pass
        return False


def detener(pin):
    """Detiene el motor."""
    canal = _PIN_A_CANAL.get(pin)
    if canal is None:
        return

    pwm_dir = _pwm_path(canal)
    if not os.path.exists(pwm_dir):
        return

    try:
        _escribir(os.path.join(pwm_dir, "duty_cycle"), str(PULSO_PARAR_NS))
        sleep(0.15)
        _escribir(os.path.join(pwm_dir, "enable"), "0")
    except Exception:
        pass


def detener_todos():
    """Detiene todos los motores."""
    for pin in _PINES_MOTOR:
        detener(pin)


def cleanup():
    """Limpia todo."""
    detener_todos()
