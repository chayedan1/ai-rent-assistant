import streamlit as st
import json
import os
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="租房预算规划 - AI租房决策系统", layout="wide")

# --- 加载CSS ---
def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

local_css("../style.css")

# --- 自定义样式 ---
st.markdown("""
<style>
/* 页面整体背景 */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

/* 页面标题 */
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

/* 模块卡片 */
.module-card {
    background: rgba(30, 41, 59, 0.8);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    border: 1px solid rgba(148, 163, 184, 0.2);
}

.module-title {
    font-size: 20px;
    font-weight: 600;
    color: #f8fafc;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* 结果展示 */
.result-box {
    background: rgba(15, 23, 42, 0.6);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
}

.result-label {
    font-size: 14px;
    color: #94a3b8;
    margin-bottom: 4px;
}

.result-value {
    font-size: 24px;
    font-weight: 700;
    color: #f8fafc;
}

.result-value-highlight {
    color: #10b981;
}

.result-value-warning {
    color: #f59e0b;
}

.result-value-danger {
    color: #ef4444;
}

/* 状态标签 */
.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
}

.status-healthy {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
}

.status-warning {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
}

.status-danger {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

/* 进度条 */
.health-bar {
    width: 100%;
    height: 8px;
    background: rgba(71, 85, 105, 0.5);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
}

.health-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.health-bar-fill.good {
    background: linear-gradient(90deg, #10b981, #34d399);
}

.health-bar-fill.warning {
    background: linear-gradient(90deg, #f59e0b, #fbbf24);
}

.health-bar-fill.danger {
    background: linear-gradient(90deg, #ef4444, #f87171);
}

/* AI建议卡片 */
.tip-card {
    background: rgba(59, 130, 246, 0.1);
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
}

.tip-card.warning {
    background: rgba(245, 158, 11, 0.1);
    border-left-color: #f59e0b;
}

/* 表格样式 */
.compare-table {
    width: 100%;
    border-collapse: collapse;
}

.compare-table th {
    background: rgba(30, 41, 59, 0.9);
    color: #f8fafc;
    padding: 12px;
    text-align: left;
    font-weight: 600;
}

.compare-table td {
    padding: 12px;
    border-bottom: 1px solid rgba(71, 85, 105, 0.3);
    color: #e2e8f0;
}

.compare-table tr:hover {
    background: rgba(59, 130, 246, 0.05);
}

/* 按钮样式 */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* 输入框样式 */
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(71, 85, 105, 0.5);
    color: #f8fafc;
    border-radius: 8px;
}

/* 滑块样式 */
.stSlider > div > div > div {
    background: #3b82f6;
}
</style>
""", unsafe_allow_html=True)

# --- 数据文件 ---
BUDGET_FILE = "data/budget_config.json"
FAVORITES_FILE = "data/favorites.json"

# --- 初始化数据文件 ---
def init_data_files():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

init_data_files()

# --- 加载预算配置 ---
def load_budget_config():
    try:
        with open(BUDGET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# --- 保存预算配置 ---
def save_budget_config(config):
    with open(BUDGET_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# --- 加载收藏房源 ---
def load_favorites():
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# --- 页面标题 ---
st.markdown('<div class="page-title">💰 租房预算规划</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">科学规划租房预算，避免财务压力</div>', unsafe_allow_html=True)

# --- 初始化Session State ---
if "budget_config" not in st.session_state:
    st.session_state.budget_config = load_budget_config()
if "compare_houses" not in st.session_state:
    st.session_state.compare_houses = []

# --- Tab切换 ---
tab1, tab2 = st.tabs(["📊 我的租房预算", "🏠 房源预算对比"])

# =============================================
# Tab 1: 我的租房预算
# =============================================
with tab1:
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # --- 模块1：基础预算计算 ---
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">📊 基础预算计算</div>', unsafe_allow_html=True)
        
        # 输入项
        monthly_income = st.number_input(
            "💵 月收入（元）",
            min_value=0,
            value=st.session_state.budget_config.get("monthly_income", 10000),
            step=500,
            format="%d",
            help="请输入您的税后月收入"
        )
        
        rent_ratio = st.slider(
            "📈 可承受房租占比",
            min_value=10,
            max_value=50,
            value=st.session_state.budget_config.get("rent_ratio", 25),
            step=5,
            format="%d%%",
            help="建议不超过30%，否则可能影响生活质量"
        )
        
        fixed_expenses = st.number_input(
            "💳 固定月支出（元）",
            min_value=0,
            value=st.session_state.budget_config.get("fixed_expenses", 0),
            step=100,
            format="%d",
            help="如：信用卡还款、贷款、保险等固定支出"
        )
        
        # 基础计算（不含物业水电）
        max_rent = monthly_income * rent_ratio / 100
        min_rent = monthly_income * 0.15
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- 模块2：隐性成本核算 ---
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">🧮 隐性成本核算</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            agency_fee_option = st.selectbox(
                "🏢 中介费",
                options=["无", "半个月租金", "1个月租金"],
                index=st.session_state.budget_config.get("agency_fee_option", 0)
            )
            
            deposit_months = st.selectbox(
                "🔒 押金月数",
                options=[1, 2, 3],
                index=st.session_state.budget_config.get("deposit_months", 0)
            )
        
        with col2:
            property_fee = st.number_input(
                "🏠 物业费（元/月）",
                min_value=0,
                value=st.session_state.budget_config.get("property_fee", 0),
                step=50
            )
            
            utilities = st.number_input(
                "💡 水电网费（元/月）",
                min_value=0,
                value=st.session_state.budget_config.get("utilities", 200),
                step=50
            )
        
        moving_fee = st.number_input(
            "🚚 搬家费（元）",
            min_value=0,
            value=st.session_state.budget_config.get("moving_fee", 500),
            step=100
        )
        
        # 计算隐性成本
        agency_fee_map = {"无": 0, "半个月租金": 0.5, "1个月租金": 1}
        agency_fee = max_rent * agency_fee_map[agency_fee_option]
        deposit = max_rent * deposit_months
        first_month_total = deposit + agency_fee + moving_fee + max_rent
        monthly_fixed = max_rent + property_fee + utilities
        annual_cost = monthly_fixed * 12 + deposit + agency_fee + moving_fee
        
        # 计算月度剩余生活费（修正公式：扣除所有月度支出）
        remaining = monthly_income - max_rent - fixed_expenses - property_fee - utilities
        
        # 预算健康度评分（基于实际剩余金额）
        if remaining > 0:
            # 剩余金额占收入的比例作为健康度基础
            remaining_ratio = remaining / monthly_income if monthly_income > 0 else 0
            health_score = round(min(remaining_ratio * 200, 100), 1)  # 剩余20%收入=100分
        else:
            health_score = 0
        
        # 状态判断（基于剩余生活费）
        if remaining > 0:
            status_class = "status-healthy"
            status_text = "✅ 预算健康"
            bar_class = "good"
        else:
            status_class = "status-danger"
            status_text = "❌ 预算严重超支"
            bar_class = "danger"
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 保存按钮
        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("💾 保存预算配置", use_container_width=True):
                config = {
                    "monthly_income": monthly_income,
                    "rent_ratio": rent_ratio,
                    "fixed_expenses": fixed_expenses,
                    "agency_fee_option": ["无", "半个月租金", "1个月租金"].index(agency_fee_option),
                    "deposit_months": deposit_months - 1,
                    "property_fee": property_fee,
                    "utilities": utilities,
                    "moving_fee": moving_fee,
                    "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_budget_config(config)
                st.session_state.budget_config = config
                st.success("✅ 预算配置已保存！")
        
        with col_reset:
            if st.button("🔄 重置", use_container_width=True):
                st.session_state.budget_config = {}
                save_budget_config({})
                st.rerun()
    
    with col_right:
        # --- 结果显示区 ---
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">📈 预算分析结果</div>', unsafe_allow_html=True)
        
        # 推荐租金区间
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<div class="result-label">💰 推荐月租金区间</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-value result-value-highlight">¥{min_rent:,.0f} - ¥{max_rent:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 月度剩余生活费
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<div class="result-label">💵 月度剩余生活费</div>', unsafe_allow_html=True)
        
        # 根据剩余金额显示不同样式
        if remaining > 0:
            remaining_class = "result-value-highlight" if remaining > 3000 else "result-value-warning" if remaining > 1500 else "result-value-danger"
            st.markdown(f'<div class="result-value {remaining_class}">¥{remaining:,.0f}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="result-value result-value-danger">¥{remaining:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 强预警：当剩余生活费 ≤ 0 时显示
        if remaining <= 0:
            st.error("🚨 **预算严重超支警告**\n\n您的月度支出已超过收入，无法承担该租金方案，请调整预算！")
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 8px; padding: 16px; margin: 12px 0;">
                <h4 style="color: #ef4444; margin: 0 0 8px 0;">💡 建议调整方案：</h4>
                <ul style="color: #e2e8f0; margin: 0; padding-left: 20px;">
                    <li>降低房租占比（建议≤25%）</li>
                    <li>减少固定月支出</li>
                    <li>寻找更经济的房源</li>
                    <li>考虑合租分摊成本</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # 预算健康度
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<div class="result-label">📊 预算健康度评分</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-value">{health_score}分</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="health-bar"><div class="health-bar-fill {bar_class}" style="width: {health_score}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top: 8px;"><span class="status-badge {status_class}">{status_text}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- 成本分析结果 ---
        with st.container():
            st.markdown('<div class="module-card">', unsafe_allow_html=True)
            st.markdown('<div class="module-title">💸 成本明细</div>', unsafe_allow_html=True)
            
            # 显示计算结果
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.metric("首月一次性支出", f"¥{first_month_total:,.0f}")
                st.metric("月度固定支出", f"¥{monthly_fixed:,.0f}")
            
            with col_c2:
                st.metric("年度租房总成本", f"¥{annual_cost:,.0f}")
                
                # 成本构成
                st.markdown("**成本构成**")
                cost_breakdown = {
                    "租金": max_rent * 12,
                    "物业费": property_fee * 12,
                    "水电网": utilities * 12,
                    "押金": deposit,
                    "中介费": agency_fee,
                    "搬家费": moving_fee
                }
                
                for label, value in cost_breakdown.items():
                    percentage = (value / annual_cost * 100) if annual_cost > 0 else 0
                    st.markdown(f"{label}: ¥{value:,.0f} ({percentage:.1f}%)")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # --- 模块3：AI省钱建议 ---
    st.markdown('<div class="module-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">🤖 AI省钱建议</div>', unsafe_allow_html=True)
    
    # 根据预算情况生成建议
    tips = []
    warnings = []
    
    if rent_ratio > 35:
        tips.append("考虑选择稍远但交通便利的区域，租金可能降低20-30%")
        tips.append("寻找合租机会，可分摊租金和水电费用")
        warnings.append("当前房租占比偏高，建议预留至少3个月租金作为应急资金")
    elif rent_ratio > 25:
        tips.append("尝试与房东协商，长租可获得5-10%的租金优惠")
        tips.append("选择简装房源自行布置，比精装房节省15-20%")
    else:
        tips.append("预算充足，可考虑品质更好的房源提升居住体验")
        tips.append("适当提高预算选择近地铁房源，节省通勤时间和成本")
    
    if agency_fee_option == "1个月租金":
        tips.append("尝试通过房东直租或小区物业租房，可省掉1个月中介费")
    
    if deposit_months == 3:
        warnings.append("押金为3个月，退房时务必保留好押金条和房屋交接记录")
    
    tips.append("签约前仔细检查家电设施，拍照留证避免退租纠纷")
    
    # 显示省钱方案
    st.markdown('<div style="margin-bottom: 16px;"><strong style="color: #10b981;">💡 省钱方案</strong></div>', unsafe_allow_html=True)
    for i, tip in enumerate(tips[:3], 1):
        st.markdown(f'<div class="tip-card">{i}. {tip}</div>', unsafe_allow_html=True)
    
    # 显示避坑提示
    st.markdown('<div style="margin: 16px 0;"><strong style="color: #f59e0b;">⚠️ 避坑提示</strong></div>', unsafe_allow_html=True)
    for i, warning in enumerate(warnings[:2], 1):
        st.markdown(f'<div class="tip-card warning">{i}. {warning}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================
# Tab 2: 房源预算对比
# =============================================
with tab2:
    # 加载收藏的房源
    favorites = load_favorites()
    
    if not favorites:
        st.info("📝 您还没有收藏任何房源，请先前往首页收藏房源")
    else:
        # 获取已保存的预算配置
        budget_config = st.session_state.budget_config
        monthly_income = budget_config.get("monthly_income", 10000)
        
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">🏠 房源预算对比分析</div>', unsafe_allow_html=True)
        
        # 显示当前预算配置
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="result-box"><div class="result-label">月收入</div><div class="result-value">¥{monthly_income:,.0f}</div></div>', unsafe_allow_html=True)
        with col2:
            max_rent = monthly_income * budget_config.get("rent_ratio", 25) / 100
            st.markdown(f'<div class="result-box"><div class="result-label">预算上限</div><div class="result-value result-value-highlight">¥{max_rent:,.0f}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="result-box"><div class="result-label">健康占比</div><div class="result-value">≤30%</div></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 选择要对比的房源
        st.markdown('<div class="module-card">', unsafe_allow_html=True)
        st.markdown('<div class="module-title">📋 选择对比房源（最多5套）</div>', unsafe_allow_html=True)
        
        # 多选房源
        house_options = {f"{h['title'][:30]}... (¥{h['price']}/月)": h for h in favorites}
        selected = st.multiselect(
            "选择要对比的房源",
            options=list(house_options.keys()),
            default=list(house_options.keys())[:3] if len(house_options) <= 3 else list(house_options.keys())[:3],
            max_selections=5
        )
        
        selected_houses = [house_options[s] for s in selected]
        
        if selected_houses:
            # 对比表格
            st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
            
            compare_data = []
            for house in selected_houses:
                rent = house.get('price', 0)
                ratio = (rent / monthly_income * 100) if monthly_income > 0 else 0
                remaining = monthly_income - rent
                
                # 判断状态
                if ratio <= 30:
                    status = "✅ 健康"
                    status_color = "#10b981"
                elif ratio <= 40:
                    status = "⚠️ 偏紧"
                    status_color = "#f59e0b"
                else:
                    status = "❌ 压力大"
                    status_color = "#ef4444"
                
                # 风险提示
                if ratio > 40:
                    risk = "租金占比过高，建议降低预算或增加收入"
                elif ratio > 30:
                    risk = "租金占比较高，需控制其他支出"
                elif remaining < 3000:
                    risk = "剩余生活费较少，需谨慎规划"
                else:
                    risk = "预算合理，可安心租住"
                
                compare_data.append({
                    "房源": house['title'][:25] + "..." if len(house['title']) > 25 else house['title'],
                    "租金": f"¥{rent}/月",
                    "占收入比": f"{ratio:.1f}%",
                    "剩余生活费": f"¥{remaining:,.0f}",
                    "状态": status,
                    "风险提示": risk
                })
            
            # 使用Streamlit的dataframe显示
            import pandas as pd
            df = pd.DataFrame(compare_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 推荐房源
            st.markdown('<div style="margin-top: 24px;">', unsafe_allow_html=True)
            st.markdown('<div class="module-title">🏆 预算推荐</div>', unsafe_allow_html=True)
            
            # 找出最符合预算的房源
            healthy_houses = [h for h in selected_houses if (h.get('price', 0) / monthly_income * 100) <= 30]
            
            if healthy_houses:
                best_house = min(healthy_houses, key=lambda x: abs(x.get('price', 0) - max_rent))
                st.markdown(f'<div class="tip-card">', unsafe_allow_html=True)
                st.markdown(f'<strong style="color: #10b981;">✅ 最推荐：{best_house["title"]}</strong>', unsafe_allow_html=True)
                st.markdown(f'<div style="color: #94a3b8; margin-top: 8px;">租金 ¥{best_house["price"]}/月，符合您的预算规划，财务压力较小</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="tip-card warning">', unsafe_allow_html=True)
                st.markdown(f'<strong style="color: #f59e0b;">⚠️ 预算提醒</strong>', unsafe_allow_html=True)
                st.markdown(f'<div style="color: #94a3b8; margin-top: 8px;">所选房源租金均超出健康预算范围（≤30%），建议调整预算或寻找更经济的房源</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 底部提示 ---
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 13px; margin-top: 40px; padding: 20px;">
    <p>💡 提示：合理的租房预算应控制在月收入的25-30%以内，预留足够的应急资金</p>
    <p>📊 数据仅供参考，实际租房请结合个人情况综合考虑</p>
</div>
""", unsafe_allow_html=True)
