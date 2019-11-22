SELECT
    CASE
    WHEN last_name is not NULL THEN (first_name::varchar)||' '||(last_name ::varchar)
    ELSE first_name
    END  "Имя водителя"
    , (drv.id::varchar)||'  /  '||(drv.ext_id::varchar) as driver_id
    , prs.email AS "Почта водителя"
    , pr.phone AS "Телефон водителя"
    , drv.promo_code AS "Промокод водителя"
FROM facts.FS_Drivers drv
LEFT JOIN facts.FS_Profiles pr
    ON drv.profile_id = pr.id
LEFT JOIN facts.FS_Profiles_security prs
    ON pr.id = prs.id
WHERE drv.ext_id = %s
