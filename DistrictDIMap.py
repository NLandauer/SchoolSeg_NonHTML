import pandas as pd
import geopandas
import folium
import requests

# read .csv of district attribute data into a Pandas DataFrame
url_districts = "https://raw.githubusercontent.com/NLandauer/SchoolSeg_NonHTML/main/District_SCI.csv"
districts = pd.read_csv(url_districts)

# round dissimilarity index to 2 decimal places
districts.DI = districts.DI.round(decimals=2)

# define the map's center starting point
map_start_point = [45.504297, -122.816187]

# Access url for custom Mapbox tileset
mapbox_url = ("https://api.mapbox.com/styles/v1/nlandauer/clphqayo7006j01ol8ov94s2r/tiles/256/{z}/{x}/{"
              "y}@2x?access_token=pk.eyJ1IjoibmxhbmRhdWVyIiwiYSI6ImNsbzNtaGt1bzIyYWYyaW82eHBzeml2aG8ifQ"
              ".PUm_asgwYlN05xkz9Gyz4g")

# initialize the map
pdxmap = folium.Map(location=map_start_point,
                    zoom_start=10,
                    tiles=mapbox_url,
                    attr="Mapbox")

# retrieve geoJSON district polygons
district_polygons = requests.get("https://raw.githubusercontent.com/NLandauer/SchoolSeg_NonHTML/main"
                                 "/cleaned_districts.geojson").json()

# generate choropleth with highlight function on
folium.Choropleth(
    geo_data=district_polygons,
    name="choropleth",
    data=districts,
    columns=["DISINSTID", "DI"],
    key_on="feature.properties.DISTINSTID",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Dissimilarity Index",
    highlight=True
).add_to(pdxmap)

# merge geojson and attribute data into a single geopandas GeoDataFrame (for tooltip)
district_gdf = geopandas.GeoDataFrame.from_features(district_polygons, crs="EPSG:4326")
district_merge = district_gdf.merge(districts, how="left", left_on="DISTINSTID", right_on="DISINSTID")

# add tooltip to district polygons
tooltip = folium.features.GeoJsonTooltip(fields=["District_Name","DI"],
                                         aliases=["District: ", "Dissimilarity Index: "],
                                        style="""
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,)
folium.GeoJson(district_merge,
               tooltip=tooltip,
               style_function=lambda feature: {"color": "black",
                                               "weight": 1,
                                               "fillColor": None,
                                               "fill": True,
                                               "fillOpacity": 0},
               highlight_function= lambda feat: {'fillColor': 'green'},
               overlay=True).add_to(pdxmap)

# to display map for testing
# pdxmap.show_in_browser()

# export to html file
pdxmap.save('DistrictDIMap.html')



