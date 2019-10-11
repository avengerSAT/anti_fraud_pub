WITH args AS (
SELECT
    CAST(%s AS INTEGER) date_from
    , CAST(%s AS INTEGER) date_to
    , CAST(%s AS INTEGER) city_id)
SELECT
DISTINCT
    o.id
    , o.driver_id
    , drv.ext_id
FROM facts.FS_Orders o
LEFT JOIN facts.FS_Fraud_orders fo
    ON o.id = fo.id
LEFT JOIN facts.FS_Fraud_verifies fv
    ON fo.id = fv.order_id
LEFT JOIN (
SELECT
    id
    , order_pattern_id
    , session_id
    , resolution
    , ROW_NUMBER() OVER(PARTITION BY order_pattern_id ORDER BY id DESC) AS rnk
FROM facts.FS_Fraud_resolutions
GROUP BY order_pattern_id, resolution, id, session_id
) fr
    ON fv.id = fr.session_id AND rnk = 1
LEFT JOIN args ON TRUE
LEFT JOIN facts.FS_Drivers drv
    ON o.driver_id = drv.id
WHERE
    fo.launch_region_id = city_id
    AND fo."date" BETWEEN date_from AND date_to
    AND (resolution IS NULL OR resolution != 'NO')
    AND o.driver_id IN %s
ORDER BY o.driver_id DESC