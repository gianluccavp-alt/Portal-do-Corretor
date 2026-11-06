#!/usr/bin/env python3
"""Converte o extrato do OpenStreetMap (c) colaboradores do OSM, ODbL) para coordenadas da cena.
Ancoragem: as 2 rotatorias da planta casam com as do OSM (erro < 1 m, rotacao 20,76 graus).
Uso: python3 osm_cena.py area.json -> osm_cena.json"""
import json, math, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
LAT0, LON0 = -21.2345, -47.79
A = math.radians(20.76)
def cena(lat, lon):
    e = (lon - LON0) * 111320 * math.cos(math.radians(LAT0)) - 100
    n = (lat - LAT0) * 110574 + 60
    r = e * math.cos(A) - n * math.sin(A)
    u = e * math.sin(A) + n * math.cos(A)
    return (round(u - 141.95, 1), round(514.2 - r, 1))
d = json.load(open(sys.argv[1]))['elements']
out = {'ruas': [], 'predios': [], 'solo': [], 'fileiras': []}
USO = {'residential': 'res', 'farmland': 'campo', 'grass': 'verde', 'forest': 'mata', 'orchard': 'mata', 'industrial': 'ind', 'commercial': 'ind', 'retail': 'ind', 'construction': 'obra', 'cemetery': 'verde', 'recreation_ground': 'verde', 'quarry': 'obra'}
for e in d:
    t, g = e.get('tags', {}), e.get('geometry')
    if not g:
        continue
    p = [cena(q['lat'], q['lon']) for q in g]
    if 'building' in t:
        out['predios'].append({'p': p, 'n': t.get('building:levels'), 'h': t.get('height'), 't': t.get('building')})
    elif 'highway' in t:
        if t['highway'] in ('footway', 'path', 'steps', 'cycleway', 'pedestrian', 'proposed', 'construction', 'track', 'services', 'corridor'):
            continue
        out['ruas'].append({'c': t['highway'], 'p': p, 'j': t.get('junction'), 'n': t.get('name')})
    elif t.get('landuse') in USO:
        out['solo'].append({'u': USO[t['landuse']], 'p': p})
    elif t.get('natural') in ('wood', 'scrub'):
        out['solo'].append({'u': 'mata', 'p': p})
    elif t.get('natural') == 'water':
        out['solo'].append({'u': 'agua', 'p': p})
    elif t.get('natural') == 'tree_row':
        out['fileiras'].append(p)
    elif t.get('leisure') in ('park', 'garden', 'pitch'):
        out['solo'].append({'u': 'verde', 'p': p})
json.dump(out, open(os.path.join(AQUI, 'osm_cena.json'), 'w'), separators=(',', ':'))
print({k: len(v) for k, v in out.items()}, os.path.getsize(os.path.join(AQUI, 'osm_cena.json')))
