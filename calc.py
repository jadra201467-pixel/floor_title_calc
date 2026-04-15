import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Tile Master Elite", layout="wide")

# --- ФУНКЦИЯ ОТРИСОВКИ (Учитывает и форму комнаты, и тип укладки) ---
def draw_layout(m_l, m_w, e_l, e_w, mode, t_l_mm, t_w_mm, layout, gap_mm):
    t_l, t_w = (t_l_mm + gap_mm) / 1000, (t_w_mm + gap_mm) / 1000
    fig, ax = plt.subplots(figsize=(8, 5))
    
    max_l = m_l + (e_l if mode == "Добавить нишу" else 0)
    max_w = max(m_w, e_w) if mode == "Добавить нишу" else m_w
    ax.set_xlim(-0.2, max_l + 0.2)
    ax.set_ylim(-0.2, max_w + 0.2)

    step = t_l / 1.414 if layout == "Диагональ" else t_l
    for r in range(-10, int(max_w/step) + 10):
        for c in range(-10, int(max_l/step) + 10):
            if layout == "Диагональ":
                x, y = (c - r) * (t_l / 1.414), (c + r) * (t_w / 1.414)
                angle = 45
            else:
                x, y = c * t_l, r * t_w
                if layout == "Вразбежку" and r % 2 != 0: x -= t_l/2
                angle = 0
            
            in_main = (0 <= x < m_l) and (0 <= y < m_w)
            is_visible = in_main
            if mode == "Добавить нишу":
                is_visible = in_main or ((m_l <= x < m_l + e_l) and (0 <= y < e_w))
            elif mode == "Вычесть угол/короб":
                is_visible = in_main and not ((m_l - e_l <= x < m_l) and (m_w - e_w <= y < m_w))

            if is_visible:
                ax.add_patch(patches.Rectangle((x, y), t_l-0.002, t_w-0.002, angle=angle, color="#f5f5f5", ec="#888888", lw=0.4))

    ax.add_patch(patches.Rectangle((0, 0), m_l, m_w, linewidth=2, edgecolor='black', facecolor='none', zorder=20))
    ax.set_aspect('equal')
    plt.axis('off')
    return fig

# --- ИНТЕРФЕЙС ---
with st.sidebar:
    st.header("💰 1. Цены")
    p_tile = st.number_input("Цена плитки (м²)", value=0.0)
    p_glue = st.number_input("Цена клея (мешок)", value=0.0)
    p_grout = st.number_input("Цена затирки (кг)", value=0.0)
    p_svp = st.number_input("Цена СВП (1 шт)", value=0.0)

    st.header("📐 2. Помещение")
    mode = st.radio("Форма пола", ["Прямоугольник", "Добавить нишу", "Вычесть угол/короб"])
    m_l = st.number_input("Длина (м)", value=3.0)
    m_w = st.number_input("Ширина (м)", value=2.0)
    e_l = e_w = 0.0
    if mode != "Прямоугольник":
        e_l = st.number_input("Длина ниши/короба (м)", value=1.0)
        e_w = st.number_input("Ширина ниши/короба (м)", value=0.5)
    
    st.subheader("🏢 Колонны (островные)")
    col_type = st.selectbox("Тип колонн", ["Нет", "Квадратные", "Круглые (число Пи)"])
    minus_area_col = 0.0
    extra_waste = 0.0
    if col_type == "Квадратные":
        c_n = st.number_input("Кол-во колонн", value=1)
        minus_area_col = st.number_input("S одной колонны (м2)", value=0.16) * c_n
        extra_waste = c_n * 0.02
    elif col_type == "Круглые (число Пи)":
        c_n = st.number_input("Кол-во колонн", value=1)
        c_d = st.number_input("Диаметр (м)", value=0.4)
        minus_area_col = (math.pi * (c_d/2)**2) * c_n
        extra_waste = c_n * 0.04

    st.header("🧩 3. Материал")
    t_l = st.number_input("Длина (мм)", value=600)
    t_w = st.number_input("Ширина (мм)", value=600)
    t_t = st.number_input("Толщина (мм)", value=9)
    in_box = st.number_input("м² в упаковке", value=1.44)
    layout = st.selectbox("Укладка", ["Прямая", "Диагональ", "Вразбежку"])
    gap = st.number_input("Шов (мм)", value=2.0)

# --- РАСЧЕТЫ ---
if mode == "Добавить нишу": area = (m_l * m_w) + (e_l * e_w)
elif mode == "Вычесть угол/короб": area = (m_l * m_w) - (e_l * e_w)
else: area = m_l * m_w

final_pure_area = area - minus_area_col
base_waste = {"Прямая": 0.1, "Диагональ": 0.15, "Вразбежку": 0.12}[layout]
total_waste = base_waste + extra_waste

boxes = math.ceil((final_pure_area * (1 + total_waste)) / in_box)
total_m2 = boxes * in_box
glue_bags = math.ceil(final_pure_area * 5 / 25)
grout_kg = round(((t_l + t_w) / (t_l * t_w)) * t_t * gap * 1.6 * final_pure_area * 1.1, 2)
svp_count = math.ceil(((1/(t_l/1000)) + (1/(t_w/1000))) * 2 * final_pure_area * 1.05)

# --- ЭКРАН ---
st.title("🏆 Tile Master Elite")
col_res, col_plot = st.columns([1, 1.2])

with col_res:
    st.subheader("🧾 Детальная смета")
    cost_t = total_m2 * p_tile
    cost_g = glue_bags * p_glue
    cost_gr = grout_kg * p_grout
    cost_s = svp_count * p_svp
    total_bill = cost_t + cost_g + cost_gr + cost_s

    st.write(f"📏 **Площадь:** {final_pure_area:.3f} м²")
    st.write(f"📦 **Плитка:** {boxes} кор. ({total_m2:.2f} м²) — **{cost_t:,.2f} р.**")
    st.write(f"🧪 **Клей:** {glue_bags} меш. — **{cost_g:,.2f} р.**")
    st.write(f"🎨 **Затирка:** {grout_kg} кг — **{cost_gr:,.2f} р.**")
    st.write(f"🛠 **СВП:** {svp_count} шт. — **{cost_s:,.2f} р.**")
    st.success(f"### ИТОГО К ОПЛАТЕ: {total_bill:,.2f} руб.")
    
    with st.expander("📝 Техническое задание для мастера"):
        note = f"Тип: {layout}. Шов: {gap}мм. Сложность: {col_type}."
        if col_type != "Нет": note += "\n⚠️ Внимание: Радиальный или усиленный рез на колоннах!"
        st.write(note)

with col_plot:
    st.subheader("🎨 Схема формы и раскладки")
    st.pyplot(draw_layout(m_l, m_w, e_l, e_w, mode, t_l, t_w, layout, gap))
