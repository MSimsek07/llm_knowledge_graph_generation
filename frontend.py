import streamlit as st
import requests

st.title("Knowledge Graph Generator 🕸️📚")

research_input = st.text_input("Enter your research query", "Resul Daş")

if st.button("Generate Knowledge Graph"):
    with st.spinner("Processing..."):
        response = requests.post("http://localhost:8000/generate_graph", json={"input_text": research_input})
        
        if response.status_code == 200:
            data = response.json()
            st.success("Knowledge Graph generated successfully!")
            
            with st.expander("Research Response"):
                st.markdown(data["research_response"])

            with st.expander("Research Report"):
                st.write(data["research_report"])

            with st.expander("Documents"):
                st.write(data["documents"])

            with st.expander("Graph Documents"):
                st.write(data["graph_documents"])
        else:
            st.error(f"Error: {response.json()['detail']}")
