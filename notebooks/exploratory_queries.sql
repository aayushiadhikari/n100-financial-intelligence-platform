-- Query 1: Total companies
SELECT COUNT(*) AS total_companies
FROM companies;

-- Query 2: Companies by sector
SELECT 
    broad_sector,
    COUNT(*) AS company_count
FROM sectors
GROUP BY broad_sector
ORDER BY company_count DESC;

-- Query 3: Top 10 companies by market cap
SELECT 
    c.company_name,
    m.year,
    m.market_cap_crore
FROM market_cap m
JOIN companies c ON m.company_id = c.id
ORDER BY m.market_cap_crore DESC
LIMIT 10;

-- Query 4: Latest profit and sales
SELECT 
    c.company_name,
    p.year,
    p.sales,
    p.net_profit
FROM profitandloss p
JOIN companies c ON p.company_id = c.id
ORDER BY p.year DESC
LIMIT 20;

-- Query 5: Highest ROE companies
SELECT 
    c.company_name,
    f.year,
    f.return_on_equity_pct
FROM financial_ratios f
JOIN companies c ON f.company_id = c.id
WHERE f.return_on_equity_pct IS NOT NULL
ORDER BY f.return_on_equity_pct DESC
LIMIT 10;

-- Query 6: Debt to equity analysis
SELECT 
    c.company_name,
    f.year,
    f.debt_to_equity
FROM financial_ratios f
JOIN companies c ON f.company_id = c.id
WHERE f.debt_to_equity IS NOT NULL
ORDER BY f.debt_to_equity DESC
LIMIT 10;

-- Query 7: Sector average market cap
SELECT
    s.broad_sector,
    AVG(m.market_cap_crore) AS avg_market_cap
FROM sectors s
JOIN market_cap m ON s.company_id = m.company_id
GROUP BY s.broad_sector
ORDER BY avg_market_cap DESC;

-- Query 8: Companies with positive cash flow
SELECT 
    c.company_name,
    cf.year,
    cf.net_cash_flow
FROM cashflow cf
JOIN companies c ON cf.company_id = c.id
WHERE cf.net_cash_flow > 0
ORDER BY cf.net_cash_flow DESC
LIMIT 10;

-- Query 9: Stock price data availability
SELECT
    c.company_name,
    COUNT(sp.date) AS price_records
FROM stock_prices sp
JOIN companies c ON sp.company_id = c.id
GROUP BY c.company_name
ORDER BY price_records DESC
LIMIT 10;

-- Query 10: Peer group benchmark companies
SELECT 
    peer_group_name,
    company_id,
    is_benchmark
FROM peer_groups
WHERE is_benchmark = 1;