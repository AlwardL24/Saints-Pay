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
