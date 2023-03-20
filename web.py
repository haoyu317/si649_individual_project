import streamlit as st
import pandas as pd
from vega_datasets import data
import altair as alt
import requests
from bs4 import BeautifulSoup
import warnings
warnings.simplefilter("ignore")

st.set_page_config(layout='wide')


disability_pop_df = pd.read_csv('dataset/disability_pop.csv',sep='\t')

dis_df = pd.read_csv('dataset/disability_dis.csv',sep='\t')
selection_state=alt.selection_single(fields=['id'], init={"id":1})
input_dropdown = alt.binding_select(options=disability_pop_df.item.unique(), name='State Information Selection')
selection = alt.selection_single(fields=['item'],
                                bind=input_dropdown)
colorCondition = alt.condition(selection_state,alt.value(1.0), alt.value(0.6))

states = alt.topo_feature(data.us_10m.url, feature = 'states')
background1 = alt.Chart(disability_pop_df).mark_geoshape(stroke='white').encode(
    color = alt.Color('value:Q'),
    tooltip=['state:N','value:Q'],
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(states,'id',fields=['geometry','type'])
).add_selection(
    selection, selection_state
).transform_filter(
    selection
).project(
    type='albersUsa'
).properties(width = 600, height = 500)

bar_count_selection = alt.Chart(dis_df).transform_lookup(
    lookup='id',
    from_=alt.LookupData(disability_pop_df,'id',fields=['geometry','type'])
).transform_filter(
    selection_state
).mark_bar().encode(
    y = alt.Y("dis_type:O", title='Count of Each Disability Type'),
    x = alt.X("count:Q", title=None),
    tooltip=['count:Q'],
).properties(width = 300, height = 150)

bar_count_text_selection = alt.Chart(dis_df).transform_lookup(
    lookup='id',
    from_=alt.LookupData(disability_pop_df,'id',fields=['geometry','type'])
).transform_filter(
    selection_state
).mark_text().encode(
    y = alt.Y("dis_type:O", title='Count of Each Disability Type'),
    x = alt.X("count:Q", title=None),
    text='count:Q',
).properties(width = 300, height = 150)

bar_percent_selection = alt.Chart(dis_df).transform_lookup(
    lookup='id',
    from_=alt.LookupData(disability_pop_df,'id',fields=['geometry','type'])
).transform_filter(
    selection_state
).mark_bar().encode(
    x = alt.X("dis_type:O", title=None,axis=alt.Axis(labelAngle=-45)),
    y = alt.Y("dis_per:Q", title='Percentage of Each Disability Type'),
    tooltip=['dis_per:Q'],
).properties(
    width = 200,
    height = 100
).properties(width = 300, height = 150)

bar_percent_text_selection = alt.Chart(dis_df).transform_lookup(
    lookup='id',
    from_=alt.LookupData(disability_pop_df,'id',fields=['geometry','type'])
).transform_filter(
    selection_state
).mark_text().encode(
    x = alt.X("dis_type:O", title=None,axis=alt.Axis(labelAngle=-45)),
    y = alt.Y("dis_per:Q", title='Percentage of Each Disability Type'),
    text='dis_per:Q',
).properties(
    width = 200,
    height = 100
).properties(width = 300, height = 150)


pie_df = dis_df[['id','total','dis']].drop_duplicates()
pie_df['health'] = pie_df['total'] - pie_df['dis']
health_df = pie_df[['id','health','total']].rename(columns = {'health':'value'})
health_df['category'] = 'Health'

disability_df = pie_df[['id','dis','total']].rename(columns = {'dis':'value'})
disability_df['category'] = 'Disability'
health_dis_df = pd.concat([health_df,disability_df])
health_dis_df['percentage'] = health_dis_df['value'] / health_dis_df['total']


pie_base = alt.Chart(health_dis_df).transform_lookup(
    lookup='id',
    from_=alt.LookupData(disability_pop_df,'id',fields=['geometry','type'])
).transform_filter(
    selection_state
).encode(
    theta=alt.Theta("value:Q"), color=alt.Color("category:N")
)
pie = pie_base.mark_arc(outerRadius=80)
pie_text = pie_base.mark_text(radius=100, size=20,radiusOffset=10).encode(
    text=alt.Text('percentage:Q', format="0.00%")
)
pie_selection = pie + pie_text


###  Medical expenditure per state
df = pd.read_csv('dataset/expenditure.csv',sep ='\t')
df = df[df.state != 'United States']
state_id = data.population_engineers_hurricanes()[['state','id']]
total_2015_df = df[['state','total_2015']]
total_2015_df['item'] = 'Total DAHE 2015 (million $)'
total_2015_df['year'] = 2015
total_2015_df = total_2015_df.rename(columns={"total_2015":"value"})

total_2003_df = df[['state','total_2003']]
total_2003_df['item'] = 'Total DAHE 2003 (million $)'
total_2003_df = total_2003_df.rename(columns={"total_2003":"value"})
total_2003_df['year'] = 2003

total_change_df = df[['state','total_change']]
total_change_df['item'] = 'Total DAHE Change (%)'
total_change_df = total_change_df.rename(columns={"total_change":"value"})
total_change_df['year'] = 2015

per_2015_df = df[['state','per_2015']]
per_2015_df['item'] = 'DAHE per person with disability 2015 ($)'
per_2015_df = per_2015_df.rename(columns={"per_2015":"value"})
per_2015_df['year'] = 2015

per_2003_df = df[['state','per_2003']]
per_2003_df['item'] = 'DAHE per person with disability 2003 ($)'
per_2003_df = per_2003_df.rename(columns={"per_2003":"value"})
per_2003_df['year'] = 2003

per_change_df = df[['state','per_change']]
per_change_df['item'] = 'DAHE per person with disability change (%)'
per_change_df = per_change_df.rename(columns={"per_change":"value"})
per_change_df['year'] = 2015

expenditure_df = pd.concat([total_2015_df,total_2003_df,total_change_df,per_2015_df,per_2003_df,per_change_df], axis=0)

expenditure_df = expenditure_df.merge(state_id, left_on='state',right_on='state')

input_dropdown = alt.binding_select(options=expenditure_df.item.unique(), name='State Information Selection')
selection2 = alt.selection_single(
                                fields=['item'],
                                init={'item':'Total DAHE 2015 (million $)'},
                                bind=input_dropdown)
selection_state=alt.selection_single(fields=['id'], init={"id":1})
colorCondition = alt.condition(selection_state,alt.value(1), alt.value(0.6))

states = alt.topo_feature(data.us_10m.url, feature = 'states')
background2 = alt.Chart(expenditure_df).mark_geoshape(stroke='white').encode(
    color = alt.Color('value:Q'),
    tooltip=['state:N','value:Q'],
    # opacity = colorCondition
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(states,'id',fields=['geometry','type'])
).add_selection(
    selection2,selection_state
).transform_filter(
    selection2
).project(
    type='albersUsa'
).properties(
    width = 650,
    height = 400
)


total_selection = alt.Chart(expenditure_df).transform_lookup(
    lookup='id',
    from_=alt.LookupData(states,'id',fields=['geometry','type'])
).transform_filter(
    (alt.datum.item == 'Total DAHE 2015 (million $)') | (alt.datum.item == 'Total DAHE 2003 (million $)')
).transform_filter(
    selection_state,
).mark_bar(width=50).encode(
    x = alt.X("year:N", title=None),
    y = alt.Y("value:Q", title='Total DAHE (million $)'),
    tooltip = ["value:Q"]
).properties(
    width = 300,
    height = 150
)


per_selection = alt.Chart(expenditure_df).transform_lookup(
    lookup='id',
    from_=alt.LookupData(states,'id',fields=['geometry','type'])
).transform_filter(
    (alt.datum.item == 'DAHE per person with disability 2015 ($)') | (alt.datum.item == 'DAHE per person with disability 2003 ($)')
).transform_filter(
    selection_state,
).mark_bar(width=50).encode(
    x = alt.X("year:N", title=None),
    y = alt.Y("value:Q", title='DAHE per person with disability ($)'),
    tooltip = ["value:Q"]
).properties(
    width = 300,
    height = 150
)


### Comparison between people with and without disability
df = pd.read_csv('dataset/poverty.csv')

education = alt.Chart(df).mark_line(point=True).encode(
    x='Year',
    y='Education:Q',
    color='people'
).properties(
    title="Less than a High School Diploma(%)",
    width = 450,
    height = 250
)

employment = alt.Chart(df).mark_line(point=True).encode(
    x='Year',
    y='Employment:Q',
    color='people'
).properties(
    title="Employment to Population Ratio(%)",
    width = 450,
    height = 250
)

earning = alt.Chart(df).mark_line(point=True).encode(
    x='Year',
    y='Earnings:Q',
    color='people'
).properties(
    title="Median Earnings of Full-Time Works($)",
    width = 450,
    height = 250
)

poverty = alt.Chart(df).mark_line(point=True).encode(
    x='Year',
    y='Poverty:Q',
    color='people'
).properties(
    title="Poverty to Population Ratio(%)",
    width = 450,
    height = 250
)

col1, col2, col3 = st.columns([1,6,1])

with col2:
  chart1 = ((background1 )| ( (( bar_count_selection   & bar_percent_selection ) | pie_selection))).properties(
          title = 'State-Level Information Associated With People With Disability'
      )
  chart1 = chart1.configure_title(fontSize=30)
  st.altair_chart(chart1)


col4, col5, col6 = st.columns([2,6,1])

with col5:
    chart2 = (background2 | (total_selection & per_selection)).properties(
        title = 'State-Level Medical Expenditures Associated With Disability'
    )
    chart2 = chart2.configure_title(fontSize=30)
    st.altair_chart(chart2)


# chart1 = ((background1 )| ( (( bar_count_selection   & bar_percent_selection ) | pie_selection))).properties(
#         title = 'State-Level Information Associated With People With Disability'
#     )
# chart1 = chart1.configure_title(fontSize=30)
# st.altair_chart(chart1)

# chart2 = (background2 | (total_selection & per_selection))
# chart2 = chart2.configure_title(fontSize=30).properties(
#         title = 'State-Level Information Associated With People With Disability'
#     )
# st.altair_chart(chart2)


chart3 = ((education | employment) & (earning | poverty))
chart3 = chart3.configure_title(fontSize=30)
st.altair_chart(chart3)







