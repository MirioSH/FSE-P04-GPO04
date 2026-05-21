### FUNDAMENTOS DE SISTEMAS EMBEBIDOS

# Máquina Expendedora — Raspberry Pi 5

Sistema de control para una máquina expendedora de **2 productos**, construido con **Python 3** sobre **Raspberry Pi 5**. Utiliza servomotores de rotación continua (MG90S 360°) para dispensar productos y un sensor ultrasónico (HC-SR04) para confirmar la entrega.

---

## Integrantes del equipo
- Arroyo
- Soto Huerta Gustavo Isaac
- Trujillo
- Urzua

---

## Descripción General

El sistema funciona de la siguiente manera:

1. El usuario presiona uno de los **2 botones físicos** para seleccionar un producto.
2. El **servomotor** correspondiente inicia un giro continuo que empuja el producto.
3. Un **sensor de distancia ultrasónico** (compartido entre ambos productos) detecta cuando el producto cae en la bandeja de entrega.
4. El motor se detiene automáticamente al confirmar la entrega, o tras un timeout de seguridad si no se detecta el producto.

---

## Arquitectura Modular

| Módulo | Descripción |
|---|---|
| `main.py` | Script principal. Inicializa hardware, gestiona el bucle de eventos y la interacción con los botones. |
| `config.py` | Configuración centralizada de pines GPIO y constantes de operación. |
| `motor.py` | Control de servomotores MG90S mediante hardware PWM (sysfs) del Raspberry Pi 5. |
| `sensor.py` | Lectura y monitoreo continuo del sensor HC-SR04 con calibración automática y detección ultra-sensible. |
| `dispensador.py` | Lógica de dispensado: coordina la secuencia motor → sensor → timeout. |
| `expendedora.service` | Archivo de servicio `systemd` para ejecución automática al encender el Raspberry Pi. |

---

## Diagrama de Pines GPIO

| Componente | GPIO | Pin Físico | Notas |
|---|---|---|---|
| Botón Producto 1 | GPIO 17 | Pin 11 | Pull-up interno |
| Botón Producto 2 | GPIO 27 | Pin 13 | Pull-up interno |
| Motor Producto 1 | GPIO 12 | Pin 32 | PWM0 (hardware) |
| Motor Producto 2 | GPIO 13 | Pin 33 | PWM1 (hardware) |
| Sensor Trigger | GPIO 23 | Pin 16 | HC-SR04 compartido |
| Sensor Echo | GPIO 24 | Pin 18 | HC-SR04 compartido |

---

## Requisitos

### Hardware
- Raspberry Pi 5
- 2× Servomotor MG90S (rotación continua 360°)
- 1× Sensor ultrasónico HC-SR04
- 2× Botones pulsadores
- Fuente de alimentación adecuada

### Software
- Raspberry Pi OS (Bookworm o superior)
- Python 3.11+
- Biblioteca `gpiozero` (incluida en Raspberry Pi OS)

---

## Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/proyecto.git
cd proyecto
```

### 2. Verificar dependencias

`gpiozero` viene preinstalado en Raspberry Pi OS. Puedes verificarlo con:

```bash
python3 -c "import gpiozero; print(gpiozero.__version__)"
```

### 3. Ejecutar manualmente

```bash
sudo python3 main.py
```

> **Nota:** Se requiere `sudo` para acceder al hardware PWM vía sysfs.

### 4. (Opcional) Configurar inicio automático con systemd

Copia el archivo de servicio y habilita el arranque automático:

```bash
sudo cp expendedora.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable expendedora.service
sudo systemctl start expendedora.service
```

Para verificar el estado:

```bash
sudo systemctl status expendedora.service
```

Para ver los logs en tiempo real:

```bash
sudo journalctl -u expendedora.service -f
```

---

## Detener el Sistema

- **Ejecución manual:** Presiona `Ctrl+C` en la terminal.
- **Servicio systemd:**

```bash
sudo systemctl stop expendedora.service
```

---

## Licencia

Este proyecto es de uso académico.
