import sys
import os

# Chemin vers votre application (à adapter avec votre username PythonAnywhere)
path = '/home/sandy54/Analyse'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
