#!/usr/bin/env python3
"""
HomeLab Unified Healthcheck
Checks connectivity and operational health across Proxmox VE, UniFi Network, and Hubitat.
"""

import sys
import os
import urllib3
import requests
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_env():
    base_dir = Path(__file__).resolve().parent.parent
    for env_name in ["config.env", ".env"]:
        env_file = base_dir / env_name
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        v = v.strip().strip("'\"")
                        if k not in os.environ:
                            os.environ[k] = v

def check_proxmox():
    host = os.environ.get("PROXMOX_HOST", "https://10.98.10.5:8006").rstrip("/")
    node = os.environ.get("PROXMOX_NODE", "proxmox-yp")
    token_id = os.environ.get("PROXMOX_TOKEN_ID", "mcp-user@pam!mcp")
    token_secret = os.environ.get("PROXMOX_TOKEN_SECRET", "")
    
    if not token_secret:
        return {"status": "SKIP", "detail": "PROXMOX_TOKEN_SECRET not configured"}
        
    headers = {"Authorization": f"PVEAPIToken={token_id}={token_secret}"}
    try:
        r_ver = requests.get(f"{host}/api2/json/version", headers=headers, verify=False, timeout=5)
        r_ver.raise_for_status()
        ver_info = r_ver.json().get("data", {})
        
        r_node = requests.get(f"{host}/api2/json/nodes/{node}/status", headers=headers, verify=False, timeout=5)
        r_node.raise_for_status()
        node_info = r_node.json().get("data", {})
        
        r_lxc = requests.get(f"{host}/api2/json/nodes/{node}/lxc", headers=headers, verify=False, timeout=5)
        lxcs = r_lxc.json().get("data", []) if r_lxc.status_code == 200 else []
        
        r_qemu = requests.get(f"{host}/api2/json/nodes/{node}/qemu", headers=headers, verify=False, timeout=5)
        vms = r_qemu.json().get("data", []) if r_qemu.status_code == 200 else []
        
        running_lxcs = sum(1 for c in lxcs if c.get("status") == "running")
        running_vms = sum(1 for v in vms if v.get("status") == "running")
        
        # Check critical containers
        critical_ids = {102: "pihole (primary)", 105: "pihole (secondary)", 107: "vaultwarden", 109: "nginxproxymanager"}
        crit_status = {}
        for c in lxcs:
            vmid = int(c.get("vmid", 0))
            if vmid in critical_ids:
                crit_status[critical_ids[vmid]] = c.get("status")
                
        all_crit_running = all(st == "running" for st in crit_status.values()) and len(crit_status) == len(critical_ids)
        
        mem = node_info.get("memory", {})
        mem_pct = (mem.get("used", 0) / mem.get("total", 1)) * 100
        uptime_days = node_info.get("uptime", 0) / 86400

        return {
            "status": "OK" if all_crit_running else "WARN",
            "version": ver_info.get("version"),
            "kernel": node_info.get("kversion"),
            "uptime_days": f"{uptime_days:.1f}d",
            "mem_usage": f"{mem_pct:.1f}%",
            "workloads": f"{running_lxcs}/{len(lxcs)} LXCs, {running_vms}/{len(vms)} VMs running",
            "critical_services": crit_status
        }
    except Exception as e:
        return {"status": "FAIL", "detail": str(e)}

def check_unifi():
    url = os.environ.get("UNIFI_API_URL", "https://10.98.50.1").rstrip("/")
    api_key = os.environ.get("UNIFI_API_KEY", "")
    if not api_key:
        return {"status": "SKIP", "detail": "UNIFI_API_KEY not configured"}
        
    headers = {"X-API-KEY": api_key}
    try:
        r = requests.get(f"{url}/proxy/network/integration/v1/info", headers=headers, verify=False, timeout=5)
        r.raise_for_status()
        data = r.json()
        
        # Check networks
        r_net = requests.get(f"{url}/proxy/network/api/s/default/rest/networkconf", headers=headers, verify=False, timeout=5)
        networks_count = len(r_net.json().get("data", [])) if r_net.status_code == 200 else "N/A"
        
        # Check devices
        r_dev = requests.get(f"{url}/proxy/network/api/s/default/stat/device", headers=headers, verify=False, timeout=5)
        devices_count = len(r_dev.json().get("data", [])) if r_dev.status_code == 200 else "N/A"

        return {
            "status": "OK",
            "version": data.get("applicationVersion", "Unknown"),
            "networks_count": networks_count,
            "devices_count": devices_count
        }
    except Exception as e:
        return {"status": "FAIL", "detail": str(e)}

def check_hubitat():
    host = os.environ.get("HUBITAT_HOST", "10.98.100.50")
    app_id = os.environ.get("HUBITAT_APP_ID", "506")
    token = os.environ.get("HUBITAT_ACCESS_TOKEN", "")
    if not token:
        return {"status": "SKIP", "detail": "HUBITAT_ACCESS_TOKEN not configured"}
        
    try:
        url = f"http://{host}/apps/api/{app_id}/devices?access_token={token}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        devices = r.json()
        return {
            "status": "OK",
            "device_count": len(devices),
            "host": host
        }
    except Exception as e:
        return {"status": "FAIL", "detail": str(e)}

def main():
    load_env()
    print("=" * 65)
    print(" AGY HomeLab — Unified Infrastructure Health Check")
    print("=" * 65)
    
    # 1. Proxmox
    print("\n[1] Proxmox VE:")
    pve = check_proxmox()
    if pve["status"] in ["OK", "WARN"]:
        badge = "🟢 OK" if pve["status"] == "OK" else "🟡 WARN"
        print(f"    Status:      {badge}")
        print(f"    Release:     Proxmox VE {pve['version']} (Uptime: {pve['uptime_days']})")
        print(f"    Kernel:      {pve['kernel']}")
        print(f"    RAM Used:    {pve['mem_usage']}")
        print(f"    Workloads:   {pve['workloads']}")
        print("    Critical Services:")
        for svc, state in pve.get("critical_services", {}).items():
            icon = "✓" if state == "running" else "✗"
            print(f"      - {svc:<22} [{icon}] {state}")
    else:
        print(f"    Status:      🔴 {pve['status']} ({pve.get('detail')})")

    # 2. UniFi Network
    print("\n[2] UniFi Network:")
    unifi = check_unifi()
    if unifi["status"] == "OK":
        print("    Status:      🟢 OK")
        print(f"    Version:     Network {unifi['version']}")
        print(f"    Topology:    {unifi['networks_count']} Networks/VLANs, {unifi['devices_count']} UniFi Devices")
    else:
        print(f"    Status:      🔴 {unifi['status']} ({unifi.get('detail')})")

    # 3. Hubitat Elevation
    print("\n[3] Hubitat Elevation:")
    hubitat = check_hubitat()
    if hubitat["status"] == "OK":
        print("    Status:      🟢 OK")
        print(f"    Host:        {hubitat['host']} (Maker API active)")
        print(f"    Devices:     {hubitat['device_count']} connected smart devices")
    else:
        print(f"    Status:      🔴 {hubitat['status']} ({hubitat.get('detail')})")

    print("\n" + "=" * 65)

if __name__ == "__main__":
    main()
