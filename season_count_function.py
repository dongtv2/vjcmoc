
from season_function import *
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd

# count the number of flights for each day of the week
count_flights = [len(df) for df in processed_dfs]
print(count_flights)

# count the number of AC for each day of the week
count_ac = [df['AC'].nunique() for df in processed_dfs]

## -- HÀM TÍNH TỔNG BLOCK TIME CỦA FLEET THEO NGÀY - BEGIN--##

# def calculate_total_block_time(df):
#     # Convert 'BLOCK_TIME' strings to minutes
#     df['BLOCK_TIME'] = df['BLOCK_TIME'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

#     # Calculate the total 'BLOCK_TIME'
#     total_block_time = df['BLOCK_TIME'].sum()

#     # Convert the total 'BLOCK_TIME' to 'HH:MM' format
#     total_hours = total_block_time // 60
#     total_minutes = total_block_time % 60
#     total_block_time_str = f"{int(total_hours)}:{int(total_minutes):02d}"

#     return total_block_time_str

def calculate_total_block_time(df):
    # Check if 'BLOCK_TIME' needs to be converted
    if df['BLOCK_TIME'].dtype == 'object':
        # Convert 'BLOCK_TIME' strings to minutes
        df['BLOCK_TIME'] = df['BLOCK_TIME'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    # Calculate the total 'BLOCK_TIME'
    total_block_time = df['BLOCK_TIME'].sum()

    # Convert the total 'BLOCK_TIME' to 'HH:MM' format
    total_hours = total_block_time // 60
    total_minutes = total_block_time % 60
    total_block_time_str = f"{int(total_hours)}:{int(total_minutes):02d}"

    return total_block_time_str

# -- HÀM TÍNH TỔNG BLOCK TIME CỦA FLEET THEO NGÀY - END--##



def calculate_total_block_time_each_ac(df):
    def convert_time(time_str):
        if isinstance(time_str, str):
            try:
                hours, minutes = time_str.split(':')
                return int(hours) * 60 + int(minutes)
            except (ValueError, IndexError):
                return 0
        elif isinstance(time_str, (int, float)):
            return int(time_str)
        else:
            return 0

    # Handle missing values in 'BLOCK_TIME'
    df['BLOCK_TIME'] = df['BLOCK_TIME'].fillna(0)

    # Convert 'BLOCK_TIME' to minutes
    df['BLOCK_TIME'] = df['BLOCK_TIME'].apply(convert_time)

    # Group by 'AC' and calculate the sum of 'BLOCK_TIME'
    total_block_time_each_ac = df.groupby('AC')['BLOCK_TIME'].sum()

    return total_block_time_each_ac

def plot_total_block_time(total_block_time_each_ac, title):
    plt.figure(figsize=(15, 5))  # Increase figure size

    # Color bars based on whether they meet the KPI
    colors = ['gold' if x < 845 else 'b' for x in total_block_time_each_ac]
    total_block_time_each_ac.plot(kind='bar', color=colors)

    plt.title(title)
    plt.xlabel('AC')
    plt.ylabel('Total Block Time')

    # Add KPI line at y = 14:05 (which is 845 minutes)
    plt.axhline(y=845, color='green', linestyle='--')
    plt.axhline(y=1440, color='red', linestyle='--', label='> 24 hours')

    # Format y ticks
    y_ticks = np.arange(0, total_block_time_each_ac.max() + 120, 120)  # Increase y-tick step
    plt.yticks(y_ticks, [f"{int(y_tick // 60):02d}:{int(y_tick % 60):02d}" for y_tick in y_ticks])

    # Add labels for the number of aircraft that meet and don't meet the KPI
    num_meet_kpi = sum(total_block_time_each_ac >= 845)
    num_dont_meet_kpi = sum(total_block_time_each_ac < 845)
    plt.text(0.02, 0.95, f'Number of AC that meet KPI: {num_meet_kpi}', transform=plt.gca().transAxes)
    # plt.text(0.02, 0.90, f'Number of AC that don\'t meet KPI: {num_dont_meet_kpi}', transform=plt.gca().transAxes, colors='yellow')
    plt.text(0.02, 0.90, f'Number of AC that don\'t meet KPI: {num_dont_meet_kpi}', transform=plt.gca().transAxes, color='gold')
total_block_time_each_ac_day1 = calculate_total_block_time_each_ac(df_D1_1_copy)
total_block_time_each_ac_day2 = calculate_total_block_time_each_ac(df_D2_1_copy)
total_block_time_each_ac_day3 = calculate_total_block_time_each_ac(df_D3_1_copy)
total_block_time_each_ac_day4 = calculate_total_block_time_each_ac(df_D4_1_copy)