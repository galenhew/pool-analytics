import plotly.express as px
import pandas as pd
import numpy as np


def scatter_returns(df, x, y):
    fig = px.scatter(df, x= x, y= y, hover_data=['match_name'],
                     title = 'Match returns over match day ')
    return fig


def line_chart(df, x, y, color= None):
    df = df.copy()
    fig = px.line(df, x = x, y = y, color = color, markers = True)
    fig.update_xaxes(range = [df['datetime'].min(), df['datetime'].max()])
    fig.show()



def win_ratio(df):
    df = df.copy()
    wr = (df['win_ind'].sum()/len(df)).round(2)
    return wr


def bet_ratio(df):
    df = df.copy()
    df['bet_ratio'] = (df['amount']/df['cum_sum']).round(2)
    return df


def box_plot(df):
    fig = px.box(df, y="bet_ratio")
    fig.show()


def confusion_matrix(df):
    pass