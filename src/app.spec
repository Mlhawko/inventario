# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('static', 'static'),
    ('templates', 'templates'),

]

a = Analysis(['app.py'],
             pathex=['C:\\ProyectosPython\\Inventario'],  # Ajusta esta ruta según tu directorio base
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='InventarioCHF',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='InventarioCHF')
