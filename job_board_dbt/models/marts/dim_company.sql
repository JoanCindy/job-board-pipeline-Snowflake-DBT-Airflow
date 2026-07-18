with distinct_companies as (

    select distinct
        company_name
    from {{ ref('stg_job_offers') }}
    where company_name is not null

),

final as (

    select
        row_number() over (order by company_name)  as company_id,
        company_name

    from distinct_companies

)

select * from final