import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import plotly.express as px


def main():
    st.set_page_config(page_title="OrgSim GenAI Demo", layout="wide")
    st.title("OrgSim — Streamlit + Google Generative AI (demo)")

    st.markdown(
        "This minimal app imports the requested libraries and shows a small DataFrame and Plotly chart."
    )

    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Google API Key (optional)", type="password")
        show_json = st.checkbox("Show sample JSON", value=True)

    # NOTE: We don't call the genai API here — only configure the client if a key is present.
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.sidebar.success("GenAI client configured")
        except Exception as e:
            st.sidebar.error(f"Failed to configure GenAI client: {e}")

    st.header("Sample data and visualization")

    # Create a small sample dataframe
    df = pd.DataFrame({"category": ["A", "B", "C", "D"], "value": [10, 23, 17, 9]})
    st.subheader("Sample DataFrame")
    st.dataframe(df)

    # Plot with Plotly Express
    fig = px.bar(df, x="category", y="value", title="Sample bar chart")
    st.plotly_chart(fig, use_container_width=True)

    if show_json:
        st.subheader("Sample JSON")
        sample = {"project": "OrgSim", "features": ["streamlit", "genai", "plotly"], "meta": {"version": "0.1"}}
        st.json(sample)


if __name__ == "__main__":
    main()
