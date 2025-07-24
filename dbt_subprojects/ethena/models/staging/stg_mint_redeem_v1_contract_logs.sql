{{
    config(
        materialized='table'
    )
}}

{{ process_contract_logs('raw_usde_contracts', 'mint_redeem_v1_contract_logs') }}