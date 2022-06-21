{% macro get_show_grant_sql(relation) %}
{{ return(adapter.dispatch("get_show_grant_sql", "dbt")(relation)) }}
{% endmacro %}

{% macro default__get_show_grant_sql(relation) %}
show grants on {{ relation.type }} {{ relation }}
{% endmacro %}

{% macro get_grant_sql(relation, grant_config) %}
{{ return(adapter.dispatch('get_grant_sql', 'dbt')(relation, grant_config)) }}
{% endmacro %}

{% macro default__get_grant_sql(relation, grant_config) %}
    {% for privilege in grant_config.keys() %}
        {% set grantee = grant_config[privilege] %}
        grant {{ privilege }} on {{ relation.type }} {{ relation }} to {{ grantee | join(', ') }}
    {% endfor %}
{% endmacro %}

{% macro get_revoke_sql(relation, grant_config) %}
{{ return(adapter.dispatch("get_revoke_sql", "dbt")(relation, grant_config)) }}
{% endmacro %}

{% macro default__get_revoke_sql(relation, grant_config) %}
    {% for privilege in grant_config.keys() %}
        {% set grantee = grant_config[privilege] %}
        revoke {{ privilege }} on {{ relation.type }} {{ relation }} from {{ grantee | join(', ') }}
        where {{ grantee }} != {{ target.user }}
    {% endfor %}
{% endmacro %}

{% macro apply_grants(relation, grant_config, should_revoke) %}
{{ return(adapter.dispatch("apply_grants", "dbt")(relation, grant_config, should_revoke)) }}
{% endmacro %}

{% macro default__apply_grants(relation, grant_config, should_revoke=True) %}
{% if grant_config %}
    {% call statement('grants') %}
        {% if should_revoke %}
            {% set current_grants =  run_query(get_show_grant_sql(relation)) %}
            {% for privilege in grant_config.keys() %}
                {% if privilege not in current_grants.keys() %}
                    {% set diff_grants = diff_of_two_dicts(grant_config, current_grants) %}
                {% endif %}
            {% endfor %}
            {{ log(diff_grants, info=True) }}
            {% set revoke_grants = get_revoke_sql(relation, diff_grants) %}
        {% endif %}
        {{ get_grant_sql(relation, grant_config) }}
    {% endcall %}
{% endif %}
{% endmacro %}

-- {% set diff_grants = { k: current_grants[k] for k in set(current_grants) - set(grant_config) } %}
-- {%- set _ =  diff_grants.update({privilege: grant_config[privilege]}) -%}