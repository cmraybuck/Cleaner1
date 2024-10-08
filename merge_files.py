import pandas as pd
import sys  # {{ edit_1 }}

def parse_config(config_file):
    """Parses the config file and extracts commands."""
    config = {
        "files": {},  # To store details about input files
        "add_columns": {},  # To store columns to be added for each file
        "output_file": "",  # To store output file path
        "delete_rows": {}, # To store rows to be deleted for each file
    }

    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("FILE"):
                _, var_name, path, *id_col = line.split()
                id_col = id_col[0] if id_col else None
                config["files"][var_name] = {"path": path, "id_col": id_col}
            elif line.startswith("OUTPUT-FILE"):
                parts = line.split("=")
                if len(parts) > 1:  # Check if there is a value after "=" 
                    config["output_file"] = parts[1].strip() # Assigns output file path to config["output_file"] so it can be used later
            elif line.startswith("ADD-COL"):
                _, var_name, columns = line.split(None, 2)
                columns = [col.strip() for col in columns.split(",")]
                config["add_columns"][var_name] = columns
            elif line.startswith("DEL-ROW"):
                _, var_name, rows = line.split(None, 2)
                rows = [row.strip() for row in rows.split(",")]
                config["delete_rows"][var_name] = rows
    return config

def load_csv_files(file_configs, config):
    """Loads the CSV files and stores them in a dictionary."""    
    csv_data = {}
    
    for var_name, file_info in file_configs.items():
        csv_path = file_info["path"]
        id_col = file_info["id_col"]
        
        # Load the CSV file without specifying header to handle extra rows
        temp_data = pd.read_csv(csv_path, header=None)
        
        # Remove the specified rows dynamically
        rows_to_delete = config["delete_rows"].get(var_name, [])
        rows_to_delete = [int(row) for row in rows_to_delete]  # Convert to integers
        temp_data = temp_data.drop(rows_to_delete, errors='ignore')  # Drop specified rows
        
        # Reset index after dropping rows
        temp_data.reset_index(drop=True, inplace=True)
        
        # Set the first row as header
        temp_data.columns = temp_data.iloc[0]  # Set the first row as header
        temp_data = temp_data[1:]  # Remove the header row from the data
        
        csv_data[var_name] = temp_data
        
        # If ID column is specified as a number (index-based)
        if id_col and id_col.isdigit():
            id_col = int(id_col)
            id_col_name = csv_data[var_name].columns[id_col]
            file_info["id_col"] = id_col_name
        else:
            file_info["id_col"] = id_col

    return csv_data

def merge_files(config, csv_data):
    """Merges CSV files based on the provided configuration."""    
    merged_data = None

    for var_name, columns in config["add_columns"].items():
        file_info = config["files"][var_name]
        id_col = file_info["id_col"]
        
        # Convert the ID column to string to avoid type mismatch
        csv_data[var_name][id_col] = csv_data[var_name][id_col].astype(str)
        
        # Handle renaming columns if specified
        columns = [col.split(" AS ") for col in columns]  # Split for renaming
        columns = [(col[0], col[1] if len(col) > 1 else col[0]) for col in columns]  # Create tuples (original, new)
        
        # Create a unique rename dictionary to avoid overwriting
        rename_dict = {}
        for original, new in columns:
            if original not in rename_dict:  # Only rename if not already renamed
                rename_dict[original] = new
        
        # Handle both column names and indices
        selected_columns = []
        for col in columns:
            if col[0].isdigit():  # Check if it's a number
                selected_columns.append(csv_data[var_name].iloc[:, int(col[0])])  # Add by index
            else:
                selected_columns.append(csv_data[var_name][col[0]])  # Add by name
        
        file_data = pd.concat([csv_data[var_name][id_col]] + selected_columns, axis=1)
        
        # Rename columns dynamically
        file_data.rename(columns=rename_dict, inplace=True)
        
        if merged_data is None:
            merged_data = file_data
        else:
            merged_data = pd.merge(merged_data, file_data, on=id_col, how='outer')
    
    return merged_data

def main(config_file):
    # Parse the configuration file
    config = parse_config(config_file)
    
    # Load CSV files based on the configuration
    csv_data = load_csv_files(config["files"], config)  # {{ edit_1 }}
    
    # Merge the files based on the configuration
    merged_data = merge_files(config, csv_data)
    
    # Output the merged data to the specified output file
    merged_data.to_csv(config["output_file"], index=False)

if __name__ == "__main__":
    config_file_path = sys.argv[1] 
    main(config_file_path)