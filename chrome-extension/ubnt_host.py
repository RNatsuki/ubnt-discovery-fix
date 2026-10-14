#!/usr/bin/env python3
"""
Ubiquiti Device Discovery - Native Messaging Host & CLI Scanner
Maneja el protocolo de descubrimiento UDP de Ubiquiti (puerto 10001)
y se comunica con la extension de Chrome mediante Chrome Native Messaging.
"""

import sys
import os
import json
import socket
import struct
import select
import time
import subprocess
import re

LOG_FILE = "/tmp/ubnt_discovery_host.log"

def log(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def get_broadcast_addresses():
    bcasts = {"255.255.255.255", "233.89.188.1"}
    try:
        out = subprocess.check_output(["ip", "-o", "-4", "addr", "show"], text=True)
        for line in out.splitlines():
            m = re.search(r"brd\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", line)
            if m:
                bcasts.add(m.group(1))
    except Exception as e:
        log(f"Error getting broadcast addresses via ip: {e}")
    return sorted(list(bcasts))

def format_mac(raw_bytes):
    if len(raw_bytes) == 6:
        return ":".join(f"{b:02X}" for b in raw_bytes)
    return raw_bytes.hex()

def format_ip(raw_bytes):
    if len(raw_bytes) == 4:
        return ".".join(str(b) for b in raw_bytes)
    return str(raw_bytes)

def parse_ubnt_packet(data, source_ip):
    if len(data) < 4:
        return None
    version = data[0]
    cmd = data[1]
    
    device = {
        "source_ip": source_ip,
        "mac": None,
        "ip": source_ip,
        "hostname": "UBNT",
        "platform": "",
        "model": "Ubiquiti Device",
        "firmware": "",
        "uptime": 0,
        "essid": "",
        "wmode": None,
        "is_default": False,
        "interfaces": []
    }

    idx = 4
    while idx < len(data):
        if idx + 3 > len(data):
            break
        t = data[idx]
        length = struct.unpack(">H", data[idx+1:idx+3])[0]
        idx += 3
        if idx + length > len(data):
            break
        val = data[idx:idx+length]
        idx += length

        try:
            if t == 0x01: # Hardware address (MAC)
                device["mac"] = format_mac(val)
            elif t == 0x02: # MAC + IP info
                if len(val) >= 10:
                    iface_mac = format_mac(val[:6])
                    iface_ip = format_ip(val[6:10])
                    device["interfaces"].append({"mac": iface_mac, "ip": iface_ip})
                    if not device["mac"]:
                        device["mac"] = iface_mac
                    if device["ip"] == source_ip or device["ip"] is None:
                        device["ip"] = iface_ip
            elif t == 0x03: # Firmware
                device["firmware"] = val.decode("latin1", "ignore").strip()
            elif t == 0x0A: # Uptime
                if len(val) == 4:
                    device["uptime"] = struct.unpack(">I", val)[0]
                elif len(val) == 8:
                    device["uptime"] = struct.unpack(">Q", val)[0]
            elif t == 0x0B: # Hostname
                device["hostname"] = val.decode("utf-8", "ignore").strip()
            elif t == 0x0C: # Platform
                device["platform"] = val.decode("utf-8", "ignore").strip()
            elif t == 0x0D: # ESSID
                device["essid"] = val.decode("utf-8", "ignore").strip()
            elif t == 0x0E: # Wireless mode
                if len(val) == 1:
                    device["wmode"] = val[0]
            elif t in (0x14, 0x15): # Full model name
                device["model"] = val.decode("utf-8", "ignore").strip()
            elif t == 0x17: # Is default
                if len(val) >= 1:
                    device["is_default"] = bool(val[0])
        except Exception as e:
            log(f"Error parsing TLV 0x{t:02x}: {e}")

    # Si el modelo no venia explicitamente en TLV 0x14/0x15, usamos la plataforma
    if device["model"] == "Ubiquiti Device" and device["platform"]:
        device["model"] = device["platform"]

    # Si hay interfaces pero device["ip"] todavia coincide con source_ip o queremos la ip mas directa
    if device["interfaces"]:
        # preferir la que coincida con la subred de origen o la primera
        matching = [i["ip"] for i in device["interfaces"] if i["ip"] == source_ip]
        if matching:
            device["ip"] = matching[0]
        else:
            device["ip"] = device["interfaces"][0]["ip"]

    return device

def scan_network(timeout_sec=2.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(False)
    
    # Intentar bind a puerto 0 para recibir respuestas
    try:
        sock.bind(("", 0))
    except Exception as e:
        log(f"Socket bind error: {e}")

    targets = get_broadcast_addresses()
    req_v1 = b"\x01\x00\x00\x00"
    req_v2 = b"\x02\x00\x00\x00"

    for bcast in targets:
        try:
            sock.sendto(req_v1, (bcast, 10001))
            sock.sendto(req_v2, (bcast, 10001))
        except Exception:
            pass

    devices_by_mac = {}
    start_time = time.time()

    while time.time() - start_time < timeout_sec:
        r, _, _ = select.select([sock], [], [], 0.3)
        if r:
            try:
                data, addr = sock.recvfrom(4096)
                dev = parse_ubnt_packet(data, addr[0])
                if dev and dev["mac"]:
                    devices_by_mac[dev["mac"]] = dev
            except Exception as e:
                log(f"Socket recv error: {e}")
                break

    sock.close()
    return list(devices_by_mac.values())

# ----------------- Chrome Native Messaging IO -----------------

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length or len(raw_length) < 4:
        return None
    message_length = struct.unpack("@I", raw_length)[0]
    raw_message = sys.stdin.buffer.read(message_length)
    if not raw_message or len(raw_message) < message_length:
        return None
    return json.loads(raw_message.decode("utf-8"))

def send_message(message_dict):
    encoded = json.dumps(message_dict).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("@I", len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "--scan"):
        print("Escaneando red local para dispositivos Ubiquiti (UDP 10001)...")
        results = scan_network(timeout_sec=3.0)
        print(f"\nDispositivos encontrados: {len(results)}\n" + "="*70)
        for d in results:
            print(f"IP:        {d['ip']}")
            print(f"MAC:       {d['mac']}")
            print(f"Hostname:  {d['hostname']}")
            print(f"Modelo:    {d['model']}")
            print(f"Firmware:  {d['firmware']}")
            print(f"ESSID:     {d['essid']}")
            print(f"Uptime:    {d['uptime']} s")
            print(f"Interfaces:{d['interfaces']}")
            print("-" * 70)
        return

    log("Host iniciado por Chrome")
    while True:
        try:
            msg = read_message()
            if msg is None:
                log("EOF o conexion cerrada por Chrome")
                break
            
            action = msg.get("action", "scan")
            if action == "ping":
                send_message({"status": "ok", "version": "1.0.0"})
            elif action == "scan":
                timeout = float(msg.get("timeout", 2.5))
                devs = scan_network(timeout_sec=timeout)
                send_message({"status": "ok", "action": "scan_result", "devices": devs})
            else:
                send_message({"status": "error", "message": f"Accion desconocida: {action}"})
        except Exception as e:
            log(f"Error en bucle principal: {e}")
            send_message({"status": "error", "message": str(e)})
            break

if __name__ == "__main__":
    main()
