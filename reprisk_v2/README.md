# RepRisk v2 — Sự cố rủi ro ESG toàn cầu

> Trạng thái: **có subscription WRDS bản v2 đầy đủ** (xác minh 29/08/2026 bằng truy vấn trực tiếp).
> Schema trên WRDS: `reprisk_v2`

## 1. Tổng quan

RepRisk đo **rủi ro ESG nhìn từ bên ngoài doanh nghiệp**: hệ thống của họ sàng lọc hằng ngày hơn 100.000 nguồn công khai (báo chí, NGO, cơ quan quản lý, mạng xã hội, think tank) bằng 23 ngôn ngữ để ghi nhận **sự cố (risk incident)** liên quan đến môi trường, xã hội, quản trị. Khác với các bộ rating dựa trên công bố tự nguyện của doanh nghiệp (LSEG, MSCI), RepRisk chỉ dùng nguồn *ngoài* doanh nghiệp — nên thường được dùng làm proxy cho ESG controversy / reputational risk / hành vi thực tế.

Số liệu coverage (đo trực tiếp trên server, 29/08/2026):

| Chỉ tiêu | Giá trị |
|---|---|
| Số công ty trong hệ thống | **1.021.966** (cả niêm yết lẫn tư nhân) |
| — trong đó có ISIN (niêm yết) | 82.630 |
| Số quốc gia/lãnh thổ (trụ sở) | 240 — top: US (230k), CN (90k), GB (57k), DE, FR, AU, ES, IN, IT, CA, BR, JP |
| Số sự cố | **1.194.528** thuộc 330.290 công ty |
| Giai đoạn | 02/01/2007 → 31/12/2025 |
| Phân bố severity | 1 (nhẹ): 842.615 · 2 (vừa): 322.332 · 3 (nghiêm trọng): 29.581 |

## 2. Cấu trúc bảng

| Bảng | Số dòng | Grain (1 dòng =) | Ghi chú |
|---|---|---|---|
| `v2_company_identifiers` | 1.021.966 | 1 công ty | Bảng định danh gốc: tên, quốc gia trụ sở, sector, ISIN |
| `v2_risk_incidents` | 1.194.528 | 1 công ty × 1 sự cố | 132 cột: ngày, severity/reach/novelty, cờ E/S/G + ~100 cờ issue chi tiết |
| `v2_metrics` | 2,34 tỷ | 1 công ty × 1 **ngày** | RRI hiện tại/xu hướng/đỉnh + 10 nguyên tắc UN Global Compact |
| `v2_rating` | 7,0 tỷ | 1 công ty × 1 ngày | Chỉ RepRisk Rating (AAA–D) + trung bình country-sector |
| `v2_wrds_company_id_table` | 1.021.966 | 1 công ty | Bản rút gọn 4 cột của identifiers |

Quan hệ: mọi bảng nối với nhau qua `reprisk_id`.

```
v2_company_identifiers (1 công ty)
    ├─< v2_risk_incidents  (n sự cố)
    ├─< v2_metrics         (n ngày)
    └─< v2_rating          (n ngày)
```

## 3. Key identifiers & cách nối

- **Khóa nội bộ:** `reprisk_id` (mọi bảng).
- **Nối ra ngoài:** `primary_isin` (hoặc danh sách `isins`) trong `v2_company_identifiers` → nối sang:
  - Compustat Global: `comp_global_daily.g_security.isin` → `gvkey`
  - Compustat North America: 9 ký tự giữa của ISIN US = CUSIP → `comp.security.cusip` → `gvkey`
  - LSEG ESG: `tr_esg.wrds_ref_esg.isin`
  - ISS: `iss_directors_global.symbology.isin`
- Chỉ ~82.630 công ty có ISIN — phần còn lại là công ty tư nhân, muốn nối phải fuzzy-match theo tên + quốc gia (chấp nhận sai số).

## 4. Cột quan trọng nhất

`v2_risk_incidents`: `reprisk_id`, `story_id`, `incident_date`, `severity` (1–3), `reach` (1–3, độ phủ nguồn tin), `novelty` (1–2, sự cố mới hay lặp lại), `environment`/`social`/`governance`/`cross_cutting` (cờ trụ cột), `unsharp_incident` (sự cố không gắn chắc chắn cho công ty — cân nhắc loại), `related_countries` + ~100 cờ issue (child_labor, fraud, climate_ghg_pollution, tax_evasion…).

`v2_metrics`: `date`, `current_rri` (0–100), `trend_rri`, `peak_rri` + `peak_rri_date` (đỉnh 2 năm gần nhất), `reprisk_rating` (AAA–D), `country_sector_average`, `principle1`…`principle10` (cờ vi phạm UNGC).

Từ điển đầy đủ 167 cột (100% có mô tả gốc của WRDS): [`dictionaries/reprisk_v2.csv`](dictionaries/reprisk_v2.csv).

## 5. Cách sử dụng điển hình

```python
import pandas as pd
inc = pd.read_parquet("data/v2_risk_incidents.parquet")

# Đếm sự cố firm-năm, tách theo trụ cột
inc["year"] = pd.to_datetime(inc["incident_date"]).dt.year
counts = (inc.groupby(["reprisk_id", "year"])
             .agg(n_incidents=("story_id", "count"),
                  n_env=("environment", "sum"),
                  n_soc=("social", "sum"),
                  n_gov=("governance", "sum"),
                  n_severe=("severity", lambda s: (s >= 2).sum())))
```

**Zero-fill đúng cách:** công ty không xuất hiện trong `v2_risk_incidents` năm t nghĩa là **0 sự cố**, không phải missing — nhưng chỉ zero-fill cho công ty có mặt trong `v2_company_identifiers` (đã nằm trong tầm quét của RepRisk). Mẫu chuẩn trong nghiên cứu: lấy toàn bộ firm niêm yết từ Compustat, nối RepRisk, sự cố NaN → 0.

Các bài dùng chuẩn tham khảo: Glossner (2021, working paper "Repeat Offenders"); Bisetti, She & Zaldokas (2026).

## 6. Caveats

1. **Hai bảng daily quá lớn để tải nguyên vẹn** (`v2_metrics` 2,34 tỷ + `v2_rating` 7 tỷ dòng). Kế hoạch đã chốt: tải **snapshot cuối tháng** cho `v2_metrics` (giữ đủ current/peak RRI); cần daily cho firm cụ thể thì kéo bổ sung theo danh sách `reprisk_id`. `v2_rating` gần như là tập con thông tin của `v2_metrics` — mặc định không tải riêng.
2. `unsharp_incident = 1`: sự cố gán cho công ty với độ tin cậy thấp hơn — nhiều paper loại ra khi robustness.
3. Một `story_id` có thể xuất hiện ở nhiều `reprisk_id` (một bài báo dính nhiều công ty) — đếm "số sự cố của firm" thì giữ nguyên, đếm "số sự kiện duy nhất trên thị trường" thì dedup theo `story_id`.
4. RepRisk chỉ thu công ty **từng dính ít nhất một sự cố hoặc nằm trong danh mục theo dõi** — 1,02 triệu công ty không phải toàn bộ vũ trụ doanh nghiệp thế giới.
5. Severity 3 rất hiếm (2,5%) — cân nhắc khi làm biến phụ thuộc.

## 7. Trạng thái tải

| File | Nguồn | Filter | Ngày tải | Dung lượng |
|---|---|---|---|---|
| _(chưa tải — sẽ điền khi bắt đầu giai đoạn download)_ | | | | |
