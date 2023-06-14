import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title='Engagement Recorder',
    page_icon=':incoming_envelope:',
    layout="wide"
)

hide_streamlit_style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('Netcore Engagement Recorder')

# Load the Parquet file into a Pandas dataframe
# @st.cache_data() # Reset cache every 1 Hour
def get_templates():
    templates = pd.read_csv('Templates/Netcore Email Stats.csv')
    return templates

st.markdown('##')
st.write('##### Upload Data from Netcore')
st.markdown('##')

try:
    existing_df = pd.read_parquet('Databases/Netcore Data.parquet')
except:
    existing_df = pd.DataFrame()

# Add file uploader for CSV file
uploaded_files = st.file_uploader('Upload a CSV file', type='csv', accept_multiple_files=True, label_visibility='collapsed')

if uploaded_files:
    df = pd.DataFrame()

    for uploaded_file in uploaded_files:
        df_1 = pd.read_csv(uploaded_file)
        df = pd.concat([df, df_1])

    existing_df = pd.concat([existing_df, df])
    existing_df = existing_df.drop_duplicates().copy()

    existing_df.to_parquet('Databases/Netcore Data.parquet', index=False)

    st.markdown('##')



    with st.empty():

        progress_text = "## Upload in progress. Please wait..."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1, text=progress_text)
        st.success('Files uploaded successfully!', icon="✅")

st.markdown("""---""")
st.markdown("##")
st.markdown('#### Data Upload Template')
st.markdown("##")
st.dataframe(get_templates(), use_container_width=True, hide_index=True)