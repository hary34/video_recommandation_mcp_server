import requests  
import re  
import scratch_datasets
import csv  
import os  
import json
import pandas as pd  
import time  
from functools import wraps  
from bilibili_api import homepage, sync, Credential  
from bilibili_api.login import login_with_password, login_with_sms, send_sms, PhoneNumber, Check  
from bilibili_api.user import get_self_info  
from bilibili_api import settings  
import video_operations
batch=True
# Toggle for using title or link in CSV  


def retry(exceptions, tries=3, delay=2, backoff=2):  
    """Retry calling the decorated function using an exponential backoff."""  
    def decorator(f):  
        @wraps(f)  
        def f_retry(*args, **kwargs):  
            mtries, mdelay = tries, delay  
            while mtries > 0:  
                try:  
                    return f(*args, **kwargs)  
                except exceptions as e:  
                    # print(f"Retrying due to {e}, tries left: {mtries-1}")  
                    mtries -= 1  
                    time.sleep(mdelay)  
                    mdelay *= backoff  
            return f(*args, **kwargs)  
        return f_retry  
    return decorator  

@retry((requests.exceptions.RequestException, ConnectionAbortedError), tries=5, delay=2, backoff=2)  
def login_with_retry(username, password):  
    """Attempt to login with retry logic."""  
    return login_with_password(username, password)  

@retry((requests.exceptions.RequestException, ConnectionAbortedError), tries=5, delay=2, backoff=2)  
def fetch_recommendations_with_retry(credential):  
    """Fetch recommendations with retry logic."""  
    return sync(homepage.get_videos(credential=credential))  

def extract_bv_id(url):  
    """Extract BV ID from URL."""  
    match = re.search(r'/video/(BV\w+)', url)  
    return match.group(1) if match else None  

def dataset_to_csv(dataset, filename='bilibili_recommendations.csv',include_title=False):  
    """Write dataset to a CSV file."""  
    with open(filename, mode='w', newline='', encoding='utf-8') as file:  
        writer = csv.writer(file)  
        headers = ['Name', 'Likes/Views', 'Coins/Views', 'Favorites/Views', 'Shares/Views']  
        writer.writerow(headers)  
        for link, stats in dataset.items():  
            writer.writerow([  
                stats['title'] if include_title else link,  
                stats['stat'].get('like', 'N/A')/stats['stat'].get('view', 'N/A'),   
                stats['stat'].get('coin', 'N/A')/stats['stat'].get('view', 'N/A'),  
                stats['stat'].get('favorite', 'N/A')/stats['stat'].get('view', 'N/A'),  
                stats['stat'].get('share', 'N/A')/stats['stat'].get('view', 'N/A')  
            ])  
    # print(f"Data successfully written to {filename}")  

def csv_to_excel(csv_filename, excel_filename):  
    """Convert CSV file to Excel file."""  
    df = pd.read_csv(csv_filename)  
    df.to_excel(excel_filename, index=False, engine='openpyxl')  
    # print(f"CSV file '{csv_filename}' has been successfully converted to Excel file '{excel_filename}'.")  

def fetch_bilibili_recommendations():  
    dataset = {}  

    try:  
        mode = int(input("请选择登录方式：\n1. 密码登录\n2. 验证码登录\n3. 本地存储\n请输入 1/2/3\n")) if not batch else 3
        
        credential = None  
        settings.geetest_auto_open = False  

        if mode not in [1, 2,3]:  
            print("请输入 1/2/3 ")  
            return None  

        if mode == 1:  
            username = input("请输入手机号/邮箱：")  
            password = input("请输入密码：")  
            print("正在登录。")  
            try:  
                credential = login_with_retry(username, password)  
            except Exception as e:  
                print(f"Error logging in with password: {e}")  
                return None  

        elif mode == 2:  
            phone = input("请输入手机号：")  
            print("正在登录。")  
            try:  
                send_sms(PhoneNumber(phone, country="+86"))  
                code = input("请输入验证码：")  
                credential = login_with_sms(PhoneNumber(phone, country="+86"), code)  
            except Exception as e:  
                print(f"Error logging in with SMS: {e}")  
                return None  
        elif mode == 3:
            try:
                user_data = []
                with open('user_data.txt', 'r') as f:
                    user_data=eval(f.read())
                    
                credential = Credential(sessdata=user_data[0], bili_jct=user_data[1], buvid3=user_data[2])
            except Exception as e:  
                print("No such user_data.txt")
        if isinstance(credential, Check):  
            print("需要进行验证。请考虑使用二维码登录")  
            return None  
        
        if credential:  
            with open('user_data.txt', 'w') as f:  
                a = [credential.sessdata, credential.bili_jct, credential.buvid3]  
                f.write(str(a))  
            name = sync(get_self_info(credential))['name']  
            print(f"欢迎，{name}!")  

            try:  
                recommendations = fetch_recommendations_with_retry(credential)  
                for video in recommendations.get("item", []):  
                    # print(f"Title: {video['title']}")  
                    # print(f"Link: {video['uri']}")  
                    
                    bv_id = extract_bv_id(video['uri'])  
                    if bv_id:  
                        try:  
                            # video_operations.like_video(bv_id)
                            video_info = scratch_datasets.get_video_info(bv_id)  
                            
                            dataset[video['uri']] = video_info  
                        except Exception as e:  
                            print(f"Error getting video info: {e}")  
            except Exception as e:  
                print(f"Error fetching videos: {e}")  

        return dataset  

    except Exception as exc:  
        print(f"An error occurred: {exc}")  
        return None  

# Fetch and save dataset
def clear_dataset(ahp):
    length=len(ahp.target_videos)
    ahp.target_videos = []

    return length
def recommandation_algorithm(batch):
    import ahp

    for i in range(batch):
        dataset = fetch_bilibili_recommendations() 
        if dataset:  
            dataset_to_csv(dataset)  
            
            dataset_to_csv(dataset, 'bilibili_recommendations_with_title.csv', include_title=True)
        ahp.create_table_by_batch(True)
    
    return ahp.target_videos,clear_dataset(ahp)
# import ahp

# for i in range(int(input("请输入要爬取的次数："))):
#     dataset = fetch_bilibili_recommendations() 
#     if dataset:  
#         dataset_to_csv(dataset)  
        
#         dataset_to_csv(dataset, 'bilibili_recommendations_with_title.csv', include_title=True)
#     ahp.create_table_by_batch(True)

# print(recommandation_algorithm(1))
# recommandation_algorithm(1)
if __name__ == "__main__":
    print(recommandation_algorithm(1))