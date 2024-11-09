import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime,time, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import pytz
from st_aggrid import AgGrid

# Global variables
mainbase = ['SGN', 'HAN', 'DAD', 'CXR', 'HPH','VII','PQC','VCA']
# File path
file_path = '/Users/dongthan/Desktop/moc/acreadiness/csv/airports.csv'

aircraft_types = ['A320', 'A321', 'A330']
airports = ['SGN', 'HAN', 'DAD', 'CXR']

def create_connection_season_fpl():
    conn = None;
    try:
        # Include the 'database' subfolder in the path
        path = 'seasonflightplan.db'
        
        conn = sqlite3.connect(path) # creates a SQLite database named 'seasonflightplan.db'
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn
##
# Ép kiểu dữ liệu về định dạng HH:MM
def normalize_time_format(value):
    if pd.isnull(value):
        return None
    elif isinstance(value, (int, float)):
        # Chuyển đổi số thành chuỗi định dạng giờ
        return f"{int(value):02d}:00:00"
    elif isinstance(value, str):
        # Xử lý các định dạng chuỗi khác nhau
        try:
            datetime_obj = pd.to_datetime(value, format='%H:%M:%S.%f')
        except ValueError:
            try:
                datetime_obj = pd.to_datetime(value, format='%H:%M:%S')
            except ValueError:
                try:
                    datetime_obj = pd.to_datetime(value, format='%H:%M')
                except ValueError:
                    try:
                        datetime_obj = pd.to_datetime(value, format='%I:%M:%S %p')
                    except ValueError:
                        print(f"Could not convert time: {value}")
                        return None
        return datetime_obj.strftime('%H:%M:%S')
    elif isinstance(value, (datetime, time)):
        # Chuyển đổi datetime hoặc time thành chuỗi định dạng giờ
        return value.strftime('%H:%M:%S')
    elif isinstance(value, timedelta):
        # Chuyển đổi timedelta thành chuỗi định dạng giờ
        hours = value.total_seconds() // 3600
        minutes = (value.total_seconds() % 3600) // 60
        seconds = value.total_seconds() % 60
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    else:
        print(f"Unsupported data type: {type(value)}")
        return None
## Hàm chuyển đổi nhiều cột thời gian về định dạng chuẩn HH:MM

def normalize_time_columns(df, columns):
    for col in columns:
        df[col] = df[col].apply(normalize_time_format)
    return df

## Hàm chuyển đổi thời gian về đơn vị phút HH:MM -> MÍNUTES
def convert_to_minutes(value):
    if pd.isnull(value):
        return None
    elif isinstance(value, (int, float)):
        return int(value)
    elif isinstance(value, str):
        try:
            time_obj = pd.to_datetime(value, format='%H:%M:%S.%f').time()
        except ValueError:
            try:
                time_obj = pd.to_datetime(value, format='%H:%M:%S').time()
            except ValueError:
                try:
                    time_obj = pd.to_datetime(value, format='%H:%M').time()
                except ValueError:
                    print(f"Could not convert time: {value}")
                    return None
        return time_obj.hour * 60 + time_obj.minute
    elif isinstance(value, (datetime, time)):
        return value.hour * 60 + value.minute
    elif isinstance(value, timedelta):
        return value.total_seconds() // 60
    else:
        print(f"Unsupported data type: {type(value)}")
        return None
## Hàm chuyển đổi nhiều cột thời gian về đơn vị phút
def convert_many_cols_to_minutes(df, columns):
    for column in columns:
        df[column] = df[column].apply(convert_to_minutes)
    return df

def convert_to_time_string(value):
    if pd.isnull(value):
        return None
    elif isinstance(value, (int, float)):
        minutes = int(value)
        return f"{minutes // 60:02d}:{minutes % 60:02d}"
    elif isinstance(value, str):
        return value
    elif isinstance(value, (datetime, time)):
        return value.strftime('%H:%M')
    elif isinstance(value, timedelta):
        minutes = value.total_seconds() // 60
        return f"{int(minutes // 60):02d}:{int(minutes % 60):02d}"
    else:
        print(f"Unsupported data type: {type(value)}")
        return None

def convert_many_cols_to_time_string(df, columns):
    for col in columns:
        df[col] = df[col].apply(convert_to_time_string)
    return df

## ----------------- Import & Processing Data----------------- ##

# def process_excel_season_file(file_path,df_date):
        
    # Read the Excel file
    df = pd.read_excel(file_path, header=1)

    # Drop row NaN
    df = df.dropna(subset=['NO'])

    # Drop specified columns
    df = df.drop(columns=['NO','STD', 'STA', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16','BLOCK','TAT'])

    # Rename column
    df = df.rename(columns={'FLIGHT N0':'FLT_NO','STD.1':'STD','STA.1':'STA'})

    # Split ROUTE into DEP and ARR
    df[['DEP', 'ARR']] = df['ROUTE'].str.split('-', expand=True)

    # Create ACTYPE from AC
    df['ACTYPE'] = df['AC'].str.split('-').str[1]

    # Convert FREQ to string
    df['FREQ'] = df['FREQ'].astype(str)

    df['DATE'] = df_date

    # Reorder columns
    cols = ["DATE", "AC", "ACTYPE", "FLT_NO", "ROUTE", "DEP", "ARR", "STD", "STA", "FREQ", "FROM", "TO"]
    df = df[cols]
    
    # Remove leading and trailing whitespaces from all string values in the DataFrame
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Remove duplicate rows based on the 'FLT_NO' column
    df = df.drop_duplicates(subset='FLT_NO')
    
    # Normalize the time columns
    df = normalize_time_columns(df, ['STD', 'STA'])
    # Connect to the SQLite database
    conn = create_connection_season_fpl()
    if conn is not None:
        # Read the DataFrame records to the SQLite database
        df_db = pd.read_sql_query("SELECT * FROM seasonflightplan", conn)
        if not df_db.equals(df):
            # Insert DataFrame records to the SQLite database
            df.to_sql('seasonflightplan', conn, if_exists='append', index=False)
        else:
            print("The DataFrame records are already in the database.")
    else:
        print("Error! cannot create the database connection.")

    return df

def process_excel_season_file(file_path, df_date):
    # Read the Excel file
    df = pd.read_excel(file_path, header=0)

    # Check if the 'NO' column exists before dropping rows
    if 'NO' in df.columns:
        df = df.dropna(subset=['NO'])

    # Drop unnecessary columns
    columns_to_drop = ['NO', 'BLOCK', 'TAT', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # Split 'ROUTE' into 'DEP' and 'ARR' if 'ROUTE' exists
    if 'ROUTE' in df.columns:
        df[['DEP', 'ARR']] = df['ROUTE'].str.split('-', expand=True)
    else:
        df['DEP'] = ''
        df['ARR'] = ''

    # Create 'ACTYPE' from 'AC' if 'AC' exists
    if 'AC' in df.columns:
        df['ACTYPE'] = df['AC'].str.split('-').str[1]
    else:
        df['ACTYPE'] = ''

    # Convert 'FREQ' to string if 'FREQ' exists
    if 'FREQ' in df.columns:
        df['FREQ'] = df['FREQ'].astype(str)
    else:
        df['FREQ'] = ''

    # Add 'DATE' column
    df['DATE'] = df_date

    # Reorder columns
    cols = ["DATE", "AC", "ACTYPE", "FLIGHT N0", "ROUTE", "DEP", "ARR", "STD", "STA", "FREQ", "FROM", "TO"]
    existing_cols = df.columns.intersection(cols)
    df = df[existing_cols]

    # Remove leading and trailing whitespaces from all string values in the DataFrame
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Remove duplicate rows based on the 'FLIGHT N0' column if it exists
    if 'FLIGHT N0' in df.columns:
        df = df.drop_duplicates(subset='FLIGHT N0')

    # Normalize the time columns if they exist
    if 'STD' in df.columns and 'STA' in df.columns:
        df = normalize_time_columns(df, ['STD', 'STA'])

    # Connect to the SQLite database
    conn = create_connection_season_fpl()
    if conn is not None:
        # Read the DataFrame records from the SQLite database
        df_db = pd.read_sql_query("SELECT * FROM seasonflightplan", conn)
        if not df_db.equals(df):
            # Insert DataFrame records into the SQLite database
            df.to_sql('seasonflightplan', conn, if_exists='append', index=False)
        else:
            print("The DataFrame records are already in the database.")
    else:
        print("Error! Cannot create the database connection.")

    return df
## -- Hàm convert date time -- ##
def convert_many_cols_hours_to_minutes(df, columns):
    from datetime import datetime, time

    # Define function to convert time to total minutes
    def time_to_minutes(time_obj):
        if isinstance(time_obj, str):
            # Handle time strings that contain hours, minutes, seconds, and microseconds
            try:
                time_obj = datetime.strptime(time_obj, '%H:%M:%S.%f').time()
            except ValueError:
                try:
                    time_obj = datetime.strptime(time_obj, '%H:%M:%S').time()
                except ValueError:
                    try:
                        time_obj = datetime.strptime(time_obj, '%H:%M').time()
                    except ValueError:
                        print(f"Could not convert time: {time_obj}")
                        return None
        total_minutes = time_obj.hour * 60 + time_obj.minute
        return total_minutes

    # Convert time columns to total minutes
    for column in columns:
        df[column] = df[column].apply(time_to_minutes)

    return df

# Hàm chuyển đổi format cho 1 cột dữ liệu phút sang giờ

def convert_many_cols_minutes_to_hours(df, columns):
    # Define function to convert total minutes to time
    def minutes_to_time(minutes):
        try:
            minutes = int(minutes)
            return f"{minutes // 60:02d}:{minutes % 60:02d}"
        except ValueError:
            # If value is not a valid integer, return it as is
            return minutes

    # Convert minutes columns to time
    for col in columns:
        df[col] = df[col].apply(minutes_to_time)
    return df
# Define a function to expand the 'FREQ' column and separate the data by day

## -- Hiển thị dữ liệu Season Flight Plan theo ngày. Sau khi upload -- ##

def display_flightplan_by_date():
    # Create a connection to the SQLite database
    with sqlite3.connect('seasonflightplan.db') as conn:
        # Get all unique dates from the 'seasonflightplan' table
        df_dates = pd.read_sql_query("SELECT DISTINCT DATE FROM seasonflightplan", conn)

        # Create a select box with the unique dates
        selected_date = st.selectbox("Select a date to view database", df_dates['DATE'])

        # If a date is selected, get the flight plan for the selected date
        if selected_date:
            df_flightplan = pd.read_sql_query(f"SELECT * FROM seasonflightplan WHERE DATE = '{selected_date}'", conn)
            df_flightplan['STA'] = pd.to_datetime(df_flightplan['STA']).dt.strftime('%H:%M')
            df_flightplan['STD'] = pd.to_datetime(df_flightplan['STD']).dt.strftime('%H:%M')

            # Return the flight plan
            return df_flightplan


## --- Expand the 'Import Flight Data' BEGIN--- ##

def expand_freq_and_separate(df):
    # Create new columns for each day of the week
    for i in range(1, 8):
        df[f'FREQ-{i}'] = df['FREQ'].apply(lambda x: 1 if str(i) in str(x) else 0)

    # Create separate dataframes for each day using a list comprehension
    day_dfs = [df[df[f'FREQ-{i}'] == 1] for i in range(1, 8)]

    # Select columns and reset index for each dataframe
    cols = ['AC', 'ACTYPE', 'FLT_NO', 'DEP', 'ARR', 'ROUTE', 'STD', 'STA','FREQ', 'FROM', 'TO']
    day_dfs = [df[cols].reset_index(drop=True) for df in day_dfs]


    # Assign each dataframe to a separate variable
    df_D1, df_D2, df_D3, df_D4, df_D5, df_D6, df_D7 = day_dfs

    return df_D1, df_D2, df_D3, df_D4, df_D5, df_D6, df_D7

## --- Expand the 'Import Flight Data' END--- ##

## -- Hàm tính ground time BEGIN -- ##

def calculate_ground_time(df):
    # Sort the dataframe by AC and STD
    # df = df.sort_values(['AC', 'STD'])

    # Group by AC
    grouped = df.groupby('AC')

    # Initialize an empty DataFrame to store the results
    result = pd.DataFrame()

    # Iterate over each group
    for name, group in grouped:
        # Calculate the ground time for each row in the group
        for i in range(len(group) - 1):
            # Get the current STD and the next STA
            std = group.iloc[i + 1]['STD']
            sta = group.iloc[i]['STA']

            # If the STD is less than the STA, add 1440 to the STD
            if std < sta:
                std += 1440

            # Calculate the ground time
            grd_time = std - sta

            # Add the ground time to the group
            group.at[group.index[i], 'GRD_TIME'] = grd_time

        # Add the group to the result
        result = pd.concat([result, group])

    # If there is no next STD for an AC group, set the ground time to 0
    result['GRD_TIME'] = result['GRD_TIME'].fillna('-')

    return result

## -- Hàm tính ground time END-- ##

## -- Hàm tính BLOCK TIME theo UTC, tự động tính chênh múi giờ -- ##
def calculate_block_time(df, timezone_file):


    from datetime import datetime, timedelta
    # Read the CSV file into a DataFrame
    timezones_df = pd.read_csv(timezone_file)

    # Create a dictionary from the DataFrame
    airport_timezones = dict(zip(timezones_df['code'], timezones_df['time_zone_id']))

    def compute_block_time(row):
        dep_airport = row['DEP']
        arr_airport = row['ARR']
        std_time = row['STD']
        sta_time = row['STA']
        
        dep_timezone = pytz.timezone(airport_timezones.get(dep_airport, 'UTC'))
        arr_timezone = pytz.timezone(airport_timezones.get(arr_airport, 'UTC'))

        # Set a reference date for comparison
        ref_date = datetime.now().date()

        # std_local = datetime.combine(ref_date, datetime.strptime(std_time, '%H:%M').time())
        std_local = datetime.combine(ref_date, time(hour=std_time // 60, minute=std_time % 60))
        # sta_local = datetime.combine(ref_date, datetime.strptime(sta_time, '%H:%M').time())
        sta_local = datetime.combine(ref_date, time(hour=sta_time // 60, minute=sta_time % 60))

        std_local = dep_timezone.localize(std_local)
        sta_local = arr_timezone.localize(sta_local)

        # Convert both times to UTC for comparison
        std_utc = std_local.astimezone(pytz.UTC)
        sta_utc = sta_local.astimezone(pytz.UTC)

        # Check if sta_utc is earlier than std_utc
        if sta_utc < std_utc:
            # Add one day to sta_utc
            sta_utc += timedelta(days=1)

        # Calculate the block time in UTC
        block_time = sta_utc - std_utc

        return block_time

    # Apply the function to each row of the DataFrame
    df['BLOCK_TIME'] = df.apply(compute_block_time, axis=1)

    # Convert 'BLOCK_TIME' to 'HH:MM' format
    df['BLOCK_TIME'] = df['BLOCK_TIME'].apply(lambda x: f"{x.days*24 + x.seconds // 3600:02d}:{(x.seconds % 3600) // 60:02d}")

    return df

## -- Hàm tính BLOCK TIME theo UTC, tự động tính chênh múi giờ -- ##

## -- Processing data Begin-- ##


# Display the flight plan by date - Lấy dữ liệu từ SQLite bằng cách select theo ngày
## *******************************************
df_flightplan = display_flightplan_by_date()


# Expand the 'FREQ' column and separate the data by day

df_D1, df_D2, df_D3, df_D4, df_D5, df_D6, df_D7 = expand_freq_and_separate(df_flightplan)

# List of DataFrames
dfs = [df_D1, df_D2, df_D3, df_D4, df_D5, df_D6, df_D7]

# Processed DataFrames
processed_dfs = []

# Apply the operations to each DataFrame
for df in dfs:
    df = convert_many_cols_hours_to_minutes(df, ['STD', 'STA'])
    df = calculate_ground_time(df)
    df = calculate_block_time(df, file_path)
    df = convert_many_cols_minutes_to_hours(df, ['STD', 'STA','GRD_TIME','BLOCK_TIME'])
    processed_dfs.append(df)

df_D1_1, df_D2_1, df_D3_1, df_D4_1, df_D5_1, df_D6_1, df_D7_1 = processed_dfs # unpack the processed DataFrames

## -- Processing data End-- ##

def calculate_connecting_flights(df_D1_1, df_D2_1, mainbase):
    # Group the dataframes and get the last row of each group in df_D1_1 and the first row of each group in df_D2_1
    last_rows_D1 = df_D1_1.groupby('AC').last().reset_index()
    first_rows_D2 = df_D2_1.groupby('AC').first().reset_index()

    # Filter the last rows of df_D1_1
    last_rows_D1 = last_rows_D1[last_rows_D1['ARR'].isin(mainbase)]

    # Filter the first rows of df_D2_1
    first_rows_D2 = first_rows_D2[first_rows_D2['DEP'].isin(mainbase)]

    # Merge the two dataframes on 'AC'
    connecting_flights = pd.merge(last_rows_D1, first_rows_D2, on='AC', suffixes=('_D1', '_D2'))

    # Filter the dataframe to only include rows where ARR_D1 is the same as DEP_D2
    connecting_flights = connecting_flights[connecting_flights['ARR_D1'] == connecting_flights['DEP_D2']]

    # Convert STA_D1 and STD_D2 to datetime
    connecting_flights['STA_D1'] = pd.to_datetime(connecting_flights['STA_D1'])
    connecting_flights['STD_D2'] = pd.to_datetime(connecting_flights['STD_D2'])

    # Calculate NS_GRD_TIME as STD_D2 - STA_D1
    connecting_flights['NS_GRD_TIME'] = connecting_flights['STD_D2'] - connecting_flights['STA_D1']

    # If STA_D1 is greater than STD_D2, add 24 hours to STD_D2
    connecting_flights.loc[connecting_flights['STA_D1'] > connecting_flights['STD_D2'], 'NS_GRD_TIME'] += pd.Timedelta(days=1)

    return connecting_flights


def count_aircraft(connecting_flights, aircraft_type, airport):
    # Filter for specified aircraft at specified airport
    aircraft_df = connecting_flights[(connecting_flights['ACTYPE_D1'] == aircraft_type) & (connecting_flights['ARR_D1'] == airport)]

    # Convert ground time to hours
    aircraft_df['NS_GRD_TIME'] = aircraft_df['NS_GRD_TIME'].dt.total_seconds() / 3600

    # Count the number of aircraft with ground time between 5-7 hours, 7-10 hours, and over 10 hours
    count_5_to_7 = aircraft_df[(aircraft_df['NS_GRD_TIME'] >= 5) & (aircraft_df['NS_GRD_TIME'] < 7)].shape[0]
    count_7_to_10 = aircraft_df[(aircraft_df['NS_GRD_TIME'] >= 7) & (aircraft_df['NS_GRD_TIME'] < 10)].shape[0]
    count_over_10 = aircraft_df[aircraft_df['NS_GRD_TIME'] >= 10].shape[0]

    return pd.DataFrame({
        'Aircraft Type': [aircraft_type],
        'Airport': [airport],
        '5-7 Hours': [count_5_to_7],
        '7-10 Hours': [count_7_to_10],
        'Over 10 Hours': [count_over_10]
    })

#########
# Copy the dataframes
df_D1_1_copy, df_D2_1_copy, df_D3_1_copy, df_D4_1_copy, df_D5_1_copy, df_D6_1_copy, df_D7_1_copy = df_D1_1.copy(), df_D2_1.copy(), df_D3_1.copy(), df_D4_1.copy(), df_D5_1.copy(), df_D6_1.copy(), df_D7_1.copy()

# Add the copied dataframes to a list
dataframes = [df_D1_1_copy, df_D2_1_copy, df_D3_1_copy, df_D4_1_copy, df_D5_1_copy, df_D6_1_copy, df_D7_1_copy, df_D1_1_copy]
# Define 'days'
days = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D1']

# Loop over each pair of dataframes
for i in range(len(dataframes) - 1):
    df1 = dataframes[i]
    df2 = dataframes[i + 1]

    # Calculate connecting flights
    connecting_flights = calculate_connecting_flights(df1, df2, mainbase)

    # Initialize an empty DataFrame to store the results
    results_df = pd.DataFrame()

    for aircraft_type in aircraft_types:
        for airport in airports:
            # Concatenate the results to the DataFrame
            results_df = pd.concat([results_df, count_aircraft(connecting_flights, aircraft_type, airport)], ignore_index=True)

    # Sort the DataFrame by 'Airport' within each 'STA' group
    results_df.sort_values(['Airport'], inplace=True)

    # Store the results in the global variables
    globals()[f'results_df_{days[i]}_{days[i + 1]}'] = results_df

##### VẼ BIỂU ĐỒ KẾT QUẢ
def plot_results(df):
    # Drop the 'index' column if it exists
    if 'index' in df.columns:
        df = df.drop(columns='index')

    # Melt the DataFrame to long format
    df_melted = df.melt(id_vars=['Aircraft Type', 'Airport'], var_name='GRD_TIME_GROUP', value_name='TOTAL AC')

    # Create a FacetGrid
    g = sns.FacetGrid(df_melted, col="Aircraft Type", row="Airport", hue="GRD_TIME_GROUP", legend_out=True)

    # Map a bar plot
    g.map(sns.barplot, "GRD_TIME_GROUP", "TOTAL AC")

    # Add a legend
    g.add_legend()

    # Add labels to the bars
    for ax in g.axes.flat:
        for bar in ax.patches:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{int(bar.get_height())}', 
                    fontsize=10, ha='center', va='bottom')

    # Change x-axis labels
    new_labels = ['5-7 H', '7-10 H', '>10 H']
    for ax in g.axes.flat:
        ax.set_xticklabels(new_labels)

    
    # Show the plot
    plt.show()