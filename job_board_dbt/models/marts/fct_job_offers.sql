with job_offers as (

    select *
    from {{ ref('stg_job_offers') }}

),

deduped_job_offers as (

    select
        *
    from job_offers
    qualify row_number() over (
        partition by job_id
        order by created_at desc nulls last
    ) = 1

),

final as (

    select
        job_offers.job_id,
        job_offers.title,
        dim_company.company_id,
        dim_location.location_id,
        job_offers.salary_min,
        job_offers.salary_max,
        (job_offers.salary_min + job_offers.salary_max) / 2  as salary_avg,
        job_offers.category,
        job_offers.contract_type,
        job_offers.created_at,
        job_offers.job_url

    from deduped_job_offers as job_offers
    left join {{ ref('dim_company') }} as dim_company
        on job_offers.company_name = dim_company.company_name
    left join {{ ref('dim_location') }} as dim_location
        on job_offers.location = dim_location.location
    where job_offers.title is not null

)

select * from final