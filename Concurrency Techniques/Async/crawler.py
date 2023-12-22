from __future__ import annotations

import asyncio
import html.parser
import pathlib
import time
import urllib.parse
from typing import Callable, Iterable

import httpx  # https://github.com/encode/httpx

class UrlFilterer:
    def __init__(
            self,
            allowed_domains: set[str] | None = None,
            allowed_schemes: set[str] | None = None,
            allowed_filetypes: set[str] | None = None,
    ):
        self.allowed_domains = allowed_domains
        self.allowed_schemes = allowed_schemes
        self.allowed_filetypes = allowed_filetypes

    def filter_url(self, base: str, url: str) -> str | None:
        url = urllib.parse.urljoin(base, url)
        url, _frag = urllib.parse.urldefrag(url)
        parsed = urllib.parse.urlparse(url)
        if (self.allowed_schemes is not None
                and parsed.scheme not in self.allowed_schemes):
            return None
        if (self.allowed_domains is not None
                and parsed.netloc not in self.allowed_domains):
            return None
        ext = pathlib.Path(parsed.path).suffix
        if (self.allowed_filetypes is not None
                and ext not in self.allowed_filetypes):
            return None
        return url


class UrlParser(html.parser.HTMLParser):
    def __init__(
            self,
            base: str,
            filter_url: Callable[[str, str], str | None]
    ):
        super().__init__()
        self.base = base
        self.filter_url = filter_url
        self.found_links = set()

    def handle_starttag(self, tag: str, attrs):
        # look for <a href="...">
        if tag != "a":
            return

        for attr, url in attrs:
            if attr != "href":
                continue

            if (url := self.filter_url(self.base, url)) is not None:
                self.found_links.add(url)



# Crawler = Rastegante = Figurinha da aranha
class Crawler:
    def __init__(
            self,
            filter_url, # filtro de urls que não queremos
            client = httpx.AsyncClient, # Cliente assincrono
            urls: Iterable[str] = [str], # lista de urls iniciais
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
        '''
            Run the crawler until all work is done.
        '''
        await self.on_found_links(self.start_urls) # coloca as urls iniciais na queue
        workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.num_workers)
        ]
        await self.todo.join()

        for worker in workers:
            worker.cancel()

    async def on_found_links(self, urls: set[str]):

        new = urls - self.seen
        self.seen.update(new)

        # await save to db or file Here...

        for url in new:
            await self.put_todo(url)


    async def worker(self):
        while True:
            try:
                await self.process_one()
            except asyncio.CancelledError:
                return

    async def process_one(self):
        url = await self.todo.get()
        try:
            await self.crawl(url)
        except Exception as exc:
            # retry handling here...
            pass
        finally:
            self.todo.task_done()

    async def crawl(self, url: str):
        # rate limit here...
        await asyncio.sleep(0.1)

        response = await self.client.get(url, follow_redirects=True)

        found_links = await self.parse_links(
            base=str(response.url),
            text=response.text,
        )

        await self.on_found_links(found_links)
        self.done.add(url)

    async def parse_links(self, base: str, text: str) -> set[str]:
        '''
            Parse links from the given text and return a set of links found.
        '''
        parser = UrlParser(base, self.filter_url)
        parser.feed(text)
        return parser.found_links

    async def on_found_links(self, urls: set[str]):
        new = urls - self.seen
        self.seen.update(new)

        # await save to database or file here...

        for url in new:
            await self.put_todo(url)
    async def put_todo(self, url: str):
        # So coloca na fila caso ainda esteja dentro do limite
        if self.total >= self.limit:
            return
        self.total += 1
        await self.todo.put(url)


async def main():
    filterer = UrlFilterer(
        allowed_domains={"mcoding.io"},
        allowed_schemes={"http", "https"},
        allowed_filetypes={".html", ".php", ""},
    )

    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        crawler = Crawler(
            client=client,
            urls=["https://mcoding.io/"],
            filter_url=filterer.filter_url,
            workers=5,
            limit=25,
        )
        await crawler.run()
    end = time.perf_counter()

    seen = sorted(crawler.seen)
    print("Results:")
    for url in seen:
        print(url)
    print(f"Crawled: {len(crawler.done)} URLs")
    print(f"Found: {len(seen)} URLs")
    print(f"Done in {end - start:.2f}s")

if __name__ == '__main__':
    asyncio.run(main(), debug=True)