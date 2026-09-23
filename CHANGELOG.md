# Changelog — Proxmox & HomeLab Infrastructure

Registro cronológico de cambios, provisionamiento, migraciones y actualizaciones en la infraestructura del HomeLab.

---

## [2026-09-22]

### Añadido
- **Servidor Laya AI (LXC 120 `laya-server`):**
  - Despliegue de nuevo contenedor LXC con Debian 13 (Trixie) en Proxmox VE (`proxmox-yp`).
  - Recursos asignados: 4 vCPUs, 4 GB RAM, 512 MB swap, 20 GB disco en NVMe `local-lvm`.
  - Red estática: IP `10.98.10.40/24`, Gateway `10.98.10.1`, DNS `10.98.10.250` (VLAN 10 Servidores / `YPA Home`).
  - Autenticación SSH configurada con clave pública `~/.ssh/id_ed25519.pub`.
  - Instalación de PyTorch (CPU) y framework **Laya** (`convaiinnovations/laya` v0.3.6) en entorno virtual `/opt/laya/venv`.
  - Servicio HTTP API en FastAPI (`/opt/laya/server.py`) exponiendo endpoints `/health` y `/predict` (System 1 decision inference).
  - Servicio systemd `laya.service` habilitado para arranque automático.
- **Reverse Proxy & SSL (Nginx Proxy Manager):**
  - Configurado nuevo Proxy Host (`ID 29`) en NPM (LXC 109 `10.98.10.23:81`) para el dominio `laya.yangers.duckdns.org` reenviando a `http://10.98.10.40:8000`.
  - Asociado certificado wildcard existente `*.yangers.duckdns.org` (Cert ID 41) con Force SSL y HTTP/2 activo.
- **Optimización y Enrutamiento Multilingüe (Español / Inglés):**
  - Ampliación de memoria de LXC 120 de 4 GB a 8 GB RAM (`8192 MB`) y swap a 1 GB (`1024 MB`) en caliente.
  - Descarga y activación del modelo multilingüe (`convaiinnovations/laya` subfolder `multilingual` para Español y otros idiomas).
  - Implementación de `laya.Router(max_loaded=2)` con precarga en memoria de ambos modelos (`english` + `multilingual`), permitiendo detección y enrutamiento automático de idioma con latencia sub-segundo (~100-300 ms).
  - Creación de interfaz Web Playground interactiva en `https://laya.yangers.duckdns.org/` con presets y visualización en tiempo real de confianzas y probabilidades.
- **Gestión de Recursos Proxmox:**
  - Detenida máquina virtual `omarchy-vm` (VMID 112) liberando 8 GB RAM y 6 vCPUs en el nodo `proxmox-yp`.
- **Resolución DNS Local:**
  - Añadido registro `laya.yangers.duckdns.org` -> `10.98.10.23` en Pi-hole Primario (LXC 102 `10.98.10.250`) y Secundario (LXC 105 `10.98.10.251`).
  - Añadido registro estático en UniFi Cloud Gateway Fiber (`10.98.1.1` / `10.98.10.1` / `10.98.50.1`) para resolución en todas las VLANs.

---

## [2026-09-19]

### Añadido
- **Repositorio de Documentación:** Creación de la carpeta del proyecto [`AGY-HomeLab`](file:///Users/ypa/Documents/AGY-HomeLab) en `Documents`.
- **Topología Exhaustiva:** Creación de [`TOPOLOGY.md`](file:///Users/ypa/Documents/AGY-HomeLab/TOPOLOGY.md) documentando la matriz de VLANs UniFi, hardware de red, configuración de red Proxmox (`bond0` LACP / `bond1` active-backup / `vmbr0`), storage pools y cargas de trabajo.
- **Herramientas de Operación y Monitoreo (Scripts):**
  - [`scripts/pve.py`](file:///Users/ypa/Documents/AGY-HomeLab/scripts/pve.py): CLI en Python para inspección de recursos, listado de VMs/LXCs, storages, snapshots preventivos y control de ciclo de vida con protección automática de contenedores críticos.
  - [`scripts/healthcheck.py`](file:///Users/ypa/Documents/AGY-HomeLab/scripts/healthcheck.py): Verificación de salud global que consulta simultáneamente Proxmox VE, UniFi Network Controller y Hubitat Elevation.
- **Runbooks Operativos:**
  - [`runbooks/EMERGENCY.md`](file:///Users/ypa/Documents/AGY-HomeLab/runbooks/EMERGENCY.md): Procedimientos de contingencia ante caídas de DNS, Nginx Proxy Manager o caída de la GUI web de Proxmox, y restauración desde PBS.
  - [`runbooks/MAINTENANCE.md`](file:///Users/ypa/Documents/AGY-HomeLab/runbooks/MAINTENANCE.md): Protocolos de snapshots preventivos y actualizaciones de sistema.
  - [`runbooks/PROVISIONING.md`](file:///Users/ypa/Documents/AGY-HomeLab/runbooks/PROVISIONING.md): Estándares de asignación de VMIDs, storage, VLAN tagging y tags.
  - [`runbooks/IOT_TROUBLESHOOTING.md`](file:///Users/ypa/Documents/AGY-HomeLab/runbooks/IOT_TROUBLESHOOTING.md): Diagnóstico y resolución de incidencias en domótica Hubitat, protocolo KLAP de TP-Link y sensores mmWave.
- **Configuración y Seguridad:**
  - `.gitignore`, `.env.example` y `config.env` para aislar credenciales locales de API tokens.
- **Manual Central:** Creación de [`README.md`](file:///Users/ypa/Documents/AGY-HomeLab/README.md) con comandos rápidos y guía de uso.

### Incidencias y Correcciones
- **Domótica / Hubitat — Caída de comunicación Kasa TP-Link tras actualización de firmware:**
  - **Dispositivos afectados:** `Guess Bathroom` (Half Bath piso 1, ID `2828`, IP `10.98.100.74`) y `Storage Light` (Storage, ID `2829`, IP `10.98.100.132`), ambos modelo Kasa HS210.
  - **Causa:** La actualización de firmware cerró el puerto TCP local 9999 (protocolo XOR sin autenticación), provocando `commsError: true` en Hubitat e impidiendo el encendido automático de luces mediante sensores de movimiento.
  - **Solución aplicada:** Conmutación de "Compatibilidad con Terceros" en la app móvil TP-Link Kasa/Tapo para reabrir el puerto local 9999, seguido de sincronización `refresh` en Hubitat, restableciendo `commsError: false` y normalizando las automatizaciones. Documentado en [`runbooks/IOT_TROUBLESHOOTING.md`](file:///Users/ypa/Documents/AGY-HomeLab/runbooks/IOT_TROUBLESHOOTING.md).


### Eliminado
- **Limpieza de Almacenamiento y Depuración de VMs:**
  - **VMID 106 (`Lubuntu`):** Eliminada con purga completa de su disco virtual en `VM-Storage:106/vm-106-disk-0.qcow2` (100 GB liberados).
  - **VMID 108 (`Ubuntu`):** Eliminada con purga de discos en `Multimedia:108/vm-108-disk-0.qcow2` y volumen EFI en `local-lvm` (200 GB liberados).
  - **VMID 110 (`Manjaro`):** Eliminada con purga completa de su disco virtual en `VM-Storage:110/vm-110-disk-0.qcow2` (100 GB liberados).
  - **Total espacio recuperado:** ~400 GB de almacenamiento.

---

## [2026-09-18]

### Añadido
- **Detección y Conexión Inicial de Proxmox VE:**
  - Identificación del host Proxmox (`proxmox-yp`) en la red UniFi en la IP `10.98.10.5` (puerto `8006`).
  - Verificación del firmware y versión: Proxmox VE 9.2.18.
- **Configuración de Acceso API:**
  - Creación y verificación del API Token de autenticación: `mcp-user@pam!mcp`.
  - Integración del servidor MCP `proxmox-mcp-server` en [`~/.gemini/config/mcp_config.json`](file:///Users/ypa/.gemini/config/mcp_config.json) con TLS inseguro habilitado para certificado autosignado.
- **Inventario Inicial:**
  - Identificación de 8 contenedores LXC activos: `hermesagent` (101), `pihole` (102), `ResilioSync` (103), `plex` (104), `pihole` secundario (105), `vaultwarden` (107), `nginxproxymanager` (109), `rustdesk` (111).
  - Identificación de 2 VMs en ejecución: `pbs-yp` (100) y `omarchy-vm` (112).
