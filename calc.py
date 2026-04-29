import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Tile Master Elite Pro", layout="wide")

# --- ФУНКЦИЯ ОТРИСОВКИ ---
def draw_layout(m_l, m_w, e_l, e_w, mode, t_l_mm, t_w_mm, layout, gap_mm, special_mode, b_w_mm, p_l, p_w, zoom):
    t_l, t_w = (t_l_mm + gap_mm) / 1000, (t_w_mm + gap_mm) / 1000
    b_w = b_w_mm / 1000
    
    # Регулировка размера фигуры через Zoom
    fig, ax = plt.subplots(figsize=(7 * zoom, 4 * zoom))
    
    max_l = m_l + (e_l if mode == "Добавить нишу" else 0)
    max_w = max(m_w, e_w) if mode == "Добавить нишу" else m_w
    ax.set_xlim(-0.1, max_l + 0.1)
    ax.set_ylim(-0.1, max_w + 0.1)

    # Отрисовка сетки
    for r in range(-2, int(max_w/t_w) + 2):
        for c in range(-2, int(max_l/t_l) + 2):
            x, y = c * t_l, r * t_w
            angle = 0
            if layout == "Диагональ":
                x, y = (c - r) * (t_l / 1.414), (c + r) * (t_w / 1.414)
                angle = 45
            elif layout == "Вразбежку" and r % 2 != 0: 
                x -= t_l/2

            in_main = (0 <= x < m_l) and (0 <= y < m_w)
            is_visible = in_main
            if mode == "Добавить нишу":
                is_visible = in_main or ((m_l <= x < m_l + e_l) and (0 <= y < e_w))
            elif mode == "Вычесть угол/короб":
                is_visible = in_main and not ((m_l - e_l <= x < m_l) and (m_w - e_w <= y < m_w))

            # Исключаем зону декора
            if special_mode == "Ковер":
                if (b_w <= x < m_l - b_w) and (b_w <= y < m_w - b_w): pass
            elif special_mode == "Панно":
                p_x, p_y = (m_l-p_l)/2, (m_w-p_w)/2
                if (p_x <= x < p_x + p_l) and (p_y <= y < p_y + p_w): is_visible = False

            if is_visible:
                ax.add_patch(patches.Rectangle((x, y), t_l-0.005, t_w-0.005, angle=angle, color="#f9f9f9", ec="#b0b0b0", lw=0.5))

    # Декор
    if special_mode == "Ковер":
        ax.add_patch(patches.Rectangle((0, 0), m_l, m_w, linewidth=b_w*60, edgecolor='#FFD700', facecolor='none', alpha=0.5))
    elif special_mode == "Панно":
        ax.add_patch(patches.Rectangle(((m_l-p_l)/2, (m_w-p_w)/2), p_l, p_w, color="#E67E22", ec="#A04000", lw=2))

    ax.add_patch(patches.Rectangle((0, 0), m_l, m_w, linewidth=2, edgecolor='black', facecolor='none', zorder=25))
    ax.set_aspect('equal')
    plt.axis('off')
    return fig

# --- ИНТЕРФЕЙС ---
with st.sidebar:
    st.title("⚙️ Настройки")
    
    st.header("🧱 Спец. Режим")
    special_mode = st.selectbox("Декор", ["Нет", "Ковер", "Панно"])
    b_w_mm = st.number_input("Ширина бордюра (мм)", 100) if special_mode == "Ковер" else 0
    p_l = st.number_input("Длина панно (м)", 1.2) if special_mode == "Панно" else 0
    p_w = st.number_input("Ширина панно (м)", 1.2) if special_mode == "Панно" else 0

    st.header("📐 Помещение")
    mode = st.radio("Форма", ["Прямоугольник", "Добавить нишу", "Вычесть угол/короб"])
    m_l = st.number_input("Длина (м)", 3.0)
    m_w = st.number_input("Ширина (м)", 2.0)
    e_l = st.number_input("Длина доп. эл. (м)", 1.0) if mode != "Прямоугольник" else 0
    e_w = st.number_input("Ширина доп. эл. (м)", 0.5) if mode != "Прямоугольник" else 0

    st.header("🧩 Материалы")
    t_l = st.number_input("Плитка Д (мм)", 600)
    t_w = st.number_input("Плитка Ш (мм)", 600)
    t_t = st.number_input("Толщина (мм)", 9)
    layout = st.selectbox("Укладка", ["Прямая", "Диагональ", "Вразбежку"])
    gap = st.number_input("Шов (мм)", 2.0)
    
    st.header("🔍 Просмотр")
    zoom = st.slider("Масштаб схемы", 0.5, 3.0, 1.2)

# --- РАСЧЕТЫ ---
# Площади
area = (m_l * m_w) + (e_l * e_w if mode == "Добавить нишу" else -e_l * e_w if mode == "Вычесть угол/короб" else 0)
decor_area = (p_l * p_w) if special_mode == "Панно" else ((2*m_l*b_w_mm/1000) + (2*(m_w-2*b_w_mm/1000)*b_w_mm/1000)) if special_mode == "Ковер" else 0
main_area = area - decor_area

# Расходники
primer = math.ceil(area * 0.3) # 0.3л на м2
hydro = math.ceil(area * 1.5)  # 1.5кг на м2
glue = math.ceil(area * 5 / 25) # мешки по 25кг
grout = round(((t_l + t_w) / (t_l * t_w)) * t_t * gap * 1.6 * area * 1.1, 1)
svp = math.ceil(((1/(t_l/1000)) + (1/(t_w/1000))) * 2 * area * 1.05)

# --- ЭКРАН ---
st.title("🏆 Tile Master Elite Pro")
c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("📦 Полная смета материалов")
    st.write(f"✅ **Плитка основная:** {main_area:.2f} м²")
    if decor_area > 0: st.write(f"✨ **Декор/Бордюр:** {decor_area:.2f} м²")
    
    st.divider()
    st.write(f"🧴 **Грунтовка:** {primer} л")
    st.write(f"💧 **Гидроизоляция:** {hydro} кг")
    st.write(f"🧱 **Клей:** {glue} меш.")
    st.write(f"🎨 **Затирка:** {grout} кг")
    st.write(f"🛠 **СВП (зажимы):** {svp} шт.")
    
    st.info(f"🚩 **Длина реза (прим):** {((m_l+m_w)*2 + (e_l+e_w)*2):.1f} пог. м")

with c2:
    st.pyplot(draw_layout(m_l, m_w, e_l, e_w, mode, t_l, t_w, layout, gap, special_mode, b_w_mm, p_l, p_w, zoom))
