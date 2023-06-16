import streamlit as st
import pandas as pd
import numpy as np
import re
import time

st.set_page_config(
    page_title='Raisers Edge Data Sanitiser',
    page_icon=':magic_wand:',
    layout="wide"
)

hide_streamlit_style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('🪄 Raisers Edge Data Sanitiser')

st.markdown('##')
st.write('##### Upload Data export from Raisers Edge')
st.markdown('##')

def is_valid_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+$'

    if bool(re.match(email_regex, email)) == True: return email
    else: return np.NaN

def do_cleanup(re_data):

    ### Rename columns
    re_data = re_data.rename(
        columns={
            'CnBio_Title_1': 'TITLE',
            'CnBio_First_Name': 'FIRST_NAME',
            'CnBio_Last_Name': 'LAST_NAME',
            'CnRelEdu_1_01_Class_of': 'CLASS_OF',
            'CnRelEdu_1_01_Degree': 'DEGREE',
            'CnRelEdu_1_01_Frat_Sorority': 'HOSTEL',
            'CnRelEdu_1_01_Maj_1_01_Tableentriesid': 'DEPARTMENT',
            'CnRelOrg_1_01_Org_Name': 'ORGANIZATION_NAME',
            'CnRelOrg_1_01_Position': 'POSITION',
            'CnPh_1_01_Phone_number': 'EMAIL',
            'CnAdrAdrProc_City': 'CITY',
            'CnAdrAdrProc_State': 'STATE_1',
            'CnAdrAdrProc_County': 'STATE_2',
            'CnAdrAdrProc_Country': 'COUNTRY',
            'CnAttrCat_1_01_Description': 'CHAPTER',
            'CnAttrCat_3_01_Description': 'REUNION_YEAR',
            'CnAttrCat_2_01_Description': 'AWARDS'
        }
    )

    ### Convert 'Class of' from FLOAT to INT
    re_data['CLASS_OF'] = re_data['CLASS_OF'].fillna(0)
    re_data['CLASS_OF'] = re_data['CLASS_OF'].astype(int)

    ### Remove incorrect organisations
    re_data['ORGANIZATION_NAME'] = re_data['ORGANIZATION_NAME'].replace('add-company', np.NaN)

    ### Get rid of records with no emails
    re_data = re_data.dropna(subset=['EMAIL']).copy()

    ### Get proper state
    re_data['STATE'] = re_data['STATE_1'].fillna('').astype(str) + ' ' + re_data['STATE_2'].fillna('').astype(str)
    re_data = re_data.drop(columns=['STATE_1', 'STATE_2']).copy()

    ### Remove Unknown chapters
    re_data['CHAPTER'] = re_data['CHAPTER'].replace('Unknown', np.NaN)

    re_data = re_data[['EMAIL', 'TITLE', 'FIRST_NAME', 'LAST_NAME', 'CLASS_OF', 'DEGREE', 'HOSTEL',
                       'DEPARTMENT', 'ORGANIZATION_NAME', 'POSITION', 'CITY', 'STATE', 'COUNTRY', 'CHAPTER',
                       'AWARDS']].copy()

    ### Check for Duplicate emails
    re_data = re_data.drop_duplicates('EMAIL').copy()

    ### Remove Invalid emails
    re_data['EMAIL'] = re_data['EMAIL'].apply(lambda x: is_valid_email(x))
    re_data = re_data.dropna(subset=['EMAIL']).copy()

    ### Remove IITB emails
    re_data = re_data[~(re_data['EMAIL'].str.contains('@iitb.ac.in'))].copy()

    ### Final Cleanup
    re_data = re_data.dropna(subset=['EMAIL']).copy()
    re_data = re_data.drop_duplicates('EMAIL').copy()

    return re_data

# Add file uploader for CSV file
uploaded_file = st.file_uploader('Upload a CSV file', type='csv', label_visibility='collapsed')

if uploaded_file:
    re_data = pd.read_csv(uploaded_file, encoding='latin1')

    re_data_csv = re_data.to_csv(index=False, lineterminator='\r\n', quoting=1)

    st.markdown('##')

    st.download_button(
        label='Download Data for Netcore',
        data=re_data_csv,
        file_name='Data for Netcore - Complete.csv',
        mime='text/csv'
    )

    st.markdown('##')

    st.dataframe(re_data, hide_index=True)