# Changelog — Proxmox & HomeLab Infrastructure

Registro cronológico de cambios, provisionamiento, migraciones y actualizaciones en la infraestructura del HomeLab.

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
- **Configuración y Seguridad:**
  - `.gitignore`, `.env.example` y `config.env` para aislar credenciales locales de API tokens.
- **Manual Central:** Creación de [`README.md`](file:///Users/ypa/Documents/AGY-HomeLab/README.md) con comandos rápidos y guía de uso.

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
