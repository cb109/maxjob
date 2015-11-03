# -*- mode: python -*-
a = Analysis(['maxjob/_maxjob.py'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

# 2.1 syntax is different from 3.0: (<trg>, <src>, <type>)
a.datas += [('backend.ms', 'maxjob/backend.ms', 'DATA')]

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='maxjob.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True, icon='misc/max.ico')
