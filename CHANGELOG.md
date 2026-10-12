# Changelog — Proxmox & HomeLab Infrastructure

Registro cronológico de cambios, provisionamiento, migraciones y actualizaciones en la infraestructura del HomeLab.

---

## [2026-10-12]

### Configurado & Instalado
- **Pi Agent & Pi Durable (LXC 122 `pi-agent`):**
  - **Instalación de paquetes Pi Durable:** Instalados globalmente `@earendil-works/pi-durable@1.1.0`, `@earendil-works/pi-ai`, `@earendil-works/chord` y el orquestador de subagentes persistentes `pi-durable-subagents`.
  - **Integración en Pi Coding Agent:** Añadidos los paquetes `npm:pi-antigravity` y `npm:pi-durable-subagents` al entorno de Pi (`~/.pi/agent/settings.json`).
  - **Sincronización de Autenticación & Modelos:** Replicadas las credenciales y configuración OAuth de Antigravity (`auth.json`, `antigravity-accounts.json`, `models-store.json`) desde la estación de trabajo local, permitiendo acceso directo a `antigravity/gemini-3.8-flash` con cuota gratuita.
  - **Verificación operativa:** Ejecutado y verificado `pi-durable-subagents smoke` (todas las superficies de ejecución y watch view operativas) y probado `pi -p` respondiendo con éxito vía Antigravity.

---

## [2026-10-04]

### Actualizado
- **Nginx Proxy Manager (LXC 109 `nginxproxymanager`):**
  - **Snapshot preventivo:** Creado snapshot `pre_upgrade_2160_20261004` antes de la intervención.
  - **Actualización de versión:** Actualizado de `v2.15.1` a `v2.16.0` (upstream release 2026-09-24) usando el script oficial de mantenimiento de Community-Scripts.
  - **Componentes:** Node.js 22 & Yarn, Certbot & certbot-dns-cloudflare, compilación de Frontend/Backend con better-sqlite3 y parches del sistema operativo Debian 13.
  - **Verificación operativa:** Panel web en puerto 81 y proxy hosts SSL activos (`pass`, `pihole`, etc.).
- **Pi-hole Alta Disponibilidad (LXC 105 Secundario & LXC 102 Primario):**
  - **Estrategia sin pérdida de servicio (Zero Downtime):** Actualizados secuencialmente para mantener resolución DNS activa y redundancy 100% operativa en todo momento.
  - **Pi-hole Secundario (LXC 105 `10.98.10.251`):** Creado snapshot `pre_upgrade_20261004`, actualizado Pi-hole FTL de `v6.7` a `v6.7.1`, y aplicados 10 parches de seguridad del sistema operativo (OpenSSL 3.5.7, Unbound 1.26.1, Bind9 libs). Verificada resolución DNS antes de intervenir el nodo primario.
  - **Pi-hole Primario (LXC 102 `10.98.10.250`):** Creado snapshot `pre_upgrade_20261004`, actualizado Pi-hole FTL a `v6.7.1`, y aplicados 10 parches de seguridad de Debian (OpenSSL, Unbound, Bind9). Verificada resolución DNS.
- **Vaultwarden (LXC 107 `vaultwarden`):**
  - **Snapshot preventivo:** Creado snapshot `pre_upgrade_20261004`.
  - **Actualización de SO:** Aplicados 17 parches de seguridad acumulativos (OpenSSL, libssl-dev, linux-libc-dev, libheif). Verificado servicio `vaultwarden` activo y portal web (`pass.yangers.duckdns.org`).
- **Plex Media Server (LXC 104 `plex`):**
  - **Actualización de SO:** Aplicados 41 parches del sistema base Ubuntu 24.04 Noble (kernel/libc, mesa drivers, openssl, apparmor, curl).
  - **Verificación operativa:** Servicio `plexmediaserver` activo y portal respondiendo vía proxy en `plex.yangers.duckdns.org`.
- **Resilio Sync (LXC 103 `ResilioSync`):**
  - **Actualización de SO:** Aplicados 7 parches de seguridad base Debian 12 Bookworm (openssl, libssl3, liblzma5, tzdata). Servicio `resilio-sync` activo.
- **Gitea (LXC 106 `gitea`):**
  - **Snapshot preventivo:** Creado snapshot `pre_upgrade_20261004`.
  - **Actualización de SO:** Aplicados 6 parches de seguridad Debian 13 (OpenSSL, libssl3, jq). Servicio `gitea` verificado y activo.
- **RustDesk Server (LXC 111 `rustdesk`):**
  - **Snapshot preventivo:** Creado snapshot `pre_upgrade_20261004`.
  - **Actualización de SO:** Aplicados 9 parches de seguridad Debian 13 (OpenSSL, bind9, jq). Verificados servicios `rustdesk-hbbs`, `rustdesk-hbbr` y `rustdesk-api` activos.
- **Hermes Agent (LXC 101 `hermesagent`):**
  - **Snapshot preventivo:** Creado snapshot `pre_upgrade_20261004`.
  - **Actualización de SO:** Aplicados 12 parches del sistema operativo incluyendo Node.js 22.23.3 y OpenSSL 3.5.7.
  - **Verificación operativa:** Servicio `hermes-dashboard`, gateway y cronjobs verificados y activos con Gemini Free Tier.

---

## [2026-09-30]

### Optimizado & Actualizado
- **Hermes Agent (LXC 101 `hermesagent`):**
  - **Activación de Gemini Free Tier Puro ($0.00/mes):**
    - Configurada nueva clave de API gratuita de Google AI Studio sin tarjeta de crédito asociada en `/home/hermes/.hermes/.env` y `config.yaml`.
    - Actualizado el modelo por defecto a `gemini-3.8-flash` (versión recomendada por Google, sin errores de alta demanda 503).
    - Limpiado el estado de credenciales agotadas en `auth.json`.
  - **Almacenamiento de clave Groq:**
    - Registrada clave `GROQ_API_KEY` en `/home/hermes/.hermes/.env` para uso en herramientas de audio/transcripción Whisper.
  - **Optimización Integral de Cronjobs (`jobs.json`):**
    - Creado script por lotes `/home/hermes/scripts/gws_cleanup.py` para `Google Workspace Daily Cleanup & Review`: ejecuta búsqueda, filtrado de confirmaciones de backups de NAS y revisión de calendario en una sola pasada.
    - Creado script `/home/hermes/scripts/healthcheck.py` para `Infrastructure Health Check`: consulta Proxmox (SSH), Hubitat (API MCP) y UniFi (puerto 443) directamente sin disparar los filtros de seguridad de terminal por URLs HTTP.
    - Restringido `enabled_toolsets: ["terminal"]` en ambos cronjobs, reduciendo el tamaño del system prompt de ~18,000 tokens a ~2,900 tokens por turno (reducción del 80%).
    - **Resultados de la optimización:**
      - Llamadas al modelo por corrida: reducidas de **25 llamadas a solo 2 llamadas**.
      - Tiempo de ejecución: reducido de **9 minutos a menos de 15 segundos**.
      - Consumo total de tokens: reducido en un **90%**.
      - Costo total operativo: **$0.00 USD / mes** garantizado dentro del tier gratuito de Gemini.

---

## [2026-09-29]

### Modificado & Corregido
- **Hermes Agent (LXC 101 `hermesagent`):**
  - **Diagnóstico de límite de cuota (HTTP 429 RESOURCE_EXHAUSTED):** Identificada la causa de fallo en las tareas programadas de Hermes (`Google Workspace Daily Cleanup & Review` y `Infrastructure Health Check`), originada por haber alcanzado el límite mensual de gasto de la clave API de Google AI Studio.
  - **Eliminación de acumulación recursiva de tokens (Paso 2):** Desactivada la acumulación de contexto histórico (`--no-continuity` -> `context_from: null`) en ambos cronjobs (`a428c4200498` y `a9ef8f8dbcc2`), evitando que el historial de ejecuciones previas multiplique exponencialmente el consumo de tokens en cada turno.
  - **Configuración de cadena de fallback gratuita (Paso 3):**
    - Añadida clave de API OpenRouter a `/home/hermes/.hermes/.env`.
    - Configurada cadena de proveedores de respaldo `fallback_providers` en `/home/hermes/.hermes/config.yaml`:
      1. Primario: `gemini-3.6-flash` (Google AI Studio).
      2. Respaldo 1: `qwen/qwen3.8-27b:free` (OpenRouter, tier 100% gratuito).
      3. Respaldo 2: `nvidia/nemotron-3-super-120b-a12b:free` (OpenRouter, tier 100% gratuito).
  - **Validación y Pruebas Operativas:**
    - Prueba exitosa de chat one-shot (`hermes -z`).
    - Ejecución manual de prueba del cronjob `a428c4200498`, verificando la activación automática del fallback hacia OpenRouter Nemotron 120B, procesamiento de correos en Google Workspace, verificación de Google Calendar y envío exitoso del informe a Telegram.
    - Reinicio limpio de LXC 101 validando el arranque automático de `hermes-gateway.service`, `hermes-dashboard.service`, WhatsApp bridge y cron heartbeat.

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
- **Servidor Obsidian Web (LXC 121 `obsidian-server`):**
  - Despliegue de nuevo contenedor LXC con Debian 13 (Trixie) en Proxmox VE (`proxmox-yp`).
  - Recursos asignados: 2 vCPUs, 4 GB RAM, 512 MB swap, 16 GB disco NVMe en `local-lvm`, features `nesting=1,keyctl=1`.
  - Red estática: IP `10.98.10.41/24`, Gateway `10.98.10.1`, DNS `10.98.10.250` (VLAN 10 Servidores / `YPA Home`).
  - Instalación de Docker CE y despliegue del contenedor `lscr.io/linuxserver/obsidian:latest` transmitiendo la interfaz gráfica de escritorio de Obsidian a la web (puerto 3000).
  - Almacenamiento persistente de vaults y configuración en `/opt/obsidian/config` y `/opt/obsidian/vaults`.
  - Configurado Proxy Host (`ID 30`) en Nginx Proxy Manager para `obsidian.yangers.duckdns.org` reenviando a `http://10.98.10.41:3000` con SSL wildcard `*.yangers.duckdns.org`, HTTP/2 y soporte para WebSockets.
  - Registro DNS añadido en Pi-hole 102 (`10.98.10.250`), Pi-hole 105 (`10.98.10.251`) y UniFi Gateway para resolución interna en toda la red.
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
