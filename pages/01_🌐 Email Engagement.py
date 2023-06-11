import streamlit as st
import pandas as pd

st.set_page_config(
    page_title='Engagement Recorder',
    page_icon=':incoming_envelope:',
    layout="wide")

hide_streamlit_style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('Netcore Engagement Recorder')

st.markdown('##')
st.write('##### Upload Data from Netcore')
# Add file uploader for CSV file
uploaded_file = st.file_uploader('Upload a CSV file', type='csv')
st.markdown('##')

if st.button('Upload'):
    df = pd.read_csv(uploaded_file)

    try:
        existing_df = pd.read_parquet('Databases/Netcore Data.parquet')
        existing_df = pd.concat(existing_df, df)

    except:
        existing_df = df.copy()

    existing_df = existing_df.drop_duplicates().copy()

    existing_df.to_parquet('Databases/Netcore Data.parquet', index=False)