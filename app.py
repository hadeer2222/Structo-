import streamlit as st
import base64
from PIL import Image
import io

# Set page configuration
st.set_page_config(
    page_title="Structo 🏗 - Steel Structure Design",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# App title and description
st.title("Structo 🏗")
st.subheader("Steel Structure Design Application")

# Create a simple logo container for Structo
# Using a custom styled div instead of SVG to avoid rendering issues
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <div style="display: inline-block; background-color: #4F8BF9; width: 200px; height: 80px; 
                   border-radius: 10px; padding: 10px; color: white; position: relative; 
                   font-size: 28px; font-weight: bold; line-height: 60px;">
            Structo 🏗
            <div style="position: absolute; bottom: 18px; left: 30px; right: 30px; height: 3px; background-color: white;"></div>
            <div style="position: absolute; bottom: 25px; left: 40px; right: 40px; height: 2px; background-color: white;"></div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Main description
st.markdown("""
    Structo is a specialized steel structure design application for calculating and analyzing:
    * Floor beams
    * Purlins
    
    Following Egyptian and American code standards with comprehensive section details, 
    charts for moments and deflections, and export capabilities.
""")

# Main options
st.markdown("### Choose Design Type")
col1, col2 = st.columns(2)

with col1:
    if st.button("Design of Floor Beams", use_container_width=True):
        st.switch_page("pages/floor_beams.py")

with col2:
    if st.button("Design of Purlins", use_container_width=True):
        st.switch_page("pages/purlins.py")

# Footer
st.markdown("---")
st.markdown("© 2023 Structo 🏗 - Specialized Steel Structure Design Application")
