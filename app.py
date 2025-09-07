# app.py

import streamlit as st
from Src.load_and_stack_bands import load_and_stack_bands
from Src.clipper import clip_raster
from Src.analysis import calculate_ndsi, classify_snow, compute_snow_area
from Src.generate_preview import generate_preview
from Src.visualization import visualize_results
from automated_agent import build_agent
import numpy as np
from PIL import Image
import os
import ast
import rasterio

st.set_page_config(page_title="Snow Sense", layout="wide")

# ---------------------------
# Sidebar: Mode selection
# ---------------------------
mode = st.sidebar.radio("Select Mode", ["Manual Mode", "Automated Mode"])

# ---------------------------
# Permanent Heading & Description
# ---------------------------
st.title("❄ Snow Sense")
st.markdown(
    "Snow Sense is a tool to analyze and visualize snow coverage in selected regions "
    "using Sentinel-2 imagery. Select a mode to start."
)

# ---------------------------
# Manual Mode
# ---------------------------
if mode == "Manual Mode":
    st.header("Manual Analysis Mode")
    
    # 1️⃣ Choose desired location
    st.markdown("### Choose Desired Location")
    location = st.selectbox(
        "Choose the Location",
        ["Central_Tibetan_Plateau", "European_Alps", "Siachen"]
    )


    # ---------------------------
    # Show Preview
    # ---------------------------
# Reset preview image if location changes
    if "prev_location" not in st.session_state or st.session_state["prev_location"] != location:
        st.session_state["preview_img"] = None
        st.session_state["prev_location"] = location

    # Show preview
    if st.button("Show Preview") or st.session_state["preview_img"] is not None:
        if st.session_state["preview_img"] is None:
            region_path = os.path.join("Data", location)
            st.session_state["preview_img"] = generate_preview(region_path)
        st.image(st.session_state["preview_img"], caption=f"{location} preview",width=300)


    # ---------------------------
    # Clip region (Optional)
    # ---------------------------
    st.markdown("### Clip Region (Optional)")
    predefined_clips = {
        "Central_Tibetan_Plateau": {
            "None": None,
            "[(700000, 3600000), (700000, 3620000), (720000, 3620000), (720000, 3600000)]": [(700000, 3600000), (700000, 3620000), (720000, 3620000), (720000, 3600000)],
            "[(730000, 3630000), (730000, 3650000), (750000, 3650000), (750000, 3630000)]": [(730000, 3630000), (730000, 3650000), (750000, 3650000), (750000, 3630000)]
        },
        "European_Alps": {
            "None": None,
            "[(300000, 5000000), (300000, 5020000), (320000, 5020000), (320000, 5000000)]": [(300000, 5000000), (300000, 5020000), (320000, 5020000), (320000, 5000000)],
            "[(350000, 5050000), (350000, 5070000), (370000, 5070000), (370000, 5050000)]": [(350000, 5050000), (350000, 5070000), (370000, 5070000), (370000, 5050000)]
        },
        "Siachen": {
            "None": None,
            "[(700000, 3700000), (700000, 3720000), (720000, 3720000), (720000, 3700000)]": [(700000, 3700000), (700000, 3720000), (720000, 3720000), (720000, 3700000)]
        }
    }

    selected_clip = st.selectbox("Select predefined clipped region", list(predefined_clips[location].keys()))
    clip_coords_input = st.text_area(
        "Or enter polygon coordinates manually [(lon, lat), ...]",
        value="",
        height=50
    )

    # Load & Stack Bands
    if st.button("Load & Stack Bands"):
        if "stacked_array" not in st.session_state:
            stacked_array, profile = load_and_stack_bands(os.path.join("Data", location))
            st.session_state["stacked_array"] = stacked_array
            st.session_state["profile"] = profile
            st.success("Bands loaded and stacked successfully!")

            # Apply clipping
            try:
                coords_to_clip = None
                if selected_clip != "None":
                    coords_to_clip = predefined_clips[location][selected_clip]
                elif clip_coords_input.strip() != "":
                    coords_to_clip = ast.literal_eval(clip_coords_input)

                if coords_to_clip is not None:
                    stacked_array, profile = clip_raster(stacked_array, profile, coords_to_clip)
                    st.session_state["stacked_array"] = stacked_array
                    st.session_state["profile"] = profile
                    st.success("Raster clipped successfully!")
            except Exception as e:
                st.error(f"Error in clipping: {e}")



    # ---------------------------
    # Analysis Panel
    # ---------------------------
    if "stacked_array" in st.session_state:
        st.markdown("### Analysis Panel")
        if "analysis_done" not in st.session_state:
            st.session_state["analysis_done"] = False

        if st.button("Run Analysis") or st.session_state["analysis_done"]:
            stacked_array = st.session_state["stacked_array"]
            if not st.session_state["analysis_done"]:
                # Compute all analysis
                snow_mask, ndsi_summary = calculate_ndsi(stacked_array)
                dry_snow, wet_snow, classify_summary = classify_snow(stacked_array, snow_mask)
                snow_area, area_summary = compute_snow_area(snow_mask)

                # Store results
                st.session_state["snow_mask"] = snow_mask
                st.session_state["dry_snow"] = dry_snow
                st.session_state["wet_snow"] = wet_snow
                st.session_state["snow_area"] = snow_area
                st.session_state["ndsi_summary"] = ndsi_summary
                st.session_state["classify_summary"] = classify_summary
                st.session_state["area_summary"] = area_summary
                st.session_state["analysis_done"] = True

            # Display results
            st.markdown("**Snow Mask (NDSI) Summary:**")
            st.text(st.session_state["ndsi_summary"])
            st.markdown("**Dry vs Wet Snow Summary:**")
            st.text(st.session_state["classify_summary"])
            st.markdown("**Total Snow Area Summary:**")
            st.text(st.session_state["area_summary"])

    # ---------------------------
    # Visualization Panel
    # ---------------------------
    if "stacked_array" in st.session_state:
        st.markdown("### Visualization Panel")
        if "figs" not in st.session_state:
            st.session_state["figs"] = None

        if st.button("Visualize Results") or st.session_state["figs"] is not None:
            if st.session_state["figs"] is None:
                st.session_state["figs"] = visualize_results(
                    st.session_state["snow_mask"],
                    st.session_state["dry_snow"],
                    st.session_state["wet_snow"],
                    st.session_state["snow_area"]
                )

            st.markdown("**Snow Mask (NDSI)**")
            st.plotly_chart(st.session_state["figs"][0], use_container_width=True)
            st.markdown("**Dry vs Wet Snow**")
            st.plotly_chart(st.session_state["figs"][1], use_container_width=True)
            st.markdown("**Total Snow Area**")
            st.plotly_chart(st.session_state["figs"][2], use_container_width=True)
else:
    user_prompt = st.text_input("Enter your prompt (e.g., 'Fetch Siachen and analyse it'):")

    if st.button("🚀 Run Analysis") and user_prompt.strip():
        st.write(f"**Running Agent with prompt:** `{user_prompt}`")
        
        with st.spinner("Processing... this may take a while ⏳"):
            executor = build_agent()
            response = executor.invoke({"input": user_prompt})
        
        # --------------------------
        # Show Results
        # --------------------------
        output_text = response.get("output", "")
        
        st.subheader("Fetched analysis for the given location")
        
        if output_text:
            st.write(output_text)  # show raw text
            