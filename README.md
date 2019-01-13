# log_analysis

This script will output the answer to three questions about the news database.  These question are:

* What are the most popular three articles of all time?
* Who are the most popular article authors of all time?
* On which days did more than 1% of requests lead to errors?


## Requirements

* Python 3
* pyscopg2 module

## Usage

```
pip3 install psycopg2
./log_analysis.py
```

Functionality is provided as a python class so, if desired, it can also run as
a module imported somewhere else.  For example:

```
from log_analysis import LogAnalysis
la = new LogAnalysis("dbname=news")
la.top_articles()
la.top_authors()
la.la.days_over_one_percent_errors()
```

## Design

### What are the most popular three articles of all time?

The query behind this answer joins the log and articles table in order to get 
the answer. The path of the url accessed is normalized to only contain the 
slug (removing '/article/') and then joined with the slug in the articles 
table to get the title. The count is generated using a group by clause on
the title.  The log table is then filtered by the 200 status to weed out any
non-existent articles (these would also be filtered out by the inner join).

### Who are the most popular article authors of all time?

The query behind this answer joins the log, articles and authors table in
order to determine which authors are the most popular.  The log.path column
is normalized, as above, to remove '/article/' and joined with the slug in
the articles table.  The authors id is then joined with the author id on
the articles table in order to get the authors name.  We then filter out
only successful GETs (200 status) and group by the authors name to get 
the total number of times on of their articles have been successfully  
accessed.  This is then sorted by the count in descending order.

### On which days did more than 1% of requests lead to errors?

The query behind this answer needs to use several subqueries as derived 
tables in order to get the answer. The first derived table is the log table
filtered for 404 errors and and grouped by the day.  This derived table
selects the count and the date.  The second derived table is the same as
the first without the filter on errors to get the total number of requests.
These two derived tables are then joined so that we can get the percentage of
failed requests per day and filter out any less than one percent.
