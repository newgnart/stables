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
        when topic0 = '0xf114ca9eb82947af39f957fa726280fd3d5d81c3d7635a4aeb5c302962856eba' then 'mint'
        when topic0 = '0x18fd144d7dbcbaa6f00fd47a84adc7dc3cc64a326ffa2dc7691a25e3837dba03' then 'redeem'
    end as event_type,
    
    {{ hex_to_address('topic1') }} as caller,
    
    -- topic2, topic3 are benefactor, beneficiary (convert to addresses)
    {{ hex_to_address('topic2') }} as benefactor,
    {{ hex_to_address('topic3') }} as beneficiary,
    
    -- Decode data field into 4 columns for v1 structure
    -- V1 data: minter (address), collateral_asset (address), collateral_amount (uint256), usde_amount (uint256)
    {{ hex_to_address("substring(data, 3, 64)") }} as collateral_asset,
    {{ hex_to_numeric("substring(data, 67, 64)") }} as collateral_amount,
    {{ hex_to_numeric("substring(data, 131, 64)") }} as usde_amount

from {{ ref('stg_mint_redeem_v1_contract_logs') }}
where topic0 in (
    '0xf114ca9eb82947af39f957fa726280fd3d5d81c3d7635a4aeb5c302962856eba',  -- mint 
    '0x18fd144d7dbcbaa6f00fd47a84adc7dc3cc64a326ffa2dc7691a25e3837dba03'   -- redeem 
)
order by block_number, log_index