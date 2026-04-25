import streamlit as st

if "q_area" not in st.session_state:
    st.session_state.q_area = ""

def set_q(val):
    st.session_state.q_area = val
    st.session_state.trigger = True

st.title("Streamlit State Test")

sample = "Hello World"
if st.button(f"Fill {sample}"):
    set_q(sample)

q = st.text_area("Input", key="q_area")

if st.button("Submit") or st.session_state.get("trigger", False):
    st.session_state.trigger = False
    st.write(f"Submitted: {q}")

st.write(f"Current q_area in state: {st.session_state.q_area}")
