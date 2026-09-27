select installation_id, gross_margin_pct
from stg_installations
where gross_margin_pct < 0
   or gross_margin_pct > 1;
