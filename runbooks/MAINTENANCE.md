# Runbook: Mantenimiento y Actualizaciones

Directrices y procedimientos seguros para la actualización del host Proxmox VE y sus contenedores/VMs.

---

## 1. Regla de Oro Previa a Actualizaciones

> [!IMPORTANT]
> **SIEMPRE** crear un snapshot o verificar que existe un backup reciente en `PBS` antes de aplicar actualizaciones de software en contenedores de infraestructura (`pihole`, `vaultwarden`, `nginxproxymanager`).

### Crear un Snapshot Preventivo
```bash
# Formato: ./scripts/pve.py snapshot <VMID> <NOMBRE_SNAPSHOT> -d "Descripción"
./scripts/pve.py snapshot 107 pre_upgrade_20260919 -d "Snapshot previo a actualizacion de Vaultwarden"
```

Verificar que se ha registrado correctamente:
```bash
./scripts/pve.py snapshots 107
```

---

## 2. Actualización de Contenedores LXC (Debian/Ubuntu)

Para contenedores basados en Debian (ej. `vaultwarden`, `pihole`, `hermesagent`):

1. **Entrar al contenedor:**
   ```bash
   ssh root@10.98.10.5 "pct enter <VMID>"
   ```
2. **Actualizar repositorios y paquetes:**
   ```bash
   apt update && apt dist-upgrade -y && apt autoremove -y
   ```
3. **Verificar que el servicio responde** antes de eliminar el snapshot preventivo.
4. **Eliminar el snapshot tras verificar estabilidad:**
   ```bash
   ssh root@10.98.10.5 "pct delsnapshot <VMID> <NOMBRE_SNAPSHOT>"
   ```

---

## 3. Actualización del Host Proxmox VE (`proxmox-yp`)

1. **Verificar espacio libre en rootfs:**
   ```bash
   ./scripts/pve.py status
   ```
2. **Revisar estado del cluster y tareas activas:**
   Asegurarse de que no haya tareas de backup o replicación en curso.
3. **Actualización de paquetes del sistema:**
   ```bash
   ssh root@10.98.10.5 "apt update && apt dist-upgrade -y"
   ```
4. **Reinicio del Host (en caso de actualización de Kernel):**
   * Avisar o programar una ventana de mantenimiento (todos los servicios se detendrán temporalmente).
   * Ejecutar reinicio ordenado:
     ```bash
     ssh root@10.98.10.5 "reboot"
     ```
   * Monitorear el regreso a línea con:
     ```bash
     ./scripts/healthcheck.py
     ```
