from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os
import re

# 深圳区域列表
SZ_DISTRICTS = ['福田区', '罗湖区', '南山区', '盐田区', '宝安区', '龙岗区', '龙华区', '坪山区', '光明区', '大鹏新区']

def extract_district(text):
    """从文本中提取深圳区域"""
    for district in SZ_DISTRICTS:
        if district in text:
            return district
    # 尝试匹配不带"区"的
    district_map = {
        '福田': '福田区', '罗湖': '罗湖区', '南山': '南山区', '盐田': '盐田区',
        '宝安': '宝安区', '龙岗': '龙岗区', '龙华': '龙华区', '坪山': '坪山区',
        '光明': '光明区', '大鹏': '大鹏新区'
    }
    for key, value in district_map.items():
        if key in text:
            return value
    return "深圳"

def scrape_anjuke_zufang():
    """使用Selenium抓取安居客深圳租房数据"""
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    print("正在启动浏览器...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 安居客深圳租房
        url = "https://sz.zu.anjuke.com/"
        print(f"正在访问: {url}")
        driver.get(url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)
        
        # 获取页面源码
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        
        # 查找房源列表 - 安居客的列表项
        house_list = soup.find_all("div", class_=re.compile("list-item|zu-itemmod"))
        
        print(f"当前页面共找到 {len(house_list)} 套房源。")
        
        all_houses_data = []
        
        for index, house in enumerate(house_list[:30], 1):  # 限制30条
            try:
                # 提取标题
                title_element = house.find("a", class_=re.compile("title|house-title")) or house.find("h3")
                if not title_element:
                    continue
                title = title_element.text.strip()
                
                # 提取链接
                link_tag = house.find('a', href=True)
                if link_tag:
                    href = link_tag['href']
                    link = href if href.startswith('http') else f"https:{href}"
                else:
                    link = "N/A"
                
                # 提取价格
                price_element = house.find("span", class_=re.compile("price|strongbox")) or house.find("b", class_=re.compile("price"))
                price = price_element.text.strip() if price_element else "面议"
                if '元' not in price and '月' not in price:
                    price = f"{price} 元/月"
                
                # 提取描述（户型、面积等）
                desc_element = house.find("p", class_=re.compile("details-item|details")) or house.find("div", class_=re.compile("details"))
                base_desc = desc_element.text.strip().replace("\n", " ") if desc_element else "暂无描述"
                
                # 从标题中提取区域信息
                district = extract_district(title)
                
                # 组合描述
                desc = f"{district} | {base_desc}"
                
                # 提取标签
                tags = []
                tag_elements = house.find_all("span", class_=re.compile("tag|label"))
                for tag in tag_elements:
                    tag_text = tag.text.strip()
                    if tag_text:
                        tags.append(tag_text)
                
                house_data = {
                    "title": title,
                    "price": price,
                    "description": desc,
                    "link": link,
                    "tags": tags if tags else ["安居客"]
                }
                all_houses_data.append(house_data)
                
                print(f"[{index}] 已提取: {title[:30]}... | {district} | {price}")
                
            except Exception as e:
                print(f"解析第{index}个房源时出错: {e}")
                continue
        
        print(f"\n成功解析 {len(all_houses_data)} 套房源。")
        
        # 保存数据
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        output_path = os.path.join(data_dir, "anjuke_sz.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_houses_data, f, ensure_ascii=False, indent=4)
        
        print(f"数据已保存到 {output_path}")
        return all_houses_data
        
    except Exception as e:
        print(f"爬取过程中发生错误: {e}")
        return []
        
    finally:
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    scrape_anjuke_zufang()
