# PyInstaller spec executed only on a native Windows runner
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
hiddenimports=collect_submodules('PySide6')
datas=collect_data_files('PySide6')
a=Analysis(['app/best_buds_weight_station/__main__.py'],pathex=['app'],binaries=[],datas=datas,hiddenimports=hiddenimports)
pyz=PYZ(a.pure); exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='BestBudsWeightStation',console=False); coll=COLLECT(exe,a.binaries,a.datas,name='BestBudsWeightStation')
