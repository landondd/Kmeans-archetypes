import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
import config

CELL_SIZE = 10_000
MIN_HOMES = 30

df = pd.read_parquet(
    config.CLUSTERED_FILE,
    columns=['cluster', 'Latitude', 'Longitude']
)
df = df[~df['cluster'].isin([6, 11])].copy()
df = df[df['Latitude'] <= 55.82]
df = df.dropna(subset=['Latitude', 'Longitude'])

# Geopandas source: https://www.datacamp.com/tutorial/geopandas-tutorial-geospatial-analysis?utm_cid=23781701478&utm_aid=196565213035&utm_campaign=260417_1-ps-dscia~amx-tofu~python_2-b2c_3-emea_4-prc_5-na_6-na_7-le_8-pdsh-go_9-nb-e_10-na_11-na&utm_loc=9198486-&utm_mtd=p-c&utm_kw=geospatial%20data%20python&utm_source=google&utm_medium=paid_search&utm_content=ps-dscia~emea-en~amx~tofu~tutorial~python&gad_source=1&gad_campaignid=23781701478&gbraid=0AAAAADQ9WsElggQRfQa0uz3BX0-Y4ZrSV&gclid=Cj0KCQjwg5zTBhCLARIsAP2AFU4Dhgk456nKwLy8VJ1LErGey97fj4Ol7SKWzY6y-StxT45LUpaQMXkaArQLEALw_wcB

# Geopandas points from xy code: https://geopandas.org/en/stable/docs/reference/api/geopandas.points_from_xy.html
points = gpd.points_from_xy(df['Longitude'], df['Latitude'])

# Geopandas dataframe source code: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html
gdf = gpd.GeoDataFrame(df, geometry=points, crs='EPSG:4326').to_crs('EPSG:27700')
gdf['cell_x'] = (gdf.geometry.x // CELL_SIZE).astype(int)
gdf['cell_y'] = (gdf.geometry.y // CELL_SIZE).astype(int)

# Value counts in Geopandas source code: https://stackoverflow.com/questions/39132742/groupby-value-counts-on-the-dataframe-pandas
cell_counts = gdf.groupby(['cell_x', 'cell_y', 'cluster']).size().unstack(fill_value=0)
home_count = cell_counts.sum(axis=1)
share = cell_counts.div(home_count, axis=0)

cells = share.reset_index()
cells['home_count'] = home_count.values

# Building box polygons source code: https://shapely.readthedocs.io/en/stable/reference/shapely.box.html
geometries = []
for x, y in zip(cells['cell_x'], cells['cell_y']):
    left = x * CELL_SIZE
    bottom = y * CELL_SIZE
    right = left + CELL_SIZE
    top = bottom + CELL_SIZE
    square = box(left, bottom, right, top)
    geometries.append(square)

cells['geometry'] = geometries

# Coordinate Reference System source code: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html
cell_map = gpd.GeoDataFrame(cells, geometry='geometry', crs='EPSG:27700')

# England & Wales outline 
countries = gpd.read_file(
    config.BOUNDARIES_FILE
)
outline = countries[countries['CTRY22NM'].isin(['England', 'Wales'])]

# Major cities lat/long to plot on my maps
CITIES = {
    'London': (51.5074, -0.1278),
    'Birmingham': (52.4862, -1.8904),
    'Manchester': (53.4808, -2.2426),
    'Leeds': (53.8008, -1.5491),
    'Liverpool': (53.4084, -2.9916),
    'Bristol': (51.4545, -2.5879),
    'Sheffield': (53.3811, -1.4701),
    'Newcastle': (54.9783, -1.6178),
    'Cardiff': (51.4816, -3.1791),
    'Nottingham': (52.9548, -1.1581),
}

# Source code for mapping with geopandas: https://geopandas.org/en/stable/docs/user_guide/mapping.html
city_points = gpd.points_from_xy([lon for lat, lon in CITIES.values()], [lat for lat, lon in CITIES.values()])
city_gdf = gpd.GeoDataFrame({'name': list(CITIES.keys())}, geometry=city_points, crs='EPSG:4326').to_crs('EPSG:27700')

for c in sorted(df['cluster'].unique()):
    cell_map['plot_value'] = cell_map[c].where(cell_map['home_count'] >= MIN_HOMES)
    fig, ax = plt.subplots(figsize=(8, 10))
    cell_map.plot(column='plot_value', cmap='Greens', vmin=0, vmax=cell_map['plot_value'].max(),
                  edgecolor='grey', linewidth=0.1, ax=ax, missing_kwds={'color': 'lightgrey'},
                  legend=True, legend_kwds={'label': 'Share of homes'})
    outline.boundary.plot(ax=ax, color='black', linewidth=0.6)
    city_gdf.plot(ax=ax, color='red', markersize=12)
    for x, y, label in zip(city_gdf.geometry.x, city_gdf.geometry.y, city_gdf['name']):
        ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=7)

    ax.set_title(f'Cluster {c}')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / f'map_cluster_{c}.png', dpi=150)
    plt.close()
