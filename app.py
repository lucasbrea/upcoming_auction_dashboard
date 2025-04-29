from flask import Flask, render_template, request, send_file, url_for
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
print(sys.executable)

print("CWD:", os.getcwd())
#Path to install packages in venv
# /Users/lucasbrea/Move37/dashboard_remates/.venv/bin/python -m pip install package


app = Flask(__name__)

CSV_PATH = os.path.join("Data/dashboard_data.csv")
DAMS_CSV_PATH = os.path.join("Data/Dashboard_Data_Dams_Table.csv")
PAST_AUCTION_PATH = os.path.join("Data/past_auction_summary.csv")
AUCTIONED_HORSES_PATH = os.path.join("Data/Auctioned_Horses_Data.csv")




HORSES_RENAMED_COLUMNS = {
    'name': 'Name',
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
    'Dam_Mean_T3_BSN': 'Dam Top 3 BSN\'s',
    'Dam_Raced_STK': 'Dam Raced STK?',
    'Dam_Placed_STK': 'Dam Placed STK?',
    'Dam_Total_Rcs': 'Dam Total Races',
    'Best_Foal_Bsn': 'Dam\'s Foals Top 3 BSN',
    'Best_Foal_Raced_Stk':'Dam\'s Foal Raced Stk?',
    'Best_Foal_Placed_Stk':'Dam\'s Foal Placed Stk?',
    'Dam_Sib_Total_G1G2': 'Dam\'s Siblings Total G1/G2',
    'DamSibs_G1G2_Total': 'Dam\'s Siblings G1G2/Races',
    'ownCharac': 'Own Chars',
    'father': 'Father',
    'Fathsiblings':'Father\'s Offs',
    'mother': 'Dam\'s Age and Racing Career',
    'Momsiblings': 'Dam\'s Offs',
    'uncles': 'Dam\'s Sibs',
    'maternalParents': 'Dam\'s Parents Career',
    'inbreedingCoefficient': 'Inbreeding',
    'M_age_at_birth': 'Age',
    'M_season': 'Dam\'s Season',
    'FathSibSTKWnrShL4Gens': 'STK Wnrs / Rnrs',
    'FathSib_runshare_3yo': '#RUnners/ Born at 3yo',
    'MSib_mean_cumAEI_at2y':'CEI per foal'

}
DAMS_RENAMED_COLUMNS = {
    'name_clean': 'Name',
    'padrillo_clean': 'Sire',
    'M_clean': 'Dam',
    'haras': 'Haras',
    'link': 'Href',
    'start': 'Start',
    'end_date': 'End',
    'lote': 'Lote',
    'inbreedingCoefficient': 'Inbreeding Coef.',
    'mother': 'Dam\'s Age and Racing Career',
    'Momsiblings': 'Dam\'s Offs',
    'uncles': 'Dam\'s Sibs',
    'maternalParents': 'Dam\'s Parents Career',
    'M_age_at_service': 'Dam\'s Age',
    'M_season_orig': 'Dam\'s Season',
    'birthRate': 'Birth Rate (All)',
    'birthRateLast3': 'Birth Rate (last 3)',
    'hadRestYear': 'Had Rest Year',
    'M_total_rcs': 'Dam\'s total races',
    'M_won_rcs': 'Dam\'s total wins',
    'M_cumAEI': 'Dam\'s CEI',
    'M_STK_ran': 'Dam STK races',
    'M_STK_won': 'Dam STK wins',
    'M_g1_STK_placed': 'Dam G1 STK placed',
    'M_g1_STK_won': 'Dam G1 STK wins',
    'MSib_StkWnrs_Offs': 'Dam Stk Wnrs / RA Offs',
    'MomSib_Sibs_at2y' : 'Dams RA Offs',
    'MomSib_Sibs_raced_at2y': '#Offs Ran',
    'Dam_Mean_T3_BSN': 'Dam Top 3 BSN\'s',
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
    'PS': 'PS'
}

PAST_AUCTION_RENAMED_COLUMNS = {
    'name': 'Name',
    'padrilloAuction': 'Sire',
    'yeguaAuction': 'Dam',
    'birth_eday': 'Birth Date',
    'genre': 'Sex',
    'PR': 'PR',
    'PS': 'PS',
    'PRS': 'PRS',
    'haras1': 'Haras',
    # 'value': 'Value',
    'valueUSDB': 'Value USDB',
    'pricePerBp': 'Price per Bp',
    'title': 'Title',
    # 'source': 'Source', 
    'auctionOrder': 'Auction Order',
    'studbook_id': 'Studbook ID',
    'year': 'Year',
    'eday': 'Auction Date'

}


PAST_AUCTION_SUMMARY_RENAMED_COLUMNS = {

    'birth_eday': 'Birth Date',
    'genre': 'Sex',
    'PR': 'PR',
    'PS': 'PS',
    'PRS': 'PRS',
    'haras1': 'Criador',
    # 'value': 'Value',
    'valueUSDB': 'valueUSDB',
    'pricePerBp': 'PricePerBp',
    'title': 'Title',
    # 'source': 'Source', 
    'auctionOrder': 'Auction Order',
    'studbook_id': 'Studbook ID',
    'year': 'Year',
    'eday': 'Auction Date'

}


# Columnas para filtrar
HORSES_FILTER_COLUMNS = [
                        'Haras',
                        'Name',
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
AUCTIONS_FILTER_COLUMNS = [
                            'Criador', 
                            'Year', 
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
                          'PBRS', 
                          'inbreedingCoefficient',
                          'Sire_Stk_Wnrs_Rnrs', 
                          'MSib_StkWnrs_Offs',
                          'DamSibs_G1G2_Total',
                          'ownCharac', 
                          'father',
                          'Fathsiblings', 
                          'mother', 
                          'Momsiblings', 
                          'uncles',
                          'maternalParents',
                          'birthRateLast3',
                          'birthRate',
                        #   'hadRestYear',
                          'FathSibSTKWnrShL4Gens',
                          'FathSib_runshare_3yo',
                          'MSib_mean_cumAEI_at2y'
                          ]
    for col in percentage_columns:
        if col in df.columns:
            # Multiply by 100
            df[col] = df[col] * 100

            # Use 1 decimal only for PRS, else round to int
            if col in ['PRS','PBRS']:
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
                        'valueUSDB'
    ]
    for col in rounded_columns:
        if col in df.columns:
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

@app.route('/')
def index():
    try:
        # Load both datasets
        horses_df = load_data(CSV_PATH)
        dams_df = load_data(DAMS_CSV_PATH)
        past_auction_summary = load_data(AUCTIONED_HORSES_PATH)
        auctioned_horses_df = load_data(AUCTIONED_HORSES_PATH)

        dams_df.rename(columns=DAMS_RENAMED_COLUMNS, inplace=True)

        horses_df.rename(columns=HORSES_RENAMED_COLUMNS, inplace=True)

        auctioned_horses_df.rename(columns=PAST_AUCTION_RENAMED_COLUMNS, inplace=True)

        past_auction_summary.rename(columns=PAST_AUCTION_SUMMARY_RENAMED_COLUMNS, inplace=True)

        def format_dollar(x):
            try:
                 return f"${float(x):,.0f}" if pd.notnull(x) else ""
            except Exception:
                return ""
        past_auction_summary["valueUSDB"] = pd.to_numeric(past_auction_summary["valueUSDB"], errors="coerce")
        past_auction_summary["PricePerBp"] = pd.to_numeric(past_auction_summary["PricePerBp"], errors="coerce")       
        past_auction_summary = past_auction_summary.groupby(["Criador","Year"]).agg(
            valueUSDB=("valueUSDB", "mean"),
            PricePerBp=("PricePerBp", "mean"),
            count=("valueUSDB", "count"),

        ).reset_index()

        past_auction_summary["valueUSDB"] = past_auction_summary["valueUSDB"].apply(format_dollar)
        past_auction_summary["PricePerBp"] = past_auction_summary["PricePerBp"].apply(format_dollar)

        for col in ['Value', 'Value USDB', 'Price per Bp']:
            if col in auctioned_horses_df.columns:
                auctioned_horses_df[col] = auctioned_horses_df[col].apply(format_dollar)

        horses_df_order = [
                       'Name',
                       'Sire',
                        'Dam',
                        'Sex',
                        'Birth Date',
                        'Haras',
                        'PRS',
                        'PR',
                        'PS',
                        'STK Wnrs / Rnrs',
                        '#RUnners/ Born at 3yo',
                        'Age',
                        'Dam Stk Wnrs / RA Offs',
                        'Dams RA Offs',
                        'Dam Top 3 BSN\'s',
                        'Dam\'s Foals Top 3 BSN',
                        'Dam Placed STK?',
                        'Dam Raced STK?',
                        'Dam Total Races',
                        'Dam\'s Foal Raced Stk?',
                        'Dam\'s Foal Placed Stk?',
                        'Dam\'s Siblings Total G1/G2',
                        'Dam\'s Siblings G1G2/Races',
                        'CEI per foal',
                        'Own Chars',
                        'Father',
                        'Father\'s Offs',
                        'Dam\'s Age and Racing Career',
                        'Dam\'s Offs',
                        'Dam\'s Sibs',
                        'Dam\'s Parents Career',
                        'Inbreeding',
                        'Dam\'s Season',
                        'Start',
                        'End',
                        'Lote',
                        'Href'
                        # 'Studbook ID'
                             ]
        
        dams_df_order = [
            'Name',
            'Sire',
            'Dam',
            'Haras',
            'PBRS',
            'PB',
            'PRS',
            'PR',
            'PS',
            'Dam\'s Age',
            'Dam Stk Wnrs / RA Offs',
            'Dams RA Offs',
            '#Offs Ran',
            'Dam Top 3 BSN\'s',
            'Dam\'s Foals Top 3 BSN',
            'Dam Raced STK?',
            'Dam\'s Foal Raced Stk?',
            'Dam\'s Foal Placed Stk?',
            'Dam\'s Siblings Total G1/G2',
            'Dam\'s Siblings G1G2/Races',
            'Inbreeding Coef.',
            'Dam\'s Age and Racing Career',
            'Dam\'s Offs',
            'Dam\'s Sibs',
            'Dam\'s Parents Career',
            'Dam\'s Season',
            'Birth Rate (All)',
            'Birth Rate (last 3)',
            'Had Rest Year',
            'Dam\'s total races',
            'Dam\'s total wins',
            'Dam\'s CEI',
            'Dam STK races',
            'Dam STK wins',
            'Dam G1 STK placed',
            'Dam G1 STK wins',
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
            # 'Value',
            'Value USDB',
            'Price per Bp',
            'Title',
            'Auction Order',
            'Year',
            'Auction Date'
        ]

        past_auction_summary_order = [
            'Criador',
            'Year',
            'valueUSDB',
            'PricePerBp',
            'count'
        ]
        horses_df = horses_df[horses_df_order]
        dams_df = dams_df[dams_df_order]
        auctioned_horses_df = auctioned_horses_df[past_auction_order]
        past_auction_summary = past_auction_summary[past_auction_summary_order]
        
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

        # Apply the functions
        horses_df['Birth Date'] = horses_df['Birth Date'].apply(parse_birth_date)
        horses_df['Start'] = horses_df['Start'].apply(parse_start_end)
        horses_df['End'] = horses_df['End'].apply(parse_start_end)
        dams_df['Start'] = dams_df['Start'].apply(parse_start_end)
        dams_df['End'] = dams_df['End'].apply(parse_start_end)
        auctioned_horses_df['Auction Date'] = auctioned_horses_df['Auction Date'].apply(parse_start_end)
        auctioned_horses_df['Birth Date'] = auctioned_horses_df['Birth Date'].apply(parse_birth_date)

        # Format all as dd/mm/yy strings
        horses_df['Birth Date'] = horses_df['Birth Date'].dt.strftime('%d/%m/%y')
        horses_df['Start'] = horses_df['Start'].dt.strftime('%d/%m/%y')
        horses_df['End'] = horses_df['End'].dt.strftime('%d/%m/%y')
        dams_df['Start'] = dams_df['Start'].dt.strftime('%d/%m/%y')
        dams_df['End'] = dams_df['End'].dt.strftime('%d/%m/%y')    
        auctioned_horses_df['Auction Date'] = auctioned_horses_df['Auction Date'].dt.strftime('%d/%m/%y')
        auctioned_horses_df['Birth Date'] = auctioned_horses_df['Birth Date'].dt.strftime('%d/%m/%y')

        # Calculate max values for gradient columns
        gradient_columns = ['PR', 'PS', 'PRS', 'PB', 'PBRS','Inbreeding Coef.']

        horses_max_values = {col: float(horses_df[col].str.rstrip('%').astype(float).max()) 
                           for col in gradient_columns if col in horses_df.columns}
        
        auctioned_horses_max_values = {}
        for col in gradient_columns:
            if col in auctioned_horses_df.columns:
                try:
                    # Remove % and convert to numeric, ignoring errors
                    numeric_values = pd.to_numeric(auctioned_horses_df[col].str.rstrip('%'), errors='coerce')
                    if not numeric_values.empty and not numeric_values.isna().all():
                        max_val = numeric_values.max()
                        if pd.notnull(max_val):
                            auctioned_horses_max_values[col] = float(max_val)
                except Exception as e:
                    print(f"Error processing column {col}: {str(e)}")
                    continue
                

        # Add error handling for dams max values calculation
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
        
        # Initialize empty filter dictionaries
        horses_filters = {col: '' for col in HORSES_FILTER_COLUMNS}
        dams_filters = {col: '' for col in DAMS_FILTER_COLUMNS}
        auctions_filters = {col: '' for col in AUCTIONS_FILTER_COLUMNS}
        auctioned_horses_filters = {col: '' for col in AUCTIONED_HORSES_FILTER_COLUMNS}

        # Update with any values from the request
        for col in HORSES_FILTER_COLUMNS:
            if request.args.get(f'horses_{col}'):
                horses_filters[col] = request.args.get(f'horses_{col}')

        for col in DAMS_FILTER_COLUMNS:
            if request.args.get(f'dams_{col}'):
                dams_filters[col] = request.args.get(f'dams_{col}')

        for col in AUCTIONS_FILTER_COLUMNS:
            if request.args.get(f'auctions_{col}'):
                auctions_filters[col] = request.args.get(f'auctions_{col}')

        for col in AUCTIONED_HORSES_FILTER_COLUMNS:
            if request.args.get(f'auctioned_horses_{col}'):
                auctioned_horses_filters[col] = request.args.get(f'auctioned_horses_{col}')
        
        # Apply filters
        horses_df = filter_dataframe(horses_df, horses_filters)
        dams_df = filter_dataframe(dams_df, dams_filters)
        past_auction_summary = filter_dataframe(past_auction_summary, auctions_filters)
        auctioned_horses_df = filter_dataframe(auctioned_horses_df, auctioned_horses_filters)
        
        #Replace sex int values with strings
        horses_df['Sex'] = horses_df['Sex'].map({1: 'F', 2: 'M'})

        # # Modify how horses_df is converted to HTML
        # horses_df['Name'] = horses_df.apply(
        #     lambda x: f'<a href="{url_for("horse_profile", studbook_id=str(x["Studbook ID"]).strip())}">{x["Name"]}</a>', 
        #     axis=1
        # )


        column_groups_horses = [
                        ("Basic Information", 9, "group-basic"),
                        ("Family Overview", 15, "group-family"),
                        ("Decomposing PS Factors", 7, "group-ps"),
                        ("Factors PR", 2, "group-pr"),
                        ("Auction Info", 5, "group-auction")
                    ]
        
        column_groups_horses_h2 = [
                        ("", 9, "group-basic"),
                        ("Sire", 2, "group-family-sire"),
                        ("Dam", 13, "group-family-dam"),
                        ("", 7, ""),
                        ("", 2, ""),
                        ("", 5, "group-auction")
                    ]
        
        column_groups_dams = [
                        ("Basic Information", 9, "group-basic"),
                        ("Dams Characteristics", 11, "group-family-dams"),
                        ("Inbreeding",1,"group-inbreeding"),
                        ("Decomposing PS Factors", 4, "group-ps-dam"),
                        ("Factors PB/PR-Dam's Birth Success", 4, "group-pb"),
                        ("Factors PS-Dam's Racing Career", 7, "group-racing"),
                        ("Auction Info", 4, "group-auction")
                    ]
        column_groups_dams_h2 = [
                        ("", 39, "group-basic"),
                    ]

        column_groups_auctioned_horses = [

                        ("Basic Information", 9, "group-basic"),
                        ("Auction Info", 7, "group-past-auction")
        ]
        column_groups_auctioned_horses_h2 = [

                        ("", 16, "group-basic")
        ]

        column_groups_past_auction_summary = [ ("", 5, "group-basic")]
        column_groups_past_auction_summary_h2 = [("", 5, "group-basic")]

        horses_data = horses_df.to_dict(orient="records")
        horses_columns = horses_df_order

        dams_data = dams_df.to_dict(orient="records")
        dams_columns = dams_df_order

        auctioned_horses_data = auctioned_horses_df.to_dict(orient="records")
        auctioned_horses_columns = past_auction_order

        auction_summary_data = past_auction_summary.to_dict(orient="records")
        auction_summary_columns = past_auction_summary_order



        initial_tab = request.args.get('tab', 'horses')
        
        return render_template('index.html', 
                            initial_tab=initial_tab,
                             column_groups=column_groups_horses,
                             column_groups_horses_h2=column_groups_horses_h2,
                             horses_data=horses_data,
                             horses_columns=horses_columns,

                             dams_data=dams_data,
                             dams_columns=dams_columns,
                             column_groups_dams=column_groups_dams,

                             auction_summary_data=auction_summary_data,
                             auction_summary_columns=auction_summary_columns,
                            column_groups_past_auction_summary=column_groups_past_auction_summary,
                            column_groups_past_auction_summary_h2=column_groups_past_auction_summary_h2,

                             horses_filters=horses_filters,
                             dams_filters=dams_filters,
                             auctions_filters=auctions_filters,
                             auctioned_horses_filters=auctioned_horses_filters,

                             auctioned_horses_data=auctioned_horses_data,
                             auctioned_horses_columns=auctioned_horses_columns,
                             column_groups_auctioned_horses=column_groups_auctioned_horses,
                             column_groups_auctioned_horses_h2=column_groups_auctioned_horses_h2,

                             auctioned_horses_max_values=auctioned_horses_max_values,
                             horses_max_values=horses_max_values,
                             dams_max_values=dams_max_values,
                             )
    
    
    except Exception as e:
        # When there's an error, we still need to pass empty filters
        return render_template('index.html', 
                             error=str(e),
                             horses_filters={col: '' for col in HORSES_FILTER_COLUMNS},
                             dams_filters={col: '' for col in DAMS_FILTER_COLUMNS},
                             auctions_filters={col: '' for col in AUCTIONS_FILTER_COLUMNS},
                             auctioned_horses_filters={col: '' for col in AUCTIONED_HORSES_FILTER_COLUMNS})


if __name__ == '__main__':
    app.run(debug=True) 