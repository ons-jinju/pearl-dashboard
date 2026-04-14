# 📡 진주품질개선팀 고장 현황 대시보드

5개 탭으로 구성된 Streamlit 웹 대시보드입니다.

## 탭 구성
| 탭 | 내용 |
|----|------|
| 📊 대시보드 | KPI 6종 + 차트 5개 (복구현황, 고장구분, 5G/LTE 비교, 장비중분류, 월별추이) |
| 🔔 금일 알람 | 최신 배치 미복구 11건 |
| 📋 전체 RAW 데이터 | 검색·필터(전체/미복구/복구/5G/LTE) |
| 📡 중계기·MIBOS | Legacy 6건 + MIBOS 9건 |
| 🏢 gREMS 알람 | Critical 9건 + OOS 2건 |

---

## 🚀 Streamlit Community Cloud 배포 (무료, URL 공유)

### 1단계 — GitHub 업로드
```bash
git init
git add .
git commit -m "진주 고장 대시보드"
git branch -M main
git remote add origin https://github.com/YOUR_ID/pearl-dashboard.git
git push -u origin main
```

### 2단계 — Streamlit Cloud 배포
1. **https://share.streamlit.io** 접속 → GitHub 계정 로그인
2. **"New app"** 클릭
3. 설정:
   - Repository: `YOUR_ID/pearl-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
4. **"Deploy!"** 클릭 → 약 1~2분 후 URL 발급

### 결과
```
https://YOUR_ID-pearl-dashboard-app-XXXXX.streamlit.app
```
이 URL을 팀원 누구에게나 공유하면 바로 접속 가능합니다.

---

## 💻 로컬 실행 (테스트용)
```bash
pip install -r requirements.txt
streamlit run app.py
```
브라우저에서 http://localhost:8501 열림

---

## 📁 파일 구조
```
pearl_dashboard/
├── app.py            ← 메인 앱 (이것만 있으면 됨)
├── requirements.txt  ← 패키지 목록
└── README.md         ← 이 파일
```

---

## 🔄 데이터 업데이트 방법
`app.py` 상단의 `BATCH`, `ALL_DATA`, `REP`, `GREMS`, `C` 딕셔너리를 수정 후
GitHub에 push하면 Streamlit Cloud가 자동으로 재배포합니다.
