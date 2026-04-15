from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os

def scrape_beike_zufang():
    """使用Selenium抓取贝壳找房深圳租房数据"""
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 启动浏览器
    print("正在启动浏览器...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 目标网址
        url = "https://sz.ke.com/zufang/"
        print(f"正在访问: {url}")
        driver.get(url)
        
        # 等待页面加载完成
        print("等待页面加载...")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content__list--item")))
        
        # 等待几秒确保JavaScript完全执行
        time.sleep(3)
        
        # 获取页面源码
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        
        # 查找所有房源信息项
        house_list = soup.find_all("div", class_="content__list--item")
        print(f"当前页面共找到 {len(house_list)} 套房源。")
        
        # 创建一个列表来存储所有房源数据
        all_houses_data = []
        
        # 遍历房源列表并提取信息
        for index, house in enumerate(house_list, 1):
            try:
                # 提取标题
                title_element = house.find("p", class_="content__list--item--title")
                if not title_element:
                    continue
                    
                title = title_element.text.strip()
                
                # 提取链接 - 查找标题的父级<a>标签
                link_tag = title_element.find_parent('a')
                if link_tag and link_tag.get('href'):
                    href = link_tag['href']
                    # 处理相对路径和绝对路径
                    if href.startswith('http'):
                        link = href
                    else:
                        link = "https://sz.ke.com" + href
                else:
                    # 备用方案：尝试在house元素中查找任何<a>标签
                    any_link = house.find('a', href=True)
                    if any_link:
                        href = any_link['href']
                        link = href if href.startswith('http') else "https://sz.ke.com" + href
                    else:
                        link = "N/A"
                
                # 提取描述信息（面积、户型等）
                desc_element = house.find("p", class_="content__list--item--des")
                desc = desc_element.text.strip().replace(" ", "").replace("\n", "") if desc_element else "暂无描述"
                
                # 提取价格
                price_element = house.find("span", class_="content__list--item-price")
                price = price_element.text.strip() if price_element else "价格面议"
                
                # 提取标签（可选）
                tags_element = house.find("p", class_="content__list--item--bottom")
                tags = []
                if tags_element:
                    tag_items = tags_element.find_all("i", class_="content__item__tag")
                    tags = [tag.text.strip() for tag in tag_items]
                
                house_data = {
                    "title": title,
                    "price": price,
                    "description": desc,
                    "link": link,
                    "tags": tags
                }
                all_houses_data.append(house_data)
                
                print(f"[{index}/{len(house_list)}] 已提取: {title[:30]}... | {price} | 链接: {link[:50]}...")
                
            except Exception as e:
                print(f"解析第{index}个房源时出错，已跳过。错误: {e}")
                continue
        
        print(f"\n成功解析 {len(all_houses_data)} 套房源。")
        
        # 确保data目录存在
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 将数据保存到JSON文件中
        output_path = os.path.join(data_dir, "beike_sz.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_houses_data, f, ensure_ascii=False, indent=4)
        
        print(f"数据已成功保存到 {output_path} 文件中。")
        print(f"共抓取 {len(all_houses_data)} 条房源数据")
        
        return all_houses_data
        
    except Exception as e:
        print(f"爬取过程中发生错误: {e}")
        return []
        
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    scrape_beike_zufang()
