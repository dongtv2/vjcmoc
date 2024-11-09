# db_utils.py
import sqlite3

def def_connect_sqlite(db_name):
    conn = None
    try:
        path = f"{db_name}"
        conn = sqlite3.connect(path)
    except sqlite3.Error as e:
        print(e)    
    return 

def process_excel_season_file(file_path,df_date):
        
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

    # Connect to the SQLite database
    conn = def_connect_sqlite()
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