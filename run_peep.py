from pathlib import Path
import duckdb

# Base path relative to this script
BASE_DIR = Path(__file__).resolve().parent

# Windows-safe path formatting for SQL strings
BRIDGES_CSV = str(BASE_DIR / "csv" / "bridges.csv").replace("\\", "/")
ENTITIES_CSV = str(BASE_DIR / "csv" / "entities.csv").replace("\\", "/")
REDIRECTS_CSV = str(BASE_DIR / "csv" / "redirects.csv").replace("\\", "/")

api_football_id = '184'

# Force string/VARCHAR typing on all identifier columns
bridges_table = f"read_csv('{BRIDGES_CSV}', types={{'external_id': 'VARCHAR', 'reep_id': 'VARCHAR'}})"
entities_table = f"read_csv('{ENTITIES_CSV}', types={{'reep_id': 'VARCHAR'}})"
redirects_table = f"read_csv('{REDIRECTS_CSV}', types={{'from_id': 'VARCHAR', 'to_id': 'VARCHAR'}})"

query = f"""
SELECT 
    b.external_id AS api_football_id,
    e.canonical_name AS player_name,
    COALESCE(r.to_id, b.reep_id) AS reep_id,
    fmob.external_id AS fmob_id,
    tm.external_id AS transfermarkt_id,
    opta.external_id AS opta_id,
    statsbomb.external_id AS statsbomb_id
FROM {bridges_table} b

-- Handle redirects safely
LEFT JOIN {redirects_table} r 
       ON b.reep_id = r.from_id

-- Join entity info
JOIN {entities_table} e 
  ON e.reep_id = COALESCE(r.to_id, b.reep_id)

--Map to FotMob 
LEFT JOIN {bridges_table} fmob
        ON fmob.reep_id = e.reep_id
        AND fmob.provider = 'fotmob'
        AND fmob.namespace = 'person'

-- Map to Transfermarkt
LEFT JOIN {bridges_table} tm 
       ON tm.reep_id = e.reep_id 
      AND tm.provider = 'transfermarkt' 
      AND tm.namespace = 'spieler'

-- Map to Opta
LEFT JOIN {bridges_table} opta
        ON opta.reep_id = e.reep_id
        AND opta.provider = 'opta'
        AND  opta.namespace = 'person'

-- Map to statsbomb
LEFT JOIN {bridges_table} statsbomb
        ON statsbomb.reep_id = e.reep_id
        AND statsbomb.provider = 'statsbomb'
        AND statsbomb.namespace = 'offline_player'

WHERE b.provider = 'api_football' 
  AND b.namespace = 'player'
  AND b.external_id = '{api_football_id}';
"""

df = duckdb.sql(query).df()
print(df)
