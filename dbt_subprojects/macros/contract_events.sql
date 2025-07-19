{% macro filter_by_event_signature(logs_ref, event_signature, event_name='') %}
select *
    {% if event_name %}
    , '{{ event_name }}' as event_name
    {% endif %}
from {{ logs_ref }}
where topic0 = '{{ event_signature }}'
{% endmacro %}

{% macro filter_by_contract_address(logs_ref, contract_address, contract_name='') %}
select *
    {% if contract_name %}
    , '{{ contract_name }}' as contract_name  
    {% endif %}
from {{ logs_ref }}
where lower(contract_address) = lower('{{ contract_address }}')
{% endmacro %}

{% macro extract_contract_deployment(logs_ref) %}
-- Extract contract deployment events (topic0 = null, from_address = null)
select 
    contract_address as deployed_contract,
    {{ hex_to_address('topic1') }} as deployer_address,
    block_number as deployment_block,
    block_timestamp as deployment_time,
    transaction_hash as deployment_tx
from {{ logs_ref }}
where topic0 is null
    and topic1 is not null
{% endmacro %}