
  create or replace view
    "iceberg"."default_staging"."stg_sales"
  security definer
  as
    with source as (
    select * from iceberg.raw.sales
),

renamed as (
    select
        sale_id,
        product_id,
        quantity,
        total as total_amount,
        date as sale_date
    from source
)

select * from renamed
  ;
