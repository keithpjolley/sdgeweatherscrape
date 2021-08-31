
    # %matplotlib
    # con =  sqlite3.connect('observations.db')
    # df = pd.read_sql_query("SELECT * from observations", con)
    # con.close()

    # df.Temp_F = df.Temp_F.astype(int)
    # df.Valid = pd.to_datetime(df.Valid)

    # sns.scatterplot(data=df, x='Valid', y='Temp_F', hue='station')
    # sns.lineplot(data=df, x='Valid', y='Temp_F', hue='station')

library(tidyverse)
library(DBI)
library(RSQLite)

con <- dbConnect(SQLite(), "observations.db")
df <- dbReadTable(con, 'observations') %>%
    as_tibble() %>%
    mutate_at((c("Winds_MPH", "Gusts_MPH", "Temp_F", "Humidity_PCT")), as.integer) %>%
    mutate(
        Valid = ymd_hms(Valid),
        time = hms::as_hms(Valid),
        date = as_date(Valid)
    )
dbDisconnect(con)

ggplot(df, aes(Valid, Temp_F, colour=station)) + geom_smooth(formula='y~x', method='loess', span=0.1, se=F)
ggplot(df, aes(time, Temp_F, shape=factor(date), colour=station)) + geom_smooth(formula='y~x', method='loess', span=0.1, se=F)
