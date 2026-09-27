select l.lead_id, l.home_id
from stg_leads l
left join raw_homes h on h.home_id = l.home_id
where h.home_id is null;
