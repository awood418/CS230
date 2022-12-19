import streamlit as st #streamlit package
import pandas as pd #package for plots and importing xlsx
import plotly.express as px #package for making graphs/plots
import folium #mapping package
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


df = pd.read_excel(
    io='California_Fire_Incidents.xlsx',
    engine='openpyxl',
    usecols='A:AG',
    nrows=1637
)

st.set_page_config(page_title='California Wildfires Analysis',
                   page_icon=':fire:', layout = 'wide')


st.subheader("California Wildfires(2013-2020)")
st.title("An Analysis on California Wildfires and Their Impacts")
st.write("""
        Below is the complete dataset used to formulate the tables and graphs shown below.\n
        Use the sidebar :arrow_left: to select and filter data.
        """)

st.sidebar.header("Wildfire selection filter")
year_range = st.sidebar.slider(
    label="Select Year Range:",
    min_value=2013,
    max_value=2020,
    value=(2013, 2020),
    step=1
)
acre_range = st.sidebar.slider(
    label="Select Acreage Range:",
    min_value=int(df["AcresBurned"].min()),
    max_value=int(df["AcresBurned"].max()),
    value=(int(df["AcresBurned"].min()), int(df["AcresBurned"].max())),
    step = 500
)
sort_by = st.sidebar.selectbox(
    label="Sort By Fire Size:",
    options=["None", "Max First", "Min First"],
)
major = st.sidebar.checkbox(
    label="View only Major Incidents",
)

if major: 
    df_selection = df.query(
        "ArchiveYear >= @year_range[0] & ArchiveYear <= @year_range[1] & AcresBurned >= @acre_range[0] & AcresBurned <= @acre_range[1] & MajorIncident == @major"
    )
else:
    df_selection = df.query(
        "ArchiveYear >= @year_range[0] & ArchiveYear <= @year_range[1] & AcresBurned >= @acre_range[0] & AcresBurned <= @acre_range[1]"
    )
if sort_by == "Max First":
    df_selection = df_selection.sort_values(by="AcresBurned", ascending=False)
elif sort_by == "Min First":
    df_selection = df_selection.sort_values(by="AcresBurned")
else:
    df_selection = df_selection

st.dataframe(df_selection, height=210)

st.title(":bar_chart: Wildfire Dashboard")
st.markdown('##')

caliMap = folium.Map(location=[37.8, -120], zoom_start=6)
df_sub = df_selection[["Longitude", "Latitude", "AcresBurned", "Name"]]
df_points = df_sub.dropna()

north_cluster = MarkerCluster(
    name="North California",
).add_to(caliMap)
mid_cluster = MarkerCluster(
    name="Mid California",
).add_to(caliMap)

south_cluster = MarkerCluster(
    name="South California",
).add_to(caliMap)

for i, row in df_points.iterrows():
    if row['Longitude'] != 0:
        fire_color = 'green'
        if row["AcresBurned"] > 50000:
            fire_color='darkred'
        elif row["AcresBurned"] < 50000 and row["AcresBurned"] > 20000:
            fire_color='red'
        elif row["AcresBurned"] < 20000 and row["AcresBurned"] > 5000:
            fire_color ='orange'
        elif row["AcresBurned"] < 5000 and row["AcresBurned"] > 2000:
            fire_color ='yellow'
        elif row["AcresBurned"] < 2000 and row["AcresBurned"] > 500:
            fire_color ='darkgreen'

        if row["Latitude"] > 38.5 and row["Latitude"] < 42.5:
            folium.Marker(
                location= (row["Latitude"], row["Longitude"]),
                popup="Fire Name:" + row["Name"] + '\n'
                + "AcresBurned:" + str(row["AcresBurned"]),
                icon=folium.Icon(color=fire_color)
            ).add_to(north_cluster)
        elif row["Latitude"] < 38.5 and row["Latitude"] > 36.5:
            folium.Marker(
                location= (row["Latitude"], row["Longitude"]),
                popup="Fire Name:" + row["Name"] + '\n'
                + "AcresBurned:" + str(row["AcresBurned"]),
                icon=folium.Icon(color=fire_color)
            ).add_to(mid_cluster)
        elif row["Latitude"] < 36.5 and row["Latitude"] > 31.5:
             folium.Marker(
                location= (row["Latitude"], row["Longitude"]),
                popup="Fire Name:" + row["Name"] + '\n'
                + "AcresBurned:" + str(row["AcresBurned"]),
                icon=folium.Icon(color=fire_color)
            ).add_to(south_cluster)

st.header("Interactive Map of California Wildfires")
folium_static(caliMap)

fig_county_counts = px.pie(
    df_selection,
    values= df_selection.groupby(by=["Counties"]).size(),
    names= df_selection["Counties"].unique(),
    title='Wildfires By County'
    )
st.plotly_chart(fig_county_counts)

st.subheader("Pie Chart Analysis")
st.write("""
        With no filters applied to the data, the distribution of wildfires appears to be evenly 
        spread across each California county, with Yolo County having the greatest portion of 
        fires at 8.88% (145 total) and Alpine County having only 0.0612% (1 total). The other 57
        counties fall somewhere in between. However, after applying filters to both the Year and 
        the Acres Burned, we find some interesting characteristics.
        """)
st.write("""
        First, by selecting different years it becomes evident that there is almost no difference 
        in wildfire county distribution per year. This is interesting since we would assume that 
        different years have larger fires in different areas, which would skew the data. This is 
        not the case.
        """)
st.write("""
        On the other hand, when we filter the data by Acres Burned, we find that there is a huge difference 
        county distribution. If we filter the dataset to only include fires with over 90,000 Acres Burned 
        we find that there are 16 such fires, with Mariposa county having 2 and the other 14 counties having 
        just 1. Now, if we move the filter to include only fires over 10,000 Acres Burned, we find that the 
        county with the most total fires, Yolo (145), has had only 3 fires over this acreage.
        """)

fig_year_acreage = px.bar(
    df_selection,
    x= df_selection["ArchiveYear"].unique(),
    y= df_selection.groupby(by=["ArchiveYear"])["AcresBurned"].mean(),
    color= df_selection["ArchiveYear"].unique(),
    title='Average Acres Burned by Year',
    labels={
        'x': 'Year',
        'y': "Average Acres Burned"
    }
)
st.plotly_chart(fig_year_acreage)

st.subheader("Bar Chart Analysis")
st.write("""
        Unlike the pie chart above, in this bar chart the distribution of average acres burned per year 
        is not as even. The average acres burned in 2018 were nearly triple that of any other year. This 
        is due to the fact that the largest wildfire from this period (2013-2020) occurred in 2018. This 410,000 
        acre fire has a huge impact on the average.
        """)

fig_year_size = px.scatter(
    df_selection,
    x = df_selection["ArchiveYear"],
    y = df_selection["PersonnelInvolved"],
    size = df_selection["AcresBurned"],
    hover_name = df_selection["Name"],
    size_max=60,
    title="Fire Size vs. Personnel Involved by Year"
)
st.plotly_chart(fig_year_size)

st.subheader("Bubble Chart Analysis")
st.write("""
        Surprisingly, we find that as the personnel involved increases, there is not much effect on the total acres burned 
        by the fire. This is not what we woud exprect. However, when we look at the dataset we find that the attribute 
        "PersonnelInvolved" has a fair amount of null values. Therefore, it is harder to display the data accurately in a graph.
        """)
