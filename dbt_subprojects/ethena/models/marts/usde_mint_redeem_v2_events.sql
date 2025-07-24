{{
    config(
        materialized='table'
    )
}}

select 
    chainid,
    contract_address,
    block_number,
    block_hash,
    block_timestamp,
    gas_price,
    gas_used,
    log_index,
    transaction_hash,
    transaction_index,
    
    -- Event type based on topic0
    case 
        when topic0 = '0x29ee92e51cda311463f5c9ef98c54824a4bebe45e689c37da35edc774585d437' then 'mint'
        when topic0 = '0x0ea36c5b7b274f8fe58654fe884bb9307dec1899e0312f40ae10d9b3d100cc0c' then 'redeem'
    end as event_type,
    
    -- Rename topic2, topic3 to benefactor, beneficiary and convert to addresses
    {{ hex_to_address('topic2') }} as benefactor,
    {{ hex_to_address('topic3') }} as beneficiary,
    
    -- Decode data field into 4 columns (each parameter is 64 hex chars)
    -- data includes 0x prefix, so positions are: 3-66, 67-130, 131-194, 195-258
    {{ hex_to_address("substring(data, 3, 64)") }} as caller,
    {{ hex_to_address("substring(data, 67, 64)") }} as collateral_asset,
    {{ hex_to_numeric("substring(data, 131, 64)") }} as collateral_amount,
    {{ hex_to_numeric("substring(data, 195, 64)") }} as usde_amount

from {{ ref('stg_mint_redeem_v2_contract_logs') }}
where topic0 in (
    '0x29ee92e51cda311463f5c9ef98c54824a4bebe45e689c37da35edc774585d437',  -- mint
    '0x0ea36c5b7b274f8fe58654fe884bb9307dec1899e0312f40ae10d9b3d100cc0c'   -- redeem
)
order by block_number, log_index