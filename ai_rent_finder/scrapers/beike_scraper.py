
import requests
from bs4 import BeautifulSoup
import json

# 目标网址
url = "https://sz.ke.com/zufang/"

# 模拟浏览器发送请求
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 发送GET请求
response = requests.get(url, headers=headers)
response.encoding = response.apparent_encoding # 解决乱码问题

# 检查请求是否成功
if response.status_code == 200:
    print("成功获取页面内容，开始解析...")
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, "lxml")
    
    # 查找所有房源信息项
    house_list = soup.find_all("div", class_="content__list--item")
    
    print(f"当前页面共找到 {len(house_list)} 套房源。")

    # 创建一个列表来存储所有房源数据
    all_houses_data = []

    # 遍历房源列表并提取信息
    for house in house_list:
        try:
            # 提取标题和链接
            title_element = house.find("p", class_="content__list--item--title")
            title = title_element.text.strip()
            
            link_tag = title_element.find_parent('a')
            link = "https://sz.ke.com" + link_tag['href'] if link_tag else "N/A"


            # 提取描述信息（面积、户型等）
            desc = house.find("p", class_="content__list--item--des").text.strip().replace(" ", "").replace("\n", "")

            # 提取价格
            price = house.find("span", class_="content__list--item-price").text.strip()
            
            house_data = {
                "title": title,
                "price": price,
                "description": desc,
                "link": link
            }
            all_houses_data.append(house_data)

            print(f"已提取: {title} | {price} | {desc}")

        except AttributeError as e:
            print(f"解析某个房源时出错，已跳过。错误: {e}")

    print(f"\n成功解析 {len(all_houses_data)} 套房源。")

    # 将数据保存到 data/beike_sz.json 文件中
    with open("data/beike_sz.json", "w", encoding="utf-8") as f:
        json.dump(all_houses_data, f, ensure_ascii=False, indent=4)
    
    print("数据已成功保存到 data/beike_sz.json 文件中。")

else:
    print(f"请求失败，状态码: {response.status_code}")


