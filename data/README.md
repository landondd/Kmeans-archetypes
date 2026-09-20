# Data

The data isn't committed to this repo because of its size (about 13 GB). To run the pipeline, place it as follows:

```
data/
  epc/                       # domestic EPC CSVs, one per local authority
    ...domestic-E06000009-Blackpool.csv
    ...
  boundaries/
    countries_2022.geojson   # used only for the map outlines
```

## EPC records

[SOURCE: add where the EPC files were downloaded from]

Files should be named `domestic-<local authority code>-<local authority name>.csv`. The preprocessing script reads every CSV under `data/epc/`, including subfolders, and takes each local authority's name from its filename. It expects `Latitude` and `Longitude` columns for mapping.

## Boundaries

[SOURCE: add where countries_2022.geojson was downloaded from]

The mapping script uses the `CTRY22NM` column to draw the England and Wales outline.
