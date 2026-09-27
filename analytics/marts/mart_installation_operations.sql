create or replace view mart_installation_operations as
select
  h.region,
  p.product_type,
  i.status,
  count(*) as installation_count,
  median(date_diff('day', s.survey_at, coalesce(i.completed_at, i.scheduled_at))) as median_days_from_survey,
  sum(case when i.status in ('scheduled', 'delayed') then 1 else 0 end) as open_backlog,
  round(avg(i.gross_margin_pct), 3) as avg_gross_margin_pct,
  round(
    sum(
      case
        when i.status = 'completed'
        then cast(p.annual_co2_savings_tons as double)
        else 0
      end
    ),
    2
  ) as annual_co2_savings_tons
from stg_installations i
join stg_leads l on l.lead_id = i.lead_id
join raw_homes h on h.home_id = l.home_id
join stg_surveys s on s.lead_id = i.lead_id
join raw_energy_products p on p.product_id = i.product_id
group by 1, 2, 3;
