# spencer
# 2023/12/12
# Asyncio basic example

# Nos n de multiplas thereads ou processers para esperar o tempo passar !

import asyncio
import time


async def do_work(s: str, delay: int = 5):
    print(f"start {s}")
    await asyncio.sleep(delay)
    print(f"end {s}")


async def main():


    todo = ['get_peckage', 'loundry', 'baking_cake']

    print('-------- 1. Modo de fazer -------------')
    # Dessa forma ele executa uma por uma
    # Sempre espera a primeira terminar para executar a segunda
    start = time.perf_counter()
    for item in todo:
        await do_work(item)
    print(f"total time: {time.perf_counter() - start}s")
    print('--------\ --------------- /------------')



    print('-------- 2. Modo de fazer -------------')
    # Dessa forma ele cria todas as tarefas antes, e dps espera elas terminarem todas terminarem de maneira assincrona
    # asyncio.wait
    # Supports waiting to be stopped after the first task is done, or after a specified timeout, allowing lower level precision of operations:
    # Essa maneira é mais low level
    start = time.perf_counter()
    # Estou Crinado as tarefas aqui, mas sem executa-las
    tasks = [asyncio.create_task(do_work(item)) for item in todo]

    # Ele retornas as tarefas que foram executadas e as que ficaram pendentes devido ao timeout
    done, pending = await asyncio.wait(tasks, timeout=20)
    print(f"total time: {time.perf_counter() - start}s")
    print('--------\ --------------- /------------')



    print('-------- 3. Modo de fazer -------------')
    # asyncio.gather
    # Returns a Future instance, allowing high level grouping of tasks
    # Outro ponto dessa abordagem é ser resiliente a erros, se uma das tarefas falhar, as outras continuam sendo executadas

    start = time.perf_counter()
    tarefas = [do_work(item) for item in todo]
    batch = asyncio.gather(*tarefas, return_exceptions=True)
    resultados = await batch
    print(f"total time: {time.perf_counter() - start}s")
    print('--------\ --------------- /------------')

    # print('-------- 4. Modo de fazer -------------')
    # # Python 3.11+
    # start = time.perf_counter()
    # async with asyncio.TaskGroup() as group:
    #     tasks = [group.create_task(do_work(item)) for item in todo]
    # print(f"total time: {time.perf_counter() - start}s")
    # print('--------\ --------------- /------------')



if __name__ == '__main__':
    asyncio.run(main())
