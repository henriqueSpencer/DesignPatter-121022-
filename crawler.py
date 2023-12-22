from __future__ import annotations

import asyncio
import html.parser
import pathlib
import time
import urllib.parse
from typing import Callable, Iterable

import httpx  # https://github.com/encode/httpx

class Crawler:
    def __init__(
            self,
            client = httpx.AsyncClient, # Cliente assincrono
            urls: Iterable[str] = [str], # lista de urls iniciais
            filter_url: Callable[[str, str], str | None], # filtro de urls que não queremos
            workers: int = 10, # numero de workers = determinas o numero de conexoes simultaneas
            limit: int = 25 # limit de paginas
    ):
        self.client = client

        self.start_urls = set(urls)
        self.todo = asyncio.Queue() # queue para fazer o trabalho necessario
        self.seen = set() # url ja visitadas
        self.done = set() #

        self.filter_url = filter_url
        self.num_workers = workers
        self.limit = limit
        self.total = 0 # keep tracker of total number of pages crawled

    async def run(self):
        await self.on_found_links(self.start_urls) # coloca as urls iniciais na queue
        workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.num_workers)
        ]
        await self.todo.join()

        for worker in workers:
            worker.cancel()

    async def on_found_links(self, urls:):
        new = url - self.seen