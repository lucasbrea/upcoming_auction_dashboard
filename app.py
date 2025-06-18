from flask import Flask, render_template, request, send_file, url_for, jsonify
from flask_cors import CORS
import pandas as pd
import os
import seaborn as sns
import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px
from plotly.io import to_html
from io import BytesIO
from weasyprint import HTML
import sys
from dateutil import parser
from unidecode import unidecode
from openai import OpenAI
# import json
# from dotenv import load_dotenv
# import traceback

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
print(sys.executable)

print("CWD:", os.getcwd())
#Path to install packages in venv
# /Users/lucasbrea/Move37/dashboard_remates/.venv/bin/python -m pip install package


app = Flask(__name__)
CORS(app)

CSV_PATH = os.path.join("Data/dashboard_data.csv")
DAMS_CSV_PATH = os.path.join("Data/Dashboard_Data_Dams_Table.csv")
AUCTIONED_HORSES_PATH = os.path.join("Data/Past Auction - Horses.csv")
SERVICES_PATH = os.path.join("Data/possible_dams_servicios.csv")
HORSES_RENAMED_COLUMNS = {
    'name': 'Horse',
    # 'studbook_id': 'Studbook ID',
    'padrillo': 'Sire',
    'M': 'Dam',
    'birth_eday':'Birth Date',
    'sex': 'Sex',
    'haras': 'Haras',
    'link' : 'Href',
    'lote': 'Lote',
    'start': 'Start',
    'end_date': 'End',
    'MSib_StkWnrs_Offs': 'Dam Stk Wnrs / RA Offs',
    'MomSib_Sibs_at2y' : 'Dams RA Offs',
    'Dam_Mean_T3_BSN': 'Top BSNs',
    'Dam_Raced_STK': 'Dam Raced STK?',
    'Dam_Placed_STK': 'Dam Placed STK?',
    'Dam_Total_Rcs': 'Dam Total Races',
    'Best_Foal_Raced_Stk':'Dam\'s Foal Raced Stk?',
    'Best_Foal_Placed_Stk':'Dam\'s Foal Placed Stk?',
    'Dam_Sib_Total_G1G2': 'Dam\'s Siblings Total G1/G2',
    'DamSibs_G1G2_Total': 'Dam\'s Siblings G1G2/Races',
    'ownCharac': 'Own Chars',
    'father': 'Father',
    'Fathsiblings':'Father\'s Offs',
    'mother': 'Dam\'s Age and Racing Career',
    'Momsiblings':'Dam\'s Offsprings Performance',
    'uncles': 'Dam\'s Family (Parents & Siblings)',
    'maternalParents': 'Dam\'s Parents Career',
    'inbreedingCoefficient': 'Inbreeding',
    'M_age_at_birth': 'Age',
    'M_season': 'Dam\'s Season',
    'FathSibSTKWnrShL4Gens': 'STK Wnrs / Rnrs',
    'FathSib_runshare_3yo': '#Runners/ Born at 3yo',
    'MSib_mean_cumAEI_at2y':'CEI per foal',
    'PRS_Value':'PRS Value (2.200 USDB per Bps)',
    'FathSibSTKWnrShL4Gens':'STK Wins 2-5yo/#2-5yo',
    'f_STK_races_total_races':'STK Races /Races',
    'MomSib_Sibs_raced_at2y':'#Offs Ran',
    'MomSib_wnrs_STK_at2y':'Offs Stk Wnrs',
    'rank':'Ranking Gen23',
    'Best_Foal_Bsn': 'Offs Top BSNs',
    'birth_month': 'Birth Month',
    'raced_won_g1_yn':'Raced Stk? Won G-Stk? Won-G1?',
    'sire_ps':'Sire PS',
    'FathSibSTKWnrsPerOffs':'Recent G1 Wnrs/Born',
    'MomSib_wnrs3yo_at2y':'Offs Wnrs before 3yo(non-ALT)',
    'cei_per_offs':'CEI per offs(**)',
    'criador_PRS':'Mean PRS',
    'criador':'Criador'



}
DAMS_RENAMED_COLUMNS = {
    'name_clean': 'Name',
    'padrillo_clean': 'Sire',
    'M_clean': 'Dam',
    'haras': 'Haras',
    'link':'Href',
    'start': 'Start',
    'end_date': 'End',
    'lote': 'Lote',
    'inbreedingCoefficient': 'Inbreeding Coef.',
    'mother': 'Age and Racing Career',
    'Momsiblings': 'Offsprings\' Quality',
    'uncles': 'Siblings\' quality',
    'maternalParents': 'Parents Career',
    'M_age_at_service': 'Age',
    'M_season_orig': 'Dam\'s Season',
    'birthRate': 'Birth Rate (All)',
    'birthRateLast3': 'Birth Rate (last 3)',
    'hadRestYear': 'Had Rest Year',
    'M_total_rcs': 'Total Races',
    'M_won_rcs': 'Total Wins',
    'M_cumAEI': 'CEI',
    'M_STK_ran': 'Stk Races',
    'M_STK_won': 'Stk Wins',
    'M_g1_STK_placed': 'G1 Placed',
    'M_g1_STK_won': 'G1 Wins',
    'MomSib_STKRunners_at2y':'Foals Stk Rnrs',
    'MomSib_wnrs_STK_at2y': 'Foals Stk Wnrs',
    'MomSib_Sibs_at2y' : 'Dams RA Offs',
    'MomSib_Sibs_raced_at2y': '#Offs Ran',
    'Dam_Mean_T3_BSN': 'Top 3 BSN\'s',
    'Dam_Raced_STK': 'Dam Raced STK?',
    'Dam_Placed_STK': 'Dam Placed STK?',
    'Dam_Total_Rcs': 'Dam Total Races',
    'Best_Foal_Bsn': 'Dam\'s Foals Top 3 BSN',
    'Best_Foal_Raced_Stk':'Dam\'s Foal Raced Stk?',
    'Best_Foal_Placed_Stk':'Dam\'s Foal Placed Stk?',
    'Dam_Sib_Total_G1G2': 'Dam\'s Siblings Total G1/G2',
    'DamSibs_G1G2_Total': 'Dam\'s Siblings G1G2/Races',
    'PBRS': 'PBRS',
    'PB': 'PB',
    'PRS': 'PRS',
    'PR': 'PR',
    'PS': 'PS',
    'TPBRS':'TPBRS',
    'MSibs_GSTK_Total_runs':'Siblings total G-stk runs',
    'MSibs_GSTK_Total_wins':'Siblings total G-stk wins',
    'foal_wnrs_3yo':'Foals wnrs before 3yo(non-ALT)', 
    'rank':'Ranking',
    'num_births':'#Births',
    'num_services':'#Services',
    'offs_ran_over_2yo':'#Offs Ran / #Running age',
    'Dam_raced_stk_won_stk':'Raced Stk? Won G-Stk?',
    'ultimo_servicio':'Date last service',
    'nacimientos_adj': '#Births',
    'servicios_adj': '#Services',
    'efectividad_adj': 'Birth Rate',
}

PAST_AUCTION_RENAMED_COLUMNS = {
    'name_clean': 'Name',
    'padrillo_clean': 'Sire',
    'M_clean': 'Dam',
    'birth_eday': 'Birth Date',
    'sex': 'Sex',
    'PR': 'PR',
    'PS': 'PS',
    'PRS': 'PRS',
    'haras1': 'Haras',
    # 'value': 'Value',
    'valueUSDB': 'Value USDB',
    'pricePerBp': 'Price per Bp',
    'title': 'Title',
    'Sire_PS': 'Sire PS',   
    # 'source': 'Source', 
    'auctionOrder': 'Auction Order',
    # 'studbook_id': 'Studbook ID',
    'auctionYear': 'Year',
    'eday': 'Auction Date',
    'haras1':'Haras'

}

# Columnas para filtrar
HORSES_FILTER_COLUMNS = [
                        'Haras',
                        'Horse',
                        'Sire', 
                        'Dam', 
                        'Href',
                        'Sex'
                        ]

DAMS_FILTER_COLUMNS = [
                        'Name', 
                        'Sire', 
                        'Dam', 
                        'Haras', 
                        'Link'
                        ]

AUCTIONED_HORSES_FILTER_COLUMNS = [

                            'Name',
                            'Sire',
                            'Dam',
                            'Year',
                            'Haras',
                            'Title'
]



def load_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found at {file_path}")
    
    df = pd.read_csv(file_path)
    


    # Re formateo de valores, a porcentaje o rodondeado o strings
    up_columns = ['name_clean','padrillo_clean','M_clean','haras','name','padrillo','M']
    for col in up_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: unidecode(str(x).upper()) if pd.notnull(x) else x)

    percentage_columns = ['PS', 
                          'PR', 
                          'PRS',
                          'PB',
                          'TPBRS',
                          'PBRS', 
                          'inbreedingCoefficient',
                          'Sire_Stk_Wnrs_Rnrs', 
                          'MSib_StkWnrs_Offs',
                          'DamSibs_G1G2_Total',
                          'ownCharac', 
                          'father',
                          'Fathsiblings', 
                          'maternalParents',
                          'birthRateLast3',
                          'birthRate',
                        #   'hadRestYear',
                        'FathSibSTKWnrShL4Gens',
                        'FathSib_runshare_3yo',
                        'MSib_mean_cumAEI_at2y',
                        'f_STK_races_total_races',
                        'Momsiblings',
                        'mother',  
                        'uncles',
                        'offs_ran_over_2yo',
                        'sire_ps',
                        'Sire_PS',
                        'FathSibSTKWnrsPerOffs',
                        'efectividad_adj',
                        'Mean PRS',
                          ]
    for col in percentage_columns:
        if col in df.columns:
            # Multiply by 100
            df[col] = df[col] * 100

            # Use 1 decimal only for PRS, else round to int
            if col in ['PRS','PBRS',]:
                df[col] = df[col].round(1).apply(lambda x: f"{x}%" if pd.notnull(x) else "-")
            else:
                df[col] = df[col].round(0).apply(lambda x: f"{int(x)}%" if pd.notnull(x) else "-")
    rounded_columns =[
                       'dams_parents_career',
                       'Dam_Mean_T3_BSN',
                        'Best_Foal_Bsn',
                        'M_age_at_birth',
                        'M_age_at_service',
                        'hadRestYear',
                        'M_cumAEI',
                        'pricePerBp',
                        'valueUSDB',
                        'mMeanMaxBsn',
                        'cei_per_offs',   
                        'nacimientos_adj',
                        'servicios_adj',              
    ]
    for col in rounded_columns:
        if col in df.columns:
            if col in ['mother', 'uncles','Momsiblings']:
                df[col] = df[col].round(2).astype('float').astype(str).replace('<NA>', '-')
            else:
                df[col] = df[col].round().astype('Int64').astype(str).replace('<NA>', '-')
    return df

def filter_dataframe(df, filters):
    if not filters:
        return df

    filtered_df = df.copy()
    for column, value in filters.items():
        if value and column in filtered_df.columns:
            # Convert both the column and search value to strings and lowercase
            filtered_df = filtered_df[
                filtered_df[column].astype(str).str.lower().str.contains(
                    str(value).lower(), 
                    na=False
                )
            ]
    return filtered_df
# Load both datasets
horses_df = load_data(CSV_PATH)
dams_df = load_data(DAMS_CSV_PATH)
auctioned_horses_df = load_data(AUCTIONED_HORSES_PATH)
services_df = load_data(SERVICES_PATH)
dams_df['name_clean'] = dams_df['name_clean'].str.upper()

dams_df = pd.merge(dams_df, services_df, how='left', left_on='name_clean', right_on='name')

dams_df.fillna('-')

dams_df.rename(columns=DAMS_RENAMED_COLUMNS, inplace=True)

horses_df.rename(columns=HORSES_RENAMED_COLUMNS, inplace=True)

auctioned_horses_df.rename(columns=PAST_AUCTION_RENAMED_COLUMNS, inplace=True)




def format_dollar(x):
    try:
            return f"${float(x):,.0f}" if pd.notnull(x) else ""
    except Exception:
        return "" 
horses_df["PRS Value (2.200 USDB per Bps)"] = pd.to_numeric(horses_df["PRS Value (2.200 USDB per Bps)"], errors="coerce")    
horses_df["PRS Value (2.200 USDB per Bps)"] = horses_df["PRS Value (2.200 USDB per Bps)"].apply(format_dollar)


for col in ['Value', 'Value USDB', 'Price per Bp']:
    if col in auctioned_horses_df.columns:
        auctioned_horses_df[col] = auctioned_horses_df[col].apply(format_dollar)

horses_df_order = [
                #Basic Info
                'Ranking Gen23',
                'Horse',
                'Sire',
                'Dam',
                'Haras',
                'Sex',
                'Birth Month',
                'Birth Date',
                #Selection
                'PRS',
                'PR',
                'PS',
                #Decomposing PS Factors
                'Sire PS',
                'Dam\'s Age and Racing Career',
                'Dam\'s Offsprings Performance',
                'Dam\'s Family (Parents & Siblings)',
                #Sires PS Characteristics
                'STK Races /Races',
                'STK Wins 2-5yo/#2-5yo',
                'Recent G1 Wnrs/Born',
                #Dams PS Characteristics
                'Age',
                'Top BSNs',
                'Raced Stk? Won G-Stk? Won-G1?',
                '#Offs Ran',
                'Offs Top BSNs',
                'Offs Wnrs before 3yo(non-ALT)',
                'Offs Stk Wnrs',
                'CEI per offs(**)',
                'Dam\'s Siblings(GS) Stk wins',
                #Internal Value
                'PRS Value (2.200 USDB per Bps)',
                'Mean PRS',
                'Criador',
                #Auction info
                'Start',
                'End',
                'Lote',
                'Href'
                        ]

dams_df_order = [
    #Basic Information
    'Ranking',
    'Name',
    'Sire',
    'Dam',
    'Haras',
    #Selection
    'TPBRS',
    'PBRS',
    'PB',
    'PRS',
    'PR',
    'PS',
    #Decomposing PS Factors
    'Age and Racing Career',
    'Offsprings\' Quality',
    'Siblings\' quality',
    'Parents Career',
    #Main Characteristics
    'Age',
    'Top 3 BSN\'s',
    'Raced Stk? Won G-Stk?',
    '#Offs Ran',
    'Dam\'s Foals Top 3 BSN',
    'Foals wnrs before 3yo(non-ALT)',  
    'Foals Stk Rnrs',
    'Foals Stk Wnrs',
    'Siblings total G-stk runs',
    'Siblings total G-stk wins',
    #Inbreeding
    'Inbreeding Coef.',
    #Factors PB/PR  
    '#Offs Ran / #Running age',
    '#Services',
    '#Births',
    'Date last service',
    'Birth Rate',
    #Detailed Racing Career
    'Total Races',
    'Total Wins',
    'Stk Races',
    'Stk Wins',
    'G1 Placed',
    'G1 Wins',
    'CEI',
    #Auction Info
    'Lote',
    'Start',
    'End',
    'Href'

]

past_auction_order = [
    'Name',
    'Sire',
    'Dam',
    'Birth Date',
    'Sex',
    'PR',
    'PS',
    'PRS',
    'Haras',
    'Sire PS',
    # 'Value',
    'Value USDB',
    'Price per Bp',
    'Title',
    'Auction Order',
    'Year',
    'Auction Date'
]


horses_df = horses_df[[col for col in horses_df_order if col in horses_df.columns]]
dams_df = dams_df[[col for col in dams_df_order if col in dams_df.columns]]
auctioned_horses_df = auctioned_horses_df[[col for col in past_auction_order if col in auctioned_horses_df.columns]]


#We have to convert all the dates into the same format
def parse_birth_date(date_str):
    try:
        return pd.to_datetime(date_str, format='%d%b%Y', dayfirst=True)
    except Exception:
        return pd.NaT

def parse_start_end(date_str):
    try:
        return parser.parse(date_str, dayfirst=True)
    except Exception:
        return pd.NaT
def parse_service(date_str):
    try:
        date = pd.to_datetime(date_str)
        return date.strftime('%d/%m/%Y')
    except Exception:
        return None
# Apply the functions
horses_df['Birth Date'] = horses_df['Birth Date'].apply(parse_birth_date)
horses_df['Start'] = horses_df['Start'].apply(parse_start_end)
horses_df['End'] = horses_df['End'].apply(parse_start_end)
dams_df['Start'] = dams_df['Start'].apply(parse_start_end)
dams_df['End'] = dams_df['End'].apply(parse_start_end)
auctioned_horses_df['Auction Date'] = auctioned_horses_df['Auction Date'].apply(parse_start_end)
auctioned_horses_df['Birth Date'] = auctioned_horses_df['Birth Date'].apply(parse_birth_date)
dams_df['Date last service'] = dams_df['Date last service'].apply(parse_service)
# Format all as dd/mm/yy strings
horses_df['Birth Date'] = horses_df['Birth Date'].dt.strftime('%d/%m/%y')
horses_df['Start'] = horses_df['Start'].dt.strftime('%d/%m/%y')
horses_df['End'] = horses_df['End'].dt.strftime('%d/%m/%y')
dams_df['Start'] = dams_df['Start'].dt.strftime('%d/%m/%y')
dams_df['End'] = dams_df['End'].dt.strftime('%d/%m/%y')    
auctioned_horses_df['Auction Date'] = auctioned_horses_df['Auction Date'].dt.strftime('%d/%m/%y')
auctioned_horses_df['Birth Date'] = auctioned_horses_df['Birth Date'].dt.strftime('%d/%m/%y')


# Calculate max values for gradient columns
gradient_columns = [
            'Inbreeding Coef.',
            'PB',
            'PBRS',
            'PR',
            'PRS',
            'PS',
            'TPBRS'
        
]

horses_max_values = {col: float(horses_df[col].str.rstrip('%').astype(float).max()) 
                    for col in gradient_columns if col in horses_df.columns}


#Corrigo nombres de haras

horses_df['Haras'] = horses_df['Haras'].replace({
    'SANTA INAAS':'SANTA INES',
    'LA GENERACIAAN':'LA GENERACION',
})
dams_df['Haras'] = dams_df['Haras'].replace({
    'SANTA INAAS':'SANTA INES',
    'LA GENERACIAAN':'LA GENERACION',
})


dams_max_values = {}
for col in gradient_columns:
    if col in dams_df.columns:
        try:
            # Remove % and convert to numeric, ignoring errors
            numeric_values = pd.to_numeric(dams_df[col].str.rstrip('%'), errors='coerce')
            if not numeric_values.empty and not numeric_values.isna().all():
                max_val = numeric_values.max()
                if pd.notnull(max_val):
                    dams_max_values[col] = float(max_val)
        except Exception as e:
            print(f"Error processing column {col}: {str(e)}")
            continue

# # Initialize empty filter dictionaries
# horses_filters = {col: '' for col in HORSES_FILTER_COLUMNS}
# dams_filters = {col: '' for col in DAMS_FILTER_COLUMNS}
# auctioned_horses_filters = {col: '' for col in AUCTIONED_HORSES_FILTER_COLUMNS}

# horses_df = filter_dataframe(horses_df, horses_filters)
# dams_df = filter_dataframe(dams_df, dams_filters)
# auctioned_horses_df = filter_dataframe(auctioned_horses_df, auctioned_horses_filters)
#Replace sex int values with strings
horses_df['Sex'] = horses_df['Sex'].map({1: 'F', 2: 'M'})

column_groups_horses = [
                ("Basic Information", 8, "group-basic"),
                ("Selection", 3, "group-selection-horses"),
                ("Decomposing PS Factors", 4, "group-ps"),
                ("Sire\'s PS Characteristics", 3, "group-sire-ps"),
                ("Dam\'s PS Characteristics", 9, "group-dam-ps"),
                ("Internal Value",1, "group-internal-value"),
                ("Auction Info", 4, "group-auction")
            ]

column_groups_horses_h2 = [
                ("", 8, "group-basic"),
                ("", 3, "group-selection-horses"),
                ("", 4, "group-ps"),
                ("", 3, "group-sire-ps"),
                ("", 9, "group-dam-ps"),
                ("",1, "group-internal-value"),
                ("", 4, "group-auction")
            ]

column_groups_dams = [
                ("Basic Information", 5, "group-basic-dams"),
                ("Selection",6, "group-selection-dams"),
                ("Decomposing PS Factors",4, "group-ps-dam"),
                ("Main Characteristics", 10, "main-characteristics-dams"),
                ("Inbreeding",1,"group-inbreeding-dams"),
                ("Factors PB/PR", 5, "group-pb-dam"),
                ("Detailed Racing Career", 7, "group-racing-dam"),
                ("Auction Info", 4, "group-auction")
            ]
column_groups_dams_h2 = [
                ("", 5, "group-basic-dams"),
                ("",6, "group-selection-dams"),
                ("",4, "group-ps-dam"),
                ("", 10, "main-characteristics-dams"),
                ("",1,"group-inbreeding-dams"),
                ("", 5, "group-pb-dam"),
                ("", 7, "group-racing-dam"),
                ("", 4, "group-auction"),
            ]

column_groups_auctioned_horses = [

                ("Basic Information", 9, "group-basic"),
                ("Auction Info", 7, "group-past-auction")
]
column_groups_auctioned_horses_h2 = [

                ("", 16, "group-basic")
]



df = pd.read_csv("Data/Past Auction - Horses.csv")

def extract_code_block(text: str) -> str:
    """Extracts the Python code inside triple backticks."""
    if "```" in text:
        lines = text.strip().splitlines()
        in_code = False
        code_lines = []
        for line in lines:
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                code_lines.append(line)
        return "\n".join(code_lines)
    return text.strip()

def sanitize_code(code: str) -> str:
    return (
        code.replace("’", "'")
            .replace("‘", "'")
            .replace("“", '"')
            .replace("”", '"')
            .strip()
    )

# Fix up bad formats
def clean_data(df):
    if 'valueUSDB' in df.columns:
        df['valueUSDB'] = (
            df['valueUSDB'].astype(str)
            .str.extract(r'([\d,\.]+)')[0]
            .str.replace(',', '', regex=False)
            .fillna('0')
            .astype(float)
        )
    if 'eday' in df.columns:
        df['eday'] = pd.to_datetime(df['eday'], errors='coerce')
    return df

df = clean_data(df)
    
# @app.route('/')
# def index():
#     try:
#         #         # Update with any values from the request
#         # for col in HORSES_FILTER_COLUMNS:
#         #     if request.args.get(f'horses_{col}'):
#         #         horses_filters[col] = request.args.get(f'horses_{col}')

#         # for col in DAMS_FILTER_COLUMNS:
#         #     if request.args.get(f'dams_{col}'):
#         #         dams_filters[col] = request.args.get(f'dams_{col}')

#         # for col in AUCTIONED_HORSES_FILTER_COLUMNS:
#         #     if request.args.get(f'auctioned_horses_{col}'):
#         #         auctioned_horses_filters[col] = request.args.get(f'auctioned_horses_{col}')

#         horses_data = horses_df.to_dict(orient="records")
#         horses_columns = horses_df_order

#         dams_data = dams_df.to_dict(orient="records")
#         dams_columns = dams_df_order

#         auctioned_horses_data = auctioned_horses_df.to_dict(orient="records")
#         auctioned_horses_columns = past_auction_order

#         initial_tab = request.args.get('tab', 'horses')
        
#         return render_template('index.html', 
#                             initial_tab=initial_tab,
#                              column_groups=column_groups_horses,
#                              column_groups_horses_h2=column_groups_horses_h2,
#                              horses_data=horses_data,
#                              horses_columns=horses_columns,

#                              dams_data=dams_data,
#                              dams_columns=dams_columns,
#                              column_groups_dams=column_groups_dams,
#                              column_groups_dams_h2=column_groups_dams_h2,


#                             #  horses_filters=horses_filters,
#                             #  dams_filters=dams_filters,
#                             #  auctioned_horses_filters=auctioned_horses_filters,

#                              auctioned_horses_data=auctioned_horses_data,
#                              auctioned_horses_columns=auctioned_horses_columns,
#                              column_groups_auctioned_horses=column_groups_auctioned_horses,
#                              column_groups_auctioned_horses_h2=column_groups_auctioned_horses_h2,

#                              horses_max_values=horses_max_values,
#                              dams_max_values=dams_max_values,

#                              )
    
    
#     except Exception as e:
#         # When there's an error, we still need to pass empty filters
#         return render_template('index.html', 
#                              error=str(e),
#                              horses_filters={col: '' for col in HORSES_FILTER_COLUMNS},
#                              dams_filters={col: '' for col in DAMS_FILTER_COLUMNS},
#                              auctioned_horses_filters={col: '' for col in AUCTIONED_HORSES_FILTER_COLUMNS})
    
@app.route('/api/data/dams')
def get_data():
    return jsonify(dams_df.replace({pd.NA: '-', pd.NaT: '-'}).to_dict(orient="records"))

@app.route('/api/data/horses')
def get_data_horses():
    return jsonify(horses_df.replace({pd.NA: '-', pd.NaT: '-'}).to_dict(orient="records"))

@app.route('/api/data/past_auctions')
def get_data_auctions():
    return jsonify(auctioned_horses_df.replace({pd.NA: '-', pd.NaT: '-'}).to_dict(orient="records"))

@app.route("/api/ai-plot", methods=["POST"])
def ai_plot():
    prompt = request.json.get("prompt")
    try:
        schema = ", ".join([f"{col}: {str(df[col].dtype)}" for col in df.columns])
        full_prompt = f"""
You are a data scientist working with a DataFrame that contains historical horse auction data. Below is the schema of the DataFrame:
{schema}

Based on the following user request:

”{prompt}”

Write Python code that uses pandas and plotly.express to generate a plot object named fig.
Do not display, save, or export the plot. Your response must include only the Python code needed to generate fig, nothing else (no explanations or comments).

Context for the data:
	•	The dataset contains information about horses sold at auction.
	•	The column “Name” refers to the name of the horse being auctioned.
	•	Columns "padrilloAuction" and "yeguaAuction" correspond to “Sire” and “Dam” and refer to the horse’s father and mother, respectively.
	•	“PRS” is a percentage value that measures a horse’s quality. It is the main metric used to compare horses.
	•	“PR” and “PS” are subcomponents of PRS.
	•	“value USDB” indicates how much the horse sold for at auction (in US dollars).
	•	“Price per BP” indicates the value of each basis point of PRS.
	•	The top criadores (breeders) to highlight or segment if needed are: Firmamento, Abolengo, Vacacion, and El Paraiso.
    •	The haras1 column is the same as saying criador.
    •	The title columns refers to the title of a specific auction.
    •	The year column refers to the year of the auction.
    •	The the birth_eday column refers to the birth date of the horse sold.
        """

        res = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}]
        )

        raw = res.choices[0].message.content
        code = sanitize_code(extract_code_block(raw))
        print("Generated Code (cleaned):\n", code)
        print("Generated code:\n", code)

        local_vars = {'df': df.copy(), 'pd': pd, 'px': px}
        print("RAW GPT OUTPUT:")
        print(repr(code)) 
        exec(code, {}, local_vars)
        fig = local_vars.get("fig")

        if not fig:
            return jsonify({"error": "No figure was generated."}), 400

        return jsonify({"plot": fig.to_json()})

    except Exception as e:
        import traceback
        print("ERROR:\n", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/reports")
def reports_landing():
    return render_template("reports_landing.html")

@app.route("/reports/tables")
def reports_tables():
    return render_template("reports_tables.html")
@app.route("/reports/statistics")
def reports_reports():
    return render_template("reports_reports.html")
@app.route("/reports/presentations")
def reports_presentations():
    return render_template("reports_presentations.html")

#Paths to folders inside reports
@app.route("/reports/statistics/choicesVScriador")
def reports_choices_criador():
    return render_template("reports_folders/choices_vs_criador.html")
@app.route("/reports/statistics/criador-caballeriza")
def reports_criador_caballeriza():
    return render_template("reports_folders/criador-caballeriza.html")
@app.route("/reports/statistics/horse")
def reports_horse():
    return render_template("reports_folders/reports_horse.html")
@app.route("/reports/statistics/jockey")
def reports_jockey():
    return render_template("reports_folders/reports_jockey.html")
@app.route("/reports/statistics/trainer")
def reports_trainer():
    return render_template("reports_folders/reports_trainer.html")

# (Add statistics/presentations if needed)

if __name__ == '__main__':
    app.run(debug=True) 