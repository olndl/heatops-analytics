create or replace view mart_installation_funnel as
select
  h.region,
  p.product_type,
  count(distinct l.lead_id) as leads,
  count(distinct s.survey_id) as surveys,
  count(distinct case when l.status = 'won' then l.lead_id end) as won_leads,
  count(distinct i.installation_id) as installations,
  count(distinct case when i.status = 'completed' then i.installation_id end) as completed_installations,
  round(count(distinct s.survey_id)::double / nullif(count(distinct l.lead_id), 0), 3) as lead_to_survey_rate,
  round(count(distinct case when i.status = 'completed' then i.installation_id end)::double / nullif(count(distinct s.survey_id), 0), 3) as survey_to_completed_rate
from stg_leads l
join raw_homes h on h.home_id = l.home_id
left join stg_surveys s on s.lead_id = l.lead_id
left join stg_installations i on i.lead_id = l.lead_id
left join raw_energy_products p on p.product_id = i.product_id
group by 1, 2;
