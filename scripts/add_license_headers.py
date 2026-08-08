#!/usr/bin/env python3
"""Ajout des en-têtes de licence - SMART_AO V7"""
from pathlib import Path

LICENSE = '''"""
SMART_AO V7 - {filename}
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""
'''

BASE = Path('/home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST 4/SMART_AO_V7')
SKIP_DIRS = ['venv', '__pycache__', '.git', 'node_modules']
SKIP_FILES = ['add_license_headers.py']

def needs_header(fp):
    if not fp.name.endswith('.py'):
        return False
    if any(s in str(fp) for s in SKIP_DIRS + SKIP_FILES):
        return False
    try:
        content = fp.read_text()
        return not ('SMART_AO V7' in content[:300] and 'Copyright' in content[:300])
    except:
        return False

files = [f for f in BASE.rglob('*') if f.is_file() and needs_header(f)]
print(f"Fichiers à corriger: {len(files)}")

for i, f in enumerate(files, 1):
    try:
        content = f.read_text()
        header = LICENSE.format(filename=f.name)
        f.write_text(header + '\n' + content)
        print(f"  ✅ {i}/{len(files)}: {f.relative_to(BASE)}")
    except Exception as e:
        print(f"  ❌ {i}/{len(files)}: {f.relative_to(BASE)} - {e}")

print(f"\n✅ {len(files)} fichiers corrigés")
