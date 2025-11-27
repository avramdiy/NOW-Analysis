from flask import Flask, render_template_string, send_file, abort
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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


def _load_and_split():
	"""Helper: load CSV, drop OpenInt, convert Date, and return the three periods."""
	df = pd.read_csv(DATA_PATH)
	if 'OpenInt' in df.columns:
		df = df.drop(columns=['OpenInt'])
	df['Date'] = pd.to_datetime(df['Date'])
	period_1 = df[(df['Date'] >= '2012-06-29') & (df['Date'] <= '2013-12-31')]
	period_2 = df[(df['Date'] >= '2014-01-01') & (df['Date'] <= '2015-12-31')]
	period_3 = df[(df['Date'] >= '2016-01-01') & (df['Date'] <= '2017-11-10')]
	return period_1, period_2, period_3


def _plot_bollinger(df, window=20, n_std=2, title=None):
	"""Create a Matplotlib figure plotting Close price with Bollinger Bands and return base64 PNG string."""
	if df.empty:
		fig, ax = plt.subplots(figsize=(8, 3))
		ax.text(0.5, 0.5, 'No data', ha='center', va='center')
		ax.axis('off')
	else:
		df_sorted = df.sort_values('Date')
		close = df_sorted['Close']
		rolling_mean = close.rolling(window=window, min_periods=1).mean()
		rolling_std = close.rolling(window=window, min_periods=1).std().fillna(0)
		upper = rolling_mean + (rolling_std * n_std)
		lower = rolling_mean - (rolling_std * n_std)

		fig, ax = plt.subplots(figsize=(10, 4))
		ax.plot(df_sorted['Date'], close, label='Close', color='C0')
		ax.plot(df_sorted['Date'], rolling_mean, label=f'{window}-day MA', color='C1')
		ax.fill_between(df_sorted['Date'], lower, upper, color='C1', alpha=0.2, label='Bollinger Bands')
		ax.set_xlabel('Date')
		ax.set_ylabel('Price')
		ax.legend(loc='best')
		if title:
			ax.set_title(title)

	buf = io.BytesIO()
	fig.tight_layout()
	fig.savefig(buf, format='png')
	plt.close(fig)
	buf.seek(0)
	img_b64 = base64.b64encode(buf.read()).decode('ascii')
	return img_b64


@app.route('/bollinger')
def bollinger():
	"""Render Bollinger band plots for each of the three data periods embedded in an HTML page."""
	if not os.path.exists(DATA_PATH):
		abort(404, description=f"Dataset not found: {DATA_PATH}")

	p1, p2, p3 = _load_and_split()

	img1 = _plot_bollinger(p1, title='Period 1: 2012-06-29 through 2013-12-31')
	img2 = _plot_bollinger(p2, title='Period 2: 2014-01-01 through 2015-12-31')
	img3 = _plot_bollinger(p3, title='Period 3: 2016-01-01 through 2017-11-10')

	html = f"<html><head>{TABLE_CSS}<title>Bollinger Bands</title></head><body>"
	html += "<h1>Bollinger Bands (Close) — 3 periods</h1>"
	html += f"<h2>Period 1</h2><img src=\"data:image/png;base64,{img1}\" alt='period1'/>"
	html += f"<h2>Period 2</h2><img src=\"data:image/png;base64,{img2}\" alt='period2'/>"
	html += f"<h2>Period 3</h2><img src=\"data:image/png;base64,{img3}\" alt='period3'/>"
	html += "</body></html>"
	return render_template_string(html)


@app.route('/yearly-open')
def yearly_open():
	"""Plot yearly average Open price for each of the three periods on a single line chart."""
	if not os.path.exists(DATA_PATH):
		abort(404, description=f"Dataset not found: {DATA_PATH}")

	p1, p2, p3 = _load_and_split()

	def yearly_avg(df):
		if df.empty:
			return pd.Series(dtype=float)
		s = df.set_index('Date')['Open'].resample('Y').mean()
		# normalize index to year numbers for plotting
		s.index = s.index.year
		return s

	s1 = yearly_avg(p1)
	s2 = yearly_avg(p2)
	s3 = yearly_avg(p3)

	# plot them together
	fig, ax = plt.subplots(figsize=(10, 4))
	if not s1.empty:
		ax.plot(s1.index, s1.values, marker='o', label='Period 1 (2012-2013)')
	if not s2.empty:
		ax.plot(s2.index, s2.values, marker='o', label='Period 2 (2014-2015)')
	if not s3.empty:
		ax.plot(s3.index, s3.values, marker='o', label='Period 3 (2016-2017)')

	ax.set_xlabel('Year')
	ax.set_ylabel('Average Open Price')
	ax.set_title('Yearly Average Open Price — Periods 1/2/3')
	ax.grid(True, linestyle='--', alpha=0.5)
	ax.legend(loc='best')

	buf = io.BytesIO()
	fig.tight_layout()
	fig.savefig(buf, format='png')
	plt.close(fig)
	buf.seek(0)
	img_b64 = base64.b64encode(buf.read()).decode('ascii')

	page = f"<html><head>{TABLE_CSS}<title>Yearly Average Open</title></head><body>"
	page += "<h1>Yearly Average Open Price — Combined</h1>"
	page += f"<img src=\"data:image/png;base64,{img_b64}\" alt='yearly-open'/>"
	page += "</body></html>"
	return render_template_string(page)


if __name__ == '__main__':
	# default dev server
	app.run(host='127.0.0.1', port=5000, debug=True)

