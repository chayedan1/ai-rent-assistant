# ============================================================
# 通勤时间计算
# 基于高德地图 API · 房源通勤时间展示
# ============================================================
import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="通勤时间计算", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
.page-title { font-size:28px; font-weight:700; color:#f8fafc; text-align:center; margin-bottom:4px; }
.page-subtitle { font-size:13px; color:#94a3b8; text-align:center; margin-bottom:20px; }
.source-panel { background:rgba(30,41,59,0.8); border-radius:12px; padding:16px; margin-top:15px; border-left:3px solid #f59e0b; }
.source-title { font-size:14px; font-weight:600; color:#fbbf24; margin-bottom:10px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 配置
# ============================================================
AMAP_KEY = "a903ec8f039e82906cbb734e0e441994"
AMAP_GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"
AMAP_DISTANCE_URL = "https://restapi.amap.com/v3/distance"

# ============================================================
# 地理编码：地址转坐标
# ============================================================
def geocode_address(address):
    try:
        response = requests.get(
            AMAP_GEOCODE_URL,
            params={
                "address": address,
                "key": AMAP_KEY
            },
            timeout=10
        )
        result = response.json()
        if result.get("status") == "1" and result.get("geocodes"):
            location = result["geocodes"][0].get("location", "")
            return location
        return None
    except:
        return None

# ============================================================
# 距离计算
# ============================================================
def calculate_distance(origin, destination, mode):
    try:
        response = requests.get(
            AMAP_DISTANCE_URL,
            params={
                "origins": origin,
                "destination": destination,
                "type": mode,
                "key": AMAP_KEY
            },
            timeout=10
        )
        result = response.json()
        if result.get("status") == "1" and result.get("results"):
            distance_info = result["results"][0]
            return {
                "distance": distance_info.get("distance", "0"),
                "duration": distance_info.get("duration", "0")
            }
        return None
    except:
        return None

# ============================================================
# 主流程
# ============================================================
def main():
    st.markdown('<div class="page-title">🚗 房源通勤地图</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">基于高德地图 API · 房源位置可视化</div>', unsafe_allow_html=True)
    
    # 房源收藏数据（从 data/favorites.json 获取）
    st.markdown('<div class="source-panel">', unsafe_allow_html=True)
    st.markdown('<div class="source-title">房源收藏</div>', unsafe_allow_html=True)
    
    FAVORITES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'favorites.json')
    
    def load_favorites():
        try:
            if os.path.exists(FAVORITES_FILE):
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return []
    
    favorites = load_favorites()
    
    if not favorites:
        st.info("暂无收藏房源，请先在「🏠 房源收藏与管理」页面收藏房源")
    else:
        st.markdown(f'<div style="font-size:13px;color:#94a3b8;margin-bottom:10px;">共 {len(favorites)} 套房源</div>', unsafe_allow_html=True)
        
        # 显示房源列表（可折叠）
        for idx, fav in enumerate(favorites):
            name = fav.get('title', '未知房源')
            district = fav.get('district', '')
            community = fav.get('community', '')
            
            # 修复面积显示
            area = fav.get('area', '')
            if area in ['00㎡', '02㎡', '0㎡', '未知', '']:
                area = '--'
            
            # 修复价格显示
            price_val = fav.get('price', 0)
            if price_val == 0:
                price = '价格待定'
            else:
                price = f"¥{price_val}/月"
            
            bedrooms = fav.get('layout', '')
            
            # 地址
            if district and community and district != '未知' and community != '未知':
                address = f"{district} · {community}"
            elif district and district != '未知':
                address = district
            elif community and community != '未知':
                address = community
            else:
                address = "地址不详"
            
            # 折叠显示
            with st.expander(f"{name} | {price}", expanded=False):
                st.caption(f"📍 {address}")
                st.caption(f"🏠 {area} | {bedrooms}")
                st.caption(f"📅 收藏于 {fav.get('collected_at', '')}")
                if fav.get('tags'):
                    st.caption(f"🏷️ {', '.join(fav['tags'])}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 地图展示
    st.markdown('<div class="source-panel">', unsafe_allow_html=True)
    st.markdown('<div class="source-title">�️ 地图可视化</div>', unsafe_allow_html=True)
    
    # 收集所有房源坐标
    locations = []
    for fav in favorites:
        district = fav.get('district', '')
        community = fav.get('community', '')
        
        # 修复地址
        if district and community and district != '未知' and community != '未知':
            address = f"{district} {community}"
        elif district and district != '未知':
            address = district
        elif community and community != '未知':
            address = community
        else:
            address = ""
        
        if address:
            coord = geocode_address(address)
            if coord:
                name = fav.get('title', '未知房源')
                price_val = fav.get('price', 0)
                if price_val == 0:
                    price = '价格待定'
                else:
                    price = f"¥{price_val}/月"
                area = fav.get('area', '')
                if area in ['00㎡', '02㎡', '0㎡', '未知', '']:
                    area = '--'
                else:
                    area = area
                bedrooms = fav.get('layout', '')
                
                locations.append({
                    "label": name,
                    "address": address,
                    "coord": coord,
                    "price": price,
                    "area": area,
                    "bedrooms": bedrooms
                })
    
    if locations:
        # 可交互地图
        st.markdown('<div style="margin-top:15px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:14px;font-weight:600;color:#fbbf24;margin-bottom:10px;">🌐 可交互地图（点击可打开高德地图网页版）</div>', unsafe_allow_html=True)
        
        # 获取中心点
        center_coord = locations[0]['coord']
        center_lon, center_lat = center_coord.split(',')[0], center_coord.split(',')[1]
        
        # 构建 markers 参数
        markers_list = []
        for loc in locations:
            coord_parts = loc["coord"].split(',')
            if len(coord_parts) == 2:
                markers_list.append(f"{coord_parts[0]},{coord_parts[1]}")
        
        iframe_markers = ",".join(markers_list)
        amap_marker_url = f"https://uri.amap.com/marker?location={center_lon},{center_lat}&zoom=12&markers={iframe_markers}&key={AMAP_KEY}"
        
        iframe_html = f"""
        <div style="position:relative;padding-bottom:60%;height:0;overflow:hidden;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.3);">
            <iframe src="{amap_marker_url}" 
                    style="position:absolute;top:0;left:0;width:100%;height:100%;border:none;"
                    allowfullscreen>
            </iframe>
        </div>
        """
        
        st.markdown(iframe_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ 所有房源地址无法解析，请检查房源数据")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
