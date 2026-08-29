# WRDS Data — RepRisk v2 · LSEG ESG · ISS

Kho dữ liệu WRDS phục vụ nghiên cứu ESG/quản trị công ty với mẫu **toàn cầu**, hand-off cho co-author khám phá. Ba database đã xác minh có subscription (29/08/2026, kiểm tra bằng truy vấn trực tiếp máy chủ WRDS):

| Database | Đo cái gì | Coverage đã xác minh | Giai đoạn | README |
|---|---|---|---|---|
| **RepRisk v2** | Sự cố rủi ro ESG từ truyền thông/NGO (góc nhìn ngoài doanh nghiệp) | 1,02 triệu công ty · 240 quốc gia · 1,19 triệu sự cố | 2007–2025 | [reprisk_v2/](reprisk_v2/README.md) |
| **LSEG ESG** (Refinitiv/Asset4) | Điểm ESG + 630 datapoint thô từ công bố của doanh nghiệp | 16.126 công ty có điểm · toàn cầu | FY2002–2026 | [lseg_esg/](lseg_esg/README.md) |
| **ISS** | HĐQT, điều khoản quản trị, thù lao điều hành, biểu quyết cổ đông | Global: 38.715 công ty/115 nước (directors), 50.995 công ty/127 nước (voting); legacy US từ 1990 | 1990–2025 tùy module | [iss/](iss/README.md) |

Ba nguồn bổ trợ nhau: LSEG đo cam kết/công bố ESG, RepRisk đo hành vi thực tế (sự cố), ISS đo cơ chế quản trị đứng sau — một thiết kế nghiên cứu có thể dùng cả ba.

## Cấu trúc thư mục

```
wrds_data_thay_khuong/
├── README.md                    ← file này
├── WDRS data.xlsx               ← danh sách database gốc (4 mục highlight)
├── check_wrds_subscriptions.py  ← script kiểm tra lại quyền truy cập bất cứ lúc nào
├── reprisk_v2/
│   ├── README.md                ← đặc điểm, bảng, identifiers, caveats
│   ├── dictionaries/            ← từ điển đủ mọi cột (CSV, mô tả gốc WRDS)
│   └── data/                    ← parquet (giai đoạn tải)
├── lseg_esg/    (như trên; dictionaries/ có thêm 4 file lookup_ mã ESG)
└── iss/         (như trên; 10 file dictionary cho 10 schema)
```

## Chiến lược nối ID giữa các nguồn

**ISIN là cây cầu trung tâm** của mẫu quốc tế:

```
RepRisk (primary_isin) ─┐
LSEG (wrds_ref_esg.isin, theo năm) ─┼─→ ISIN ─→ gvkey (Compustat Global/NA)
ISS (symbology.isin) ───┘
```

- Bảng `iss_directors_global.symbology` và `iss_compensation_analytics.company_reference` có sẵn **gvkey** (37.468 công ty) — dùng làm bảng nối trung tâm, đỡ phải tự match.
- Compustat NA: lấy CUSIP từ 9 ký tự giữa của ISIN US.
- Nối theo **từng năm** với LSEG (identifier đổi theo thời gian); RepRisk và ISS symbology là identifier tĩnh (điểm hiện tại).
- Công ty tư nhân trong RepRisk (94% số công ty) không có ISIN — muốn dùng phải fuzzy-match tên + quốc gia.

## Kế hoạch tải (giai đoạn tiếp theo)

1. **Tải full raw**: mọi bảng trừ hai bảng daily của RepRisk (xem 2) và `voteanalysis_npx` của ISS (238 triệu dòng phiếu bầu quỹ — tải khi có nhu cầu cụ thể). Định dạng parquet, streaming từng khối để không tràn RAM.
2. **RepRisk RRI**: `v2_metrics` (2,34 tỷ dòng daily) tải **snapshot cuối tháng** (~77 triệu dòng); `v2_rating` (7 tỷ dòng) bỏ qua vì trùng thông tin. Cần daily cho firm cụ thể → kéo bổ sung theo `reprisk_id`.
3. Mỗi lần tải xong sẽ điền vào bảng "Trạng thái tải" cuối README từng database (file, filter, ngày, dung lượng).

## Kết nối WRDS

- Credentials: biến môi trường `wrds_id` / `wrds_password` (máy của Oliver).
- Package `wrds` không cài được trên Python 3.14 → kết nối trực tiếp bằng `psycopg`: host `wrds-pgdata.wharton.upenn.edu`, port `9737`, db `wrds`, `sslmode=require`.
- Kiểm tra lại subscription: `python check_wrds_subscriptions.py`.

## Không có subscription (đã kiểm tra, để khỏi mất công thử lại)

Calcbench (chỉ trial) · MSCI ESG + KLD · ISS Climate · Audit Analytics (chỉ sample) · Sustainalytics · MarketPsych · Markit CDS · SDC M&A. Có sẵn ngoài 3 database chính: Compustat (NA + Global), CRSP, ExecuComp, I/B/E/S, DealScan, Worldscope, Datastream, BoardEx, 13F, Mergent FISD.
