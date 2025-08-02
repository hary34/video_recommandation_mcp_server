import asyncio
from bilibili_api import video, Credential

async def like_bvid(video_) -> None:
    try:
        user_data = []
        with open('user_data.txt', 'r') as f:
            user_data=eval(f.read())
            
        credential = Credential(sessdata=user_data[0], bili_jct=user_data[1], buvid3=user_data[2])
        v = video.Video(bvid=video_, credential=credential)
    
        await v.like(True)
    except Exception as E:
        print(E)
def like_video(video):
    asyncio.get_event_loop().run_until_complete(like_bvid(video))
    