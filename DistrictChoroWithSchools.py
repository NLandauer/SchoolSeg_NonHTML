import pandas as pd
import geopandas
import folium
import requests

# read .csv of district attribute data from github into a Pandas DataFrame
url_districts = "https://raw.githubusercontent.com/NLandauer/SchoolSeg_NonHTML/main/District_SCI.csv"
districts = pd.read_csv(url_districts)

# read .csv of school point locations and attributes from github into a pandas DataFrame
url_schools = "https://raw.githubusercontent.com/NLandauer/SchoolSeg_NonHTML/main/Elementaries.csv"
schools = pd.read_csv(url_schools)

# query schools with <10% white (for special circle markers)
high_seg_schools = schools.query('Percent_White < .1')

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

# generate choropleth
folium.Choropleth(
    geo_data=district_polygons,
    name="choropleth",
    data=districts,
    columns=["DISINSTID", "Percent_White"],
    key_on="feature.properties.DISTINSTID",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Percent White Students"
).add_to(pdxmap)

# merge geojson and attribute data into a single geopandas GeoDataFrame (for tooltip)
district_gdf = geopandas.GeoDataFrame.from_features(district_polygons, crs="EPSG:4326")
district_merge = district_gdf.merge(districts, how="left", left_on="DISTINSTID", right_on="DISINSTID")

# add tooltip to district polygons
tooltip = folium.features.GeoJsonTooltip(fields=["District_Name", "Percent_Blk_Lat", "Percent_White"],
                                         aliases=["District: ", "Percent Black or Latino: ", "Percent White: "],
                                         style="""
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """, )
folium.GeoJson(district_merge,
               tooltip=tooltip,
               style_function=lambda feature: {"color": "black",
                                               "weight": 1,
                                               "fillColor": None,
                                               "fill": True,
                                               "fillOpacity": 0},
               highlight_function=lambda feat: {'color': 'black',
                                                'weight': 3,
                                                'fill': True},
               overlay=True).add_to(pdxmap)

# create a new column in dataframe with custom color bins (matches choro legend)
schools['marker_color'] = pd.cut(schools['Percent_White'], bins=6,
                                 labels=['#ffffcc', '#c7e9b4', '#7fcdbb', '#41b6c4', '#2c7fb8', '#253494'])

# add open circles for high seg schools (layer below other point markers)
for i in range(0, len(high_seg_schools)):
    folium.CircleMarker(
        location=[high_seg_schools.iloc[i]['Latitude'], high_seg_schools.iloc[i]['Longitude']],
        color='orange',
        weight=4,
        radius=20,
        fill=False
    ).add_to(pdxmap)

# add schools to map as circles with custom color and simple popups
for i in range(0, len(schools)):
    folium.CircleMarker(
        location=[schools.iloc[i]['Latitude'], schools.iloc[i]['Longitude']],
        color='black',
        weight=1,
        radius=5,
        fill_color=schools.iloc[i]['marker_color'],
        fill_opacity=0.3,
        fill=False,
        popup=schools.iloc[i]['School_Name'],
    ).add_to(pdxmap)


# display map in default browser for testing
# pdxmap.show_in_browser()

# export to html file
pdxmap.save('DistrictChoroWithSchools.html')
