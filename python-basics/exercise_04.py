

JsonValue = str | int | float | bool | None

def return_values(json_records: dict[int, JsonValue], key: int):
    return json_records.get(key)

values = { 1: "Lalit", 2: "Radiohead", 3: "orion"}

print(return_values(values, 1))