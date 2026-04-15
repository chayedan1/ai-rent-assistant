import streamlit as st
import pandas as pd
import json
import os
import re
import random
from datetime import datetime, timedelta
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# --- 页面配置 ---
st.set_page_config(page_title="房源收藏与管理 - AI租房决策系统", layout="wide")

# --- 加载CSS ---
def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

local_css("../style.css")

# --- 自定义深色科技风样式 ---
st.markdown("""
<style>
/* 页面整体背景 */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

/* 标题样式 */
.page-title {
    font-size: 32px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 8px;
    text-align: center;
}

.page-subtitle {
    font-size: 16px;
    color: #94a3b8;
    text-align: center;
    margin-bottom: 32px;
}

/* 筛选栏样式 */
.filter-bar {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(71, 85, 105, 0.5);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 24px;
}

/* 房源卡片 */
.house-card {
    background: rgba(30, 41, 59, 0.9);
    border: 1px solid rgba(71, 85, 105, 0.3);
    border-radius: 16px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.house-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    border-color: rgba(59, 130, 246, 0.5);
}

.house-card-image {
    width: 100%;
    height: 180px;
    object-fit: cover;
    background: linear-gradient(135deg, #334155 0%, #475569 100%);
}

.house-card-content {
    padding: 16px;
}

.house-card-title {
    font-size: 18px;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 8px;
}

.house-card-info {
    font-size: 14px;
    color: #94a3b8;
    margin-bottom: 4px;
}

.house-card-price {
    font-size: 24px;
    font-weight: 700;
    color: #f97316;
    margin: 12px 0;
}

/* AI评分 */
.ai-score {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 12px 0;
}

.ai-score-label {
    font-size: 13px;
    color: #64748b;
}

.ai-score-value {
    font-size: 16px;
    font-weight: 600;
    color: #10b981;
}

.ai-score-bar {
    flex: 1;
    height: 6px;
    background: rgba(71, 85, 105, 0.5);
    border-radius: 3px;
    overflow: hidden;
}

.ai-score-fill {
    height: 100%;
    background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
    border-radius: 3px;
    transition: width 0.5s ease;
}

/* 收藏时间 */
.collect-time {
    font-size: 12px;
    color: #64748b;
    margin-top: 8px;
}

/* 操作按钮组 */
.action-buttons {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    border-top: 1px solid rgba(71, 85, 105, 0.3);
}

.action-btn {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #60a5fa;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
}

.action-btn:hover {
    background: rgba(59, 130, 246, 0.2);
    border-color: rgba(59, 130, 246, 0.5);
}

.action-btn-danger {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #f87171;
}

.action-btn-danger:hover {
    background: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.5);
}

.action-btn-success {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
}

.action-btn-success:hover {
    background: rgba(16, 185, 129, 0.2);
    border-color: rgba(16, 185, 129, 0.5);
}

/* 复选框样式 */
.house-checkbox {
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 10;
}

/* 批量操作栏 */
.batch-actions {
    background: rgba(30, 41, 59, 0.95);
    border: 1px solid rgba(71, 85, 105, 0.5);
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* 模态框样式 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-content {
    background: #1e293b;
    border: 1px solid rgba(71, 85, 105, 0.5);
    border-radius: 16px;
    padding: 24px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

/* 星级评分 */
.stars {
    color: #fbbf24;
    font-size: 16px;
}

/* 空状态 */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #64748b;
}

.empty-state-icon {
    font-size: 64px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# --- 数据文件路径 ---
FAVORITES_FILE = "data/favorites.json"
REMINDERS_FILE = "data/reminders.json"

# --- 初始化数据文件 ---
def init_data_files():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

init_data_files()

# --- 加载收藏数据 ---
def load_favorites():
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# --- 保存收藏数据 ---
def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

# --- 加载提醒数据 ---
def load_reminders():
    try:
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# --- 保存提醒数据 ---
def save_reminders(reminders):
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)

# --- AI评分算法 ---
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
    if price == 0:
        price = house_data.get('price', 0)
    
    # 从description中提取区域
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
    area = 0
    area_match = re.search(r'(\d+\.?\d*)\s*㎡', description)
    if not area_match:
        area_match = re.search(r'(\d+\.?\d*)\s*平米', description)
    if not area_match:
        area_match = re.search(r'(\d+\.?\d*)\s*平方米', description)
    if area_match:
        area = float(area_match.group(1))
    
    # 价格评分 (30分)
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
    elif price > 0 and area > 0:
        # 有价格和面积但没有区域，给中等分
        score += 18
    elif district:
        # 只有区域信息，给基础分
        score += 12
    else:
        # 完全没有价格相关信息
        score += 8
    
    # 2. 户型实用性评分 (25分)
    layout_match = re.search(r'(\d+)室', description)
    if layout_match and area > 0:
        rooms = int(layout_match.group(1))
        if rooms > 0:
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
    elif layout_match:
        # 有户型但没有面积
        score += 15
    elif area > 0:
        # 有面积但没有户型
        score += 12
    else:
        score += 8  # 无法判断户型
    
    # 3. 区域便利性评分 (25分)
    convenience_keywords = {
        '地铁': 8, '公交站': 5, '近地铁': 8, '地铁口': 8,
        '商圈': 5, '购物中心': 5, '超市': 3, '便利店': 3,
        '医院': 5, '诊所': 3, '学校': 4, '幼儿园': 3,
        '公园': 4, '健身房': 3, '菜市场': 3,
        '拎包入住': 5, '精装修': 4, '家电齐全': 4
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
    
    # 确保最低有30分的基础分（避免数据不全时分数过低）
    score = max(score, 30)
    
    # 添加一些随机性 (±5分)，避免评分过于固定
    random_factor = random.randint(-5, 5)
    score = max(0, min(100, score + random_factor))
    
    return round(score)

# --- 页面标题 ---
st.markdown('<div class="page-title">🏠 我的房源收藏库</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">收藏心仪房源，AI帮你管理、对比、提醒</div>', unsafe_allow_html=True)

# --- 初始化Session State ---
# 每次页面加载都重新读取收藏数据，确保与首页同步
st.session_state.favorites = load_favorites()
if "selected_houses" not in st.session_state:
    st.session_state.selected_houses = []
if "show_compare" not in st.session_state:
    st.session_state.show_compare = False
if "show_evaluate" not in st.session_state:
    st.session_state.show_evaluate = False
if "evaluate_house" not in st.session_state:
    st.session_state.evaluate_house = None
if "show_reminder" not in st.session_state:
    st.session_state.show_reminder = False
if "reminder_house" not in st.session_state:
    st.session_state.reminder_house = None

# --- 模拟数据（如果没有收藏数据） ---
if not st.session_state.favorites:
    st.session_state.favorites = [
        {
            "id": "1",
            "title": "福田中心区精装两房",
            "price": 6500,
            "layout": "2室1厅",
            "area": "75㎡",
            "district": "福田区",
            "community": "皇庭世纪",
            "ai_score": 88,
            "collected_at": "2025-04-10 14:30",
            "image": "https://via.placeholder.com/400x300/334155/475569?text=房源图片",
            "tags": ["近地铁", "精装修", "南向"]
        },
        {
            "id": "2", 
            "title": "南山科技园单间公寓",
            "price": 4200,
            "layout": "1室0厅",
            "area": "35㎡",
            "district": "南山区",
            "community": "大冲新城花园",
            "ai_score": 82,
            "collected_at": "2025-04-11 09:15",
            "image": "https://via.placeholder.com/400x300/334155/475569?text=房源图片",
            "tags": ["近地铁", "电梯房", "新小区"]
        },
        {
            "id": "3",
            "title": "罗湖国贸商圈三房",
            "price": 7800,
            "layout": "3室2厅",
            "area": "98㎡",
            "district": "罗湖区",
            "community": "金光华广场",
            "ai_score": 85,
            "collected_at": "2025-04-11 16:45",
            "image": "https://via.placeholder.com/400x300/334155/475569?text=房源图片",
            "tags": ["商圈房", "交通便利", "配套完善"]
        }
    ]
    save_favorites(st.session_state.favorites)

# --- 筛选栏 ---
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    price_range = st.selectbox(
        "价格区间",
        options=["不限", "3000以下", "3000-5000", "5000-7000", "7000-10000", "10000以上"],
        key="filter_price"
    )

with filter_col2:
    district_filter = st.selectbox(
        "区域",
        options=["不限", "福田区", "罗湖区", "南山区", "宝安区", "龙岗区", "龙华区"],
        key="filter_district"
    )

with filter_col3:
    layout_filter = st.selectbox(
        "户型",
        options=["不限", "1室", "2室", "3室", "4室及以上"],
        key="filter_layout"
    )

with filter_col4:
    score_filter = st.selectbox(
        "AI评分",
        options=["不限", "90分以上", "80-90分", "70-80分", "70分以下"],
        key="filter_score"
    )

st.markdown('</div>', unsafe_allow_html=True)

# --- 筛选逻辑 ---
filtered_favorites = st.session_state.favorites.copy()

if price_range != "不限":
    if price_range == "3000以下":
        filtered_favorites = [h for h in filtered_favorites if h["price"] < 3000]
    elif price_range == "3000-5000":
        filtered_favorites = [h for h in filtered_favorites if 3000 <= h["price"] < 5000]
    elif price_range == "5000-7000":
        filtered_favorites = [h for h in filtered_favorites if 5000 <= h["price"] < 7000]
    elif price_range == "7000-10000":
        filtered_favorites = [h for h in filtered_favorites if 7000 <= h["price"] < 10000]
    elif price_range == "10000以上":
        filtered_favorites = [h for h in filtered_favorites if h["price"] >= 10000]

if district_filter != "不限":
    filtered_favorites = [h for h in filtered_favorites if h["district"] == district_filter]

if layout_filter != "不限":
    if layout_filter == "4室及以上":
        filtered_favorites = [h for h in filtered_favorites if h["layout"].startswith("4") or h["layout"].startswith("5")]
    else:
        filtered_favorites = [h for h in filtered_favorites if h["layout"].startswith(layout_filter[0])]

if score_filter != "不限":
    if score_filter == "90分以上":
        filtered_favorites = [h for h in filtered_favorites if h["ai_score"] >= 90]
    elif score_filter == "80-90分":
        filtered_favorites = [h for h in filtered_favorites if 80 <= h["ai_score"] < 90]
    elif score_filter == "70-80分":
        filtered_favorites = [h for h in filtered_favorites if 70 <= h["ai_score"] < 80]
    elif score_filter == "70分以下":
        filtered_favorites = [h for h in filtered_favorites if h["ai_score"] < 70]

# --- 批量操作栏 ---
if len(st.session_state.selected_houses) > 0:
    st.markdown(f"""
    <div class="batch-actions">
        <span style="color: #f8fafc;">已选择 {len(st.session_state.selected_houses)} 套房源</span>
        <div style="display: flex; gap: 12px;">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 AI批量对比", type="primary", use_container_width=True):
            if len(st.session_state.selected_houses) >= 2:
                st.session_state.show_compare = True
            else:
                st.warning("请至少选择2套房源进行对比")
    with col2:
        if st.button("❌ 取消选择", use_container_width=True):
            st.session_state.selected_houses = []
            st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# --- 房源卡片网格 ---
if not filtered_favorites:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📭</div>
        <div style="font-size: 18px; margin-bottom: 8px;">暂无收藏的房源</div>
        <div>快去首页搜索并收藏心仪的房源吧！</div>
    </div>
    """, unsafe_allow_html=True)
else:
    # 每行显示3个卡片
    cols = st.columns(3)
    for idx, house in enumerate(filtered_favorites):
        with cols[idx % 3]:
            # 检查是否被选中
            is_selected = house["id"] in st.session_state.selected_houses
            
            # 截断标题，最多显示2行
            title = house['title'][:30] + "..." if len(house['title']) > 30 else house['title']
            
            # 使用容器创建卡片效果 - 固定高度
            with st.container():
                # 标题 - 固定高度区域
                st.markdown(f"""
                <div style="height: 45px; overflow: hidden; margin-bottom: 8px;">
                    <strong>{title}</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # 信息
                st.caption(f"{house['community']} · {house['district']}")
                st.caption(f"{house['layout']} · {house['area']}")
                
                # 价格
                st.markdown(f"<h4 style='color: #f97316; margin: 8px 0;'>¥{house['price']}/月</h4>", unsafe_allow_html=True)
                
                # AI评分 - 使用进度条
                if house.get('ai_score') is not None:
                    st.progress(house['ai_score'] / 100, text=f"AI评分: {house['ai_score']}分")
                else:
                    st.info("📊 AI评分: 未评估")
                
                # 收藏时间
                st.caption(f"📅 收藏于 {house['collected_at']}")
                
                st.divider()
            
            # 操作按钮
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
            
            with btn_col1:
                # 选择复选框
                if st.checkbox("选择", key=f"select_{house['id']}", value=is_selected):
                    if house["id"] not in st.session_state.selected_houses:
                        st.session_state.selected_houses.append(house["id"])
                        st.rerun()
                else:
                    if house["id"] in st.session_state.selected_houses:
                        st.session_state.selected_houses.remove(house["id"])
                        st.rerun()
            
            with btn_col2:
                if st.button("📊 AI评估", key=f"eval_{house['id']}", use_container_width=True):
                    st.session_state.evaluate_house = house
                    st.session_state.show_evaluate = True
                    st.rerun()
            
            with btn_col3:
                if st.button("⏰ 提醒", key=f"remind_{house['id']}", use_container_width=True):
                    st.session_state.reminder_house = house
                    st.session_state.show_reminder = True
                    st.rerun()
            
            with btn_col4:
                if st.button("取消", key=f"remove_{house['id']}", use_container_width=True):
                    st.session_state.favorites = [h for h in st.session_state.favorites if h["id"] != house["id"]]
                    save_favorites(st.session_state.favorites)
                    if house["id"] in st.session_state.selected_houses:
                        st.session_state.selected_houses.remove(house["id"])
                    st.success("✅ 已取消收藏！")
                    st.rerun()

# --- AI批量对比模态框 ---
if st.session_state.show_compare and len(st.session_state.selected_houses) >= 2:
    selected_houses_data = [h for h in st.session_state.favorites if h["id"] in st.session_state.selected_houses]
    
    # 创建对比弹窗容器
    with st.container():
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.95); border-radius: 16px; padding: 24px; margin: 20px 0; border: 1px solid rgba(148, 163, 184, 0.2);">
        """, unsafe_allow_html=True)
        
        # 标题和关闭按钮放在同一行
        col_title, col_close = st.columns([5, 1])
        with col_title:
            st.markdown("<h3 style='color: #f8fafc; margin: 0;'>📊 AI批量对比分析</h3>", unsafe_allow_html=True)
        with col_close:
            if st.button("❌ 关闭", key="close_compare", use_container_width=True):
                st.session_state.show_compare = False
                st.rerun()
        
        st.divider()
        
        # 对比表格
        compare_data = []
        for house in selected_houses_data[:3]:  # 最多对比3套
            ai_score_display = f"{house['ai_score']}分" if house.get('ai_score') is not None else "未评估"
            compare_data.append({
                "房源": house["title"][:20] + "..." if len(house["title"]) > 20 else house["title"],
                "价格": f"¥{house['price']}/月",
                "户型": house["layout"],
                "区域": house["district"],
                "AI评分": ai_score_display
            })
        
        st.dataframe(pd.DataFrame(compare_data), use_container_width=True, hide_index=True)
        
        st.divider()
        
        # AI对比分析
        st.markdown("<h4 style='color: #60a5fa; margin: 16px 0;'>🤖 AI对比分析报告</h4>", unsafe_allow_html=True)
        
        with st.spinner("🤖 AI正在生成对比报告，请稍候..."):
            try:
                llm = Ollama(model="qwen3.5:9b")
                
                houses_info = "\n\n".join([
                    f"房源{i+1}：{h['title']}\n- 价格：¥{h['price']}/月\n- 户型：{h['layout']}\n- 区域：{h['district']}\n- AI评分：{h['ai_score'] if h.get('ai_score') is not None else '未评估'}分"
                    for i, h in enumerate(selected_houses_data[:3])
                ])
                
                prompt = f"""作为租房专家，请对以下房源进行多维度对比分析：

{houses_info}

请从以下维度进行分析：
1. 性价比对比（价格与面积、配置的匹配度）
2. 通勤便利性（根据区域判断）
3. 潜在风险提示
4. 最终推荐及理由

请用中文输出结构化的对比报告。"""
                
                response = llm.invoke(prompt)
                
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.8); border-radius: 12px; padding: 20px; margin-top: 10px; color: #e2e8f0; line-height: 1.8;">
                    {response}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ AI分析失败：{str(e)}")
                st.info("💡 提示：请确保Ollama服务已启动，并且已下载qwen3.5:9b模型")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- AI房源评估模态框 ---
if st.session_state.show_evaluate and st.session_state.evaluate_house:
    # 通过ID从当前favorites中查找最新的房源数据
    evaluate_house_id = st.session_state.evaluate_house['id']
    house = None
    for h in st.session_state.favorites:
        if h['id'] == evaluate_house_id:
            house = h
            break
    
    # 如果找不到房源（可能被删除了），关闭弹窗
    if house is None:
        st.session_state.show_evaluate = False
        st.session_state.evaluate_house = None
        st.rerun()
    
    # 创建评估弹窗容器
    with st.container():
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.95); border-radius: 16px; padding: 24px; margin: 20px 0; border: 1px solid rgba(148, 163, 184, 0.2);">
        """, unsafe_allow_html=True)
        
        # 标题和关闭按钮放在同一行
        col_title, col_close = st.columns([5, 1])
        with col_title:
            title = house['title'][:25] + "..." if len(house['title']) > 25 else house['title']
            st.markdown(f"<h3 style='color: #f8fafc; margin: 0;'>📊 {title} - AI专属评估</h3>", unsafe_allow_html=True)
        with col_close:
            if st.button("❌ 关闭", key="close_evaluate", use_container_width=True):
                st.session_state.show_evaluate = False
                st.session_state.evaluate_house = None
                st.rerun()
        
        st.divider()
        
        # 如果还未评分，先计算评分
        if house.get('ai_score') is None:
            # 计算AI评分
            house_data = {'price_num': house.get('price', 0)}
            description = house.get('description', '')
            
            # 调试信息
            st.write(f"调试 - 房源ID: {house.get('id')}")
            st.write(f"调试 - 价格: {house.get('price')}")
            st.write(f"调试 - 描述: {description[:50]}...")
            
            with st.spinner("🤖 AI正在计算评分..."):
                new_score = calculate_ai_score(house_data, description)
                
                # 调试信息
                st.write(f"调试 - 计算出的评分: {new_score}")
                
                # 更新房源评分
                for i, h in enumerate(st.session_state.favorites):
                    if h['id'] == house['id']:
                        st.session_state.favorites[i]['ai_score'] = new_score
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
                        
                        st.session_state.favorites[i]['tags'] = tags[:3]
                        break
                
                save_favorites(st.session_state.favorites)
            
            # 显示成功消息并刷新
            st.success(f"✅ AI评分完成：{new_score}分")
            st.rerun()
        
        # 房源信息摘要
        score_display = f"{house['ai_score']}分" if house.get('ai_score') is not None else "未评分"
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.6); border-radius: 8px; padding: 12px; margin-bottom: 16px; color: #94a3b8;">
            💰 ¥{house['price']}/月 | 🏠 {house['layout']} | 📍 {house['district']} | ⭐ AI评分: {score_display}
        </div>
        """, unsafe_allow_html=True)
        
        # AI评估分析
        with st.spinner("🤖 AI正在生成评估报告，请稍候..."):
            try:
                llm = Ollama(model="qwen3.5:9b")
                
                score_text = f"{house['ai_score']}分" if house.get('ai_score') is not None else "未评分"
                
                prompt = f"""作为租房专家，请对以下房源进行深度分析：

房源信息：
- 标题：{house['title']}
- 价格：¥{house['price']}/月
- 户型：{house['layout']}
- 面积：{house['area']}
- 区域：{house['district']}
- 小区：{house['community']}
- AI评分：{score_text}

请从以下维度进行分析：
1. 房源优缺点分析
2. 砍价空间评估及建议
3. 潜在风险点及避坑指南
4. 适合人群推荐
5. 最终建议（是否值得租）

请用中文输出结构化的评估报告。"""
                
                response = llm.invoke(prompt)
                
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.8); border-radius: 12px; padding: 20px; color: #e2e8f0; line-height: 1.8;">
                    {response}
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ AI评估失败：{str(e)}")
                st.info("💡 提示：请确保Ollama服务已启动，并且已下载qwen3.5:9b模型")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 看房提醒模态框 ---
if st.session_state.show_reminder and st.session_state.reminder_house:
    # 通过ID从当前favorites中查找最新的房源数据
    reminder_house_id = st.session_state.reminder_house['id']
    house = None
    for h in st.session_state.favorites:
        if h['id'] == reminder_house_id:
            house = h
            break
    
    # 如果找不到房源（可能被删除了），关闭弹窗
    if house is None:
        st.session_state.show_reminder = False
        st.session_state.reminder_house = None
        st.rerun()
    
    # 创建提醒弹窗容器
    with st.container():
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.95); border-radius: 16px; padding: 24px; margin: 20px 0; border: 1px solid rgba(148, 163, 184, 0.2);">
        """, unsafe_allow_html=True)
        
        # 标题和关闭按钮放在同一行
        col_title, col_close = st.columns([5, 1])
        with col_title:
            st.markdown("<h3 style='color: #f8fafc; margin: 0;'>⏰ 设置看房提醒</h3>", unsafe_allow_html=True)
        with col_close:
            if st.button("❌ 关闭", key="close_reminder", use_container_width=True):
                st.session_state.show_reminder = False
                st.session_state.reminder_house = None
                st.rerun()
        
        st.divider()
        
        # 房源标题
        st.markdown(f"<div style='color: #94a3b8; margin-bottom: 20px;'>📍 {house['title']}</div>", unsafe_allow_html=True)
        
        reminder_date = st.date_input("选择看房日期", min_value=datetime.now().date())
        reminder_time = st.time_input("选择看房时间", value=datetime.strptime("10:00", "%H:%M").time())
        reminder_note = st.text_area("备注（可选）", placeholder="例如：联系房东电话、需要带看的物品等")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 设置提醒", type="primary", use_container_width=True):
                reminders = load_reminders()
                reminders.append({
                    "id": f"reminder_{datetime.now().timestamp()}",
                    "house_id": house["id"],
                    "house_title": house["title"],
                    "datetime": f"{reminder_date} {reminder_time}",
                    "note": reminder_note,
                    "created_at": datetime.now().isoformat()
                })
                save_reminders(reminders)
                st.success("✅ 提醒设置成功！")
                st.session_state.show_reminder = False
                st.session_state.reminder_house = None
                st.rerun()
        
        with col2:
            if st.button("❌ 取消", use_container_width=True):
                st.session_state.show_reminder = False
                st.session_state.reminder_house = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 显示已设置的提醒 ---
reminders = load_reminders()
if reminders:
    st.divider()
    st.subheader("⏰ 我的看房提醒")
    
    for reminder in reminders:
        reminder_datetime = datetime.fromisoformat(reminder["datetime"]) if isinstance(reminder["datetime"], str) else reminder["datetime"]
        is_overdue = reminder_datetime < datetime.now()
        
        # 检查是否处于编辑模式
        edit_key = f"edit_reminder_{reminder['id']}"
        if edit_key not in st.session_state:
            st.session_state[edit_key] = False
        
        if st.session_state[edit_key]:
            # 编辑模式
            with st.container():
                st.markdown(f"**编辑提醒: {reminder['house_title']}**")
                
                # 解析现有日期时间
                try:
                    current_datetime = datetime.fromisoformat(reminder["datetime"])
                    current_date = current_datetime.date()
                    current_time = current_datetime.time()
                except:
                    current_date = datetime.now().date()
                    current_time = datetime.strptime("10:00", "%H:%M").time()
                
                edit_date = st.date_input("修改日期", value=current_date, min_value=datetime.now().date(), key=f"edit_date_{reminder['id']}")
                edit_time = st.time_input("修改时间", value=current_time, key=f"edit_time_{reminder['id']}")
                edit_note = st.text_area("修改备注", value=reminder.get("note", ""), key=f"edit_note_{reminder['id']}")
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("✅ 保存修改", key=f"save_edit_{reminder['id']}", type="primary", use_container_width=True):
                        # 更新提醒数据
                        for r in reminders:
                            if r["id"] == reminder["id"]:
                                r["datetime"] = f"{edit_date} {edit_time}"
                                r["note"] = edit_note
                                break
                        save_reminders(reminders)
                        st.session_state[edit_key] = False
                        st.success("✅ 提醒已更新！")
                        st.rerun()
                
                with col_cancel:
                    if st.button("❌ 取消编辑", key=f"cancel_edit_{reminder['id']}", use_container_width=True):
                        st.session_state[edit_key] = False
                        st.rerun()
                
                st.divider()
        else:
            # 显示模式
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                status_color = "🔴" if is_overdue else "🟢"
                st.markdown(f"{status_color} **{reminder['house_title']}**")
            with col2:
                st.markdown(f"📅 {reminder['datetime']}")
            with col3:
                if st.button("✏️ 编辑", key=f"edit_btn_{reminder['id']}"):
                    st.session_state[edit_key] = True
                    st.rerun()
            with col4:
                if st.button("🗑️ 删除", key=f"del_reminder_{reminder['id']}"):
                    reminders = [r for r in reminders if r["id"] != reminder["id"]]
                    save_reminders(reminders)
                    st.rerun()
            
            if reminder.get("note"):
                st.markdown(f"<div style='color: #64748b; font-size: 13px; margin-left: 24px;'>📝 {reminder['note']}</div>", unsafe_allow_html=True)
