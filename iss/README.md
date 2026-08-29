# ISS (Institutional Shareholder Services) — Quản trị công ty, thù lao & biểu quyết

> Trạng thái: **có subscription phần lớn module** (xác minh 29/08/2026). Bị từ chối: bộ ISS Climate (`iss_climate_*`), `iss_compensation_peers`, và 2 bảng legacy `risk_proposals`/`risk_votes` (đã có bản mới thay thế).

ISS (tiền thân RiskMetrics/IRRC) là nguồn chuẩn của nghiên cứu quản trị công ty. Subscription hiện tại gồm **6 nhóm module**, mỗi nhóm một schema riêng trên WRDS.

## 1. Tóm tắt 6 module

| Module | Schema | Giai đoạn | Coverage (đo thực tế) | Grain chính |
|---|---|---|---|---|
| Directors (legacy US) | `risk_directors` | 1996–2006 (`directors`) + 2007–2025 (`rmdirectors`) | 3.033 / 3.524 công ty (~S&P 1500) | director × firm × năm |
| Governance (legacy US) | `risk_governance` | 1990–2006 (`gset`, G-index) + 2007–2025 (`rmgovernance`) | 4.016 / 3.193 công ty | firm × năm |
| Directors Global | `iss_directors_global` | ~2015–nay | **38.715 công ty, 115 quốc gia** — US 8.184, JP 4.305, CA 4.043, KR 2.489, HK 2.427, IN 1.942… | directorship-event |
| Incentive Lab (US + Europe) | `iss_incentive_lab`, `iss_incentive_lab_europe` | US: FY1998–2025 · EU: FY2002–2025 | US: 4.984 CIK · EU: 743 công ty | grant / participant × fy |
| Compensation Analytics | `iss_compensation_analytics` | FY2006–2026 | 17.533 công ty, 55 quốc gia — US 8.178, AU 1.675, GB 1.501, CA 1.397… | executive × firm × fy |
| Voting Analytics | `iss_va_vote_us`, `iss_va_vote_global`, `iss_va_mf`, `iss_va_shareholder` | US: 2003–2025 · Global: 2013–2025 · MF: 2003–2025 | US: 15.055 công ty · Global: **50.995 công ty, 127 quốc gia** | agenda item × meeting |

**Cho mục tiêu global:** Directors Global, Compensation Analytics và Voting Global là ba module quốc tế thực thụ; legacy US và Incentive Lab US phủ Mỹ sâu và dài hơn.

## 2. Chi tiết từng module

### 2a. Directors legacy US (`risk_directors`)
- `directors` (166.375 dòng, 1996–2006) và `rmdirectors` (268.451 dòng, 2007–2025): mỗi dòng = 1 giám đốc tại 1 công ty 1 năm. Biến chính: `classification` (I/E/L — độc lập/điều hành/liên kết), `audit_membership`, `comp_membership`, `female`, `age`, `outside_public_boards`, `attend_less75_pct`, `num_of_shares`.
- Hai bảng **khác cấu trúc cột** — nối dọc phải map biến thủ công (dictionary có đủ cả hai).

### 2b. Governance legacy US (`risk_governance`)
- `gset` (13.998 dòng, 1990–2006): 24 điều khoản IRRC → dựng **G-index** (Gompers–Ishii–Metrick 2003).
- `rmgovernance` (28.667 dòng, 2007–2025): điều khoản thế hệ mới (cboard, ppill, gparachute, supermajor…) → dựng **E-index** (Bebchuk–Cohen–Ferrell 2009).
- Lưu ý đứt gãy 2006/2007: định nghĩa biến đổi, không nối chuỗi thô hai giai đoạn.

### 2c. Directors Global (`iss_directors_global`)
- `director_roles` (4,9 triệu): mỗi dòng = 1 directorship-event; 120 cột gồm độc lập, tenure, vai trò ủy ban (audit/comp/nominating/sustainability…), sở hữu, kết quả phiếu bầu cho chính giám đốc đó.
- `committee_detail` (8,4 triệu), `company_diversity` (597k), `person_ethnicity` (449k).
- **`symbology` (38.715 dòng) là bảng vàng:** có sẵn `gvkey` (37.468 công ty!), `cik`, `isin`, `cusip`, `sedol`, `ticker`, GICS — dùng làm bảng nối trung tâm cho cả dự án.

### 2d. Incentive Lab (`iss_incentive_lab` + `iss_incentive_lab_europe`)
- Chi tiết **hợp đồng thù lao** ở cấp từng grant: `gpbaabs`/`gpbagrant`/`gpbarel` (mục tiêu tuyệt đối/tương đối của performance award), `oeoption`/`oestock` (option/cổ phiếu đang nắm), `sumcomp` (tổng thù lao), `participantfy` (danh sách executive, có `participantcik`), `dircomp` (thù lao HĐQT).
- Khóa: `cik` × `fiscalyear` (+ `participantid`). Bản Europe: 10 bảng tiền tố `euro_`.

### 2e. Compensation Analytics (`iss_compensation_analytics`)
- `person_pay` (2,07 triệu): thù lao từng executive-năm, cả pay ratio, điều khoản hợp đồng, severance, CIC.
- `company_reference` (151k): **cũng có sẵn `gvkey`/`isin`/`cusip`/`sedol`** + các biến chính sách thù lao cấp công ty (clawback, hedging ban, ownership guidelines, kết quả say-on-pay).
- Khóa: `iss_company_id` × `fiscal_year`; executive: `iss_person_id`.

### 2f. Voting Analytics (`iss_va_*`)
- `vavoteresults` (US, 887k) / `globalvoteresults` (3,99 triệu): mỗi dòng = 1 agenda item tại 1 đại hội — votedfor/against/abstain, mgmtrec, voterequirement, voteresult.
- `voteanalysis_npx` (**238,5 triệu dòng** — phiếu bầu của từng quỹ tương hỗ Mỹ theo N-PX, 2003-07→2025-06): bảng rất lớn, tải có chọn lọc.
- `va_proposals` (20.867): shareholder proposals US 2006–2025 kèm sponsor, kết quả.
- Khóa: `companyid` (× `meetingid` × `issagendaitemid`); quỹ: `fundid`/`institutionid`.
- Các bảng `chars*` đều rỗng (0 dòng) — bỏ qua.

## 3. Key identifiers & cách nối

| Hệ | Khóa | Nối sang ngoài |
|---|---|---|
| Legacy US (`risk_*`) | `rt_id`, `company_id` | `cusip` (6/8 ký tự), `ticker` → CRSP/Compustat |
| Global mới (`iss_*`) | `iss_company_id`, `iss_person_id` | qua `symbology` / `company_reference`: **gvkey, cik, isin, cusip, sedol có sẵn** |
| Incentive Lab | `cik` | CIK → Compustat qua `comp.company.cik`; nối SEC trực tiếp |
| Voting Analytics | `companyid` | `cusip`, `ticker` trong chính bảng vote |

Lưu ý: `iss_company_id` (mới) ≠ `companyid` (Voting Analytics) ≠ `rt_id` (legacy) — **ba hệ ID khác nhau**, không nối trực tiếp với nhau; đi vòng qua cusip/isin/gvkey.

## 4. Data dictionary

Đầy đủ mọi cột (phần lớn kèm mô tả gốc WRDS) trong `dictionaries/`:
`risk_directors.csv` (171 cột) · `risk_governance.csv` (290) · `iss_directors_global.csv` (271) · `iss_incentive_lab.csv` (292) · `iss_incentive_lab_europe.csv` (205) · `iss_compensation_analytics.csv` (219) · `iss_va_vote_us.csv` (181) · `iss_va_vote_global.csv` (193) · `iss_va_mf.csv` (186) · `iss_va_shareholder.csv` (180).

## 5. Cách sử dụng điển hình

```python
import pandas as pd

# Board independence firm-năm từ Directors Global
roles = pd.read_parquet("data/iss_directors_global/director_roles.parquet")
sym = pd.read_parquet("data/iss_directors_global/symbology.parquet")

board = (roles[roles["include_in_board_stats_yn"] == "Yes"]
         .groupby("iss_company_id")
         .agg(board_size=("iss_person_id", "nunique"),
              pct_indep=("independent_yn", lambda s: (s == "Yes").mean())))
board = board.join(sym.set_index("iss_company_id")[["gvkey", "isin", "iss_country"]])
```

## 6. Caveats

1. **Đứt gãy legacy/new 2006–2007** ở Directors và Governance (đổi vendor IRRC → RiskMetrics → ISS): biến đổi định nghĩa, mẫu đổi nhẹ.
2. Directors Global và Voting Global chỉ sâu từ ~2013–2015 — nghiên cứu dài hạn về Mỹ vẫn phải dùng bảng legacy.
3. `director_roles` là bảng **event-level** (mỗi lần bầu/bổ nhiệm một dòng) — dựng panel firm-năm phải lọc `person_most_recent_event_yn`/`directorship_most_recent_yn` hoặc theo meeting date, kẻo double-count.
4. `voteanalysis_npx` 238 triệu dòng — chỉ tải khi thật cần, và lọc server-side theo năm/quỹ.
5. Luxembourg/Cayman/Ireland đứng cao trong Voting Global vì là nơi **đăng ký pháp lý** (`countryofinc`), không phải nơi hoạt động — phân tích theo quốc gia nên dùng country của `symbology` hoặc Compustat.

## 7. Trạng thái tải

| File | Nguồn | Filter | Ngày tải | Dung lượng |
|---|---|---|---|---|
| _(chưa tải)_ | | | | |
