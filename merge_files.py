import pandas as pd

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

def load_csv_files(file_configs):
    """Loads the CSV files and stores them in a dictionary."""
    csv_data = {}
    
    for var_name, file_info in file_configs.items():
        csv_path = file_info["path"]
        id_col = file_info["id_col"]
        csv_data[var_name] = pd.read_csv(csv_path)

        

        
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
    
    # Corrected iteration over delete_rows
    for var_name, rows_to_delete in config["delete_rows"].items():  
        # Convert rows_to_delete from strings to integers
        rows_to_delete = [int(row) for row in rows_to_delete]  # converts from string to int
        # Ensure rows_to_delete are valid indices
        valid_rows_to_delete = [row for row in rows_to_delete if row in csv_data[var_name].index]
        csv_data[var_name] = csv_data[var_name].drop(valid_rows_to_delete)  # Use drop to remove rows

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
        
        file_data = csv_data[var_name][[id_col] + [col[0] for col in columns]]
        
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
    csv_data = load_csv_files(config["files"])
    
    # Merge the files based on the configuration
    merged_data = merge_files(config, csv_data)
    
    # Output the merged data to the specified output file
    merged_data.to_csv(config["output_file"], index=False)

if __name__ == "__main__":
    config_file_path = "config.cfg"  # Update this with the actual config file path
    main(config_file_path)