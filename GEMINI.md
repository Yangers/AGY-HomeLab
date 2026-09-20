# Proxmox VE — AGY HomeLab Context & Guidelines

Este archivo contiene las directrices, topología y procedimientos operativos para interactuar con el entorno de virtualización **Proxmox VE** en la infraestructura doméstica (HomeLab).

---

## 1. Información del Host y Red

| Parámetro | Valor |
| :--- | :--- |
| **Hostname / Nodo** | `proxmox-yp` |
| **Dirección IP** | `10.98.10.5` |
| **Puerto Web / API** | `8006` (HTTPS) |
| **Versión PVE** | `Proxmox VE 9.2.18` (Kernel Linux, release 9.2) |
| **Certificado TLS** | Autosignado (`CN=proxmox-yp.com`), requiere omitir validación TLS (`insecure: true`) |
| **Recursos del Nodo** | 20 vCPUs, ~32 GB RAM |
| **Red / Subred** | VLAN Servidores `10.98.10.0/24` (Gateway gestionado en UniFi) |

---

## 2. Autenticación y Acceso API

El acceso automatizado está configurado a través de **API Tokens** de Proxmox y gestionado mediante el servidor MCP (`proxmox-mcp-server`) y llamadas directas a la API REST:

- **Token ID:** `mcp-user@pam!mcp`
- **Configuración MCP:** [`~/.gemini/config/mcp_config.json`](file:///Users/ypa/.gemini/config/mcp_config.json)
- **Cabecera HTTP:**
  ```http
  Authorization: PVEAPIToken=mcp-user@pam!mcp=<PROXMOX_TOKEN_SECRET>
  ```
- **Variables de Entorno Estándar:**
  ```bash
  PROXMOX_HOST="https://10.98.10.5:8006"
  PROXMOX_TOKEN_ID="mcp-user@pam!mcp"
  PROXMOX_TOKEN_SECRET="<SECRET_EN_MCP_CONFIG>"
  PROXMOX_INSECURE_TLS="true"
  PVE_READONLY="false"
  ```

---

## 3. Inventario de Cargas de Trabajo (Workloads)

### Contenedores LXC Activos

| VMID | Nombre | Rol / Propósito | Recursos | Tags |
| :---: | :--- | :--- | :--- | :--- |
| **101** | `hermesagent` | Agente IA y automatización | 2 vCPUs, 4 GB RAM, 20 GB disco | `agent`, `ai`, `automation` |
| **102** | `pihole` | DNS Primario / Bloqueo de anuncios | 4 vCPUs, 1 GB RAM, 4 GB disco | `adblock` |
| **103** | `ResilioSync` | Sincronización continua de archivos | 2 vCPUs, 4.3 GB RAM, 20 GB disco | — |
| **104** | `plex` | Servidor de medios Plex | 8 vCPUs, 8.6 GB RAM, 8.3 GB disco | `media` |
| **105** | `pihole` | DNS Secundario (alta disponibilidad) | 4 vCPUs, 1 GB RAM, 4 GB disco | `adblock` |
| **107** | `vaultwarden` | Gestor de contraseñas Bitwarden | 4 vCPUs, 1 GB RAM, 20 GB disco | `password-manager` |
| **109** | `nginxproxymanager` | Reverse Proxy & SSL certificates | 2 vCPUs, 2.1 GB RAM, 16.8 GB disco | `proxy` |
| **111** | `rustdesk` | Servidor de acceso remoto RustDesk | 2 vCPUs, 1 GB RAM, 8.5 GB disco | `remote-desktop` |

### Máquinas Virtuales (QEMU / KVM) Activas

| VMID | Nombre | Rol / Propósito | Recursos |
| :---: | :--- | :--- | :--- |
| **100** | `pbs-yp` | Proxmox Backup Server dedicado | 4 vCPUs, 6 GB RAM, 40 GB disco |
| **112** | `omarchy-vm` | Entorno Linux Arch/Omarchy | 6 vCPUs, 8 GB RAM, 64 GB disco |

---

## 4. Pools de Almacenamiento (Storages)

- **`local`**: Directorio raíz (100 GB) para ISOs y plantillas.
- **`local-lvm`**: NVMe Thin Pool (~876 GB) para discos de SO de LXCs y VMs.
- **`SSD2`**: Pool ZFS de estado sólido (~248 GB) para cargas I/O intensivas.
- **`VM-Storage`**: Almacenamiento local (~2 TB) para discos virtuales QEMU/LXC.
- **`PBS`**: Proxmox Backup Server dedicado (~48 TB) para backups deduplicados.
- **`Multimedia` / `nasypa`**: Recursos NFS/CIFS (~8.6 TB) para medios y descargas.
- **`UNAS_*`**: Volúmenes de almacenamiento CIFS en red (~48 TB) para fotos, archivos y catálogos.

---

## 5. Herramientas Locales del Repositorio (Scripts)

El repositorio cuenta con herramientas CLI listas para usar con credenciales locales (`config.env`):
- **[`scripts/healthcheck.py`](file:///Users/ypa/Documents/AGY-HomeLab/scripts/healthcheck.py)**: Chequeo de salud integral de Proxmox VE, UniFi Network y Hubitat.
- **[`scripts/pve.py`](file:///Users/ypa/Documents/AGY-HomeLab/scripts/pve.py)**: CLI rápida para consultar estado, cargas, storages, snapshots y control de ciclo de vida con protección de servicios críticos.

---

## 6. Procedimientos y Runbooks Operativos

- **Topología completa y red UniFi:** [`TOPOLOGY.md`](file:///Users/ypa/Documents/AGY-HomeLab/TOPOLOGY.md)
- **Procedimientos de emergencia y contingencia:** [`runbooks/EMERGENCY.md`](file:///Users/ypa/Documents/AGY-HomeLab/runbooks/EMERGENCY.md)
- **Actualizaciones y snapshots preventivos:** [`runbooks/MAINTENANCE.md`](file:///Users/ypa/Documents/AGY-HomeLab/runbooks/MAINTENANCE.md)
- **Estándares para nuevas VMs / LXCs:** [`runbooks/PROVISIONING.md`](file:///Users/ypa/Documents/AGY-HomeLab/runbooks/PROVISIONING.md)

---

## 7. Reglas Operativas para el Asistente (Agent Guidelines)

1. **Servicios Críticos:**
   - `pihole` (102, 105), `nginxproxymanager` (109) y `vaultwarden` (107) son componentes esenciales de la red. **No detener, reiniciar ni alterar su configuración** sin autorización explícita.
2. **Acciones Destructivas:**
   - La eliminación de VMs/LXCs, borrado de snapshots o purga de volúmenes siempre requiere confirmación previa detallando qué datos y capacidad se verán afectados.
3. **Consulta de Estado vía API o CLI:**
   - Preferir el uso de `scripts/pve.py` o herramientas MCP `proxmox` para una inspección rápida y estandarizada.
   - Registrar cualquier cambio estructural en [`CHANGELOG.md`](file:///Users/ypa/Documents/AGY-HomeLab/CHANGELOG.md).

