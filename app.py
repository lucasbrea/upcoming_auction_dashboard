from flask import Flask, render_template, request, send_file
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
print(sys.executable)

#Path to install packages in venv
# /Users/lucasbrea/Move37/dashboard_remates/.venv/bin/python -m pip install package


app = Flask(__name__)

CSV_PATH = os.path.join("Data/dashboard_data.csv")
DAMS_CSV_PATH = os.path.join("Data/merge_auction_dams.csv")
PAST_AUCTION_PATH = os.path.join("Data/past_auction_summary.csv")
AUCTIONED_HORSES_PATH = os.path.join("Data/Past Auctions - Horses.csv")


HORSES_RENAMED_COLUMNS = {
    'name': 'Name',
    'studbook_id': 'Studbook ID',
    'padrillo': 'Sire',
    'M': 'Dam',
    'birth_eday':'Birth Date',
    'sex': 'Sex',
    'haras': 'Haras',
    'remate': 'Remate',
    'source': 'Source',
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
HORSES_FILTER_COLUMNS = ['Name', 'Studbook_id', 'Sire', 'Dam', 'Sex', 'Haras', 'Remate', 'Source']
DAMS_FILTER_COLUMNS = ['Name', 'Sire', 'Dam', 'Haras', 'Link']
AUCTIONS_FILTER_COLUMNS = ['criador', 'year', 'valueUSDB']
AUCTIONED_HORSES_FILTER_COLUMNS = ['name', 'padrillo', 'yegua','criador','valueUSDB','year']


def load_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found at {file_path}")
    
    df = pd.read_csv(file_path)
    
    # PR, PS , PB, PRS, PBRS, Inbreeding Coefficient a porcentaje
    percentage_columns = ['PS', 'PR', 'PRS','PB','PBRS', 'inbreedingCoefficient']
    for col in percentage_columns:
        if col in df.columns and col == 'PRS':
            df[col] = (df[col]*100).round(1).astype(str)+"%"
        elif col in df.columns:
            df[col] = (df[col]*100).round(0).astype(int).astype(str)+"%"

    rounded_columns =[ 'mother', 'Momsiblings','uncles','dams_parents_career' ]
    for col in rounded_columns:
        if col in df.columns:
            df[col] = df[col].round(2).astype(str)
    return df

def filter_dataframe(df, filters):
    if not filters:
        return df

    for column, value in filters.items():
        if value and column in df.columns:
            df = df[df[column].astype(str).str.contains(value, case=False, na=False, regex=False)]
    return df
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
            df = df.iloc[:, [0,5,2,3,4,14,15,10,9,6,7,8,11,12,1,13,16]]
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

        # Apply gradient highlighting to the DataFrame
        gradient_columns = ['PR', 'PS', 'PRS', 'PB', 'PBRS']
        for col in gradient_columns:
            if col in df.columns:
                def apply_gradient(value):
                    try:
                        val = float(str(value).rstrip('%'))
                        normalized = val / max_values[col]
                        normalized = max(0, min(1, normalized))
                        
                        if normalized < 0.2:
                            opacity = 0.3 + (normalized * 0.7)
                            return f'background-color: rgba(255, {int(normalized * 255)}, 0, {opacity})'
                        else:
                            opacity = 0.3 + ((normalized - 0.2) * 0.7)
                            return f'background-color: rgba(0, 255, 0, {opacity})'
                    except:
                        return ''
                
                df[col] = df[col].apply(lambda x: f'<td style="{apply_gradient(x)}">{x}</td>')

        # Convert DataFrame to HTML with gradient highlighting
        html = render_template("pdf_template.html", 
                             table=df.to_html(index=False, classes='table table-striped', escape=False),
                             title=current_tab.replace('-', ' ').title(),
                             max_values=max_values,
                             gradient_columns=gradient_columns)

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
        # Get the requested tab from query parameters
        requested_tab = request.args.get('tab', 'horses')
        
        # Load both datasets
        horses_df = load_data(CSV_PATH)
        dams_df = load_data(DAMS_CSV_PATH)
        past_auction_df = load_data(PAST_AUCTION_PATH)
        auctioned_horses_df = load_data(AUCTIONED_HORSES_PATH)

        dams_df.rename(columns=DAMS_RENAMED_COLUMNS, inplace=True)
        dams_df.drop(['highInbreedingPadrillos'], axis=1, inplace=True)
        dams_df = dams_df.iloc[:, [0,11,12,13,1,2,3,4,14,5,6,7,8,9,10,15,16]]

        horses_df.rename(columns=HORSES_RENAMED_COLUMNS, inplace=True)
        horses_df = horses_df.iloc[:, [0,5,2,3,4,14,15,10,9,6,7,8,11,12,1,13,16]]

        # Calculate max values for gradient columns
        gradient_columns = ['PR', 'PS', 'PRS', 'PB', 'PBRS']
        horses_max_values = {col: float(horses_df[col].str.rstrip('%').astype(float).max()) 
                           for col in gradient_columns if col in horses_df.columns}
        dams_max_values = {col: float(dams_df[col].str.rstrip('%').astype(float).max()) 
                          for col in gradient_columns if col in dams_df.columns}
        
        # Get filter values from request only for specified columns
        horses_filters = {col: request.args.get(f'horses_{col}') for col in HORSES_FILTER_COLUMNS}
        dams_filters = {col: request.args.get(f'dams_{col}') for col in DAMS_FILTER_COLUMNS}
        auctions_filters = {col: request.args.get(f'auctions_{col}') for col in AUCTIONS_FILTER_COLUMNS}
        auctioned_horses_filters = {col: request.args.get(f'auctioned_horses_{col}') for col in AUCTIONED_HORSES_FILTER_COLUMNS}
        
        # Apply filters
        horses_df = filter_dataframe(horses_df, horses_filters)
        dams_df = filter_dataframe(dams_df, dams_filters)
        past_auction_df = filter_dataframe(past_auction_df, auctions_filters)
        auctioned_horses_df = filter_dataframe(auctioned_horses_df, auctioned_horses_filters)
        
        # Convert DataFrames to HTML tables
        horses_table = horses_df.to_html(classes='table table-striped', index=False)
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
        
        return render_template('index.html', 
                             horses_table=horses_table,
                             dams_table=dams_table,
                             past_auction_table=past_auction_table,
                             auctioned_horses_table=auctioned_horses_table,
                             horses_filters=horses_filters,
                             dams_filters=dams_filters,
                             auctions_filters=auctions_filters,
                             auctioned_horses_filters=auctioned_horses_filters,
                             horses_max_values=horses_max_values,
                             dams_max_values=dams_max_values,
                             plot_url=plot_html,
                             initial_tab=requested_tab)
    except Exception as e:
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True) 