import streamlit as st

import charts
import etl
import numpy as np
from metrics import get_archie_score, get_num_bets

st.title("SGPools Soccer Bets Tracker")
st.write('- No information is stored. \n'
         '- Step 1: Download "Transaction History" PDF from SGPools app. \n '
         '- Step 2: Upload the PDF here.')

global df


def convert_to_df(df_input):
    if df_input is not None:
        df = df_input.copy()
        df = etl.process(df)
    return df


def df_to_match(df):
    if df is not None:
        df = etl.football_table(df)
        df_wr = etl.win_ratio_table(df)
        # wr= charts.win_ratio(df_wr)
        df_match = etl.return_by_match_table(df_wr)
    return df_match


option = st.selectbox(
    'Input file',
    ('Sample file', 'Upload my file'))


def df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def st_return_chart(df):
    df = convert_to_df(df)
    df_match = df_to_match(df)
    df_match2 = etl.return_by_match_table_simple(df_match)
    st.dataframe(df_match2)
    download_butt = st.download_button(
        label="Download data as csv",
        data=df_to_csv(df_match2),
        file_name='sgpools_cleaned.csv',
        mime='text/csv',
    )
    st.header("Historical Metrics")
    st.subheader("Returns per match")
    fig = charts.scatter_returns(df_match2, 'date', 'returns')
    st.plotly_chart(fig)
    st.subheader("Archie Score")
    return df, df_match, df_match2


def st_open_bets(df):
    st.header('Open Bets')
    df_open_bets = etl.open_bets(df)
    st.dataframe(df_open_bets)

    total_odds = np.round(np.mean(df_open_bets)['odds'], 2)
    total_imp_prob = np.round(1 / total_odds, 2)
    total_amount = np.round(np.sum(df_open_bets)['amount'], 2)
    total_potential_win = np.round(np.sum(df_open_bets)['potential_win'], 2)

    st.markdown("Mean Odds/ Implied Prob.:")
    st.markdown(total_odds)
    st.markdown(total_imp_prob)
    st.markdown("Total Amount:")
    st.markdown(total_amount)
    st.markdown("Total Potential Payout:")
    st.markdown(total_potential_win)

def st_num_bets(df):
    every_bet, num_matches_bet = get_num_bets(df)
    st.markdown("Total number of bets made")
    st.markdown(every_bet)
    st.markdown("Number of matches bet")
    st.markdown(num_matches_bet)


def st_archie_score(df):
    archie_score, chance_fluke = get_archie_score(df)
    st.markdown("Archie Score")
    st.markdown(archie_score)
    st.markdown("Chance of Fluke Results")
    st.markdown(chance_fluke)


if option == 'Sample file':
    df = etl.fetch_eg_csv()
    df, df_match, df_match2 = st_return_chart(df)
    st_num_bets(df_match)
    st_archie_score(df_match)
    st_open_bets(df)


elif option == 'Upload my file':
    uploaded_file = st.file_uploader(label="Upload SGPools pdf export", type=["pdf"])
    if uploaded_file is not None:
        df = etl.fetch(uploaded_file)
        df, df_match, df_match2 = st_return_chart(df)
        st_num_bets(df_match)
        st_archie_score(df_match)
        st_open_bets(df)
