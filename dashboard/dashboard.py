import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

sns.set(style="white")

st.set_page_config(
    page_title="Capital Bikeshare: Bike-sharing Dashboard",
    page_icon=":bike:",
    layout="wide",
) 

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)

df = pd.read_csv(
    "https://raw.githubusercontent.com/rifialdiif/Project_DA_Dicoding/main/dashboard/cleaned_day_bike_data.csv"
)
df["dateday"] = pd.to_datetime(df["dateday"])

min_date = df["dateday"].min()
max_date = df["dateday"].max()
# SIDE BAR
with st.sidebar:
    # add capital bikeshare logo
    st.image("https://github.com/rifialdiif/Project_DA_Dicoding/blob/main/dashboard/logo.png?raw=true")

    st.sidebar.header("Filter:")

    # mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

st.sidebar.header("Let's Connect!")

st.sidebar.markdown("Rifialdi Faturrochman")

col1, col2 = st.sidebar.columns(2)

with col1:
    st.markdown("[![LinkedIn](https://img.icons8.com/glyph-neue/FFFFFF/linkedin)](https://www.linkedin.com/in/rifialdi-faturrochman/)")
with col2:
    st.markdown("[![Github](https://img.icons8.com/glyph-neue/64/FFFFFF/github.png)](https://github.com/rifialdiif)")

    main_df = df[
    (df["dateday"] >= str(start_date)) &
    (df["dateday"] <= str(end_date))
]

# Functions
def create_users_summary_df(df):
    # Menghitung total untuk masing-masing tipe pengguna
    users_summary = {
        "Casual": df["casual"].sum(),
        "Registered": df["registered"].sum(),
    }
    # Menambahkan total keseluruhan pengguna
    users_summary["Total Users"] = users_summary["Casual"] + users_summary["Registered"]
    
    # Mengubah dictionary ke DataFrame untuk visualisasi
    users_summary_df = pd.DataFrame(list(users_summary.items()), columns=["User_Type", "Count"])
    
    return users_summary_df

def create_users_summary_percen_df(df):
    # Menghitung total untuk masing-masing tipe pengguna
    users_summary = {
        "Casual": df["casual"].sum(),
        "Registered": df["registered"].sum(),
    }
    
    # Mengubah dictionary ke DataFrame untuk visualisasi
    users_summary_percen_df = pd.DataFrame(list(users_summary.items()), columns=["User_Type", "Count"])
    
    return users_summary_percen_df

def create_monthly_users_df(df):
    monthly_users_df = df.resample(rule='M', on='dateday').agg({
        "casual": "sum",
        "registered": "sum",
        "count": "sum"
    })
    monthly_users_df.index = monthly_users_df.index.strftime('%b-%y')
    monthly_users_df = monthly_users_df.reset_index()
    monthly_users_df.rename(columns={
        "index": "yearmonth",  # Pastikan ini sesuai dengan kolom waktu setelah resampling
        "count": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    return monthly_users_df

def create_seasonly_users_df(df):
    # Aggregasi data berdasarkan 'season'
    seasonly_users_df = df.groupby("season").agg({
        "casual": "sum",
        "registered": "sum",
        "count": "sum"
    }).reset_index()
    
    # Rename kolom untuk kejelasan
    seasonly_users_df.rename(columns={
        "count": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    # Melakukan unpivot/melt DataFrame agar sesuai format Plotly Express
    seasonly_users_df = pd.melt(seasonly_users_df,
                                id_vars=['season'],
                                value_vars=['casual_rides', 'registered_rides'],
                                var_name='type_of_rides',
                                value_name='count_rides')
    
    # Mengatur urutan season secara eksplisit untuk visualisasi
    seasonly_users_df['season'] = pd.Categorical(seasonly_users_df['season'],
                                                 categories=['Spring', 'Summer', 'Fall', 'Winter'],
                                                 ordered=True)
    
    seasonly_users_df = seasonly_users_df.sort_values('season')
    
    return seasonly_users_df

def create_weather_users_df(df):
    # Aggregasi data berdasarkan 'weather'
    weather_users_df = df.groupby("weather").agg({
        "casual": "sum",
        "registered": "sum",
        "count": "sum"
    }).reset_index()
    
    # Rename kolom untuk kejelasan
    weather_users_df.rename(columns={
        "count": "total_rides",
        "casual": "casual_rides",
        "registered": "registered_rides"
    }, inplace=True)
    
    # Melakukan unpivot/melt DataFrame agar sesuai format Plotly Express
    weather_users_df = pd.melt(weather_users_df,
                               id_vars=['weather'],
                               value_vars=['casual_rides', 'registered_rides'],
                               var_name='type_of_rides',
                               value_name='count_rides')
    
    # Mengatur urutan weather secara eksplisit untuk visualisasi
    weather_users_df['weather'] = pd.Categorical(weather_users_df['weather'],
                                                 categories=['Clear', 'Cloudy', 'Light Rain', 'Heavy Snow/Rain'],
                                                 ordered=True)
    
    weather_users_df = weather_users_df.sort_values('weather')
    
    return weather_users_df

def create_weekday_users_df(df):
    # Mengkonversi 'dateday' menjadi hari dalam seminggu, dimana 0 adalah Senin dan 6 adalah Minggu
    df['weekday'] = df['dateday'].dt.dayofweek
    
    # Filter hanya hari Senin-Jumat (0-4)
    weekday_df = df[df['weekday'].isin(range(5))]
    
    # Mengelompokkan data berdasarkan hari dan menghitung jumlah pengguna untuk masing-masing jenis
    weekday_users_df = weekday_df.groupby('weekday').agg({
        'casual': 'sum',
        'registered': 'sum'
    }).reset_index()
    
    # Mengubah kode hari menjadi nama hari
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    weekday_users_df['weekday'] = weekday_users_df['weekday'].apply(lambda x: days[x])
    
    return weekday_users_df

def create_holiday_users_df(df):
    # Menghitung jumlah pengguna berdasarkan status hari libur
    holiday_users_df = df.groupby("holiday").agg({
        "count": "sum"
    }).reset_index()
    
    # Mengubah label 'holiday' menjadi lebih deskriptif
    holiday_users_df['holiday'] = holiday_users_df['holiday'].map({0: "Tidak", 1: "Ya"})
    holiday_users_df.rename(columns={"count": "total_rides", "holiday": "Holiday"}, inplace=True)
    
    return holiday_users_df

def plot_holiday_users(df):
    fig = px.bar(df,
                 x='Holiday',
                 y='total_rides',
                 color='Holiday',
                 title="Pengguna Bike-sharing Berdasarkan Hari Libur",
                 color_discrete_map={"Tidak": "red", "Ya": "green"})  # Merah untuk 'Tidak', Hijau untuk 'Ya'
    fig.update_layout(xaxis_title="Hari Libur", yaxis_title="Total Pengguna",
                      legend_title="Hari Libur", legend=dict(yanchor="top", y=1.02, xanchor="right", x=1))
    return fig

# Main
filtered_df = main_df[
    (main_df["dateday"] >= pd.to_datetime(start_date)) &
    (main_df["dateday"] <= pd.to_datetime(end_date))
]

st.title(":bike: Capital Bikeshare : Bike-Sharing Dashboard")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    total_users = main_df["count"].sum()
    st.metric("Total Users", value=total_users)
with col2:
    casual_users = main_df["casual"].sum()
    st.metric("Casual Users", value=casual_users)
with col3:
    registered_users = main_df["registered"].sum()
    st.metric("Registered Users", value=registered_users)

st.markdown("---")

# Assign Main
users_summary_df = create_users_summary_df(filtered_df)
users_summary_percen_df = create_users_summary_percen_df(filtered_df)
monthly_users_df = create_monthly_users_df(filtered_df)
seasonly_users_df = create_seasonly_users_df(filtered_df)
weather_users_df = create_weather_users_df(filtered_df)
weekday_users_df = create_weekday_users_df(filtered_df)
holiday_users_df = create_holiday_users_df(filtered_df)

# CHART

col1, col2 = st.columns(2)

# Grafik pertama di kolom pertama
with col1:
    fig1 = go.Figure()

    # Menambahkan bar untuk setiap jenis pengguna
    for index, row in users_summary_df.iterrows():
        if row['User_Type'] == 'Casual':
            color = 'skyblue'
        elif row['User_Type'] == 'Registered':
            color = 'salmon'
        else:
            # Warna untuk tipe pengguna lainnya atau total rides
            color = 'lightgreen'

        fig1.add_trace(go.Bar(x=[row['User_Type']], y=[row['Count']],
                             name=row['User_Type'],
                             text=[row['Count']],
                             textposition='auto',
                             marker_color=color))

    # Menyesuaikan layout
    fig1.update_layout(
        title_text='Total Casual vs Registered Users',
        xaxis=dict(title='Type of User'),
        yaxis=dict(title='Total Users'),
        barmode='group',
        legend_title_text='Type of User'
    )

    st.plotly_chart(fig1, use_container_width=True)

# Grafik kedua di kolom kedua
with col2:
    fig2 = go.Figure()

    # Menambahkan pie chart untuk proporsi pengguna
    fig2.add_trace(go.Pie(labels=users_summary_percen_df['User_Type'], 
                         values=users_summary_percen_df['Count'],
                         textinfo='label+percent',
                         insidetextorientation='radial',
                         marker_colors=['#1f77b4', '#2ca02c']))

    # Menyesuaikan layout
    fig2.update_layout(
        title_text='Persentase Casual vs Registered Users'
    )

    st.plotly_chart(fig2, use_container_width=True)

# CHART 2
fig = px.line(monthly_users_df,
              x='dateday',
              y=['casual_rides', 'registered_rides', 'total_rides'],
              labels={'value': 'Total Rides', 'yearmonth': 'Month-Year', 'variable': 'Ride Type'},
              color_discrete_map={
                'casual_rides': '#00CC96',  # Mint Green, kontras baik pada latar hitam maupun putih
                'registered_rides': '#636EFA',  # Bright Blue, memberikan kontras yang baik
                'total_rides': '#EF553B'},
              markers=True,
              title="Jumlah Pengguna Bikeshare (Bulan - Tahun)")
fig.update_layout(xaxis_title='', yaxis_title='Total Rides')

st.plotly_chart(fig, use_container_width=True)

# CHART 3: Jumlah Pengguna BikeShare by Season
fig1 = px.bar(seasonly_users_df,
              x='season',
              y='count_rides',
              color='type_of_rides',
              barmode='group',
              color_discrete_map={"casual_rides": "#00CC96", "registered_rides": "#636EFA"},
              title='Jumlah Pengguna BikeShare by Season')

fig1.update_layout(xaxis_title='Season', yaxis_title='Total Rides', legend_title_text='Type of Ride')

# CHART 4: Count of Bikeshare Rides by Weather
fig2 = px.bar(weather_users_df,
              x='weather',
              y='count_rides',
              color='type_of_rides',
              barmode='group',
              color_discrete_map={
                  "casual_rides": "#FFD700",  # Gold
                  "registered_rides": "#4169E1"  # Royal Blue, previously Medium Spring Green
              },
              title='Jumlah Pengguna Bikeshare by Weather')

fig2.update_layout(xaxis_title='Weather', yaxis_title='Total Rides', legend_title_text='Type of Ride')

# Menampilkan grafik bersebelahan
col1, col2 = st.columns(2)  # Membuat dua kolom

with col1:
    st.plotly_chart(fig1, use_container_width=True)  # Menampilkan grafik 1 di kolom pertama

with col2:
    st.plotly_chart(fig2, use_container_width=True)  # Menampilkan grafik 2 di kolom kedua

# CHART 5: Membuat grafik batang untuk jumlah pengguna di hari kerja
fig1 = go.Figure()

# Menambahkan batang untuk pengguna kasual
fig1.add_trace(go.Bar(x=weekday_users_df['weekday'], y=weekday_users_df['casual'],
                     name='Casual Users', marker_color='#17BECF'))  # Cyan/Aqua

# Menambahkan batang untuk pengguna terdaftar
fig1.add_trace(go.Bar(x=weekday_users_df['weekday'], y=weekday_users_df['registered'],
                     name='Registered Users', marker_color='#E377C2'))  # Pink

# Menambahkan garis tren
fig1.add_trace(go.Scatter(x=weekday_users_df['weekday'], y=weekday_users_df['casual'].tolist(),
                         mode='lines+markers', name='Trend Casual Users',
                         line=dict(color='#17BECF', width=2)))  # Cyan/Aqua

fig1.add_trace(go.Scatter(x=weekday_users_df['weekday'], y=weekday_users_df['registered'].tolist(),
                         mode='lines+markers', name='Trend Registered Users',
                         line=dict(color='#E377C2', width=2)))  # Pink

fig1.update_layout(title_text='Total Pengguna berdasarkan Hari Kerja dengan Garis Tren (Senin-Jumat)',
                  xaxis_title='Weekday',
                  yaxis_title='Total Users',
                  plot_bgcolor='rgba(0,0,0,0)',
                  paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(color="white"),
                  legend_title='User Type')

# CHART 6: Menggunakan fungsi plot_holiday_users untuk menghasilkan grafik
fig2 = plot_holiday_users(holiday_users_df)

# Menampilkan kedua grafik bersebelahan
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)

st.caption("Copyright (c) 2024, Created with ❤ by Rifialdi Faturrochman")
