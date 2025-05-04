with products as (
    select * from "iceberg"."default_staging"."stg_products"
),

sales as (
    select * from "iceberg"."default_staging"."stg_sales"
),

sales_by_product as (
    select
        p.product_id,
        p.product_name,
        p.category,
        p.price as unit_price,
        sum(s.quantity) as total_quantity_sold,
        sum(s.total_amount) as total_revenue,
        min(s.sale_date) as first_sale_date,
        max(s.sale_date) as last_sale_date,
        count(distinct s.sale_id) as number_of_sales
    from products p
    inner join sales s on p.product_id = s.product_id
    group by 1, 2, 3, 4
)

select * from sales_by_product