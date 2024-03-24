import m3u8
import asyncio
import aiohttp
from aiofile import AIOFile, Writer
import hashlib
import os
from Crypto.Cipher import AES


def generate_file(save_file, files, cmds):
    with open(save_file, 'wb') as f:
        for file in files:
            with open(file, 'rb') as sub_f:
                f.write(sub_f.read())
    if not cmds: return
    if isinstance(cmds, str): cmds = [cmds]
    for cmd in cmds:
        os.system(cmd)


class M3U8Downloader:

    def __init__(self,  cache_dir=".", headers={'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 ' 'Firefox/3.5.5'}) -> None:
        self.headers = headers
        self.cache_dir = cache_dir
        self.key_uris = {}
        os.makedirs(self.cache_dir, exist_ok=True)

    async def get_text(self, uri):
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as response:
                return await response.text()

    async def get_bin(self, uri):
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as response:
                return await response.read()

    async def save_bin(self, uri, file_name, decrypt_method=None):
        if os.path.exists(file_name):
            return
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(uri) as response:
                    async with AIOFile(file_name, 'wb') as afp:
                        writer = Writer(afp)
                        result = await response.read()
                        if decrypt_method:
                            result = decrypt_method(result)
                        await writer(result)
                        await afp.fsync()
        except Exception as e:
            print(f"m3u8 download error {e}: uri={uri}")
            os.remove(file_name)
            raise e

    async def parse_uri(self, uri):
        content = await self.get_text(uri)
        playlist = m3u8.loads(content, uri)
        if len(playlist.segments) > 0:
            return playlist.segments
        return await self.parse_uri(playlist.playlists[0].absolute_uri)
    
    async def generate_file(self, save_file, files, cmds):
        await asyncio.to_thread(generate_file, save_file, files, cmds)
    
    async def download_segment(self, segment, file_path):
        if segment.key is None or segment.key.method != "AES-128":
            await self.save_bin(segment.absolute_uri, file_path)
            return
        if segment.key.absolute_uri not in self.key_uris:
            self.key_uris[segment.key.absolute_uri] = await self.get_bin(segment.key.absolute_uri)
        def decrypt_method(data):
            # TODO not use key.iv
            cipher = AES.new(self.key_uris[segment.key.absolute_uri], AES.MODE_CBC)
            return cipher.decrypt(data)
        await self.save_bin(segment.absolute_uri, file_path, decrypt_method)

    async def download(self, uri, save_file, cmds=None):
        segments = await self.parse_uri(uri)
        file_paths = [os.path.join(self.cache_dir, hashlib.sha256(segment.absolute_uri.encode()).hexdigest()) for segment in segments]
        tasks = [self.download_segment(segment, file_path) for segment, file_path in zip (segments, file_paths)]
        await asyncio.gather(*tasks)
        await self.generate_file(save_file, file_paths, cmds)


if __name__ == '__main__':
    uri = "https://yzzy.play-cdn21.com/20240321/12306_29e1c50e/index.m3u8"
    downloader = M3U8Downloader("tmp")
    asyncio.run(downloader.download(uri, "08.ts", "ffmpeg -i 08.ts -c copy -map 0:v -map 0:a -bsf:a aac_adtstoasc 08.mp4"))