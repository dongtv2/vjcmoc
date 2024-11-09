## CONFIG PAGE
import streamlit as st

import streamlit.components.v1 as components
st.set_page_config(page_title='ACREADINESS HOMPAGE', page_icon='🔒', layout='wide')
st.set_option('deprecation.showPyplotGlobalUse', False)

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from streamlit_option_menu import option_menu

from season_function import * # load all function from season_function.py
from season_count_function import * # load all function from season_count_function.py

from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder

import matplotlib.pyplot as plt

import pygwalker as pyg


# Load the configuration file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create an authentication object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Render the login widget
name, authentication_status, username = authenticator.login(
    location='main',
    fields={
        'Form name': 'Login',
        'Username': 'Username',
        'Password': 'Password',
        'Login': 'Login'
    }
)

# Check the authentication status
if authentication_status:


    with st.sidebar:
        authenticator.logout('Logout', 'main')

        selected = option_menu(
            menu_title = st.write(f'Welcome ...*{name}*'),
            
            options = ['Dashboard', 'Season Flight', 'Daily Flight', 'Reset Password'],
        )

    if selected == 'Dashboard':
        st.title('Dashboard')
        st.write('Welcome to the dashboard')
        df1 = pyg.to_html(results_df_D1_D2)
        components.html(df1, height=1000, scrolling=True)    

    if selected == 'Season Flight':
        st.title('Season Flight')
        st.write('Welcome to the Season Flight')

        tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9 = st.tabs(["Import","Select","D1-Mon","D2-Tue","D3-Wed","D4-Thu","D5-Fri","D6-Sat","D7-Sun"])

        ## Tab1 --- Import Data --- ##
        with tab1:
            st.write('Import Data')
                # Import flight data
            with st.expander("Import Flight Data", expanded=True):
                df_date = st.date_input("Select a date to import", value=None)

                if df_date is not None:
                    st.write("Selected date:", df_date.strftime("%m.%d.%Y"))

                uploaded_file = st.file_uploader("Upload Season flight plan XLSX file", type='xlsx')
                if uploaded_file is not None:
                    df_com = process_excel_season_file(uploaded_file,df_date)
                    st.dataframe(df_com)
        with tab2:
            st.write('Select Data')

            df = display_flightplan_by_date()
            st.dataframe(df)

        with tab3:
            st.title('D1- Monday')
            st.write('#### Tổng số máy bay sử dụng ngày 1:',f'<span style="font-size: 24px;">{count_ac[0]}</span>', unsafe_allow_html=True)
            st.write('#### Tổng số chuyến bay ngày 1:',f'<span style="font-size: 24px;">{count_flights[0]}</span>', unsafe_allow_html=True)
            st.write('#### Tổng thời gian bay ngày 1:',f'<span style="font-size: 24px;">{calculate_total_block_time(df_D1_1)}</span>', unsafe_allow_html=True)
            
            
            with st.expander("D1- Monday - Đã tính block time & ground time (TAT)", expanded=False):
                AgGrid(df_D1_1_copy)
            
            with st.expander("Kết quả tìm kiếm ngày 1 và ngày 2 số tàu ground time theo station và theo ac type", expanded=False):
                results_df_D1_D2 = results_df_D1_D2.reset_index()
                AgGrid(results_df_D1_D2)
            
            with st.expander("Biểu đồ KPI số giờ bay của mỗi tàu - Ngày 1"):
                st.info('Dựa vào đây để biết được tần suất các tầu bay')
                st.pyplot(plot_total_block_time(total_block_time_each_ac_day1, 'Total Block Time for Each AC in Day 1'))

            with st.expander("Biểu đồ kết quả", expanded=False):
                st.pyplot(plot_results(results_df_D1_D2))   

        with tab4:
            st.write('D2- Tuesday')
            st.write('#### Tổng số máy bay sử dụng ngày 2:',f'<span style="font-size: 24px;">{count_ac[1]}</span>', unsafe_allow_html=True)
            st.write('#### Tổng số chuyến bay ngày 2:',f'<span style="font-size: 24px;">{count_flights[1]}</span>', unsafe_allow_html=True)
            st.write('#### Tổng thời gian bay ngày 2:',f'<span style="font-size: 24px;">{calculate_total_block_time(df_D2_1)}</span>', unsafe_allow_html=True)
        
            with st.expander("D2- Tue - Đã tính block time & ground time (TAT)", expanded=False):
                AgGrid(df_D2_1_copy)
            
            with st.expander("Kết quả tìm kiếm ngày 1 và ngày 2 số tàu ground time theo station và theo ac type", expanded=False):
                results_df_D2_D3 = results_df_D2_D3.reset_index()
                AgGrid(results_df_D2_D3)
            
            with st.expander("Biểu đồ KPI số giờ bay của mỗi tàu - Ngày 1"):
                st.info('Dựa vào đây để biết được tần suất các tầu bay')
                st.pyplot(plot_total_block_time(total_block_time_each_ac_day2, 'Total Block Time for Each AC in Day 2'))

            with st.expander("Biểu đồ kết quả", expanded=False):
                st.pyplot(plot_results(results_df_D2_D3))   

        
        with tab5:
            st.write('D3- Wednesday')

        with tab6:
            st.write('D4- Thursday')

        with tab7:
            st.write('D5- Friday')
        
        with tab8:
            st.write('D6- Saturday')
        
    if selected == 'Daily Flight':
        st.title('Daily Flight')
        st.write('Welcome to the Daily Flight')    

    if selected == 'Reset Password':
        st.title('Reset Password')
        # Reset password widget
        if authentication_status:
            try:
                if authenticator.reset_password(username):
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(e)

        # Update the configuration file
        with open('../config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
