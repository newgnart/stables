WITH daily_dates AS (
  SELECT 
    date_trunc('day', block_time) as day_start
  FROM tokens.transfers
  WHERE blockchain = 'unichain'
    AND contract_address IN (
      0x9151434b16b9763660705744891fa906f660ecc5, -- USDT
      0x078d782b760474a361dda0af3839290b0ef57ad6, -- USDC
      0x20cab320a855b39f724131c69424240519573f81  -- DAI
    )
  GROUP BY 1
  ORDER BY 1
),
token_mints AS (
  SELECT
    date_trunc('day', block_time) as day_start,
    contract_address,
    SUM(amount) as total_minted
  FROM tokens.transfers
  WHERE
    blockchain = 'unichain'
    AND contract_address IN (
      0x9151434b16b9763660705744891fa906f660ecc5, -- USDT
      0x078d782b760474a361dda0af3839290b0ef57ad6, -- USDC
      0x20cab320a855b39f724131c69424240519573f81  -- DAI
    )
    AND "from" = 0x0000000000000000000000000000000000000000
  GROUP BY 1, 2
),
token_burns AS (
  SELECT
    date_trunc('day', block_time) as day_start,
    contract_address,
    SUM(amount) as total_burned
  FROM tokens.transfers
  WHERE
    blockchain = 'unichain'
    AND contract_address IN (
      0x9151434b16b9763660705744891fa906f660ecc5, -- USDT
      0x078d782b760474a361dda0af3839290b0ef57ad6, -- USDC
      0x20cab320a855b39f724131c69424240519573f81  -- DAI
    )
    AND "to" = 0x0000000000000000000000000000000000000000
  GROUP BY 1, 2
),
daily_supply AS (
  SELECT
    d.day_start,
    t.contract_address,
    CASE 
      WHEN t.contract_address = 0x9151434b16b9763660705744891fa906f660ecc5 THEN 'USDT'
      WHEN t.contract_address = 0x078d782b760474a361dda0af3839290b0ef57ad6 THEN 'USDC'
      WHEN t.contract_address = 0x20cab320a855b39f724131c69424240519573f81 THEN 'DAI'
    END as token_symbol,
    SUM(COALESCE(m.total_minted, 0) - COALESCE(b.total_burned, 0)) OVER (
      PARTITION BY t.contract_address 
      ORDER BY d.day_start
    ) as current_supply
  FROM daily_dates d
  CROSS JOIN (SELECT DISTINCT contract_address FROM token_mints) t
  LEFT JOIN token_mints m ON m.day_start = d.day_start AND m.contract_address = t.contract_address
  LEFT JOIN token_burns b ON b.day_start = d.day_start AND b.contract_address = t.contract_address
)
SELECT
  day_start,
  token_symbol,
  current_supply
FROM daily_supply
ORDER BY day_start, token_symbol;