import pandas as pd
import numpy as np
import os
# from tkinter import Tk, filedialog

# 读取文件
def normalize_data():
    # root = Tk()
    # root.withdraw()  # 隐藏主窗口

    file_path = "./bilibili_recommendations.csv"
    # if not os.path.isfile(file_path):
    #     with open(file_path, 'w') as f:
    #         f.write("")
    # if not os.path.isfile("bilibili_recommendations_with_title.csv"):
    #     with open("bilibili_recommendations_with_title.csv", 'w') as f:
    #         f.write("")
    # 读取CSV文件
    data = pd.read_csv(file_path, index_col=0)
    
    # print("数据集:\n", data)



    # 数据归一化
    def normalize(df):
        result = df.copy()
        for column in df.columns:
            col_sum = df[column].sum()
            result[column] = df[column] / col_sum

        return result

    # 进行归一化
    normalized_data = normalize(data)
    
    # 打印归一化后的数据

    return normalized_data,data.columns,data.index