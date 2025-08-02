from mcp.server.fastmcp import FastMCP
import spider
import asyncio
import webbrowser
import scratch_datasets
import ahp
import os
import platform
import psutil
import json
import csv
import video_operations
from bilibili_api import search, sync

"""
帮我扩展mcp的功能

我来帮你扩展 MCP 的功能。首先让我查看一下现有的 spider 模块，了解它提供了哪些功能，然后为你的 MCP 服务器添加更多有用的工具。
基于现有的 spider 模块功能，我来为你的 MCP 服务器添加一些有用的扩展功能：
很好！我已经为你的 MCP 服务器添加了许多有用的扩展功能。现在让我创建一个 requirements.txt 文件来管理依赖项：
完美！我已经成功扩展了你的 MCP 服务器功能。以下是新增的功能：
新增的 MCP 工具功能：
1. 视频相关功能
get_video_info(bv_id) - 获取指定 BV ID 的 Bilibili 视频详细信息
get_target_videos() - 获取当前目标视频列表
clear_target_videos() - 清空目标视频列表
2. 文件操作功能
list_files(directory) - 列出指定目录下的文件和文件夹
read_file(file_path) - 读取文本文件内容
search_files_by_name(file_name, directory) - 在目录中搜索指定名称的文件
3. 数据导出功能
export_recommendations_to_json(file_path) - 将推荐视频导出为 JSON 文件
convert_csv_to_excel(csv_file, excel_file) - 将 CSV 文件转换为 Excel 格式
4. 系统信息功能
get_system_info() - 获取系统信息（CPU、内存、磁盘使用情况等）"""

mcp = FastMCP("Harry")

@mcp.tool()
async def recommend_videos(batch=1, show_ui=True):
    """
    recommend ranked videos in bilibili, the videos are shown in homepage.
    
    Args:
        batch: Number of batches to process (default: 1)
        show_ui: Whether to show the UI interface (default: True)
    """
    
    batch = int(batch)
    data_tuple = await asyncio.to_thread(spider.recommandation_algorithm, batch)
    
    # data_tuple[0] 是 ahp.target_videos 列表
    target_videos = data_tuple[0]
    cleared_count = data_tuple[1]
    
    # 根据 show_ui 参数决定是否展示界面
    if show_ui and target_videos and len(target_videos) > 0:
        show_videos_ui(target_videos, f"Bilibili 视频推荐 - 共 {len(target_videos)} 个视频")
        return {
            "message": f"成功获取并展示 {len(target_videos)} 个推荐视频",
            "videos_count": len(target_videos),
            "ui_opened": True,
            "videos": target_videos
        }
    elif target_videos and len(target_videos) > 0:
        return {
            "message": f"成功获取 {len(target_videos)} 个推荐视频",
            "videos_count": len(target_videos),
            "ui_opened": False,
            "videos": target_videos
        }
    else:
        return {
            "message": "没有获取到推荐视频",
            "videos_count": 0,
            "ui_opened": False,
            "videos": []
        }

@mcp.tool()
def watch_video(url: str):
    """
    Opens the given URL in a web browser, the url is often the address of video in Bilibili.
    """
    webbrowser.open(url)
    return f"Successfully opened {url}"

@mcp.tool()
async def like_videos(bv_ids):
    """
    Like multiple Bilibili videos by their BV IDs.
    
    Args:
        bv_ids: A list of BV IDs or a single BV ID string
               Can be BV IDs, URLs, or a mix of both
    """
    # 如果输入是字符串，转换为列表
    if isinstance(bv_ids, str):
        bv_ids = [bv_ids]
    
    results = []
    success_count = 0
    fail_count = 0
    
    for bv_id in bv_ids:
        try:
            # 如果输入的是完整URL，提取BV ID
            original_input = bv_id
            if bv_id.startswith("http") or bv_id.startswith("/video/"):
                import re
                match = re.search(r'BV[\w]+', bv_id)
                if match:
                    bv_id = match.group(0)
                else:
                    results.append({
                        "input": original_input,
                        "success": False,
                        "message": "无法从URL中提取BV ID"
                    })
                    fail_count += 1
                    continue
            
            # 调用点赞功能
            await asyncio.to_thread(video_operations.like_video, bv_id)
            
            # 获取视频信息
            video_info = await asyncio.to_thread(scratch_datasets.get_video_info, bv_id)
            
            results.append({
                "input": original_input,
                "success": True,
                "bv_id": bv_id,
                "title": video_info.get("title", "未知标题"),
                "author": video_info.get("owner", {}).get("name", "未知作者"),
                "current_likes": video_info.get("stat", {}).get("like", 0)
            })
            success_count += 1
            
            # 添加短暂延迟，避免请求过快
            await asyncio.sleep(0.5)
            
        except Exception as e:
            results.append({
                "input": original_input,
                "success": False,
                "message": f"点赞失败: {str(e)}"
            })
            fail_count += 1
    
    return {
        "total": len(bv_ids),
        "success": success_count,
        "failed": fail_count,
        "results": results
    }

@mcp.tool()
async def search_videos(keyword: str, page: int = 1):
    """
    Search videos on Bilibili.
    """
    from bilibili_api import search
    
    result = await search.search_by_type(
        keyword,
        search_type=search.SearchObjectType.VIDEO,
        page=page
    )
    
    return result["result"]

@mcp.tool()
async def get_video_info(bv_id: str):
    """
    Get detailed information about a Bilibili video by BV ID.
    """
    try:
        video_info = await asyncio.to_thread(scratch_datasets.get_video_info, bv_id)
        return {
            "title": video_info.get("title", "N/A"),
            "author": video_info.get("owner", {}).get("name", "N/A"),
            "view": video_info.get("stat", {}).get("view", 0),
            "like": video_info.get("stat", {}).get("like", 0),
            "coin": video_info.get("stat", {}).get("coin", 0),
            "favorite": video_info.get("stat", {}).get("favorite", 0),
            "share": video_info.get("stat", {}).get("share", 0),
            "duration": video_info.get("duration", 0),
            "pubdate": video_info.get("pubdate", 0),
            "desc": video_info.get("desc", "N/A")
        }
    except Exception as e:
        return f"Error getting video info: {str(e)}"

@mcp.tool()
def list_files(directory: str = "."):
    """
    List files and directories in the specified path.
    """
    try:
        items = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            items.append({
                "name": item,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        return items
    except Exception as e:
        return f"Error listing files: {str(e)}"

@mcp.tool()
def read_file(file_path: str):
    """
    Read the contents of a text file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return {
            "file_path": file_path,
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def get_system_info():
    """
    Get system information including OS, CPU, memory usage.
    """
    try:
        return {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free
            }
        }
    except Exception as e:
        return f"Error getting system info: {str(e)}"


@mcp.tool()
def search_files_by_name(file_name: str, directory: str = "."):
    """
    Search for files by name in the specified directory and subdirectories.
    """
    try:
        matches = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file_name.lower() in file.lower():
                    matches.append({
                        "name": file,
                        "path": os.path.join(root, file),
                        "size": os.path.getsize(os.path.join(root, file))
                    })
        return {
            "query": file_name,
            "matches_count": len(matches),
            "matches": matches
        }
    except Exception as e:
        return f"Error searching files: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str, overwrite: bool = False):
    """
    Write content to a file.
    If overwrite is False and file exists, content will be appended.
    If overwrite is True and file exists, file will be overwritten.
    """
    try:
        mode = 'w' if overwrite else 'a'
        with open(file_path, mode, encoding='utf-8') as file:
            file.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"


def show_videos_ui(data, title: str = "Bilibili 视频推荐"):
    """
    Create a beautiful UI to display Bilibili videos information.
    Data can be a dict, list, or JSON string containing video information.
    """
    try:
        import tempfile
        import datetime
        
        # 如果输入是字符串，尝试解析为 JSON
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                return f"Error parsing JSON string: {str(e)}"
        
        # 确保数据是可序列化的
        if not isinstance(data, (dict, list)):
            return "Error: Data must be a dictionary, list, or valid JSON string"
        
        # 提取视频列表
        videos = []
        if isinstance(data, list):
            videos = data
        elif isinstance(data, dict):
            if 'videos' in data:
                videos = data['videos']
            elif 'item' in data:
                videos = data['item']
            else:
                # 如果是单个视频信息，包装成列表
                videos = [data]
        
        # Convert data to JSON string for JavaScript
        json_data = json.dumps(videos, ensure_ascii=False, indent=2)
        
        # Create HTML content with modern styling
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: #f5f5f5;
                    min-height: 100vh;
                    padding: 20px;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }}
                
                h1 {{
                    color: #00a1d6;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                
                .subtitle {{
                    color: #666;
                    font-size: 1.1em;
                }}
                
                .timestamp {{
                    color: #999;
                    font-size: 0.9em;
                    margin-top: 10px;
                }}
                
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                
                .videos-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                    gap: 25px;
                    margin-bottom: 40px;
                }}
                
                .video-card {{
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    transition: all 0.3s ease;
                    cursor: pointer;
                }}
                
                .video-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
                }}
                
                .video-cover {{
                    width: 100%;
                    height: 200px;
                    object-fit: cover;
                    background: #f0f0f0;
                    position: relative;
                }}
                
                .video-duration {{
                    position: absolute;
                    bottom: 8px;
                    right: 8px;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.85em;
                }}
                
                .video-info {{
                    padding: 15px;
                }}
                
                .video-title {{
                    font-size: 1.1em;
                    font-weight: 500;
                    color: #222;
                    margin-bottom: 10px;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                    line-height: 1.4;
                }}
                
                .video-author {{
                    color: #666;
                    font-size: 0.9em;
                    margin-bottom: 10px;
                }}
                
                .video-stats {{
                    display: flex;
                    gap: 15px;
                    font-size: 0.85em;
                    color: #999;
                }}
                
                .stat-item {{
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }}
                
                .stat-icon {{
                    width: 16px;
                    height: 16px;
                }}
                
                .video-link {{
                    display: inline-block;
                    margin-top: 10px;
                    color: #00a1d6;
                    text-decoration: none;
                    font-size: 0.9em;
                }}
                
                .video-link:hover {{
                    text-decoration: underline;
                }}
                
                .no-cover {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-size: 1.2em;
                }}
                
                .stats-summary {{
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    gap: 20px;
                }}
                
                .summary-item {{
                    text-align: center;
                }}
                
                .summary-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #00a1d6;
                }}
                
                .summary-label {{
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                    <div class="subtitle">发现精彩视频内容</div>
                    <div class="timestamp">更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>
                
                <div class="stats-summary" id="stats-summary"></div>
                
                <div class="videos-grid" id="videos-grid"></div>
            </div>
            
            <script>
                const videos = {json_data};
                
                // 格式化数字
                function formatNumber(num) {{
                    if (num >= 10000) {{
                        return (num / 10000).toFixed(1) + '万';
                    }}
                    return num.toString();
                }}
                
                // 格式化时长
                function formatDuration(seconds) {{
                    const hours = Math.floor(seconds / 3600);
                    const minutes = Math.floor((seconds % 3600) / 60);
                    const secs = seconds % 60;
                    
                    if (hours > 0) {{
                        return `${{hours}}:${{minutes.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
                    }}
                    return `${{minutes}}:${{secs.toString().padStart(2, '0')}}`;
                }}
                
                // 生成统计摘要
                function generateSummary() {{
                    const summary = document.getElementById('stats-summary');
                    let totalViews = 0;
                    let totalLikes = 0;
                    
                    videos.forEach(video => {{
                        if (video.stat) {{
                            totalViews += video.stat.view || 0;
                            totalLikes += video.stat.like || 0;
                        }}
                    }});
                    
                    summary.innerHTML = `
                        <div class="summary-item">
                            <div class="summary-value">${{videos.length}}</div>
                            <div class="summary-label">视频总数</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-value">${{formatNumber(totalViews)}}</div>
                            <div class="summary-label">总播放量</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-value">${{formatNumber(totalLikes)}}</div>
                            <div class="summary-label">总点赞数</div>
                        </div>
                    `;
                }}
                
                // 生成视频卡片
                function generateVideoCards() {{
                    const grid = document.getElementById('videos-grid');
                    
                    videos.forEach((video, index) => {{
                        const card = document.createElement('div');
                        card.className = 'video-card';
                        
                        // 构建视频链接 - 兼容不同格式
                        let videoUrl = video.URL || video.uri || video.url || '';
                        if (videoUrl && !videoUrl.startsWith('http')) {{
                            videoUrl = 'https://www.bilibili.com' + videoUrl;
                        }}
                        
                        // 获取封面图片 - 兼容不同格式
                        const coverUrl = video.Cover || video.pic || video.cover || '';
                        
                        // 获取标题 - 兼容不同格式
                        const title = video.Title || video.title || '未知标题';
                        
                        // 获取排名和评分
                        const rank = video.Rank || (index + 1);
                        const score = video.Score || 0;
                        
                        // 获取作者信息
                        const author = video.owner?.name || video.author || '未知作者';
                        
                        card.innerHTML = `
                            <div class="video-cover ${{!coverUrl ? 'no-cover' : ''}}">
                                ${{coverUrl ? `<img src="${{coverUrl}}" alt="${{title}}" style="width: 100%; height: 100%; object-fit: cover;">` : `<div>视频 ${{rank}}</div>`}}
                                ${{video.duration ? `<div class="video-duration">${{formatDuration(video.duration)}}</div>` : ''}}
                            </div>
                            <div class="video-info">
                                <div class="video-title">${{title}}</div>
                                <div class="video-author">
                                    ${{score ? `<span style="color: #f25d8e;">排名 #${{rank}} | 评分: ${{(score*10).toFixed(1)}}/10</span>` : author}}
                                </div>
                                <div class="video-stats">
                                    <div class="stat-item">
                                        <span>▶</span>
                                        <span>${{formatNumber(video.stat?.view || video.view || 0)}}</span>
                                    </div>
                                    <div class="stat-item">
                                        <span>👍</span>
                                        <span>${{formatNumber(video.stat?.like || video.like || 0)}}</span>
                                    </div>
                                    <div class="stat-item">
                                        <span>💰</span>
                                        <span>${{formatNumber(video.stat?.coin || video.coin || 0)}}</span>
                                    </div>
                                </div>
                                ${{videoUrl ? `<a href="${{videoUrl}}" target="_blank" class="video-link">在B站观看 →</a>` : ''}}
                            </div>
                        `;
                        
                        if (videoUrl) {{
                            card.onclick = () => window.open(videoUrl, '_blank');
                        }}
                        
                        grid.appendChild(card);
                    }});
                }}
                
                // 初始化页面
                generateSummary();
                generateVideoCards();
            </script>
        </body>
        </html>
        """
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name
        
        # Open in browser
        webbrowser.open(f'file://{temp_file}')
        
        return f"Videos UI created and opened in browser: {temp_file}"
        
    except Exception as e:
        return f"Error creating videos UI: {str(e)}"

def main():
    # # 调试搜索功能
    # import asyncio
    # result = asyncio.run(search_videos("艾尔登法环"))
    
    # # 保存到本地文件
    # with open('search_results.json', 'w', encoding='utf-8') as f:
    #     json.dump(result, f, ensure_ascii=False, indent=2)
    
    # print("搜索结果已保存到 search_results.json")
    
    # # 只打印基本信息
    # if 'result' in result:
    #     print(f"找到 {len(result['result'])} 个视频")
    #     for i, video in enumerate(result['result'][:5]):  # 只显示前5个
    #         print(f"{i+1}. {video.get('title', 'N/A')}")
    
    mcp.run()

if __name__ == "__main__":
    main()