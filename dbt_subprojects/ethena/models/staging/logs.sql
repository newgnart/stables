{{
    config(
        materialized='table'
    )
}}

SELECT DISTINCT
    json_extract_string(topics, '$[0]') AS topic0,
    CASE WHEN json_array_length(topics) >= 2 THEN json_extract_string(topics, '$[1]') END AS topic1,
    CASE WHEN json_array_length(topics) >= 3 THEN json_extract_string(topics, '$[2]') END AS topic2,
    CASE WHEN json_array_length(topics) >= 4 THEN json_extract_string(topics, '$[3]') END AS topic3,
    address,
    data,
    ('0x' || ltrim(block_number, '0x'))::bigint AS block_number,
    block_hash,
    to_timestamp(('0x' || ltrim(time_stamp, '0x'))::bigint) AS time_stamp,
    ('0x' || ltrim(gas_price, '0x'))::bigint AS gas_price,
    ('0x' || ltrim(gas_used, '0x'))::bigint AS gas_used,
    log_index,
    transaction_hash,
    transaction_index

FROM {{ source('raw_ethena', 'logs') }} 