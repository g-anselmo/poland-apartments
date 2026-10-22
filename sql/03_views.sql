CREATE OR REPLACE VIEW v_median_price_by_city AS
SELECT
    city,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY price_per_m2) AS median_city
FROM apartments
WHERE is_outlier = FALSE
GROUP BY city;

CREATE OR REPLACE VIEW v_warsaw_price_evolution AS
SELECT
    month,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY price_per_m2) AS median_price_per_m2
FROM apartments
WHERE is_outlier = FALSE AND city = 'warszawa'
GROUP BY month
ORDER BY month;

CREATE OR REPLACE VIEW v_var_median AS
SELECT
    month,
    median_price_per_m2,
    LAG(median_price_per_m2) OVER (ORDER BY month) AS previous_median,
    ROUND(((median_price_per_m2 / NULLIF(LAG(median_price_per_m2) OVER (ORDER BY month), 0) - 1) * 100)::numeric, 2) AS var_pct
FROM v_warsaw_price_evolution;