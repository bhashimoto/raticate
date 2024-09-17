import base64
from io import BytesIO
import qrcode
from crc import Calculator, Crc16

def generate_pix_qr(key, amount, name, city):
    merchant_account_info = "0014br.gov.bcb.pix" + f"01{add_length(key)}"
    amount_string = f"{amount:.2f}"
    pre_crc = f"00020126" + add_length(merchant_account_info) + "52040000530398654" + add_length(amount_string) + "5802BR59" + add_length(name) +"60" + add_length(city) + "6304"
    
    calculator = Calculator(Crc16.IBM_3740)
    cs = calculator.checksum(pre_crc.encode())

    code = pre_crc + hex(cs).encode().decode()[2:].upper()
    img = qrcode.make(code)
    buffered = BytesIO()
    img.save(buffered)
    img_string = base64.b64encode(buffered.getvalue())
    ret = {
        "code": code,
        "image": img_string.decode(),
    }
    return ret 


def add_length(string):
    return f"{len(string):02d}{string}"