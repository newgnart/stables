{{
    config(
        materialized='table'
    )
}}

{{ extract_erc20_transfers(ref('stg_usde_contract_logs'), decimals=18)}}