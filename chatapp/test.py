import streamlit as st

fruit = st.selectbox("Select a fruit:", ["apple", "banana", "cherry"], key='fruitselect')
car = st.selectbox("Select a car:", ["peogeot", "renault", "ford"], key='carselect')

st.write("You selected:", fruit, car)

st.write("session", st.session_state)

