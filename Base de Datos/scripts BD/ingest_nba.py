# ingest_nba.py
import os, re, time, tempfile, random
from typing import Tuple, Callable, Any, Dict
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
import pyarrow as pa
import pyarrow.parquet as pq

# --- Configuración opcional de headers para nba_api (seguro en cualquier versión) ---
try:
    # Intento 1: path nuevo
    from nba_api.stats.library.http import NBAStatsHTTP  # type: ignore
except Exception:
    try:
        # Intento 2: path antiguo
        from nba_api.library.http import NBAStatsHTTP  # type: ignore
    except Exception:
        NBAStatsHTTP = None  # no disponible en esta versión

def _configure_nba_headers():
    if NBAStatsHTTP is None:
        return  # no hay clase -> no configuramos (silent no-op)
    # Solo si la clase tiene _session y headers
    sess = getattr(NBAStatsHTTP, "_session", None)
    if getattr(sess, "headers", None) is None:
        return
    try:
        sess.headers.clear()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://www.nba.com",
            "Referer": "https://www.nba.com/",
            "Connection": "keep-alive",
        })
    except Exception:
        # Si algo falla, lo ignoramos; el script sigue funcionando
        pass

_configure_nba_headers()



from google.cloud import bigquery, storage
from google.oauth2 import service_account

# nba_api
from nba_api.stats.endpoints import (
    commonplayerinfo,          # CommonPlayerInfo
    playercareerstats,         # PlayerCareerStats
    teaminfocommon,            # TeamInfoCommon
    draftcombineplayeranthro,  # DraftCombinePlayerAnthro
    boxscoretraditionalv2,     # BoxScoreTraditionalV2
    leaguegamefinder,          # LeagueGameFinder
    boxscoresummaryv2,         # BoxScoreSummaryV2
    commonallplayers           # CommonAllPlayers (para "player")
)

# ========= CONFIG =========
PROJECT_ID  = "nba-henry-476501"
DATASET_ID  = "nbadataset"
BUCKET_NAME = "bucketnba"
KEY_PATH    = r"C:\Users\Shai-Hulud\Downloads\nba-ingest.json"

# Temporadas a procesar
SEASONS = [f"{y}-{str(y+1)[-2:]}" for y in range(2024, 2025)]
DATASET_REF = f"{PROJECT_ID}.{DATASET_ID}"

# Límites/tiempos (robustos)
MAX_GAMES_PER_SEASON = 60
SLEEP_SEC   = 1.2
TIMEOUT     = 45
MAX_RETRIES = 8
BACKOFF_BASE = 1.4

# ========= CLIENTES =========
creds = service_account.Credentials.from_service_account_file(KEY_PATH)
bq = bigquery.Client(project=PROJECT_ID, credentials=creds)
gcs = storage.Client(project=PROJECT_ID, credentials=creds)
bucket = gcs.bucket(BUCKET_NAME)

# ========= HELPERS =========
def normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    df = df.copy()
    df.columns = [re.sub(r"\W+", "_", c.strip().lower()) for c in df.columns]
    return df

def dedupe_cols(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.loc[:, ~df.columns.duplicated()]

def ensure_unique_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    seen = {}
    new_cols = []
    for c in df.columns:
        if c not in seen:
            seen[c] = 0
            new_cols.append(c)
        else:
            seen[c] += 1
            new_cols.append(f"{c}_dup{seen[c]}")
    df.columns = new_cols
    return df

def ensure_dataset():
    try:
        ds = bq.get_dataset(DATASET_REF)
        print(f"Dataset detectado: {DATASET_REF} (location={ds.location})")
    except Exception:
        ds = bigquery.Dataset(DATASET_REF)
        ds.location = "northamerica-south1"
        bq.create_dataset(ds)
        print(f"Dataset creado: {DATASET_REF} (location=northamerica-south1)")

def get_bq_schema(table: str) -> Dict[str, str]:
    try:
        t = bq.get_table(f"{DATASET_REF}.{table}")
        return {f.name: f.field_type for f in t.schema}
    except Exception:
        return {}

def cast_series(s: pd.Series, bq_type: str) -> pd.Series:
    if bq_type in ("INT64", "INTEGER"):
        return pd.to_numeric(s, errors="coerce").astype("Int64")
    if bq_type in ("FLOAT64", "FLOAT", "NUMERIC", "BIGNUMERIC"):
        return pd.to_numeric(s, errors="coerce").astype("float64")
    if bq_type in ("BOOL", "BOOLEAN"):
        return (
            s.astype(str)
             .str.strip()
             .str.upper()
             .map({"1": True, "0": False, "TRUE": True, "FALSE": False,
                   "T": True, "F": False, "Y": True, "N": False})
        )
    if bq_type == "TIMESTAMP":
        return pd.to_datetime(s, errors="coerce", utc=True)
    return s.astype(str)

def align_to_bq(table: str, df: pd.DataFrame) -> pd.DataFrame:
    bq_schema = get_bq_schema(table)
    if not bq_schema or df is None or df.empty:
        return df

    df = df.copy()

    if table == "player":
        low = {c.lower(): c for c in df.columns}
        if "person_id" in low:
            df.rename(columns={low["person_id"]: "id"}, inplace=True)
        if "full_name" not in df.columns and "display_first_last" in low:
            df.rename(columns={low["display_first_last"]: "full_name"}, inplace=True)
        keep = list(bq_schema.keys())
        for k in keep:
            if k not in df.columns:
                df[k] = pd.NA
        df = df[keep]

    if table == "common_player_info":
        if "birthdate" in df.columns and bq_schema.get("birthdate") == "TIMESTAMP":
            df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce", utc=True)
        if "season_exp" in df.columns and bq_schema.get("season_exp") in ("FLOAT","FLOAT64"):
            df["season_exp"] = pd.to_numeric(df["season_exp"], errors="coerce").astype("float64")

    if table == "draft_combine_stats":
        if "height_w_shoes" in df.columns and bq_schema.get("height_w_shoes") in ("FLOAT","FLOAT64"):
            df["height_w_shoes"] = pd.to_numeric(df["height_w_shoes"], errors="coerce").astype("float64")

    common_cols = [c for c in df.columns if c in bq_schema]
    if not common_cols:
        return df
    df = df[common_cols]
    for c in common_cols:
        try:
            df[c] = cast_series(df[c], bq_schema[c])
        except Exception:
            pass
    return df

def _downcast_datetimes_to_us(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pa.DataType]]:
    df = df.copy()
    pa_schema_map: Dict[str, pa.DataType] = {}
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            if getattr(df[col].dtype, "tz", None) is not None:
                df[col] = df[col].dt.tz_convert("UTC").dt.floor("us")
                pa_schema_map[col] = pa.timestamp("us", tz="UTC")
            else:
                s = pd.to_datetime(df[col], errors="coerce", utc=True).dt.floor("us")
                df[col] = s
                pa_schema_map[col] = pa.timestamp("us", tz="UTC")
    return df, pa_schema_map

def to_parquet_gcs(df: pd.DataFrame, path: str, table: str = None):
    if df is None or df.empty:
        return None

    if table == "common_player_info":
        if "season_exp" in df.columns:
            df["season_exp"] = pd.to_numeric(df["season_exp"], errors="coerce").astype("float64")

    df_fix, pa_schema_map = _downcast_datetimes_to_us(df)

    fields = []
    for c in df_fix.columns:
        if c in pa_schema_map:
            fields.append(pa.field(c, pa_schema_map[c]))

    if fields:
        base_schema = pa.schema(fields)
        table_pa = pa.Table.from_pandas(df_fix, schema=base_schema, preserve_index=False)
    else:
        table_pa = pa.Table.from_pandas(df_fix, preserve_index=False)

    os.makedirs(tempfile.gettempdir(), exist_ok=True)
    tmp = os.path.join(tempfile.gettempdir(), os.path.basename(path))
    pq.write_table(table_pa, tmp, version="2.6")
    blob = bucket.blob(path)
    blob.upload_from_filename(tmp)
    return f"gs://{BUCKET_NAME}/{path}"

def load_parquet_to_bq(gcs_uri: str, table: str):
    if not gcs_uri:
        return
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition="WRITE_APPEND",
        schema_update_options=[
            bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
            bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION,
        ],
    )
    bq.load_table_from_uri(gcs_uri, f"{DATASET_REF}.{table}", job_config=job_config).result()

def fetch_df(endpoint_fn: Callable[..., Any], *, label: str, retries: int = MAX_RETRIES, **kwargs) -> pd.DataFrame:
    for attempt in range(retries):
        try:
            obj = endpoint_fn(timeout=TIMEOUT, **kwargs)
            dfs = obj.get_data_frames()
            if dfs and len(dfs) > 0:
                return dfs[0]
            return pd.DataFrame()
        except Exception as e:
            wait = (BACKOFF_BASE * (2 ** attempt)) + random.uniform(0, 0.4)
            print(f"  retry {label} ({attempt+1}/{retries}): {e} -> sleep {wait:.1f}s")
            time.sleep(wait)
    try:
        obj = endpoint_fn(timeout=TIMEOUT, **kwargs)
        dfs = obj.get_data_frames()
        if dfs and len(dfs) > 0:
            return dfs[0]
    except Exception as e:
        print(f"  skip {label}: {e}")
    return pd.DataFrame()

# ========= EXTRACTORES =========
def get_common_player_info() -> pd.DataFrame:
    df = fetch_df(commonplayerinfo.CommonPlayerInfo, label="common_player_info", player_id=2544)
    return normalize(df)

def get_players() -> pd.DataFrame:
    df = fetch_df(commonallplayers.CommonAllPlayers, label="players", is_only_current_season=0)
    return normalize(df)

def get_team_info() -> pd.DataFrame:
    df = fetch_df(teaminfocommon.TeamInfoCommon, label="team_info_common", team_id=1610612747)
    return normalize(df)

def get_draft_combine() -> pd.DataFrame:
    df = fetch_df(draftcombineplayeranthro.DraftCombinePlayerAnthro, label="draft_combine_stats")
    return normalize(df)

def get_player_career_stats() -> pd.DataFrame:
    df = fetch_df(playercareerstats.PlayerCareerStats, label="player_career_stats", player_id=2544)
    return normalize(df)

def get_boxscore_traditional(season: str = None) -> pd.DataFrame:
    games_df = fetch_df(leaguegamefinder.LeagueGameFinder, label="leaguegamefinder", season_nullable=season)
    if games_df.empty or "GAME_ID" not in games_df.columns:
        return pd.DataFrame()

    df_all = []
    game_ids = list(games_df["GAME_ID"])[:MAX_GAMES_PER_SEASON]
    total = len(game_ids)
    for i, gid in enumerate(game_ids, 1):
        try:
            df = fetch_df(boxscoretraditionalv2.BoxScoreTraditionalV2, label=f"boxscore {gid}", game_id=gid)
            if df is None or df.empty:
                continue
            low = {c.lower(): c for c in df.columns}
            if "game_id" not in low:
                df["GAME_ID"] = gid
            df = normalize(df)
            df_all.append(df)
        except Exception as e:
            print(f"  boxscore skip {gid}: {e}")

        if i % 25 == 0 or i == total:
            print(f"  boxscores {i}/{total}")
        time.sleep(SLEEP_SEC)

    if not df_all:
        return pd.DataFrame()
    out = pd.concat(df_all, ignore_index=True)
    out = dedupe_cols(out)
    out = ensure_unique_columns(out)
    return out

def get_game_summary_and_other_stats(season: str = None):
    games_df = fetch_df(leaguegamefinder.LeagueGameFinder, label="leaguegamefinder", season_nullable=season)
    if games_df.empty or "GAME_ID" not in games_df.columns:
        return pd.DataFrame(), pd.DataFrame()

    summaries, others = [], []
    game_ids = list(games_df["GAME_ID"])[:MAX_GAMES_PER_SEASON]
    total = len(game_ids)

    for i, gid in enumerate(game_ids, 1):
        try:
            bs = boxscoresummaryv2.BoxScoreSummaryV2(game_id=gid, timeout=TIMEOUT)
            frames = bs.get_data_frames()
            gsum  = frames[0] if len(frames) > 0 else pd.DataFrame()
            other = frames[5] if len(frames) > 5 else pd.DataFrame()

            if not gsum.empty:
                low = {c.lower(): c for c in gsum.columns}
                if "game_id" not in low:
                    gsum["GAME_ID"] = gid
                gsum = normalize(gsum)
                summaries.append(gsum)

            if not other.empty:
                low = {c.lower(): c for c in other.columns}
                if "game_id" not in low:
                    other["GAME_ID"] = gid
                other = normalize(other)
                others.append(other)

        except Exception as e:
            print(f"  summary/other skip {gid}: {e}")

        if i % 25 == 0 or i == total:
            print(f"  summaries {i}/{total}")
        time.sleep(SLEEP_SEC)

    gs = pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame()
    os = pd.concat(others,    ignore_index=True) if others    else pd.DataFrame()

    if not gs.empty:
        gs = dedupe_cols(gs)
        gs = ensure_unique_columns(gs)
    if not os.empty:
        os = dedupe_cols(os)
        os = ensure_unique_columns(os)

    return gs, os

# ========= MAIN =========
def main():
    print("Iniciando proceso historico (2025-2026)")
    ensure_dataset()

    for season in SEASONS:
        print(f"\nProcesando temporada {season}...")

        # 1) common_player_info
        try:
            df = get_common_player_info()
            df = align_to_bq("common_player_info", df)
            uri = to_parquet_gcs(df, f"bronze/{season}/common_player_info.parquet", table="common_player_info")
            load_parquet_to_bq(uri, "common_player_info")
            print("OK: common_player_info")
        except Exception as e:
            print(f"WARN common_player_info: {e}")

        # 2) player
        try:
            df = get_players()
            df = align_to_bq("player", df)
            uri = to_parquet_gcs(df, f"bronze/{season}/player.parquet", table="player")
            load_parquet_to_bq(uri, "player")
            print("OK: player")
        except Exception as e:
            print(f"WARN player: {e}")

        # 3) team_info_common
        try:
            df = get_team_info()
            df = align_to_bq("team_info_common", df)
            uri = to_parquet_gcs(df, f"bronze/{season}/team_info_common.parquet", table="team_info_common")
            load_parquet_to_bq(uri, "team_info_common")
            print("OK: team_info_common")
        except Exception as e:
            print(f"WARN team_info_common: {e}")

        # 4) draft_combine_stats
        try:
            df = get_draft_combine()
            df = align_to_bq("draft_combine_stats", df)
            uri = to_parquet_gcs(df, f"bronze/{season}/draft_combine_stats.parquet", table="draft_combine_stats")
            load_parquet_to_bq(uri, "draft_combine_stats")
            print("OK: draft_combine_stats")
        except Exception as e:
            print(f"WARN draft_combine_stats: {e}")

        # 5) player_career_stats
        try:
            df = get_player_career_stats()
            df = align_to_bq("player_career_stats", df)
            uri = to_parquet_gcs(df, f"bronze/{season}/player_career_stats.parquet", table="player_career_stats")
            load_parquet_to_bq(uri, "player_career_stats")
            print("OK: player_career_stats")
        except Exception as e:
            print(f"WARN player_career_stats: {e}")

        # 6) game_summary, other_stats, boxscore_traditional
        try:
            box = get_boxscore_traditional(season)
            gs, os = get_game_summary_and_other_stats(season)

            if not box.empty:
                box = align_to_bq("boxscore_traditional", box)
                uri = to_parquet_gcs(box, f"bronze/{season}/boxscore_traditional.parquet", table="boxscore_traditional")
                load_parquet_to_bq(uri, "boxscore_traditional")
                print("OK: boxscore_traditional")

            if not gs.empty:
                gs = align_to_bq("game_summary", gs)
                uri = to_parquet_gcs(gs, f"bronze/{season}/game_summary.parquet", table="game_summary")
                load_parquet_to_bq(uri, "game_summary")
                print("OK: game_summary")

            if not os.empty:
                os = align_to_bq("other_stats", os)
                uri = to_parquet_gcs(os, f"bronze/{season}/other_stats.parquet", table="other_stats")
                load_parquet_to_bq(uri, "other_stats")
                print("OK: other_stats")
        except Exception as e:
            print(f"WARN game data: {e}")

    print("\nIngesta historica completa (2025-2026).")

if __name__ == "__main__":
    main()
