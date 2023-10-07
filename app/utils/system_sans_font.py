from sys import platform

normal = ""
bold = ""

if platform == "win32":
    normal = "Segoe UI"
    bold = "Segoe UI Bold"
elif platform == "darwin":
    # normal = "Helvetica"
    # bold = "Helvetica Bold"
    normal = "SF Pro Text"
    bold = "SF Pro Text Bold"
elif platform == "linux":
    normal = "DejaVu Sans"
    bold = "DejaVu Sans Bold"
else:
    normal = "Arial"
    bold = "Arial Bold"

size_multiplier = 1.0

if platform == "win32":
    size_multiplier = 0.8
