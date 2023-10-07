import sys


def sadf(format: str):
    if sys.platform == "win32":
        return format.replace("%-", "%#")
    else:
        return format.replace("%#", "%-")
