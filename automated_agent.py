import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain import hub
import tempfile
import numpy as np
import plotly.express as px
import plotly.io as pio

from Src.load_and_stack_bands import load_and_stack_bands
from Src.analysis import calculate_ndsi, classify_snow, compute_snow_area
from Src.visualization import visualize_results

load_dotenv()


# --------------------------
# Tools
# --------------------------

@tool
def load_and_stack(location: str) -> str:
    """
    Convert the user-provided location name to a folder path automatically.
    """

    # Normalize agent input to match folder names
    if 'siachen' in location.lower():
        key = 'Siachen'
    elif 'european alps' in location.lower():
        key = 'European_Alps'
    elif 'central tibetan plateau' in location.lower():
        key = 'Central_Tibetan_Plateau'
    else:
        return "Location not found"

    folder_name = key
    folder_path = os.path.join("Data", folder_name)  # Use the mapped folder name

    # Load the bands
    stacked_raster, profile = load_and_stack_bands(folder_path)

    temp_file = tempfile.NamedTemporaryFile(delete=False,suffix='.npy')
    np.save(temp_file,stacked_raster)
    temp_file.close()

    return json.dumps({
        "status": "success",
        "location": folder_name,
        "folder": folder_path,
        "profile": str(profile),
        "shape": stacked_raster.shape,
        "stacked_raster": temp_file.name
    })


@tool
def analyse(stacked_raster: str) -> str:
    """
    Analyse the stacked raster by calculating NDSI, classifying snow, 
    and computing snow area.
    """

    # Load raster from saved .npy file
    # Load stacked array
    data = np.load(stacked_raster)

    # 1. Compute NDSI mask
    snow_mask, ndsi_text = calculate_ndsi(data)

    # 2. Classify snow into dry vs wet
    dry_snow, wet_snow, snow_class_text = classify_snow(data, snow_mask)

    # 3. Compute snow area
    snow_area, area_text = compute_snow_area(snow_mask)
    # --- Save masks to temporary files ---
    snow_mask_file = tempfile.NamedTemporaryFile(delete=False, suffix=".npy")
    np.save(snow_mask_file, snow_mask)
    snow_mask_file.close()

    dry_file = tempfile.NamedTemporaryFile(delete=False, suffix=".npy")
    np.save(dry_file, dry_snow)
    dry_file.close()

    wet_file = tempfile.NamedTemporaryFile(delete=False, suffix=".npy")
    np.save(wet_file, wet_snow)
    wet_file.close()

    # --- Return results + file paths ---
    results = {
        "ndsi_text": ndsi_text,
        "snow_class_text": snow_class_text,
        "snow_area_text": area_text,
        "snow_area_value": float(snow_area),
        "snow_mask_path": snow_mask_file.name,
        "dry_snow_path": dry_file.name,
        "wet_snow_path": wet_file.name,
    }

    return json.dumps(results)
    


# --------------------------
# Agent setup
# --------------------------

def build_agent():
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    tool_names = [load_and_stack,analyse]

    prompt = hub.pull("hwchase17/react")


    agent = create_react_agent(
        llm = llm, 
        tools = tool_names,
        prompt = prompt)
    executor = AgentExecutor(
        agent=agent, 
        tools=tool_names, 
        verbose=True)
    return executor

executor = build_agent()
result = executor.invoke({"input": "Fetch siachen and analyse it"})
print(result)