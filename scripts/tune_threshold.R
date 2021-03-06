library(dplyr)
library(ggplot2)
library(tidyr)
library(readr)
library(RColorBrewer)


args = commandArgs(TRUE)

load_data <- function(directory){
  wd = getwd()
  setwd(directory)
  data <- readr::read_csv("tuning.csv")
  return(data)
}

setwd('/home/thomas/work/GUIdance')

data <- load_data('/home/thomas/work/GUIdance')

p = data %>%
  ggplot(aes(x=threshold, y=val, color=var)) +
  geom_line() +
  #geom_smooth(method="lm", se=F) +
  #scale_y_log10() +
  labs(x="Confidence Threshold",
       y="",
       title=paste("")) +
  #scale_x_discrete() +
  #scale_y_log10() +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))+
  scale_fill_brewer(palette="Set1") + 
  scale_color_brewer(palette="Dark2")

spread_data = data %>% spread(var, val)

correlation = spread_data %>%
  ggplot(aes(y=true_positive_rate, x=false_positive_rate)) +
  geom_point() +
  geom_line()
  #geom_smooth(method="lm", se=F) +
  #scale_y_log10() +
  labs(x="False Positive Rate",
       y="True Positive Rate",
       title="Precision against Recall")+
  #scale_x_discrete() +
  #scale_y_log10() +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))+
  scale_fill_brewer(palette="Set1") + 
  scale_color_brewer(palette="Dark2")

print(p)
