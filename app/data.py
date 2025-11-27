from flask import Flask, render_template_string, send_file, abort
import pandas as pd
import os

app = Flask(__name__)

# locate the dataset relative to this file
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'now.us.txt')

TABLE_CSS = '''
<style>
  table.dataframe {border-collapse: collapse; width: 100%;}
  table.dataframe th, table.dataframe td {border: 1px solid #ddd; padding: 8px;}
  table.dataframe tr:nth-child(even){background-color: #f9f9f9;}
  table.dataframe tr:hover {background-color: #f1f1f1;}
  table.dataframe th {padding-top: 12px; padding-bottom: 12px; background-color: #0074D9; color: white; text-align: left;}
</style>
'''

@app.route('/')
def index():
	"""Read now.us.txt and return an HTML table of the dataframe.

	This returns the full CSV rendered as an HTML table using pandas.DataFrame.to_html().
	For very large files in production you may want to paginate or return a summary instead.
	"""
	if not os.path.exists(DATA_PATH):
		abort(404, description=f"Dataset not found: {DATA_PATH}")

	# load CSV and clean
	df = pd.read_csv(DATA_PATH)

	# drop OpenInt if present (requested)
	if 'OpenInt' in df.columns:
		df = df.drop(columns=['OpenInt'])

	# ensure Date is datetime so we can split by ranges
	df['Date'] = pd.to_datetime(df['Date'])

	# The CSV spans 2012-06-29 through 2017-11-10. Split it into 3 meaningful periods:
	#  - period_1: 2012-06-29 through 2013-12-31
	#  - period_2: 2014-01-01 through 2015-12-31
	#  - period_3: 2016-01-01 through 2017-11-10
	period_1 = df[(df['Date'] >= '2012-06-29') & (df['Date'] <= '2013-12-31')]
	period_2 = df[(df['Date'] >= '2014-01-01') & (df['Date'] <= '2015-12-31')]
	period_3 = df[(df['Date'] >= '2016-01-01') & (df['Date'] <= '2017-11-10')]

	# render the three periods separately in the page (keep original behavior otherwise)
	html_p1 = period_1.to_html(classes='dataframe', index=False)
	html_p2 = period_2.to_html(classes='dataframe', index=False)
	html_p3 = period_3.to_html(classes='dataframe', index=False)

	page = f"<html><head>{TABLE_CSS}<title>now.us - data</title></head><body>\n<h1>now.us.csv (ServiceNow) — dataset preview</h1>\n"
	page += f"<h2>Period 1: 2012-06-29 through 2013-12-31 (n={len(period_1)})</h2>\n{html_p1}\n"
	page += f"<h2>Period 2: 2014-01-01 through 2015-12-31 (n={len(period_2)})</h2>\n{html_p2}\n"
	page += f"<h2>Period 3: 2016-01-01 through 2017-11-10 (n={len(period_3)})</h2>\n{html_p3}\n</body></html>"
	return render_template_string(page)

@app.route('/download')
def download():
	"""Offer the original CSV file for download."""
	if os.path.exists(DATA_PATH):
		return send_file(DATA_PATH, as_attachment=True)
	abort(404, description="File not found")


if __name__ == '__main__':
	# default dev server
	app.run(host='127.0.0.1', port=5000, debug=True)

