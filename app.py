"""
AgroSense AI  —  app.py
Run:  streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="AgroSense AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.config   import SOIL_ZONES, CROP_NPK
from modules.weather  import get_weather_by_city, weather_risk_summary
from modules.market   import get_market_price, get_profit_estimate
from modules.disease  import analyse_leaf, heuristic_diagnosis
from modules.agronomy import (get_field_calendar, fertiliser_recommendation,
                               soil_health_score, irrigation_advice, MONTHS, ACTIVITY_COLORS)

# ── Permanent Light Mode Tokens ───────────────────────────────────────────────
T = dict(
    bg         = "#F6F8FA",
    surface    = "#FFFFFF",
    surface2   = "#F6F8FA",
    border     = "#D0D7DE",
    text       = "#1F2328",
    text2      = "#656D76",
    accent     = "#1A7F37",
    accent2    = "#2DA44E",
    blue       = "#0969DA",
    red        = "#CF222E",
    amber      = "#9A6700",
    sidebar_bg = "#FFFFFF",
    topbar_bg  = "#1F2328",
    topbar_txt = "#FFFFFF",
    chart_bg   = "#FFFFFF",
    chart_grid = "#F0F0F0",
    chart_txt  = "#656D76",
    input_bg   = "#FFFFFF",
)

# ── Helper for Plotly Transparencies ──────────────────────────────────────────
def hex_to_rgba(hex_color, opacity=1.0):
    """Converts a 6-char hex string to an rgba string for Plotly validation."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{opacity})"
    return hex_color

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background: {T['bg']};
    color: {T['text']};
}}

/* Fix Sidebar Toggle Bug while hiding annoying elements */
#MainMenu {{ display: none !important; }}
footer {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}
[data-testid="stHeader"] {{ background: transparent !important; }}

/* Main container */
.main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']} !important;
    border-right: 1px solid {T['border']};
}}
[data-testid="stSidebar"] * {{ color: {T['text']} !important; }}
[data-testid="stSidebar"] .stRadio label {{
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 6px 0 !important;
    color: {T['text2']} !important;
}}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {{
    color: {T['text']} !important;
}}

/* Page wrapper */
.ag-page {{ padding: 1.8rem 2.4rem 4rem; background: {T['bg']}; }}

/* Top bar */
.ag-topbar {{
    background: {T['topbar_bg']};
    padding: 0 2.4rem;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid {T['border']};
    position: sticky;
    top: 0;
    z-index: 99;
}}
.ag-logo {{
    font-size: 1.05rem;
    font-weight: 600;
    color: {T['topbar_txt']};
    letter-spacing: -0.01em;
}}
.ag-logo-dot {{ color: {T['accent']}; }}
.ag-tagline {{
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #484F58;
}}

/* Page header */
.ag-header {{
    padding-bottom: 1.1rem;
    margin-bottom: 1.6rem;
    border-bottom: 1px solid {T['border']};
}}
.ag-title {{
    font-size: 1.4rem;
    font-weight: 600;
    color: {T['text']};
    letter-spacing: -0.02em;
    margin: 0 0 3px;
    line-height: 1.3;
}}
.ag-sub {{
    font-size: 12px;
    color: {T['text2']};
    margin: 0;
}}

/* Cards */
.ag-card {{
    background: {T['surface']};
    border: 1px solid {T['border']};
    border-radius: 6px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 10px;
}}
.ag-card-green {{
    border-left: 3px solid {T['accent']};
}}

/* Label */
.ag-label {{
    display: block;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {T['text2']};
    margin: 1.2rem 0 0.5rem;
}}

/* Tags */
.ag-tag {{
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 12px;
}}
.ag-tag-green {{ background: #DAFBE1; color: {T['accent']}; }}
.ag-tag-red   {{ background: #FFEBE9; color: {T['red']}; }}
.ag-tag-amber {{ background: #FFF8C5; color: {T['amber']}; }}
.ag-tag-blue  {{ background: #DDF4FF; color: {T['blue']}; }}
.ag-tag-gray  {{ background: {T['surface2']}; color: {T['text2']}; }}

/* Stat row */
.ag-stat-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid {T['border']};
    font-size: 13px;
}}
.ag-stat-row:last-child {{ border-bottom: none; }}
.ag-stat-label {{ color: {T['text2']}; }}
.ag-stat-val   {{ font-family: 'DM Mono', monospace; font-weight: 500; color: {T['text']}; }}

/* Progress bar */
.ag-bar-wrap {{ margin-bottom: 12px; }}
.ag-bar-head {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    font-weight: 500;
    color: {T['text']};
    margin-bottom: 4px;
}}
.ag-bar-track {{
    background: {T['border']};
    border-radius: 2px;
    height: 6px;
    overflow: hidden;
}}
.ag-bar-fill {{ height: 6px; border-radius: 2px; }}

/* Weather card */
.ag-weather {{
    background: {T['surface2']};
    border: 1px solid {T['border']};
    border-radius: 6px;
    padding: 16px 20px;
    margin-bottom: 14px;
}}
.ag-weather-city {{ font-size: 11px; font-weight: 600;
    letter-spacing:.08em; text-transform:uppercase; color: {T['accent']}; }}
.ag-weather-temp {{ font-family:'DM Mono',monospace; font-size:2.2rem;
    font-weight:400; color:{T['text']}; line-height:1.1; }}
.ag-weather-desc {{ font-size:11px; color:{T['text2']}; text-transform:capitalize; }}
.ag-weather-grid {{ display:grid; grid-template-columns:repeat(3,1fr);
    gap:10px; margin-top:12px; padding-top:12px; border-top:1px solid {T['border']}; }}
.ag-wi-label {{ font-size:9px; font-weight:600; letter-spacing:.1em;
    text-transform:uppercase; color:{T['text2']}; }}
.ag-wi-val {{ font-family:'DM Mono',monospace; font-size:13px;
    font-weight:500; color:{T['text']}; }}

/* Risk pill */
.ag-risk {{
    padding: 8px 12px;
    border-radius: 5px;
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 6px;
    border: 1px solid transparent;
}}
.ag-risk-low  {{ background: #DAFBE1; color:{T['accent']}; border-color: #56D364; }}
.ag-risk-med  {{ background: #FFF8C5; color:{T['amber']};  border-color: #D4A72C; }}
.ag-risk-high {{ background: #FFEBE9; color:{T['red']};    border-color: #FF8182; }}

/* Calendar */
.ag-cal {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 6px;
    margin-top: 10px;
}}
.ag-cal-cell {{
    border-radius: 5px;
    padding: 10px 6px;
    text-align: center;
}}
.ag-cal-month {{ font-size: 10px; font-weight: 700;
    letter-spacing:.06em; text-transform:uppercase; }}
.ag-cal-act {{ font-size: 10px; margin-top: 3px; }}

/* Streamlit overrides */
.stButton > button {{
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    background: {T['accent2']} !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 5px !important;
    padding: .45rem 1.2rem !important;
}}
.stButton > button:hover {{ opacity: 0.88 !important; }}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {{
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    border: 1px solid {T['border']} !important;
    border-radius: 5px !important;
    background: {T['input_bg']} !important;
    color: {T['text']} !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px rgba(26,127,55,.1) !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {T['border']} !important;
    gap: 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
    color: {T['text2']} !important;
    background: transparent !important;
    border: none !important;
    padding: .7rem 1.2rem !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1px !important;
}}
.stTabs [aria-selected="true"] {{
    color: {T['text']} !important;
    border-bottom: 2px solid {T['accent']} !important;
}}

[data-testid="metric-container"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border']} !important;
    border-radius: 6px !important;
    padding: .9rem 1.1rem !important;
}}
[data-testid="metric-container"] label {{
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    color: {T['text2']} !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 1.3rem !important;
    color: {T['text']} !important;
}}

.stProgress > div > div > div {{
    background: {T['accent']} !important;
    border-radius: 2px !important;
}}
.stProgress > div > div {{
    background: {T['border']} !important;
    border-radius: 2px !important;
    height: 5px !important;
}}

[data-testid="stExpander"] {{
    border: 1px solid {T['border']} !important;
    border-radius: 6px !important;
    background: {T['surface']} !important;
}}
[data-testid="stExpander"] summary {{
    font-size: 13px !important;
    font-weight: 600 !important;
    background: {T['surface2']} !important;
    color: {T['text']} !important;
    padding: .7rem 1rem !important;
}}

hr {{
    border: none !important;
    border-top: 1px solid {T['border']} !important;
    margin: 1.2rem 0 !important;
}}

[data-testid="stDataFrame"] {{
    background: {T['surface']} !important;
}}
[data-testid="stDataFrame"] th {{
    background: {T['surface2']} !important;
    color: {T['text2']} !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
}}
[data-testid="stDataFrame"] td {{
    color: {T['text']} !important;
    font-size: 12px !important;
    background: {T['surface']} !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ag-topbar">
    <span class="ag-logo">Agro<span class="ag-logo-dot">Sense</span> AI</span>
    <span class="ag-tagline">Crop Intelligence System</span>
</div>
<div class="ag-page">
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:20px 16px 12px;border-bottom:1px solid {T['border']};margin-bottom:12px">
        <div style="font-size:1rem;font-weight:600;color:{T['text']};
            letter-spacing:-0.01em">AgroSense AI</div>
        <div style="font-size:10px;font-weight:600;letter-spacing:.1em;
            text-transform:uppercase;color:{T['text2']};margin-top:2px">
            Crop Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["Crop Advisor", "Plant Health", "Soil Analysis",
         "Market Prices", "Field Calendar", "ML Insights"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.divider()

    # Quick stats if result exists
    last = st.session_state.get("last_result", {})
    if last:
        st.markdown(f"""
        <div style="margin-top:16px;padding:12px 4px;font-size:12px">
            <div style="font-size:9px;font-weight:700;letter-spacing:.1em;
                text-transform:uppercase;color:{T['text2']};margin-bottom:8px">
                Last Result
            </div>
            <div style="font-weight:600;color:{T['accent']};
                text-transform:capitalize;font-size:14px">
                {last.get('crop','—').title()}
            </div>
            <div style="color:{T['text2']};font-size:11px;margin-top:2px">
                N:{last.get('N','—')} P:{last.get('P','—')} K:{last.get('K','—')}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Load ML pipeline ──────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Training ML models — first run only, ~30 seconds...")
def load_pipeline():
    from modules.ml_engine import get_pipeline
    return get_pipeline("Crop_recommendation.csv")

CSV_EXISTS = os.path.exists("Crop_recommendation.csv")
pipeline   = load_pipeline() if CSV_EXISTS else None


def plot_cfg(fig, h=280):
    """Apply consistent light chart styling."""
    fig.update_layout(
        paper_bgcolor = T['chart_bg'],
        plot_bgcolor  = T['chart_bg'],
        font          = dict(family="DM Sans", color=T['chart_txt']),
        height        = h,
        margin        = dict(l=0, r=10, t=36, b=10),
    )
    fig.update_xaxes(gridcolor=T['chart_grid'], zerolinecolor=T['border'],
                     tickfont=dict(color=T['chart_txt']))
    fig.update_yaxes(gridcolor=T['chart_grid'], zerolinecolor=T['border'],
                     tickfont=dict(color=T['chart_txt']))
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — CROP ADVISOR
# ══════════════════════════════════════════════════════════════════════════════
if page == "Crop Advisor":
    st.markdown("""
    <div class="ag-header">
        <p class="ag-title">Crop Advisor</p>
        <p class="ag-sub">Enter soil and climate parameters. Use live weather auto-fill for your location.</p>
    </div>
    """, unsafe_allow_html=True)

    col_in, col_out = st.columns([2, 3], gap="large")

    with col_in:
        # Weather auto-fill
        st.markdown('<span class="ag-label">Weather Auto-Fill</span>', unsafe_allow_html=True)
        wc1, wc2 = st.columns([3, 1])
        city = wc1.text_input("City", placeholder="e.g. Kangeyam, Coimbatore",
                               label_visibility="collapsed", key="city_inp")
        if wc2.button("Fetch", key="fetch_w"):
            with st.spinner("Fetching..."):
                wd = get_weather_by_city(city.strip())
            if "error" in wd:
                st.error(wd["error"])
            else:
                st.session_state["wd"] = wd
                st.success(f"{wd['city']}, {wd['country']}")
                st.session_state["temp"] = float(wd.get("temp", 25.0))
                st.session_state["hum"]  = float(wd.get("humidity", 70.0))
                st.session_state["rain"] = float(wd.get("rainfall_7d", 100.0))

        wd = st.session_state.get("wd", {})
        if wd and "temp" in wd:
            st.markdown(f"""
            <div class="ag-weather">
                <div class="ag-weather-city">{wd['city']}, {wd['country']}</div>
                <div class="ag-weather-temp">{wd['temp']}°C</div>
                <div class="ag-weather-desc">{wd['weather_desc']}</div>
                <div class="ag-weather-grid">
                    <div><div class="ag-wi-label">Humidity</div>
                         <div class="ag-wi-val">{wd['humidity']}%</div></div>
                    <div><div class="ag-wi-label">5-Day Rain</div>
                         <div class="ag-wi-val">{wd['rainfall_7d']} mm</div></div>
                    <div><div class="ag-wi-label">Wind</div>
                         <div class="ag-wi-val">{wd['wind_speed']} km/h</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Inputs
        st.markdown('<span class="ag-label">Soil Nutrients (kg/ha)</span>', unsafe_allow_html=True)
        i1, i2, i3 = st.columns(3)
        N = i1.number_input("N", 0, 200, 90, key="N")
        P = i2.number_input("P", 0, 145, 42, key="P")
        K = i3.number_input("K", 0, 205, 43, key="K")

        st.markdown('<span class="ag-label">Climate</span>', unsafe_allow_html=True)
        i4, i5 = st.columns(2)
        temp     = i4.number_input("Temp (°C)",   0.0, 55.0, float(wd.get("temp", 25.0)),     key="temp")
        humidity = i5.number_input("Humidity (%)", 0.0, 100.0, float(wd.get("humidity", 70.0)), key="hum")
        i6, i7 = st.columns(2)
        ph       = i6.number_input("Soil pH",      0.0, 14.0, 6.5,                              key="ph")
        rainfall = i7.number_input("Rainfall (mm)",0.0, 400.0, float(wd.get("rainfall_7d", 100.0)), key="rain")

        st.markdown('<span class="ag-label">Farm Details</span>', unsafe_allow_html=True)
        i8, i9 = st.columns(2)
        land   = i8.number_input("Land (acres)", 0.1, 100.0, 1.0, key="acres")
        prev   = i9.selectbox("Previous crop",
                    ["None","Rice","Wheat","Maize","Cotton","Pulses","Vegetables"])
        irr_m  = st.selectbox("Irrigation method",
                    ["Rainfed","Drip","Sprinkler","Flood/Furrow","Canal"])

        go_btn = st.button("Get Recommendation", type="primary")

    with col_out:
        if go_btn:
            if not CSV_EXISTS or pipeline is None:
                st.error("Place Crop_recommendation.csv in the project folder first.")
            else:
                from modules.ml_engine import predict_crop, get_arm_rules_for_crop
                
                # CRITICAL BUG FIX 1: Lowercase keys expected by Pandas
                feats = {"n":N,"p":P,"k":K,"temperature":temp,"humidity":humidity,"ph":ph,"rainfall":rainfall}
                res   = predict_crop(pipeline, feats)

                top_crop = res["top_crop"]
                top5     = res["top5"]
                zone_id  = res["soil_zone"]
                zname, zdesc = SOIL_ZONES.get(zone_id, ("Unknown",""))
                conf = res["confidence"]

                # Top recommendation card
                conf_tag = "ag-tag-green" if conf>=75 else "ag-tag-amber"
                st.markdown(f"""
                <div class="ag-card ag-card-green">
                    <span class="ag-label" style="margin-top:0">Recommended Crop</span>
                    <div style="display:flex;align-items:baseline;gap:10px;margin:4px 0 8px">
                        <span style="font-size:1.6rem;font-weight:600;
                            color:{T['text']};text-transform:capitalize">{top_crop.title()}</span>
                        <span class="{conf_tag} ag-tag">{conf}% confidence</span>
                    </div>
                    <div style="font-size:12px;color:{T['text2']}">
                        Soil zone: <strong style="color:{T['text']}">{zname}</strong>
                        &nbsp;·&nbsp; {zdesc}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Top-5 bar
                crops_list  = [c.title() for c,_ in top5]
                scores_list = [s for _,s in top5]
                fig_bar = go.Figure(go.Bar(
                    x=scores_list, y=crops_list, orientation="h",
                    marker_color=[T['accent'] if i==0 else T['border'] for i in range(5)],
                    text=[f"{s}%" for s in scores_list], textposition="outside",
                    textfont=dict(color=T['text']),
                ))
                fig_bar.update_layout(title="Top 5 Suitable Crops",
                                       xaxis_title="Confidence (%)",
                                       yaxis=dict(autorange="reversed"))
                plot_cfg(fig_bar, 240)
                st.plotly_chart(fig_bar, use_container_width=True)

                # Radar chart
                opt = CROP_NPK.get(top_crop.lower(), (80,40,40))
                rc  = ["N","P","K","Temp","Humidity","pH","Rainfall"]
                act = [min(N/180,1)*100, min(P/145,1)*100, min(K/205,1)*100,
                       min(temp/50,1)*100, min(humidity/100,1)*100,
                       min(ph/14,1)*100, min(rainfall/300,1)*100]
                ideal = [min(opt[0]/180,1)*100, min(opt[1]/145,1)*100, min(opt[2]/205,1)*100,
                         60, 65, 50, 60]

                fig_r = go.Figure()
                
                # CRITICAL BUG FIX 2: Valid Plotly rgba transparency for Radar
                user_soil_fill = hex_to_rgba(T['accent'], 0.16)
                ideal_soil_fill = hex_to_rgba(T['blue'], 0.09)

                fig_r.add_trace(go.Scatterpolar(r=act+[act[0]], theta=rc+[rc[0]],
                    fill="toself", name="Your Soil",
                    line_color=T['accent'], fillcolor=user_soil_fill))
                fig_r.add_trace(go.Scatterpolar(r=ideal+[ideal[0]], theta=rc+[rc[0]],
                    fill="toself", name=f"Ideal ({top_crop.title()})",
                    line_color=T['blue'], fillcolor=ideal_soil_fill,
                    line_dash="dash"))
                fig_r.update_layout(
                    polar=dict(bgcolor=T['chart_bg'],
                               radialaxis=dict(visible=True, range=[0,100],
                                              gridcolor=T['chart_grid'],
                                              tickfont=dict(size=8, color=T['chart_txt'])),
                               angularaxis=dict(tickfont=dict(size=10, color=T['text']))),
                    paper_bgcolor=T['chart_bg'],
                    legend=dict(font=dict(color=T['text'], size=10)),
                    height=300, margin=dict(l=20,r=20,t=20,b=20),
                    font=dict(family="DM Sans", color=T['text']),
                )
                st.plotly_chart(fig_r, use_container_width=True)

                # Risk + irrigation
                risks = weather_risk_summary(temp, humidity, rainfall)
                irr   = irrigation_advice(top_crop, rainfall, humidity, temp)

                def risk_cls(v): return "ag-risk-high" if v>65 else "ag-risk-med" if v>35 else "ag-risk-low"
                def rlabel(v):   return "High" if v>65 else "Moderate" if v>35 else "Low"

                st.markdown(f"""
                <span class="ag-label">Risk Assessment</span>
                <div class="ag-risk {risk_cls(risks['drought_risk'])}">
                    Drought Risk: {risks['drought_risk']}% — {rlabel(risks['drought_risk'])}
                </div>
                <div class="ag-risk {risk_cls(risks['waterlog_risk'])}">
                    Waterlogging Risk: {risks['waterlog_risk']}% — {rlabel(risks['waterlog_risk'])}
                </div>
                {'<div class="ag-risk ag-risk-high">Heat Stress: Temperature above 38°C</div>' if risks['heat_stress'] else ''}
                <span class="ag-label">Irrigation Advisory</span>
                <div class="ag-card" style="display:flex;gap:28px;font-size:13px">
                    <div><div style="font-size:9px;font-weight:600;letter-spacing:.1em;
                        text-transform:uppercase;color:{T['text2']};margin-bottom:3px">Frequency</div>
                        <strong>Every {irr['frequency_days']} days</strong></div>
                    <div><div style="font-size:9px;font-weight:600;letter-spacing:.1em;
                        text-transform:uppercase;color:{T['text2']};margin-bottom:3px">Method</div>
                        <strong>{irr['method']}</strong></div>
                    <div><div style="font-size:9px;font-weight:600;letter-spacing:.1em;
                        text-transform:uppercase;color:{T['text2']};margin-bottom:3px">Demand</div>
                        <strong>{irr['demand_level']}</strong></div>
                </div>
                """, unsafe_allow_html=True)

                # ARM rules
                rules = get_arm_rules_for_crop(pipeline, top_crop)
                if not rules.empty:
                    st.markdown('<span class="ag-label">Planting Rules (ARM)</span>',
                                unsafe_allow_html=True)
                    st.dataframe(rules.reset_index(drop=True),
                                 use_container_width=True, hide_index=True)

                st.session_state["last_result"] = {
                    "crop": top_crop, "N":N, "P":P, "K":K,
                    "temp":temp, "humidity":humidity,
                    "ph":ph, "rainfall":rainfall, "land_acres":land
                }
        else:
            st.markdown(f"""
            <div style="padding:60px 32px;text-align:center;border:1px solid {T['border']};
                border-radius:8px;background:{T['surface']};color:{T['text2']}">
                <p style="font-size:1rem;font-weight:600;color:{T['text']};margin-bottom:6px">
                    Enter your field parameters</p>
                <p style="font-size:12px">Auto-fill temperature, humidity and rainfall by
                    typing your city name and clicking Fetch.</p>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PLANT HEALTH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Plant Health":
    st.markdown("""
    <div class="ag-header">
        <p class="ag-title">Plant Health Check</p>
        <p class="ag-sub">Upload a leaf photo. The system detects disease and prescribes treatment.</p>
    </div>
    """, unsafe_allow_html=True)

    up_col, res_col = st.columns([1,1], gap="large")

    with up_col:
        st.markdown('<span class="ag-label">Upload Leaf Image</span>',
                    unsafe_allow_html=True)
        uploaded = st.file_uploader("Leaf photo (JPG / PNG)",
                                     type=["jpg","jpeg","png"],
                                     label_visibility="collapsed")
        if uploaded:
            from PIL import Image
            import io
            img_bytes = uploaded.read()
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            st.image(img, use_container_width=True)
            w, h = img.size
            st.markdown(f"""
            <div class="ag-card" style="display:flex;gap:20px;font-size:12px">
                <div><span class="ag-label" style="margin:0 0 3px">Dimensions</span>
                    <span style="font-family:'DM Mono',monospace">{w}×{h}</span></div>
                <div><span class="ag-label" style="margin:0 0 3px">Format</span>
                    <span style="font-family:'DM Mono',monospace">
                    {uploaded.type.split('/')[-1].upper()}</span></div>
                <div><span class="ag-label" style="margin:0 0 3px">Size</span>
                    <span style="font-family:'DM Mono',monospace">
                    {len(img_bytes)//1024} KB</span></div>
            </div>
            """, unsafe_allow_html=True)

    with res_col:
        if uploaded:
            with st.spinner("Analysing..."):
                uploaded.seek(0)
                diag = analyse_leaf(uploaded)

            healthy  = "healthy" in diag["disease"].lower()
            tag_cls  = "ag-tag-green" if healthy else "ag-tag-red"
            tag_txt  = "Healthy" if healthy else "Disease Detected"
            conf     = diag["confidence"]
            bar_c    = T['accent'] if conf>=70 else T['amber'] if conf>=45 else T['red']

            st.markdown(f"""
            <div class="ag-card ag-card-green">
                <span class="ag-label" style="margin-top:0">Diagnosis</span>
                <div style="display:flex;align-items:baseline;gap:10px;margin:4px 0 6px">
                    <span style="font-size:1.25rem;font-weight:600;
                        color:{T['text']}">{diag['condition']}</span>
                    <span class="{tag_cls} ag-tag">{tag_txt}</span>
                </div>
                <div style="font-size:12px;color:{T['text2']}">
                    Plant: <strong style="color:{T['text']}">{diag['plant']}</strong>
                    &nbsp;·&nbsp; Method: {diag['method']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="ag-bar-wrap">
                <div class="ag-bar-head">
                    <span>Confidence</span>
                    <span style="font-family:'DM Mono',monospace">{conf}%</span>
                </div>
                <div class="ag-bar-track">
                    <div class="ag-bar-fill" style="width:{conf}%;background:{bar_c}"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Colour ratios
            if "ratios" in diag:
                st.markdown('<span class="ag-label">Colour Analysis</span>',
                            unsafe_allow_html=True)
                for name, val in [("Green — Healthy",  diag["ratios"]["green"]),
                                   ("Brown — Necrosis", diag["ratios"]["brown"]),
                                   ("Yellow — Chlorosis",diag["ratios"]["yellow"]),
                                   ("Dark Spots",       diag["ratios"]["dark"])]:
                    pct  = int(val*100)
                    bc2  = T['accent'] if "Green" in name else T['red'] if pct>15 else T['border']
                    st.markdown(f"""
                    <div class="ag-bar-wrap">
                        <div class="ag-bar-head" style="font-size:11px">
                            <span>{name}</span>
                            <span style="font-family:'DM Mono',monospace">{pct}%</span>
                        </div>
                        <div class="ag-bar-track" style="height:4px">
                            <div class="ag-bar-fill" style="width:{min(pct,100)}%;
                                height:4px;background:{bc2}"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Treatment
            if not healthy:
                border_c = T['red']
                bg_c = "#FFEBE9"
                st.markdown(f"""
                <span class="ag-label">Treatment Protocol</span>
                <div class="ag-card" style="border-left:3px solid {border_c};
                    background:{bg_c}">
                    <p style="font-size:13px;color:{T['text']};
                        line-height:1.6;margin:0">{diag['treatment']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ag-card ag-card-green">
                    <p style="font-size:13px;color:{T['accent']};margin:0">
                        Plant appears healthy. Continue regular monitoring.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding:60px 32px;text-align:center;
                border:1px dashed {T['border']};border-radius:8px;
                background:{T['surface']};color:{T['text2']}">
                <p style="font-size:13px">Upload a clear, well-lit leaf photo.<br>
                    JPG and PNG supported.</p>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — SOIL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Soil Analysis":
    st.markdown("""
    <div class="ag-header">
        <p class="ag-title">Soil Analysis</p>
        <p class="ag-sub">NPK profiling, pH suitability, health score, and fertiliser schedule.</p>
    </div>
    """, unsafe_allow_html=True)

    last = st.session_state.get("last_result", {})
    sc1, sc2 = st.columns([1,1], gap="large")

    with sc1:
        st.markdown('<span class="ag-label">Parameters</span>', unsafe_allow_html=True)
        sa1, sa2, sa3 = st.columns(3)
        sN  = sa1.number_input("N", 0, 200, int(last.get("N",  90)), key="sN")
        sP  = sa2.number_input("P", 0, 145, int(last.get("P",  42)), key="sP")
        sK  = sa3.number_input("K", 0, 205, int(last.get("K",  43)), key="sK")
        sb1, sb2 = st.columns(2)
        sph  = sb1.number_input("pH",       0.0, 14.0, float(last.get("ph", 6.5)), key="sph")
        shum = sb2.number_input("Humidity", 0.0, 100.0, 70.0, key="shum")
        scrop = st.selectbox("Crop for fertiliser",
            sorted(list(CROP_NPK.keys())), key="scrop")
        sacres = st.number_input("Land (acres)", 0.1, 100.0,
                                  float(last.get("land_acres",1.0)), key="sacres")

        hs = soil_health_score(sN, sP, sK, sph, shum)
        score_c = T['accent'] if hs['overall']>=70 else T['amber'] if hs['overall']>=45 else T['red']
        tag_cls = "ag-tag-green" if hs['overall']>=70 else "ag-tag-amber" if hs['overall']>=45 else "ag-tag-red"

        st.markdown(f"""
        <div class="ag-card" style="text-align:center;margin-top:12px">
            <span class="ag-label" style="margin-top:0">Overall Soil Health</span>
            <div style="font-size:2.8rem;font-weight:600;color:{score_c};
                font-family:'DM Mono',monospace;margin:6px 0">{hs['overall']}</div>
            <span class="{tag_cls} ag-tag">{hs['label']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="ag-label">Parameter Scores</span>',
                    unsafe_allow_html=True)
        for param, score, lbl, val, unit in [
            ("Nitrogen (N)",   hs["N_score"],  hs["N_label"],  sN,  "kg/ha"),
            ("Phosphorus (P)", hs["P_score"],  hs["P_label"],  sP,  "kg/ha"),
            ("Potassium (K)",  hs["K_score"],  hs["K_label"],  sK,  "kg/ha"),
            ("Soil pH",        hs["ph_score"], hs["ph_label"], sph, ""),
        ]:
            bc = T['accent'] if score>=70 else T['amber'] if score>=45 else T['red']
            tc = "ag-tag-green" if score>=70 else "ag-tag-amber" if score>=45 else "ag-tag-red"
            st.markdown(f"""
            <div class="ag-bar-wrap">
                <div class="ag-bar-head">
                    <span>{param}
                        <span style="font-family:'DM Mono',monospace;font-size:10px;
                            color:{T['text2']};margin-left:6px">{val} {unit}</span>
                    </span>
                    <span class="{tc} ag-tag" style="font-size:9px">{lbl}</span>
                </div>
                <div class="ag-bar-track">
                    <div class="ag-bar-fill" style="width:{score}%;background:{bc}"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # pH gauge
        fig_ph = go.Figure(go.Indicator(
            mode="gauge+number", value=sph,
            title={"text":"Soil pH","font":{"family":"DM Sans","size":12,
                                             "color":T['text']}},
            number={"font":{"color":T['text']}},
            gauge={
                "axis":  {"range":[0,14], "tickfont":{"size":8,"color":T['text2']}},
                "bar":   {"color":T['accent']},
                "bgcolor": T['chart_bg'],
                # CRITICAL BUG FIX 3: Valid Plotly rgba transparency for Gauge
                "steps": [
                    {"range":[0,4.5],  "color": hex_to_rgba(T['red'], 0.25)},
                    {"range":[4.5,6],  "color": hex_to_rgba(T['amber'], 0.25)},
                    {"range":[6,7.5],  "color": hex_to_rgba(T['accent'], 0.25)},
                    {"range":[7.5,9],  "color": hex_to_rgba(T['amber'], 0.25)},
                    {"range":[9,14],   "color": hex_to_rgba(T['red'], 0.25)},
                ],
            }
        ))
        fig_ph.update_layout(height=180, margin=dict(l=20,r=20,t=30,b=5),
                              paper_bgcolor=T['chart_bg'],
                              font=dict(family="DM Sans", color=T['text']))
        st.plotly_chart(fig_ph, use_container_width=True)

    with sc2:
        fert = fertiliser_recommendation(scrop, sN, sP, sK, sacres)

        # NPK comparison chart
        fig_npk = go.Figure()
        
        # CRITICAL BUG FIX 4: Valid Plotly rgba transparency for Bars
        fig_npk.add_trace(go.Bar(name="Current",
            x=["Nitrogen","Phosphorus","Potassium"],
            y=[sN, sP, sK], marker_color=hex_to_rgba(T['accent'], 0.6)))
        fig_npk.add_trace(go.Bar(name="Optimal",
            x=["Nitrogen","Phosphorus","Potassium"],
            y=[fert["optimal_N"], fert["optimal_P"], fert["optimal_K"]],
            marker_color=hex_to_rgba(T['blue'], 0.73)))
            
        fig_npk.update_layout(barmode="group", title="Current vs Optimal NPK",
                               yaxis_title="kg/ha")
        plot_cfg(fig_npk, 240)
        st.plotly_chart(fig_npk, use_container_width=True)

        st.markdown('<span class="ag-label">Fertiliser Schedule</span>',
                    unsafe_allow_html=True)
        if fert["schedule"]:
            for item in fert["schedule"]:
                st.markdown(f"""
                <div class="ag-card" style="display:flex;justify-content:space-between;
                    align-items:center;padding:12px 14px">
                    <div>
                        <div style="font-size:13px;font-weight:600;
                            color:{T['text']}">{item['product']}</div>
                        <div style="font-size:11px;color:{T['text2']};
                            margin-top:2px">{item['timing']}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-family:'DM Mono',monospace;font-size:1.1rem;
                            font-weight:500;color:{T['text']}">{item['dose_kg']} kg</div>
                        <div style="font-size:10px;color:{T['text2']}">
                            for {fert['land_ha']} ha</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ag-card ag-card-green">
                <p style="font-size:13px;color:{T['accent']};margin:0">
                    Nutrient levels meet or exceed optimal. No additional
                    fertiliser needed.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <span class="ag-label">Deficits Summary</span>
        <div class="ag-card">
            <div class="ag-stat-row">
                <span class="ag-stat-label">N Deficit</span>
                <span class="ag-stat-val">{fert['deficit_N']} kg/ha</span>
            </div>
            <div class="ag-stat-row">
                <span class="ag-stat-label">P Deficit</span>
                <span class="ag-stat-val">{fert['deficit_P']} kg/ha</span>
            </div>
            <div class="ag-stat-row">
                <span class="ag-stat-label">K Deficit</span>
                <span class="ag-stat-val">{fert['deficit_K']} kg/ha</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — MARKET PRICES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Market Prices":
    st.markdown("""
    <div class="ag-header">
        <p class="ag-title">Market Prices</p>
        <p class="ag-sub">Live mandi prices from data.gov.in and Agmarknet — with profit estimator.</p>
    </div>
    """, unsafe_allow_html=True)

    last_crop = st.session_state.get("last_result", {}).get("crop", "rice")
    all_crops = sorted(list(CROP_NPK.keys()))
    try: default_i = all_crops.index(last_crop.lower())
    except: default_i = 0

    mp1, mp2 = st.columns([1,1], gap="large")

    with mp1:
        st.markdown('<span class="ag-label">Crop & Land</span>', unsafe_allow_html=True)
        sel_crop = st.selectbox("Crop", all_crops, index=default_i,
                                 label_visibility="collapsed", key="mp_crop")
        mp_acres = st.number_input("Land (acres)", 0.1, 100.0,
                                    float(st.session_state.get("last_result",{}).get("land_acres",1.0)),
                                    key="mp_acres")
        if st.button("Get Price & Profit", type="primary"):
            with st.spinner("Fetching..."):
                st.session_state["mp"] = get_market_price(sel_crop)
                st.session_state["pf"] = get_profit_estimate(sel_crop, mp_acres)
                st.session_state["mp_crop_sel"] = sel_crop

    mp  = st.session_state.get("mp", {})
    pf  = st.session_state.get("pf", {})
    mcs = st.session_state.get("mp_crop_sel", sel_crop)

    if mp and mp.get("price"):
        with mp1:
            trend     = mp.get("trend","stable")
            trend_sym = {"up": "▲", "down": "▼", "stable": "→"}[trend]
            trend_c   = {"up": T['accent'], "down": T['red'], "stable": T['text2']}[trend]

            st.markdown(f"""
            <div class="ag-card ag-card-green" style="margin-top:10px">
                <span class="ag-label" style="margin-top:0">{mcs.title()} — Mandi Price</span>
                <div style="display:flex;align-items:baseline;gap:8px;margin:4px 0">
                    <span style="font-family:'DM Mono',monospace;font-size:2rem;
                        font-weight:500;color:{T['text']}">₹ {mp['price']:,}</span>
                    <span style="font-size:11px;color:{T['text2']}">{mp['unit']}</span>
                </div>
                <div style="font-size:11px;color:{T['text2']};line-height:1.6">
                    {mp['market']}<br>
                    {mp.get('date','—')} · {mp.get('source','—')}
                </div>
                <div style="font-size:12px;font-weight:600;color:{trend_c};margin-top:6px">
                    {trend_sym} {'Trending up' if trend=='up' else 'Trending down' if trend=='down' else 'Stable'}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Price comparison
        from modules.market import FALLBACK_PRICES
        cps = [(c.title(), FALLBACK_PRICES[c]["price"])
               for c in ["rice","wheat","maize","chickpea","cotton","groundnut","mustard","lentil"]
               if c in FALLBACK_PRICES]
        cps.sort(key=lambda x: x[1], reverse=True)

        fig_mp = go.Figure(go.Bar(
            x=[p for _,p in cps], y=[n for n,_ in cps], orientation="h",
            marker_color=[T['accent'] if n.lower()==mcs.lower() else T['border'] for n,_ in cps],
            text=[f"₹{p:,}" for _,p in cps], textposition="outside",
            textfont=dict(color=T['text']),
        ))
        fig_mp.update_layout(title="Price Comparison (₹/quintal)",
                              yaxis=dict(autorange="reversed"))
        plot_cfg(fig_mp, 260)
        st.plotly_chart(fig_mp, use_container_width=True)

        if pf:
            with mp2:
                st.markdown(f"""
                <div class="ag-header">
                    <p class="ag-title" style="font-size:1.2rem">Profit Estimator</p>
                    <p class="ag-sub">{mp_acres} acres of {mcs.title()}</p>
                </div>
                """, unsafe_allow_html=True)

                m1, m2 = st.columns(2)
                m1.metric("Revenue", f"₹ {pf['revenue']:,}")
                m2.metric("Costs",   f"₹ {pf['cost']:,}")
                m3, m4 = st.columns(2)
                m3.metric("Net Profit", f"₹ {pf['profit']:,}")
                m4.metric("ROI",        f"{pf['roi_pct']}%")

                fig_wf = go.Figure(go.Waterfall(
                    orientation="v",
                    measure=["absolute","relative","total"],
                    x=["Revenue","Input Cost","Net Profit"],
                    y=[pf["revenue"], -pf["cost"], 0],
                    connector={"line":{"color":T['border']}},
                    decreasing={"marker":{"color":T['red']}},
                    increasing={"marker":{"color":T['accent']}},
                    totals={"marker":{"color":T['blue']}},
                    text=[f"₹{pf['revenue']:,}", f"-₹{pf['cost']:,}", f"₹{pf['profit']:,}"],
                    textposition="outside",
                    textfont={"color":T['text']},
                ))
                fig_wf.update_layout(showlegend=False)
                plot_cfg(fig_wf, 270)
                st.plotly_chart(fig_wf, use_container_width=True)

                st.markdown(f"""
                <div class="ag-card">
                    <div class="ag-stat-row">
                        <span class="ag-stat-label">Expected Yield</span>
                        <span class="ag-stat-val">{pf['yield_q']} quintals</span>
                    </div>
                    <div class="ag-stat-row">
                        <span class="ag-stat-label">Price per Quintal</span>
                        <span class="ag-stat-val">₹ {pf['price_per_q']:,}</span>
                    </div>
                    <div class="ag-stat-row">
                        <span class="ag-stat-label">Profit per Acre</span>
                        <span class="ag-stat-val">₹ {int(pf['profit']/mp_acres):,}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — FIELD CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Field Calendar":
    st.markdown("""
    <div class="ag-header">
        <p class="ag-title">Field Calendar</p>
        <p class="ag-sub">Month-by-month agronomic schedule with key milestones.</p>
    </div>
    """, unsafe_allow_html=True)

    cal_crop = st.selectbox("Crop", sorted(list(CROP_NPK.keys())),
                             label_visibility="collapsed", key="cal_crop")
    cal = get_field_calendar(cal_crop)

    st.markdown(f"""
    <div class="ag-card" style="margin-bottom:16px;display:flex;
        justify-content:space-between;align-items:center">
        <div>
            <span style="font-size:1rem;font-weight:600;
                text-transform:capitalize;color:{T['text']}">{cal_crop.title()}</span>
            <span style="font-size:12px;color:{T['text2']};
                margin-left:10px">{cal['season']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calendar grid
    html_cells = ""
    for month in MONTHS:
        activity = cal["calendar"].get(month, "Rest")
        base_c   = ACTIVITY_COLORS.get(activity, "#888888")
        bg_c     = base_c + "22"
        
        # CRITICAL BUG FIX 5: HTML formatting fully un-indented
        html_cells += f"""
<div class="ag-cal-cell" style="background:{bg_c}; border:1px solid {base_c}44">
    <div class="ag-cal-month" style="color:{T['text2']}">{month}</div>
    <div class="ag-cal-act" style="color:{base_c};font-weight:600">{activity}</div>
</div>"""

    st.markdown(f'<div class="ag-cal">{html_cells}</div>', unsafe_allow_html=True)

    # Legend
    st.markdown('<span class="ag-label" style="margin-top:18px">Legend</span>',
                unsafe_allow_html=True)
    leg_html = f'<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:6px">'
    for act, color in ACTIVITY_COLORS.items():
        leg_html += f"""
        <div style="display:flex;align-items:center;gap:6px;font-size:12px;
            font-weight:500;color:{T['text']}">
            <div style="width:10px;height:10px;border-radius:2px;
                background:{color}"></div>{act}
        </div>"""
    leg_html += "</div>"
    st.markdown(leg_html, unsafe_allow_html=True)

    # Milestones
    st.markdown('<span class="ag-label" style="margin-top:18px">Key Milestones</span>',
                unsafe_allow_html=True)
    for month, desc in cal["milestones"]:
        st.markdown(f"""
<div class="ag-card" style="display:flex;gap:14px;padding:10px 14px;align-items:flex-start;margin-bottom:6px">
    <span style="font-family:'DM Mono',monospace;font-size:11px;font-weight:600;color:{T['text2']};min-width:32px">{month}</span>
    <span style="font-size:13px;color:{T['text']}">{desc}</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — ML INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "ML Insights":
    st.markdown("""
    <div class="ag-header">
        <p class="ag-title">ML Insights</p>
        <p class="ag-sub">Pipeline overview, model benchmarks, clustering, and association rules.</p>
    </div>
    """, unsafe_allow_html=True)

    if not CSV_EXISTS or pipeline is None:
        st.info("Place Crop_recommendation.csv in the project folder to run and view ML insights.")
    else:
        # Pipeline table
        st.markdown('<span class="ag-label">Pipeline Overview</span>',
                    unsafe_allow_html=True)
        pl_rows = [
            ("Phase 1 — EDA",            "Crop_recommendation.csv",      "2200 rows × 7 features, 22 crop labels"),
            ("Phase 2 — Preprocessing",  "StandardScaler + IQR capping", "Feature engineering: NPK ratio, climate stress"),
            ("Phase 3 — Classification", "6 models benchmarked",         f"Best: {pipeline.get('best_model_name','Random Forest')} — {pipeline.get('best_acc','—')}%"),
            ("Phase 4 — Clustering",     "K-Means (k=6)",                "6 soil zone clusters, Silhouette + Elbow verified"),
            ("Phase 5 — CNN",            "MobileNetV2 transfer learning","38 disease classes, colour fallback always active"),
            ("Phase 6 — ARM",            "Apriori (mlxtend)",            "Min support 4%, confidence 55%, lift-ranked rules"),
        ]
        pl_df = pd.DataFrame(pl_rows, columns=["Phase","Method","Output"])
        st.dataframe(pl_df, use_container_width=True, hide_index=True)

        st.divider()

        bm = pipeline.get("benchmark")
        if bm is not None and not bm.empty:
            st.markdown('<span class="ag-label">Classifier Benchmarks</span>',
                        unsafe_allow_html=True)
            st.dataframe(bm, use_container_width=True, hide_index=True)

            fig_bm = go.Figure()
            
            # CRITICAL BUG FIX 6: Valid Plotly rgba transparency for Benchmarks
            fig_bm.add_trace(go.Bar(name="Train", x=bm["Model"], y=bm["Train Acc %"],
                                    marker_color=hex_to_rgba(T['accent'], 0.55)))
            fig_bm.add_trace(go.Bar(name="Test",  x=bm["Model"], y=bm["Test Acc %"],
                                     marker_color=T['accent']))
            fig_bm.add_trace(go.Bar(name="CV",    x=bm["Model"], y=bm["CV Mean %"],
                                     marker_color=T['blue']))
                                     
            fig_bm.update_layout(barmode="group", title="Model Accuracy Comparison",
                                  yaxis_title="Accuracy (%)")
            plot_cfg(fig_bm, 300)
            st.plotly_chart(fig_bm, use_container_width=True)

        st.divider()

        fi = pipeline.get("feature_imp")
        if fi is not None:
            from modules.ml_engine import FEATURES
            st.markdown('<span class="ag-label">Feature Importance (Random Forest)</span>',
                        unsafe_allow_html=True)
            fi_df = pd.DataFrame({"Feature":FEATURES,"Importance":fi}).sort_values("Importance")
            fig_fi = go.Figure(go.Bar(
                x=fi_df["Importance"], y=fi_df["Feature"], orientation="h",
                marker_color=T['accent'],
                text=[f"{v:.3f}" for v in fi_df["Importance"]],
                textposition="outside", textfont=dict(color=T['text']),
            ))
            fig_fi.update_layout(xaxis_title="Importance Score")
            plot_cfg(fig_fi, 280)
            st.plotly_chart(fig_fi, use_container_width=True)

        st.divider()

        st.markdown('<span class="ag-label">Soil Zone Descriptions</span>',
                    unsafe_allow_html=True)
        zone_df = pd.DataFrame(
            [(k, v[0], v[1]) for k,v in SOIL_ZONES.items()],
            columns=["Zone","Name","Description"])
        st.dataframe(zone_df, use_container_width=True, hide_index=True)

        st.divider()

        rules = pipeline.get("arm_rules")
        if rules is not None and not rules.empty:
            st.markdown('<span class="ag-label">Top Association Rules</span>',
                        unsafe_allow_html=True)
            st.dataframe(rules.head(15).reset_index(drop=True),
                         use_container_width=True, hide_index=True)

        st.divider()
        st.markdown('<span class="ag-label">Innovation Features</span>',
                    unsafe_allow_html=True)
        for name, desc in [
            ("Live Weather API",      "OpenWeatherMap — auto-fills temp, humidity, 5-day rainfall"),
            ("Live Market Prices",    "data.gov.in + Agmarknet — real mandi prices with seasonal adjustment"),
            ("Profit Estimator",      "Revenue, cost, net profit, ROI per acre for any recommended crop"),
            ("Multi-Model Benchmark", "6 classifiers compared; best selected automatically"),
            ("K-Means Soil Zoning",   "6 agronomic soil zones mapped from NPK + climate cluster"),
            ("Association Rule Mining","Apriori rules — e.g. N_high + Rain_high → Rice (91% conf)"),
            ("Disease Detection",     "CNN + colour heuristic fallback — always functional"),
            ("Fertiliser Calculator", "Exact kg/ha doses for Urea, DAP, MOP by land area"),
        ]:
            st.markdown(f"""
            <div class="ag-card" style="padding:10px 14px;margin-bottom:6px;
                display:flex;gap:12px;align-items:flex-start">
                <span style="font-size:12px;font-weight:600;
                    color:{T['text']};min-width:180px">{name}</span>
                <span style="font-size:12px;color:{T['text2']}">{desc}</span>
            </div>
            """, unsafe_allow_html=True)

# Close page wrapper
st.markdown("</div>", unsafe_allow_html=True)