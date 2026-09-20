"""Shared paths for the pipeline. All paths are relative to the repository root."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Inputs (not committed; see data/README.md)
DATA_DIR = ROOT / "data" / "epc"
BOUNDARIES_FILE = ROOT / "data" / "boundaries" / "countries_2022.geojson"

# Intermediate files written by the pipeline
PROCESSED_DIR = ROOT / "processed"
SCALED_FILE = PROCESSED_DIR / "epc_scaled.parquet"
CLEAN_FILE = PROCESSED_DIR / "epc_clean.parquet"
CLUSTERED_FILE = PROCESSED_DIR / "epc_clustered.parquet"

# Outputs
FIGURES_DIR = ROOT / "outputs" / "figures"
TABLES_DIR = ROOT / "outputs" / "tables"

for folder in (PROCESSED_DIR, FIGURES_DIR, TABLES_DIR):
    folder.mkdir(parents=True, exist_ok=True)
