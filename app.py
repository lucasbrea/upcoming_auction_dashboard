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
print(sys.executable)

print("CWD:", os.getcwd())
#Path to install packages in venv
# /Users/lucasbrea/Move37/dashboard_remates/.venv/bin/python -m pip install package


app = Flask(__name__)

CSV_PATH = os.path.join("Data/dashboard_data.csv")
DAMS_CSV_PATH = os.path.join("Data/merge_auction_dams.csv")
PAST_AUCTION_PATH = os.path.join("Data/past_auction_summary.csv")
AUCTIONED_HORSES_PATH = os.path.join("Data/Past Auctions - Horses.csv")




HORSES_RENAMED_COLUMNS = {
    'name': 'Name',
    # 'studbook_id': 'Studbook ID',
    'padrillo': 'Sire',
    'M': 'Dam',
    'birth_eday':'Birth Date',
    'sex': 'Sex',
    'haras': 'Haras',
    'link' : 'Href',
    'start': 'Start',
    'end_date': 'End',
    'Sire_Stk_Wnrs_Rnrs': 'Sire Stk Wnrs / Rnrs',
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
    'M_age_at_birth': 'Dam\'s Age',
    'M_season': 'Dam\'s Season',

}
DAMS_RENAMED_COLUMNS = {
    'name': 'Name',
    'studbook_id': 'Studbook ID',
    'padrillo': 'Sire',
    'M': 'Dam',
    'birth_eday':'Birth Date',
    'sex': 'Sex',
    'haras': 'Haras',
    'remate': 'Remate',
    'source': 'Source',
    'inbreedingCoefficient': 'Avg. Inbreeding Coefficient(if IC<0.05)',
    'mother': 'Dams Age and Racing Career',
    'Momsiblings': 'Dams Offsprings',
    'uncles': 'Dams Siblings',
    'dams_parents_career':'Dams Parents Career',
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
                            'criador', 
                            'year', 
                            'valueUSDB'
                            ]

AUCTIONED_HORSES_FILTER_COLUMNS = [
                                    'name', 
                                    'padrillo', 
                                    'yegua',
                                    'criador',
                                    'valueUSDB',
                                    'year'
                                    ]


def load_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found at {file_path}")
    
    df = pd.read_csv(file_path)
    


    # Re formateo de valores, a porcentaje o rodondeado

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
                          
                          ]
    for col in percentage_columns:
        if col in df.columns:
            # Multiply by 100
            df[col] = df[col] * 100

            # Use 1 decimal only for PRS, else round to int
            if col == 'PRS':
                df[col] = df[col].round(1).apply(lambda x: f"{x}%" if pd.notnull(x) else "-")
            else:
                df[col] = df[col].round(0).apply(lambda x: f"{int(x)}%" if pd.notnull(x) else "-")
    rounded_columns =[
                       'dams_parents_career',
                       'Dam_Mean_T3_BSN',
                        'Best_Foal_Bsn',
                        'M_age_at_birth' ]
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
@app.route("/export-pdf")
def export_pdf():
    try:
        # Get the current tab and filters from query parameters
        current_tab = request.args.get('current_tab', 'horses')
        filters = {k: v for k, v in request.args.items() if k != 'current_tab'}

        # Load the appropriate dataset based on the current tab
        if current_tab == 'horses':
            df = load_data(CSV_PATH)
            df.rename(columns=HORSES_RENAMED_COLUMNS, inplace=True)
            max_values = {col: float(df[col].str.rstrip('%').astype(float).max()) 
                         for col in ['PR', 'PS', 'PRS', 'PB', 'PBRS'] if col in df.columns}
        elif current_tab == 'dams':
            df = load_data(DAMS_CSV_PATH)
            df.rename(columns=DAMS_RENAMED_COLUMNS, inplace=True)
            df = df.iloc[:, [0,12,13,1,2,3,4,15,5,6,7,8,9,10,11,14,16]]
            max_values = {col: float(df[col].str.rstrip('%').astype(float).max()) 
                         for col in ['PR', 'PS', 'PRS', 'PB', 'PBRS'] if col in df.columns}
        elif current_tab == 'auctions':
            df = load_data(PAST_AUCTION_PATH)
            max_values = {}
        elif current_tab == 'auctioned-horses':
            df = load_data(AUCTIONED_HORSES_PATH)
            max_values = {}
        else:
            return "Invalid tab selected", 400

        # Apply filters
        df = filter_dataframe(df, filters)

        # Convert DataFrame to HTML with gradient highlighting
        html = render_template("pdf_template.html", 
                             table=df.to_html(index=False, classes='table table-striped'),
                             title=current_tab.replace('-', ' ').title(),
                             max_values=max_values,
                             gradient_columns=['PR', 'PS', 'PRS', 'PB', 'PBRS'])

        # Generate PDF
        pdf_file = BytesIO()
        HTML(string=html).write_pdf(pdf_file)
        pdf_file.seek(0)

        # Return PDF file
        return send_file(
            pdf_file,
            download_name=f"{current_tab}_filtered.pdf",
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        return str(e), 500

@app.route('/')
def index():
    try:
        # Load both datasets
        horses_df = load_data(CSV_PATH)
        dams_df = load_data(DAMS_CSV_PATH)
        past_auction_df = load_data(PAST_AUCTION_PATH)
        auctioned_horses_df = load_data(AUCTIONED_HORSES_PATH)

        dams_df.rename(columns=DAMS_RENAMED_COLUMNS, inplace=True)
        dams_df = dams_df.iloc[:, [0,12,13,1,2,3,4,15,5,6,7,8,9,10,11,14,16]]

        horses_df.rename(columns=HORSES_RENAMED_COLUMNS, inplace=True)
        horses_df_order = ['Name',
                       'Sire',
                        'Dam',
                        'Sex',
                        'Birth Date',
                        'Haras',
                        'PRS',
                        'PR',
                        'PS',
                        'Sire Stk Wnrs / Rnrs',
                        'Dam Stk Wnrs / RA Offs',
                        'Dams RA Offs',
                        'Dam Top 3 BSN\'s',
                        'Dam\'s Foals Top 3 BSN',
                        'Dam Raced STK?',
                        'Dam Total Races',
                        'Dam\'s Foal Raced Stk?',
                        'Dam\'s Foal Placed Stk?',
                        'Dam\'s Siblings Total G1/G2',
                        'Dam\'s Siblings G1G2/Races',
                        'Own Chars',
                        'Father',
                        'Father\'s Offs',
                        'Dam\'s Age and Racing Career',
                        'Dam\'s Offs',
                        'Dam\'s Sibs',
                        'Dam\'s Parents Career',
                        'Inbreeding',
                        'Dam\'s Age',
                        'Dam\'s Season',
                        'Start',
                        'End',
                        'lote',
                        'Href'
                        # 'Studbook ID'
                             ]
        

        horses_df = horses_df[horses_df_order]
        
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

        # Format all as dd/mm/yy strings
        horses_df['Birth Date'] = horses_df['Birth Date'].dt.strftime('%d/%m/%y')
        horses_df['Start'] = horses_df['Start'].dt.strftime('%d/%m/%y')
        horses_df['End'] = horses_df['End'].dt.strftime('%d/%m/%y')

        # Calculate max values for gradient columns
        gradient_columns = ['PR', 'PS', 'PRS', 'PB', 'PBRS']
        horses_max_values = {col: float(horses_df[col].str.rstrip('%').astype(float).max()) 
                           for col in gradient_columns if col in horses_df.columns}
        dams_max_values = {col: float(dams_df[col].str.rstrip('%').astype(float).max()) 
                          for col in gradient_columns if col in dams_df.columns}
        
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
        past_auction_df = filter_dataframe(past_auction_df, auctions_filters)
        auctioned_horses_df = filter_dataframe(auctioned_horses_df, auctioned_horses_filters)
        
        #Replace sex int values with strings
        horses_df['Sex'] = horses_df['Sex'].map({1: 'F', 2: 'M'})

        # # Modify how horses_df is converted to HTML
        # horses_df['Name'] = horses_df.apply(
        #     lambda x: f'<a href="{url_for("horse_profile", studbook_id=str(x["Studbook ID"]).strip())}">{x["Name"]}</a>', 
        #     axis=1
        # )

        # horses_df.drop(columns=['Studbook ID'], inplace=True)

        column_groups = [
                        ("Basic Information", 9, "group-basic"),
                        ("Family Overview", 11, "group-family"),
                        ("Decomposing PS Factors", 7, "group-ps"),
                        ("Factors PR", 3, "group-pr"),
                        ("Auction Info", 5, "group-auction")
                    ]

        horses_data = horses_df.to_dict(orient="records")
        horses_columns = horses_df_order

        dams_table = dams_df.to_html(classes='table table-striped', index=False)
        past_auction_table = past_auction_df.to_html(classes='table table-striped', index=False)
        auctioned_horses_table = auctioned_horses_df.to_html(classes='table table-striped', index=False)

        fig = px.line(
            past_auction_df,
            x="year",
            y="valueUSDB",
            color="criador",
            markers=True,
            title="Precio Promedio por Criador",
            labels={
                "year": "Año",
                "valueUSDB": "Precio Promedio (USD)",
                "criador": "Criador"
            }
        )

        fig.update_layout(
            yaxis_tickformat=',',
            legend_title_text="Criador",
            margin=dict(t=50, b=40, l=40, r=40),
            plot_bgcolor="#fff",
            hovermode="x unified"
        )
        plot_html = to_html(fig, full_html=False, include_plotlyjs='cdn')

        initial_tab = request.args.get('tab', 'horses')
        
        return render_template('index.html', 
                            initial_tab=initial_tab,
                             column_groups=column_groups,
                             horses_data=horses_data,
                             horses_columns=horses_columns,
                             dams_table=dams_table,
                             past_auction_table=past_auction_table,
                             auctioned_horses_table=auctioned_horses_table,
                             horses_filters=horses_filters,
                             dams_filters=dams_filters,
                             auctions_filters=auctions_filters,
                             auctioned_horses_filters=auctioned_horses_filters,
                             horses_max_values=horses_max_values,
                             dams_max_values=dams_max_values,
                             plot_url=plot_html)
    except Exception as e:
        # When there's an error, we still need to pass empty filters
        return render_template('index.html', 
                             error=str(e),
                             horses_filters={col: '' for col in HORSES_FILTER_COLUMNS},
                             dams_filters={col: '' for col in DAMS_FILTER_COLUMNS},
                             auctions_filters={col: '' for col in AUCTIONS_FILTER_COLUMNS},
                             auctioned_horses_filters={col: '' for col in AUCTIONED_HORSES_FILTER_COLUMNS})



@app.route('/horse/<studbook_id>')
def horse_profile(studbook_id):
    try:
        # Load the horses dataset
        df = load_data(CSV_PATH)
        df.rename(columns=HORSES_RENAMED_COLUMNS, inplace=True)
        
        # Convert studbook_id column to string for comparison
        df['Studbook ID'] = df['Studbook ID'].astype(str).str.strip()
        studbook_id = str(studbook_id).strip()
        
        # Find the horse with matching studbook_id
        matching_horses = df[df['Studbook ID'] == studbook_id]
        
        if matching_horses.empty:
            return f"No horse found with Studbook ID: {studbook_id}", 404
            
        horse = matching_horses.iloc[0]
        display_columns = list(HORSES_RENAMED_COLUMNS.values())
        print("Display columns:", display_columns)
        
        return render_template('horse_profile.html', 
                             horse=horse,
                             columns=display_columns,
                             title=f"Profile - {horse['Name']}")
    
    except Exception as e:
        print(f"Error in horse_profile: {str(e)}")
        print(f"Searching for studbook_id: {studbook_id}")
        print(f"Available IDs: {df['Studbook ID'].unique()}")
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True) 