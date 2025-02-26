import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import math
import io

st.set_page_config(layout="wide")

# Sidebar: Upload CSV dataset
uploaded_file = st.sidebar.file_uploader("Upload CSV dataset", type=["csv"])

if uploaded_file:
    # Read the uploaded CSV file and fill missing values
    df = pd.read_csv(uploaded_file, low_memory=False).fillna(0)
    
    # Sidebar: Choose the label column and group column (e.g., subject)
    all_columns = df.columns.tolist()
    label_column = st.sidebar.selectbox(
        "Select Label Column", 
        options=all_columns, 
        index=all_columns.index("label") if "label" in all_columns else 0
    )
    group_column = st.sidebar.selectbox(
        "Select Group Column", 
        options=all_columns, 
        index=all_columns.index("subject") if "subject" in all_columns else 0
    )
    
    # Sidebar: Input for the number of columns in the composite plot grid
    cols_per_row = st.sidebar.number_input(
        "Number of columns for composite plot grid", 
        min_value=1, value=6, step=1
    )
    
    # Sidebar: Select the feature to visualize (exclude the chosen id columns and 'task' if present)
    features = [col for col in df.columns if col not in [group_column, label_column, 'task']]
    if features:
        feature_selected = st.sidebar.selectbox("Select Feature to Visualize", options=features)
    else:
        st.error("No valid features available for visualization.")
    
    # Sidebar: Option to set fixed y-axis limits
    use_fixed_y = st.sidebar.checkbox("Use fixed y-axis limits", value=False)
    
    # Sidebar: Filter the DataFrame based on unique values in the selected label column
    unique_labels = sorted(df[label_column].unique())
    label_filter = st.sidebar.multiselect("Select values for Label Column", options=unique_labels, default=unique_labels)
    
    # Filter the DataFrame based on the selected label values
    filtered_df = df[df[label_column].isin(label_filter)]
    
    # If fixed y-axis is desired, provide inputs for min and max limits based on filtered data
    if use_fixed_y:
        default_y_min = float(filtered_df[feature_selected].min())
        default_y_max = float(filtered_df[feature_selected].max() * 1.1)
        y_min_fixed = st.sidebar.number_input("Y-axis Minimum", value=default_y_min, step=0.1)
        y_max_fixed = st.sidebar.number_input("Y-axis Maximum", value=default_y_max, step=0.1)
    
    # Get unique groups from the chosen group column
    groups = sorted(filtered_df[group_column].unique())
    st.write(f"Displaying composite plot for {len(groups)} groups in a grid layout.")
    
    # Set up the grid layout for the composite plot using the user-specified number of columns
    rows = math.ceil(len(groups) / cols_per_row)
    fig, axes = plt.subplots(rows, cols_per_row, figsize=(4 * cols_per_row, 3 * rows))
    # Ensure axes is iterable even if only one row is present
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]
    
    # Create boxplots for each group based on the selected feature and label column
    for idx, grp in enumerate(groups):
        grp_df = filtered_df[filtered_df[group_column] == grp]
        ax = axes[idx]
        if not grp_df.empty:
            sns.boxplot(x=label_column, y=feature_selected, data=grp_df, ax=ax, showfliers=False)
            ax.set_title(f"{group_column}: {grp}", fontsize=10)
            if use_fixed_y:
                ax.set_ylim(y_min_fixed, y_max_fixed)
            else:
                ax.set_ylim(grp_df[feature_selected].min(), grp_df[feature_selected].max() * 1.1)
            ax.set_xlabel(label_column, fontsize=8)
            ax.set_ylabel("", fontsize=8)
            ax.tick_params(axis='both', which='major', labelsize=8)
        else:
            ax.set_visible(False)
    
    # Hide any unused subplots
    for ax in axes[len(groups):]:
        ax.set_visible(False)
    
    fig.tight_layout()
    
    # Display the composite plot on the page
    st.pyplot(fig, use_container_width=True)
    
    # Save the composite plot to a BytesIO buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    # Create a dynamic filename using the selected feature
    filename = f"{feature_selected.replace(' ', '_')}.png"
    
    # Download button placed below the image for saving the composite plot
    st.download_button(
        label="Download Composite Plot as PNG",
        data=buf,
        file_name=filename,
        mime="image/png"
    )
else:
    st.info("Please upload a CSV dataset to begin.")
