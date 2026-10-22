# Data shape

*Generated 2026-10-22T11:40:50Z by `wss schema` from the derived rows. Do not hand-edit — regenerate after any derive.*

**You should not need to download anything to read this.**

- **39,810 observations** across 2 partition(s), in **1 series**
  - `databricks.marketplace.listings` — 39,810 rows, **2211 entities**
- Raw: 1 file(s), 118,163 bytes on disk, 5 capture date(s), 2026-09-24 → 2026-10-22

## Sources

| source | cadence | endpoints | storage | personal data | licence |
| --- | --- | ---: | --- | --- | --- |
| `databricks.marketplace.listings` | weekly | 1 | git | none | NOT ESTABLISHED (checked 2026-09-25). marketplace.databricks |

## Columns

```
series_id, entity_id, observed_at, captured_at, metric, value, unit, source_id, raw_ref, parser_version
```

`entity_id` looks like: **databricks.marketplace.listings** `0006d848-2ebc-488e-8297-55d98d6b7748`, `0018ab7d-a6d8-47eb-b3cc-fd4129c2aac4`, `001da8f5-69f2-4c7c-a896-9bc337e43b3f`

## Metrics

| metric | series | rows | entities | type | unit | distinct | range / samples |
| --- | --- | ---: | ---: | --- | --- | ---: | --- |
| `is_sample` | databricks.marketplace.listings | 6,645 | 1329 | text |  | 1 | `true` |
| `listed` | databricks.marketplace.listings | 11,055 | 2211 | bool | count | 1 | `1` |
| `listing_name` | databricks.marketplace.listings | 11,055 | 2211 | text |  | 2193 | `APISCRAPY_-SAMPLE-Amazon`, `APISCRAPY_-SAMPLE-B2B-Ma`, `APISCRAPY_-SAMPLE-Best-W` |
| `vendor` | databricks.marketplace.listings | 11,055 | 2211 | text |  | 226 | `APISCRAPY`, `AWIS-Weather-Services`, `AccuWeather` |

## Partitions

- `derived/observations/2026-09.csv.gz`
- `derived/observations/2026-10.csv.gz`
