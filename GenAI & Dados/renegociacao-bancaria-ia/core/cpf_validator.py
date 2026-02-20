import re

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()
