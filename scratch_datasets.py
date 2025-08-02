import asyncio
from bilibili_api import video


async def get_video_api(link) -> None:
    # 实例化 Video 类
    v = video.Video(bvid=link)
    
    # 获取信息
    info = await v.get_info()
    # 打印信息
    # print(info)
    return info

def get_video_info(link):
    info=asyncio.get_event_loop().run_until_complete(get_video_api(link))
    return info
if __name__=='__main__':
    print(get_video_info("BV1z5pweDEuM"))
