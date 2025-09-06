from flask import Flask, render_template, send_file
import pyodbc
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# SQL Server connection
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=Tharushi\\SQLEXPRESS;'  
    'DATABASE=PeopleCounterDB;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

@app.route("/")
def index():
    cursor.execute("SELECT Timestamp, CountIn, CountOut FROM PeopleCount ORDER BY Timestamp")
    rows = cursor.fetchall()

    df = pd.DataFrame([(row.Timestamp, row.CountIn, row.CountOut) for row in rows],
                      columns=['Timestamp', 'CountIn', 'CountOut'])
    
    # Chart data
    chart_labels = df['Timestamp'].dt.strftime("%H:%M:%S").tolist()
    chart_data = {
        'count_in': df['CountIn'].tolist(),
        'count_out': df['CountOut'].tolist()
    }

    # Latest counts
    count_in = df['CountIn'].iloc[-1] if not df.empty else 0
    count_out = df['CountOut'].iloc[-1] if not df.empty else 0

    # Peak hours
    df['Hour'] = df['Timestamp'].dt.hour
    peak_in_hour = df.groupby('Hour')['CountIn'].sum().idxmax() if not df.empty else None
    peak_out_hour = df.groupby('Hour')['CountOut'].sum().idxmax() if not df.empty else None

    # Daily summaries
    df['Date'] = df['Timestamp'].dt.date
    daily_summary = df.groupby('Date')[['CountIn', 'CountOut']].sum().reset_index()

    return render_template(
        'index.html',
        count_in=count_in,
        count_out=count_out,
        chart_labels=chart_labels,
        chart_data=chart_data,
        peak_in_hour=peak_in_hour,
        peak_out_hour=peak_out_hour,
        daily_summary=daily_summary.to_dict(orient='records')
    )

@app.route("/export")
def export_csv():
    cursor.execute("SELECT Timestamp, CountIn, CountOut FROM PeopleCount ORDER BY Timestamp")
    rows = cursor.fetchall()
    df = pd.DataFrame([(row.Timestamp, row.CountIn, row.CountOut) for row in rows],
                      columns=['Timestamp', 'CountIn', 'CountOut'])
    
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="people_count.csv")

if __name__ == "__main__":
    app.run(debug=True)
