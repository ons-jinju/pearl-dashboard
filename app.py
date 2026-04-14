import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
.kpi-val { font-size: 28px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
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
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── 데이터 ────────────────────────────────────────────────────────
C = {
    "5g_vals":  [139, 11, 32, 9, 3, 9],
    "lte_vals": [149, 18,  2,15, 4, 2],
    "sub_labels": ["AAU","RRU","MUX","SFP","정류기","PRU","공중선","전송선로"],
    "sub_vals":   [34, 13, 7, 4, 2, 2, 1, 1],
    "month_labels": ["1월","2월","3월","4월","12월"],
    "month_vals":   [111, 112, 103, 66, 11],
    "total":403,"unpaired":11,"paired":392,"g5":206,"lte":197,
    "dabal_total":111,"dabal_removed":481,
    "base_date":"2026-04-13","generated":"2026-04-14 10:57",
    "batch_fix":0,"batch_unfix":11,
}

BATCH = [
    {"상태":"미복구","Port":"jinju-hadae-QD3_07","장비명":"(고압)(경계)진주하대3LRRU_F5","발생일시":"2026-04-13 22:27","고장구분":"Unit","중분류":"RRU","다발":"-","복구사유/상세내역":"RRU 불량","시스템":"LTE","시군구":"진주시","알람등급":15},
    {"상태":"미복구","Port":"jinju-hadae-QD3_27","장비명":"(고압)(경계)진주하대3LRRU_F5","발생일시":"2026-04-13 22:27","고장구분":"Unit","중분류":"RRU","다발":"-","복구사유/상세내역":"RRU 불량","시스템":"LTE","시군구":"진주시","알람등급":16},
    {"상태":"미복구","Port":"kn-hadong-cheongam4-GX01_05","장비명":"(공동)하동묵계5AAU_1","발생일시":"2026-04-13 14:25","고장구분":"BP","중분류":"AAU","다발":"-","복구사유/상세내역":"AAU 불량","시스템":"5G","시군구":"하동군","알람등급":26},
    {"상태":"미복구","Port":"kn-hadong-geumseong3-GX14_00","장비명":"(공동)하동궁항6AAU_3","발생일시":"2026-04-13 09:57","고장구분":"Unit","중분류":"정류기","다발":"-","복구사유/상세내역":"정류기 불량","시스템":"5G","시군구":"하동군","알람등급":35},
    {"상태":"미복구","Port":"sacheon-sanam-NX01_43","장비명":"(공동)사천화전2LRRU","발생일시":"2026-04-12 01:31","고장구분":"Unit","중분류":"RRU","다발":"다발 3회","복구사유/상세내역":"RRU 불량","시스템":"LTE","시군구":"사천시","알람등급":62},
    {"상태":"미복구","Port":"kn-sacheon-donggeum-GX07_01","장비명":"사천갑룡사AAU_2","발생일시":"2026-04-10 20:49","고장구분":"Unit","중분류":"AAU","다발":"다발 3회","복구사유/상세내역":"AAU 알람","시스템":"5G","시군구":"사천시","알람등급":78},
    {"상태":"미복구","Port":"namhaeyidongDA0_00","장비명":"(공동)남해무림2LRRU","발생일시":"2026-04-09 05:43","고장구분":" ","중분류":"-","다발":"-","복구사유/상세내역":"RRU 불량","시스템":"LTE","시군구":"남해군","알람등급":9},
    {"상태":"미복구","Port":"kn-hamyang-gyosan-GX22_06","장비명":"(공동)함양백연AAU_2","발생일시":"2026-04-06 09:05","고장구분":"BP","중분류":"AAU","다발":"다발 7회","복구사유/상세내역":"AAU 불량","시스템":"5G","시군구":"함양군","알람등급":82},
    {"상태":"미복구","Port":"kn-uiryeong-uiryeong-GX02_05","장비명":"(공동)의령동동7AAU_2","발생일시":"2026-04-02 09:24","고장구분":"BP","중분류":"AAU","다발":"다발 9회","복구사유/상세내역":"AAU 불량","시스템":"5G","시군구":"의령군","알람등급":54},
    {"상태":"미복구","Port":"hamyangohcheonQA0_10","장비명":"(공동)함양양백2LRRU_F2","발생일시":"2026-03-29 00:45","고장구분":"기타","중분류":"-","다발":"다발 2회","복구사유/상세내역":"한전 고장","시스템":"LTE","시군구":"함양군","알람등급":44},
    {"상태":"미복구","Port":"JinjujeongchonDB1_01","장비명":"(공동)(고_대통)진주신율5LRRUM","발생일시":"2026-03-22 19:31","고장구분":"UNIT","중분류":"-","다발":"다발 4회","복구사유/상세내역":"RRU 불량","시스템":"LTE","시군구":"진주시","알람등급":16},
]

ALL_DATA = [
    {"status":"미복구","port":"jinju-hadae-QD3_07","name":"(고압)(경계)진주하대3LRRU_F5","date":"2026-04-13 22:27","type":"Unit","sub":"RRU","detail":"RRU 불량","system":"LTE","area":"진주시","grade":15,"dabal":1},
    {"status":"미복구","port":"jinju-hadae-QD3_27","name":"(고압)(경계)진주하대3LRRU_F5","date":"2026-04-13 22:27","type":"Unit","sub":"RRU","detail":"RRU 불량","system":"LTE","area":"진주시","grade":16,"dabal":1},
    {"status":"미복구","port":"kn-hadong-cheongam4-GX01_05","name":"(공동)하동묵계5AAU_1","date":"2026-04-13 14:25","type":"BP","sub":"AAU","detail":"AAU 불량","system":"5G","area":"하동군","grade":26,"dabal":1},
    {"status":"미복구","port":"kn-hadong-geumseong3-GX14_00","name":"(공동)하동궁항6AAU_3","date":"2026-04-13 09:57","type":"Unit","sub":"정류기","detail":"정류기 불량","system":"5G","area":"하동군","grade":35,"dabal":1},
    {"status":"복구","port":"jinju-hadae-QD3_27","name":"(고압)(경계)진주하대3LRRU_F5","date":"2026-04-13 05:35","type":"복구","sub":"RRU","detail":"RRU 교체 후 복구","system":"LTE","area":"진주시","grade":19,"dabal":2},
    {"status":"복구","port":"jinju-hadae-QD3_07","name":"(고압)(경계)진주하대3LRRU_F5","date":"2026-04-13 05:35","type":"복구","sub":"RRU","detail":"RRU 교체 후 복구","system":"LTE","area":"진주시","grade":18,"dabal":2},
    {"status":"복구","port":"kn-hadong-cheongam4-GX01_05","name":"(공동)하동묵계5AAU_1","date":"2026-04-13 04:49","type":"Unit","sub":"AAU","detail":"AAU 불량","system":"5G","area":"하동군","grade":20,"dabal":2},
    {"status":"미복구","port":"sacheon-sanam-NX01_43","name":"(공동)사천화전2LRRU","date":"2026-04-12 01:31","type":"Unit","sub":"RRU","detail":"RRU 불량","system":"LTE","area":"사천시","grade":62,"dabal":3},
    {"status":"복구","port":"kn-Jinju-sugok2-GX02_05","name":"(공동)하동종화마을AAU_2","date":"2026-04-11 10:31","type":"복구","sub":"-","detail":"정류기 2번 절체 후 복구.(1번 교체 예정)","system":"5G","area":"하동군","grade":68,"dabal":2},
    {"status":"복구","port":"kn-Jinju-sugok2-GX02_04","name":"(공동)하동종화마을AAU_1","date":"2026-04-11 10:31","type":"복구","sub":"-","detail":"정류기 2번 절체 후 복구.(1번 교체 예정)","system":"5G","area":"하동군","grade":67,"dabal":2},
    {"status":"미복구","port":"kn-sacheon-donggeum-GX07_01","name":"사천갑룡사AAU_2","date":"2026-04-10 20:49","type":"Unit","sub":"AAU","detail":"AAU 알람","system":"5G","area":"사천시","grade":78,"dabal":3},
    {"status":"복구","port":"hapcheon-hapcheon-DB0_01","name":"(공동)합천서산5LRRU","date":"2026-04-10 08:18","type":"복구","sub":"-","detail":"자동복구","system":"LTE","area":"합천군","grade":2,"dabal":1},
    {"status":"복구","port":"jinju-hadae-QD3_07","name":"(고압)(경계)진주하대3LRRU_F5","date":"2026-04-09 21:10","type":"Unit","sub":"RRU","detail":"RRU 불량","system":"LTE","area":"진주시","grade":40,"dabal":1},
    {"status":"복구","port":"jinju-hadae-QD3_27","name":"(고압)(경계)진주하대3LRRU_F5","date":"2026-04-09 21:10","type":"Unit","sub":"RRU","detail":"RRU 불량","system":"LTE","area":"진주시","grade":39,"dabal":1},
    {"status":"미복구","port":"namhaeyidongDA0_00","name":"(공동)남해무림2LRRU","date":"2026-04-09 05:43","type":" ","sub":"-","detail":"RRU 불량","system":"LTE","area":"남해군","grade":9,"dabal":1},
    {"status":"복구","port":"kn-jinju-insa-20-01_11","name":"(고압)진주레일바이크회차지AAU_1","date":"2026-04-09 05:42","type":"복구","sub":"-","detail":"DU SFP 교체 후 복구","system":"5G","area":"진주시","grade":10,"dabal":1},
    {"status":"복구","port":"hapcheon-ssangchaek-NX0_07","name":"(공동)합천성산5LRRU","date":"2026-04-08 21:44","type":"복구","sub":"-","detail":"정류기 교체","system":"LTE","area":"합천군","grade":73,"dabal":2},
    {"status":"복구","port":"kn-Jinju-hotan-GX21_07","name":"(K_경전)KTX진주역AAU_2","date":"2026-04-08 15:22","type":"복구","sub":"-","detail":"AAU 리셋 후 복구","system":"5G","area":"진주시","grade":53,"dabal":1},
    {"status":"미복구","port":"kn-hamyang-gyosan-GX22_06","name":"(공동)함양백연AAU_2","date":"2026-04-06 09:05","type":"BP","sub":"AAU","detail":"AAU 불량","system":"5G","area":"함양군","grade":82,"dabal":7},
    {"status":"미복구","port":"kn-uiryeong-uiryeong-GX02_05","name":"(공동)의령동동7AAU_2","date":"2026-04-02 09:24","type":"BP","sub":"AAU","detail":"AAU 불량","system":"5G","area":"의령군","grade":54,"dabal":9},
    {"status":"미복구","port":"hamyangohcheonQA0_10","name":"(공동)함양양백2LRRU_F2","date":"2026-03-29 00:45","type":"기타","sub":"-","detail":"한전 고장","system":"LTE","area":"함양군","grade":44,"dabal":2},
    {"status":"미복구","port":"JinjujeongchonDB1_01","name":"(공동)(고_대통)진주신율5LRRUM","date":"2026-03-22 19:31","type":"UNIT","sub":"-","detail":"RRU 불량","system":"LTE","area":"진주시","grade":16,"dabal":4},
    {"status":"복구","port":"kn-hamyang-gyosan-NX09_33","name":"(공동)함양지리산주유소LRRU_F5","date":"2026-04-06 14:47","type":"복구","sub":"-","detail":"AC차단기 ON","system":"LTE","area":"함양군","grade":61,"dabal":1},
    {"status":"복구","port":"kn-hamyang-gyosan-NX09_13","name":"(공동)함양지리산주유소LRRU_F5","date":"2026-04-06 14:47","type":"복구","sub":"-","detail":"AC차단기 ON","system":"LTE","area":"함양군","grade":60,"dabal":1},
    {"status":"복구","port":"kn-hamyang-gunja-GX04_04","name":"(공동)함양군자2AAU_1","date":"2026-04-06 14:41","type":"복구","sub":"-","detail":"AC차단기 ON","system":"5G","area":"함양군","grade":63,"dabal":1},
    {"status":"복구","port":"kn-hamyang-gunja-GX04_05","name":"(공동)함양군자2AAU_2","date":"2026-04-06 14:32","type":"복구","sub":"-","detail":"AC차단기 ON","system":"5G","area":"함양군","grade":66,"dabal":1},
    {"status":"복구","port":"kn-hadong-gojeon-GX13_04","name":"(공동)하동제첩특화마을AAU_1","date":"2026-04-05 18:25","type":"복구","sub":"-","detail":"정류기 교체","system":"5G","area":"하동군","grade":95,"dabal":5},
    {"status":"복구","port":"kn-hadong-gojeon-GX13_05","name":"(공동)하동제첩특화마을AAU_2","date":"2026-04-05 18:25","type":"복구","sub":"-","detail":"정류기 교체","system":"5G","area":"하동군","grade":96,"dabal":5},
    {"status":"복구","port":"geochangnamha2NX01_02","name":"(공동)거창양항3LRRU_F2","date":"2026-04-05 12:09","type":"복구","sub":"-","detail":"RRU 교체","system":"LTE","area":"거창군","grade":57,"dabal":1},
    {"status":"복구","port":"sacheon-donggeum-NX16_06","name":"사천향촌2LRRU_FW23","date":"2026-04-04 05:27","type":"복구","sub":"-","detail":"OJC 교체","system":"LTE","area":"사천시","grade":94,"dabal":1},
    {"status":"복구","port":"JinjusugokNX3_03","name":"(공동)진주수곡효자2LRRU","date":"2026-04-03 02:09","type":"복구","sub":"-","detail":"AC차단기 ON","system":"LTE","area":"진주시","grade":24,"dabal":1},
    {"status":"복구","port":"kn-Jinju-sugok-GX11_02","name":"(공동)진주수곡효자2AAU_2","date":"2026-04-03 01:16","type":"복구","sub":"-","detail":"AC차단기 ON","system":"5G","area":"진주시","grade":26,"dabal":1},
    {"status":"복구","port":"kn-Jinju-sugok-GX11_01","name":"(공동)진주수곡효자2AAU_1","date":"2026-04-03 01:16","type":"복구","sub":"-","detail":"AC차단기 ON","system":"5G","area":"진주시","grade":25,"dabal":1},
    {"status":"복구","port":"kn-hadong-jingyo-GX06_04","name":"(공동)하동고룡평당교차로AAU_2","date":"2026-04-02 09:25","type":"복구","sub":"-","detail":"AAU 교체","system":"5G","area":"하동군","grade":101,"dabal":6},
    {"status":"복구","port":"hamyangoksanDA0_08","name":"(공동)함양옥산3LRRU","date":"2026-04-01 23:21","type":"복구","sub":"-","detail":"한전 복전","system":"LTE","area":"함양군","grade":33,"dabal":1},
    {"status":"복구","port":"kn-jinju-insa-20-01_11","name":"(고압)진주레일바이크회차지AAU_1","date":"2026-04-01 07:14","type":"복구","sub":"-","detail":"자동복구","system":"5G","area":"진주시","grade":1,"dabal":1},
    {"status":"복구","port":"namhaeseomyeonNX0_34","name":"(공동)남해서상LRRU","date":"2026-03-31 16:20","type":"복구","sub":"-","detail":"RRU Reset","system":"LTE","area":"남해군","grade":61,"dabal":2},
    {"status":"복구","port":"Jinjusabong-LW136_07","name":"(공동)(고_남해)진주금곡2LRRUM","date":"2026-04-08 02:46","type":"복구","sub":"-","detail":"자동복구","system":"LTE","area":"진주시","grade":9,"dabal":1},
    {"status":"복구","port":"namhae-seolcheon2-NX0_06","name":"(공동)남해덕신LRRU_F5","date":"2026-04-07 05:41","type":"복구","sub":"-","detail":"자동복구","system":"LTE","area":"남해군","grade":25,"dabal":1},
    {"status":"복구","port":"kn-sacheon-gonmyeong4W-GX08_05","name":"(공동)사천초량터널앞AAU_2","date":"2026-04-06 17:34","type":"복구","sub":"-","detail":"LMUX COT 교체","system":"5G","area":"사천시","grade":37,"dabal":1},
    {"status":"복구","port":"sanchungsaengbiryangNX1_12","name":"(공동)의령대의천곡태양광LRRU_F2","date":"2026-04-06 02:58","type":"복구","sub":"-","detail":"DU SFP 교체","system":"LTE","area":"의령군","grade":34,"dabal":1},
    {"status":"복구","port":"kn-jinju-hadae-GX05_05","name":"진주상평19AAU_2","date":"2026-04-06 05:38","type":"복구","sub":"-","detail":"AAU Reset","system":"5G","area":"진주시","grade":12,"dabal":1},
]

REP = [
    {"시스템구분":"Legacy중계기","경과일":1,"망구분":"WCDMA","중계기명":"남해포상2WIC","연관중계기명":" ","중계기구분":"REMOTE","알람내역":"불통","중계기모델":"ICS-WN20","기지국명":"남해고현W"},
    {"시스템구분":"Legacy중계기","경과일":1,"망구분":"CDMA","중계기명":"함양삼정2DOR","연관중계기명":" ","중계기구분":"REMOTE","알람내역":"불통","중계기모델":"DUO-LO","기지국명":"함양백무동W"},
    {"시스템구분":"Legacy중계기","경과일":1,"망구분":"WCDMA","중계기명":"함양삼정2DOR","연관중계기명":" ","중계기구분":"REMOTE","알람내역":"불통","중계기모델":"DUO-LO","기지국명":"함양백무동W"},
    {"시스템구분":"Legacy중계기","경과일":1,"망구분":"WCDMA","중계기명":"의령대곡WIC","연관중계기명":" ","중계기구분":"REMOTE","알람내역":"불통","중계기모델":"ICS-WN20","기지국명":"의령부림2W"},
    {"시스템구분":"Legacy중계기","경과일":4,"망구분":"CDMA","중계기명":"진주수곡W-NO_J","연관중계기명":"진주사곡4DMOU","중계기구분":"MOU","알람내역":"PD 이상","중계기모델":"DDR-DuoN5","기지국명":"진주수곡W_감시회선용"},
    {"시스템구분":"Legacy중계기","경과일":4,"망구분":"WCDMA","중계기명":"진주수곡W-NO_J","연관중계기명":"진주사곡4DMOU","중계기구분":"MOU","알람내역":"PD 이상","중계기모델":"DDR-DuoN5","기지국명":"진주수곡W_감시회선용"},
    {"시스템구분":"MIBOS","경과일":1,"망구분":"CDMA","중계기명":"(대_경상)S진주가좌X_진주경상대2LCRO0M_D","연관중계기명":"(대_경상)S진주가좌X_진주경상대2LCRO0M","중계기구분":"QMHS","알람내역":"PD2 이상","중계기모델":"MiBOS(ARO지원)","기지국명":"(공동)진주호탄LW197"},
    {"시스템구분":"MIBOS","경과일":1,"망구분":"CDMA","중계기명":"(대_경상)S진주가좌X_진주경상대2LCRO0M","연관중계기명":"(대_경상)S진주가좌X_진주경상대2LCRO0M_D","중계기구분":"QRO","알람내역":"Link Fail","중계기모델":"MiBOS-L60","기지국명":"(공동)진주호탄LW197"},
    {"시스템구분":"MIBOS","경과일":3,"망구분":"CDMA","중계기명":"진주상평20LTRO_D","연관중계기명":"진주상평20LTRO","중계기구분":"QMHS","알람내역":"불통","중계기모델":"MiBOS(기본)","기지국명":"진주상대3W_감시회선용"},
    {"시스템구분":"MIBOS","경과일":3,"망구분":"CDMA","중계기명":"진주상평20LTRO","연관중계기명":"진주상평20LTRO_D","중계기구분":"QRO","알람내역":"불통","중계기모델":"MiBOS(기본)","기지국명":"진주상대3W_감시회선용"},
    {"시스템구분":"MIBOS","경과일":3,"망구분":"CDMA","중계기명":"진주상평22LTRO","연관중계기명":"진주상평20LTRO_D","중계기구분":"QRO","알람내역":"불통","중계기모델":"MiBOS(기본)","기지국명":"진주상대3W_감시회선용"},
    {"시스템구분":"MIBOS","경과일":3,"망구분":"CDMA","중계기명":"하동전도상가타운LTROM_D","연관중계기명":"하동전도상가타운LTROM","중계기구분":"QMHS","알람내역":"불통","중계기모델":"MiBOS(기본)","기지국명":"하동고전2W"},
    {"시스템구분":"MIBOS","경과일":3,"망구분":"CDMA","중계기명":"하동전도상가타운LTROM","연관중계기명":"하동전도상가타운LTROM_D","중계기구분":"QRO","알람내역":"불통","중계기모델":"MiBOS(기본)","기지국명":"하동고전2W"},
    {"시스템구분":"MIBOS","경과일":3,"망구분":"CDMA","중계기명":"하동계천3LTRO","연관중계기명":"하동전도상가타운LTROM_D","중계기구분":"QRO","알람내역":"불통","중계기모델":"MiBOS(기본)","기지국명":"하동고전2W"},
    {"시스템구분":"MIBOS","경과일":3,"망구분":"CDMA","중계기명":"하동갈사만진입로LTRO","연관중계기명":"하동전도상가타운LTROM_D","중계기구분":"QRO","알람내역":"불통","중계기모델":"MiBOS(기본)","기지국명":"하동고전2W"},
]

GREMS = [
    {"알람등급":"Critical","알람발생일자":"20260413","장비명":"(S)진주센트럴자이아파트IB_GIRO2_SI1L_0100","중계기모델":"gIRO","알람명":"DC","서비스그룹명":"공통","PCI":"877"},
    {"알람등급":"Critical","알람발생일자":"20260412","장비명":"(K)진주백화점IB_PRU_1_1L","중계기모델":"PRU","알람명":"PD Power 하한","서비스그룹명":"5G-3.6 Layer1","PCI":"476"},
    {"알람등급":"OOS","알람발생일자":"20260409","장비명":"(공동)(S)사천사남삼정그린코아IB_GIRO_SI1L_8000","중계기모델":"gIRO","알람명":"Shutdown(DL)","서비스그룹명":"5G-3.6 Layer4","PCI":"202"},
    {"알람등급":"Critical","알람발생일자":"20260409","장비명":"(공동)(S)사천사남삼정그린코아IB_GIRO_SI1L_8000","중계기모델":"gIRO","알람명":"PAU DC(DL)","서비스그룹명":"5G-3.6 Layer4","PCI":"202"},
    {"알람등급":"Critical","알람발생일자":"20260409","장비명":"(단)진주역승강장통로IB_AAU(C)_2_4L","중계기모델":"AAU(천정형)","알람명":"DL 출력 하한","서비스그룹명":"5G-3.6 Layer2","PCI":"499"},
    {"알람등급":"Critical","알람발생일자":"20260407","장비명":"(공동)(S)진주금산진흥더루벤스IB_GIRO_F2_0100","중계기모델":"gIRO","알람명":"Device Fail(Low Gain)(DL)","서비스그룹명":"5G-3.6 Layer2","PCI":"564"},
    {"알람등급":"Critical","알람발생일자":"20260406","장비명":"(공동)(S)모다아울렛(진주점)IB_GIRO_SI2L_81W0","중계기모델":"gIRO","알람명":"UL RSSI High","서비스그룹명":"5G-3.6 Layer3","PCI":"406"},
    {"알람등급":"Critical","알람발생일자":"20260322","장비명":"(L)진주LH사옥IB_PRU_6_1L","중계기모델":"PRU","알람명":"PD Power 하한","서비스그룹명":"5G-3.6 Layer1","PCI":"408"},
    {"알람등급":"Critical","알람발생일자":"20260319","장비명":"(공동)(S)사천사남삼정그린코아IB_GIRO_SI1L_8000","중계기모델":"gIRO","알람명":"AC","서비스그룹명":"공통","PCI":"202"},
    {"알람등급":"OOS","알람발생일자":"20260316","장비명":"(공동)(S)사천KAI에비에이션센터IB_PRU_2_2L","중계기모델":"PRU","알람명":"Shutdown(DL)","서비스그룹명":"5G-3.6 Layer3","PCI":"511"},
    {"알람등급":"Critical","알람발생일자":"20260316","장비명":"(공동)(S)사천KAI에비에이션센터IB_PRU_2_2L","중계기모델":"PRU","알람명":"VSWR(DL)","서비스그룹명":"5G-3.6 Layer3","PCI":"511"},
]

# ── 헤더 ─────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#fff; border-bottom:1.5px solid #b8dcf5; padding:10px 0 10px 0; margin-bottom:16px;">
  <span style="font-size:17px; font-weight:700; color:#1a5c8a;">📡 진주품질개선팀 &nbsp; 고장 현황 대시보드</span>
  <span style="font-size:11px; color:#a0bcd4; float:right; margin-top:3px;">기준일: 2026-04-13 &nbsp;|&nbsp; 생성: 2026-04-14 10:57</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 대시보드", "🔔 금일 알람", "📋 전체 RAW 데이터", "📡 중계기·MIBOS", "🏢 gREMS 알람"
])

# ══ TAB1 ══════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="info-bar">📅 기준일: <b>2026-04-13</b> &nbsp;|&nbsp; 다발알람 기준시각: <b>2026-04-12 08:00</b></div>
    <div class="rule-bar">
    ① 동일 Port+발생시각 = 다발알람 → 1건 (복구 행 우선) &nbsp;|&nbsp;
    ② 동일 Port+다른 발생시각 = 각각 별개 건수 &nbsp;|&nbsp;
    ③ 복구사유 = AP열(복구/미복구 상세내역) 우선, 없으면 자동복구 &nbsp;|&nbsp;
    ④ 미복구 = 최신배치 중 고장구분 ≠ 복구
    </div>
    """, unsafe_allow_html=True)

    kpi_data = [
        ("403", "실 고장 건수", "#4da6e8"),
        ("11",  "미복구",       "#e05c5c"),
        ("392", "복구 완료",    "#2ecc87"),
        ("111", "다발알람 국소","#e65100"),
        ("206", "5G 고장",      "#4da6e8"),
        ("197", "LTE 고장",     "#f5a623"),
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
    cats = ["복구","Unit","BP","재발생","점검중","기타"]

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Pie(
            labels=["복구","미복구"], values=[392,11], hole=0.65,
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
        total_v = [v1+v2 for v1,v2 in zip(C["5g_vals"],C["lte_vals"])]
        fig2 = go.Figure(go.Bar(
            x=cats, y=total_v,
            marker_color=["#4da6e8","#f5a623","#a78bfa","#60a5fa","#34d399","#f87171"],
        ))
        fig2.update_layout(title="고장구분별 현황",
            title_font=dict(size=14,color="#1a5c8a"),
            height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="5G", x=cats, y=C["5g_vals"], marker_color="#4da6e8"))
        fig3.add_trace(go.Bar(name="LTE", x=cats, y=C["lte_vals"], marker_color="#f5a623"))
        fig3.update_layout(title="5G / LTE 고장구분 비교",
            title_font=dict(size=14,color="#1a5c8a"),
            barmode="group", height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            legend=dict(orientation="h",y=1.1),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        fig4 = go.Figure(go.Bar(
            x=C["sub_vals"], y=C["sub_labels"], orientation="h",
            marker_color="#4da6e8",
        ))
        fig4.update_layout(title="장비 중분류별 고장",
            title_font=dict(size=14,color="#1a5c8a"),
            height=260, margin=dict(t=40,b=10,l=10,r=10),
            xaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
            yaxis=dict(showgrid=False,autorange="reversed"),
            paper_bgcolor="#fff", plot_bgcolor="#fff")
        st.plotly_chart(fig4, use_container_width=True)

    fig5 = go.Figure(go.Scatter(
        x=C["month_labels"], y=C["month_vals"],
        mode="lines+markers",
        line=dict(color="#4da6e8",width=2.5),
        fill="tozeroy", fillcolor="rgba(77,166,232,0.12)",
        marker=dict(size=8,color="#4da6e8"),
    ))
    fig5.update_layout(title="월별 고장 발생 추이 (실건수)",
        title_font=dict(size=14,color="#1a5c8a"),
        height=220, margin=dict(t=40,b=10,l=10,r=10),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(150,200,240,0.2)"),
        paper_bgcolor="#fff", plot_bgcolor="#fff")
    st.plotly_chart(fig5, use_container_width=True)
    st.caption("※ 기준일: 2026-04-13 | 복구내역 없는 과거건 = 자동복구")

# ══ TAB2 ══════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <h4 style="color:#1a5c8a; margin-bottom:12px;">
      금일 알람
      <span style="background:#ffe8e8;color:#c0392b;font-size:11px;border-radius:12px;padding:2px 10px;font-weight:700;margin-left:8px;">미복구 11건</span>
      <span style="background:#d6f5e8;color:#1a7a50;font-size:11px;border-radius:12px;padding:2px 10px;font-weight:700;margin-left:6px;">복구 0건</span>
    </h4>
    """, unsafe_allow_html=True)
    df_batch = pd.DataFrame(BATCH)
    st.dataframe(
        df_batch.style.map(
            lambda v: "background:#ffe8e8;color:#c0392b;font-weight:bold;" if v=="미복구" else "",
            subset=["상태"]
        ),
        use_container_width=True, height=500
    )

# ══ TAB3 ══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<h4 style="color:#1a5c8a; margin-bottom:12px;">전체 고장 RAW 데이터</h4>', unsafe_allow_html=True)

    col_s, col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([3,1,1,1,1,1])
    with col_s:
        sq = st.text_input("", placeholder="🔍  Port, 장비명, 시군구, 복구사유 검색...", label_visibility="collapsed", key="raw_search")
    btn_all   = col_f1.button("전체",    key="rb_all")
    btn_unfix = col_f2.button("미복구만", key="rb_unfix")
    btn_fix   = col_f3.button("복구만",  key="rb_fix")
    btn_5g    = col_f4.button("5G",      key="rb_5g")
    btn_lte   = col_f5.button("LTE",     key="rb_lte")

    if "rfilt" not in st.session_state: st.session_state.rfilt = "all"
    if btn_all:   st.session_state.rfilt = "all"
    if btn_unfix: st.session_state.rfilt = "미복구"
    if btn_fix:   st.session_state.rfilt = "복구"
    if btn_5g:    st.session_state.rfilt = "5G"
    if btn_lte:   st.session_state.rfilt = "LTE"

    df = pd.DataFrame(ALL_DATA)
    if st.session_state.rfilt == "미복구": df = df[df.status=="미복구"]
    elif st.session_state.rfilt == "복구": df = df[df.status=="복구"]
    elif st.session_state.rfilt == "5G":  df = df[df.system=="5G"]
    elif st.session_state.rfilt == "LTE": df = df[df.system=="LTE"]
    if sq:
        q = sq.lower()
        df = df[df.apply(lambda r: any(q in str(r[c]).lower() for c in ["port","name","area","detail"]), axis=1)]

    df["다발"] = df["dabal"].apply(lambda x: f"다발 {x}회" if x>1 else "-")
    disp = df[["status","date","name","port","type","sub","다발","detail","system","area","grade"]].copy()
    disp.columns = ["상태","발생일시","장비명","Port","고장구분","중분류","다발","복구사유","시스템","시군구","알람등급"]

    st.caption(f"총 {len(disp)}건 (필터: {st.session_state.rfilt})")
    st.dataframe(
        disp.style.map(
            lambda v: ("background:#ffe8e8;color:#c0392b;font-weight:bold;" if v=="미복구"
                       else "background:#d6f5e8;color:#1a7a50;font-weight:bold;" if v=="복구" else ""),
            subset=["상태"]
        ),
        use_container_width=True, height=560
    )

# ══ TAB4 ══════════════════════════════════════════════════════════
with tab4:
    st.markdown('<h4 style="color:#1a5c8a; margin-bottom:12px;">중계기 및 MIBOS 알람 현황</h4>', unsafe_allow_html=True)
    legacy_n = sum(1 for r in REP if "Legacy" in r["시스템구분"])
    mibos_n  = sum(1 for r in REP if r["시스템구분"]=="MIBOS")
    c_rep = st.columns(4)
    for col, (v, lbl, clr) in zip(c_rep, [
        (str(len(REP)), "전체 알람", "#4da6e8"),
        (str(legacy_n), "Legacy 중계기", "#e05c5c"),
        (str(mibos_n),  "MIBOS",        "#2ecc87"),
        (str(len(REP)), "CDMA+WCDMA",   "#f5a623"),
    ]):
        col.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{clr};">{v}</div><div class="kpi-label">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    df_rep = pd.DataFrame(REP)
    st.dataframe(
        df_rep.style.map(
            lambda v: ("background:#fff0d6;color:#b45309;" if "Legacy" in str(v)
                       else "background:#dbeeff;color:#1a5c8a;" if v=="MIBOS" else ""),
            subset=["시스템구분"]
        ).map(
            lambda v: "color:#e05c5c;font-weight:bold;" if isinstance(v,int) and v>=3 else "",
            subset=["경과일"]
        ),
        use_container_width=True, height=500
    )

# ══ TAB5 ══════════════════════════════════════════════════════════
with tab5:
    st.markdown('<h4 style="color:#1a5c8a; margin-bottom:12px;">gREMS 알람 현황</h4>', unsafe_allow_html=True)
    crit_n = sum(1 for r in GREMS if r["알람등급"]=="Critical")
    oos_n  = sum(1 for r in GREMS if r["알람등급"]=="OOS")
    c_gr = st.columns(3)
    for col, (v, lbl, clr) in zip(c_gr, [
        (str(len(GREMS)), "전체 알람", "#4da6e8"),
        (str(crit_n),     "Critical",  "#e05c5c"),
        (str(oos_n),      "OOS",        "#f5a623"),
    ]):
        col.markdown(f'<div class="kpi-card"><div class="kpi-val" style="color:{clr};">{v}</div><div class="kpi-label">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    df_gr = pd.DataFrame(GREMS)
    st.dataframe(
        df_gr.style.map(
            lambda v: ("background:#ffe8e8;color:#c0392b;font-weight:bold;" if v=="Critical"
                       else "background:#fff0d6;color:#b45309;font-weight:bold;" if v=="OOS" else ""),
            subset=["알람등급"]
        ),
        use_container_width=True, height=480
    )

st.markdown("""
<hr style="border:none; border-top:1px solid #d8edf9; margin-top:24px;">
<div style="text-align:center; font-size:10px; color:#a0bcd4; padding-bottom:8px;">
  진주품질개선팀 고장 현황 대시보드 | 기준일 2026-04-13 | 생성: 2026-04-14 10:57
</div>
""", unsafe_allow_html=True)
