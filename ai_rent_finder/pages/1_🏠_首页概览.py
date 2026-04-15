import streamlit as st
import pandas as pd
from core.analyzer import load_house_data, get_summary_suggestion
import os
import re
import json
import random
from datetime import datetime

# --- 页面配置和CSS注入 ---
st.set_page_config(page_title="首页概览 - AI租房决策系统", layout="wide")

def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# 尝试从根目录加载CSS
local_css("../style.css")

# --- 平台选择 ---
st.sidebar.header("🏠 选择房源平台")
platform_options = {
    "贝壳找房": "beike_sz.json",
    "58同城": "58_sz.json", 
    "安居客": "anjuke_sz.json",
    "自如": "ziroom_sz.json"
}
selected_platform = st.sidebar.selectbox(
    "选择平台",
    options=list(platform_options.keys()),
    index=0
)
data_file = platform_options[selected_platform]

# --- 优化：添加加载状态 ---
with st.spinner(f"🚀 正在从【{selected_platform}】加载房源数据，请稍候..."):
    @st.cache_data
    def load_and_preprocess_data(file_path):
        df = pd.DataFrame(load_house_data(f"data/{file_path}"))
        if df.empty:
            return df
        
        def parse_price(price_str):
            numbers = re.findall(r'\d+', str(price_str))
            return int(numbers[0]) if numbers else 0
        
        df['price_num'] = df['price'].apply(parse_price)
        # 添加平台标识
        df['platform'] = selected_platform
        return df

    houses_df = load_and_preprocess_data(data_file)

if houses_df.empty:
    st.warning(f"⚠️ 【{selected_platform}】暂无数据，请先运行对应爬虫或选择其他平台。")
else:
    st.success(f"✅ 【{selected_platform}】数据加载完成！共 {len(houses_df)} 条房源")

# --- 页面标题 ---
st.title("首页概览")
st.write("在这里您可以快速筛选房源，并获得AI的初步建议。")

# --- 搜索与筛选卡片 ---
st.markdown("""
<div class="card">
    <h4>智能搜索与筛选</h4>
    <p>输入您的核心需求，快速锁定目标房源。</p>
</div>
""", unsafe_allow_html=True)

# 使用列布局来组织输入框
col1, col2 = st.columns(2)
with col1:
    budget_min = st.number_input("最低预算 (元/月)", min_value=0, value=0, step=100, format="%d")
with col2:
    budget_max = st.number_input("最高预算 (元/月)", min_value=0, value=10000, step=100, format="%d")

# 深圳统一区域列表
SZ_DISTRICTS = ['不限', '福田区', '罗湖区', '南山区', '盐田区', '宝安区', '龙岗区', '龙华区', '坪山区', '光明区', '大鹏新区']

col1, col2 = st.columns(2)
with col1:
    area = st.selectbox("选择区域", options=SZ_DISTRICTS)
with col2:
    layout_options = ["不限", "1室", "2室", "3室", "4室", "5室及以上"]
    layout = st.selectbox("选择户型", options=layout_options)

st.divider()

# 初始化session state
if 'filtered_houses' not in st.session_state:
    st.session_state.filtered_houses = pd.DataFrame()

# 收藏功能相关函数
FAVORITES_FILE = "data/favorites.json"

def load_favorites():
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_favorites(favorites):
    os.makedirs("data", exist_ok=True)
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def add_to_favorites(house_data):
    favorites = load_favorites()
    # 生成唯一ID
    house_id = f"house_{datetime.now().timestamp()}"
    
    # 提取户型和面积信息
    description = str(house_data.get('description', ''))
    layout = "未知"
    area_size = "未知"
    
    # 尝试从描述中提取户型
    layout_match = re.search(r'(\d+室\d*厅?)', description)
    if layout_match:
        layout = layout_match.group(1)
    
    # 尝试从描述中提取面积
    area_match = re.search(r'(\d+)㎡', description)
    if area_match:
        area_size = f"{area_match.group(1)}㎡"
    
    # 尝试从描述中提取区域
    district = "未知"
    for d in ['福田区', '罗湖区', '南山区', '盐田区', '宝安区', '龙岗区', '龙华区', '坪山区', '光明区', '大鹏新区']:
        if d in description:
            district = d
            break
    
    # 新收藏的房源默认未评分，AI评估后才计算分数
    ai_score = None  # None表示未评分
    
    # 根据描述生成基础标签（不涉及评分）
    tags = []
    if '地铁' in description or '近地铁' in description:
        tags.append("近地铁")
    if '精装修' in description or '精装' in description:
        tags.append("精装修")
    if '拎包入住' in description:
        tags.append("拎包入住")
    if not tags:
        tags.append("待评估")
    
    new_favorite = {
        "id": house_id,
        "title": house_data.get('title', '未知房源'),
        "price": house_data.get('price_num', 0),
        "layout": layout,
        "area": area_size,
        "district": district,
        "community": "未知小区",
        "ai_score": None,  # 默认未评分
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "image": "https://via.placeholder.com/400x300/334155/475569?text=房源图片",
        "tags": tags[:3],  # 最多3个标签
        "link": house_data.get('link', ''),
        "description": description
    }
    
    favorites.append(new_favorite)
    save_favorites(favorites)
    return True

def remove_from_favorites(link):
    """从收藏中移除房源"""
    favorites = load_favorites()
    favorites = [f for f in favorites if f.get('link') != link]
    save_favorites(favorites)
    return True

def calculate_ai_score(house_data, description):
    """
    基于房源数据计算AI评分 (0-100分)
    评分维度：
    1. 价格合理性 (30分)
    2. 户型实用性 (25分) 
    3. 区域便利性 (25分)
    4. 信息完整度 (20分)
    """
    score = 0
    
    # 1. 价格合理性评分 (30分)
    price = house_data.get('price_num', 0)
    district = ""
    for d in ['福田区', '罗湖区', '南山区', '盐田区', '宝安区', '龙岗区', '龙华区', '坪山区', '光明区', '大鹏新区']:
        if d in description:
            district = d
            break
    
    # 深圳各区域租金参考 (元/月/㎡)
    district_avg_price = {
        '福田区': 120, '南山区': 115, '罗湖区': 90, '盐田区': 70,
        '宝安区': 65, '龙岗区': 55, '龙华区': 60, '坪山区': 45, '光明区': 50, '大鹏新区': 40
    }
    
    # 提取面积 - 支持多种格式：㎡、平米、平方米
    area = 50  # 默认50㎡
    area_match = re.search(r'(\d+\.?\d*)\s*㎡', description)
    if not area_match:
        area_match = re.search(r'(\d+\.?\d*)\s*平米', description)
    if not area_match:
        area_match = re.search(r'(\d+\.?\d*)\s*平方米', description)
    if area_match:
        area = float(area_match.group(1))
    
    # 价格评分
    if price > 0 and district and area > 0:
        avg_price = district_avg_price.get(district, 70)
        price_per_sqm = price / area
        
        # 价格越接近区域均价，得分越高
        if price_per_sqm <= avg_price * 0.8:
            score += 30  # 价格很优惠
        elif price_per_sqm <= avg_price * 1.0:
            score += 25  # 价格合理
        elif price_per_sqm <= avg_price * 1.2:
            score += 18  # 价格略高
        elif price_per_sqm <= avg_price * 1.5:
            score += 10  # 价格偏高
        else:
            score += 5   # 价格过高
    else:
        # 无法判断价格，根据区域给基础分
        score += 20 if district else 15
    
    # 2. 户型实用性评分 (25分)
    layout_match = re.search(r'(\d+)室', description)
    if layout_match:
        rooms = int(layout_match.group(1))
        if area > 0 and rooms > 0:
            area_per_room = area / rooms
            # 人均面积在15-25㎡比较舒适
            if 15 <= area_per_room <= 25:
                score += 25
            elif 10 <= area_per_room < 15 or 25 < area_per_room <= 35:
                score += 20
            elif area_per_room > 35:
                score += 18  # 面积过大，可能浪费
            else:
                score += 12  # 面积过小，拥挤
        else:
            score += 15
    else:
        score += 10  # 无法判断户型
    
    # 3. 区域便利性评分 (25分)
    convenience_keywords = {
        '地铁': 8, '公交站': 5, '近地铁': 8, '地铁口': 8,
        '商圈': 5, '购物中心': 5, '超市': 3, '便利店': 3,
        '医院': 5, '诊所': 3, '学校': 4, '幼儿园': 3,
        '公园': 4, '健身房': 3, '菜市场': 3
    }
    
    convenience_score = 0
    for keyword, points in convenience_keywords.items():
        if keyword in description:
            convenience_score += points
    
    score += min(convenience_score, 25)  # 最高25分
    
    # 4. 信息完整度评分 (20分)
    info_score = 0
    if area_match: info_score += 5
    if layout_match: info_score += 5
    if district: info_score += 5
    if len(description) > 50: info_score += 5
    
    score += info_score
    
    # 添加一些随机性 (±5分)，避免评分过于固定
    random_factor = random.randint(-5, 5)
    score = max(0, min(100, score + random_factor))
    
    return round(score)


def recalculate_all_scores():
    """重新计算所有收藏房源的AI评分"""
    favorites = load_favorites()
    updated = False
    
    for house in favorites:
        # 创建模拟的house_data
        house_data = {
            'price_num': house.get('price', 0)
        }
        description = house.get('description', '')
        
        # 重新计算评分
        new_score = calculate_ai_score(house_data, description)
        
        # 如果评分有变化，更新它
        if house.get('ai_score') != new_score:
            house['ai_score'] = new_score
            updated = True
            
            # 更新标签
            tags = []
            if new_score >= 85:
                tags.append("超值推荐")
            elif new_score >= 75:
                tags.append("性价比高")
            elif new_score >= 60:
                tags.append("可以考虑")
            else:
                tags.append("需谨慎")
            
            if '地铁' in description or '近地铁' in description:
                tags.append("近地铁")
            if '精装修' in description or '精装' in description:
                tags.append("精装修")
            if '拎包入住' in description:
                tags.append("拎包入住")
            
            house['tags'] = tags[:3]
    
    if updated:
        save_favorites(favorites)
        return True
    return False

if st.button("🔍 开始查找", use_container_width=True, type="primary"):
    filtered_df = houses_df.copy()
    
    # 预算筛选
    if budget_max > 0:
        filtered_df = filtered_df[(filtered_df['price_num'] >= budget_min) & (filtered_df['price_num'] <= budget_max)]
    
    # 区域筛选
    if area != "不限":
        filtered_df = filtered_df[filtered_df['description'].str.contains(area, na=False)]
        
    # 户型筛选
    if layout != "不限":
        if "及以上" in layout:
            num = int(layout[0])
            # 这是一个简化的匹配，实际可能需要更复杂的正则
            filtered_df = filtered_df[filtered_df['description'].str.contains(f'[{num}-9]室', na=False)]
        else:
            filtered_df = filtered_df[filtered_df['description'].str.contains(layout, na=False)]
            
    st.session_state.filtered_houses = filtered_df

# --- 房源展示区 ---
st.subheader(f"为您找到 {len(st.session_state.filtered_houses)} 套房源")

if not st.session_state.filtered_houses.empty:
    # 加载当前收藏列表
    current_favorites = load_favorites()
    favorite_links = {f.get('link', '') for f in current_favorites}
    
    # 逐条展示房源，每条都有收藏按钮
    for idx, (_, house) in enumerate(st.session_state.filtered_houses.iterrows()):
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.markdown(f"**{house['title']}**")
                st.markdown(f"💰 {house['price']} | 📍 {house.get('description', '暂无描述')[:50]}...")
            
            with col2:
                # 查看详情链接
                if house.get('link'):
                    st.markdown(f"[查看详情]({house['link']})")
            
            with col3:
                # 收藏/取消收藏按钮
                is_favorited = house.get('link', '') in favorite_links
                if is_favorited:
                    if st.button("❤️ 已收藏", key=f"fav_{idx}"):
                        if remove_from_favorites(house.get('link', '')):
                            st.success("✅ 已取消收藏！")
                            st.rerun()
                else:
                    if st.button("🤍 收藏", key=f"fav_{idx}"):
                        if add_to_favorites(house.to_dict()):
                            st.success("✅ 收藏成功！")
                            st.rerun()
        
        st.divider()
    
    # AI总体建议按钮
    if st.button("💡 获取AI总体建议"):
        with st.spinner("AI正在分析您的筛选结果，请稍候..."):
            try:
                suggestion = get_summary_suggestion(st.session_state.filtered_houses)
                st.markdown("### 🤖 AI 租房策略师")
                st.markdown(f'<div class="card-ai">{suggestion}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AI分析时出现错误: {e}")
else:
    st.info('请调整筛选条件后点击"开始查找"。')
