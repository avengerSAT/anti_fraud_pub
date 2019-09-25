SELECT DISTINCT
    dd.ext_id
    ,oo.customer_id
    ,oo.driver_id
FROM facts.FS_Orders oo 
LEFT JOIN facts.FS_Drivers dd 
    ON oo.driver_id = dd.id
WHERE oo.id = %s