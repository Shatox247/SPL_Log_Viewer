# Interactive CSV Plotter

This project provides a small Streamlit app for plotting data from a CSV file.

## Run locally

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the app:

```powershell
python -m streamlit run log_viewer.py
```

In the browser, upload a CSV file, choose the X-axis column, select one or more
numeric Y-axis columns, and use the color pickers to set each series color.
You can rename both axis labels. The graph occupies 75% of the page and
resizes responsively with the browser window. Use **Export graph image** to
download the current plot as a PNG file. ISO timestamp X-axis values are
labeled at every full minute (`HH:MM`). When recording crosses midnight, the
new date is shown once on the midnight tick.
