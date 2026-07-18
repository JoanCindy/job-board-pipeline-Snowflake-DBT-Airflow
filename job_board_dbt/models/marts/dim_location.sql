with distinct_locations as (

    select distinct
        location
    from {{ ref('stg_job_offers') }}
    where location is not null

),

final as (

    select
        row_number() over (order by location)  as location_id,
        location

    from distinct_locations

)

select * from final