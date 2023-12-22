
# spencer
# 2023/12/12

import asyncio
import time

async def do_work(s: str, delay: int=5):
    print(f"start {s}")
    await asyncio.sleep(delay)
    #time.sleep(delay)
    print(f"end {s}")

async def main():
    start = time.perf_counter()

    todo = ['get_peckage', 'loundry', 'baking_cake']

    # for item in todo:
    #     await do_work(item, 1)
    
    tasks = [asyncio.create_task(do_work(item)) for item in todo]
    done, pending = await asyncio.wait(tasks, timeout=20)

    batch = asyncio.gather(do_work('lala'), do_work('lala'))
    r1, r2 = await batch

    end = time.perf_counter()
    print(f"total time: {end - start}s")

if __name__ == '__main__':
    asyncio.run(main())