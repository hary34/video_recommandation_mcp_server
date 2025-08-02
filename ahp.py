# import tkinter as tk  
import re  
import pandas as pd  
# from tkinter import ttk  
import numpy as np  
import normalize_data  
import os  
import scratch_datasets
tags=["艾尔登法环","法环","pvp","1.14","更新","r2","入侵"]
# Analytic hierarchy process 
results = normalize_data.normalize_data()  
normalized_data = results[0]  
indicators = list(results[1])  
indexs = list(results[2])  
target_videos=[]
def update_data(): 
    global results, normalized_data, indicators, indexs
    results = normalize_data.normalize_data()  
    normalized_data = results[0]  
    indicators = list(results[1])  
    indexs = list(results[2])  

def extract_bv_id(url):  
    """Extract BV ID from URL."""  
    match = re.search(r'/video/(BV\w+)', url)  
    return match.group(1) if match else None  

def load_matrix(file_path, num_items):  
    if os.path.exists(file_path):  
        return pd.read_csv(file_path, header=None).values.tolist()  
    else:  
        return [["" for _ in range(num_items)] for _ in range(num_items)]  
def append_best_video_to_file(best_video):  
    """Append the best video recommendation to a text file."""  
    with open('bilibili_video_recommendations_list.txt', 'a', encoding='utf-8') as f:  
        f.write(f"{best_video}\n")
def save_matrix(matrix, file_path): 
    # print("check") 
    df = pd.DataFrame(matrix)  
    df.to_csv(file_path, header=False, index=False) 
def filter_algorithem(rank,title,info,video_info):
    if rank<6:
        # added=False
        # flag=0
        # for i in tags:
            
        #     if i in title:
        #         flag+=1
        #         if flag>1 and not added:
                    
        #             append_best_video_to_file(info)
        #             added=True
        
        # 将完整的视频信息添加到 info 字典中
        info['stat'] = video_info.get('stat', {})
        info['owner'] = video_info.get('owner', {})
        info['duration'] = video_info.get('duration', 0)
        info['pubdate'] = video_info.get('pubdate', 0)
        
        target_videos.append(info)
        append_best_video_to_file(info)
        # for i in tags:
        #     if i in title:
        #         target_videos.append(info)
        #         append_best_video_to_file(info)
        #         break
        
            
            
def get_consistency_ratio_with_saved_matrix():  
    RI_table = [0.00, 0.00, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49] 
    matrix = load_matrix("ahp_matrix.csv", 1)
    num_items = len(matrix)

    np_matrix = np.array(matrix)  

    # Calculate eigenvalues  
    eigenvalues = np.linalg.eigvals(np_matrix)  
    max_eigenvalue = np.max(np.abs(eigenvalues))  

    # Calculate consistency index CI  
    CI = (max_eigenvalue - num_items) / (num_items - 1)  

    # Find matching RI from table  
    RI = RI_table[num_items - 1] if num_items - 1 < len(RI_table) else None  

    if RI is None:  
        # print("RI 未定义，请扩展 RI 表。")  
        return  

    # Calculate consistency ratio CR  
    CR = CI / RI  
    # print(f"一致性比例 CR: {CR:.3f}")  

    if CR >= 0.1:  
        pass
        # print("请修改判断矩阵直到CR小于0.1")  
    else:  
        # print("通过一致性检验")  
        # print("判断矩阵:\n", np_matrix)  

        # Column normalization  
        column_sums = np_matrix.sum(axis=0)  
        normalized_matrix = np_matrix / column_sums  

        # Calculate weight vector  
        weights = normalized_matrix.mean(axis=1)  
        # print("列归一化矩阵：\n", normalized_matrix)  
        # print("权重向量：\n", weights)  

        weights_ = np.array(weights)  
        data_array = normalized_data.to_numpy()  
        final_scores = data_array.dot(weights_)  

        final_scores = dict(zip(final_scores, indexs))  

        sorted_scores = sorted(final_scores.items(), key=lambda x: x[0], reverse=True)  

        # print("最终评分:", final_scores)  
        file_path_ = "./bilibili_recommendations_with_title.csv"
        
        data = pd.read_csv(file_path_, index_col=0)  

        best_video_info=""
        for rank, (score, url) in enumerate(sorted_scores, start=1):
            video_info=scratch_datasets.get_video_info(extract_bv_id(url=url))
            title=video_info['title']
            cover=video_info['pic']
            info={"Rank":rank, "Title" :title, "URL":url, "Score": score,"Cover":cover}
            # print(info)
            if rank==1:
                best_video_info=info

            # if rank>7:
            #     append_best_video_to_file(info)
            filter_algorithem(rank=rank,title=title,info=info,video_info=video_info)
        # print("最好的视频：",best_video_info)
        # append_best_video_to_file(best_video_info)
        # Save the matrix after successful validation  
        
def create_table(items, use_saved_matrix=False):  
    num_items = len(items)  
    # Random consistency index table  
    RI_table = [0.00, 0.00, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]  

    # Load previous matrix data  
    data = load_matrix("ahp_matrix.csv", num_items)  

    # If not using saved matrix, set diagonal values to 1  
    if not use_saved_matrix:  
        pass
        # for i in range(num_items):  
        #     data[i][i] = 1  

        # # Create main window  
        # root = tk.Tk()  
        # root.title("求权重")  
        # exit_button = tk.Button(root, text="Exit", command=root.quit)  
        # exit_button.pack()  

        # # Use Treeview to display the table  
        # columns = ["Row"] + items  
        # tree = ttk.Treeview(root, columns=columns, show='headings', height=num_items)  
        # tree.pack(fill=tk.BOTH, expand=True)  

        # # Define all column headers  
        # tree.heading("Row", text="Row")  
        # for col in items:  
        #     tree.heading(col, text=col)  

        # # Insert data rows  
        # for i, row in enumerate(data):  
        #     display_row = [items[i]] + row  
        #     tree.insert("", "end", iid=i, values=display_row)  

        # # Double-click event to create editable cell  
        # def on_double_click(event):  
        #     region = tree.identify('region', event.x, event.y)  

        #     if region != 'cell':  
        #         return  

        #     item = tree.selection()[0]  
        #     column = tree.identify_column(event.x)  
        #     column_index = int(column.replace("#", "")) - 1  

        #     # Disable editing first column (row titles) and diagonal  
        #     if column_index == 0 or column_index == int(item) + 1:  
        #         return  

        #     # Display input box  
        #     entry_popup(event, item, column_index)  

        # def entry_popup(event, item, column_index):  
        #     # Get the location and size of the cell  
        #     x, y, width, height = tree.bbox(item, column=f"#{column_index + 1}")  
        #     value = tree.set(item, column=f"#{column_index + 1}")  
        #     entry = tk.Entry(root)  
        #     entry.place(x=x, y=y, width=width, height=height)  
        #     entry.insert(0, value)  
        #     entry.focus()  

        #     def on_focus_out(event):  
        #         new_value = entry.get()  
        #         tree.set(item, column=f"#{column_index + 1}", value=new_value)  
        #         update_opposite_value(int(item), column_index - 1, new_value)  
        #         entry.destroy()  

        #     entry.bind("<FocusOut>", on_focus_out)  

        # def update_opposite_value(row, col, new_value):  
        #     # Update symmetric position with reciprocal value  
        #     try:  
        #         reciprocal = f"{1 / float(new_value):.3f}"  
        #     except ZeroDivisionError:  
        #         reciprocal = "inf"  
        #     except ValueError:  
        #         return  

        #     # Symmetric position: (row, col) -> (col, row)  
        #     tree.set(col, column=f"#{row + 2}", value=reciprocal)  

        # def get_consistency_ratio():  
        #     # Get matrix data  
        #     matrix = []  
        #     for i in range(num_items):  
        #         row = []  
        #         for j in range(1, num_items + 1):  
        #             value = tree.set(i, column=f"#{j + 1}")  # Skip row title column  
        #             try:  
        #                 row.append(float(value))  
        #             except ValueError:  
        #                 row.append(np.nan)  # Replace invalid values with NaN  
        #         matrix.append(row)  

        #     np_matrix = np.array(matrix)  

        #     # Calculate eigenvalues  
        #     eigenvalues = np.linalg.eigvals(np_matrix)  
        #     max_eigenvalue = np.max(np.abs(eigenvalues))  

        #     # Calculate consistency index CI  
        #     CI = (max_eigenvalue - num_items) / (num_items - 1)  

        #     # Find matching RI from table  
        #     RI = RI_table[num_items - 1] if num_items - 1 < len(RI_table) else None  

        #     if RI is None:  
        #         print("RI 未定义，请扩展 RI 表。")  
        #         return  

        #     # Calculate consistency ratio CR  
        #     CR = CI / RI  
        #     print(f"一致性比例 CR: {CR:.3f}")  

        #     if CR >= 0.1:  
        #         print("请修改判断矩阵直到CR小于0.1")  
        #     else:  
        #         print("通过一致性检验")  
        #         print("判断矩阵:\n", np_matrix)  
        #         save_matrix(np_matrix,"ahp_matrix.csv")
        #         # Column normalization  
        #         column_sums = np_matrix.sum(axis=0)  
        #         normalized_matrix = np_matrix / column_sums  

        #         # Calculate weight vector  
        #         weights = normalized_matrix.mean(axis=1)  
        #         print("列归一化矩阵：\n", normalized_matrix)  
        #         print("权重向量：\n", weights)  

        #         weights_ = np.array(weights)  
        #         data_array = normalized_data.to_numpy()  
        #         final_scores = data_array.dot(weights_)  

        #         final_scores = dict(zip(final_scores, indexs))  

        #         sorted_scores = sorted(final_scores.items(), key=lambda x: x[0], reverse=True)  

        #         print("最终评分:", final_scores)  
        #         file_path_ = "./bilibili_recommendations_with_title.csv"  
        #         data = pd.read_csv(file_path_, index_col=0)  

                
        #         best_video_info=""
        #         for rank, (score, url) in enumerate(sorted_scores, start=1):
        #             video_info=scratch_datasets.get_video_info(extract_bv_id(url=url))
        #             title=video_info['title']
        #             info=f"Rank {rank}, Title {title}, URL {url}, Score {score}"
        #             print(info)
        #             if rank==1:
        #                 best_video_info=info
        #             # if rank>7:
        #             #     append_best_video_to_file(info)
        #             filter_algorithem(rank=rank,title=title,video_info=video_info,info=info)
        #         print("最好的视频：",best_video_info)
        #         # append_best_video_to_file(best_video_info)
                    
                 

        # # Bind double-click event for cell editing  
        # tree.bind("<Double-1>", on_double_click)  

        # # Add button to get consistency ratio  
        # button = tk.Button(root, text="获取一致性比例", command=get_consistency_ratio)  
        # button.pack()  

        # # Start main event loop  
        # root.mainloop()  
    else:  
        # Directly calculate the consistency ratio without GUI  
        get_consistency_ratio_with_saved_matrix()  

# Usage example: to use the saved matrix directly set the flag to True  
def create_table_by_batch(mode):
    update_data()  
    create_table(indicators, use_saved_matrix=mode)
    return target_videos
    