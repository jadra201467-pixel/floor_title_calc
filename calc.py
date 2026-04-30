import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ ---
if 'unit_system' not in st.session_state:
    st.session_state.unit_system = 'Metric'
if 'lang' not in st.session_state:
    st.session_state.lang = 'RU'

st.set_page_config(page_title="Tile Master Elite Pro", layout="wide")

# --- СЛОВАРЬ ПЕРЕВОДОВ ---
t = {
    'RU': {
        'title': "🏆 Tile Master Elite Pro: ИМПЕРСКИЙ ХОД",
        'settings': "⚙️ Настройки",
        'special': "🧱 Спец. Режим",
        'decor': "Декор",
        'room': "📐 Помещение",
        'shape': "Форма",
        'mats': "🧩 Материалы",
        'tile_l': "Плитка Д",
        'tile_w': "Плитка Ш",
        'thick': "Толщина",
        'layout': "Укладка",
        'gap': "Шов",
        'zoom': "🔍 Масштаб просмотра",
        'estimate': "📦 Смета материалов",
        'main_tile': "Плитка основная",
        'decor_area': "Декор/Бордюр",
        'primer': "Грунтовка",
        'hydro': "Гидроизоляция",
        'glue': "Клей",
        'grout': "Затирка",
        'svp': "СВП (зажимы)",
        'cut': "Длина реза",
        'none': "Нет", 'carpet': "Ковер", 'panel': "Панно",
        'rect': "Прямоугольник", 'niche': "Добавить нишу", 'corner': "Вычесть угол",
        'straight': "Прямая", 'diag': "Диагональ", 'offset': "Вразбежку",
        'unit_m': "м", 'unit_mm': "мм", 'unit_ft': "ft", 'unit_in': "in",
        'weight_kg': "кг", 'weight_lb': "lb", 'vol_l': "л", 'vol_gal': "gal"
    },
    'EN': {
        'title': "🏆 Tile Master Elite Pro: IMPERIAL MOVE",
        'settings': "⚙️ Settings",
        'special': "🧱 Special Mode",
        'decor': "Decor",
        'room': "📐 Room Geometry",
        'shape': "Shape",
        'mats': "🧩 Materials",
        'tile_l': "Tile Length",
        'tile_w': "Tile Width",
        'thick': "Thickness",
        'layout': "Layout",
        'gap': "Gap",
        'zoom': "🔍 Viewing Zoom",
        'estimate': "📦 Material Estimate",
        'main_tile': "Main Tile",
        'decor_area': "Decor/Border",
        'primer': "Primer",
        'hydro': "Waterproofing",
        'glue': "Glue",
        'grout': "Grout",
        'svp': "Clips (SVP)",
        'cut': "Cut length",
        'none': "None", 'carpet': "Carpet", 'panel': "Panel",
        'rect': "Rectangle", 'niche': "Add Niche", 'corner': "Subtract Corner",
        'straight': "Straight", 'diag': "Diagonal", 'offset': "Offset",
        'unit_m': "m", 'unit_mm': "mm", 'unit_ft': "ft", 'unit_in': "in",
        'weight_kg': "kg", 'weight_lb': "lb", 'vol_l': "L", 'vol_gal': "gal"
    }
}

L = t[st.session_state.lang]
is_imp = st.session_state.unit_system == 'Imperial'

# --- ФУНКЦИЯ ОТРИСОВКИ ---
def draw_layout(m_l, m_w, e_l, e_w, mode, t_l_val, t_w_val, layout, gap_val, special_mode, b_w_val, p_l, p_w, zoom):
    # Внутренний пересчет в единицы отрисовки (футы или метры)
    scale = 12 if is_imp else 1000
    t_l = (t_l_val + gap_val) / scale
    t_w = (t_w_val + gap_val) / scale
    b_w = b_w_val / scale
    
    fig, ax = plt.subplots(figsize=(8 * zoom, 5 * zoom))
    
    max_l = m_l + (e_l if mode == L['niche'] else 0)
    max_w = max(m_w, e_w) if mode == L['niche'] else m_w
    ax.set_xlim(-0.1, max_l + 0.1)
    ax.set_ylim(-0.1, max_w + 0.1)

    for r in range(-1, int(max_w/t_w) + 2):
        for c in range(-1, int(max_l/t_l) + 2):
            x, y = c * t_l, r * t_w
            angle = 0
            if layout == L['diag']:
                x, y = (c - r) * (t_l / 1.414), (c + r) * (t_w / 1.414)
                angle = 45
            elif layout == L['offset'] and r % 2 != 0: 
                x -= t_l/2

            in_main = (0 <= x < m_l) and (0 <= y < m_w)
            is_visible = in_main
            if mode == L['niche']:
                is_visible = in_main or ((m_l <= x < m_l + e_l) and (0 <= y < e_w))
            elif mode == L['corner']:
                is_visible = in_main and not ((m_l - e_l <= x < m_l) and (m_w - e_w <= y < m_w))

            if special_mode == L['carpet']:
                if (b_w <= x < m_l - b_w) and (b_w <= y < m_w - b_w): is_visible = False
            elif special_mode == L['panel']:
                p_x, p_y = (m_l-p_l)/2, (m_w-p_w)/2
                if (p_x <= x < p_x + p_l) and (p_y <= y < p_y + p_w): is_visible = False

            if is_visible:
                ax.add_patch(patches.Rectangle((x, y), t_l*0.98, t_w*0.98, angle=angle, color="#f0f0f0", ec="#aaaaaa", lw=0.3))

    # Рамка помещения
    ax.add_patch(patches.Rectangle((0, 0), m_l, m_w, linewidth=2, edgecolor='black', facecolor='none', zorder=10))
    ax.set_aspect('equal')
    plt.axis('off')
    return fig

# --- ВЕРХНЯЯ ПАНЕЛЬ УПРАВЛЕНИЯ ---
c_top1, c_top2, c_top3 = st.columns([3, 1, 1])
with c_top1:
    st.title(L['title'])
with c_top2:
    if st.button("🌐 EN / RU"):
        st.session_state.lang = 'EN' if st.session_state.lang == 'RU' else 'RU'
        st.rerun()
with c_top3:
    if st.button(f"📏 {st.session_state.unit_system}"):
        st.session_state.unit_system = 'Imperial' if st.session_state.unit_system == 'Metric' else 'Metric'
        st.rerun()

# --- БОКОВАЯ ПАНЕЛЬ (БЕЗ ЗУМА) ---
with st.sidebar:
    st.header(L['settings'])
    
    st.subheader(L['special'])
    s_mode = st.selectbox(L['decor'], [L['none'], L['carpet'], L['panel']])
    b_w_val = st.number_input(f"Bord. ({L['unit_mm'] if not is_imp else L['unit_in']})", 100 if not is_imp else 4) if s_mode == L['carpet'] else 0
    p_l = st.number_input(f"Panel L ({L['unit_m'] if not is_imp else L['unit_ft']})", 1.2) if s_mode == L['panel'] else 0
    p_w = st.number_input(f"Panel W ({L['unit_m'] if not is_imp else L['unit_ft']})", 1.2) if s_mode == L['panel'] else 0

    st.subheader(L['room'])
    room_mode = st.radio(L['shape'], [L['rect'], L['niche'], L['corner']])
    m_l = st.number_input(f"{L['wall_l']} ({L['unit_m'] if not is_imp else L['unit_ft']})", 3.0 if not is_imp else 10.0)
    m_w = st.number_input(f"{L['wall_w']} ({L['unit_m'] if not is_imp else L['unit_ft']})", 2.0 if not is_imp else 8.0)
    e_l = st.number_input(f"Extra L", 1.0) if room_mode != L['rect'] else 0
    e_w = st.number_input(f"Extra W", 0.5) if room_mode != L['rect'] else 0

    st.subheader(L['mats'])
    t_l = st.number_input(f"{L['tile_l']}", 600 if not is_imp else 12)
    t_w = st.number_input(f"{L['tile_w']}", 600 if not is_imp else 12)
    t_thick = st.number_input(f"{L['thick']}", 9)
    lay_mode = st.selectbox(L['layout'], [L['straight'], L['diag'], L['offset']])
    gap = st.number_input(f"{L['gap']}", 2.0 if not is_imp else 0.125)

# --- РАСЧЕТЫ ---
area = (m_l * m_w) + (e_l * e_w if room_mode == L['niche'] else -e_l * e_w if room_mode == L['corner'] else 0)
u_area = f"{L['unit_m']}²" if not is_imp else f"{L['unit_ft']}²"

# Расходники (коэффициенты меняются для имперской системы)
if not is_imp:
    primer = math.ceil(area * 0.3)
    hydro = math.ceil(area * 1.5)
    glue = math.ceil(area * 5 / 25)
    grout = round(((t_l + t_w) / (t_l * t_w)) * t_thick * gap * 1.6 * area * 1.1, 1)
else:
    primer = round(area * 0.007, 1) # gal
    hydro = math.ceil(area * 0.3)   # lb
    glue = math.ceil(area * 1 / 50) # 50lb bags
    grout = round(area * 0.1, 1)    # lb approx

# --- ГЛАВНЫЙ ЭКРАН ---
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader(L['estimate'])
    st.write(f"✅ **{L['main_tile']}:** {area:.2f} {u_area}")
    st.divider()
    st.write(f"🧴 **{L['primer']}:** {primer} {L['vol_l'] if not is_imp else L['vol_gal']}")
    st.write(f"💧 **{L['hydro']}:** {hydro} {L['weight_kg'] if not is_imp else L['weight_lb']}")
    st.write(f"🧱 **{L['glue']}:** {glue} {'pcs'}")
    st.write(f"🎨 **{L['grout']}:** {grout} {L['weight_kg'] if not is_imp else L['weight_lb']}")

with c2:
    # Зум теперь здесь
    zoom = st.select_slider(L['zoom'], options=[0.5, 1.0, 1.5, 2.0, 3.0], value=1.0)
    st.pyplot(draw_layout(m_l, m_w, e_l, e_w, room_mode, t_l, t_w, lay_mode, gap, s_mode, b_w_val, p_l, p_w, zoom))
