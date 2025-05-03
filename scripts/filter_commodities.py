import os
import re
import pandas as pd

def filter_relevant_rows(input_file, week_start, week_end):
    pattern = re.compile(r"^[a-z]{2,3}\d{4}\s+,\d+.*$")
    filtered_rows = []

    with open(input_file, "r") as infile:
        for line in infile:
            if pattern.match(line.strip()):
                row = line.strip().split(",")
                row.append(week_start)
                row.append(week_end)
                filtered_rows.append(row)

    return filtered_rows

def extract_dates_from_filename(filename):
    # Example: "2024-01-01--2024-01-07.txt" -> ("2024-01-01", "2024-01-07")
    match = re.search(r"(\d{4}-\d{2}-\d{2})--(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return match.group(1), match.group(2)  # week_start, week_end
    return "Unknown", "Unknown"

def process_all_files(input_dir, output_file):
    all_data = []

    # Iterate through all files in the input directory
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            print(f"Processing file: {filename}")
            week_start, week_end = extract_dates_from_filename(filename)
            filtered_rows = filter_relevant_rows(file_path, week_start, week_end)
            all_data.extend(filtered_rows)

    # Convert the data to a DataFrame and save as CSV
    if all_data:
        # Dynamically determine the number of columns
        max_columns = max(len(row) for row in all_data)
        columns = [
            "Species", "Weekly Opening Price", "High", "Low", "Weekly Close",
            "Net Change", "Open Interest", "O.I Change", "Weekly Volume", "Volume", "Turnover", "Week Start", "Week End"
        ]
        # Extend column names if there are extra columns
        if len(columns) < max_columns:
            columns.extend([f"Extra_Column_{i}" for i in range(len(columns), max_columns)])

        df = pd.DataFrame(all_data, columns=columns)
        df.to_csv(output_file, index=False)
        print(f"Filtered data saved to: {output_file}")
    else:
        print("No relevant data found.")

# Paths
input_dir = "./downloads/commodities"
output_file = "./data/commodities.csv"

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Process all files
process_all_files(input_dir, output_file)