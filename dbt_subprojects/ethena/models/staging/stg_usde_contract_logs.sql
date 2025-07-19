{{
    config(
        materialized='table'
    )
}}

{{ process_contract_logs('raw_usde_contracts', 'usde_contract_logs') }}