{{
    config(
        materialized='table'
    )
}}

SELECT 
    json_extract_string(topics, '$[0]') AS topic0,
    CASE WHEN json_array_length(topics) >= 2 THEN json_extract_string(topics, '$[1]') END AS topic1,
    CASE WHEN json_array_length(topics) >= 3 THEN json_extract_string(topics, '$[2]') END AS topic2,
    CASE WHEN json_array_length(topics) >= 4 THEN json_extract_string(topics, '$[3]') END AS topic3,
    address,
    data,
    block_number,
    block_hash,
    time_stamp,
    gas_price,
    gas_used,
    log_index,
    transaction_hash,
    transaction_index

FROM {{ source('raw_curve', 'logs') }} 