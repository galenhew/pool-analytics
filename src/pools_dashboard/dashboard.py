import streamlit as st
import etl
import charts
import pandas as pd


st.title("Football Bets Dashboard")
st.markdown('A dashboard to keep track of football bets on SGPools, '
             'as betting houses provide few tools and only a PDF export '
            'for your transactions. This one\'s for the hamsters' )
st.sidebar.subheader("Menu")

global df


def convert_to_df(df_input):
    if df_input is not None:
        df = df_input.copy()
        df = etl.process(df)
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
    st.dataframe(df)
    download_butt = st.download_button(
        label="Download data as csv",
        data=df_to_csv(df),
        file_name='sgpools_cleaned.csv',
        mime='text/csv',
    )

    fig = charts.scatter_returns(df, 'date', 'returns')
    st.plotly_chart(fig)


elif option == 'Upload my file':
    uploaded_file = st.file_uploader(label = "Upload SGPools pdf export", type = ["pdf"])
    if uploaded_file is not None:
        df = etl.fetch(uploaded_file)
        df = convert_to_df(df)
        st.dataframe(df)
        download_butt = st.download_button(
            label="Download data as csv",
            data=df_to_csv(df),
            file_name='sgpools_cleaned.csv',
            mime='text/csv',
        )

        fig = charts.scatter_returns(df, 'date', 'returns')
        st.plotly_chart(fig)





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

