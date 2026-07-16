with source as (

    select raw_data, loaded_at
    from {{ source('raw', 'job_offers') }}

),

renamed as (

    select
        raw_data:id::varchar                       as job_id,
        raw_data:title::varchar                     as title,
        raw_data:company.display_name::varchar      as company_name,
        raw_data:location.display_name::varchar     as location,
        raw_data:salary_min::float                  as salary_min,
        raw_data:salary_max::float                  as salary_max,
        raw_data:category.label::varchar            as category,
        raw_data:contract_type::varchar             as contract_type,
        raw_data:created::timestamp_ntz             as created_at,
        raw_data:description::varchar               as description,
        raw_data:redirect_url::varchar               as job_url,
        loaded_at

    from source

)

select * from renamed