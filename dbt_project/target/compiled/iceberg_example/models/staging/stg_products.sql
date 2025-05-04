with source as (
    select * from iceberg.raw.products
),

renamed as (
    select
        id as product_id,
        name as product_name,
        category,
        price,
        date as created_date
    from source
)

select * from renamed