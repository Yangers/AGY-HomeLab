# AGY HomeLab — Central Management & Operations Repository

Repositorio central de documentación, utilidades operativas, directrices de automatización y runbooks para la infraestructura del HomeLab (Proxmox VE, UniFi Network y Hubitat Elevation).

---

## 📁 Estructura del Repositorio

```
AGY-HomeLab/
├── .env.example              # Plantilla de variables de entorno
├── config.env                # Configuración activa local (ignorado en git)
├── .gitignore                # Reglas de exclusión para credenciales y temporales
├── GEMINI.md                 # Contexto operativo y reglas del asistente de IA
├── TOPOLOGY.md               # Especificaciones de hardware, VLANs y almacenamiento
├── CHANGELOG.md              # Registro cronológico de cambios de infraestructura
├── scripts/
│   ├── requirements.txt      # Dependencias Python mínimas
│   ├── pve.py                # CLI para gestión e inspección de Proxmox VE
│   └── healthcheck.py        # Dashboard de salud unificado (PVE + UniFi + Hubitat)
└── runbooks/
    ├── EMERGENCY.md          # Protocolos de recuperación y contingencia
    ├── MAINTENANCE.md        # Procedimientos de snapshots y actualizaciones
    ├── PROVISIONING.md       # Estándares para nuevos LXCs y VMs
    └── IOT_TROUBLESHOOTING.md# Solución de problemas de domótica Hubitat y TP-Link Kasa
```

---

## 🚀 Utilidades Rápidas (CLI)

### 1. Chequeo de Salud Global del HomeLab
Verifica en segundos el estado del host Proxmox, servicios críticos, controladora UniFi y Hubitat:
```bash
./scripts/healthcheck.py
```

### 2. Gestión de Proxmox VE con `pve.py`

* **Estado del host y recursos (CPU, RAM, Uptime):**
  ```bash
  ./scripts/pve.py status
  ```
* **Listado de todas las cargas de trabajo (LXCs y VMs):**
  ```bash
  ./scripts/pve.py list
  ```
* **Estado y espacio de todos los storage pools:**
  ```bash
  ./scripts/pve.py storage
  ```
* **Crear un snapshot preventivo:**
  ```bash
  ./scripts/pve.py snapshot 107 backup_pre_update -d "Snapshot previo a actualizacion"
  ```
* **Listar snapshots de un contenedor/VM:**
  ```bash
  ./scripts/pve.py snapshots 107
  ```
* **Iniciar, reiniciar o detener un servicio:**
  ```bash
  ./scripts/pve.py start 101
  ./scripts/pve.py reboot 101
  # Servicios críticos requieren confirmación explícita con --force:
  ./scripts/pve.py reboot 102 --force
  ```

---

## 🔒 Reglas de Seguridad Operacional

1. **Servicios Críticos Protegidos:**
   * `102` (`pihole` primario), `105` (`pihole` secundario)
   * `107` (`vaultwarden`)
   * `109` (`nginxproxymanager`)
   * *Bajo ninguna circunstancia detenerlos o reiniciarlos sin autorización explícita.*
2. **Acciones Destructivas:**
   * La eliminación de discos virtuales, purga de snapshots o destrucción de VMs requiere confirmación previa detallada en [`CHANGELOG.md`](file:///Users/ypa/Documents/AGY-HomeLab/CHANGELOG.md).
