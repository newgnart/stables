WITH tracked_addresses AS (
  SELECT 
    address,
    label
  FROM (VALUES
    (0x1F98400000000000000000000000000000000004, 'PoolManager'),
    (0xb0DcFEeF31375AcD194aDfFcf6F3e685D5708981, '0xb0Dc'),
    (0x8a474ec171133B03318e23955D99Aa251442Ee89, '0x8a47'),
    (0x5C75bFB6194D7D763d33eA292cBc50cDa806451B, 'UniswapV3Pool'),
    (0xdD824635E10545eEA64de4e95E6CA3acDbb59d28, '0xdD82')
  ) AS t(address, label)
),
stablecoins AS (
  SELECT address
  FROM (VALUES
    (0x9151434b16b9763660705744891fa906f660ecc5)  -- USDT
  ) AS t(address)
),
tracked_balances AS (
  SELECT
    ta.label as address_label,
    SUM(CASE 
      WHEN "to" = ta.address THEN amount
      WHEN "from" = ta.address THEN -amount
      ELSE 0
    END) as balance
  FROM tokens.transfers t
  JOIN tracked_addresses ta ON t."to" = ta.address OR t."from" = ta.address
  WHERE
    blockchain = 'unichain'
    AND contract_address IN (SELECT address FROM stablecoins)
  GROUP BY 1
),
total_supply AS (
  SELECT 
    SUM(CASE 
      WHEN "from" = 0x0000000000000000000000000000000000000000 THEN amount  -- Mint
      WHEN "to" = 0x0000000000000000000000000000000000000000 THEN -amount   -- Burn
      ELSE 0
    END) as total
  FROM tokens.transfers t
  WHERE
    blockchain = 'unichain'
    AND contract_address IN (SELECT address FROM stablecoins)
)
SELECT
  address_label,
  balance as total_balance
FROM tracked_balances
WHERE balance > 0

UNION ALL

SELECT
  'Other Addresses' as address_label,
  (SELECT total FROM total_supply) - (SELECT SUM(balance) FROM tracked_balances) as total_balance
WHERE (SELECT total FROM total_supply) - (SELECT SUM(balance) FROM tracked_balances) > 0

ORDER BY 
  CASE 
    WHEN address_label = 'Other Addresses' THEN 1
    ELSE 0
  END,
  total_balance DESC; 