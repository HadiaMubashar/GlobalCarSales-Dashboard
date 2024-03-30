import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(page_title= 'Car Sales Dashoboard',
                   page_icon= ':bar_chart:', 
                   layout= 'wide')


st.header("Passenger Car Sales Dashboard",divider='rainbow')
st.markdown("##")

# ---------------- Load Data -------------------
@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path)
    return df
df = load_data('E:\Data Projects\Cars Sales Dashboard\Passenger_Cars_Sales.csv')

# ---------------- Preprocess Data ------------------
def preprocess_data(df):
    df[sales_columns] = df[sales_columns].apply(lambda x: x.str.replace(",", "").fillna(0).astype(int))

sales_columns = df.columns[df.columns.str.contains('Sales')]
Country = df['Country'].unique()
preprocess_data(df)


# --------------------- Preview Data Frame------------------
with st.expander("Data Preview"):
    st.dataframe(df)


st.sidebar.header("Apply Filter...")


# ----------------- Slider bar -------------------
year = st.sidebar.selectbox(
    'Select the Year:',
    options = sales_columns, 
)

country = st.sidebar.selectbox(
    'Select the Country:',
    options = Country,
)
years = [year]
df_selection = df.query("Country in @country")[['Country'] + years]

# overall sales
over_sales = df[sales_columns].sum().sum()

# total Sales
sales_per_country = df_selection[years].sum(axis=1)
df['Total_sales'] = sales_per_country
total_sales = int(df['Total_sales'].sum())

# Sales Growth Rate
Sales_Growth = pd.DataFrame(df['Country'])
for i in range(1, len(sales_columns)):
    current_year_sales_col = sales_columns[i]
    previous_year_sales_col = sales_columns[i - 1]
    Sales_Growth[f'{current_year_sales_col}'] = round((((df[current_year_sales_col] - df[previous_year_sales_col]) / df[previous_year_sales_col]) * 100), 2)


# Maket Share
Market_Share = pd.DataFrame(df['Country'])   
for col in sales_columns:
    Market_Share[f'{col}'] =  round(((df[col] / df[col].sum()) * 100), 2)

left_column,middle_coulmn1, middle_column2, right_column = st.columns(4)

left_column.metric("Total Sales", f'{over_sales:,}')

middle_coulmn1.metric(f'{country} {year}', f'{total_sales:,}')

if year != '2005 Sales':
    growth = Sales_Growth.loc[Sales_Growth['Country'] == country, year].values[0]
    share = Market_Share.loc[Market_Share['Country'] == country, year].values[0]

    middle_column2.metric(f'Sales Growth', f'{growth} %')

    right_column.metric(f'Market Share', f'{share} %')

df_melted = df.melt(id_vars='Country', var_name='Year', value_name='Sales')

# Top plots
top_left, top_right = st.columns(2)

def plot_top_left():
    fig = px.line(df, 
                    x='Country',
                    y=year,
                    title= f'{year} in Each Country',
                    labels={'Country': 'Country', 'Sales': 'Sales','Year': 'Year'},
                    color_discrete_sequence=["#0083B8"] * len(df),)
    fig.update_layout(
            xaxis_title='Country',
            yaxis_title='Sales',
            legend_title_text='Year',
            showlegend=True,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
    st.plotly_chart(fig, use_container_width= True)

with top_left:
    plot_top_left()

def plot_top_right():  

    top_5_sales_countries = df[['Country', year]].nlargest(5, year)
    
    fig = px.bar(top_5_sales_countries, y='Country', x=year,
                title=f'Top 5 highest Sales Country in {year}', color='Country',
                orientation= 'h',
                color_discrete_sequence=px.colors.qualitative.Set3)

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title='Country',
        yaxis_title='Number of Sales',
        legend_title_text='Countries',
        showlegend=True,
        bargap=0.05,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
  
    st.plotly_chart(fig, use_container_width= True)

with top_right:
    plot_top_right()


# middle plots
middle_left, middle_middle ,middle_right = st.columns(3)

def plot_middle_left():
    continent_sales = df_melted.groupby('Country')['Sales'].sum().reset_index()
    continent_sales_top5 = continent_sales.sort_values(by='Sales', ascending=False).head(5)

    fig = px.pie(continent_sales_top5, names='Country', values='Sales', 
                        title='Top 5 Countries by Sales',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width= True)


with middle_left:
    plot_middle_left()

def plot_middle_middle():
    sales_country = Market_Share[Market_Share['Country'] == country].squeeze()
    sales_country = sales_country.drop('Country')
    sales_country_df = pd.DataFrame({'Year': sales_country.index, 'Sales Market Shares': sales_country.values})

    fig = px.line(sales_country_df, x='Year', y='Sales Market Shares', title=f'<br>Market Shares in {country}<br>', 
                  labels={'Country': 'Country', 'Market Share': 'Sales','Year': 'Year'},
                  color_discrete_sequence=["#0083B8"] * len(sales_country_df),
                  markers= True)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig, use_container_width= True)
    

with middle_middle:
    plot_middle_middle()


def plot_middle_right():
    sales_country = Sales_Growth[Sales_Growth['Country'] == country].squeeze()
    sales_country = sales_country.drop('Country')
    sales_country_df = pd.DataFrame({'Year': sales_country.index, 'Sales': sales_country.values})

    fig = px.line(sales_country_df, x='Year', y='Sales', title=f'Sales Growth Rate in {country}', 
                  labels={'Country': 'Country', 'Growth Rate': 'Sales','Year': 'Year'},
                  color_discrete_sequence=["#0083B8"] * len(sales_country_df), markers= True)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
  
    st.plotly_chart(fig, use_container_width= True)

with middle_right:
    plot_middle_right()


# Bottom plot
fig = px.scatter(df_melted, x='Year', y='Sales', color='Country',
                         title='Passenger Car Sales Over the Years',
                         labels={'Year': 'Year', 'Sales': 'Sales'},
                         hover_name='Country')
fig.update_layout(
            xaxis_title='Country',
            yaxis_title='Sales',
            legend_title_text='Year',
            showlegend=True,
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
st.plotly_chart(fig, use_container_width= True)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            # header {visibility: hidden;}
            </style>
             
            """
st.markdown(hide_st_style, unsafe_allow_html=True)






