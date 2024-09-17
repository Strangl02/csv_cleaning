mport streamlit as st
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
        output_df['Route Name'] = 'Run: ' + output_df['Route Name'].astype(str).str.replace('.0', '', regex=False)

        # Default Stop Departure Time
        stop_departure_time = datetime.now().strftime("%m/%d/%y 4:00")

        # Initialize an empty DataFrame to hold the final output
        final_df = pd.DataFrame()

        # Iterate over each unique route
        for route in output_df['Route Name'].unique():
            # Filter data for the current route
            route_data = output_df[output_df['Route Name'] == route]
            
            # Get the driver username for this route
            driver_username = route_data['Assigned Driver Username'].iloc[0]

            # Create the Bradford Depot rows
            start_row = pd.DataFrame({
                'Route Name': [route],
                'Assigned Driver Username': [driver_username],
                'Assigned Vehicle Name': [""],
                'Stop Name': ["Bradford Depot"],
                'Stop Arrival Time': "",  # Empty arrival time
                'Stop Departure Time': stop_departure_time,  # Only the first has departure time
                'Stop Notes': [""],
                'Address Name': ["Bradford Depot"],
                'Full Address': [""],
                'Latitude': [""],
                'Longitude': [""]
            })

            end_row = pd.DataFrame({
                'Route Name': [route],
                'Assigned Driver Username': [driver_username],
                'Assigned Vehicle Name': [""],
                'Stop Name': ["Bradford Depot"],
                'Stop Arrival Time': "",  # Empty arrival time
                'Stop Departure Time': "",  # Leave blank for the end row
                'Stop Notes': [""],
                'Address Name': ["Bradford Depot"],
                'Full Address': [""],
                'Latitude': [""],
                'Longitude': [""]
            })

            # Append the start row, route data, and end row
            route_with_bradford = pd.concat([start_row, route_data, end_row], ignore_index=True)

            # Ensure Address Name is correctly set for all rows
            route_with_bradford['Address Name'] = route_with_bradford['Address Name'].fillna(route_with_bradford['Stop Name'])

            # Reorder columns to ensure 'Stop Arrival Time' is before 'Stop Departure Time'
            route_with_bradford = route_with_bradford[['Route Name', 'Assigned Driver Username', 'Assigned Vehicle Name',
                                                   'Stop Name', 'Stop Arrival Time', 'Stop Departure Time',
                                                   'Stop Notes', 'Address Name', 'Full Address', 'Latitude', 'Longitude']]

            # Append to final DataFrame
            final_df = pd.concat([final_df, route_with_bradford], ignore_index=True)

        return final_df

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Streamlit App Interface
st.title("Lorry Run Details Cleaner")