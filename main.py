import asyncio
from time import localtime, strftime
from teleplay import ZBKYYYTeleplay, IJUJITVTeleplay
from downloader import M3U8Downloader
import os

async def download(teleplay, save_dir, query_update=False):
    os.makedirs(save_dir, exist_ok=True)
    downloader = M3U8Downloader("tmp")
    download_size = len(list(filter(lambda value: value.endswith('.mp4'), os.listdir(save_dir))))
    await teleplay.initlize()

    while query_update:
        if len(teleplay) > download_size and teleplay[-1]:
            break
        await teleplay.initlize()
        await asyncio.sleep(3)
        print(f'{strftime("%H:%M:%S", localtime())}\r', end="")

    generate_cmd = lambda src, dst: f"ffmpeg -i {src} -c copy -map 0:v -map 0:a -bsf:a aac_adtstoasc {dst}"
    for name, uri in teleplay.items():
        print(f"download => {name} {uri}")
        if not uri:
            print("uri empty!")
            break
        ts_file = os.path.join(save_dir, f"{name}.ts")
        mp4_file = os.path.join(save_dir, f"{name}.mp4")
        if os.path.exists(mp4_file):
            continue
        for i in range(3):
            # try:
                await downloader.download(uri, ts_file)
            #     break
            # except Exception as e:
            #     print(f"download {uri}=>{ts_file} as {e}, try {i}")

        if os.path.exists(ts_file):
            os.system(generate_cmd(ts_file, mp4_file))
            os.system(f"rm {ts_file}")

    if query_update and len(list(filter(lambda value: value.endswith('.mp4'), os.listdir(save_dir)))) > download_size:
        from playsound import playsound
        playsound('/home/mking/Music/chengdu.mp3')

async def main():
    # await download(ZBKYYYTeleplay(8391), "陈情令")
    # await download(ZBKYYYTeleplay(67856), "追风者", True)
    await download(IJUJITVTeleplay(54460), "承欢记", True)


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
            break
        except:
            continue

