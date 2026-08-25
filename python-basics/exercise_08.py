def parse_port(value: str) -> int:
    port = int(value)
    
    if not 1 <= port <=65535:
        raise ValueError("Port must be between 1 and 65535")
    return port

def load_port(value: str) -> tuple[int | None, str | None]:
    try:
        return parse_port(value), None
    except ValueError as error:
        return None, str(error)

print(load_port(""))
print(load_port("abc"))
print(load_port("0"))
print(load_port("-10"))
print(load_port("65535"))
print(load_port("65536"))