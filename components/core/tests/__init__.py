import os
import sys

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, f"..{os.path.sep}..{os.path.sep}..{os.path.sep}ptbtest")
sys.path.append(filename)
