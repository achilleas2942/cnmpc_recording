def extract_data_to_dict(dataframe, columns, has_time=True):
    """Extracts specified columns from a dataframe and returns a dictionary"""
    data_dict = {col: dataframe[col].tolist() for col in columns}
    if has_time and "Time" in data_dict:
        initial_time = data_dict["Time"][0]
        data_dict["Time"] = [t - initial_time for t in data_dict["Time"]]
    return data_dict