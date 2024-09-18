import base64
from io import BytesIO
import qrcode
from crc import Calculator, Crc16
import re

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

def validate_key(key:str) -> tuple[bool, str]: 
    """Checks if the given string is a valid pix key and returns the key correctly formatted.
    
    Returns: (valid:bool, formatted_key:str)
    """
    result = validate_key_CPF(key)
    if result[0]:
        return result
    result = validate_key_phone(key)
    if result[0]:
        return result
    result = validate_key_random(key)
    if result[0]:
        return result
    result = validate_key_email(key)
    if result[0]:
        return result
    result = validate_key_cnpj(key)
    if result[0]:
        return result
    
    return (False, "")

def validate_key_CPF(key:str) -> tuple[bool, str]:
    invalid = (False, "")
    treated = re.sub("[^0-9]","", key)
    if len(treated) != 11:
        return invalid 
    
    if treated in [s*11 for s in [str(n) for n in range(10)]]:
        return invalid
    
    weights = [i for i in range(2,12)]

    r1 = (sum([int(a)*b for a,b in zip(reversed(treated[:-2]), weights[:-1])]) % 11)
    d1 = 0 if (r1 < 2) else (11 - r1)
    r2 = (sum([int(a)*b for a,b in zip(reversed(treated[:-1]), weights)]) % 11)
    d2 = 0 if (r2 < 2) else (11 - r2)

    if str(d1) != treated[-2] or str(d2) != treated[-1]:
        return invalid
    
    return (True, treated)

def validate_key_phone(key:str) -> tuple[bool, str]:
    treated = re.sub("[^0-9]", "", key)

    if len(treated) != 11:
        return (False, "")

    ddd = ['11', '12', '13', '14', '15', '16', '17', '18', '19',
           '21', '22', '24', '27', '28',
           '31', '32', '33', '34', '35', '37', '38',
           '41', '42', '43', '44', '45', '46', '47', '48', '49',
           '51', '53', '54', '55',
           '61', '62', '63', '64', '65', '66', '67', '68', '69',
           '71', '73', '74', '75', '77', '79',
           '81', '82', '83', '84', '85', '86', '87', '88', '89',
           '91', '92', '93', '94', '95', '96', '97', '98', '99',
           ]

    # not a valid cell phone
    if treated[2] != '9' or treated[0:2] not in ddd:
        return (False, "")
    

    return (True, "+55" + treated)

def validate_key_random(key:str) -> tuple[bool, str]:
    treated = re.sub("[^0-9A-Za-z\-]","", key)
    pattern = r'[0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12}'
    if not re.match(pattern, treated):
        return (False, "")
    return (True, treated)

def validate_key_email(key:str) -> tuple[bool, str]:
    invalid = (False, "")
    treated = key.strip()
    parts = treated.split('@')
    if len(parts) != 2:
        return invalid
    local_pattern = r"^[A-Za-z0-9!#$%&'*+-/=?^_`{|}~.]"

    if not re.match(local_pattern, parts[0]):
        return invalid

    if ".." in key:
        return invalid

    domain_pattern = r"^[A-Za-z0-9\-.]"
    if not re.match(domain_pattern, parts[1]):
        return invalid

    if '.' not in parts[1]:
        return invalid
    
    return (True, treated)

def validate_key_cnpj(key:str) -> tuple[bool, str]:
    treated = re.sub("[^0-9]", "", key)
    invalid = (False, "")
    if len(treated) != 14:
        return invalid

    weights_d1 = [5,4,3,2,9,8,7,6,5,4,3,2]
    weights_d2 = [6,5,4,3,2,9,8,7,6,5,4,3,2]

    r1 = sum([int(a)*b for a,b in zip(treated[:-2], weights_d1)]) % 11
    d1 = 0 if r1 < 2 else (11 - r1)
    r2 = sum([int(a)*b for a,b in zip(treated[:-1], weights_d2)]) % 11
    d2 = 0 if r2 < 2 else (11 - r2)

    if str(d1) != treated[-2] or str(d2) != treated[-1]:
        return invalid
    
    return (True, treated)

def add_length(string):
    return f"{len(string):02d}{string}"