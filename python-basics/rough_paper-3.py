from dataclasses import dataclass
from collections.abc import Callable
import time

@dataclass
class Request:
    user: str
    
@dataclass
class Response:
    msg: str

def core_app(req: Request) -> Response:
    return Response(msg=f"Hello, {req.user}!")

def auth_middleware(req: Request, next_stage: Callable[[Request], Response]) -> Response:
    if req.user == "anonymous":
        return Response(msg="401 Unauthorized")
    return next_stage(req)

def log_middleware(req: Request, next_stage: Callable[[Request], Response]) -> Response:
    print(f"[LOG] Processing for {req.user}")
    res = next_stage(req)
    print(f"[LOG] Done: {res.msg}")
    return res

def timing_middleware(req: Request, next_stage: Callable[[Request], Response]) -> Response:
    start = time.perf_counter()
    res = next_stage(req)
    total_time = time.perf_counter() - start
    print(f"[TIMING] total time taken: {total_time: .2f}")
    return res

def build_pipeline(
    handler: Callable[[Request], Response],
    middlewares: list[Callable[[Request, Callable[[Request], Response]], Response]]
) -> Callable[[Request], Response]:
    
    current_handler = handler
    
    for mw in reversed(middlewares):
        next_fn = current_handler
        
        def wrapped(
            req: Request,
            m: Callable[[Request, Callable[[Request], Response]], Response] = mw,
            n: Callable[[Request], Response] = next_fn
        ) -> Response:
            return m(req, n)
        
        current_handler = wrapped
    return current_handler

pipeline = build_pipeline(
    handler=core_app,
    middlewares=[log_middleware, auth_middleware, timing_middleware]
)

print("--- Test 1: Authorized User ---")
print(pipeline(Request("Alice")))

print("\n--- TEST 2: Anonymous User ---")
print(pipeline(Request("anonymous")))