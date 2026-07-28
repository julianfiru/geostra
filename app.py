import streamlit as st
import os, gc, shutil, time, json, math, sys
import base64

LOGO_PATH = os.path.join(os.path.dirname(__file__), 'image', 'logo.png') if '__file__' in globals() else os.path.join(os.getcwd(), 'image', 'logo.png')

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ''

import pytz
from datetime import datetime



# ==============================================================================
# AUTO-LAUNCHER IF RUN WITH 'python app_local.py' DIRECTLY -
# ==============================================================================
if not st.runtime.exists():
    from streamlit.web import cli as stcli
    print("\n" + "=" * 60)
    print("  APLIKASI BATCH DETEKSI SIAP DIBUKA!")
    print("  LINK BROWSER LOKAL : http://localhost:8501")
    print("=" * 60 + "\n")
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image

import rasterio
from rasterio.windows import Window
import rasterio.transform
import geopandas as gpd
from shapely.geometry import box as sbox
from shapely.ops import unary_union
import folium
from folium.plugins import MiniMap, Fullscreen, MeasureControl, HeatMap

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title='GEOSTRA — Geospasial Sistem Tata Ruang dan Area', page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else '🌍', layout='wide')

st.markdown("""<style>
/* ═══════════════════════════════════════════════════════════════
   GEOSTRA v3 — INDUSTRY-GRADE DESIGN SYSTEM
   Dark Mode · Glassmorphism · Premium Typography
   ═══════════════════════════════════════════════════════════════ */

/* --- Google Fonts Import --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* --- Root Variables --- */
:root {
    --g-bg-primary: #0B1120;
    --g-bg-secondary: #111827;
    --g-bg-card: rgba(17, 24, 39, 0.75);
    --g-bg-glass: rgba(15, 23, 42, 0.65);
    --g-border: rgba(255, 255, 255, 0.06);
    --g-border-hover: rgba(255, 255, 255, 0.12);
    --g-text-primary: #F1F5F9;
    --g-text-secondary: #94A3B8;
    --g-text-muted: #64748B;
    --g-accent-teal: #14B8A6;
    --g-accent-sky: #38BDF8;
    --g-accent-violet: #8B5CF6;
    --g-accent-amber: #F59E0B;
    --g-accent-rose: #F43F5E;
    --g-gradient-brand: linear-gradient(135deg, #0D9488 0%, #0EA5E9 50%, #8B5CF6 100%);
    --g-shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
    --g-shadow-md: 0 8px 24px rgba(0, 0, 0, 0.35);
    --g-shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.45);
    --g-radius-sm: 8px;
    --g-radius-md: 12px;
    --g-radius-lg: 16px;
    --g-radius-xl: 20px;
}

/* --- Global App Background --- */
.stApp, .main .block-container {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
}
.stApp {
    background: linear-gradient(180deg, #0B1120 0%, #111827 40%, #0F172A 100%) !important;
}

/* --- Sidebar Overhaul --- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1120 0%, #0F172A 60%, #111827 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] label {
    color: #CBD5E1 !important;
}

/* --- Premium Metric Cards --- */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.65)) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: var(--g-radius-md) !important;
    padding: 18px 20px !important;
    box-shadow: var(--g-shadow-sm) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(20, 184, 166, 0.3) !important;
    box-shadow: var(--g-shadow-md), 0 0 20px rgba(20, 184, 166, 0.08) !important;
    transform: translateY(-2px);
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #F1F5F9 !important;
    font-weight: 800 !important;
    font-family: 'JetBrains Mono', 'Inter', monospace !important;
}

/* --- Tab System Overhaul --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(15, 23, 42, 0.5) !important;
    border-radius: var(--g-radius-md) !important;
    padding: 4px !important;
    border: 1px solid rgba(255, 255, 255, 0.04) !important;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 22px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: var(--g-radius-sm) !important;
    color: #94A3B8 !important;
    transition: all 0.25s ease !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(30, 41, 59, 0.6) !important;
    color: #F1F5F9 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(13, 148, 136, 0.2), rgba(14, 165, 233, 0.15)) !important;
    color: #2DD4BF !important;
    border: 1px solid rgba(45, 212, 191, 0.25) !important;
    box-shadow: 0 0 12px rgba(20, 184, 166, 0.1) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* --- Expander Overhaul --- */
div[data-testid="stExpander"] {
    background: var(--g-bg-glass) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid var(--g-border) !important;
    border-radius: var(--g-radius-md) !important;
    overflow: hidden;
}
div[data-testid="stExpander"] details summary {
    padding: 14px 18px !important;
}
div[data-testid="stExpander"] details summary p {
    font-weight: 700 !important;
    font-size: 14px !important;
    color: #E2E8F0 !important;
}
div[data-testid="stExpander"] details[open] summary {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

/* --- Button Enhancements --- */
.stButton > button {
    font-family: 'Inter', system-ui, sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: var(--g-radius-sm) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    letter-spacing: 0.3px !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #0D9488, #0EA5E9) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(13, 148, 136, 0.3) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    box-shadow: 0 6px 20px rgba(13, 148, 136, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* --- Selectbox & Input Styling --- */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: var(--g-radius-sm) !important;
    color: #F1F5F9 !important;
}

/* --- DataFrame Styling --- */
.stDataFrame {
    border-radius: var(--g-radius-md) !important;
    overflow: hidden !important;
    border: 1px solid var(--g-border) !important;
}

/* --- Slider Styling --- */
.stSlider > div > div > div > div {
    background: var(--g-accent-teal) !important;
}

/* --- Progress Bar --- */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #0D9488, #38BDF8) !important;
    border-radius: 100px !important;
}

/* --- Custom Scrollbar --- */
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.4); }
::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.25); border-radius: 100px; }
::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.4); }

/* --- Alert/Info/Warning Boxes --- */
.stAlert {
    border-radius: var(--g-radius-sm) !important;
    border: 1px solid var(--g-border) !important;
}

/* --- Tooltip --- */
div[data-testid="stTooltipIcon"] svg { color: #64748B !important; }

/* --- File Uploader --- */
section[data-testid="stFileUploader"] {
    border: 2px dashed rgba(255, 255, 255, 0.08) !important;
    border-radius: var(--g-radius-md) !important;
    background: rgba(15, 23, 42, 0.3) !important;
    transition: border-color 0.3s ease !important;
}
section[data-testid="stFileUploader"]:hover {
    border-color: rgba(20, 184, 166, 0.3) !important;
}

/* --- Animated Gradient Accent Bar (for dividers) --- */
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.geostra-accent-bar {
    height: 3px;
    background: linear-gradient(90deg, #0D9488, #38BDF8, #8B5CF6, #F59E0B, #0D9488);
    background-size: 300% 100%;
    animation: gradientShift 6s ease infinite;
    border-radius: 100px;
    margin: 8px 0 16px 0;
}

/* --- Fade-in Animation --- */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.geostra-fade-in {
    animation: fadeInUp 0.5s ease-out forwards;
}

/* --- Glass Card Component --- */
.geostra-glass-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.5));
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: var(--g-radius-lg);
    padding: 24px;
    box-shadow: var(--g-shadow-md);
    transition: all 0.3s ease;
}
.geostra-glass-card:hover {
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: var(--g-shadow-lg);
}

/* --- Status Pill --- */
.geostra-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.geostra-pill-teal {
    background: rgba(13, 148, 136, 0.15);
    color: #2DD4BF;
    border: 1px solid rgba(45, 212, 191, 0.2);
}
.geostra-pill-sky {
    background: rgba(56, 189, 248, 0.12);
    color: #7DD3FC;
    border: 1px solid rgba(56, 189, 248, 0.2);
}
.geostra-pill-violet {
    background: rgba(139, 92, 246, 0.12);
    color: #C4B5FD;
    border: 1px solid rgba(139, 92, 246, 0.2);
}

/* --- Section Header Utility --- */
.geostra-section-title {
    font-size: 15px;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.geostra-section-title::before {
    content: '';
    width: 4px;
    height: 20px;
    background: var(--g-gradient-brand);
    border-radius: 100px;
    flex-shrink: 0;
}

/* --- Hide default Streamlit elements for cleaner look --- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: rgba(11, 17, 32, 0.85) !important;
    backdrop-filter: blur(12px) !important;
}
</style>""", unsafe_allow_html=True)

DRIVE_BASE = r'./SIG_Deteksi_Bangunan'
DRIVE_BATCH = os.path.join(DRIVE_BASE, 'batch_results')
os.makedirs(DRIVE_BATCH, exist_ok=True)
TEMP = os.path.join(os.getcwd(), 'temp')
TEMP_UPLOADS = os.path.join(TEMP, 'uploads')
os.makedirs(TEMP_UPLOADS, exist_ok=True)

AREA_COLORS = [
    {'building':'#1f77b4','perm':'#1f77b4','grid_j':'#aec7e8','grid_s':'#1f77b4','grid_t':'#08306b'}, # Blue
    {'building':'#ff7f0e','perm':'#ff7f0e','grid_j':'#ffbb78','grid_s':'#ff7f0e','grid_t':'#7f3b04'}, # Orange
    {'building':'#2ca02c','perm':'#2ca02c','grid_j':'#98df8a','grid_s':'#2ca02c','grid_t':'#00441b'}, # Green
    {'building':'#d62728','perm':'#d62728','grid_j':'#ff9896','grid_s':'#d62728','grid_t':'#67000d'}, # Red
    {'building':'#9467bd','perm':'#9467bd','grid_j':'#c5b0d5','grid_s':'#9467bd','grid_t':'#3f007d'}, # Purple
]

# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════
def S(stats_dict, key, default=0):
    return stats_dict.get(key, default)

def clear_area(area_name):
    st.session_state['all_stats'].pop(area_name, None)
    st.session_state['all_results'].pop(area_name, None)
    target = os.path.join(DRIVE_BATCH, area_name)
    if os.path.exists(target):
        shutil.rmtree(target)

def clear_all_areas():
    st.session_state['all_stats'] = {}
    st.session_state['all_results'] = {}
    if os.path.exists(DRIVE_BATCH):
        for item in os.listdir(DRIVE_BATCH):
            item_path = os.path.join(DRIVE_BATCH, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

def load_area_results(area_name):
    if area_name in st.session_state['all_results']:
        return st.session_state['all_results'][area_name]
    
    area_dir = os.path.join(DRIVE_BATCH, area_name)
    if not os.path.exists(area_dir):
        return None

    bgn_p = os.path.join(area_dir, 'hasil_deteksi_bangunan.geojson')
    grid_p = os.path.join(area_dir, 'grid_kepadatan.geojson')
    perm_p = os.path.join(area_dir, 'area_permukiman.geojson')
    kdf_p = os.path.join(area_dir, 'kepadatan_bertingkat.geojson')
    stats_p = os.path.join(area_dir, 'stats.json')
    chart_p = os.path.join(area_dir, 'statistik.png')

    if os.path.exists(bgn_p) and os.path.exists(stats_p):
        try:
            gdf = gpd.read_file(bgn_p)
            grid = gpd.read_file(grid_p) if os.path.exists(grid_p) else gpd.GeoDataFrame()
            perm = gpd.read_file(perm_p) if os.path.exists(perm_p) else gpd.GeoDataFrame()
            kdf = gpd.read_file(kdf_p) if os.path.exists(kdf_p) else gpd.GeoDataFrame()
            with open(stats_p) as f:
                stats = json.load(f)

            if not os.path.exists(chart_p) and len(gdf):
                cp = make_chart_area(gdf, grid, stats, area_name)
                if cp and os.path.exists(cp):
                    shutil.copy(cp, chart_p)

            # Restore saved color_idx — fallback to area list order if not in stats
            color_idx = stats.get('color_idx', None)

            res = {
                'gdf': gdf,
                'grid': grid,
                'perm': perm,
                'kdf': kdf,
                'stats': stats,
                'chart': chart_p if os.path.exists(chart_p) else None,
                'used_gs': 0.001,
                'color_idx': color_idx
            }
            st.session_state['all_results'][area_name] = res
            return res
        except Exception:
            return None
    return None

# ══════════════════════════════════════════════════════════════
# STATE INIT
# ══════════════════════════════════════════════════════════════
for k in ['queue','all_results','all_stats','batch_running','model']:
    if k not in st.session_state:
        st.session_state[k] = [] if k == 'queue' else {} if k in ('all_results','all_stats') else False if k == 'batch_running' else None

for area in (os.listdir(DRIVE_BATCH) if os.path.exists(DRIVE_BATCH) else []):
    sp = os.path.join(DRIVE_BATCH, area, 'stats.json')
    if os.path.exists(sp):
        if area not in st.session_state['all_stats']:
            with open(sp) as f:
                st.session_state['all_stats'][area] = json.load(f)
        load_area_results(area)

# ══════════════════════════════════════════════════════════════
# PROCESSING FUNCTIONS
# ══════════════════════════════════════════════════════════════
def do_tile(path, tsz, prog):
    shutil.rmtree(os.path.join(TEMP, 'tiles_tif'), ignore_errors=True)
    shutil.rmtree(os.path.join(TEMP, 'tiles_jpg'), ignore_errors=True)
    os.makedirs(os.path.join(TEMP, 'tiles_tif'), exist_ok=True)
    os.makedirs(os.path.join(TEMP, 'tiles_jpg'), exist_ok=True)
    meta_list = []
    with rasterio.open(path) as src:
        W, H = src.width, src.height
        xs = list(range(0, W, tsz)); ys = list(range(0, H, tsz))
        tot = len(xs) * len(ys); done = 0
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                w = min(tsz, W - x); h = min(tsz, H - y)
                win = Window(x, y, w, h); tf = src.window_transform(win)
                dat = src.read(window=win)
                nm = f'tile_{str(i).zfill(4)}_{str(j).zfill(4)}'
                tp = os.path.join(TEMP, 'tiles_tif', f'{nm}.tif')
                mt = src.meta.copy(); mt.update({'width': w, 'height': h, 'transform': tf})
                with rasterio.open(tp, 'w', **mt) as dst:
                    dst.write(dat)
                rgb = dat[:3] if dat.shape[0] >= 3 else np.repeat(dat[:1], 3, axis=0)
                rgb = np.transpose(rgb, (1, 2, 0)).astype(np.float32)
                mn, mx = rgb.min(), rgb.max()
                rgb = np.clip((rgb - mn) / (mx - mn + 1e-8) * 255, 0, 255).astype(np.uint8)
                if w < tsz or h < tsz:
                    pad = np.zeros((tsz, tsz, 3), dtype=np.uint8); pad[:h, :w] = rgb; rgb = pad
                jp = os.path.join(TEMP, 'tiles_jpg', f'{nm}.jpg')
                Image.fromarray(rgb).save(jp, quality=95)
                meta_list.append({'name': nm, 'tif': tp, 'w': w, 'h': h})
                done += 1
                if done % 20 == 0: prog(done / tot)
    prog(1.0)
    return meta_list

def do_infer(tile_meta, conf, tsz, prog):
    if st.session_state['model'] is None:
        from ultralytics import YOLO
        best_pt_path = os.path.join(DRIVE_BASE, 'weights', 'best.pt')
        st.session_state['model'] = YOLO(best_pt_path)
    model = st.session_state['model']
    dets = []
    for i, tile in enumerate(tile_meta):
        img_path = os.path.join(TEMP, 'tiles_jpg', f"{tile['name']}.jpg")
        res = model.predict(source=img_path, conf=conf, iou=0.45, imgsz=tsz, verbose=False)
        for r in res:
            if r.boxes is None or len(r.boxes) == 0: continue
            for box in r.boxes:
                xn = box.xywhn[0].tolist()
                dets.append({
                    'tif': tile['tif'], 'xc': xn[0], 'yc': xn[1],
                    'bw': xn[2], 'bh': xn[3],
                    'conf': float(box.conf[0]), 'tile': tile['name']
                })
        if (i + 1) % 30 == 0: prog((i + 1) / len(tile_meta))
    prog(1.0)
    return dets

def do_georef(dets, prog):
    geoms, confs, tiles = [], [], []
    skipped = 0
    for i, d in enumerate(dets):
        try:
            with rasterio.open(d['tif']) as src:
                tf = src.transform; w = src.width; h = src.height
                xc = d['xc'] * w; yc = d['yc'] * h
                bw = d['bw'] * w; bh = d['bh'] * h
                lo, lt = rasterio.transform.xy(tf, yc - bh / 2, xc - bw / 2)
                hi, la = rasterio.transform.xy(tf, yc + bh / 2, xc + bw / 2)
                geoms.append(sbox(lo, la, hi, lt))
                confs.append(d['conf']); tiles.append(d['tile'])
        except Exception as e:
            skipped += 1
            pass
        if (i + 1) % 500 == 0: prog((i + 1) / len(dets))
    prog(1.0)
    if skipped > 0:
        print(f"Warning: {skipped} deteksi dilewati karena error georeferensi.")
    gdf = gpd.GeoDataFrame({'confidence': confs, 'tile': tiles, 'geometry': geoms}, crs='EPSG:4326')
    if len(gdf):
        gdf['lon'] = gdf.to_crs('EPSG:32748').geometry.centroid.to_crs('EPSG:4326').x
        gdf['lat'] = gdf.to_crs('EPSG:32748').geometry.centroid.to_crs('EPSG:4326').y
    return gdf

def do_grid(gdf, gs_mode, manual_gs, prog):
    if len(gdf) == 0:
        return gpd.GeoDataFrame(), gpd.GeoDataFrame(), gpd.GeoDataFrame(), 0.001

    bounds = gdf.total_bounds
    if gs_mode == 'Auto':
        luas_deg2 = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
        gs_raw = max(0.001, min(0.02, math.sqrt(luas_deg2 / 5000)))
        gs = round(gs_raw / 0.001) * 0.001
        if gs < 0.001: gs = 0.001
    else:
        gs = manual_gs

    nx = len(np.arange(bounds[0], bounds[2] + gs, gs))
    ny = len(np.arange(bounds[1], bounds[3] + gs, gs))
    if nx * ny > 20000:
        for cand in [0.002, 0.003, 0.005, 0.01]:
            nx2 = len(np.arange(bounds[0], bounds[2] + cand, cand))
            ny2 = len(np.arange(bounds[1], bounds[3] + cand, cand))
            if nx2 * ny2 <= 20000:
                gs = cand; break

    cells = [sbox(x, y, x + gs, y + gs)
             for x in np.arange(bounds[0], bounds[2] + gs, gs)
             for y in np.arange(bounds[1], bounds[3] + gs, gs)]
    grid = gpd.GeoDataFrame({'geometry': cells}, crs='EPSG:4326')
    prog(0.3)

    cen = gpd.GeoDataFrame(
        {'geometry': gdf.to_crs('EPSG:32748').geometry.centroid.to_crs('EPSG:4326')},
        crs='EPSG:4326')
    joined = gpd.sjoin(cen, grid, how='left', predicate='within')
    counts = joined.groupby('index_right').size().reset_index(name='count')
    grid['count'] = 0
    grid.loc[counts['index_right'].values, 'count'] = counts['count'].values
    prog(0.6)

    grid['kelas'] = grid['count'].apply(lambda c: 0 if c == 0 else 1 if c < 5 else 2 if c < 10 else 3)
    grid['kelas_nama'] = grid['kelas'].map(
        {0: 'Tidak Ada', 1: 'Jarang (1-4)', 2: 'Sedang (5-9)', 3: 'Tinggi (>=10)'})

    kls_list = []
    for kn, grp in grid[grid['kelas'] > 0].groupby('kelas_nama'):
        kls_list.append(gpd.GeoDataFrame(
            {'kelas': [kn], 'bangunan': [int(grp['count'].sum())],
             'geometry': [unary_union(grp.geometry)]}, crs='EPSG:4326'))
    kdf = gpd.GeoDataFrame(pd.concat(kls_list, ignore_index=True), crs='EPSG:4326') if kls_list else gpd.GeoDataFrame(geometry=[], crs='EPSG:4326')
    if len(kdf): kdf['luas_ha'] = kdf.to_crs('EPSG:32748').geometry.area / 10000

    perm = grid[grid['kelas'] >= 2]
    if len(perm):
        pdis = gpd.GeoDataFrame(geometry=[unary_union(perm.geometry)], crs='EPSG:4326').explode(index_parts=False).reset_index(drop=True)
        pdis['luas_ha'] = pdis.to_crs('EPSG:32748').geometry.area / 10000
    else:
        pdis = gpd.GeoDataFrame(geometry=[], crs='EPSG:4326')
    prog(1.0)
    return grid, kdf, pdis, gs

def compute_stats(gdf, grid, perm):
    if len(gdf) == 0:
        return {k: 0 for k in ['n_bgn','conf_mean','conf_std','conf_min','conf_max',
                                'luas_atap','luas_ha','rata','median','std_luas','min_luas','max_luas',
                                'aoi_km2','kd','ptb','n_perm','luas_perm',
                                'n_sel_jarang','n_sel_sedang','n_sel_tinggi',
                                'bgn_jarang','bgn_sedang','bgn_tinggi']}
    m = gdf.to_crs('EPSG:32748'); m['luas'] = m.geometry.area
    b = m.total_bounds; aoi = (b[2] - b[0]) * (b[3] - b[1])
    ptb = m['luas'].sum() / aoi * 100
    kd = len(gdf) / (aoi / 1e6)

    n_j = int(len(grid[grid['kelas'] == 1]))
    n_s = int(len(grid[grid['kelas'] == 2]))
    n_t = int(len(grid[grid['kelas'] == 3]))
    b_j = int(grid[grid['kelas'] == 1]['count'].sum()) if n_j else 0
    b_s = int(grid[grid['kelas'] == 2]['count'].sum()) if n_s else 0
    b_t = int(grid[grid['kelas'] == 3]['count'].sum()) if n_t else 0

    return {
        'n_bgn': len(gdf),
        'conf_mean': round(float(gdf['confidence'].mean()), 3),
        'conf_std': round(float(gdf['confidence'].std()), 3),
        'conf_min': round(float(gdf['confidence'].min()), 3),
        'conf_max': round(float(gdf['confidence'].max()), 3),
        'luas_atap': round(m['luas'].sum()),
        'luas_ha': round(m['luas'].sum() / 10000, 2),
        'rata': round(float(m['luas'].mean()), 1),
        'median': round(float(m['luas'].median()), 1),
        'std_luas': round(float(m['luas'].std()), 1),
        'min_luas': round(float(m['luas'].min()), 1),
        'max_luas': round(float(m['luas'].max()), 1),
        'aoi_km2': round(aoi / 1e6, 2),
        'kd': round(kd, 1),
        'ptb': round(ptb, 2),
        'n_perm': len(perm),
        'luas_perm': round(float(perm['luas_ha'].sum()), 2) if len(perm) and 'luas_ha' in perm.columns else 0,
        'n_sel_jarang': n_j, 'n_sel_sedang': n_s, 'n_sel_tinggi': n_t,
        'bgn_jarang': b_j, 'bgn_sedang': b_s, 'bgn_tinggi': b_t,
    }

def make_map_area(gdf, grid, perm, area_name):
    if len(gdf) == 0: return '<p>Tidak ada data.</p>'
    center = [float(gdf['lat'].mean()), float(gdf['lon'].mean())]
    m = folium.Map(location=center, zoom_start=15, tiles=None)

    folium.TileLayer(
        tiles='https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&key=',
        attr='Google Satellite',
        name='🛰️ Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='OpenStreetMap',
        name='OpenStreetMap',
        overlay=False,
        control=True
    ).add_to(m)

    if len(perm):
        folium.GeoJson(perm.__geo_interface__, name='Area Permukiman',
                       style_function=lambda x: {'fillColor': '#FFA500', 'color': '#FF6600',
                                                  'weight': 2, 'fillOpacity': 0.35}).add_to(m)

    ksty = {
        'Jarang (1-4)': {'fillColor': '#FFEB3B', 'color': '#CCCC00', 'weight': 1, 'fillOpacity': 0.5},
        'Sedang (5-9)': {'fillColor': '#FF9800', 'color': '#E65100', 'weight': 1, 'fillOpacity': 0.5},
        'Tinggi (>=10)': {'fillColor': '#F44336', 'color': '#B71C1C', 'weight': 1, 'fillOpacity': 0.5},
    }
    for kn, sty in ksty.items():
        sub = grid[grid['kelas_nama'] == kn]
        if len(sub):
            folium.GeoJson(sub.__geo_interface__, name=f'Kepadatan {kn}',
                           style_function=lambda x, s=sty: s,
                           tooltip=folium.GeoJsonTooltip(['count', 'kelas_nama'], ['Bangunan:', 'Kelas:']),
                           show=False).add_to(m)

    MAX = 5000
    subset = gdf if len(gdf) <= MAX else gdf.sample(MAX)
    fg_bgn = folium.FeatureGroup(name='Bangunan Terdeteksi', show=True)
    for _, row in subset.iterrows():
        coords = [[c[1], c[0]] for c in row.geometry.exterior.coords]
        cf = row['confidence']
        col = '#00CC00' if cf >= 0.7 else '#FFAA00' if cf >= 0.5 else '#FF3300'
        folium.Polygon(locations=coords, color=col, weight=1.5,
                       fill=True, fill_color=col, fill_opacity=0.25,
                       tooltip=f'Conf: {round(cf,2)}').add_to(fg_bgn)
    fg_bgn.add_to(m)

    # 4. Heatmap Kepadatan Layer
    heat_data = [[row['lat'], row['lon']] for _, row in gdf.iterrows()]
    if heat_data:
        HeatMap(heat_data, name="Heatmap Kepadatan Bangunan", radius=15, blur=10, min_opacity=0.3, show=False).add_to(m)

    folium.LayerControl(collapsed=True, position='topright').add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)
    MeasureControl().add_to(m)

    css = """
    <style>
        .leaflet-control-layers {
            background: rgba(15, 23, 42, 0.92) !important;
            backdrop-filter: blur(12px) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
            padding: 10px 14px !important;
            max-height: 280px !important;
            overflow-y: auto !important;
            font-family: 'Segoe UI', system-ui, sans-serif !important;
        }
        .leaflet-control-layers-toggle {
            background-color: rgba(15, 23, 42, 0.9) !important;
            border-radius: 8px !important;
        }
        .leaflet-control-layers-overlays label, .leaflet-control-layers-base label {
            color: #f8fafc !important;
            font-size: 12px !important;
            cursor: pointer !important;
        }
    </style>
    """
    m.get_root().html.add_child(folium.Element(css))

    legend_html = f"""
    <div style="position:fixed; top:12px; left:55px; z-index:999; font-family: 'Segoe UI', Roboto, sans-serif;">
      <details open style="background: rgba(15, 23, 42, 0.90); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; padding: 10px 14px; color: #f8fafc; box-shadow: 0 10px 30px rgba(0,0,0,0.5); min-width: 220px;">
        <summary style="cursor: pointer; font-weight: 700; font-size: 13px; outline: none; user-select: none; display: flex; align-items: center; justify-content: space-between;">
          <span>Legend — {area_name}</span>
        </summary>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.15); margin: 8px 0;">
        <div style="font-size: 11px; line-height: 1.6;">
          <div style="margin-bottom: 4px;"><b>Bangunan YOLOv8:</b></div>
          <div><span style="color:#00CC00; font-weight:bold;">■</span> High Conf (≥ 0.70)</div>
          <div><span style="color:#FFAA00; font-weight:bold;">■</span> Mid Conf (0.50 - 0.69)</div>
          <div><span style="color:#FF3300; font-weight:bold;">■</span> Low Conf (< 0.50)</div>
          <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 6px 0;">
          <div><span style="color:#FF6600; font-weight:bold;">■</span> Area Permukiman</div>
          <div>Total Bangunan: <b>{len(gdf):,} unit</b></div>
        </div>
      </details>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m.get_root().render()

def make_merged_map(all_results, focus_area=None):
    all_gdfs = [r['gdf'] for r in all_results.values() if len(r['gdf'])]
    if not all_gdfs: return '<p>Tidak ada data.</p>'

    if focus_area and focus_area in all_results and len(all_results[focus_area]['gdf']):
        fgdf = all_results[focus_area]['gdf']
        center = [float(fgdf['lat'].mean()), float(fgdf['lon'].mean())]
        zoom_level = 15
    else:
        all_points = pd.concat([g[['lat', 'lon']] for g in all_gdfs])
        center = [float(all_points['lat'].mean()), float(all_points['lon'].mean())]
        zoom_level = 12

    m = folium.Map(location=center, zoom_start=zoom_level, tiles=None)

    folium.TileLayer(
        tiles='https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&key=',
        attr='Google Satellite',
        name='🛰️ Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='OpenStreetMap',
        name='OpenStreetMap',
        overlay=False,
        control=True
    ).add_to(m)

    legend_items = []

    for idx, (area_name, res) in enumerate(all_results.items()):
        if idx >= len(AREA_COLORS): break  # Limit to 5 colors
        color_slot = res.get('color_idx')
        if color_slot is None or color_slot >= len(AREA_COLORS):
            color_slot = idx
        col = AREA_COLORS[color_slot]

        n_bgn = len(res['gdf'])
        legend_items.append((area_name, col['building'], n_bgn))

        if len(res['gdf']):
            MAX = 3000
            subset = res['gdf'] if len(res['gdf']) <= MAX else res['gdf'].sample(MAX)
            fg = folium.FeatureGroup(name=f'Bangunan — {area_name}', show=True)
            for _, row in subset.iterrows():
                coords = [[c[1], c[0]] for c in row.geometry.exterior.coords]
                folium.Polygon(locations=coords, color=col['building'], weight=1,
                               fill=True, fill_color=col['building'], fill_opacity=0.3,
                               tooltip=f'{area_name} | Conf:{round(row["confidence"],2)}').add_to(fg)
            fg.add_to(m)

        if len(res['perm']):
            folium.GeoJson(res['perm'].__geo_interface__,
                           name=f'Permukiman — {area_name}',
                           style_function=lambda x, c=col: {'color': c['perm'], 'fillColor': c['perm'],
                                                             'weight': 2, 'fillOpacity': 0.4},
                           show=False).add_to(m)

        for kn, kk in [('Jarang (1-4)', 'grid_j'), ('Sedang (5-9)', 'grid_s'), ('Tinggi (>=10)', 'grid_t')]:
            sub = res['grid'][res['grid']['kelas_nama'] == kn]
            if len(sub):
                folium.GeoJson(sub.__geo_interface__,
                               name=f'Grid {kn} — {area_name}',
                               style_function=lambda x, c=col[kk]: {'fillColor': c, 'color': c, 'weight': 1, 'fillOpacity': 0.5},
                               tooltip=folium.GeoJsonTooltip(['count', 'kelas_nama'], ['Bangunan:', 'Kelas:']),
                               show=False).add_to(m)

    folium.LayerControl(collapsed=True, position='topright').add_to(m)
    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)

    total_bgn = sum(len(r['gdf']) for r in all_results.values())
    total_areas = min(len(all_results), 5)

    css = """
    <style>
        .leaflet-control-layers {
            background: rgba(15, 23, 42, 0.92) !important;
            backdrop-filter: blur(12px) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            padding: 12px 16px !important;
            max-height: 300px !important;
            overflow-y: auto !important;
            font-family: 'Segoe UI', system-ui, sans-serif !important;
        }
        .leaflet-control-layers-toggle {
            background-color: rgba(15, 23, 42, 0.9) !important;
            border-radius: 8px !important;
            width: 38px !important;
            height: 38px !important;
        }
        .leaflet-control-layers-overlays label, .leaflet-control-layers-base label {
            color: #f8fafc !important;
            font-size: 12px !important;
            cursor: pointer !important;
            margin-bottom: 3px !important;
        }
        .leaflet-control-layers-scrollbar::-webkit-scrollbar {
            width: 6px;
        }
        .leaflet-control-layers-scrollbar::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.3);
            border-radius: 3px;
        }
    </style>
    """
    m.get_root().html.add_child(folium.Element(css))

    color_rows_html = ""
    for aname, hexcol, nbgn in legend_items:
        color_rows_html += f"""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
            <span><span style="color:{hexcol}; font-size:14px;">●</span> <b>{aname}</b></span>
            <span style="opacity:0.8; font-size:11px;">{nbgn:,} bgn</span>
        </div>
        """

    legend_html = f"""
    <div style="position:fixed; top:12px; left:55px; z-index:999; font-family: 'Segoe UI', Roboto, sans-serif;">
      <details open style="background: rgba(15, 23, 42, 0.90); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; padding: 10px 14px; color: #f8fafc; box-shadow: 0 10px 30px rgba(0,0,0,0.5); min-width: 240px; max-width: 300px;">
        <summary style="cursor: pointer; font-weight: 700; font-size: 13px; outline: none; user-select: none; display: flex; align-items: center; justify-content: space-between;">
          <span>Peta Gabungan ({total_areas} Area)</span>
        </summary>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.15); margin: 8px 0;">
        <div style="font-size: 11px; line-height: 1.6;">
          <div style="margin-bottom: 6px; font-weight:600; opacity:0.9;">🎨 Warna Indikator Area:</div>
          {color_rows_html}
          <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.15); margin: 6px 0;">
          <div style="display:flex; align-items:center; justify-content:space-between; font-weight:700; font-size:12px;">
            <span>Total Terdeteksi</span>
            <span style="color:#60a5fa;">{total_bgn:,} unit</span>
          </div>
        </div>
      </details>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m.get_root().render()

def make_chart_area(gdf, grid, stats, area_name):
    if len(gdf) == 0: return None
    gm = gdf.to_crs('EPSG:32748'); gm['luas'] = gm.geometry.area
    bins = [0, 25, 50, 100, 200, 500, float('inf')]
    labels = ['<25', '25-50', '50-100', '100-200', '200-500', '>500']
    gm['kat'] = pd.cut(gm['luas'], bins=bins, labels=labels)
    dist = gm['kat'].value_counts().sort_index()
    kc = grid[grid['kelas'] > 0].groupby('kelas_nama')['count'].sum()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor='#ffffff')

    axes[0, 0].hist(gdf['confidence'].values, bins=25, color='steelblue', edgecolor='white')
    axes[0, 0].axvline(S(stats, 'conf_mean'), color='red', linestyle='--', label=f"Mean: {S(stats, 'conf_mean')}")
    axes[0, 0].axvline(0.7, color='green', linestyle=':', label='0.7')
    axes[0, 0].axvline(0.5, color='orange', linestyle=':', label='0.5')
    axes[0, 0].set_title('Distribusi Confidence Score', fontsize=11, color='#0f172a', fontweight='bold')
    axes[0, 0].set_xlabel('Confidence', color='#475569'); axes[0, 0].set_ylabel('Frekuensi', color='#475569')
    axes[0, 0].tick_params(colors='#334155')
    axes[0, 0].set_facecolor('#ffffff')
    axes[0, 0].grid(axis='y', linestyle='--', alpha=0.3, color='#94a3b8')
    axes[0, 0].legend(fontsize=8)

    cl = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0', '#795548']
    b2 = axes[0, 1].bar(range(len(dist)), dist.values, color=cl[:len(dist)])
    axes[0, 1].set_xticks(range(len(dist)))
    axes[0, 1].set_xticklabels([str(l) + 'm²' for l in dist.index], rotation=30, ha='right', fontsize=9, color='#334155')
    axes[0, 1].set_title('Distribusi Ukuran Bangunan', fontsize=11, color='#0f172a', fontweight='bold')
    axes[0, 1].set_ylabel('Jumlah', color='#475569')
    axes[0, 1].tick_params(colors='#334155')
    axes[0, 1].set_facecolor('#ffffff')
    axes[0, 1].grid(axis='y', linestyle='--', alpha=0.3, color='#94a3b8')
    for b, v in zip(b2, dist.values):
        axes[0, 1].text(b.get_x() + b.get_width() / 2, v + 0.5, str(v), ha='center', fontsize=8, color='#0f172a')

    kno = ['Jarang (1-4)', 'Sedang (5-9)', 'Tinggi (>=10)']
    kv = [int(kc.get(k, 0)) for k in kno]
    kc2 = ['#FFEB3B', '#FF9800', '#F44336']
    b3 = axes[1, 0].bar(range(3), kv, color=kc2)
    axes[1, 0].set_xticks(range(3))
    axes[1, 0].set_xticklabels(kno, rotation=15, ha='right', fontsize=9, color='#334155')
    axes[1, 0].set_title('Bangunan per Kelas Kepadatan', fontsize=11, color='#0f172a', fontweight='bold')
    axes[1, 0].set_ylabel('Jumlah Bangunan', color='#475569')
    axes[1, 0].tick_params(colors='#334155')
    axes[1, 0].set_facecolor('#ffffff')
    axes[1, 0].grid(axis='y', linestyle='--', alpha=0.3, color='#94a3b8')
    for b, v in zip(b3, kv):
        axes[1, 0].text(b.get_x() + b.get_width() / 2, v + 0.5, str(v), ha='center', fontsize=9, color='#0f172a')

    axes[1, 1].pie([S(stats, 'ptb'), 100 - S(stats, 'ptb')],
                   labels=[f"Terbangun {S(stats, 'ptb')}%", 'Non-terbangun'],
                   colors=['#FF5722', '#4CAF50'], autopct='%1.1f%%', startangle=90,
                   wedgeprops=dict(edgecolor='white', linewidth=2),
                   textprops={'color': '#0f172a'})
    axes[1, 1].set_title(f"Tutupan Lahan AOI ({S(stats, 'aoi_km2')} km²)", fontsize=11, color='#0f172a', fontweight='bold')
    axes[1, 1].set_facecolor('#ffffff')

    for ax in [axes[0,0], axes[0,1], axes[1,0]]:
        for spine in ax.spines.values(): spine.set_color('#cbd5e1')

    plt.suptitle(f'Analisis Spasial — {area_name}', fontsize=14, fontweight='bold', color='#0f172a')
    plt.tight_layout()
    cp = os.path.join(TEMP, 'output', f'chart_{area_name}.png')
    os.makedirs(os.path.join(TEMP, 'output'), exist_ok=True)
    plt.savefig(cp, dpi=130, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    return cp

def make_status_board_charts(all_stats):
    if not all_stats: return None
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    names = list(all_stats.keys())[:5]
    bgns = [S(all_stats[k], 'n_bgn') for k in names]
    ptbs = [S(all_stats[k], 'ptb') for k in names]
    aois = [S(all_stats[k], 'aoi_km2') for k in names]
    luas_has = [S(all_stats[k], 'luas_ha') for k in names]
    colors = [AREA_COLORS[S(all_stats[k], 'color_idx', i) % len(AREA_COLORS)]['building'] for i, k in enumerate(names)]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Total Deteksi Bangunan per Area', 'Persentase Lahan Terbangun (% BCR)'),
        horizontal_spacing=0.12
    )

    # Subplot 1: Vertical Bar Chart (Building Count)
    fig.add_trace(
        go.Bar(
            x=names,
            y=bgns,
            text=[f"<b>{v:,}</b>" for v in bgns],
            textposition='outside',
            marker_color=colors,
            marker_line=dict(color='#ffffff', width=1),
            customdata=[[a] for a in aois],
            hovertemplate="<b>%{x}</b><br>Total Bangunan: <b>%{y:,} unit</b><br>Luas AOI: %{customdata[0]} km²<extra></extra>",
            name="Bangunan"
        ),
        row=1, col=1
    )

    # Subplot 2: Horizontal Bar Chart (% BCR)
    fig.add_trace(
        go.Bar(
            y=names,
            x=ptbs,
            orientation='h',
            text=[f"<b>{v}%</b>" for v in ptbs],
            textposition='outside',
            marker_color=colors,
            marker_line=dict(color='#ffffff', width=1),
            customdata=[[l] for l in luas_has],
            hovertemplate="<b>%{y}</b><br>% Lahan Terbangun: <b>%{x}%</b><br>Luas Atap: %{customdata[0]} ha<extra></extra>",
            name="BCR (%)"
        ),
        row=1, col=2
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(15, 23, 42, 0.85)',
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        height=380,
        margin=dict(l=40, r=40, t=50, b=40),
        showlegend=False,
        font=dict(family="Segoe UI, system-ui, sans-serif", color="#f8fafc", size=12)
    )

    fig.update_xaxes(title_text="Area", row=1, col=1, gridcolor='rgba(255,255,255,0.08)')
    fig.update_yaxes(title_text="Jumlah Unit", row=1, col=1, gridcolor='rgba(255,255,255,0.08)')

    fig.update_xaxes(title_text="Rasio Terbangun (%)", row=1, col=2, gridcolor='rgba(255,255,255,0.08)')
    fig.update_yaxes(title_text="Area", row=1, col=2, gridcolor='rgba(255,255,255,0.08)')

    return fig

def make_comparison_charts(all_stats):
    names = list(all_stats.keys())[:5]
    if len(names) < 2: return None, None

    fig, axes = plt.subplots(2, 2, figsize=(16, 11), facecolor='#ffffff')
    bar_colors = [AREA_COLORS[S(all_stats[n], 'color_idx', i) % len(AREA_COLORS)]['building'] for i, n in enumerate(names)]

    vals = [S(all_stats[n], 'n_bgn') for n in names]
    bars = axes[0, 0].bar(names, vals, color=bar_colors, edgecolor='none', width=0.55)
    axes[0, 0].set_title('Total Bangunan per Area', fontsize=12, fontweight='bold', color='#0f172a', pad=10)
    axes[0, 0].set_ylabel('Jumlah Unit', color='#475569', fontsize=9)
    axes[0, 0].tick_params(colors='#334155', labelsize=9)
    axes[0, 0].set_facecolor('#ffffff')
    axes[0, 0].grid(axis='y', linestyle='--', alpha=0.3, color='#94a3b8')
    for b, v in zip(bars, vals):
        axes[0, 0].text(b.get_x() + b.get_width() / 2, v + (max(vals) * 0.015 if vals else 1), f'{v:,}', ha='center', fontsize=9, color='#0f172a', fontweight='bold')

    vals2 = [S(all_stats[n], 'kd') for n in names]
    bars2 = axes[0, 1].bar(names, vals2, color=bar_colors, edgecolor='none', width=0.55)
    axes[0, 1].set_title('Kepadatan Bangunan (bgn/km²)', fontsize=12, fontweight='bold', color='#0f172a', pad=10)
    axes[0, 1].set_ylabel('bgn/km²', color='#475569', fontsize=9)
    axes[0, 1].tick_params(colors='#334155', labelsize=9)
    axes[0, 1].set_facecolor('#ffffff')
    axes[0, 1].grid(axis='y', linestyle='--', alpha=0.3, color='#94a3b8')
    for b, v in zip(bars2, vals2):
        axes[0, 1].text(b.get_x() + b.get_width() / 2, v + (max(vals2) * 0.015 if vals2 else 1), str(v), ha='center', fontsize=9, color='#0f172a', fontweight='bold')

    axes[1, 0].set_facecolor('#ffffff')
    for idx, n in enumerate(names):
        axes[1, 0].scatter(S(all_stats[n], 'kd'), S(all_stats[n], 'ptb'), s=140, zorder=5, color=bar_colors[idx], edgecolors='#ffffff', linewidth=1.2)
        axes[1, 0].annotate(n, (S(all_stats[n], 'kd'), S(all_stats[n], 'ptb')),
                            textcoords='offset points', xytext=(8, 8), fontsize=10, color='#0f172a', fontweight='bold')
    axes[1, 0].set_title('Matriks Kepadatan vs % Lahan Terbangun (% BCR)', fontsize=12, fontweight='bold', color='#0f172a', pad=10)
    axes[1, 0].set_xlabel('Kepadatan (bgn/km²)', color='#475569', fontsize=9); axes[1, 0].set_ylabel('% Lahan Terbangun', color='#475569', fontsize=9)
    axes[1, 0].tick_params(colors='#334155', labelsize=9)
    axes[1, 0].grid(True, linestyle='--', alpha=0.3, color='#94a3b8')

    categories = ['Bangunan', 'Kepadatan', '% Terbangun', 'Conf AI', 'Permukiman']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    axes[1, 1].remove()
    axes[1, 1] = fig.add_subplot(224, polar=True, facecolor='#ffffff')
    axes[1, 1].set_theta_offset(np.pi / 2)
    axes[1, 1].set_theta_direction(-1)
    axes[1, 1].set_xticks(angles[:-1])
    axes[1, 1].set_xticklabels(categories, fontsize=9, color='#0f172a', fontweight='bold')
    axes[1, 1].tick_params(colors='#475569')

    raw = {n: [S(all_stats[n], 'n_bgn'), S(all_stats[n], 'kd'), S(all_stats[n], 'ptb'),
               S(all_stats[n], 'conf_mean') * 100, S(all_stats[n], 'luas_perm')] for n in names}
    maxvals = [max(raw[n][i] for n in names) or 1 for i in range(5)]

    for idx, n in enumerate(names):
        values = [raw[n][i] / maxvals[i] for i in range(5)]
        values += values[:1]
        axes[1, 1].plot(angles, values, 'o-', linewidth=2, label=n, color=bar_colors[idx])
        axes[1, 1].fill(angles, values, alpha=0.15, color=bar_colors[idx])
    axes[1, 1].set_title('Profil Radar Multidimensi per Area', fontsize=12, fontweight='bold', pad=20, color='#0f172a')
    leg = axes[1, 1].legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=8.5)
    for text in leg.get_texts(): text.set_color('#0f172a')

    for ax in [axes[0,0], axes[0,1], axes[1,0]]:
        for spine in ax.spines.values(): spine.set_color('#cbd5e1')

    plt.suptitle('Dashboard Komparasi Spasial Antar-Area', fontsize=14, fontweight='bold', color='#0f172a', y=0.98)
    plt.tight_layout()
    cp = os.path.join(TEMP, 'output', 'komparasi.png')
    os.makedirs(os.path.join(TEMP, 'output'), exist_ok=True)
    plt.savefig(cp, dpi=140, facecolor=fig.get_facecolor(), bbox_inches='tight'); plt.close()

    rankings = {
        'Bangunan Terbanyak': max(names, key=lambda n: S(all_stats[n], 'n_bgn')),
        'AOI Terluas': max(names, key=lambda n: S(all_stats[n], 'aoi_km2')),
        'Terpadat': max(names, key=lambda n: S(all_stats[n], 'kd')),
        'Conf Tertinggi': max(names, key=lambda n: S(all_stats[n], 'conf_mean')),
        'Permukiman Terluas': max(names, key=lambda n: S(all_stats[n], 'luas_perm')),
    }
    return cp, rankings

def generate_pdf(all_stats, all_chart_paths, comparison_chart_path):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, 
                                     Spacer, Image as RLImage, PageBreak, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors as rl_colors
    from reportlab.pdfgen import canvas

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_decorations(num_pages)
                super().showPage()
            super().save()

        def draw_page_decorations(self, page_count):
            if self._pageNumber == 1:
                return  # Skip cover page
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(rl_colors.HexColor("#475569"))
            
            # Header text & line
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'image', 'logo.png')
            if os.path.exists(logo_path):
                self.drawImage(logo_path, 54, 796, width=16, height=16, mask='auto')
                self.drawString(76, 802, "GEOSTRA — LAPORAN ANALISIS TATA RUANG DAN AREA (DETEKSI YOLOv8)")
            else:
                self.drawString(54, 802, "GEOSTRA — LAPORAN ANALISIS TATA RUANG DAN AREA (DETEKSI YOLOv8)")
            
            self.setStrokeColor(rl_colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(54, 794, 541, 794)

            # Footer line & text
            self.line(54, 45, 541, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(rl_colors.HexColor("#64748B"))
            self.drawString(54, 32, "Geospasial Sistem Tata Ruang dan Area — Hasil Inferensi Deep Learning")
            page_text = f"Halaman {self._pageNumber} dari {page_count}"
            self.drawRightString(541, 32, page_text)
            self.restoreState()

    pdf_path = os.path.join(TEMP, 'output', 'batch_report.pdf')
    os.makedirs(os.path.join(TEMP, 'output'), exist_ok=True)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    
    c_primary = rl_colors.HexColor("#1E293B")    # Slate 800
    c_secondary = rl_colors.HexColor("#0D9488")  # Teal 600
    c_dark = rl_colors.HexColor("#334155")       # Slate 700
    c_bg_light = rl_colors.HexColor("#F8FAFC")   # Slate 50
    c_border = rl_colors.HexColor("#E2E8F0")     # Slate 200

    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=26, leading=30,
        textColor=rl_colors.white, alignment=0
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=rl_colors.HexColor("#38BDF8"), alignment=0
    )
    desc_style = ParagraphStyle(
        'CoverDesc', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14,
        textColor=rl_colors.HexColor("#94A3B8"), alignment=0
    )
    h1_style = ParagraphStyle(
        'SectionH1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, leading=19,
        textColor=c_primary, spaceBefore=15, spaceAfter=10
    )
    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=c_secondary, spaceBefore=10, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13.5,
        textColor=c_dark, alignment=4
    )
    toc_style = ParagraphStyle(
        'TOCItem', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=15,
        textColor=c_primary
    )
    
    names = list(all_stats.keys())
    total_bgn = sum(S(s, 'n_bgn') for s in all_stats.values())
    total_aoi = round(sum(S(s, 'aoi_km2') for s in all_stats.values()), 2)
    total_atap_ha = round(sum(S(s, 'luas_ha') for s in all_stats.values()), 2)
    total_perm_ha = round(sum(S(s, 'luas_perm') for s in all_stats.values()), 2)

    # PAGE 1: COVER PAGE
    story.append(Spacer(1, 10))
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'image', 'logo.png')
    
    if os.path.exists(logo_path):
        logo_img = RLImage(logo_path, width=60, height=60)
        header_data = [
            [logo_img, Paragraph('GEOSTRA', title_style)],
            ['', Paragraph('Geospasial Sistem Tata Ruang dan Area', subtitle_style)],
            ['', Paragraph('Laporan Analisis Spasial & Inferensi Deteksi Bangunan YOLOv8', desc_style)]
        ]
        header_table = Table(header_data, colWidths=[70, 417])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_primary),
            ('SPAN', (0,0), (0,2)),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (1,0), 16),
            ('BOTTOMPADDING', (0,2), (1,2), 16),
            ('LEFTPADDING', (0,0), (0,2), 16),
            ('RIGHTPADDING', (1,0), (1,2), 16),
        ]))
    else:
        header_data = [
            [Paragraph('GEOSTRA', title_style)],
            [Paragraph('Geospasial Sistem Tata Ruang dan Area', subtitle_style)],
            [Paragraph('Laporan Analisis Spasial & Inferensi Deteksi Bangunan YOLOv8', desc_style)]
        ]
        header_table = Table(header_data, colWidths=[487])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), c_primary),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (0,0), 16),
            ('BOTTOMPADDING', (0,2), (0,2), 16),
            ('LEFTPADDING', (0,0), (-1,-1), 16),
            ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ]))

    story.append(header_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=4, color=c_secondary, spaceAfter=18))

    tz_wib = pytz.timezone('Asia/Jakarta')
    waktu_sekarang = datetime.now(tz_wib).strftime("%d %B %Y, %H:%M WIB")
    
    meta_info = [
        [Paragraph('<b>Tanggal Pembuatan:</b>', body_style), Paragraph(waktu_sekarang, body_style)],
        [Paragraph('<b>Jumlah Area Studi:</b>', body_style), Paragraph(f'{len(all_stats)} Wilayah GeoTIFF', body_style)],
        [Paragraph('<b>Total Deteksi Bangunan:</b>', body_style), Paragraph(f'<b>{total_bgn:,} Unit</b>', body_style)],
        [Paragraph('<b>Cakupan Wilayah (AOI):</b>', body_style), Paragraph(f'{total_aoi} km²', body_style)],
        [Paragraph('<b>Total Tutupan Atap:</b>', body_style), Paragraph(f'{total_atap_ha} Hektar', body_style)],
        [Paragraph('<b>Estimasi Permukiman:</b>', body_style), Paragraph(f'{total_perm_ha} Hektar', body_style)],
        [Paragraph('<b>Arsitektur Model:</b>', body_style), Paragraph('YOLOv8 + Spatial Tiling & PyTorch Pipeline', body_style)],
    ]
    meta_table = Table(meta_info, colWidths=[150, 337])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TEXTCOLOR', (0,0), (0,-1), c_dark),
        ('BACKGROUND', (0,0), (0,-1), rl_colors.HexColor("#F1F5F9")), # Darker bg for headers
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    cover_desc = (
        f"Laporan komprehensif ini menyajikan hasil ekstraksi spasial otomatis objek bangunan dan area permukiman "
        f"dari <b>{len(all_stats)} citra GeoTIFF</b> menggunakan model deep learning <i>YOLOv8</i>. Seluruh data hasil "
        f"deteksi telah dikonversi ke sistem koordinat WGS84 (EPSG:4326), dilakukan analisis kepadatan berbasis grid "
        f"rasional, serta dihitung indikator morfologi wilayahnya secara otomatis."
    )
    story.append(Paragraph(cover_desc, body_style))
    story.append(PageBreak())

    # PAGE 2: DAFTAR ISI & RINGKASAN EKSEKUTIF
    story.append(Paragraph('DAFTAR ISI LAPORAN', h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceAfter=12))
    
    toc_data = [
        [Paragraph('<b>1. Ringkasan Eksekutif & Metrik Utama Wilayah</b>', toc_style), Paragraph('Halaman 2', toc_style)],
        [Paragraph('<b>2. Tabel Komparasi Spasial Antar-Area Studi</b>', toc_style), Paragraph('Halaman 2', toc_style)],
        [Paragraph('<b>3. Dashboard Grafik & Perbandingan Multi-Area</b>', toc_style), Paragraph('Halaman 3', toc_style)],
    ]
    for idx_t, name_t in enumerate(names, start=1):
        toc_data.append([Paragraph(f'<b>4.{idx_t} Analisis Detail Area: {name_t}</b>', toc_style), Paragraph(f'Halaman {3+idx_t}', toc_style)])

    toc_table = Table(toc_data, colWidths=[387, 100])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph('1. RINGKASAN EKSEKUTIF', h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))
    
    exec_summary_text = (
        f"Berdasarkan pemrosesan batch pada <b>{len(all_stats)} area studi</b>, sistem berhasil mendeteksi "
        f"sebanyak <b>{total_bgn:,} unit bangunan fisik</b> di atas total luas wilayah pengamatan <b>{total_aoi} km²</b>. "
        f"Total luas tutupan atap bangunan teridentifikasi sebesar <b>{total_atap_ha} ha</b>, dengan estimasi zona "
        f"permukiman padat mencapai <b>{total_perm_ha} ha</b>. Secara keseluruhan, model YOLOv8 menunjukkan tingkat "
        f"keandalan inferensi yang stabil dengan nilai kepastian (confidence score) rerata tergolong sangat baik."
    )
    story.append(Paragraph(exec_summary_text, body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph('2. TABEL KOMPARASI SPASIAL ANTAR-AREA', h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    headers = ['Area Studi', 'Jumlah Bgn', 'Luas AOI', 'Kepadatan', '% Terbangun', 'Conf Mean', 'Permukiman']
    comp_table_data = [headers]
    for name, s in all_stats.items():
        comp_table_data.append([
            name,
            f"{S(s, 'n_bgn'):,}",
            f"{S(s, 'aoi_km2')} km²",
            f"{S(s, 'kd')} bgn/km²",
            f"{S(s, 'ptb')}%",
            f"{S(s, 'conf_mean')}",
            f"{S(s, 'luas_perm')} ha"
        ])
    
    comp_table = Table(comp_table_data, colWidths=[90, 65, 65, 80, 65, 60, 62])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), rl_colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [rl_colors.white, c_bg_light]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(comp_table)
    story.append(PageBreak())

    # PAGE 3: DASHBOARD GRAPHICS & COMPARISON
    story.append(Paragraph('3. DASHBOARD GRAFIK KOMPARASI MULTI-AREA', h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=10))

    comp_narrative = (
        "Grafik komparasi di bawah menggambarkan perbandingan kuantitatif antar-area studi berdasarkan empat metrik utama: "
        "Total Bangunan, Kepadatan Spasial (bgn/km²), Hubungan Kepadatan vs Persentase Terbangun, serta Profil Radar 5 Atribut. "
        "Visualisasi ini memfasilitasi identifikasi wilayah mana yang tergolong kawasan perkotaan padat versus kawasan perdesaan/suburban."
    )
    story.append(Paragraph(comp_narrative, body_style))
    story.append(Spacer(1, 10))

    if comparison_chart_path and os.path.exists(comparison_chart_path):
        story.append(RLImage(comparison_chart_path, width=480, height=350))
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # PAGE 4+: PER AREA DETAILED ANALYSIS
    for idx, (name, s) in enumerate(all_stats.items(), start=1):
        story.append(Paragraph(f'4.{idx} ANALISIS DETAIL AREA: {name.upper()}', h1_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=c_secondary, spaceAfter=10))

        n_bgn = S(s, 'n_bgn')
        aoi_km2 = S(s, 'aoi_km2')
        kd = S(s, 'kd')
        ptb = S(s, 'ptb')
        conf_m = S(s, 'conf_mean')
        conf_s = S(s, 'conf_std')
        luas_ha = S(s, 'luas_ha')
        rata = S(s, 'rata')
        median = S(s, 'median')
        n_perm = S(s, 'n_perm')
        luas_perm = S(s, 'luas_perm')
        n_sel_tinggi = S(s, 'n_sel_tinggi')
        bgn_tinggi = S(s, 'bgn_tinggi')

        dens_cat = "Tinggi (Kawasan Padat/Perkotaan)" if kd > 500 else "Sedang (Suburban)" if kd > 150 else "Rendah (Pedesaan/Agraris)"
        
        area_narration = (
            f"<b>Profil & Morfologi Wilayah:</b> Area studi <b>{name}</b> memiliki luas cakupan (AOI) sebesar <b>{aoi_km2} km²</b>. "
            f"Berdasarkan hasil analisis inferensi YOLOv8, teridentifikasi sebanyak <b>{n_bgn:,} unit objek bangunan fisik</b> dengan "
            f"kepadatan rata-rata <b>{kd} bangunan/km²</b>. Tingkat penutupan lahan oleh atap bangunan (<i>building coverage ratio</i>) "
            f"adalah sebesar <b>{ptb}%</b>, sehingga area ini dapat dikategorikan sebagai kawasan berkarakteristik <b>{dens_cat}</b>.<br/><br/>"
            f"<b>Karakteristik Ukuran Bangunan:</b> Total luas tutupan atap terdeteksi mencapai <b>{luas_ha} hektar</b>. Rata-rata luas "
            f"bangunan individual adalah <b>{rata} m²</b> dengan nilai median <b>{median} m²</b>. Hal ini menunjukkan dominasi bangunan "
            f"skala hunian standar. Zona klaster permukiman padat teridentifikasi sebanyak <b>{n_perm} klaster utama</b> dengan total "
            f"luas <b>{luas_perm} ha</b>, yang mana terdapat <b>{n_sel_tinggi} sel grid kepadatan tinggi</b> memuat {bgn_tinggi:,} unit bangunan.<br/><br/>"
            f"<b>Kualitas Inferensi YOLOv8:</b> Hasil pendeteksian memiliki nilai confidence rerata <b>{conf_m} ± {conf_s}</b>. "
            f"Tingkat presisi ini menunjukkan keandalan algoritma yang sangat tinggi dalam membedakan atap bangunan dari vegetasi atau jalan."
        )
        story.append(Paragraph(area_narration, body_style))
        story.append(Spacer(1, 10))

        area_detail_data = [
            [Paragraph('<b>Indikator Metrik</b>', body_style), Paragraph('<b>Nilai Terukur</b>', body_style), Paragraph('<b>Keterangan Spasial</b>', body_style)],
            ['Total Objek Terdeteksi', f"{n_bgn:,} Unit", 'Jumlah poligon fisik bangunan'],
            ['Luas Wilayah (AOI)', f"{aoi_km2} km²", 'Luas total bounding box GeoTIFF'],
            ['Kepadatan Bangunan', f"{kd} bgn/km²", f"Klasifikasi: {dens_cat}"],
            ['Persentase Terbangun', f"{ptb}%", 'Rasio tutupan atap vs luas AOI'],
            ['Total Luas Atap', f"{luas_ha} Hektar", f"Rata-rata: {rata} m² | Median: {median} m²"],
            ['Klaster Permukiman Padat', f"{n_perm} Klaster", f"Luas zona permukiman: {luas_perm} ha"],
            ['Confidence Score Model', f"{conf_m} ± {conf_s}", 'Tingkat akurasi deteksi YOLOv8'],
        ]
        area_table = Table(area_detail_data, colWidths=[140, 127, 220])
        area_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), c_secondary),
            ('TEXTCOLOR', (0,0), (-1,0), rl_colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, c_border),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [rl_colors.white, c_bg_light]),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(area_table)
        story.append(Spacer(1, 10))

        cp = all_chart_paths.get(name)
        if cp and os.path.exists(cp):
            story.append(Paragraph('<b>Grafik Distribusi & Analisis Spasial Area:</b>', h2_style))
            story.append(Spacer(1, 4))
            story.append(RLImage(cp, width=470, height=310))

        story.append(PageBreak())

    doc.build(story, canvasmaker=NumberedCanvas)
    return pdf_path

def generate_single_pdf(area_name, s, chart_path):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, 
                                     Spacer, Image as RLImage, PageBreak, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors as rl_colors
    from reportlab.pdfgen import canvas

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_decorations(num_pages)
                super().showPage()
            super().save()

        def draw_page_decorations(self, page_count):
            if self._pageNumber == 1:
                return  # Skip cover page
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(rl_colors.HexColor("#475569"))
            
            # Header text & line
            self.drawString(54, 802, f"LAPORAN ANALISIS SPASIAL DETAIL — AREA: {area_name.upper()}")
            self.setStrokeColor(rl_colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(54, 794, 541, 794)

            # Footer line & text
            self.line(54, 45, 541, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(rl_colors.HexColor("#64748B"))
            self.drawString(54, 32, "Sistem Otomasi SIG & Inferensi Model YOLOv8")
            page_text = f"Halaman {self._pageNumber} dari {page_count}"
            self.drawRightString(541, 32, page_text)
            self.restoreState()

    pdf_path = os.path.join(TEMP, 'output', f'laporan_{area_name}.pdf')
    os.makedirs(os.path.join(TEMP, 'output'), exist_ok=True)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()
    
    c_primary = rl_colors.HexColor("#1E293B")    # Slate 800
    c_secondary = rl_colors.HexColor("#0D9488")  # Teal 600
    c_dark = rl_colors.HexColor("#334155")       # Slate 700
    c_bg_light = rl_colors.HexColor("#F8FAFC")   # Slate 50
    c_border = rl_colors.HexColor("#E2E8F0")     # Slate 200

    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=rl_colors.white, alignment=0
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=15,
        textColor=rl_colors.HexColor("#94A3B8"), alignment=0
    )
    h1_style = ParagraphStyle(
        'SectionH1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=c_primary, spaceBefore=14, spaceAfter=8
    )
    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=c_secondary, spaceBefore=10, spaceAfter=6
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13.5,
        textColor=c_dark, alignment=4
    )

    n_bgn = S(s, 'n_bgn')
    aoi_km2 = S(s, 'aoi_km2')
    kd = S(s, 'kd')
    ptb = S(s, 'ptb')
    conf_m = S(s, 'conf_mean')
    conf_s = S(s, 'conf_std')
    luas_ha = S(s, 'luas_ha')
    luas_atap = S(s, 'luas_atap')
    rata = S(s, 'rata')
    median = S(s, 'median')
    min_l = S(s, 'min_luas')
    max_l = S(s, 'max_luas')
    n_perm = S(s, 'n_perm')
    luas_perm = S(s, 'luas_perm')
    n_j = S(s, 'n_sel_jarang'); n_s_sel = S(s, 'n_sel_sedang'); n_t_sel = S(s, 'n_sel_tinggi')
    b_j = S(s, 'bgn_jarang'); b_s = S(s, 'bgn_sedang'); b_t = S(s, 'bgn_tinggi')

    dens_cat = "Tinggi (Kawasan Padat/Perkotaan)" if kd > 500 else "Sedang (Suburban)" if kd > 150 else "Rendah (Pedesaan/Agraris)"

    # COVER PAGE / HEADER
    story.append(Spacer(1, 10))
    header_data = [[
        Paragraph(f'LAPORAN ANALISIS SPASIAL DETAIL AREA: {area_name.upper()}', title_style),
    ], [
        Paragraph('Hasil Ekstraksi Spasial Otomatis Bangunan & Morfologi Wilayah Berbasis YOLOv8', subtitle_style)
    ]]
    header_table = Table(header_data, colWidths=[487])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=4, color=c_secondary, spaceAfter=16))

    # METADATA TABLE
    meta_info = [
        [Paragraph('<b>Tanggal Analisis:</b>', body_style), Paragraph(datetime.now().strftime("%d %B %Y, %H:%M WIB"), body_style)],
        [Paragraph('<b>Nama Wilayah Studi:</b>', body_style), Paragraph(f'<b>{area_name}</b>', body_style)],
        [Paragraph('<b>Total Deteksi Bangunan:</b>', body_style), Paragraph(f'<b>{n_bgn:,} Unit</b>', body_style)],
        [Paragraph('<b>Cakupan Wilayah (AOI):</b>', body_style), Paragraph(f'{aoi_km2} km²', body_style)],
        [Paragraph('<b>Kepadatan Bangunan:</b>', body_style), Paragraph(f'<b>{kd} bgn/km²</b> ({dens_cat})', body_style)],
        [Paragraph('<b>Rasio Tutupan Atap (% Terbangun):</b>', body_style), Paragraph(f'{ptb}% dari total AOI', body_style)],
        [Paragraph('<b>Total Luas Tutupan Atap:</b>', body_style), Paragraph(f'{luas_ha} Hektar ({luas_atap:,} m²)', body_style)],
        [Paragraph('<b>Akurasi Inferensi YOLOv8:</b>', body_style), Paragraph(f'Confidence Score: <b>{conf_m} ± {conf_s}</b>', body_style)],
    ]
    meta_table = Table(meta_info, colWidths=[160, 327])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # SECTION 1: PROFIL & KARAKTERISTIK SPASIAL
    story.append(Paragraph('1. PROFIL DAN MORFOLOGI SPASIAL WILAYAH', h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    sec1_text = (
        f"Wilayah studi <b>{area_name}</b> memiliki batas spasial pengamatan (Area of Interest / AOI) seluas <b>{aoi_km2} km²</b>. "
        f"Dari hasil ekstraksi fitur berbasis model deep learning YOLOv8, teridentifikasi sebanyak <b>{n_bgn:,} unit fisik bangunan</b> "
        f"yang tersebar di seluruh area pengamatan. Kepadatan fisik rata-rata wilayah ini tercatat sebesar <b>{kd} bangunan/km²</b>, "
        f"dengan rasio tutupan permukaan oleh atap bangunan (<i>building coverage ratio</i>) mencapai <b>{ptb}%</b>. "
        f"Berdasarkan standar tipologi spasial, area ini diklasifikasikan sebagai kawasan berkarakteristik <b>{dens_cat}</b>."
    )
    story.append(Paragraph(sec1_text, body_style))
    story.append(Spacer(1, 12))

    # SECTION 2: DISPERSI UKURAN BANGUNAN & GRID KEPADATAN
    story.append(Paragraph('2. ANALISIS UKURAN ATAP DAN SEBARAN KEPADATAN GRID', h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    sec2_text = (
        f"Total akumulasi tutupan atap bangunan terdeteksi adalah sebesar <b>{luas_ha} hektar</b> (setara {luas_atap:,} m²). "
        f"Rata-rata luas atap individual per bangunan adalah <b>{rata} m²</b> dengan nilai median sebesar <b>{median} m²</b> "
        f"(rentang ukuran terdeteksi dari minimum {min_l} m² hingga maksimum {max_l} m²). Distribusi ukuran ini mengindikasikan "
        f"bahwa struktur fisik mayoritas didominasi oleh unit bangunan hunian.<br/><br/>"
        f"Berdasarkan analisis grid kepadatan rasional, distribusi keruangan unit bangunan dibagi menjadi tiga tingkatan:<br/>"
        f"• <b>Kelas Jarang (1-4 bgn/sel):</b> Terdapat <b>{n_j} sel grid</b> memuat total <b>{b_j:,} unit bangunan</b>.<br/>"
        f"• <b>Kelas Sedang (5-9 bgn/sel):</b> Terdapat <b>{n_s_sel} sel grid</b> memuat total <b>{b_s:,} unit bangunan</b>.<br/>"
        f"• <b>Kelas Tinggi (≥10 bgn/sel):</b> Terdapat <b>{n_t_sel} sel grid</b> memuat total <b>{b_t:,} unit bangunan</b>."
    )
    story.append(Paragraph(sec2_text, body_style))
    story.append(Spacer(1, 12))

    # SECTION 3: ZONA PERMUKIMAN PADAT
    story.append(Paragraph('3. IDENTIFIKASI ZONA KLASTER PERMUKIMAN', h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))

    sec3_text = (
        f"Melalui penggabungan spasial (spatial dissolve) pada sel grid berjarak kontinu dengan kelas kepadatan sedang hingga tinggi, "
        f"sistem secara otomatis mengisolasi zona permukiman utama. Pada area <b>{area_name}</b>, teridentifikasi sebanyak "
        f"<b>{n_perm} klaster permukiman utama</b> dengan estimasi total luas kawasan permukiman mencapai <b>{luas_perm} hektar</b>."
    )
    story.append(Paragraph(sec3_text, body_style))
    story.append(Spacer(1, 12))

    # SECTION 4: GRAFIK & VISUALISASI SPASIAL
    if chart_path and os.path.exists(chart_path):
        story.append(Paragraph('4. GRAFIK DISTRIBUSI DAN STATISTIK ANALISIS', h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceAfter=8))
        story.append(RLImage(chart_path, width=470, height=310))
        story.append(Spacer(1, 10))

    doc.build(story, canvasmaker=NumberedCanvas)
    return pdf_path

# ══════════════════════════════════════════════════════════════
# MAIN PROCESSING ORCHESTRATOR
# ══════════════════════════════════════════════════════════════
def process_area(area_name, file_path, conf, tsz, gs_mode, manual_gs, container, color_idx=0):
    with container:
        st_box = st.empty(); pb = st.progress(0); eta = st.empty()
        t0 = time.time()

        st_box.info(f'Validasi GeoTIFF — {area_name}...')
        with rasterio.open(file_path) as src:
            if src.count < 3:
                st_box.error(f'GeoTIFF {area_name} memiliki kurang dari 3 band (harus citra RGB).')
                return None
            if src.crs and '4326' not in str(src.crs):
                from rasterio.warp import calculate_default_transform, reproject, Resampling
                dst_crs = 'EPSG:4326'
                tr, W, H = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
                meta = src.meta.copy(); meta.update({'crs': dst_crs, 'transform': tr, 'width': W, 'height': H})
                rp = file_path.replace('.tif', '_4326.tif')
                with rasterio.open(rp, 'w', **meta) as dst:
                    for i in range(1, src.count + 1):
                        reproject(source=rasterio.band(src, i), destination=rasterio.band(dst, i),
                                  src_transform=src.transform, src_crs=src.crs,
                                  dst_transform=tr, dst_crs=dst_crs, resampling=Resampling.bilinear)
                file_path = rp
        pb.progress(5)

        st_box.info(f'Tiling — {area_name}...')
        t1 = time.time()
        def p1(v): pb.progress(int(5 + v * 20))
        tile_meta = do_tile(file_path, tsz, p1)
        eta.caption(f'Tiling: {round(time.time()-t1,1)}s | {len(tile_meta)} tiles')

        st_box.info(f'Inferensi YOLOv8 — {area_name}...')
        t2 = time.time()
        def p2(v): pb.progress(int(25 + v * 35))
        dets = do_infer(tile_meta, conf, tsz, p2)
        eta.caption(f'Inference: {round(time.time()-t2,1)}s | {len(dets)} deteksi')

        if len(dets) == 0:
            st_box.warning(f'0 bangunan terdeteksi di {area_name}. Turunkan confidence threshold.')
            return None

        st_box.info(f'Konversi Koordinat — {area_name}...')
        t3 = time.time()
        def p3(v): pb.progress(int(60 + v * 10))
        gdf = do_georef(dets, p3)

        st_box.info(f'Analisis Kepadatan — {area_name}...')
        t4 = time.time()
        def p4(v): pb.progress(int(70 + v * 15))
        grid, kdf, perm, used_gs = do_grid(gdf, gs_mode, manual_gs, p4)

        st_box.info(f'Generate Statistik & Grafik — {area_name}...')
        stats = compute_stats(gdf, grid, perm)
        stats['color_idx'] = color_idx
        stats['processing_time_s'] = round(time.time() - t0, 1)
        chart_path = make_chart_area(gdf, grid, stats, area_name)

        out_dir = os.path.join(DRIVE_BATCH, area_name)
        os.makedirs(out_dir, exist_ok=True)
        if len(gdf): gdf.to_file(os.path.join(out_dir, 'hasil_deteksi_bangunan.geojson'), driver='GeoJSON')
        if len(grid): grid.to_file(os.path.join(out_dir, 'grid_kepadatan.geojson'), driver='GeoJSON')
        if len(perm): perm.to_file(os.path.join(out_dir, 'area_permukiman.geojson'), driver='GeoJSON')
        if len(kdf): kdf.to_file(os.path.join(out_dir, 'kepadatan_bertingkat.geojson'), driver='GeoJSON')
        with open(os.path.join(out_dir, 'stats.json'), 'w') as f: json.dump(stats, f)
        if chart_path: shutil.copy(chart_path, os.path.join(out_dir, 'statistik.png'))

        shutil.rmtree(os.path.join(TEMP, 'tiles_tif'), ignore_errors=True)
        shutil.rmtree(os.path.join(TEMP, 'tiles_jpg'), ignore_errors=True)
        gc.collect()

        pb.progress(100)
        tt = round(time.time() - t0, 1)
        st_box.success(f"{area_name} selesai! {tt}s | {stats['n_bgn']} bangunan")
        eta.empty()

        return {'gdf': gdf, 'grid': grid, 'perm': perm, 'kdf': kdf,
                'stats': stats, 'chart': chart_path, 'used_gs': used_gs}

# ══════════════════════════════════════════════════════════════
# UI — SIDEBAR (PROFESSIONAL INDUSTRY-GRADE REDESIGN)
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    logo_b64 = get_base64_image(LOGO_PATH)
    st.markdown(f"""
        <div style='background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.6)); 
                    backdrop-filter: blur(16px);
                    padding: 18px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.06); 
                    margin-bottom: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
                    overflow: hidden; position: relative;'>
            <div style='position: absolute; top: 0; left: 0; right: 0; height: 2px;
                        background: linear-gradient(90deg, #0D9488, #38BDF8, #8B5CF6);'></div>
            <div style='display:flex; align-items:center; gap:14px; margin-top: 4px;'>
                <div style='width: 42px; height: 42px; border-radius: 10px; overflow: hidden;
                            background: linear-gradient(135deg, rgba(13, 148, 136, 0.12), rgba(56, 189, 248, 0.08));
                            border: 1px solid rgba(45, 212, 191, 0.12); display: flex; align-items: center; justify-content: center;
                            flex-shrink: 0;'>
                    <img src='data:image/png;base64,{logo_b64}' style='height:30px; width:30px; object-fit:contain;'>
                </div>
                <div>
                    <h3 style='margin:0; color:#F1F5F9; font-size:18px; font-weight:900; letter-spacing:1px;
                               font-family: 'Inter', system-ui, sans-serif;'>GEOSTRA</h3>
                    <p style='margin:0; color:#64748B; font-size:10px; font-weight:500; letter-spacing: 0.3px;'>Geospasial Sistem Tata Ruang & Area</p>
                </div>
            </div>
            <hr style='border:0; border-top:1px solid rgba(255,255,255,0.06); margin: 12px 0 8px 0;'>
            <div style='display:flex; justify-content:space-between; align-items:center; font-size:10px; color:#64748B;'>
                <span>Model: <b style='color:#CBD5E1;'>YOLOv8x-OBB</b></span>
                <span>Engine: <b style='color:#7DD3FC;'>PyTorch</b></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. DATA INPUT & GEOTIFF UPLOADER
    with st.expander('1. Upload Citra GeoTIFF', expanded=True):
        uploaded_files = st.file_uploader(
            'Upload hingga 5 file GeoTIFF',
            type=['tif', 'tiff'],
            accept_multiple_files=True,
            help='Gunakan GeoTIFF bertanda CRS WGS84 (EPSG:4326). Skala rekomen 1:2000.'
        )
        if uploaded_files:
            if len(uploaded_files) > 5:
                st.error('Maksimal 5 file GeoTIFF sekaligus!')
                uploaded_files = uploaded_files[:5]
            
            st.markdown("""<p style='font-size:11px; color:#94a3b8; margin-bottom:4px;'><b>File Siap Diproses:</b></p>""", unsafe_allow_html=True)
            for uf in uploaded_files:
                fmb = len(uf.getvalue()) / (1024 * 1024)
                st.caption(f'<b>{uf.name}</b> ({round(fmb,1)} MB)', unsafe_allow_html=True)

    # 3. AI & SPATIAL PARAMETER CONFIGURATION
    with st.expander('2. Parameter AI & Grid', expanded=True):
        conf = st.slider('Confidence Threshold', 0.1, 0.9, 0.4, 0.05,
                         help='Batas sensitivitas inferensi YOLOv8. Nilai 0.40 adalah batas optimal.')
        
        gs_mode = st.radio('Resolusi Grid Kepadatan', ['Auto (Rasional)', 'Manual'], index=0,
                           help='Auto secara otomatis menghitung ukuran grid berdasarkan estimasi densitas.')
        if gs_mode == 'Manual':
            manual_gs = st.slider('Ukuran Grid (derajat)', 0.001, 0.02, 0.001, 0.001,
                                   help='0.001° setara ± 111 meter di khatulistiwa.')
        else:
            manual_gs = 0.001
        tsz = 512

    st.markdown("""<div style='margin-top: 10px;'></div>""", unsafe_allow_html=True)
    
    # 4. PRIMARY RUN ACTION BUTTON
    btn = st.button(
        'Mulai Batch Deteksi AI',
        type='primary',
        disabled=(not uploaded_files or st.session_state['batch_running'] or len(uploaded_files) > 5),
        width='stretch'
    )

    # 5. REPOSITORY MANAGER & AREA LIST
    if st.session_state['all_stats']:
        st.divider()
        st.markdown("""<h4 style='font-size:13px; font-weight:700; color:#f8fafc; margin-bottom:8px;'>📂 Repositori Hasil Scan</h4>""", unsafe_allow_html=True)
        
        for name, s in list(st.session_state['all_stats'].items()):
            # Fetch color for area badge
            c_idx = s.get('color_idx', 0)
            c_hex = AREA_COLORS[c_idx % len(AREA_COLORS)]['building']
            
            c_card, c_del = st.columns([3.2, 0.8])
            with c_card:
                st.markdown(f"""
                    <div style='background: rgba(30, 41, 59, 0.7); padding: 6px 10px; border-radius: 6px; 
                                border-left: 4px solid {c_hex}; font-size: 11px; margin-bottom: 4px;'>
                        <b style='color:#f8fafc;'>{name}</b><br/>
                        <span style='color:#94a3b8;'>{S(s, 'n_bgn')} bgn | {S(s, 'aoi_km2')} km²</span>
                    </div>
                """, unsafe_allow_html=True)
            with c_del:
                if st.button('🗑️', key=f'del_{name}', help=f'Hapus area {name}'):
                    clear_area(name)
                    st.rerun()

        st.markdown("""<div style='margin-top:6px;'></div>""", unsafe_allow_html=True)
        with st.expander('Pemeliharaan Workspace'):
            if st.button('Hapus Semua Hasil Scan', width='stretch', type='secondary'):
                clear_all_areas()
                st.rerun()

    # 6. SYSTEM INFO FOOTER
    st.markdown("""
        <div style='margin-top: 25px; padding: 10px; border-radius: 8px; 
                    background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05); 
                    font-size: 10px; color: #64748b; text-align: center;'>
            <b>Environment Local:</b> Python 3.14 (smt6)<br/>
            <b>Drive Sync:</b> Active | SIG Project
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# UI — TITLE HEADER (GEOSTRA ENTERPRISE BANNER)
# ══════════════════════════════════════════════════════════════
logo_header_b64 = get_base64_image(LOGO_PATH)
tz_now = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%d %b %Y, %H:%M WIB')
st.markdown(f"""
    <div class='geostra-fade-in' style='
        background: linear-gradient(135deg, rgba(11, 17, 32, 0.95) 0%, rgba(15, 23, 42, 0.9) 40%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 0;
        margin-bottom: 8px;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.04);
        overflow: hidden;
        position: relative;'>
        <div style='height: 3px; background: linear-gradient(90deg, #0D9488, #38BDF8, #8B5CF6, #F59E0B, #0D9488);
                    background-size: 300% 100%; animation: gradientShift 6s ease infinite;'></div>
        <div style='padding: 22px 28px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;'>
            <div style='display: flex; align-items: center; gap: 20px;'>
                <div style='width: 56px; height: 56px; border-radius: 14px; overflow: hidden;
                            background: linear-gradient(135deg, rgba(13, 148, 136, 0.15), rgba(56, 189, 248, 0.1));
                            border: 1px solid rgba(45, 212, 191, 0.15); display: flex; align-items: center; justify-content: center;
                            box-shadow: 0 4px 16px rgba(13, 148, 136, 0.15);'>
                    <img src='data:image/png;base64,{logo_header_b64}' style='height: 40px; width: 40px; object-fit: contain;'>
                </div>
                <div>
                    <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 4px;'>
                        <h1 style='margin: 0; color: #F1F5F9; font-size: 26px; font-weight: 900; letter-spacing: 1.5px; line-height: 1;
                                   font-family: 'Inter', system-ui, sans-serif;'>GEOSTRA</h1>
                        <span class='geostra-pill geostra-pill-teal'>v3.0 PRO</span>
                    </div>
                    <p style='margin: 0; color: #64748B; font-size: 13px; font-weight: 500; letter-spacing: 0.2px;'>
                        Geospasial Sistem Tata Ruang dan Area &mdash; Platform Inferensi YOLOv8 &amp; Analisis Kepadatan Spasial
                    </p>
                </div>
            </div>
            <div style='display: flex; gap: 8px; flex-wrap: wrap; align-items: center;'>
                <span class='geostra-pill geostra-pill-teal'>Multi-GeoTIFF Batch</span>
                <span class='geostra-pill geostra-pill-sky'>EPSG:4326 GIS Engine</span>
                <span class='geostra-pill geostra-pill-violet'>PyTorch Pipeline</span>
                <span style='color: #475569; font-size: 10px; margin-left: 8px;'>{tz_now}</span>
            </div>
        </div>
    </div>
    <div class='geostra-accent-bar'></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# BATCH RUNNER
# ══════════════════════════════════════════════════════════════
if btn and uploaded_files:
    st.session_state['batch_running'] = True
    n_files = len(uploaded_files)

    st.subheader(f'🔄 Batch Processing — {n_files} file')
    total_pb = st.progress(0)

    # Assign color_idx before processing — use current count of processed areas
    # so each area always gets the same color slot regardless of reload order
    for file_idx, uf in enumerate(uploaded_files):
        area_name = os.path.splitext(uf.name)[0].replace(' ', '_').lower()

        if area_name in st.session_state['all_results']:
            st.info(f'⏭️ {area_name} sudah diproses sebelumnya — skip.')
            total_pb.progress(int((file_idx + 1) / n_files * 100))
            continue

        if area_name in st.session_state['all_stats']:
            st.info(f'⏭️ {area_name} sudah ada di Drive — skip.')
            total_pb.progress(int((file_idx + 1) / n_files * 100))
            continue

        path = os.path.join(TEMP_UPLOADS, uf.name)
        with open(path, 'wb') as out_f:
            out_f.write(uf.getvalue())

        # Assign color based on how many areas have been finalized so far
        assigned_color_idx = len(st.session_state['all_stats']) % len(AREA_COLORS)

        container = st.container()
        gs_m = 'Auto' if 'Auto' in gs_mode else 'Manual'
        result = process_area(area_name, path, conf, tsz, gs_m, manual_gs, container, color_idx=assigned_color_idx)

        if result:
            st.session_state['all_results'][area_name] = result
            st.session_state['all_stats'][area_name] = result['stats']

        total_pb.progress(int((file_idx + 1) / n_files * 100))

    st.session_state['batch_running'] = False
    st.success(f'Batch selesai! {len(st.session_state["all_results"])} area berhasil diproses.')
    st.balloons()

# ══════════════════════════════════════════════════════════════
# UI — RESULT TABS
# ══════════════════════════════════════════════════════════════
if st.session_state['all_stats']:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(['📊 Executive Dashboard', '🌍 Peta Interaktif Global', '⚖️ Analisis Komparatif', '🔍 Inspeksi Per Area', '📥 Data Center & Export'])

    with tab1:
        st.markdown("""
            <div class='geostra-section-title' style='margin-bottom: 20px;'>📊 Executive Status Board & Telemetri Batch</div>
        """, unsafe_allow_html=True)
        
        # 1. TOP METRICS CARDS ROW (5 COLUMNS)
        total_bgn = sum(S(s, 'n_bgn') for s in st.session_state['all_stats'].values())
        total_aoi = sum(S(s, 'aoi_km2') for s in st.session_state['all_stats'].values())
        total_atap_ha = sum(S(s, 'luas_ha') for s in st.session_state['all_stats'].values())
        total_perm_ha = sum(S(s, 'luas_perm') for s in st.session_state['all_stats'].values())
        avg_conf = float(np.mean([S(s, 'conf_mean') for s in st.session_state['all_stats'].values()])) if st.session_state['all_stats'] else 0.0
        
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric('Total Bangunan', f'{total_bgn:,} unit', help='Total seluruh poligon bangunan terdeteksi dari semua citra.')
        m2.metric('Total AOI', f'{round(total_aoi, 2)} km²', help='Total luas area pengamatan (Area of Interest).')
        m3.metric('Tutupan Atap', f'{round(total_atap_ha, 2)} ha', help='Total luas tutupan atap fisik (Building Coverage).')
        m4.metric('Permukiman', f'{round(total_perm_ha, 2)} ha', help='Total luas area yang diklasifikasikan sebagai kawasan permukiman.')
        m5.metric('Conf AI Rata', f'{round(avg_conf, 2)}', help='Rata-rata tingkat keyakinan (Confidence Score) YOLOv8.')

        st.divider()

        # 2. TABEL MATRIX LENGKAP WITH SEARCH & DOWNLOAD
        st.markdown("""<div class='geostra-section-title'>📈 Matriks Status Telemetri Spasial</div>""", unsafe_allow_html=True)
        
        rows = []
        for name, s in st.session_state['all_stats'].items():
            c_idx = s.get('color_idx', 0)
            c_hex = AREA_COLORS[c_idx % len(AREA_COLORS)]['building']
            rows.append({
                'Area': name,
                'Status': 'Processed',
                'Warna Indikator': f"● ({c_hex})",
                'Total Bangunan': S(s, 'n_bgn'),
                'Luas AOI (km²)': S(s, 'aoi_km2'),
                'Kepadatan (bgn/km²)': S(s, 'kd'),
                '% Terbangun (BCR)': S(s, 'ptb'),
                'Luas Atap (ha)': S(s, 'luas_ha'),
                'Rata Luas (m²)': S(s, 'rata'),
                'Median Luas (m²)': S(s, 'median'),
                'Cluster Permukiman': S(s, 'n_perm'),
                'Luas Permukiman (ha)': S(s, 'luas_perm'),
                'YOLOv8 Conf Mean': S(s, 'conf_mean'),
                'Tipologi Kepadatan': S(s, 'kepadatan_cat', 'Normal'),
                'Waktu Proses (s)': S(s, 'processing_time_s', 0)
            })
        
        df_status = pd.DataFrame(rows)
        st.dataframe(df_status, width='stretch', hide_index=True)

        col_csv, col_space = st.columns([1.5, 2.5])
        with col_csv:
            csv_data = df_status.to_csv(index=False).encode('utf-8')
            st.download_button(
                'Export Matriks Telemetri (CSV)',
                data=csv_data,
                file_name=f'telemetri_status_batch_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
                width='stretch'
            )

        st.divider()

        # 3. MACRO SUMMARY CHARTS ROW (INTERACTIVE ANIMATED PLOTLY)
        st.markdown("""<div class='geostra-section-title' style='margin-bottom:12px;'>📊 Analisis Visual Makro Antar-Area (Interactive Plotly Studio)</div>""", unsafe_allow_html=True)
        fig_macro = make_status_board_charts(st.session_state['all_stats'])
        if fig_macro:
            st.plotly_chart(fig_macro, width='stretch', config={'displayModeBar': False})

        # 4. SYSTEM HEALTH & AUDIT CARD
        st.divider()
        st.markdown(f"""
            <div style='background: rgba(15, 23, 42, 0.7); padding: 14px 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); font-size: 12px; color: #cbd5e1;'>
                <b style='color:#f8fafc;'>Catatan Audit Kualitas Telemetri Spasial:</b>
                <ul style='margin: 6px 0 0 18px; padding: 0; line-height:1.7;'>
                    <li>Semua data spasial tersinkronisasi otomatis dengan checkpoint Google Drive di <code>SIG_Deteksi_Bangunan/batch_results</code>.</li>
                    <li>Evaluasi <i>Confidence Mean</i> (Rata-rata <b>{avg_conf:.2f}</b>) menunjukkan inferensi model YOLOv8x-OBB berjalan stabil di atas ambang batas 0.40.</li>
                    <li>Warna indikator tiap area terkunci secara deterministik untuk menjaga konsistensi komparasi spasial antar-tab.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""<div class='geostra-section-title' style='font-size: 18px; margin-bottom:12px;'>🗺️ Peta Gabungan & Konsolidasi Spasial Multi-Sample</div>""", unsafe_allow_html=True)
        st.caption('Eksplorasi spasial terpadu seluruh area pengamatan dengan layer overlay interaktif dan penyesuaian fokal wilayah.')

        for a_name in st.session_state['all_stats']:
            load_area_results(a_name)

        if st.session_state['all_results']:
            # 1. TOP METRIC BADGES
            t_bgn = sum(S(s, 'n_bgn') for s in st.session_state['all_stats'].values())
            t_aoi = sum(S(s, 'aoi_km2') for s in st.session_state['all_stats'].values())
            t_perm = sum(S(s, 'luas_perm') for s in st.session_state['all_stats'].values())
            n_areas = len(st.session_state['all_results'])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric('Total Bangunan', f'{t_bgn:,} unit', help='Akumulasi total bangunan dari seluruh area yang di-scan.')
            c2.metric('Area Terkonsolidasi', f'{n_areas} Wilayah', help='Jumlah area GeoTIFF yang dipetakan secara gabungan.')
            c3.metric('Cakupan Total AOI', f'{round(t_aoi, 2)} km²', help='Total area of interest.')
            c4.metric('Luas Permukiman', f'{round(t_perm, 2)} ha', help='Total wilayah terklasifikasi sebagai klaster permukiman.')

            st.divider()

            # 2. QUICK FOCUS SPATIAL TOOLBAR
            col_sel, col_info = st.columns([1.5, 2.5])
            with col_sel:
                focus_opt = st.selectbox(
                    'Fokus Tampilan Kamera Peta:',
                    ['🌐 Tampilkan Semua Area'] + list(st.session_state['all_results'].keys()),
                    key='map_merged_focus'
                )
            with col_info:
                pill_html = "<div style='display:flex; flex-wrap:wrap; gap:8px; margin-top:24px;'>"
                for area_k, res_v in st.session_state['all_results'].items():
                    c_idx = res_v.get('color_idx', 0)
                    c_hex = AREA_COLORS[c_idx % len(AREA_COLORS)]['building']
                    n_unit = len(res_v['gdf'])
                    pill_html += f"<span style='background:rgba(30,41,59,0.8); border:1px solid rgba(255,255,255,0.15); border-left:4px solid {c_hex}; padding:4px 10px; border-radius:6px; font-size:11px; color:#f8fafc;'>● <b>{area_k}</b> ({n_unit:,} bgn)</span>"
                pill_html += "</div>"
                st.markdown(pill_html, unsafe_allow_html=True)

            st.markdown("""<div style='margin-top:10px;'></div>""", unsafe_allow_html=True)

            # 3. INTERACTIVE FOLIUM MAP
            sel_area_name = None if 'Semua' in focus_opt else focus_opt
            import streamlit.components.v1 as components
            with st.spinner('Memuat & Merender Studio Peta Gabungan Interaktif... 🗺️'):
                merged_html = make_merged_map(st.session_state['all_results'], focus_area=sel_area_name)
                components.html(merged_html, height=680, scrolling=False)

            # 4. BOTTOM AREA CARDS GRID
            st.divider()
            st.markdown("""<div class='geostra-section-title' style='margin-bottom:14px;'>📋 Card Ringkasan Karakteristik Per Area</div>""", unsafe_allow_html=True)
            
            grid_cols = st.columns(min(len(st.session_state['all_stats']), 5))
            for i, (aname, stats_v) in enumerate(list(st.session_state['all_stats'].items())[:5]):
                c_idx = stats_v.get('color_idx', i)
                c_hex = AREA_COLORS[c_idx % len(AREA_COLORS)]['building']
                with grid_cols[i]:
                    card_html = (
                        f"<div style='background:rgba(15,23,42,0.8); padding:12px; border-radius:10px; "
                        f"border:1px solid rgba(255,255,255,0.1); border-top:4px solid {c_hex};'>"
                        f"<h5 style='margin:0 0 6px 0; color:#f8fafc; font-size:13px; font-weight:700;'>{aname}</h5>"
                        f"<div style='font-size:11px; color:#cbd5e1; line-height:1.6;'>"
                        f"<div><b>{S(stats_v, 'n_bgn'):,}</b> bangunan</div>"
                        f"<div><b>{S(stats_v, 'kd')}</b> bgn/km²</div>"
                        f"<div><b>{S(stats_v, 'ptb')}%</b> terbangun</div>"
                        f"<div><b>{S(stats_v, 'luas_perm')}</b> ha permukiman</div>"
                        f"</div></div>"
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info('Belum ada data peta area. Upload GeoTIFF di sidebar!')

    with tab3:
        st.markdown("""<div class='geostra-section-title' style='font-size: 18px; margin-bottom:12px;'>📊 Dashboard Komparasi Multi-Dimensi Antar-Area</div>""", unsafe_allow_html=True)
        st.caption('Komparasi kuantitatif & perbandingan statistik atribut spasial antar wilayah studi (hingga 5 area sekaligus).')

        if len(st.session_state['all_stats']) >= 2:
            comp_png, rankings = make_comparison_charts(st.session_state['all_stats'])

            # 1. RANKING PODIUM CARDS
            if rankings:
                st.markdown("""<div class='geostra-section-title' style='margin-bottom:14px;'>🏆 Papan Peringkat & Juara Komparasi Spasial</div>""", unsafe_allow_html=True)
                cols = st.columns(len(rankings))
                for i, (label, winner) in enumerate(rankings.items()):
                    w_s = st.session_state['all_stats'].get(winner, {})
                    w_cidx = w_s.get('color_idx', 0)
                    w_chex = AREA_COLORS[w_cidx % len(AREA_COLORS)]['building']
                    with cols[i]:
                        card_rank_html = (
                            f"<div style='background:rgba(15,23,42,0.8); padding:12px; border-radius:10px; "
                            f"border:1px solid rgba(255,255,255,0.1); border-left:4px solid {w_chex};'>"
                            f"<span style='font-size:11px; color:#94a3b8; font-weight:600;'>{label}</span><br/>"
                            f"<h4 style='margin:4px 0 0 0; color:#f8fafc; font-size:15px; font-weight:700;'>👑 {winner}</h4>"
                            f"</div>"
                        )
                        st.markdown(card_rank_html, unsafe_allow_html=True)

            st.divider()

            # 2. COMPARATIVE MATRIX TABLE
            st.markdown("""<div class='geostra-section-title' style='margin-bottom:12px;'>⚖️ Matriks Perbandingan Kuantitatif Antar-Wilayah</div>""", unsafe_allow_html=True)
            df_comp = pd.DataFrame([{
                'Area': k,
                'Bangunan (unit)': S(v, 'n_bgn'),
                'Luas AOI (km²)': S(v, 'aoi_km2'),
                'Kepadatan (bgn/km²)': S(v, 'kd'),
                '% Lahan Terbangun': S(v, 'ptb'),
                'Rata Luas (m²)': S(v, 'rata'),
                'Median Luas (m²)': S(v, 'median'),
                'Luas Permukiman (ha)': S(v, 'luas_perm'),
                'Jumlah Cluster': S(v, 'n_perm'),
                'YOLOv8 Conf': S(v, 'conf_mean')
            } for k, v in list(st.session_state['all_stats'].items())[:5]])
            st.dataframe(df_comp.set_index('Area'), width='stretch')

            st.divider()

            # 3. 4-PANEL COMPARISON GRAPHIC
            st.markdown("""<div class='geostra-section-title' style='margin-bottom:12px;'>📈 Grafik Komparasi Spasial 4-Panel Multidimensi</div>""", unsafe_allow_html=True)
            if comp_png and os.path.exists(comp_png):
                st.image(comp_png, width='stretch')
                
                # NARRATIVE AUTO-GENERATE
                st.markdown("""<div class='geostra-section-title' style='margin-top:24px; margin-bottom:14px;'>🤖 Interpretasi Narasi Otomatis</div>""", unsafe_allow_html=True)
                narasi = (
                    f"Berdasarkan analisis komparatif antar-area di atas, wilayah **{rankings['Bangunan Terbanyak']}** memimpin dengan jumlah bangunan terbanyak, "
                    f"sementara wilayah **{rankings['Terpadat']}** tercatat sebagai kawasan dengan tingkat kepadatan spasial paling tinggi. "
                    f"Dari segi cakupan permukiman komunal, **{rankings['Permukiman Terluas']}** memiliki area permukiman terluas dibandingkan wilayah lainnya. "
                    f"Adapun model AI YOLOv8 mencatat tingkat keyakinan (confidence score) terbaik pada citra wilayah **{rankings['Conf Tertinggi']}**, "
                    f"yang mengindikasikan kualitas resolusi citra dan kejelasan objek pada area tersebut sangat optimal."
                )
                st.info(narasi)
        else:
            st.info('Minimal dibutuhkan 2 area yang telah discan untuk melakukan komparasi multi-dimensi. Silakan upload file GeoTIFF tambahan di sidebar!')

    with tab4:
        st.markdown("""<div class='geostra-section-title' style='font-size: 18px; margin-bottom:12px;'>🔍 Studio Analisis Spasial Detail Per-Area</div>""", unsafe_allow_html=True)
        st.caption('Inspeksi mendalam atribut spasial, visualisasi peta 1-to-1, grafik distribusi, dan audit telemetri polygon bangunan.')

        if st.session_state['all_stats']:
            col_sel_area, col_badge = st.columns([1.5, 2.5])
            with col_sel_area:
                area_sel = st.selectbox('Pilih Target Wilayah Pengamatan:', list(st.session_state['all_stats'].keys()), key='sel_tab4_area')
            
            s = st.session_state['all_stats'][area_sel]
            res_area = load_area_results(area_sel)
            
            c_idx = s.get('color_idx', 0)
            c_hex = AREA_COLORS[c_idx % len(AREA_COLORS)]['building']

            with col_badge:
                badge_html = (
                    f"<div style='display:flex; align-items:center; gap:12px; margin-top:24px; "
                    f"background:rgba(30,41,59,0.8); padding:8px 14px; border-radius:8px; border:1px solid rgba(255,255,255,0.15); border-left:5px solid {c_hex};'>"
                    f"<div>"
                    f"<span style='font-size:12px; color:#f8fafc; font-weight:700;'>● Target Wilayah: {area_sel}</span>"
                    f"<span style='font-size:11px; color:#94a3b8; margin-left:10px;'>Warna Indikator Spasial: <b style='color:{c_hex};'>{c_hex}</b></span>"
                    f"</div></div>"
                )
                st.markdown(badge_html, unsafe_allow_html=True)

            st.divider()

            # 1. EXECUTIVE 8-METRIC GRID (COMPACT STYLING)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric('Total Bangunan', f"{S(s, 'n_bgn'):,} unit", help='Jumlah total unit bangunan.')
            m2.metric('Luas AOI Wilayah', f"{S(s, 'aoi_km2')} km²", help='Luas Area of Interest.')
            m3.metric('Rasio Terbangun (BCR)', f"{S(s, 'ptb')}%", help='Persentase Building Coverage Ratio.')
            m4.metric('Kepadatan Spasial', f"{S(s, 'kd')} bgn/km²", help='Rasio jumlah bangunan per km persegi.')

            m5, m6, m7, m8 = st.columns(4)
            m5.metric('Akurasi AI (Mean Conf)', f"{S(s, 'conf_mean')}", help='Rata-rata akurasi prediksi YOLO.')
            m6.metric('Luas Atap Total', f"{S(s, 'luas_ha')} ha", help='Luas keseluruhan atap bangunan.')
            m7.metric('Rata / Median Luas', f"{S(s, 'rata')} / {S(s, 'median')} m²", help='Distribusi ukuran rata-rata dan nilai tengah.')
            m8.metric('Permukiman', f"{S(s, 'n_perm')} cluster ({S(s, 'luas_perm')} ha)", help='Jumlah klaster dan luas permukiman.')

            st.divider()

            # 2. SUB-TABS: PETA, GRAFIK, & TABEL TELEMETRI POLYGON
            subtab1, subtab2, subtab3 = st.tabs(['Peta Interactive GIS', 'Studio Grafik Analisis', 'Tabel Telemetri & Export Data'])

            with subtab1:
                st.markdown(f"<div class='geostra-section-title' style='margin-bottom:12px;'>Peta Tematik Vector & Raster (Leaflet Studio) area_sel</div>", unsafe_allow_html=True)
                if res_area:
                    import streamlit.components.v1 as components
                    with st.spinner(f'Merender Visualisasi Peta Analisis untuk {area_sel}... 🗺️'):
                        map_html = make_map_area(res_area['gdf'], res_area['grid'], res_area['perm'], area_sel)
                        components.html(map_html, height=650, scrolling=False)
                else:
                    st.info('Gagal memuat data peta dari disk.')

            with subtab2:
                st.markdown(f"<div class='geostra-section-title' style='margin-bottom:12px;'>Grafik Distribusi Spasial & Histogram Bangunan area_sel</div>", unsafe_allow_html=True)
                chart_path = res_area.get('chart') if res_area else None
                if not chart_path or not os.path.exists(chart_path):
                    chart_drive = os.path.join(DRIVE_BATCH, area_sel, 'statistik.png')
                    if os.path.exists(chart_drive):
                        chart_path = chart_drive
                    elif res_area and len(res_area.get('gdf', [])):
                        cp = make_chart_area(res_area['gdf'], res_area['grid'], res_area['stats'], area_sel)
                        if cp and os.path.exists(cp):
                            shutil.copy(cp, chart_drive)
                            chart_path = chart_drive
                            if res_area: res_area['chart'] = chart_drive

                if chart_path and os.path.exists(chart_path):
                    st.image(chart_path, width='stretch')
                else:
                    st.info('Belum ada data untuk dirender menjadi grafik.')

            with subtab3:
                st.markdown(f"<div class='geostra-section-title' style='margin-bottom:12px;'>Tabel Telemetri Polygon & Quick Export area_sel</div>", unsafe_allow_html=True)
                if res_area and len(res_area['gdf']):
                    gdf_sel = res_area['gdf']
                    areas_m2 = gdf_sel.to_crs('EPSG:32748').geometry.area
                    df_view = pd.DataFrame({
                        'ID Bangunan': range(1, len(gdf_sel) + 1),
                        'Confidence Score': gdf_sel['confidence'].round(3),
                        'Luas Atap (m²)': areas_m2.round(2),
                        'Latitude (Center)': gdf_sel['lat'].round(6),
                        'Longitude (Center)': gdf_sel['lon'].round(6)
                    })
                    st.dataframe(df_view, width='stretch', hide_index=True, height=350)

                    # Quick Export Bar
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        geojson_str = res_area['gdf'].to_json()
                        st.download_button(
                            f"Export GeoJSON Vector ({area_sel})",
                            data=geojson_str,
                            file_name=f"bangunan_{area_sel}.geojson",
                            mime="application/geo+json",
                            width='stretch'
                        )
                    with col_exp2:
                        csv_str = df_view.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            f"Export CSV Telemetri ({area_sel})",
                            data=csv_str,
                            file_name=f"telemetri_{area_sel}.csv",
                            mime="text/csv",
                            width='stretch'
                        )
        else:
            st.info('Belum ada area yang di-scan. Upload file GeoTIFF di sidebar!')

    with tab5:
        st.markdown("""<div class='geostra-section-title' style='font-size: 18px; margin-bottom:12px;'>💾 Pusat Unduhan & Export Hub Spasial Terpadu</div>""", unsafe_allow_html=True)
        st.caption('Akses eksekutif untuk mengunduh Laporan PDF ReportLab, Data Vektor GeoJSON (QGIS Ready), dan Telemetri Matriks CSV.')

        if st.session_state['all_stats']:
            # 1. EXECUTIVE STATUS BADGES
            c1, c2, c3, c4 = st.columns(4)
            c1.metric('Format Laporan', 'ReportLab PDF A4')
            c2.metric('Vektor GIS', 'GeoJSON EPSG:4326')
            c3.metric('Telemetri Data', 'CSV / Tabular Data')
            c4.metric('☁️ Synchronized', 'Google Drive Checkpoint')

            st.divider()

            # 2. TWO MAIN HUBS (2 COLUMNS)
            col_hub_left, col_hub_right = st.columns(2)

            with col_hub_left:
                st.markdown("""<div class='geostra-section-title' style='margin-bottom:14px;'>📄 Laporan PDF Eksekutif ReportLab</div>""", unsafe_allow_html=True)
                
                # Card A1: Laporan Batch (Gabungan)
                card_a1_html = (
                    "<div style='background:rgba(15,23,42,0.8); padding:14px; border-radius:10px; border:1px solid rgba(255,255,255,0.12); margin-bottom:14px;'>"
                    "<h5 style='margin:0 0 6px 0; color:#f8fafc; font-size:13px; font-weight:700;'>Laporan Gabungan Multi-Area (Batch Report)</h5>"
                    "<p style='margin:0; color:#cbd5e1; font-size:11px; line-height:1.5;'>"
                    "Mencakup Cover Page Eksekutif, Matriks Komparasi, Grafik 4-Panel, dan Narasi Analisis Detail untuk seluruh wilayah pengamatan."
                    "</p></div>"
                )
                st.markdown(card_a1_html, unsafe_allow_html=True)
                
                if st.button('Generate PDF Gabungan (Semua Area)', type='primary', width='stretch'):
                    with st.spinner('Menghasilkan laporan PDF gabungan...'):
                        chart_paths = {}
                        for name in st.session_state['all_stats']:
                            cp = os.path.join(DRIVE_BATCH, name, 'statistik.png')
                            if os.path.exists(cp): chart_paths[name] = cp
                        comp_cp = os.path.join(TEMP, 'output', 'komparasi.png')
                        if not os.path.exists(comp_cp) and len(st.session_state['all_stats']) >= 2:
                            make_comparison_charts(st.session_state['all_stats'])
                        pdf_path = generate_pdf(st.session_state['all_stats'], chart_paths, comp_cp if os.path.exists(comp_cp) else None)
                        if os.path.exists(pdf_path):
                            st.session_state['pdf_batch_ready'] = pdf_path

                if 'pdf_batch_ready' in st.session_state and os.path.exists(st.session_state['pdf_batch_ready']):
                    with open(st.session_state['pdf_batch_ready'], 'rb') as f:
                        pdf_data_b = f.read()
                    st.download_button('Download PDF Gabungan (Batch)', pdf_data_b,
                                       file_name='Laporan_Gabungan_Komparasi_YOLOv8.pdf', mime='application/pdf', width='stretch')

                st.markdown("""<div style='margin-top:16px;'></div>""", unsafe_allow_html=True)

                # Card A2: Laporan Single Area
                card_a2_html = (
                    """<div style='background:rgba(15,23,42,0.8); padding:14px; border-radius:10px; border:1px solid rgba(255,255,255,0.12); margin-bottom:10px;'>"""
                    """<h5 style='margin:0 0 6px 0; color:#f8fafc; font-size:13px; font-weight:700;'>Laporan Spesifik Per-Wilayah (Single Report)</h5>"""
                    """<p style='margin:0; color:#cbd5e1; font-size:11px; line-height:1.5;'>"""
                    """Membuat dokumen PDF A4 profesional khusus untuk 1 wilayah GeoTIFF target pengamatan."""
                    """</p></div>"""
                )
                st.markdown(card_a2_html, unsafe_allow_html=True)

                sel_pdf_area = st.selectbox('Pilih Target Wilayah PDF:', list(st.session_state['all_stats'].keys()), key='sel_pdf_single')
                if st.button(f'Generate PDF Khusus ({sel_pdf_area})', width='stretch'):
                    with st.spinner(f'Menghasilkan laporan PDF khusus {sel_pdf_area}...'):
                        single_stats = st.session_state['all_stats'][sel_pdf_area]
                        cp_path = os.path.join(DRIVE_BATCH, sel_pdf_area, 'statistik.png')
                        pdf_path = generate_single_pdf(sel_pdf_area, single_stats, cp_path if os.path.exists(cp_path) else None)
                        if os.path.exists(pdf_path):
                            st.session_state['pdf_single_ready'] = (sel_pdf_area, pdf_path)

                if 'pdf_single_ready' in st.session_state and os.path.exists(st.session_state['pdf_single_ready'][1]):
                    area_name_pdf, single_pdf_path = st.session_state['pdf_single_ready']
                    with open(single_pdf_path, 'rb') as f:
                        pdf_data_s = f.read()
                    st.download_button(f'Download PDF ({area_name_pdf})', pdf_data_s,
                                       file_name=f'Laporan_Spasial_{area_name_pdf}_YOLOv8.pdf', mime='application/pdf', width='stretch')

            with col_hub_right:
                st.markdown("""<div class='geostra-section-title' style='margin-bottom:14px;'>🗺️ Export Vektor GeoJSON & Datasets GIS</div>""", unsafe_allow_html=True)

                info_qgis_html = (
                    "<div style='background:rgba(15,23,42,0.8); padding:10px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.12); margin-bottom:12px;'>"
                    "<span style='font-size:11px; color:#cbd5e1;'><b>GeoJSON Standard Format (EPSG:4326)</b> dapat langsung di-drag & drop ke dalam QGIS, ArcGIS, atau Leaflet Web GIS.</span>"
                    "</div>"
                )
                st.markdown(info_qgis_html, unsafe_allow_html=True)

                # 🌐 MERGED GEOJSON CONSOLIDATED (ALL AREAS)
                st.markdown("""<div class='geostra-section-title' style='font-size:13px; margin-bottom:10px;'>🌐 GeoJSON Gabungan Konsolidasi (Semua Area)</div>""", unsafe_allow_html=True)
                
                # Make sure all results are loaded into session_state['all_results']
                for a_k in st.session_state['all_stats']:
                    load_area_results(a_k)

                if st.session_state['all_results']:
                    merged_bgns = []
                    merged_perms = []
                    for a_k, res_v in st.session_state['all_results'].items():
                        if len(res_v.get('gdf', [])):
                            g_bgn = res_v['gdf'].copy()
                            g_bgn['area_name'] = a_k
                            merged_bgns.append(g_bgn)
                        if len(res_v.get('perm', [])):
                            g_perm = res_v['perm'].copy()
                            g_perm['area_name'] = a_k
                            merged_perms.append(g_perm)

                    if merged_bgns:
                        gdf_merged_bgn = gpd.GeoDataFrame(pd.concat(merged_bgns, ignore_index=True), crs='EPSG:4326')
                        st.download_button(
                            '🌐 Download GeoJSON Bangunan Gabungan (Semua Area)',
                            data=gdf_merged_bgn.to_json(),
                            file_name=f'bangunan_gabungan_{len(st.session_state["all_results"])}_area.geojson',
                            mime='application/geo+json',
                            help='Poligon bangunan terkonsolidasi dari seluruh area pengamatan (termasuk atribut area_name)',
                            width='stretch',
                            type='primary'
                        )
                    
                    if merged_perms:
                        gdf_merged_perm = gpd.GeoDataFrame(pd.concat(merged_perms, ignore_index=True), crs='EPSG:4326')
                        st.download_button(
                            '🌐 Download GeoJSON Permukiman Gabungan (Semua Area)',
                            data=gdf_merged_perm.to_json(),
                            file_name=f'permukiman_gabungan_{len(st.session_state["all_results"])}_area.geojson',
                            mime='application/geo+json',
                            help='Zona permukiman terkonsolidasi dari seluruh area pengamatan (termasuk atribut area_name)',
                            width='stretch'
                        )

                st.divider()

                # SPECIFIC PER AREA GEOJSON
                st.markdown("""<div class='geostra-section-title' style='font-size:13px; margin-bottom:10px;'>📍 GeoJSON Spesifik Per-Wilayah</div>""", unsafe_allow_html=True)
                dl_area = st.selectbox('Pilih Target Wilayah Export GIS:', list(st.session_state['all_stats'].keys()), key='dl_sel_hub')
                dl_dir = os.path.join(DRIVE_BATCH, dl_area)

                for fn, label_name, desc in [
                    ('hasil_deteksi_bangunan.geojson', 'Polygon Bangunan YOLOv8', 'Polygon presisi per unit bangunan (WGS84)'),
                    ('area_permukiman.geojson', 'Klaster Zona Permukiman', 'Batas wilayah permukiman terkelompok'),
                    ('grid_kepadatan.geojson', 'Grid Analisis Kepadatan', 'Sel grid spasial pembagian unit'),
                    ('kepadatan_bertingkat.geojson', 'Grid 4 Kelas Kepadatan', 'Peta tematik 4 tingkat kepadatan'),
                ]:
                    fp = os.path.join(dl_dir, fn)
                    if os.path.exists(fp):
                        with open(fp, 'rb') as f:
                            fp_data = f.read()
                        st.download_button(
                            f'{label_name}',
                            fp_data,
                            file_name=f'{dl_area}_{fn}',
                            mime='application/geo+json',
                            help=desc,
                            width='stretch'
                        )
                
                st.divider()
                st.markdown("""<div class='geostra-section-title' style='font-size:13px; margin-bottom:10px;'>📊 Export Matriks Telemetri Batch (CSV)</div>""", unsafe_allow_html=True)
                df_exp = pd.DataFrame([{'Area': k, **v} for k, v in st.session_state['all_stats'].items()])
                csv = df_exp.to_csv(index=False).encode('utf-8')
                st.download_button('Download Tabel Metrik Batch (CSV)', csv, file_name='ringkasan_metrik_batch.csv',
                                   mime='text/csv', width='stretch')

            st.divider()
            
            # 3. AUDIT & QGIS HELP CARD
            st.markdown("""
                <div style="background: rgba(15, 23, 42, 0.7); padding: 14px 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); font-size: 12px; color: #cbd5e1;">
                    <b style="color:#f8fafc;">Panduan Integrasi QGIS & Pemakaian Laporan PDF:</b>
                    <ul style="margin: 6px 0 0 18px; padding: 0; line-height:1.7;">
                        <li>Semua file <b>.geojson</b> yang diunduh secara default menggunakan sistem koordinat WGS 84 (<code>EPSG:4326</code>).</li>
                        <li>File laporan PDF disusun menggunakan engine <b>ReportLab Platypus</b> dengan standar dokumen A4 siap cetak.</li>
                        <li>Untuk membuka layer GeoJSON di QGIS, cukup drag & drop file <code>.geojson</code> langsung ke canvas QGIS.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info('Belum ada data wilayah yang discan. Upload file GeoTIFF di sidebar!')
else:
    if not st.session_state['batch_running']:
        st.info('👈 Upload hingga 5 file GeoTIFF di sidebar kiri, lalu tekan **Mulai Batch Deteksi**.')
