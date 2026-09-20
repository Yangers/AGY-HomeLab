# Runbook: Aprovisionamiento de Cargas de Trabajo (VMs y LXCs)

Estándares y convenciones para crear nuevos contenedores o máquinas virtuales en `proxmox-yp`.

---

## 1. Convención de Asignación de VMIDs

* **`100`:** Reservado para `pbs-yp` (Proxmox Backup Server).
* **`101 - 119`:** Cargas de trabajo de infraestructura base existentes.
* **`120 - 199`:** Nuevos servicios LXC / contenedores de aplicaciones.
* **`200 - 299`:** Nuevas máquinas virtuales (QEMU / KVM).
* **`900 - 999`:** Plantillas (Templates Cloud-Init / Base LXC).

---

## 2. Asignación de Almacenamiento

| Tipo de Carga | Disco Raíz / OS | Datos / Almacenamiento Masivo |
| :--- | :--- | :--- |
| **Contenedores LXC ligeros** | `local-lvm` (NVMe thin) | Mount point a `Multimedia` o `UNAS` |
| **Bases de datos / I/O intensiva** | `SSD2` (ZFS Pool) | `SSD2` o volúmenes locales |
| **Máquinas Virtuales QEMU** | `local-lvm` o `VM-Storage` | `VM-Storage` o NFS `nasypa` |

---

## 3. Red y VLANs

* **Puente principal:** `vmbr0` (VLAN-aware).
* **Etiquetado:**
  * Servidores internos / API: VLAN Tag `10`
  * Cargas IoT / Domótica: VLAN Tag `100`
  * Cargas aisladas / DMZ: VLAN específica según política UniFi

---

## 4. Convención de Etiquetas (Tags)

Todos los contenedores y VMs deben crearse con tags que describan su rol para facilitar el filtrado y la gestión automatizada:
* `adblock`, `proxy`, `password-manager`, `media`, `automation`, `agent`, `db`, `dev`, `community-script`.
