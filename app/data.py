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

	df = pd.read_csv(DATA_PATH)

	html_table = df.to_html(classes='dataframe', index=False)
	page = f"<html><head>{TABLE_CSS}<title>now.us - data</title></head><body>\n<h1>now.us.csv (ServiceNow) — dataset preview</h1>\n{html_table}\n</body></html>"
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

