# TRG Week 51

## $NOW (ServiceNow Inc.)

- Leading enterprise cloud workflow and automation platform (IT service management, operations, HR and customer workflows); subscription-driven, high-margin recurring revenue with strong growth and platform-led expansion — but priced at a premium and sensitive to enterprise IT spending cycles.

- https://www.kaggle.com/borismarjanovic/datasets

### 1st Commit

- Added a minimal Flask API (`app/data.py`) that reads the `now.us.txt` dataset and serves it as an HTML dataframe at `/` (also provides `/download` to fetch the original CSV).

### 2nd Commit

- Split the `now.us.txt` dataset into three time-based dataframes (Periods 1/2/3 spanning 2012->2013, 2014->2015, and 2016->2017 respectively) and dropped the `OpenInt` column; the root Flask page now shows each period as its own HTML table.

### 3rd Commit

- Added a `/bollinger` route which computes and visualizes Bollinger Bands (20-day MA ± 2σ) for each of the three time-split dataframes and returns inline PNG plots for each period.

### 4th Commit

### 5th Commit