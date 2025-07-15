{{
    config(
        materialized='table'
    )
}}

SELECT 
    address AS token_address,
    '0x' || RIGHT(topic1, 40) AS from_address,
    '0x' || RIGHT(topic2, 40) AS to_address,
    CASE 
       WHEN data IS NULL OR data = '' OR data = '0x' THEN '0'
       ELSE ltrim(data, '0x')
    END AS amount_hex,
    CASE 
       WHEN data IS NULL OR data = '' OR data = '0x' THEN 0.0
       ELSE TRY_CAST('0x' || ltrim(data, '0x') AS HUGEINT) / 1e18
    END AS amount,
    block_number,
    block_hash,
    time_stamp,
    gas_price,
    gas_used,
    log_index,
    transaction_hash,
    transaction_index
FROM {{ ref('logs') }}
WHERE topic0 = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
    AND topic1 IS NOT NULL
    AND topic2 IS NOT NULL
ORDER BY block_number, log_index