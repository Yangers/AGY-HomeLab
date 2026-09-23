# AGY HomeLab — Infrastructure & Network Topology

Documentación exhaustiva de la arquitectura de red, hardware, virtualización y almacenamiento del HomeLab.

---

## 1. Topología de Red (UniFi Network)

### Controladora y Dispositivos de Red
* **Gateway:** `YP Gateway Fiber` (UniFi Dream Machine / Gateway)
* **Backbone 10G / SFP+:** `YP USW Aggregation` (`10.98.1.3`)
* **Switch Core PoE:** `YP Pro Max PoE` (`10.98.1.2`)
* **Switch 10G Escritorio:** `OF USW Flex XG` (`10.98.1.4`)
* **Switches Edge:**
  * `LR Lite 8 PoE` (`10.98.1.6`)
  * `MB Flex Mini` (`10.98.1.8`)
  * `GB Flex Mini` (`10.98.1.9`)
* **Puntos de Acceso Wi-Fi:**
  * `YP U7 Pro Max` (`10.98.1.201`)
  * `YP U7 Pro Wall` (`10.98.1.202`)
  * `U7 Pro XG` (`10.98.1.205`)
* **Sistema de Alimentación Redundante:** `YP USP RPS` (`10.98.1.20`)

### Segmentación por VLANs
| VLAN ID | Nombre | Subred / Gateway | Propósito / Dispositivos |
| :---: | :--- | :--- | :--- |
| **1** | `YPA Core` | `10.98.1.0/24` (GW `10.98.1.1`) | Gestión de infraestructura de red UniFi |
| **10** | `YPA Home` | `10.98.10.0/24` (GW `10.98.10.1`) | Servidores, Proxmox VE (`10.98.10.5`), almacenamiento |
| **40** | `YPA Cameras` | Subred aislada de seguridad | Cámaras UniFi Protect y videovigilancia |
| **50** | `YPA Wifi` | `10.98.50.0/24` (GW `10.98.50.1`) | Dispositivos de confianza personales (laptops, móviles) |
| **60** | `YPA Work` | Subred de trabajo | Equipos corporativos / trabajo remoto |
| **100** | `YPA IoT` | `10.98.100.0/24` (GW `10.98.100.1`) | Domótica: Hubitat Elevation (`10.98.100.50`), sensores |
| **200** | `YPA Guess` | Red de invitados | Acceso aislado a Internet |

---

## 2. Nodo de Virtualización: Proxmox VE (`proxmox-yp`)

### Especificaciones de Hardware
* **Hostname:** `proxmox-yp`
* **Dirección IP:** `10.98.10.5:8006` (VLAN 10)
* **CPU:** 13th Gen Intel Core i9-13900H (14 cores físicos, 20 hilos/vCPUs)
* **Memoria RAM:** ~32 GB DDR5
* **Almacenamiento Local:** NVMe de alta velocidad (`local`, `local-lvm`, `SSD2`)

### Configuración de Red del Host Proxmox
* **`bond0` (LACP - 802.3ad):** Enlace agregado de alta velocidad entre interfaces `enp2s0f0np0` y `enp2s0f1np1` con política de hash `layer3+4`.
* **`bond1` (Active-Backup):** Redundancia y tolerancia a fallos entre `bond0` (principal) y `enp90s0` (backup).
* **`vmbr0` (Bridge VLAN-Aware):** Puente virtual conectado a `bond1`, con soporte para VLANs `2-4094`, permitiendo etiquetar tráfico por contenedor/VM sin crear interfaces de red adicionales en el host.

---

## 3. Matriz de Almacenamiento (Storage Pools)

| Identificador | Tipo | Capacidad Total | Uso Típico | Contenido Permitido |
| :--- | :---: | :---: | :--- | :--- |
| **`local`** | `dir` | ~100 GB | Sistema base Proxmox | ISOs, plantillas LXC, backups locales |
| **`local-lvm`** | `lvmthin` | ~876 GB | Discos NVMe locales | Discos de VMs/LXCs, discos de arranque |
| **`SSD2`** | `zfspool` | ~248 GB | ZFS Pool SSD rápido | Discos virtuales de alta I/O |
| **`VM-Storage`** | `dir` | ~2.0 TB | Almacén masivo de VMs | Discos virtuales qcow2/raw, plantillas |
| **`Multimedia`** | `cifs` | ~8.6 TB | NAS / Almacén multimedia | Contenido Plex, descargas, backups |
| **`PBS`** | `pbs` | ~48 TB | Proxmox Backup Server | Copias de seguridad deduplicadas e incrementales |
| **`UNASMultimedia`**| `cifs` | ~48 TB | UNAS CIFS | Almacén masivo de medios |
| **`UNAS_Photos_RAW`**| `cifs`| ~48 TB | UNAS CIFS | Archivo fotográfico RAW |
| **`UNAS_Photos_Catalog`**| `cifs`| ~48 TB | UNAS CIFS | Catálogos de fotografía |
| **`UNAS_Yangers`** | `cifs` | ~48 TB | UNAS CIFS | Almacenamiento dedicado usuarios |
| **`nasypa`** | `nfs` | ~8.6 TB | Compartido NFS | Backups, imágenes y plantillas |

---

## 4. Inventario de Cargas de Trabajo (Workloads)

### Contenedores LXC
| VMID | Nombre | Estado | vCPUs | RAM (Max) | Propósito / Rol | Tags | Criticidad |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- | :---: |
| **101** | `hermesagent` | Activo | 2 | 4.0 GB | Agente IA y automatización | `agent`, `ai`, `automation` | Media |
| **102** | `pihole` | Activo | 4 | 1.0 GB | DNS Primario y bloqueo de publicidad | `adblock` | **CRÍTICO** |
| **103** | `ResilioSync` | Activo | 2 | 4.0 GB | Sincronización continua P2P | — | Media |
| **104** | `plex` | Activo | 8 | 8.0 GB | Servidor de medios y transcodificación | `media` | Normal |
| **105** | `pihole` | Activo | 4 | 1.0 GB | DNS Secundario (HA) | `adblock` | **CRÍTICO** |
| **107** | `vaultwarden` | Activo | 4 | 1.0 GB | Gestor de contraseñas Bitwarden | `password-manager` | **CRÍTICO** |
| **109** | `nginxproxymanager` | Activo | 2 | 2.0 GB | Reverse Proxy, SSL, certificados | `proxy` | **CRÍTICO** |
| **111** | `rustdesk` | Activo | 2 | 1.0 GB | Servidor de acceso remoto RustDesk | `remote-desktop` | Media |
| **120** | `laya-server` | Activo | 4 | 8.0 GB | Laya Fast Decision Model (System 1 AI) | `ai`, `ml`, `api` | Media |
| **121** | `obsidian-server` | Activo | 2 | 4.0 GB | Obsidian Web UI (LinuxServer Docker) | `notes`, `productivity`, `web` | Media |

### Máquinas Virtuales (QEMU/KVM)
| VMID | Nombre | Estado | vCPUs | RAM (Max) | Propósito / Rol | Criticidad |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **100** | `pbs-yp` | Activo | 4 | 6.0 GB | Proxmox Backup Server dedicado | Alta |
| **112** | `omarchy-vm` | Detenido | 6 | 8.0 GB | Entorno Arch Linux / Omarchy | Normal |

---

## 5. Domótica y Automatización (Hubitat Elevation)
* **Host:** `10.98.100.50` (VLAN 100 IoT)
* **App ID:** `506` (Maker API)
* **Dispositivos Conectados:** 49 dispositivos (sensores Zigbee/Z-Wave, actuadores, switches e integraciones).
