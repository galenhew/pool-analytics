import streamlit as st

import charts
import etl
import numpy as np

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
        df_match2 = etl.return_by_match_table_simple(df_match)
    return df_match2


option = st.selectbox(
    'Input file',
    ('Sample file', 'Upload my file'))


def df_to_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


if option == 'Sample file':
    df = etl.fetch_eg_csv()
    df = convert_to_df(df)
    df_match = df_to_match(df)
    st.dataframe(df_match)
    download_butt = st.download_button(
        label="Download data as csv",
        data=df_to_csv(df_match),
        file_name='sgpools_cleaned.csv',
        mime='text/csv',
    )

    fig = charts.scatter_returns(df_match, 'date', 'returns')
    st.plotly_chart(fig)

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


elif option == 'Upload my file':
    uploaded_file = st.file_uploader(label="Upload SGPools pdf export", type=["pdf"])
    if uploaded_file is not None:
        df = etl.fetch(uploaded_file)
        df = convert_to_df(df)
        df_match = df_to_match(df)
        st.dataframe(df_match)
        download_butt = st.download_button(
            label="Download data as csv",
            data=df_to_csv(df_match),
            file_name='sgpools_cleaned.csv',
            mime='text/csv',
        )

        fig = charts.scatter_returns(df_match, 'date', 'returns')
        st.plotly_chart(fig)

        st.header('Open Bets')
        df_open_bets = etl.open_bets(df)
        st.dataframe(df_open_bets)

        total_odds = np.round(np.mean(df_open_bets)['odds'], 2)
        total_imp_prob = np.round(1 / total_odds, 2)
        total_amount = np.round(np.sum(df_open_bets)['amount'], 2)
        total_potential_win = np.round(np.sum(df_open_bets)['potential_win'], 2)
        total_potential_win_ev = np.multiply(total_potential_win, total_imp_prob)

        st.markdown("Mean Odds/ Implied Prob.:")
        st.markdown(total_odds)
        st.markdown(total_imp_prob)
        st.markdown("Total Amount:")
        st.markdown(total_amount)
        st.markdown("Total Potential Payout EV:")
        st.markdown(total_potential_win_ev)

# main page

# try:
#     df = convert_to_df(uploaded_file)
#     st.dataframe(df)
# except Exception as e:
#     print(e)
#     st.write("please upload file to app")

# try:
#     st.markdown("Win Ratio")
#     st.markdown(wr)
# except Exception as e:
#     print(e)


# csv = df_to_csv(df)
