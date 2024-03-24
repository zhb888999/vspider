import json
from urllib.parse import urlparse, urljoin
from lxml import html

import asyncio
import aiohttp


class ZBKYYYTeleplay:
    """
    url: https://zbkyyy.com
    """

    def __init__(self, url) -> None:
        self.hosturl = url
        if isinstance(url, int):
            self.hosturl = f"https://www.zbkyyy.com/qyvoddetail/{self.hosturl}.html"
        self.name = ""
        self.info = {}
        self.episode_urls = None
        self.episode_names = None
        self.episode_infos = {}
        self.index = 0

    @staticmethod
    async def get_html(url):
        headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 ' 'Firefox/3.5.5'}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                return await response.text()
    
    async def initlize(self):
        await self.parse_teleplay()
        tasks = [self.parse_episode(name, url) for name, url in self.episode_urls.items()]
        await asyncio.gather(*tasks)
    
    def get_max_episode_list(self, uls):
        urls, names = [], []
        for ul in uls:
            sub_html = html.tostring(ul)
            ul = html.fromstring(sub_html)
            hrefs = ul.xpath('//a/@href')
            if len(hrefs) > len(urls):
                urls = hrefs
                names = ul.xpath('//a/text()')
        return urls, names
    
    async def parse_teleplay(self):
        parsed_result = urlparse(self.hosturl)
        base_url = f"{parsed_result.scheme}://{parsed_result.hostname}"
        text = await self.get_html(self.hosturl)
        parsed_html = html.fromstring(text)

        keys = ["影片名称"]
        values = parsed_html.xpath('//div[@class="txt_intro_con"]//h1/text()')
        self.name = values[0]
        keys.extend(parsed_html.xpath('//div[@class="txt_intro_con"]//ul/li/em/text()'))
        values.extend(parsed_html.xpath('//div[@class="txt_intro_con"]//ul/li/text()'))
        keys.extend(parsed_html.xpath('//div[@class="txt_intro_con"]//ul/li/span/a/text()'))
        values.extend(parsed_html.xpath('//div[@class="txt_intro_con"]//ul/li/span/text()'))
        for key, value in zip(keys, values):
            key = key.split('：')[0].strip()
            value = value.split('：')[-1].strip()
            self.info[key] = value
        urls, names = self.get_max_episode_list(parsed_html.xpath('//div[@class="v_con_box"]//ul'))
        urls = [urljoin(base_url, url) for url in urls]
        self.episode_urls = {name: url for name, url in zip(names, urls)}
        self.info["剧集"] = len(self.episode_urls)
        self.episode_names = list(self.episode_urls.keys())
    
    async def parse_episode(self, name, url):
        text = await self.get_html(url)
        parsed_html = html.fromstring(text)
        play_var_str = parsed_html.xpath('//div[@class="iplays"]/script/text()')[0]
        play_info = json.loads(play_var_str.split('=')[1])
        self.episode_infos[name] = play_info
    
    def get_episode_play_url(self, episode_name):
        return self.episode_infos[episode_name]['url']
    
    def play_urls(self):
        return [self.get_episode_play_url(episode_name) for episode_name in self.episode_urls.keys()]
        
    def keys(self):
        return self.episode_urls.keys()
    
    def items(self):
        for episode_name in self.episode_urls.keys():
            yield episode_name, self.get_episode_play_url(episode_name)

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.episode_urls):
            url = self.get_episode_play_url(self.episode_names[self.index])
            self.index += 1
            return url
        self.index = 0
        raise StopIteration()
    
    def __len__(self):
        return len(self.episode_urls)
    
    def __getitem__(self, key):
        if isinstance(key, int):
            key = self.episode_names[key]
        return self.get_episode_play_url(key)
    
    def __str__(self):
        return f"{self.info}"


if __name__ == '__main__':
    teleplay = ZBKYYYTeleplay(67856)
    asyncio.run(teleplay.initlize())
    for k, v in teleplay.items():
        print(k, v)