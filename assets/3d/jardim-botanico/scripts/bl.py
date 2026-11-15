#!/usr/bin/env python3
"""Envia codigo Python para o add-on MCP oficial do Blender (localhost:9876).
Uso: python3 -I bl.py arquivo.py   (ou codigo via stdin). O codigo preenche o dict `result`.
Antes do codigo, injeta `__file__ = <caminho absoluto do arquivo>`, para os scripts acharem
os caminhos relativos ao repo (tex/, cams_fit.json, gaia.glb...)."""
import json, os, socket, sys
if len(sys.argv) > 1:
    path = os.path.abspath(sys.argv[1])
    code = '__file__ = %r\n' % path + open(path).read()
else:
    code = sys.stdin.read()
s = socket.create_connection(("localhost", 9876), timeout=1800)
s.sendall(json.dumps({"type": "execute", "code": code, "strict_json": False}).encode() + b"\0")
buf = b""
while not buf.endswith(b"\0"):
    chunk = s.recv(65536)
    if not chunk: break
    buf += chunk
print(json.dumps(json.loads(buf.rstrip(b"\0")), ensure_ascii=False, indent=1)[:20000])
