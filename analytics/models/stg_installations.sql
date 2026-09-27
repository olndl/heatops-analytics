create or replace view stg_installations as
select
  installation_id,
  lead_id,
  product_id,
  technician_id,
  cast(scheduled_at as date) as scheduled_at,
  try_cast(nullif(completed_at, '') as date) as completed_at,
  status,
  cast(gross_margin_pct as double) as gross_margin_pct
from raw_installations;
