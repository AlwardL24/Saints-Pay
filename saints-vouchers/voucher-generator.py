from io import BytesIO

from barcode import EAN13
from barcode.writer import SVGWriter

import random

def generate():
    code = random.randint(100000000000, 999999999999)
    with open(f"saints-vouchers/vouchers/barcode_{code}.svg", "wb") as f:
        EAN13(str(code), writer=SVGWriter()).write(f)

    with open("saints-vouchers/active-vouchers.txt", "a") as f:
        f.write(f"{code}\n")

while True:
    input("Press enter to generate another code...")
    generate()
