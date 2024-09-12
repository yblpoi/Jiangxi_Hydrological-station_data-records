import requests
import pandas as pd
import os

# 爬虫部分
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
def filter_data(data, keyword):
    rows = data['data']['rows']
    filtered_rows = [row for row in rows if keyword in row['stnm']]
    return filtered_rows

def process_data(data):
    df = pd.DataFrame(data)
    columns_to_drop = ['hTM', 'img', 'wptn', 'obhtztm', 'HTM', 'stcd', 'style', 'bsnm']
    df = df.drop(columns=columns_to_drop)
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
    df = df[['记录时间', '位置', '记录站', '警戒水位', '水位', '距离警戒水位', '历史最高', '流量']]
    return df

# 保存每个站点数据到单独的Sheet
def save_to_excel_per_station(data):
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_path = os.path.join(output_dir, 'river_data_per_station.xlsx')
    
    # 将数据按站点分组
    grouped_data = pd.DataFrame(data).groupby('stnm')

    # 使用 ExcelWriter 来将每个站点的数据保存到不同的Sheet中
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        for station_name, group_data in grouped_data:
            station_df = process_data(group_data.to_dict('records'))
            # 给每个Sheet命名为站点名
            station_df.to_excel(writer, sheet_name=station_name, index=False)
    
    print(f"每个水文站的数据已保存到 {file_path}")

if __name__ == "__main__":
    url = 'http://111.75.205.67:7080/syq/rivermap/riverMapHandler'
    data = fetch_data(url)
    
    if data:
        keyword = ""
        filtered_data = filter_data(data, keyword)
        
        if filtered_data:
            save_to_excel_per_station(filtered_data)
        else:
            print(f"未找到包含关键字 '{keyword}' 的数据")
