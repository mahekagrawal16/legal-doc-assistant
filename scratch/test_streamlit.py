import streamlit as st

if "q_input" not in st.session_state:
    st.session_state.q_input = ""

sq = "What is the meaning of life?"
if st.button(f"Fill: {sq}"):
    st.session_state.q_input = sq

st.text_area("Question", value=st.session_state.q_input, key="q_area")

if st.button("Clear"):
    st.session_state.q_input = ""
    # Does this clear the text area? 
    # If not, we need to do st.session_state["q_area"] = ""

st.write(f"Session State q_input: '{st.session_state.q_input}'")
st.write(f"Session State q_area: '{st.session_state.get('q_area', 'N/A')}'")
