# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['tianqi.py'],
             pathex=['E:\\weiqi_self'],
             binaries=[],
             datas=['Pictures\B.png','Pictures\BD-13.png','Pictures\BU-13.png','Pictures\W.png','Pictures\WD-13.png','Pictures\WU-13.png','Pictures\preview1.gif'],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='tianqi',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
