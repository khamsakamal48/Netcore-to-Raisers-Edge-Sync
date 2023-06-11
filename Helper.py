import streamlit as st

st.set_page_config(
    page_title='Netcore Data synchronizer',
    page_icon=':arrows_counterclockwise:',
    layout="wide")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Add a title and intro text
st.title('Netcore Data synchronizer')
st.text('This is a web app to perform data syncing between Netcore and Raisers Edge.')