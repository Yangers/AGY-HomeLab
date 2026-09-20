# Runbook: Procedimientos de Emergencia y Recuperación

Guía de contingencia ante caídas de servicios, fallos de red o problemas en Proxmox VE.

---

## 1. Pérdida de Resolución DNS (Fallo de Pi-hole)

Si los clientes de la red no pueden resolver nombres de dominio o acceder a Internet:

1. **Diagnóstico rápido:**
   ```bash
   # Comprobar estado de los Pi-holes desde la CLI del proyecto
   ./scripts/pve.py list | grep pihole
   ```
2. **Reinicio de emergencia:**
   ```bash
   # Forzar reinicio del primario (102) o secundario (105)
   ./scripts/pve.py reboot 102 --force
   ./scripts/pve.py reboot 105 --force
   ```
3. **Alternativa temporal en UniFi:**
   Si ambos contenedores están inaccesibles, cambiar temporalmente el servidor DNS en la red UniFi (VLAN 10/50) a `1.1.1.1` o `8.8.8.8` desde la consola de UniFi Network.

---

## 2. Pérdida de Acceso a Servicios Web (Fallo de Nginx Proxy Manager)

Si los dominios internos (`*.ypa` o certificados SSL) no cargan:

1. **Comprobar contenedor 109:**
   ```bash
   ./scripts/pve.py status
   ./scripts/pve.py list | grep nginxproxymanager
   ```
2. **Reinicio seguro:**
   ```bash
   ./scripts/pve.py reboot 109 --force
   ```
3. **Verificación de logs en host:**
   ```bash
   ssh root@10.98.10.5 "pct status 109 && pct logs 109"
   ```

---

## 3. Caída de la Interfaz Web de Proxmox (Puerto 8006)

Si la web GUI no responde pero el host hace ping:

1. **Acceso directo vía SSH:**
   ```bash
   ssh root@10.98.10.5
   ```
2. **Reiniciar servicios de gestión de Proxmox:**
   ```bash
   systemctl restart pveproxy pvedaemon pvestatd
   ```
3. **Comprobar estado del demonio:**
   ```bash
   systemctl status pveproxy
   ```

---

## 4. Restauración de Backups desde Proxmox Backup Server (PBS)

El nodo `pbs-yp` (VMID 100) gestiona el repositorio de copias de seguridad de 48 TB en el storage `PBS`.

1. **Listar backups disponibles para un VMID:**
   ```bash
   ssh root@10.98.10.5 "pvesm list PBS --vmid <VMID>"
   ```
2. **Restaurar un contenedor LXC:**
   ```bash
   ssh root@10.98.10.5 "pct restore <NEW_OR_SAME_VMID> PBS:backup/ct/<VMID>/<TIMESTAMP> --storage local-lvm"
   ```
3. **Restaurar una VM QEMU:**
   ```bash
   ssh root@10.98.10.5 "qmrestore PBS:backup/vm/<VMID>/<TIMESTAMP> <NEW_OR_SAME_VMID> --storage VM-Storage"
   ```
