from collections.abc import Callable

Validator = Callable[[int], bool]

Parser = Callable[[str], int]

list_of_string = ["testing", "name", "what", "not"]

def full_process(list_string: list[str], parser: Parser, validator: Validator)-> list[bool]:
    firstProcess = [parser(string) for string in list_string]
    return [validator(process) for process in firstProcess]

def parser(value: str)-> int:
    return len(value)

def validator(value:int) -> bool:
    return value%2 == 0

final_product = full_process(list_of_string, parser=parser, validator=validator)

for product in final_product:
    print(product)