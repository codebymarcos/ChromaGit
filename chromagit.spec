# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ChromaGit
Compila o projeto completo em um executável standalone
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Coletar todos os submódulos necessários
hidden_imports = [
    # Core modules
    'cli.collor',
    'cli.progress',
    
    # Commands
    'commands.init',
    'commands.camprint',
    'commands.save',
    'commands.new',
    'commands.hub',
    'commands.duple',
    'commands.init_assist',
    
    # Commands noctis_map
    'commands.noctis_map',
    'commands.noctis_map.import',
    'commands.noctis_map.loader',
    'commands.noctis_map.noctis_map',
    'commands.noctis_map.core.ide.ide',
    'commands.noctis_map.core.ide.ide_funct',
    'commands.noctis_map.core.scan.scan',
    'commands.noctis_map.core.view.view',
    'commands.noctis_map.core.view.extend',
    
    # Utils
    'utils.config',
    'utils.ignore',
    
    # ChromaBuddy modules
    'ChromaBuddy.chat',
    'ChromaBuddy.models.cohe',
    'ChromaBuddy.locate.dds',
    'ChromaBuddy.tools.toolshub',
    'ChromaBuddy.tools.new',
    
    # ChromaBuddy core modules
    'ChromaBuddy.core.tokenizer',
    'ChromaBuddy.core.execute',
    'ChromaBuddy.core.test',
    'ChromaBuddy.core.memory',
    'ChromaBuddy.core.test_gen',
    'ChromaBuddy.core.analyzer',
    'ChromaBuddy.core.cache',
    'ChromaBuddy.core.mentions',
    'ChromaBuddy.core.batch',
    'ChromaBuddy.core.docs',
    'ChromaBuddy.core.git',
    'ChromaBuddy.core.performance',
    'ChromaBuddy.core.tools',
    'ChromaBuddy.core.templates',
    'ChromaBuddy.core.config',
    'ChromaBuddy.core.ui',
    'ChromaBuddy.core.deep_think',
    'ChromaBuddy.core.context',
    'ChromaBuddy.core.diff',
    
    # Spark Easy
    'ChromaBuddy.spark_easy',
    'ChromaBuddy.spark_easy.tool_sys',
    'ChromaBuddy.spark_easy.tool_sys.tool',
    'ChromaBuddy.spark_easy.decisor',
    'ChromaBuddy.spark_easy.decisor.decisor',
    
    # Third-party dependencies
    'cohere',
    'rich',
    'rich.console',
    'rich.panel',
    'rich.syntax',
    'rich.spinner',
    'rich.progress',
    'rich.table',
    'rich.markdown',
    'ast',
    'json',
    'pathlib',
    'subprocess',
    'shutil',
]

# Coletar data files (configs, templates, etc)
datas = [
    ('ChromaBuddy/config.json', 'ChromaBuddy/'),
    ('favicon.ico', '.'),
]

# Coletar todos os __init__.py
def collect_init_files(base_path):
    """Coleta todos os arquivos __init__.py para incluir na build"""
    init_files = []
    for root, dirs, files in os.walk(base_path):
        # Ignorar __pycache__ e .git
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv']]
        
        if '__init__.py' in files:
            rel_path = os.path.relpath(root, base_path)
            init_file = os.path.join(root, '__init__.py')
            dest_folder = rel_path if rel_path != '.' else '.'
            init_files.append((init_file, dest_folder))
    
    return init_files

# Adicionar __init__.py files
if os.path.exists('ChromaBuddy'):
    datas.extend(collect_init_files('ChromaBuddy'))
if os.path.exists('commands'):
    datas.extend(collect_init_files('commands'))
if os.path.exists('cli'):
    datas.extend(collect_init_files('cli'))
if os.path.exists('utils'):
    datas.extend(collect_init_files('utils'))

a = Analysis(
    ['main.py'],
    pathex=['ChromaBuddy'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt5',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='chromagit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',
)
