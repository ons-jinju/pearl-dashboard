import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import gspread
from google.oauth2.service_account import Credentials

# ── Google Sheets 연결 ────────────────────────────────────────────
@st.cache_resource
def get_sheet():
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(st.secrets["SHEET_ID"]).sheet1
        return sheet
    except Exception:
        return None

def save_to_sheet(port, 장비명, 고장구분, 중분류, teams, 상세내역):
    try:
        sheet = get_sheet()
        if sheet is None: return False
        records = sheet.get_all_records()
        for i, r in enumerate(records):
            if r.get('Port') == port:
                sheet.update(f'A{i+2}:F{i+2}',
                    [[port, 장비명, 고장구분, 중분류, teams, 상세내역]])
                return True
        sheet.append_row([port, 장비명, 고장구분, 중분류, teams, 상세내역])
        return True
    except Exception:
        return False

def save_rep_to_sheet(중계기명, 작업내용):
    try:
        sheet = get_sheet()
        if sheet is None: return False
        key = f'[중계기]{중계기명}'
        records = sheet.get_all_records()
        for i, r in enumerate(records):
            if r.get('Port') == key:
                sheet.update(f'A{i+2}:F{i+2}',
                    [[key, 중계기명, '', '', '', 작업내용]])
                return True
        sheet.append_row([key, 중계기명, '', '', '', 작업내용])
        return True
    except Exception:
        return False

def load_from_sheet():
    try:
        sheet = get_sheet()
        if sheet is None: return {}, {}
        records = sheet.get_all_records()
        batch_data, rep_data = {}, {}
        for r in records:
            port = r.get('Port', '')
            if port.startswith('[중계기]'):
                rep_data[port.replace('[중계기]','')] = r.get('복구/미복구 상세내역','')
            else:
                batch_data[port] = {
                    '고장구분':             r.get('고장구분',''),
                    '고장구분(중분류)':     r.get('고장구분(중분류)',''),
                    'Teams 등록여부':       r.get('Teams 등록여부',''),
                    '복구/미복구 상세내역': r.get('복구/미복구 상세내역',''),
                }
        return batch_data, rep_data
    except Exception:
        return {}, {}

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
    background: #fff; border-radius: 16px; padding: 14px 8px; text-align: center;
    box-shadow: 0 2px 10px rgba(100,160,220,0.12); margin-bottom: 4px;
}
.kpi-val  { font-size: 26px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.kpi-label{ font-size: 11px; color: #7aabcc; margin-top: 3px; }
.info-bar {
    background: #f0f8ff; border-left: 3px solid #4da6e8; border-radius: 0 8px 8px 0;
    padding: 7px 14px; margin-bottom: 10px; font-size: 12px; color: #3a7cb0;
}
.rule-bar {
    background: #f0f8ff; border-left: 3px solid #4da6e8; border-radius: 0 8px 8px 0;
    padding: 8px 14px; margin-bottom: 12px; font-size: 11px; color: #3a7cb0; line-height: 1.9;
}
.empty-bar {
    background: #f8f8f8; border-left: 3px solid #ccc; border-radius: 0 8px 8px 0;
    padding: 12px 16px; font-size: 13px; color: #999; text-align: center;
}
.alarm-summary {
    background: #fff; border-radius: 12px; padding: 12px 18px;
    box-shadow: 0 2px 10px rgba(100,160,220,0.12); margin-bottom: 14px;
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.badge-red   { background:#ffe8e8; color:#c0392b; font-size:11px; border-radius:12px; padding:3px 11px; font-weight:700; margin:0 2px; display:inline-block; }
.badge-green { background:#d6f5e8; color:#1a7a50; font-size:11px; border-radius:12px; padding:3px 11px; font-weight:700; margin:0 2px; display:inline-block; }
.badge-orange{ background:#fff0d6; color:#b45309; font-size:11px; border-radius:12px; padding:3px 11px; font-weight:700; margin:0 2px; display:inline-block; }
.badge-blue  { background:#dbeeff; color:#1a5c8a; font-size:11px; border-radius:12px; padding:3px 11px; font-weight:700; margin:0 2px; display:inline-block; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#fff; border-bottom:1.5px solid #b8dcf5; padding:10px 0; margin-bottom:12px;">
  <span style="font-size:17px; font-weight:700; color:#1a5c8a;">📡 진주품질개선팀 &nbsp; 고장 현황 대시보드</span>
</div>
""", unsafe_allow_html=True)

FILE_NAME = "26년_진주품질개선팀_고장_RAW_DATA.xlsx"
FILE_PATH = os.path.join(os.path.dirname(__file__), FILE_NAME)

if not os.path.exists(FILE_PATH):
    st.error(f"⚠️ 파일을 찾을 수 없습니다: `{FILE_NAME}`")
    st.stop()

@st.cache_data(ttl=300)
def load_all(filepath):
    xls    = pd.ExcelFile(filepath)
    sheets = xls.sheet_names
    data   = {}

    df = pd.read_excel(filepath, sheet_name='5G_LTE OOS_진주')
    df['발생시각_dt'] = pd.to_datetime(df['발생시각'], errors='coerce')
    df['발생일자']   = df['발생시각_dt'].dt.date
    df['월']         = df['발생시각_dt'].dt.month
    data['main'] = df

    for s in ['중계기 및 MIBOS 알람', 'gREMS',
              'RMS_A망 미복구', 'RMS_DACS 미복구', 'RMS_통합RCU미복구',
              'NO-CALL현황', 'MIBOS AMP 미사용']:
        if s in sheets:
            d = pd.read_excel(filepath, sheet_name=s)
            # 중계기 시트에 작업내용 컬럼 없으면 추가
            if s == '중계기 및 MIBOS 알람' and '작업내용' not in d.columns:
                d['작업내용'] = ''
            data[s] = d

    return data

data = load_all(FILE_PATH)
df   = data['main']

# ── 금일 알람 로직 ────────────────────────────────────────────────
def calc_batch(df):
    df = df.copy()
    df['A열날짜'] = pd.to_datetime(df.iloc[:, 0], errors='coerce').dt.date

    # 최신 배치일: A열 기준 (12월31일 이상값 제외)
    df_valid    = df[df['A열날짜'] != pd.Timestamp('2026-12-31').date()]
    latest_date = df_valid['A열날짜'].max()
    df_new      = df[df['A열날짜'] == latest_date].copy()

    # 복구 판단
    def judge_status(row):
        gj     = str(row.get('고장구분', '')).strip()
        detail = str(row.get('복구/미복구 상세내역', '')).strip()
        if pd.isna(row.get('고장구분')):       return '미복구'
        if '복구' in gj or '복구' in detail:  return '복구'
        if gj in ['', ' ']:                    return '미복구'
        return '미복구'

    df_new['상태'] = df_new.apply(judge_status, axis=1)

    # 점검중 / 신규 구분
    # 점검중 = 미복구 중 복구사유/상세내역에 내용 있는 것
    # 신규   = 미복구 중 복구사유/상세내역 비어있는 것
    def detail_type(row):
        if row['상태'] == '복구': return '복구'
        detail = str(row.get('복구/미복구 상세내역', '')).strip()
        if detail and detail != 'nan': return '점검중'
        return '신규'

    df_new['구분'] = df_new.apply(detail_type, axis=1)

    # 다발: 동일 Port, 발생시각 다른 것 (전체 기준)
    df_all_dedup = df.drop_duplicates(subset=['Port', '발생시각'])
    dabal_map    = df_all_dedup.groupby('Port').size().to_dict()
    df_new['다발횟수'] = df_new['Port'].map(dabal_map)
    df_new['다발']     = df_new['다발횟수'].apply(lambda x: f"다발 {x}회" if x > 1 else "-")

    return df_new, latest_date, dabal_map

df_batch, latest_date, dabal_map = calc_batch(df)

# ── 통계 ─────────────────────────────────────────────────────────
def get_stats(df):
    df_dedup    = df.drop_duplicates(subset=['Port', '발생시각'])
    total       = len(df_dedup)
    unfix       = len(df_batch[df_batch['상태'] == '미복구'])
    fix         = total - unfix
    dabal_total = sum(1 for v in dabal_map.values() if v > 1)
    g5          = len(df_dedup[df_dedup['시스템'] == '5G'])
    lte         = len(df_dedup[df_dedup['시스템'] == 'LTE'])

    cats_labels = ['복구','Unit','BP','재발생','점검중','기타']
    def get_cats(d):
        return [
            len(d[d['고장구분'].str.strip().str.lower() == '복구']),
            len(d[d['고장구분'].str.strip().str.upper() == 'UNIT']),
            len(d[d['고장구분'].str.strip().str.upper() == 'BP']),
            len(d[d['고장구분'].str.strip() == '재발생']),
            len(d[d['고장구분'].str.strip() == '점검중']),
            len(d[~d['고장구분'].str.strip().str.lower().isin(['복구','unit','bp','재발생','점검중',''])]),
        ]

    cats_vals    = get_cats(df_dedup)
    cats5_vals   = get_cats(df_dedup[df_dedup['시스템'] == '5G'])
    catslte_vals = get_cats(df_dedup[df_dedup['시스템'] == 'LTE'])
    sub          = df_dedup['고장구분(중분류)'].value_counts().head(8)
    month_grp    = df_dedup.groupby('월').size().sort_index()
    month_labels = [f"{int(m)}월" for m in month_grp.index]
    month_vals   = month_grp.values.tolist()
    area         = df_dedup['시군구'].value_counts().head(10)

    return dict(total=total, unfix=unfix, fix=fix,
                dabal_total=dabal_total, g5=g5, lte=lte,
                cats_labels=cats_labels,
                cats_vals=cats_vals, cats5_vals=cats5_vals, catslte_vals=catslte_vals,
                sub=sub, month_labels=month_labels, month_vals=month_vals, area=area)

stats = get_stats(df)

# 배지 카운트
unfix_n = len(df_batch[df_batch['상태'] == '미복구'])
fix_n   = len(df_batch[df_batch['상태'] == '복구'])
jgm_n   = len(df_batch[df_batch['구분'] == '점검중'])
new_n   = len(df_batch[df_batch['구분'] == '신규'])

# 중계기/MIBOS/gREMS
df_rep  = data.get('중계기 및 MIBOS 알람', pd.DataFrame())
df_gr   = data.get('gREMS', pd.DataFrame())
legacy_n = len(df_rep[df_rep.iloc[:,0].astype(str).str.contains('Legacy', na=False)]) if len(df_rep) > 0 else 0
mibos_n  = len(df_rep[df_rep.iloc[:,0].astype(str).str.contains('MIBOS',  na=False)]) if len(df_rep) > 0 else 0
grems_n  = len(df_gr)

# ── 탭: 금일알람 → RAW → 대시보드 → 중계기+gREMS → 기타 ─────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔔 금일 알람",
    "📋 전체 RAW 데이터",
    "📊 대시보드",
    "📡 중계기·MIBOS·gREMS",
    "🔔 기타 알람 현황",
])

# ══ TAB1 금일 알람 ═════════════════════════════════════════════════
with tab1:
    st.markdown(f"""
    <div class="alarm-summary">
      <span style="font-size:13px;font-weight:700;color:#1a5c8a;">금일 알람</span>
      <span style="font-size:11px;color:#a0bcd4;">기준일: {latest_date}</span>
      &nbsp;
      <span class="badge-red">미복구 {unfix_n}건</span>
      <span class="badge-orange">점검중 {jgm_n}건</span>
      <span class="badge-blue">신규 {new_n}건</span>
      <span class="badge-green">복구 {fix_n}건</span>
    </div>
    """, unsafe_allow_html=True)

    # session_state 초기화 (AL~AP 수기입력 저장용)
    if 'batch_edits' not in st.session_state:
        st.session_state.batch_edits = {}

    disp = df_batch[[
        '구분','발생시각','장비명','Port','시스템','시군구',
        '고장구분','고장구분(중분류)','다발','복구/미복구 상세내역'
    ]].copy()
    disp.columns = ['구분','발생일시','장비명','Port','시스템','시군구',
                    '고장구분','중분류','다발','복구사유/상세내역']

    def style_batch(v):
        if v == '미복구': return "background:#ffe8e8;color:#c0392b;font-weight:bold;"
        if v == '점검중': return "background:#fff0d6;color:#b45309;font-weight:bold;"
        if v == '신규':   return "background:#dbeeff;color:#1a5c8a;font-weight:bold;"
        if v == '복구':   return "background:#d6f5e8;color:#1a7a50;font-weight:bold;"
        return ""

    st.dataframe(
        disp.style.map(style_batch, subset=["구분"]),
        use_container_width=True, height=300
    )

    # ── 수기 입력 섹션 (AL~AP열) ────────────────────────────────
    st.markdown('<div style="font-size:14px;font-weight:700;color:#1a5c8a;margin:16px 0 8px 0;">✏️ 작업 내용 입력</div>', unsafe_allow_html=True)
    st.caption("국소를 선택하고 작업 내용을 입력하세요. 저장하면 Google Sheets에 자동 저장됩니다.")

    # Google Sheets에서 기존 입력값 불러오기
    sheet_batch, sheet_rep = load_from_sheet()

    # 국소 선택
    port_list = df_batch['Port'].tolist()
    name_list = df_batch['장비명'].tolist()
    options   = [f"{p} | {n}" for p, n in zip(port_list, name_list)]

    selected = st.selectbox("📍 국소 선택", options, key="sel_port")

    if selected:
        sel_port = selected.split(" | ")[0]
        sel_idx  = df_batch[df_batch['Port'] == sel_port].index[0]
        sel_name = df_batch.loc[sel_idx, '장비명']

        # Sheets 저장값 우선, 없으면 엑셀 원본값
        saved = sheet_batch.get(sel_port, {})

        col_a, col_b = st.columns(2)
        with col_a:
            gj = st.text_input("고장구분 (AL)",
                value=saved.get('고장구분') or (str(df_batch.loc[sel_idx,'고장구분']) if pd.notna(df_batch.loc[sel_idx,'고장구분']) else ""),
                key=f"gj_{sel_port}")
            gj_mid = st.text_input("고장구분(중분류) (AM)",
                value=saved.get('고장구분(중분류)') or (str(df_batch.loc[sel_idx,'고장구분(중분류)']) if pd.notna(df_batch.loc[sel_idx,'고장구분(중분류)']) else ""),
                key=f"gjm_{sel_port}")
            unit_type = st.text_input("Unit Type (AN)",
                value=str(df_batch.loc[sel_idx,'Unit Type']) if pd.notna(df_batch.loc[sel_idx,'Unit Type']) else "",
                key=f"ut_{sel_port}")
        with col_b:
            teams = st.text_input("Teams 등록여부 (AO)",
                value=saved.get('Teams 등록여부') or (str(df_batch.loc[sel_idx,'Teams 등록여부']) if pd.notna(df_batch.loc[sel_idx,'Teams 등록여부']) else ""),
                key=f"tm_{sel_port}")
            detail = st.text_area("복구/미복구 상세내역 (AP)",
                value=saved.get('복구/미복구 상세내역') or (str(df_batch.loc[sel_idx,'복구/미복구 상세내역']) if pd.notna(df_batch.loc[sel_idx,'복구/미복구 상세내역']) else ""),
                height=120,
                key=f"dt_{sel_port}")

        if st.button("💾 저장 (Google Sheets)", key="save_batch", use_container_width=True):
            ok = save_to_sheet(sel_port, sel_name, gj, gj_mid, teams, detail)
            if ok:
                st.success(f"✅ {sel_port} Google Sheets 저장 완료!")
                st.cache_resource.clear()
            else:
                st.error("❌ 저장 실패. 잠시 후 다시 시도해주세요.")

    # 저장된 항목 요약 (Google Sheets에서 불러오기)
    if sheet_batch:
        st.markdown('<div style="font-size:13px;font-weight:700;color:#1a5c8a;margin:12px 0 6px 0;">📋 입력 완료 목록 (Google Sheets)</div>', unsafe_allow_html=True)
        summary_rows = []
        for p, v in sheet_batch.items():
            summary_rows.append({
                'Port': p,
                '고장구분': v.get('고장구분',''),
                '중분류': v.get('고장구분(중분류)',''),
                '복구/미복구 상세내역': v.get('복구/미복구 상세내역',''),
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, height=200)

# ══ TAB2 전체 RAW ══════════════════════════════════════════════════
with tab2:
    st.markdown('<h4 style="color:#1a5c8a;margin-bottom:12px;">전체 고장 RAW 데이터</h4>', unsafe_allow_html=True)

    c_s, c1, c2, c3, c4 = st.columns([3,1,1,1,1])
    with c_s:
        sq = st.text_input("", placeholder="🔍  Port, 장비명, 시군구, 복구사유 검색...",
                           label_visibility="collapsed", key="raw_search")
    btn_all   = c1.button("전체",    key="rb_all")
    btn_unfix = c2.button("미복구만", key="rb_unfix")
    btn_5g    = c3.button("5G",      key="rb_5g")
    btn_lte   = c4.button("LTE",     key="rb_lte")

    if "rfilt" not in st.session_state: st.session_state.rfilt = "all"
    if btn_all:   st.session_state.rfilt = "all"
    if btn_unfix: st.session_state.rfilt = "미복구"
    if btn_5g:    st.session_state.rfilt = "5G"
    if btn_lte:   st.session_state.rfilt = "LTE"

    df_raw = df.copy()
    df_raw['다발'] = df_raw['Port'].map(dabal_map).apply(lambda x: f"다발 {x}회" if x > 1 else "-")

    if st.session_state.rfilt == "미복구":
        up = df_batch[df_batch['상태']=='미복구']['Port'].tolist()
        df_raw = df_raw[df_raw['Port'].isin(up)]
    elif st.session_state.rfilt == "5G":
        df_raw = df_raw[df_raw['시스템']=='5G']
    elif st.session_state.rfilt == "LTE":
        df_raw = df_raw[df_raw['시스템']=='LTE']

    if sq:
        q = sq.lower()
        df_raw = df_raw[df_raw.apply(
            lambda r: any(q in str(r[c]).lower()
                         for c in ['Port','장비명','시군구','복구/미복구 상세내역']), axis=1)]

    disp_raw = df_raw[['발생시각','장비명','Port','시스템','시군구',
                        '고장구분','고장구분(중분류)','다발','복구/미복구 상세내역']].copy()
    disp_raw.columns = ['발생일시','장비명','Port','시스템','시군구',
                        '고장구분','중분류','다발','복구사유/상세내역']

    st.caption(f"총 {len(disp_raw)}건 (필터: {st.session_state.rfilt})")
    st.dataframe(disp_raw, use_container_width=True, height=560)

# ══ TAB3 대시보드 ══════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div class="info-bar">📅 기준일: <b>{latest_date}</b></div>
    <div class="rule-bar">
    ① A열 배치일 기준 최신일 = 금일 알람 &nbsp;|&nbsp;
    ② 동일 Port+발생시각 동일 = 다발알람 1건 &nbsp;|&nbsp;
    ③ 고장구분/상세내역에 복구 → 복구, 그 외 → 미복구 &nbsp;|&nbsp;
    ④ 최신배치에 없는 Port → 자동복구
    </div>
    """, unsafe_allow_html=True)

    kpi_list = [
        (str(stats['total']),       "실 고장 건수",  "#4da6e8"),
        (str(stats['unfix']),       "미복구",        "#e05c5c"),
        (str(stats['fix']),         "복구 완료",     "#2ecc87"),
        (str(stats['dabal_total']), "다발알람 국소", "#e65100"),
        (str(stats['g5']),          "5G 고장",       "#4da6e8"),
        (str(stats['lte']),         "LTE 고장",      "#f5a623"),
    ]
    kcols = st.columns(6)
    for col, (val, label, color) in zip(kcols, kpi_list):
        col.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{color};">{val}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cb = ["#4da6e8","#f5a623","#a78bfa","#60a5fa","#34d399","#f87171"]

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        fig = go.Figure(go.Pie(
            labels=["복구","미복구"], values=[stats['fix'],stats['unfix']], hole=0.65,
            marker=dict(colors=["#2ecc87","#f87171"]), textinfo="label+value", textfont_size=13))
        fig.update_layout(title=f"복구 / 미복구 현황 (전체 {stats['total']}건)",
            title_font=dict(size=14,color="#1a5c8a"), height=260,
            margin=dict(t=40,b=10,l=10,r=10), legend=dict(orientation="h",y=-0.05),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        fig2 = go.Figure(go.Bar(x=stats['cats_labels'], y=stats['cats_vals'], marker_color=cb))
        fig2.update_layout(title="고장구분별 현황", title_font=dict(size=14,color="#1a5c8a"),
            height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig2, use_container_width=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="5G",  x=stats['cats_labels'], y=stats['cats5_vals'],   marker_color="#4da6e8"))
        fig3.add_trace(go.Bar(name="LTE", x=stats['cats_labels'], y=stats['catslte_vals'], marker_color="#f5a623"))
        fig3.update_layout(title="5G / LTE 고장구분 비교", title_font=dict(size=14,color="#1a5c8a"),
            barmode="group", height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            legend=dict(orientation="h",y=1.1), paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig3, use_container_width=True)

    with r2c2:
        fig4 = go.Figure(go.Bar(
            x=stats['sub'].values.tolist(), y=stats['sub'].index.tolist(),
            orientation="h", marker_color="#4da6e8"))
        fig4.update_layout(title="장비 중분류별 고장", title_font=dict(size=14,color="#1a5c8a"),
            height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            yaxis=dict(showgrid=False,autorange="reversed"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig4, use_container_width=True)

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        fig5 = go.Figure(go.Scatter(
            x=stats['month_labels'], y=stats['month_vals'], mode="lines+markers",
            line=dict(color="#4da6e8",width=2.5), fill="tozeroy",
            fillcolor="rgba(77,166,232,0.12)", marker=dict(size=8,color="#4da6e8")))
        fig5.update_layout(title="월별 고장 발생 추이", title_font=dict(size=14,color="#1a5c8a"),
            height=240, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig5, use_container_width=True)

    with r3c2:
        fig6 = go.Figure(go.Bar(
            x=stats['area'].values.tolist(), y=stats['area'].index.tolist(),
            orientation="h", marker_color="#a78bfa"))
        fig6.update_layout(title="시군구별 고장 현황 (Top 10)", title_font=dict(size=14,color="#1a5c8a"),
            height=240, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            yaxis=dict(showgrid=False,autorange="reversed"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig6, use_container_width=True)

# ══ TAB4 중계기·MIBOS·gREMS 통합 ══════════════════════════════════
with tab4:
    st.markdown(f"""
    <div class="alarm-summary">
      <span style="font-size:13px;font-weight:700;color:#1a5c8a;">알람 현황</span>
      &nbsp;
      <span class="badge-orange">LEGACY 중계기 {legacy_n}</span>
      <span class="badge-blue">MIBOS {mibos_n}</span>
      <span class="badge-red">gREMS {grems_n}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:14px;font-weight:700;color:#1a5c8a;margin:8px 0 8px 0;">📡 중계기 및 MIBOS 알람</div>', unsafe_allow_html=True)
    if len(df_rep) > 0:
        st.dataframe(
            df_rep.style.map(
                lambda v: ("background:#fff0d6;color:#b45309;" if "Legacy" in str(v)
                           else "background:#dbeeff;color:#1a5c8a;" if "MIBOS" in str(v) else ""),
                subset=[df_rep.columns[0]]
            ).map(
                lambda v: "color:#e05c5c;font-weight:bold;" if isinstance(v, int) and v >= 3 else "",
                subset=[df_rep.columns[1]]
            ),
            use_container_width=True, height=300
        )

        # ── 중계기 작업내용 수기 입력 (J열) ─────────────────────
        st.markdown('<div style="font-size:13px;font-weight:700;color:#1a5c8a;margin:12px 0 6px 0;">✏️ 작업내용 입력 (J열)</div>', unsafe_allow_html=True)

        rep_options = [f"{r['중계기명']} | {r['망구분']}" for _, r in df_rep.iterrows()]
        sel_rep = st.selectbox("📍 중계기 선택", rep_options, key="sel_rep")

        if sel_rep:
            sel_name = sel_rep.split(" | ")[0]
            # Sheets 저장값 우선, 없으면 엑셀 원본값
            existing = df_rep[df_rep['중계기명'] == sel_name]['작업내용'].values
            default_val = sheet_rep.get(sel_name) or (str(existing[0]) if len(existing) > 0 and pd.notna(existing[0]) else "")

            rep_detail = st.text_area("작업내용",
                value=default_val,
                height=100,
                key=f"rep_{sel_name}")

            if st.button("💾 작업내용 저장 (Google Sheets)", key="save_rep", use_container_width=True):
                ok = save_rep_to_sheet(sel_name, rep_detail)
                if ok:
                    st.success(f"✅ {sel_name} Google Sheets 저장 완료!")
                    st.cache_resource.clear()
                else:
                    st.error("❌ 저장 실패. 잠시 후 다시 시도해주세요.")

        # 저장된 항목 요약 (Google Sheets)
        if sheet_rep:
            st.markdown('<div style="font-size:13px;font-weight:700;color:#1a5c8a;margin:10px 0 4px 0;">📋 입력 완료 목록</div>', unsafe_allow_html=True)
            rep_summary = [{'중계기명': k, '작업내용': v} for k, v in sheet_rep.items()]
            st.dataframe(pd.DataFrame(rep_summary), use_container_width=True, height=150)
    else:
        st.markdown('<div class="empty-bar">📭 현재 중계기·MIBOS 알람 데이터가 없습니다</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;font-weight:700;color:#1a5c8a;margin:8px 0 8px 0;">🏢 gREMS 알람</div>', unsafe_allow_html=True)
    if len(df_gr) > 0:
        st.dataframe(
            df_gr.style.map(
                lambda v: ("background:#ffe8e8;color:#c0392b;font-weight:bold;" if v == 'Critical'
                           else "background:#fff0d6;color:#b45309;font-weight:bold;" if v == 'OOS' else ""),
                subset=[df_gr.columns[0]]
            ),
            use_container_width=True, height=300
        )
    else:
        st.markdown('<div class="empty-bar">📭 현재 gREMS 알람 데이터가 없습니다</div>', unsafe_allow_html=True)

# ══ TAB5 기타 알람 현황 ════════════════════════════════════════════
with tab5:
    st.markdown('<h4 style="color:#1a5c8a;margin-bottom:16px;">기타 알람 현황</h4>', unsafe_allow_html=True)

    for sheet_key, sheet_label in {
        'RMS_A망 미복구':    '📡 RMS A망 미복구',
        'RMS_DACS 미복구':   '📡 RMS DACS 미복구',
        'RMS_통합RCU미복구': '📡 RMS 통합RCU 미복구',
        'NO-CALL현황':       '📞 NO-CALL 현황',
        'MIBOS AMP 미사용':  '🔧 MIBOS AMP 미사용',
    }.items():
        st.markdown(f'<div style="font-size:14px;font-weight:700;color:#1a5c8a;margin:16px 0 8px 0;">{sheet_label}</div>', unsafe_allow_html=True)
        df_ex = data.get(sheet_key)
        if df_ex is not None and len(df_ex) > 0:
            st.caption(f"총 {len(df_ex)}건")
            st.dataframe(df_ex, use_container_width=True, height=280)
        else:
            st.markdown('<div class="empty-bar">📭 현재 대상 없음</div>', unsafe_allow_html=True)

st.markdown(f"""
<hr style="border:none;border-top:1px solid #d8edf9;margin-top:24px;">
<div style="text-align:center;font-size:10px;color:#a0bcd4;padding-bottom:8px;">
  진주품질개선팀 고장 현황 대시보드 | 기준일 {latest_date}
</div>
""", unsafe_allow_html=True)
