# ❄ Snow Sense

**Snow Sense** is a Python-based tool for analyzing snow coverage in selected regions using **Sentinel-2 imagery**. It allows both **manual** and **automated** modes for fetching, analyzing, and visualizing snow data from regions such as **Siachen Glacier**, **Central Tibetan Plateau**, and **European Alps**.

---

## 🌟 Features

### Manual Analysis Mode
- Preview Sentinel-2 imagery for selected regions.
- Clip the area of interest using predefined or custom polygon coordinates.
- Calculate **NDSI (Normalized Difference Snow Index)** to detect snow pixels.
- Classify snow into **dry** and **wet** types.
- Compute total snow area (in km²).
- Visualize results using interactive **Plotly** figures:
  - Snow Mask (NDSI)
  - Dry vs Wet Snow
  - Total Snow Area

### Automated AI Agent Mode
- Uses a **Google Gemini-powered LLM agent** to parse natural language prompts.
- Automatically fetches the location, loads data, analyzes snow, and returns results.
- Example prompt: `"Fetch Siachen and analyse it"`

### Support for Multiple Regions
- Siachen Glacier
- Central Tibetan Plateau
- European Alps
