# Bilibili Video Recommendation System

An intelligent video recommendation system based on Analytic Hierarchy Process (AHP) that recommends high-quality video content through multi-criteria evaluation.

## Features

- 🎯 Intelligent recommendation algorithm based on AHP (Analytic Hierarchy Process)
- 📊 Multi-dimensional video evaluation indicator system
- 🕷️ Bilibili video data crawling functionality
- 🔍 Intelligent video search and filtering
- 📈 Video data normalization processing
- 💾 Persistent storage of recommendation results

## Main Modules

- `ahp.py` - Core AHP algorithm implementation
- `spider.py` - Bilibili video data crawler
- `search.py` - Video search functionality
- `normalize_data.py` - Data normalization processing
- `video_operations.py` - Video operation related functions
- `server.py` - Server-side implementation
- `harry_mcp.py` - MCP server implementation

## Data Files

- `bilibili_recommendations.csv` - Bilibili recommended video data
- `bilibili_recommendations_with_title.csv` - Recommendation data with titles
- `ahp_matrix.csv` - AHP judgment matrix
- `user_data.txt` - User data
- `bilibili_video_recommendations_list.txt` - Recommended video list

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Run the crawler to fetch video data
2. Configure the AHP judgment matrix
3. Execute the recommendation algorithm
4. View recommendation results

## Technology Stack

- Python 3.x
- Pandas - Data processing
- NumPy - Numerical computation
- Requests - HTTP requests
- JSON - Data format

## Contributing

Welcome to submit Issues and Pull Requests to improve the project!

## License

MIT License 