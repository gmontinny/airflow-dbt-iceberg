with products as (
    select * from "iceberg"."default_staging"."stg_products"
),

sales as (
    select * from "iceberg"."default_staging"."stg_sales"
),

sales_by_category as (
    select
        p.category,
        count(distinct p.product_id) as number_of_products,
        sum(s.quantity) as total_quantity_sold,
        sum(s.total_amount) as total_revenue,
        avg(s.total_amount / s.quantity) as average_unit_price,
        min(s.sale_date) as first_sale_date,
        max(s.sale_date) as last_sale_date
    from products p
    inner join sales s on p.product_id = s.product_id
    group by 1
)

select * from sales_by_category