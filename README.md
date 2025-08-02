# 视频推荐系统 (Video Recommendation System)

基于层次分析法(AHP)的B站视频推荐系统，通过多指标综合评价来推荐高质量视频内容。

## 功能特性

- 🎯 基于AHP层次分析法的智能推荐算法
- 📊 多维度视频评价指标体系
- 🕷️ B站视频数据爬取功能
- 🔍 智能视频搜索和筛选
- 📈 视频数据标准化处理
- 💾 推荐结果持久化存储

## 主要模块

- `ahp.py` - 层次分析法核心算法实现
- `spider.py` - B站视频数据爬虫
- `search.py` - 视频搜索功能
- `normalize_data.py` - 数据标准化处理
- `video_operations.py` - 视频操作相关功能
- `server.py` - 服务器端实现
- `harry_mcp.py` - MCP服务端实现

## 数据文件

- `bilibili_recommendations.csv` - B站推荐视频数据
- `bilibili_recommendations_with_title.csv` - 包含标题的推荐数据
- `ahp_matrix.csv` - AHP判断矩阵
- `user_data.txt` - 用户数据
- `bilibili_video_recommendations_list.txt` - 推荐视频列表

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行爬虫获取视频数据
2. 配置AHP判断矩阵
3. 执行推荐算法
4. 查看推荐结果

## 技术栈

- Python 3.x
- Pandas - 数据处理
- NumPy - 数值计算
- Requests - 网络请求
- JSON - 数据格式

## 贡献

欢迎提交Issues和Pull Requests来改进项目！

## 许可证

MIT License 