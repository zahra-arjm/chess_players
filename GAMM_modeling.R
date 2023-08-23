# installing packages from CRAN:
# install.packages('mgcv')


# install.packages('itsadug')
# install.packages('dplyr')
# itsadug automatically loads mgcv:
library(itsadug)

library(mgcv)
library(dplyr)
# load the dataset; make sure it's in your current directory
df <- read.csv("data_with_cent_loss_long.csv")

# add a column for time
df$time = df$move_no / df$count_moves

# check how many players we have
unique(df$name)
#612 players!

# check the distribution of number of games each player have played in the dataset
class(df$game_id) = "character"
df_count_games <- df %>%
  group_by(name) %>%
  summarise("game_count" = length(unique(game_id)))
summary(df_count_games$game_count)
# the majority of players have only played 1 game!
# we will go on anyways!

# check also the distribution of ELOs among players
# note that a player's ELO may have changed by time; we need to decide how
# to take it into account
# for now, I will treat player with changing ELO as a different person
df_ELO <- df %>%
  group_by(name) %>%
  summarise(unique(ELO))
hist(df_ELO$`unique(ELO)`)

# let's make players into two groups of below and higher than 2000 ELO
df <- df %>%
  mutate(ELO_group = if_else(ELO > 2000, 1, 2))
df$ELO_group = as.factor(df$ELO_group)

# apply the GAMM model
m = bam(CP_loss ~ ELO_group + s(time, by=ELO_group), data=df)
summary(m)

# specify two plot panels:
par(mfrow=c(1,2), cex=1.1)
plot_smooth(m, view='time', cond=list(ELO_group=2)
            , main="top ELO")
plot_smooth(m, view='time', cond=list(ELO_group=1)
            , main="low ELO")