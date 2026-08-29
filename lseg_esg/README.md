# LSEG ESG (Refinitiv / Asset4) — Điểm ESG toàn cầu

> Trạng thái: **có subscription WRDS** (xác minh 29/08/2026 bằng truy vấn trực tiếp).
> Schema trên WRDS: `tr_esg`

## 1. Tổng quan

Bộ điểm ESG của LSEG (tên cũ: Refinitiv ESG, gốc là Thomson Reuters Asset4) — một trong những bộ rating ESG được dùng nhiều nhất trong nghiên cứu học thuật quốc tế. LSEG thu thập ~630 datapoint từ báo cáo thường niên, báo cáo bền vững, website và tin tức của doanh nghiệp, rồi tổng hợp thành điểm theo 3 trụ cột (E/S/G), 10 category, và điểm tổng (ESG Score, ESGC Score có phạt controversy).

Số liệu coverage (đo trực tiếp trên server, 29/08/2026):

| Chỉ tiêu | Giá trị |
|---|---|
| Số công ty có điểm ESG | **16.126** (`esgscores`); 23.626 trong bảng tham chiếu |
| Giai đoạn | FY **2002 → 2026** (năm cuối chưa đầy đủ) |
| Phạm vi | Toàn cầu — top theo ISIN: US (8.502), JP (1.568), CN (1.288), GB (1.105), MY, CA, IN, AU, TW, SE, DE, TH… |
| Cấp độ | Firm × fiscal year |

## 2. Cấu trúc bảng — 3 lớp + lookup

| Lớp | Bảng | Số dòng | Grain |
|---|---|---|---|
| **Bảng tiện dụng (khuyên dùng trước)** | `wrds_ref_esg` | 45,9 triệu | firm × năm × field — đã flatten, **kèm sẵn cusip/isin/sedol/ticker, tên, SIC/NAICS** |
| Điểm tổng hợp | `esgscores` | 2,28 triệu | firm × fy × item (điểm pillar/category/tổng) |
| | `esgdniratings` | 311.628 | rating legacy (Datastream ESG cũ) |
| Raw datapoints | `esgenvdatapoint` / `esgsocdatapoint` / `esggovdatapoint` | 8,8 / 15,3 / 10,4 triệu | firm × fy × datapoint thô (630+ mã) |
| | `esgenvindicator` / `esgsocindicator` / `esggovindicator` | 1,7 / 2,0 / 5,2 triệu | indicator đã chuẩn hóa |
| As-reported | `esgasrepdata` | 1,16 triệu | firm × fy × item, giá trị như doanh nghiệp báo cáo (kèm đơn vị, scale) |
| Nguồn gốc | `esgsourcedata`, `esgsourcemap`, `esgstmtdet` | 10,9 / 17,0 / 0,19 triệu | truy vết nguồn của từng datapoint |
| Lookup | `esgcode` (182), `esgitem` (633), `esgdesc` (1.588), `esgorgindcls` | | từ điển mã — đã xuất sẵn CSV trong `dictionaries/lookup_*.csv` |

## 3. Key identifiers & cách nối

- **Khóa nội bộ:** `orgpermid` (LSEG PermID của tổ chức) + `fy` (fiscal year).
- **Nối ra ngoài:** dùng `wrds_ref_esg` — bảng này có sẵn `isin`, `cusip`, `sedol`, `ticker` theo từng năm:
  - → Compustat NA qua `cusip`; Compustat Global qua `isin` → `gvkey`
  - → RepRisk qua `isin` = `primary_isin`
  - → ISS qua `isin`/`cusip` trong `symbology`
- Lưu ý: identifier có thể đổi theo năm (đổi sàn, đổi ISIN) — nối theo **từng năm**, không lấy 1 ISIN áp cho cả lịch sử công ty.

## 4. Cột quan trọng nhất

`esgscores`: `orgpermid`, `item` (mã điểm — tra nghĩa trong `lookup_esgcode.csv`, ví dụ ESGScore, ESGCombinedScore, EnvironmentPillarScore…), `fy`, `value_` (điểm 0–100), `valuegrade` (A+…D-), `valuecalcdt` (ngày tính — quan trọng, xem caveat 2).

`wrds_ref_esg`: `orgpermid`, `year`, `fieldid`/`fieldname` (tra trong `lookup_wrds_ref_esg_item.csv`), `pillar`, `hierarchy`, `value`, `valuescore`, + đủ bộ identifier.

`esgasrepdata`: `value_` kèm `scalecode`/`unitcode` — giá trị thô như báo cáo (ví dụ tấn CO2, số nhân viên).

Từ điển đầy đủ 142 cột: [`dictionaries/tr_esg.csv`](dictionaries/tr_esg.csv). Danh mục 633 field: [`dictionaries/lookup_wrds_ref_esg_item.csv`](dictionaries/lookup_wrds_ref_esg_item.csv).

## 5. Cách sử dụng điển hình

```python
import pandas as pd
scores = pd.read_parquet("data/esgscores.parquet")

# Panel firm-năm: điểm ESG tổng + 3 trụ cột
pivot = (scores[scores["item"].isin(
            ["ESGScore", "EnvironmentPillarScore",
             "SocialPillarScore", "GovernancePillarScore"])]
         .pivot_table(index=["orgpermid", "fy"],
                      columns="item", values="value_"))
```

Muốn lấy biến thô (phát thải CO2, tỷ lệ nữ trong HĐQT, chính sách chống tham nhũng…): lọc `wrds_ref_esg` theo `fieldid` sau khi tra mã trong lookup CSV.

## 6. Caveats

1. `fy` là **fiscal year**, không phải calendar year — khi nối với Compustat phải khớp theo datadate/fyear.
2. **LSEG viết lại điểm lịch sử** khi cập nhật phương pháp (vấn đề được Berg, Fabisik & Sautner 2021 chỉ ra) — điểm tải hôm nay có thể khác điểm các paper cũ dùng. `valuecalcdt` cho biết điểm được tính khi nào; ghi rõ ngày tải trong mọi phân tích.
3. Coverage tăng mạnh theo thời gian: ~1.000 công ty đầu 2002 → 16.000+ hiện nay; mẫu những năm đầu thiên về công ty lớn ở thị trường phát triển (survivorship theo hướng mở rộng).
4. FY2025–2026 chưa hoàn chỉnh (điểm được điền dần khi báo cáo công bố).
5. Boolean datapoint có nhiều missing ≠ No — LSEG mã hóa không đồng nhất giữa các field; kiểm tra từng field trước khi ép NaN → 0.

## 7. Trạng thái tải

| File | Nguồn | Filter | Ngày tải | Dung lượng |
|---|---|---|---|---|
| _(chưa tải)_ | | | | |
