import asyncio
import time

async def fake_service(name: str, delay:float) -> str:
    await asyncio.sleep(delay)
    return f"{name} - delay: {delay}"


async def sequential_calls() -> list[str]:
    results = []
    
    results.append(await fake_service("google gemini", 4))
    results.append(await fake_service("chatgpt", 1))
    results.append(await fake_service("claude", 2))
    
    return results

async def concurrent_calls() -> list[str]:
    result =  await asyncio.gather(
        fake_service("google gemini", 4),
        fake_service("chatgpt", 1),
        fake_service("claude", 2)
    )
    
    return list(result)

async def group() -> list[str]:
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fake_service("Gemini", 4))
        task2 = tg.create_task(fake_service("Chatgpt", 1))
        task3 = tg.create_task(fake_service("Claude", 2))
    return [task1.result(), task2.result(), task3.result()]

async def main() -> None:
    start  = time.perf_counter()
    sequential_results = await sequential_calls()
    sequential_time = time.perf_counter() - start
    
    start = time.perf_counter()
    concurrent_results = await concurrent_calls()
    concurrent_time = time.perf_counter() - start
    
    start  = time.perf_counter()
    group_exec_result = await group()
    group_time = time.perf_counter() - start
    
    
    print(f"Sequential results: {sequential_results}")
    print(f"Sequential time: {sequential_time:.2f} secons ")
    
    print(f"concurrent results: {concurrent_results}")
    print(f"concurrent time: {concurrent_time: .2f} seconds")
    
    # test
    print(f"Group result: {group_exec_result}")
    print(f"group timeL {group_time:.2f}")
        
asyncio.run(main())