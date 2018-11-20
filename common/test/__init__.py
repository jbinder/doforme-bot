import os
import sys

dirname = os.path.dirname(__file__)
lib_dirname = os.path.join(dirname, f"..{os.path.sep}..{os.path.sep}libraries{os.path.sep}ptbtest")
sys.path.append(lib_dirname)
