"""Interactive CSV plotter built with Streamlit."""

from __future__ import annotations

from io import BytesIO
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd
import streamlit as st


DEFAULT_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


@st.cache_data
def load_csv(file_contents: bytes) -> pd.DataFrame:
    """Load an uploaded CSV into a DataFrame."""
    return pd.read_csv(BytesIO(file_contents))


def numeric_columns(dataframe: pd.DataFrame) -> list[str]:
    """Return columns containing at least one value usable as a number."""
    columns: list[str] = []
    for column in dataframe.columns:
        values = pd.to_numeric(dataframe[column], errors="coerce")
        if values.notna().any():
            columns.append(str(column))
    return columns


def format_timestamp_tick(value: float, _: float) -> str:
    """Format every minute and show the date on midnight ticks."""
    timestamp = mdates.num2date(value)
    if timestamp.hour == 0 and timestamp.minute == 0:
        return f"{timestamp:%Y-%m-%d}\n{timestamp:%H:%M}"
    return f"{timestamp:%H:%M}"


def plot_data(
    dataframe: pd.DataFrame,
    x_column: str,
    y_columns: list[str],
    colors: dict[str, str],
    x_label: str,
    y_label: str,
) -> Any:
    """Create a Matplotlib figure for the selected columns."""
    figure, axis = plt.subplots(figsize=(10, 6))
    raw_x_values = dataframe[x_column]
    datetime_x_values = pd.to_datetime(raw_x_values, errors="coerce")
    is_datetime = (
        not pd.api.types.is_numeric_dtype(raw_x_values)
        and datetime_x_values.notna().all()
    )
    x_values = datetime_x_values if is_datetime else raw_x_values

    for y_column in y_columns:
        y_values = pd.to_numeric(dataframe[y_column], errors="coerce")
        valid_rows = y_values.notna()
        if is_datetime:
            valid_rows &= datetime_x_values.notna()
        if not valid_rows.any():
            continue
        axis.plot(
            x_values[valid_rows],
            y_values[valid_rows],
            label=y_column,
            color=colors[y_column],
        )

    axis.set_xlabel(x_label)
    axis.set_ylabel(y_label)
    axis.set_title("SPL data")
    axis.grid(True, alpha=0.3)
    axis.legend()
    if is_datetime:
        axis.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        axis.xaxis.set_major_formatter(FuncFormatter(format_timestamp_tick))
        figure.autofmt_xdate()
    else:
        axis.locator_params(axis="x", nbins=10)
    figure.tight_layout()
    return figure


def main() -> None:
    """Render the Streamlit application."""
    st.set_page_config(page_title="CSV Plotter", layout="wide")
    st.title("Interactive CSV Plotter")
    st.write("Upload a CSV, choose the columns to plot, and assign a color to each series.")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is None:
        st.info("Upload a CSV file to begin.")
        return

    try:
        dataframe = load_csv(uploaded_file.getvalue())
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        st.error(f"Could not read the CSV file: {error}")
        return

    if dataframe.empty:
        st.error("The CSV file contains no data rows.")
        return

    columns = [str(column) for column in dataframe.columns]
    if not columns:
        st.error("The CSV file does not contain any columns.")
        return

    y_options = numeric_columns(dataframe)
    if not y_options:
        st.error("The CSV file does not contain a column with numeric data to plot.")
        return

    st.subheader("Plot settings")
    x_column = st.selectbox("X-axis column", options=columns)
    x_label = st.text_input("X-axis label", value="Time")
    default_y_columns = y_options[: min(2, len(y_options))]
    y_columns = st.multiselect(
        "Y-axis columns",
        options=y_options,
        default=default_y_columns,
        help="Only columns with at least one numeric value are available as Y series.",
    )

    if not y_columns:
        st.warning("Select at least one Y-axis column.")
        return

    y_label = st.text_input("Y-axis label", value="dB")
    colors: dict[str, str] = {}
    color_columns = st.columns(min(3, len(y_columns)))
    for index, y_column in enumerate(y_columns):
        with color_columns[index % len(color_columns)]:
            colors[y_column] = st.color_picker(
                f"Color for {y_column}",
                value=DEFAULT_COLORS[index % len(DEFAULT_COLORS)],
                key=f"color-{y_column}",
            )

    figure = plot_data(dataframe, x_column, y_columns, colors, x_label, y_label)
    image_buffer = BytesIO()
    figure.savefig(image_buffer, format="png", dpi=150, bbox_inches="tight")
    image_buffer.seek(0)

    plot_columns = st.columns([1, 6, 1])
    with plot_columns[1]:
        st.pyplot(figure, use_container_width=True)
        st.download_button(
            "Export graph image",
            data=image_buffer.getvalue(),
            file_name="csv-plot.png",
            mime="image/png",
        )
    plt.close(figure)

    with st.expander("Preview data"):
        st.dataframe(dataframe, use_container_width=True)


if __name__ == "__main__":
    main()