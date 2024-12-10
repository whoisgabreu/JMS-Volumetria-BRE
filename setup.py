import sys
import os
from cx_Freeze import setup, Executable

sys.setrecursionlimit(3000)

base = None
if sys.platform == "win32":
    base = "Win32GUI"

assets = os.path.join(os.path.dirname(__file__),"assets")

build_options = {
    "packages": [], 
    "excludes": [],
    "include_files": [assets]
    }

setup(
    name = "Volumetria Tronco BRE",
    version="1.0",
    description="Volumetria Tronco BRE by Gabreu",
    executables=[Executable(r"C:\Users\1887\OneDrive - J&T EXPRESS BRAZIL LTDA\Área de Trabalho\Projetos\Ajudando Osotto\TIME PLANEJAS\Previsão Volumetria (HTTP Requests)\Troncal BRE\main.py", base=base, icon=None)],
    options={"build_exe": build_options}
)