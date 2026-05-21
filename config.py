"""
Configuración central de la máquina expendedora.
Todos los pines GPIO y constantes de operación en un solo lugar.
"""

# Producto 1
BOTON_1_PIN = 17     # GPIO 17 — Pin físico 11
MOTOR_1_PIN = 12     # GPIO 12 — Pin físico 32 (PWM0)

# Producto 2
BOTON_2_PIN = 27     # GPIO 27 — Pin físico 13
MOTOR_2_PIN = 13     # GPIO 13 — Pin físico 33 (PWM1)

# Sensor de distancia HC-SR04 (compartido)
SENSOR_TRIGGER_PIN = 23   # GPIO 23 — Pin físico 16
SENSOR_ECHO_PIN    = 24   # GPIO 24 — Pin físico 18

# Constantes de operación
TIMEOUT_DISPENSADO_S   = 5
INTERVALO_LECTURA_S    = 0.03
DEBOUNCE_S             = 0.5
