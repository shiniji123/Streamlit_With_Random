import streamlit as st
import random
import threading
import time

# ตั้งค่า layout ให้กว้าง (wide) เพื่อให้แสดงตารางตัวเลขในหน้าเดียวได้
#st.set_page_config(layout="wide")

# Custom CSS เพื่อปรับแต่งสไตล์ (รวมถึงการปรับขนาดปุ่ม และลด padding ของ container)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sarabun&display=swap" rel="stylesheet">
<style>
/* กำหนดฟอนต์ภาษาไทย */
h1, h2, h3, p, div, span {
    font-family: 'Sarabun', sans-serif !important;
}

/* ปรับขนาดปุ่มตัวเลขให้ใหญ่ขึ้นและลด margin/padding */
div.stButton > button {
    height: 35px; 
    width: 80px;
    font-size: 20px;
    margin: 0px;
    padding: 0px;
}

</style>
""", unsafe_allow_html=True)

# ตรวจสอบและกำหนดค่าเริ่มต้นให้กับ session_state keys ที่จำเป็น
if 'selected_number' not in st.session_state:
    st.session_state['selected_number'] = None
if 'target_number' not in st.session_state:
    st.session_state['target_number'] = None
if 'attempts' not in st.session_state:
    st.session_state['attempts'] = 0
if 'game_over' not in st.session_state:
    st.session_state['game_over'] = False
if 'used_numbers' not in st.session_state:
    st.session_state['used_numbers'] = set()
if 'feedback_message' not in st.session_state:
    st.session_state['feedback_message'] = ""
if 'turn' not in st.session_state:
    st.session_state['turn'] = 0
if 'waiting_for_input' not in st.session_state:
    st.session_state['waiting_for_input'] = True
if 'available_numbers' not in st.session_state:
    st.session_state['available_numbers'] = list(range(0, 100))
if 'player_name' not in st.session_state:
    st.session_state['player_name'] = []
if 'bg_music_inserted' not in st.session_state:
    st.session_state['bg_music_inserted'] = False

# (ถ้าต้องการ) ฟังก์ชันสำหรับเพลงพื้นหลัง (Background Music) ที่จะฝังเพียงครั้งเดียว
def insert_background_music():
    if not st.session_state['bg_music_inserted']:
        st.markdown(f"""
        <script>
        if (!document.getElementById('bg-music')) {{
            var audio = document.createElement('audio');
            audio.id = 'bg-music';
            audio.src = 'https://raw.githubusercontent.com/shiniji123/Streamlit_With_Random/main/sounds/background.mp3';
            audio.autoplay = true;
            audio.loop = true;
            audio.volume = 0.5;
            document.body.appendChild(audio);
        }}
        </script>
        """, unsafe_allow_html=True)
        st.session_state['bg_music_inserted'] = True

# เรียกใช้งานเพลงพื้นหลัง (Background Music) เมื่อเข้าสู่หน้าเกม
insert_background_music()

# ฟังก์ชันเริ่มต้นเกม
def start_game():
    st.session_state['target_number'] = random.randint(1, 99)  # ตัวเลขที่ต้องทาย
    st.session_state['attempts'] = 0
    st.session_state['game_over'] = False
    st.session_state['used_numbers'] = set()
    st.session_state['feedback_message'] = ""
    st.session_state['selected_number'] = None
    st.session_state['turn'] = 0
    st.session_state['waiting_for_input'] = True
    st.session_state['available_numbers'] = list(range(0, 100))

# ฟังก์ชันหน้ากรอกชื่อผู้เล่น
def player_name_input():
    st.title("เลขแห่งทวยเทพ")
    st.write("กรุณากรอกชื่อผู้เล่นทั้ง 2 คน:")
    player_name1 = st.text_input("ชื่อผู้เล่นคนที่ 1:", "")
    player_name2 = st.text_input("ชื่อผู้เล่นคนที่ 2:", "")
    if player_name1 and player_name2:
        st.session_state['player_name'] = [player_name1, player_name2]
        if st.button("Start Game"):
            start_game()
            #st.session_state['waiting_for_input'] = False
            st.rerun()


# ถ้ายังไม่มี target_number ให้แสดงหน้ากรอกชื่อ
if st.session_state['target_number'] is None:
    player_name_input()
    st.stop()


# ฟังก์ชันแสดงปุ่มตัวเลขในตาราง 10x10
def render_number_buttons():
    available_numbers = st.session_state['available_numbers']
    # แสดงตาราง 10x10: จำนวน 100 ปุ่ม (00 ถึง 99)
    for i in range(0, 100, 10):
        cols = st.columns(10)
        for j in range(10):
            number = i + j
            if number > 99:
                continue
            formatted_number = f"{number:02}"
            disabled = number not in available_numbers
            if cols[j].button(formatted_number, key=formatted_number, disabled=disabled):
                st.session_state['selected_number'] = number
                handle_guess(number)


# ฟังก์ชันจัดการการทาย
def handle_guess(selected_number):
    st.session_state['attempts'] += 1
    target_number = st.session_state['target_number']

    if selected_number < target_number:
        st.session_state['feedback_message'] = f"คุณเลือกเลข {selected_number:02} - น้อยไป!"
        st.session_state['available_numbers'] = [n for n in st.session_state['available_numbers'] if
                                                 n > selected_number]
        st.session_state['turn'] = 1 - st.session_state['turn']
        st.rerun()
    elif selected_number > target_number:
        st.session_state['feedback_message'] = f"คุณเลือกเลข {selected_number:02} - มากไป!"
        st.session_state['available_numbers'] = [n for n in st.session_state['available_numbers'] if
                                                 n < selected_number]
        st.session_state['turn'] = 1 - st.session_state['turn']
        st.rerun()
    else:
        current_player = st.session_state['player_name'][st.session_state['turn']]
        st.session_state['feedback_message'] = f"{current_player} เป็นผู้ชนะ! เลขแห่งทวยเทพคือ {selected_number:02}"
        st.session_state['game_over'] = True
        st.rerun()


# แสดงข้อความผลลัพธ์
if st.session_state['selected_number'] is not None:
    feedback = st.session_state['feedback_message']
    if st.session_state['game_over']:
        st.markdown(
            f"""
            <div style="text-align:center">
                <h1 style="color:yellow; font-size:100px;">{feedback}</h1>
                <audio autoplay>
                    <source src="https://raw.githubusercontent.com/shiniji123/Streamlit_With_Random/main/sounds/winner.mp3" type="audio/mp3">
                    Your browser does not support the audio element.
                </audio>
            </div>
            """, unsafe_allow_html=True)
        st.balloons()
    else:
        current_player = st.session_state['player_name'][st.session_state['turn']]
        st.markdown(
            f"""
            <div style="text-align:center">
                <h1 style="color:red; font-size:40px;">{feedback}</h1>
                <h1 style="color:lightgreen; font-size:50px;">ตอนนี้เป็นเทิร์นของ {current_player}</h1>
            </div>
            """, unsafe_allow_html=True)

if st.session_state.get('target_number') is not None and not st.session_state.get('game_over', False):
    st.markdown("""
    <audio autoplay loop>
      <source src="https://raw.githubusercontent.com/shiniji123/Streamlit_With_Random/main/sounds/background.mp3" type="audio/mp3">
      Your browser does not support the audio element.
    </audio>
    """, unsafe_allow_html=True)

# แสดงปุ่มตัวเลขถ้าเกมยังไม่จบ
if st.session_state['waiting_for_input'] and not st.session_state['game_over']:
    render_number_buttons()


# ปุ่มย้อนกลับไปกรอกชื่อผู้เล่น
if st.button("ย้อนกลับ"):
    st.session_state.clear()
    st.rerun()

# ปุ่มเริ่มเกมใหม่
if st.button("เริ่มเกมใหม่"):
    start_game()
    st.rerun()