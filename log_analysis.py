#!/usr//bin/env python3
import psycopg2


def main():
    la = LogAnalysis()
    la.top_articles()
    la.top_authors()
    la.days_over_one_percent_errors()


class LogAnalysis:
    """
    Class to open up a connection to the news database and
    generate various reports
    """

    def __init__(self, connection_string="dbname=news"):
        self.db = psycopg2.connect(connection_string)

    def top_articles(self):
        c = self.db.cursor()
        c.execute("""
            select
                articles.title,
                count(log.path)
            from
                log,
                articles
            where
                replace(log.path, '/article/', '') = articles.slug
                and status = '200 OK'
                and path like '%article%'
            group by articles.title
            order by 2 desc
            limit 3
        """)

        print("Three most popular articles of all time:")
        for rows in c.fetchall():
            print("\t{} - {} views".format(rows[0], rows[1]))
        print()
        c.close()

    def top_authors(self):
        c = self.db.cursor()
        c.execute("""
            select
                authors.name,
                count(authors.name)
            from
                log,
                articles,
                authors
            where
                replace(log.path, '/article/', '') = articles.slug
                and authors.id = articles.author
                and status = '200 OK'
                and path like '%article%'
            group by authors.name
            order by 2 desc
        """)

        print("Most popular article authors of all time:")
        for row in c.fetchall():
            print("\t{} - {} views".format(row[0], row[1]))
        print()
        c.close()

    def days_over_one_percent_errors(self):
        c = self.db.cursor()
        c.execute("""
            select
                total.date,
                (
                    100 * (error.errorCount::float / total.totalCount::float)
                ) as "errorPercent",
                total.totalCount,
                error.errorCount
            from
            (
                select
                    count(error.status) as errorCount,
                    error.time::date as "date"
                from log error
                where
                    error.status = '404 NOT FOUND'
                group by error.time::date
            ) as error,
            (
                select
                    count(total.status) as totalCount,
                    total.time::date as "date"
                from log total
                group by total.time::date
            ) as total
            where error.date = total.date
            and (100 * (error.errorCount::float / total.totalCount::float)) > 1
        """)
        rows = c.fetchall()
        print("Days where more than 1% of requests lead to errors:")
        for row in rows:
            print("\t{:%B %d, %Y} - {:.3}%".format(row[0], row[1]))
        print()

    def __del__(self):
        self.db.close()


if __name__ == "__main__":
    main()
