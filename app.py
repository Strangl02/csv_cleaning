import streamlit as st
import pandas as pd
from datetime import datetime

def process_lorry_run(file):
    try:
        # Load the CSV into a DataFrame, skipping the first two rows
        df = pd.read_csv(file, skiprows=2, header=None)

        # Check if the expected columns are present
        expected_cols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12]  # Adjust indices based on actual columns
        if not all(col < len(df.columns) for col in expected_cols):
            st.error("CSV file does not contain the required columns.")
            return None

        # Create a new DataFrame for the output
        output_df = pd.DataFrame()

        # Combine Column H and I to create the 'Route Name'
        output_df['Route Name'] = df.iloc[:, 7].astype(str) + " " + df.iloc[:, 8].astype(str)  # Column H + Column I

        # 'Assigned Driver Username' from Column M
        output_df['Assigned Driver Username'] = df.iloc[:, 12].astype(str)  # Column M

        # 'Assigned Vehicle Name' left blank
        output_df['Assigned Vehicle Name'] = ""

        # 'Stop Name' with [Postcode] stripped from the beginning (Assuming postcode is separated by space)
        output_df['Stop Name'] = df.iloc[:, 0].astype(str).str.replace(r'^\[.*?\]\s*', '', regex=True)  # Column A, remove [Postcode]

        # Remove rows where 'Stop Name' starts with 'Run:'
        output_df = output_df[~output_df['Stop Name'].str.startswith('Run:')]

        # Remove duplicate rows based on 'Stop Name'
        output_df = output_df.drop_duplicates(subset='Stop Name')

        # Modify 'Route Name': Add 'Run:' at the start and remove '.0' from numbers
        output_df['Route Name'] = 'Run ' + output_df['Route Name'].astype(str).str.replace('.0', ':', regex=False)

        # Default Stop Departure Time
        stop_departure_time = datetime.now().strftime("%m/%d/%y 4:00")

        # Initialize an empty DataFrame to hold the final output
        final_df = pd.DataFrame()

        # Helper function to determine depot based on route number
        def get_depot(route_name):
            try:
                # Extract number from route name
                route_number = int(route_name.split()[1].replace(':', ''))
                if 1 <= route_number <= 60:
                    return 'Bradford Depot'
                elif 90 <= route_number <= 110:
                    return 'Slough Depot'
                elif 150 <= route_number <= 170:
                    return 'Widnes Depot'
                elif 180 <= route_number <= 190:
                    return 'Leamington Spa Depot'
                elif 200 <= route_number <= 225:
                    return 'Cramlington Depot'
                return None
            except (ValueError, IndexError):
                # Return None if the route number is invalid
                return None

        # Iterate over each unique route
        for route in output_df['Route Name'].unique():
            # Filter data for the current route
            route_data = output_df[output_df['Route Name'] == route]
            
            # Get the driver username for this route
            driver_username = route_data['Assigned Driver Username'].iloc[0]

            # Get the appropriate depot for the route
            depot_name = get_depot(route)

            if depot_name is None:
                # Skip routes that don't belong to the specified depots
                continue

            # Create the start and end rows for the depot
            start_row = pd.DataFrame({
                'Route Name': [route],
                'Assigned Driver Username': [driver_username],
                'Assigned Vehicle Name': [""],
                'Stop Name': [depot_name],
                'Stop Arrival Time': "",  # Empty arrival time
                'Stop Departure Time': stop_departure_time,  # Only the first has departure time
                'Stop Notes': [""],
                'Address Name': [depot_name],
                'Full Address': [""],
                'Latitude': [""],
                'Longitude': [""]
            })

            end_row = pd.DataFrame({
                'Route Name': [route],
                'Assigned Driver Username': [driver_username],
                'Assigned Vehicle Name': [""],
                'Stop Name': [depot_name],
                'Stop Arrival Time': "",  # Empty arrival time
                'Stop Departure Time': "",  # Leave blank for the end row
                'Stop Notes': [""],
                'Address Name': [depot_name],
                'Full Address': [""],
                'Latitude': [""],
                'Longitude': [""]
            })

            # Append the start row, route data, and end row
            route_with_depot = pd.concat([start_row, route_data, end_row], ignore_index=True)

            # Ensure Address Name is correctly set for all rows
            route_with_depot['Address Name'] = route_with_depot['Address Name'].fillna(route_with_depot['Stop Name'])

            # Reorder columns to ensure 'Stop Arrival Time' is before 'Stop Departure Time'
            route_with_depot = route_with_depot[['Route Name', 'Assigned Driver Username', 'Assigned Vehicle Name',
                                                   'Stop Name', 'Stop Arrival Time', 'Stop Departure Time',
                                                   'Stop Notes', 'Address Name', 'Full Address', 'Latitude', 'Longitude']]

            # Append to final DataFrame
            final_df = pd.concat([final_df, route_with_depot], ignore_index=True)

        return final_df

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Streamlit App Interface
st.title("Lorry Run Details Cleaner")

# File uploader for LorryRunDetails CSV
uploaded_file = st.file_uploader("Upload the LorryRunDetails CSV", type="csv")

if uploaded_file is not None:
    # Process the file
    cleaned_data = process_lorry_run(uploaded_file)

    if cleaned_data is not None:
        # Show the cleaned data in the app
        st.write("Cleaned Data Preview:")
        st.dataframe(cleaned_data)

        # Provide a download button for the cleaned CSV
        st.download_button(
            label="Download Cleaned CSV",
            data=cleaned_data.to_csv(index=False),
            file_name="Cleaned_LorryRunDetails.csv",
            mime="text/csv"
        )
