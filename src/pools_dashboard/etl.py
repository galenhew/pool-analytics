import pandas as pd
import numpy as np
import tabula
import re


def fetch(filename):
    # Read pdf into list of DataFrame
    df_list = tabula.read_pdf(filename , pages='all')
    df= pd.concat(df_list)
    return df


def fetch_eg_csv():
    # note that file path starts from pools-dashboard directory
    path = 'data/'
    df_list = tabula.read_pdf(path + "TransactionHistory.pdf" , pages='all')
    df= pd.concat(df_list)
    return df


def fetch_matches():
    path = '../../data/'
    name = 'sportsref_download_'

    from os import listdir
    from os.path import isfile, join

    only_files = [f for f in listdir(path)
                  if isfile(join(path, f)) and name in f]
    print(only_files)
    df1 = pd.read_html(path+only_files[0])

    return df1


def process(df):

    # rename
    # print('hi', df.columns.values)
    df=df.copy().reset_index()
    df_cols = list(df.columns)
    a = [re.sub('\\r|\&|\/|\.', '', x) .strip() for x in df_cols]
    a = ["_".join(x.split()).lower() for x in a]
    df.columns = a

    # datatypes
    df['amount'] = df['amount'].str.split(' ').str[-1]
    df['payout_winnings'] = df['payout_winnings'].str.split(' ').str[-1]

    df['transaction_date_time'] = df['transaction_date_time'].str.split('\\r').str[0] + ' ' + \
                                    df['transaction_date_time'].str.split('\\r').str[1]
    df['draw_eventdate_time'] = df['draw_eventdate_time'].str.split('\\r').str[0] + ' ' + \
                                    df['draw_eventdate_time'].str.split('\\r').str[1]
    df['status_receiptno'] = df['status_receiptno'].str.split('\\r').str[0]
    df['type'] = df['type'].str.split('\\r').str[0]

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['payout_winnings'] = pd.to_numeric(df['payout_winnings'], errors='coerce')
    df['transaction_date_time'] = pd.to_datetime(df['transaction_date_time'], format='%d %b %Y %I:%M %p')
    df['draw_eventdate_time'] = pd.to_datetime(df['draw_eventdate_time'], format='%d %b %Y %I:%M %p')


    def date_filter(df):
        if (df['type'] == 'Withdrawal') or (df['type'] == 'Deposit'):
            return df['transaction_date_time']
        else:
            return df['draw_eventdate_time']

    df['datetime'] = df.apply(date_filter, axis=1)

    df = df.drop(['channel'], axis=1)

    return df


def football_table(df):
    df= df.copy()
    df= df.loc[(df['type']=='Football')| (df['type']=='Deposit') | (df['type']=='Withdrawal')]
    df= df.sort_values(by= ['datetime'])
    # df['returns']= df[['payout_winnings','amount']].max(axis=1)
    # df['returns']= np.where(df['payout_winnings']== 0,  df['returns']*-1, df['returns'])
    # df['returns'] = np.where(df['type'] == 'Withdrawal', df['returns'] * -1, df['returns'])

    def returns_filter(df):
        if (df['type'] == 'Football') and (df['status_receiptno'] == 'Settled'):
            return df['payout_winnings'] - df['amount']
        elif df['type'] == 'Withdrawal':
            return -df['amount']
        elif (df['type'] == 'Deposit'):
            return df['amount']

    df['returns'] = df.apply(returns_filter, axis=1)
    df['cum_sum']= df['returns'].cumsum()
    df['perc_returns'] = df['returns']/ df['cum_sum'].shift(periods = 1)

    # selection_details split into columns
    df['selection_details'] = df['selection_details']\
                                .apply(lambda x: re.sub('\\r|\&|\@|\([a-zA-Z]+\)', ' ', x).strip())
    df['live'] = np.where(df['selection_details'].str.contains('live'), 1, 0)

    df['league'] = df['selection_details'].str.split('-').str[0]
    df['match'] = df['selection_details'].str.split('-').str[1]
    df['home'] = df['match'].str.split('vs').str[0]
    df['away'] = df['match'].str.split('vs').str[1]
    df['bet_side'] = df['selection_details'].str.split('-').str[2]
    df[['league', 'match', 'bet_side', 'home', 'away']] = \
                df[['league', 'match', 'bet_side', 'home', 'away']].apply(lambda x: x.str.strip())
    df['sub_type'] = df['bet_side'].str.split(' ').str[0]
    df['bet_side'] = df['bet_side'].str.split(' ').str[1]
    df['odds'] = df['selection_details'].str.split(' ').str[-1]
    df['odds'] = pd.to_numeric(df['odds'], errors='coerce')
    df['imp_prob'] = 1/df['odds']

    df['home'].fillna('Unknown', inplace=True)
    df['away'].fillna('Unknown', inplace=True)

    def bet_filter(df):
        if df['bet_side'] == 'Draw' :
            return 'D'
        elif str(df.bet_side) in str(df.home):
            return 'H'
        else:
            return 'A'

    df['bet_side'] = df.apply(bet_filter, axis=1)

    df = df.drop(['selection_details'], axis=1)

    return df


def win_ratio_table(df):
    df = df.copy()
    df = df.loc[df['status_receiptno'] == 'Settled']
    df['win_ind'] = np.where(df['returns'] > 0, 1, 0)
    return df


def return_by_match_table(df):
    df = df.copy()
    df= df[['datetime', 'home', 'away', 'amount', 'payout_winnings', 'imp_prob', 'bet_side', 'win_ind', 'returns']]
    df['match_total_bet'] = df.groupby([ 'home', 'away', 'datetime'])['amount'].transform(np.sum)
    df['match_total_returns'] = df.groupby(['home', 'away', 'datetime'])['payout_winnings'].transform(np.sum)
    df['bet_per_match'] = df['amount']/ df['match_total_bet']
    df['imp_prob_weighted'] = df['imp_prob'] * df['bet_per_match']
    df['date'] = df['datetime'].dt.date

    # groupby
    # aggregate bets for each match, since same event
    bet_side_one_hot = pd.get_dummies(df['bet_side'])
    df = pd.concat([df, bet_side_one_hot], axis=1)
    # df[['bet_side_A', 'bet_side_D', 'bet_side_H']] = df[['bet_side_A', 'bet_side_D', 'bet_side_H']]\
    df[['A', 'D', 'H']] = df[['A', 'D', 'H']].apply(lambda x: x * df['bet_per_match'])

    df = df.drop(['match_total_returns', 'match_total_bet', 'bet_per_match', 'imp_prob'], axis= 1)
    df['num_of_bets'] = 1
    df = df.groupby(['home', 'away', 'date']).sum()

    df['frac_bets_win'] = df['win_ind']/ df['num_of_bets']
    df['agg_win_ind'] = np.where((df['payout_winnings'] - df['amount']) > 0, 1, 0)
    a = df[['A', 'D', 'H']]
    df = df.assign(side_agg = a.idxmax(axis=1), max_side_bet = a.max(axis=1))
    df['exact_frac_win'] = df['max_side_bet'] * df['agg_win_ind']

    return df.reset_index()

def return_by_match_table_simple(df):
    df['match_name'] = df['home'] + ' v ' + df['away']
    df = df[['match_name', 'date', 'returns']]
    return df


def return_by_day_table(df):

    return df