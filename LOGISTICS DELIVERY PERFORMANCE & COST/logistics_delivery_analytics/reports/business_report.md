# Logistics Delivery Performance & Cost Report

## Scope and data quality

- Raw rows: 5,000
- Cleaned orders: 4,975
- Rows removed during cleaning: 25 (exact duplicates and rows missing required identifiers/dates)
- Missing values in the raw file: destination_city: 40; shipping_cost: 50; fuel_cost: 50; warehouse_processing_hours: 59; customer_rating: 89.
- Missing fuel cost is imputed using the shipping-mode median, then the overall median. Missing shipping costs, destinations, customer ratings, and warehouse processing hours are retained.
- The source `delivery_status` field is retained; on-time performance is independently calculated from actual versus expected delivery dates.

## Portfolio snapshot

| KPI | Value |
| --- | ---: |
| Unique orders | 4,975 |
| On-time delivery | 76.1% |
| Average shipping cost | 2,284.31 |
| Average tracked shipping + fuel cost | 2,656.24 |
| Average customer rating | 4.12 / 5 |
| Average delay among late orders | 2.95 days |
| Orders flagged damaged | 2.9% |
| Orders flagged returned | 4.4% |

## Delivery partner comparison

Rates and costs are unadjusted averages; differences may reflect route, distance, mode, or order mix.

```text
                  orders  on_time_rate  avg_shipping_cost  avg_rating
delivery_partner                                                     
Ecom Express         853          0.74            2388.76        4.14
XpressBees           844          0.73            2188.20        4.08
Shadowfax            841          0.79            2344.87        4.17
Delhivery            829          0.79            2152.85        4.14
DTDC                 809          0.71            2354.67        4.10
Blue Dart            799          0.81            2276.16        4.12
```

## Shipping mode comparison

```text
               orders  on_time_rate  avg_shipping_cost
shipping_mode                                         
Road             2521          0.74            1844.26
Rail              931          0.72            1465.42
Air               911          0.81            3791.73
Express           612          0.83            3089.06
```

## Interpretation notes

- `tracked_total_cost` is the sum of recorded shipping and fuel costs; confirm whether fuel is already included in shipping charges before treating it as an accounting total.
- Compare delivery partners within similar routes and shipping modes before making sourcing decisions.
- Missing ratings, shipping costs, and warehouse processing hours are not imputed; averages use available observations only. Destination city remains blank where missing.
