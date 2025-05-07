import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime
import os
from timezonefinder import TimezoneFinder
import pytz
import streamlit.components.v1 as components

# Hàm chuyển đổi thời gian sang múi giờ người dùng
def convert_to_user_timezone(lat, lon):
    tf = TimezoneFinder()
    result = tf.timezone_at(lng=lon, lat=lat)
    if result:
        user_timezone = pytz.timezone(result)
        utc_time = datetime.datetime.now(pytz.utc)
        local_time = utc_time.astimezone(user_timezone)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")
    return None

# Set page config
st.set_page_config(page_title="Bản đồ cảm xúc đô thị", layout="wide")

# Title
st.title("🗺️ Bản đồ cảm xúc đô thị")
st.markdown("Gắn cảm xúc của bạn tại một địa điểm trên bản đồ, cùng chia sẻ trải nghiệm với cộng đồng.")

# File dữ liệu
DATA_PATH = "emotion_data.csv"

# Nếu file chưa có thì tạo mới
if not os.path.exists(DATA_PATH):
    df = pd.DataFrame(columns=["lat", "lon", "emotion", "note", "user", "timestamp"])
    df.to_csv(DATA_PATH, index=False)
else:
    df = pd.read_csv(DATA_PATH)

# --- Sidebar nhập liệu ---
st.sidebar.header("📍 Gửi cảm xúc của bạn")
emotion = st.sidebar.selectbox("Cảm xúc", ["😊 Vui", "😢 Buồn", "😨 Sợ", "😠 Tức giận", "😌 Thoải mái"])
note = st.sidebar.text_input("Ghi chú (tuỳ chọn)")
user_name = st.sidebar.text_input("Tên người dùng (hoặc tên bạn bè)", "Bạn")
st.sidebar.markdown("*Bấm vào bản đồ để chọn vị trí hoặc sử dụng định vị hiện tại.*")

# --- Định vị vị trí người dùng ---
location = components.html("""
    <script type="text/javascript">
        navigator.geolocation.getCurrentPosition(function(position) {
            window.parent.postMessage({lat: position.coords.latitude, lon: position.coords.longitude}, "*");
        });
    </script>
""", height=0, width=0)

# --- Bản đồ ---
m = folium.Map(location=[10.762622, 106.660172], zoom_start=12)

# Hiển thị các cảm xúc đã có
for _, row in df.iterrows():
    popup_text = f"{row['emotion']} lúc {row['timestamp']}<br>Người gửi: {row['user']}<br>{row['note']}"
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup_text,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Hiển thị bản đồ tương tác
map_data = st_folium(m, width=700, height=500)
coords = map_data.get("last_clicked")

# Nếu định vị được vị trí, hiển thị vị trí hiện tại của người dùng trên bản đồ
if location:
    lat, lon = location["lat"], location["lon"]
    folium.Marker([lat, lon], popup="Vị trí hiện tại", icon=folium.Icon(color="green")).add_to(m)
    coords = {"lat": lat, "lng": lon}  # Cập nhật vị trí của người dùng

# Kiểm tra nếu đã chọn vị trí và cảm xúc
if coords and emotion:
    # Hiển thị nút Gửi cảm xúc
    if st.sidebar.button("📩 Gửi cảm xúc"):
        # Chuyển đổi thời gian theo múi giờ người dùng
        local_time = convert_to_user_timezone(coords["lat"], coords["lng"])
        
        new_row = {
            "lat": coords["lat"],
            "lon": coords["lng"],
            "emotion": emotion,
            "note": note,
            "user": user_name,
            "timestamp": local_time  # Sử dụng thời gian theo múi giờ người dùng
        }
        
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        st.success("✅ Đã ghi nhận cảm xúc!")

# --- Hiển thị dữ liệu ---
with st.expander("📊 Dữ liệu cảm xúc cộng đồng"):
    st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True))
