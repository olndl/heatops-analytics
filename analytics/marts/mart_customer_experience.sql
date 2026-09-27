create or replace view mart_customer_experience as
select
  h.region,
  p.product_type,
  count(f.feedback_id) as feedback_count,
  round(avg(cast(f.score as integer)), 2) as avg_score,
  round(
    sum(case when cast(f.score as integer) >= 4 then 1 else 0 end)::double
    / nullif(count(f.feedback_id), 0),
    3
  ) as positive_feedback_rate
from raw_customer_feedback f
join stg_installations i on i.installation_id = f.installation_id
join stg_leads l on l.lead_id = i.lead_id
join raw_homes h on h.home_id = l.home_id
join raw_energy_products p on p.product_id = i.product_id
group by 1, 2;
