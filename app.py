import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

st.set_page_config(
    page_title="진주품질개선팀 고장 현황",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.main .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 1400px; }
.kpi-card {
    background: #fff;
    border-radius: 16px;
    padding: 14px 8px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(100,160,220,0.12);
    margin-bottom: 4px;
}
.kpi-val { font-size: 26px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.kpi-label { font-size: 11px; color: #7aabcc; margin-top: 3px; }
.info-bar {
    background: #f0f8ff;
    border-left: 3px solid #4da6e8;
    border-radius: 0 8px 8px 0;
    padding: 7px 14px;
    margin-bottom: 10px;
    font-size: 12px;
    color: #3a7cb0;
}
.rule-bar {
    background: #f0f8ff;
    border-left: 3px solid #4da6e8;
    border-radius: 0 8px 8px 0;
    padding: 8px 14px;
    margin-bottom: 12px;
    font-size: 11px;
    color: #3a7cb0;
    line-height: 1.9;
}
.empty-bar {
    background: #f8f8f8;
    border-left: 3px solid #ccc;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 13px;
    color: #999;
    text-align: center;
}
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#fff; border-bottom:1.5px solid #b8dcf5; padding:10px 0; margin-bottom:12px;">
  <span style="font-size:17px; font-weight:700; color:#1a5c8a;">📡 진주품질개선팀 &nbsp; 고장 현황 대시보드</span>
</div>
""", unsafe_allow_html=True)

# ── 파일 업로드 ───────────────────────────────────────────────────
uploaded = st.file_uploader(
    "📂 엑셀 파일 업로드 (매일 새 파일로 교체하면 자동 갱신)",
    type=["xlsx"],
    help="26년_진주품질개선팀_고장_RAW_DATA.xlsx"
)

if uploaded is None:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; color:#7aabcc;">
      <div style="font-size:48px;">📂</div>
      <div style="font-size:16px; margin-top:12px;">위의 버튼을 눌러 엑셀 파일을 업로드해주세요</div>
      <div style="font-size:12px; margin-top:6px; color:#b0cfe0;">파일명: 26년_진주품질개선팀_고장_RAW_DATA.xlsx</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── 데이터 로드 ───────────────────────────────────────────────────
@st.cache_data
def load_all(file_bytes):
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    sheets = xls.sheet_names
    data = {}

    # 메인 시트
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name='5G_LTE OOS_진주')
    df['발생시각_dt'] = pd.to_datetime(df['발생시각'], errors='coerce')
    df['발생일자'] = df['발생시각_dt'].dt.date
    df['월'] = df['발생시각_dt'].dt.month
    data['main'] = df

    # 중계기 및 MIBOS
    if '중계기 및 MIBOS 알람' in sheets:
        data['rep'] = pd.read_excel(io.BytesIO(file_bytes), sheet_name='중계기 및 MIBOS 알람')
    
    # gREMS
    if 'gREMS' in sheets:
        data['grems'] = pd.read_excel(io.BytesIO(file_bytes), sheet_name='gREMS')

    # 추가 알람 시트들
    extra_sheets = ['RMS_A망 미복구', 'RMS_DACS 미복구', 'RMS_통합RCU미복구', 'NO-CALL현황', 'MIBOS AMP 미사용']
    for s in extra_sheets:
        if s in sheets:
            data[s] = pd.read_excel(io.BytesIO(file_bytes), sheet_name=s)

    return data, sheets

file_bytes = uploaded.read()
data, sheet_names = load_all(file_bytes)
df = data['main']

# ── 금일 알람 로직 ────────────────────────────────────────────────
def calc_batch(df):
    latest_date = df['발생일자'].max()
    
    # 전체 데이터에서 장비명별 다발 횟수 계산
    dabal_map = df.groupby('장비명').size().to_dict()
    
    # 최신일자 데이터
    df_latest = df[df['발생일자'] == latest_date].copy()
    
    # 장비명별로 최신 발생시각 1건만 남김
    df_latest = df_latest.sort_values('발생시각_dt', ascending=False)
    df_latest = df_latest.drop_duplicates(subset=['장비명'], keep='first')
    
    # 복구 여부 판단
    def judge_status(row):
        gj = str(row.get('고장구분', '')).strip()
        detail = str(row.get('복구/미복구 상세내역', '')).strip()
        # 고장구분 또는 상세내역에 '복구' 포함 → 복구
        if '복구' in gj or '복구' in detail:
            return '복구'
        # 고장구분 비어있거나 nan → 미복구
        if gj == '' or gj == 'nan':
            return '미복구'
        return '미복구'

    df_latest['상태'] = df_latest.apply(judge_status, axis=1)
    df_latest['다발횟수'] = df_latest['장비명'].map(dabal_map)
    df_latest['다발'] = df_latest['다발횟수'].apply(lambda x: f"다발 {x}회" if x > 1 else "-")
    
    return df_latest, latest_date, dabal_map

df_batch, latest_date, dabal_map = calc_batch(df)

# ── 대시보드 통계 ─────────────────────────────────────────────────
def get_stats(df):
    # 다발 제거 후 실건수 (Port+발생시각 중복제거)
    df_dedup = df.drop_duplicates(subset=['Port', '발생시각'])
    total = len(df_dedup)
    
    # 미복구: 최신일자 기준
    unfix = len(df_batch[df_batch['상태'] == '미복구'])
    fix = len(df_batch[df_batch['상태'] == '복구'])
    
    # 다발 국소 수
    dabal_total = sum(1 for v in dabal_map.values() if v > 1)
    
    g5 = len(df_dedup[df_dedup['시스템'] == '5G'])
    lte = len(df_dedup[df_dedup['시스템'] == 'LTE'])
    
    # 고장구분별 (복구/Unit/BP/재발생/점검중/기타)
    gj = df_dedup['고장구분'].str.strip().str.upper()
    cats = {
        '복구':   len(df_dedup[df_dedup['고장구분'].str.strip().str.lower() == '복구']),
        'Unit':   len(df_dedup[gj == 'UNIT']),
        'BP':     len(df_dedup[gj == 'BP']),
        '재발생': len(df_dedup[df_dedup['고장구분'].str.strip() == '재발생']),
        '점검중': len(df_dedup[df_dedup['고장구분'].str.strip() == '점검중']),
        '기타':   len(df_dedup[~df_dedup['고장구분'].str.strip().str.lower().isin(['복구','unit','bp','재발생','점검중',''])]),
    }
    
    # 5G/LTE 고장구분별
    df5 = df_dedup[df_dedup['시스템'] == '5G']
    dflte = df_dedup[df_dedup['시스템'] == 'LTE']
    cats5 = {
        '복구':   len(df5[df5['고장구분'].str.strip().str.lower() == '복구']),
        'Unit':   len(df5[df5['고장구분'].str.strip().str.upper() == 'UNIT']),
        'BP':     len(df5[df5['고장구분'].str.strip().str.upper() == 'BP']),
        '재발생': len(df5[df5['고장구분'].str.strip() == '재발생']),
        '점검중': len(df5[df5['고장구분'].str.strip() == '점검중']),
        '기타':   len(df5[~df5['고장구분'].str.strip().str.lower().isin(['복구','unit','bp','재발생','점검중',''])]),
    }
    catslte = {
        '복구':   len(dflte[dflte['고장구분'].str.strip().str.lower() == '복구']),
        'Unit':   len(dflte[dflte['고장구분'].str.strip().str.upper() == 'UNIT']),
        'BP':     len(dflte[dflte['고장구분'].str.strip().str.upper() == 'BP']),
        '재발생': len(dflte[dflte['고장구분'].str.strip() == '재발생']),
        '점검중': len(dflte[dflte['고장구분'].str.strip() == '점검중']),
        '기타':   len(dflte[~dflte['고장구분'].str.strip().str.lower().isin(['복구','unit','bp','재발생','점검중',''])]),
    }
    
    # 장비 중분류별
    sub = df_dedup['고장구분(중분류)'].value_counts().head(8)
    
    # 월별
    month_grp = df_dedup.groupby('월').size().sort_index()
    month_labels = [f"{int(m)}월" for m in month_grp.index]
    month_vals   = month_grp.values.tolist()
    
    # 시군구별
    area = df_dedup['시군구'].value_counts().head(10)
    
    return {
        'total': total, 'unfix': unfix, 'fix': fix,
        'dabal_total': dabal_total, 'g5': g5, 'lte': lte,
        'cats': cats, 'cats5': cats5, 'catslte': catslte,
        'sub': sub, 'month_labels': month_labels, 'month_vals': month_vals,
        'area': area,
    }

stats = get_stats(df)

# ── 탭 구성 ───────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 대시보드",
    "🔔 금일 알람",
    "📋 전체 RAW 데이터",
    "📡 중계기·MIBOS",
    "🏢 gREMS 알람",
    "🔔 기타 알람 현황",
])

# ══ TAB1 대시보드 ══════════════════════════════════════════════════
with tab1:
    st.markdown(f"""
    <div class="info-bar">📅 기준일: <b>{latest_date}</b> &nbsp;|&nbsp; 파일: <b>{uploaded.name}</b></div>
    <div class="rule-bar">
    ① 동일 Port+발생시각 = 다발알람 → 1건 &nbsp;|&nbsp;
    ② 동일 장비명+다른 발생시각 = 최신 1건만, 나머지 자동복구 &nbsp;|&nbsp;
    ③ 고장구분/상세내역에 복구 포함 → 복구, 비어있으면 → 미복구 &nbsp;|&nbsp;
    ④ 최신일자에 없는 장비 → 복구 처리
    </div>
    """, unsafe_allow_html=True)

    # KPI
    kpi_data = [
        (str(stats['total']),        "실 고장 건수",    "#4da6e8"),
        (str(stats['unfix']),        "미복구",          "#e05c5c"),
        (str(stats['fix']),          "복구 완료",       "#2ecc87"),
        (str(stats['dabal_total']),  "다발알람 국소",   "#e65100"),
        (str(stats['g5']),           "5G 고장",         "#4da6e8"),
        (str(stats['lte']),          "LTE 고장",        "#f5a623"),
    ]
    cols_kpi = st.columns(6)
    for col, (val, label, color) in zip(cols_kpi, kpi_data):
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-val" style="color:{color};">{val}</div>
          <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cats_labels = list(stats['cats'].keys())
    cats_vals   = list(stats['cats'].values())
    colors_bar  = ["#4da6e8","#f5a623","#a78bfa","#60a5fa","#34d399","#f87171"]

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Pie(
            labels=["복구","미복구"],
            values=[stats['fix'], stats['unfix']],
            hole=0.65,
            marker=dict(colors=["#2ecc87","#f87171"]),
            textinfo="label+value", textfont_size=13,
        ))
        fig.update_layout(title="복구 / 미복구 현황",
            title_font=dict(size=14,color="#1a5c8a"),
            height=260, margin=dict(t=40,b=10,l=10,r=10),
            legend=dict(orientation="h",y=-0.05),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig2 = go.Figure(go.Bar(x=cats_labels, y=cats_vals, marker_color=colors_bar))
        fig2.update_layout(title="고장구분별 현황",
            title_font=dict(size=14,color="#1a5c8a"),
            height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="5G",  x=cats_labels, y=list(stats['cats5'].values()),  marker_color="#4da6e8"))
        fig3.add_trace(go.Bar(name="LTE", x=cats_labels, y=list(stats['catslte'].values()), marker_color="#f5a623"))
        fig3.update_layout(title="5G / LTE 고장구분 비교",
            title_font=dict(size=14,color="#1a5c8a"),
            barmode="group", height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            legend=dict(orientation="h",y=1.1),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        fig4 = go.Figure(go.Bar(
            x=stats['sub'].values.tolist(),
            y=stats['sub'].index.tolist(),
            orientation="h", marker_color="#4da6e8",
        ))
        fig4.update_layout(title="장비 중분류별 고장",
            title_font=dict(size=14,color="#1a5c8a"),
            height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            yaxis=dict(showgrid=False,autorange="reversed"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig4, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        fig5 = go.Figure(go.Scatter(
            x=stats['month_labels'], y=stats['month_vals'],
            mode="lines+markers",
            line=dict(color="#4da6e8",width=2.5),
            fill="tozeroy", fillcolor="rgba(77,166,232,0.12)",
            marker=dict(size=8,color="#4da6e8"),
        ))
        fig5.update_layout(title="월별 고장 발생 추이",
            title_font=dict(size=14,color="#1a5c8a"),
            height=240, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig5, use_container_width=True)

    with c6:
        fig6 = go.Figure(go.Bar(
            x=stats['area'].values.tolist(),
            y=stats['area'].index.tolist(),
            orientation="h", marker_color="#a78bfa",
        ))
        fig6.update_layout(title="시군구별 고장 현황 (Top 10)",
            title_font=dict(size=14,color="#1a5c8a"),
            height=240, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            yaxis=dict(showgrid=False,autorange="reversed"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig6, use_container_width=True)

# ══ TAB2 금일 알람 ═════════════════════════════════════════════════
with tab2:
    unfix_cnt = len(df_batch[df_batch['상태']=='미복구'])
    fix_cnt   = len(df_batch[df_batch['상태']=='복구'])
    st.markdown(f"""
    <h4 style="color:#1a5c8a; margin-bottom:12px;">
      금일 알람 &nbsp;
      <span style="background:#ffe8e8;color:#c0392b;font-size:11px;border-radius:12px;padding:2px 10px;font-weight:700;">미복구 {unfix_cnt}건</span>
      <span style="background:#d6f5e8;color:#1a7a50;font-size:11px;border-radius:12px;padding:2px 10px;font-weight:700;margin-left:6px;">복구 {fix_cnt}건</span>
      <span style="font-size:11px;color:#a0bcd4;font-weight:400;margin-left:8px;">기준일: {latest_date}</span>
    </h4>
    """, unsafe_allow_html=True)

    disp_batch = df_batch[[
        '상태','발생시각','장비명','Port','시스템','시군구',
        '고장구분','고장구분(중분류)','다발','복구/미복구 상세내역'
    ]].copy()
    disp_batch.columns = ['상태','발생일시','장비명','Port','시스템','시군구','고장구분','중분류','다발','복구사유/상세내역']

    st.dataframe(
        disp_batch.style.map(
            lambda v: ("background:#ffe8e8;color:#c0392b;font-weight:bold;" if v=="미복구"
                       else "background:#d6f5e8;color:#1a7a50;font-weight:bold;" if v=="복구" else ""),
            subset=["상태"]
        ),
        use_container_width=True, height=500
    )

# ══ TAB3 전체 RAW 데이터 ═══════════════════════════════════════════
with tab3:
    st.markdown('<h4 style="color:#1a5c8a; margin-bottom:12px;">전체 고장 RAW 데이터</h4>', unsafe_allow_html=True)

    col_s, col_f1, col_f2, col_f3, col_f4 = st.columns([3,1,1,1,1])
    with col_s:
        sq = st.text_input("", placeholder="🔍  Port, 장비명, 시군구, 복구사유 검색...", label_visibility="collapsed", key="raw_search")
    btn_all   = col_f1.button("전체",    key="rb_all")
    btn_unfix = col_f2.button("미복구만", key="rb_unfix")
    btn_5g    = col_f3.button("5G",      key="rb_5g")
    btn_lte   = col_f4.button("LTE",     key="rb_lte")

    if "rfilt" not in st.session_state: st.session_state.rfilt = "all"
    if btn_all:   st.session_state.rfilt = "all"
    if btn_unfix: st.session_state.rfilt = "미복구"
    if btn_5g:    st.session_state.rfilt = "5G"
    if btn_lte:   st.session_state.rfilt = "LTE"

    df_raw = df.copy()
    # 다발 추가
    df_raw['다발'] = df_raw['장비명'].map(dabal_map).apply(lambda x: f"다발 {x}회" if x > 1 else "-")

    if st.session_state.rfilt == "미복구":
        unfix_names = df_batch[df_batch['상태']=='미복구']['장비명'].tolist()
        df_raw = df_raw[df_raw['장비명'].isin(unfix_names)]
    elif st.session_state.rfilt == "5G":
        df_raw = df_raw[df_raw['시스템']=='5G']
    elif st.session_state.rfilt == "LTE":
        df_raw = df_raw[df_raw['시스템']=='LTE']

    if sq:
        q = sq.lower()
        df_raw = df_raw[df_raw.apply(
            lambda r: any(q in str(r[c]).lower() for c in ['Port','장비명','시군구','복구/미복구 상세내역']), axis=1
        )]

    disp_raw = df_raw[[
        '발생시각','장비명','Port','시스템','시군구',
        '고장구분','고장구분(중분류)','다발','복구/미복구 상세내역'
    ]].copy()
    disp_raw.columns = ['발생일시','장비명','Port','시스템','시군구','고장구분','중분류','다발','복구사유/상세내역']

    st.caption(f"총 {len(disp_raw)}건 (필터: {st.session_state.rfilt})")
    st.dataframe(disp_raw, use_container_width=True, height=560)

# ══ TAB4 중계기·MIBOS ══════════════════════════════════════════════
with tab4:
    st.markdown('<h4 style="color:#1a5c8a; margin-bottom:12px;">중계기 및 MIBOS 알람 현황</h4>', unsafe_allow_html=True)
    if 'rep' in data and len(data['rep']) > 0:
        df_rep = data['rep']
        legacy_n = len(df_rep[df_rep.iloc[:,0].astype(str).str.contains('Legacy', na=False)])
        mibos_n  = len(df_rep[df_rep.iloc[:,0].astype(str).str.contains('MIBOS', na=False)])
        c_rep = st.columns(4)
        for col, (v, lbl, clr) in zip(c_rep, [
            (str(len(df_rep)), "전체 알람",     "#4da6e8"),
            (str(legacy_n),   "Legacy 중계기", "#e05c5c"),
            (str(mibos_n),    "MIBOS",         "#2ecc87"),
            ("-",             "CDMA+WCDMA",    "#f5a623"),
        ]):
            col.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{clr};">{v}</div><div class="kpi-label">{lbl}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_rep, use_container_width=True, height=480)
    else:
        st.markdown('<div class="empty-bar">📭 현재 중계기·MIBOS 알람 데이터가 없습니다</div>', unsafe_allow_html=True)

# ══ TAB5 gREMS ════════════════════════════════════════════════════
with tab5:
    st.markdown('<h4 style="color:#1a5c8a; margin-bottom:12px;">gREMS 알람 현황</h4>', unsafe_allow_html=True)
    if 'grems' in data and len(data['grems']) > 0:
        df_gr = data['grems']
        crit_n = len(df_gr[df_gr.iloc[:,0].astype(str) == 'Critical'])
        oos_n  = len(df_gr[df_gr.iloc[:,0].astype(str) == 'OOS'])
        c_gr = st.columns(3)
        for col, (v, lbl, clr) in zip(c_gr, [
            (str(len(df_gr)), "전체 알람", "#4da6e8"),
            (str(crit_n),     "Critical",  "#e05c5c"),
            (str(oos_n),      "OOS",        "#f5a623"),
        ]):
            col.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{clr};">{v}</div><div class="kpi-label">{lbl}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        def style_grade(v):
            if v == 'Critical': return "background:#ffe8e8;color:#c0392b;font-weight:bold;"
            if v == 'OOS':      return "background:#fff0d6;color:#b45309;font-weight:bold;"
            return ""

        st.dataframe(
            df_gr.style.map(style_grade, subset=[df_gr.columns[0]]),
            use_container_width=True, height=480
        )
    else:
        st.markdown('<div class="empty-bar">📭 현재 gREMS 알람 데이터가 없습니다</div>', unsafe_allow_html=True)

# ══ TAB6 기타 알람 현황 ════════════════════════════════════════════
with tab6:
    st.markdown('<h4 style="color:#1a5c8a; margin-bottom:16px;">기타 알람 현황</h4>', unsafe_allow_html=True)

    extra_sheets = {
        'RMS_A망 미복구':    '📡 RMS A망 미복구',
        'RMS_DACS 미복구':   '📡 RMS DACS 미복구',
        'RMS_통합RCU미복구': '📡 RMS 통합RCU 미복구',
        'NO-CALL현황':       '📞 NO-CALL 현황',
        'MIBOS AMP 미사용':  '🔧 MIBOS AMP 미사용',
    }

    for sheet_key, sheet_label in extra_sheets.items():
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#1a5c8a;margin:16px 0 8px 0;">{sheet_label}</div>', unsafe_allow_html=True)
        if sheet_key in data and data[sheet_key] is not None and len(data[sheet_key]) > 0:
            df_extra = data[sheet_key]
            st.caption(f"총 {len(df_extra)}건")
            st.dataframe(df_extra, use_container_width=True, height=300)
        else:
            st.markdown('<div class="empty-bar">📭 현재 대상 없음</div>', unsafe_allow_html=True)

# ── 푸터 ──────────────────────────────────────────────────────────
st.markdown(f"""
<hr style="border:none; border-top:1px solid #d8edf9; margin-top:24px;">
<div style="text-align:center; font-size:10px; color:#a0bcd4; padding-bottom:8px;">
  진주품질개선팀 고장 현황 대시보드 | 기준일 {latest_date} | 파일: {uploaded.name}
</div>
""", unsafe_allow_html=True)
