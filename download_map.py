import asyncio
from downloader import M3U8Downloader
import os

async def download(m3u8_map, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    downloader = M3U8Downloader("tmp")
    download_size = len(list(filter(lambda value: value.endswith('.mp4'), os.listdir(save_dir))))
    generate_cmd = lambda src, dst: f"ffmpeg -i {src} -c copy -map 0:v -map 0:a -bsf:a aac_adtstoasc {dst}"

    for name, uri in m3u8_map.items():
        print(f"download => {name} {uri}")
        if not uri:
            print("uri empty!")
            break
        ts_file = os.path.join(save_dir, f"{name}.ts")
        mp4_file = os.path.join(save_dir, f"{name}.mp4")
        if os.path.exists(mp4_file):
            continue
        for i in range(3):
            try:
                await downloader.download(uri, ts_file)
                break
            except Exception as e:
                print(f"download {uri}=>{ts_file} as {e}, try {i}")

        if os.path.exists(ts_file):
            os.system(generate_cmd(ts_file, mp4_file))
            os.system(f"rm {ts_file}")

async def main():
    chen_huan_ji = {
        "第01集": "https://v.cdnlz2.com/20240409/29677_3f005fc9/index.m3u8",
        "第02集": "https://v.cdnlz2.com/20240409/29676_6e0be8f5/index.m3u8",
        "第03集": "https://v.cdnlz2.com/20240409/29675_31710f23/index.m3u8",
        "第04集": "https://v.cdnlz2.com/20240409/29674_bb521726/index.m3u8",
        "第05集": "https://v.cdnlz2.com/20240410/29726_2a457c22/index.m3u8",
        "第06集": "https://v.cdnlz2.com/20240410/29725_27347b37/index.m3u8",
        "第07集": "https://v.cdnlz2.com/20240411/29782_320d1815/index.m3u8",
        "第08集": "https://v.cdnlz2.com/20240411/29781_adebc99a/index.m3u8",
        "第09集": "https://v.cdnlz2.com/20240412/29838_d2bbc097/index.m3u8",
        "第10集": "https://v.cdnlz2.com/20240412/29837_8a2f86dc/index.m3u8",
        "第11集": "https://v.cdnlz2.com/20240413/29903_2b0e7f2a/index.m3u8",
        "第12集": "https://v.cdnlz2.com/20240413/29902_c21b5d65/index.m3u8",
        "第13集": "https://v.cdnlz2.com/20240414/29932_e942b904/index.m3u8",
        "第14集": "https://v.cdnlz2.com/20240414/29931_cc1baefb/index.m3u8",
        "第15集": "https://v.cdnlz2.com/20240415/29979_204f0e8e/index.m3u8",
        "第16集": "https://v.cdnlz2.com/20240415/29978_163ea09b/index.m3u8",
        "第17集": "https://v.cdnlz2.com/20240416/29995_f50d90d6/index.m3u8",
        "第18集": "https://v.cdnlz2.com/20240416/29994_e5576c71/index.m3u8",
        "第19集": "https://v.cdnlz2.com/20240417/30037_6d56ac2f/index.m3u8",
        "第20集": "https://v.cdnlz2.com/20240417/30038_f67bce37/index.m3u8",
        "第21集": "https://v.cdnlz2.com/20240418/30088_a4fa7307/index.m3u8",
        "第22集": "https://v.cdnlz2.com/20240418/30089_1c905630/index.m3u8",
        "第23集": "https://v.cdnlz2.com/20240419/30216_ec1c3a3a/index.m3u8",
        "第24集": "https://v.cdnlz2.com/20240419/30215_1aafce18/index.m3u8",
        "第25集": "https://v.cdnlz2.com/20240420/30253_7b2358d6/index.m3u8",
        "第26集": "https://v.cdnlz2.com/20240420/30252_43652b50/index.m3u8",
        "第27集": "https://v.cdnlz2.com/20240421/30320_a7f11884/index.m3u8",
        "第28集": "https://v.cdnlz2.com/20240421/30319_f36c7dd8/index.m3u8",
        "第29集": "https://v.cdnlz2.com/20240422/30365_a882004d/index.m3u8",
        "第30集": "https://v.cdnlz2.com/20240422/30364_e3f76fc7/index.m3u8",
        "第31集": "https://v.cdnlz2.com/20240423/30421_80576d76/index.m3u8",
        "第32集": "https://v.cdnlz2.com/20240423/30420_1923c90f/index.m3u8",
        "第33集": "https://v.cdnlz2.com/20240424/30475_5085748b/index.m3u8",
    }
    await download(chen_huan_ji, "承欢记")


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
            break
        except:
            continue