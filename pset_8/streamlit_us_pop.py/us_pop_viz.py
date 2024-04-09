import streamlit as st

import pandas as pd
#import matplotlib.pyplot as plt
import altair as alt
from vega_datasets import data # for the map

# pip install streamlit pandas altair vega_datasets

tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
# make a side bar
st.sidebar.title("Side Bar")
st.sidebar.title("Navigation")
option = st.sidebar.radio("Select the options: ", ["Home", "Data Header", "Data Summary", "Scatterplot"])


if option == "Home":
    st.title("US States viz")
    st.text("This is an app that explores the population stats in US cities")
    #st.markdown("## This is an app that explores earthquake data")


#tranforming the data
#use pandas to read
df = pd.read_csv("us-population-2010-2019-states-code.csv")
df_reshaped=pd.melt(df,id_vars=['id','states','states_code'],value_name='population',var_name='year')

#change year to int format
df_reshaped['year']=df_reshaped['year'].astype(int)

#replace "," with nothing and then format as integer
df_reshaped['population']=df_reshaped['population'].apply(lambda x: x.replace(",", ""))
df_reshaped['population']=df_reshaped['population'].astype(int)

#change states to string
df_reshaped['states'] = df_reshaped['states'].astype(str)

#keep only 2019 year
df_selected_year = df_reshaped[df_reshaped['year'] == 2019]

if option == "Data Header":
    st.markdown("Data Head")
    st.write(df_reshaped.head())
if option == "Data Summary":
    st.markdown("Summary Stata")
    st.write(df_reshaped.describe(exclude=['states_code']))
if option == "Scatterplot":
    st.header("Heatplot of Population by State")

    # plotting heatmap ----
    alt.themes.enable("dark")

    heatmap = alt.Chart(df_reshaped).mark_rect().encode(
        y=alt.Y('year:O', axis=alt.Axis(title="Year", titleFontSize=16,
                                        titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X('states:O', axis=alt.Axis(title="States", titleFontSize=16,
                                              titlePadding=15, titleFontWeight=900)),
            color=alt.Color('max(population):Q',
                            legend=alt.Legend(title=" "),
                            scale=alt.Scale(scheme="blueorange")),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
            # tooltip=[
            #    alt.Tooltip('year:O', title='Year'),
            #    alt.Tooltip('population:Q', title='Population')
            # ]
        ).properties(width=900
                     # ).configure_legend(orient='bottom', titleFontSize=16, labelFontSize=14, titlePadding=0
                     # ).configure_axisX(labelFontSize=14)
                     ).configure_axis(
            labelFontSize=12,
            titleFontSize=12
        ).interactive()

    st.altair_chart(heatmap)

    # plotting the map ----
    states = alt.topo_feature(data.us_10m.url, 'states')

    maps = alt.Chart(states).mark_geoshape().encode(
        color=alt.Color('population:Q', scale=alt.Scale(scheme='blues')),  # scale=color_scale
        stroke=alt.value('#154360')
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(df_selected_year, 'id', list(df_selected_year.columns))
    ).properties(
        width=500,
        height=300
    ).project(
        type='albersUsa'
    ).interactive()

    #show altair plot on app
    st.altair_chart(maps)



#st.rerun() to rerun scripts