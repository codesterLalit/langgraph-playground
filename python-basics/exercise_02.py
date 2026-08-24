def run_pipeline(values, steps):
    return_list = []
    for value in values:
        for step in steps:
            value = step(value)
        return_list.append(value)
    return return_list



new_thing = run_pipeline([" test thing. ", "     testing"], [lambda x: x.strip(), lambda x: x.lower(), lambda x: f"{x}!"])
print(new_thing)