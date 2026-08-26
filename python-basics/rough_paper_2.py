def describe_item(*args, **kwargs):
    print("args (tuple):", args)
    print("kwargs (dict):", kwargs)

describe_item("Apple", "Banana", category="Fruit", price=1.50)