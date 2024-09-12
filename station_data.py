import requests
import pandas as pd
import os

# 爬虫部分
## 没有任何反爬措施
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"已获得数据如下：\n{data}")
        return data
    else:
        print(f"无法访问，状态码: {response.status_code}")
        return None

# 数据处理部分
## 过滤关键字 "星子" 的数据
def filter_data(data, keyword):
    rows = data['data']['rows']
    filtered_rows = [row for row in rows if keyword in row['stnm']]
    return filtered_rows

## 删除无用列并汉化
## 新增调整顺序功能
def process_data(data):
    # 将数据转换为 DataFrame
    df = pd.DataFrame(data)

    # 删除不需要的列
    columns_to_drop = ['hTM', 'img', 'wptn', 'obhtztm', 'HTM', 'stcd', 'style', 'bsnm']
    df = df.drop(columns=columns_to_drop)

    # 汉化列名
    df = df.rename(columns={
        'tm': '记录时间',
        'county': '位置',
        'obhtz': '历史最高',
        'q': '流量',
        'cwrz': '距离警戒水位',
        'stnm': '记录站',
        'z': '水位',
        'wrz': '警戒水位'
    })
    
    # 调整列的顺序
    df = df[['记录时间', '位置', '记录站', '警戒水位', '水位', '距离警戒水位', '历史最高', '流量']]
    
    return df

## 保存数据到 Excel 文件
## 改为保存到"output目录下的Excel文件"
## 追加模式保存，防止覆盖数据
def save_to_excel(data):
    # 确保 "output" 文件夹存在，如果不存在则创建
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 设置保存路径
    file_path = os.path.join(output_dir, 'river_data.xlsx')
    
    df = pd.DataFrame(data)
    
    # 检查文件是否存在，存在则追加，不存在则创建新文件
    if os.path.exists(file_path):
        # 追加模式，保留原有数据
        with pd.ExcelWriter(file_path,engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, sheet_name='Sheet1', startrow=writer.sheets['Sheet1'].max_row, index=False, header=False)
    else:
        # 创建新文件
        df.to_excel(file_path, index=False)
    
    print(f"数据已保存到 {file_path}")

if __name__ == "__main__":
    url = 'http://111.75.205.67:7080/syq/rivermap/riverMapHandler'
    data = fetch_data(url)
    
    if data:
        # 过滤关键字 "星子" 的数据
        keyword = "星子"
        filtered_data = filter_data(data, keyword)
        
        if filtered_data:
            # 删除无用列并汉化剩余列，调整列顺序
            processed_data = process_data(filtered_data)
            
            # 保存到 "output" 文件夹中的 Excel 文件
            save_to_excel(processed_data)
        else:
            print(f"未找到包含关键字 '{keyword}' 的数据")
