from typing import Any
from collections.abc import Callable
from functools import wraps

def required_role(role:str):
    def middle_func(function: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(function)
        def wrapper(*args:Any, **kwargs:Any) -> Any:
            if role == kwargs.get("current_role"):
                print("verified")
                return function(*args, **kwargs)
            else:
                raise ValueError("Sorry! admin is required to verify this")
        return wrapper
    return middle_func

@required_role("admin")
def delete_user(username, current_role:str):
    print(f"{username} deleted")
    
delete_user("codesterlalit", current_role="admin")
                