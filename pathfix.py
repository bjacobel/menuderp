import os, sys
base = os.path.dirname(os.path.dirname("menuwatch/settings/prod.py"))
base_parent = os.path.dirname(base)
sys.path.append(base)
sys.path.append(base_parent)
print(":".join(sys.path))
