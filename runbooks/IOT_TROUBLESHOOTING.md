# Runbook — IoT & Home Automation Troubleshooting (Hubitat)

Guía operativa y resolución de incidentes comunes en la plataforma de domótica **Hubitat Elevation** (`10.98.100.50`, VLAN 100 IoT).

---

## 1. Incidente: Pérdida de Comunicación en Interruptores TP-Link Kasa / Tapo

### Síntomas
- Las luces automatizadas no encienden tras detectar presencia o movimiento.
- El sensor de movimiento / presencia registra eventos `motion: active` correctamente en los logs de Hubitat.
- Las aplicaciones de iluminación (e.g. *Room Lights*) ejecutan los comandos `on()` / `off()`, pero el estado del interruptor no cambia o permanece en `off`.
- En el dispositivo en Hubitat, el atributo **`commsError`** está en **`true`** con un contador elevado de fallos (`errorCount > 0`).

### Causa Raíz
- Las actualizaciones de firmware de TP-Link (Kasa / Tapo) para modelos como el **HS210**, **HS200**, **KP115**, etc., **cierran por defecto el puerto TCP local 9999** (protocolo heredado XOR sin autenticación).
- El driver integrado de Hubitat (`davegutBuiltin`) se comunica localmente por el puerto 9999. Al cerrarse, el puerto responde `Connection refused` (error 111), bloqueando todas las órdenes LAN.

### Diagnóstico Rápido
1. Comprobar conectividad ICMP y estado del puerto 9999 desde la red:
   ```bash
   # Ping al dispositivo
   ping -c 2 <IP_DISPOSITIVO>
   
   # Verificar si el puerto local 9999 está abierto o cerrado
   nc -zv -w 2 <IP_DISPOSITIVO> 9999
   ```
2. Si el ping responde pero el puerto 9999 da error o rechazo (mientras el puerto 80 responde con `Server: SHIP 2.0`), la actualización de firmware ha bloqueado el protocolo local.

### Solución

#### Método Rápido (Reapertura de Puerto 9999)
1. Abrir la aplicación móvil **TP-Link Kasa** o **Tapo** en el smartphone.
2. Ir a **Ajustes del Dispositivo** (icono de engranaje) o en la pestaña **"Yo" / Configuración**.
3. Buscar la sección **"Servicios de Terceros"** o **"Compatibilidad con Terceros"** (*Third-Party Compatibility*).
4. **Desactivar y volver a activar** el interruptor. Esto fuerza al firmware a volver a escuchar peticiones en el puerto local 9999.
5. En Hubitat, enviar un comando `refresh` al dispositivo para restablecer `commsError: false`.
6. **Recomendado:** Desactivar las actualizaciones automáticas de firmware en la app Kasa/Tapo para prevenir caídas recurrentes.

#### Método Definitivo (Migración a Integración KLAP)
Si en futuras actualizaciones el puerto 9999 queda permanentemente eliminado:
1. Abrir **Hubitat Package Manager (HPM)** en `http://10.98.100.50/`.
2. Instalar el paquete **TP-Link Tapo / Kasa Integration** de Dave Gutheinz (compatible con el protocolo autenticado KLAP / cifrado local sobre puertos 80/443).
3. Configurar las credenciales de la cuenta TP-Link y redescubrir los interruptores.

---

## 2. Inventario de Dispositivos Kasa Involucrados

| Dispositivo Hubitat | ID | Modelo | Dirección IP | Habitación | Sensor Asociado | App de Automatización |
| :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| `Guess Bathroom` | **2828** | HS210 | `10.98.100.74` | 1st Floor Half Bath (Living Room) | `Guess Bathroom Motion` (Hue, ID 1620) | App 695 (*Guess Bathroom Light Automation*) |
| `Storage Light` | **2829** | HS210 | `10.98.100.132` | Storage Room | `Storage Motion` (Tuya, ID 1874) | App 793 (*New Storage Ligths*) |

---

## 3. Sensores mmWave / Radar de Presencia (Linptech ES1)

### Particularidades
- En el baño del dormitorio de invitados (`Guess Bedroom Bath`), el sensor **Linptech Human Presence Sensor ES1** (`ID: 2922`, Zigbee) mide distancia en tiempo real (`distance`).
- Si la persona permanece inmóvil o en el límite de la zona de cobertura, el sensor puede reportar cambios de distancia sin activar la transición `motion: active`.
- **Ajustes recomendados:**
  - `motionSensitivity`: medium
  - `staticSensitivity`: medium-high
  - `detectionDistance`: 3m
  - `fadeTime`: 10s
- En la app de automatización (*Room Lights* 702), se recomienda añadir el sensor PIR secundario (`Guess Bedroom Bath Motion`, ID 1621) como disparador adicional para asegurar encendido instantáneo al cruzar la puerta.
