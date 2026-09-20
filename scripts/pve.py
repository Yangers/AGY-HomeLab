#!/usr/bin/env python3
"""
Proxmox VE Command-Line Utility for AGY-HomeLab
Supports inspection, inventory, storage checks, and safe workload control.
"""

import sys
import os
import argparse
import json
import urllib3
import requests
from pathlib import Path

# Suppress TLS warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CRITICAL_VMIDS = {102, 105, 107, 109}  # PiHoles, Vaultwarden, Nginx Proxy Manager

def load_env():
    """Load environment variables from config.env or .env if present."""
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

class ProxmoxClient:
    def __init__(self):
        load_env()
        self.host = os.environ.get("PROXMOX_HOST", "https://10.98.10.5:8006").rstrip("/")
        self.node = os.environ.get("PROXMOX_NODE", "proxmox-yp")
        token_id = os.environ.get("PROXMOX_TOKEN_ID", "mcp-user@pam!mcp")
        token_secret = os.environ.get("PROXMOX_TOKEN_SECRET", "")
        
        if not token_secret:
            print("Error: PROXMOX_TOKEN_SECRET not set in environment or config.env", file=sys.stderr)
            sys.exit(1)
            
        self.headers = {
            "Authorization": f"PVEAPIToken={token_id}={token_secret}",
            "Accept": "application/json"
        }
        self.verify = False

    def get(self, endpoint, params=None):
        url = f"{self.host}/api2/json/{endpoint.lstrip('/')}"
        try:
            r = requests.get(url, headers=self.headers, params=params, verify=self.verify, timeout=10)
            r.raise_for_status()
            return r.json().get("data")
        except requests.exceptions.RequestException as e:
            print(f"API Request Failed [{endpoint}]: {e}", file=sys.stderr)
            sys.exit(1)

    def post(self, endpoint, data=None):
        url = f"{self.host}/api2/json/{endpoint.lstrip('/')}"
        try:
            r = requests.post(url, headers=self.headers, json=data, verify=self.verify, timeout=15)
            r.raise_for_status()
            return r.json().get("data")
        except requests.exceptions.RequestException as e:
            print(f"API Request Failed [{endpoint}]: {e}", file=sys.stderr)
            sys.exit(1)

    def find_workload_type(self, vmid):
        """Determine whether VMID is 'lxc' or 'qemu'."""
        lxcs = self.get(f"nodes/{self.node}/lxc")
        for ct in lxcs:
            if int(ct["vmid"]) == vmid:
                return "lxc", ct["name"]
        vms = self.get(f"nodes/{self.node}/qemu")
        for vm in vms:
            if int(vm["vmid"]) == vmid:
                return "qemu", vm.get("name", "VM")
        return None, None

def format_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024.0:
            return f"{b:.1f} {unit}"
        b /= 1024.0
    return f"{b:.1f} PB"

def cmd_status(client, args):
    status = client.get(f"nodes/{client.node}/status")
    version = client.get("version")
    
    cpu_model = status.get("cpuinfo", {}).get("model", "Unknown")
    cpus = status.get("cpuinfo", {}).get("cpus", 0)
    cores = status.get("cpuinfo", {}).get("cores", 0)
    cpu_usage = status.get("cpu", 0) * 100
    
    mem = status.get("memory", {})
    mem_total = mem.get("total", 0)
    mem_used = mem.get("used", 0)
    mem_free = mem.get("free", 0)
    mem_pct = (mem_used / mem_total * 100) if mem_total else 0
    
    uptime_days = status.get("uptime", 0) / 86400
    loadavg = ", ".join(str(x) for x in status.get("loadavg", []))
    
    print("=" * 65)
    print(f" Proxmox VE Node: {client.node} (PVE {version.get('version')})")
    print("=" * 65)
    print(f" CPU:         {cpu_model} ({cores} cores, {cpus} threads)")
    print(f" CPU Usage:   {cpu_usage:.1f}%")
    print(f" Load Avg:    {loadavg}")
    print(f" Memory:      {format_bytes(mem_used)} / {format_bytes(mem_total)} ({mem_pct:.1f}% used) | Free: {format_bytes(mem_free)}")
    print(f" Kernel:      {status.get('kversion', 'Unknown')}")
    print(f" Uptime:      {uptime_days:.1f} days")
    print("=" * 65)

def cmd_list(client, args):
    lxcs = client.get(f"nodes/{client.node}/lxc")
    vms = client.get(f"nodes/{client.node}/qemu")
    
    all_workloads = []
    for ct in lxcs:
        all_workloads.append({
            "vmid": int(ct["vmid"]),
            "name": ct.get("name", ""),
            "type": "LXC",
            "status": ct.get("status", "unknown"),
            "cpus": ct.get("cpus", 0),
            "mem_used": ct.get("mem", 0),
            "mem_max": ct.get("maxmem", 0),
            "tags": ct.get("tags", "")
        })
    for vm in vms:
        all_workloads.append({
            "vmid": int(vm["vmid"]),
            "name": vm.get("name", ""),
            "type": "QEMU",
            "status": vm.get("status", "unknown"),
            "cpus": vm.get("cpus", 0),
            "mem_used": vm.get("mem", 0),
            "mem_max": vm.get("maxmem", 0),
            "tags": vm.get("tags", "")
        })
        
    all_workloads.sort(key=lambda x: x["vmid"])
    
    print(f"{'VMID':<6} {'NAME':<20} {'TYPE':<6} {'STATUS':<9} {'vCPU':<5} {'MEM (USED/MAX)':<18} {'TAGS'}")
    print("-" * 80)
    for w in all_workloads:
        mem_str = f"{format_bytes(w['mem_used'])} / {format_bytes(w['mem_max'])}"
        status_marker = "● " + w["status"] if w["status"] == "running" else "○ " + w["status"]
        crit = " [CRITICAL]" if w["vmid"] in CRITICAL_VMIDS else ""
        print(f"{w['vmid']:<6} {w['name']:<20} {w['type']:<6} {status_marker:<9} {w['cpus']:<5} {mem_str:<18} {w['tags']}{crit}")

def cmd_storage(client, args):
    storages = client.get(f"nodes/{client.node}/storage")
    print(f"{'STORAGE':<22} {'TYPE':<10} {'STATUS':<8} {'USED / TOTAL':<22} {'USAGE %':<8} {'CONTENT'}")
    print("-" * 88)
    for s in storages:
        used = s.get("used", 0)
        total = s.get("total", 0)
        pct = (s.get("used_fraction", 0) * 100)
        active = "Active" if s.get("active") == 1 else "Inactive"
        used_total_str = f"{format_bytes(used)} / {format_bytes(total)}" if total > 0 else "N/A"
        print(f"{s['storage']:<22} {s.get('type', ''):<10} {active:<8} {used_total_str:<22} {pct:5.1f}%  {s.get('content', '')}")

def cmd_action(client, args, action_name):
    vmid = args.vmid
    w_type, name = client.find_workload_type(vmid)
    if not w_type:
        print(f"Error: Workload ID {vmid} not found on node {client.node}", file=sys.stderr)
        sys.exit(1)
        
    if vmid in CRITICAL_VMIDS and action_name in ["stop", "reboot"] and not args.force:
        print(f"BLOCKED: Workload {vmid} ({name}) is a protected CRITICAL service!", file=sys.stderr)
        print("To proceed, you must pass the --force flag.", file=sys.stderr)
        sys.exit(2)
        
    print(f"Executing '{action_name}' on {w_type.upper()} {vmid} ({name})...")
    res = client.post(f"nodes/{client.node}/{w_type}/{vmid}/status/{action_name}")
    print(f"Task dispatched: UPID = {res}")

def cmd_snapshot(client, args):
    vmid = args.vmid
    snapname = args.snapname
    w_type, name = client.find_workload_type(vmid)
    if not w_type:
        print(f"Error: Workload ID {vmid} not found", file=sys.stderr)
        sys.exit(1)
        
    payload = {"snapname": snapname}
    if args.description:
        payload["description"] = args.description
        
    print(f"Creating snapshot '{snapname}' for {w_type.upper()} {vmid} ({name})...")
    res = client.post(f"nodes/{client.node}/{w_type}/{vmid}/snapshot", data=payload)
    print(f"Task dispatched: UPID = {res}")

def cmd_snapshots(client, args):
    vmid = args.vmid
    w_type, name = client.find_workload_type(vmid)
    if not w_type:
        print(f"Error: Workload ID {vmid} not found", file=sys.stderr)
        sys.exit(1)
        
    snaps = client.get(f"nodes/{client.node}/{w_type}/{vmid}/snapshot")
    print(f"Snapshots for {w_type.upper()} {vmid} ({name}):")
    print(f"{'NAME':<20} {'DATE':<22} {'DESCRIPTION'}")
    print("-" * 65)
    for s in snaps:
        if s.get("name") == "current":
            continue
        snap_time = s.get("snaptime", "N/A")
        print(f"{s.get('name', ''):<20} {str(snap_time):<22} {s.get('description', '')}")

def main():
    parser = argparse.ArgumentParser(description="AGY HomeLab Proxmox VE CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Status
    p_status = subparsers.add_parser("status", help="Show node health and hardware status")
    p_status.set_defaults(func=cmd_status)

    # List
    p_list = subparsers.add_parser("list", help="List all LXCs and VMs")
    p_list.set_defaults(func=cmd_list)

    # Storage
    p_storage = subparsers.add_parser("storage", help="List all storage pools and disk space")
    p_storage.set_defaults(func=cmd_storage)

    # Lifecycle commands
    for action in ["start", "stop", "reboot"]:
        p_act = subparsers.add_parser(action, help=f"{action.capitalize()} a workload")
        p_act.add_argument("vmid", type=int, help="Target VMID")
        p_act.add_argument("--force", action="store_true", help="Force action on critical services")
        p_act.set_defaults(func=lambda client, args, a=action: cmd_action(client, args, a))

    # Snapshot commands
    p_snap = subparsers.add_parser("snapshot", help="Create a snapshot for a workload")
    p_snap.add_argument("vmid", type=int, help="Target VMID")
    p_snap.add_argument("snapname", type=str, help="Snapshot name")
    p_snap.add_argument("--description", "-d", type=str, default="", help="Snapshot description")
    p_snap.set_defaults(func=cmd_snapshot)

    p_snaps = subparsers.add_parser("snapshots", help="List snapshots for a workload")
    p_snaps.add_argument("vmid", type=int, help="Target VMID")
    p_snaps.set_defaults(func=cmd_snapshots)

    args = parser.parse_args()
    client = ProxmoxClient()
    args.func(client, args)

if __name__ == "__main__":
    main()
