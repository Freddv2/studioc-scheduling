import pandas as pd
import argparse


def main(input_file, output_file):
    # Mapping of old column names to new ones.
    column_mapping = {
        "Enseignant(e)": "teacher_name",
        "Instrument": "instrument",
        "Journée": "day",
        "Location": "location",
        "Heure début": "start_time",
        "Heure Fin": "end_time",
        "Début Pause 1": "start_break_1",
        "Fin Pause 1": "end_break_1",
        "Durée Pause 1": "length_break_1",
        "Début Pause 2": "start_break_2",
        "Fin Pause 2": "end_break_2",
        "Durée Pause 2": "length_break_2",

    }

    # Read the CSV file.
    df = pd.read_csv(input_file)
    # Trim whitespace from the column names
    df.columns = df.columns.str.strip()

    # Select the columns from the dataframe based on the keys in column_mapping.
    df = df[list(column_mapping.keys())]

    # Rename the columns based on the mapping.
    df.rename(columns=column_mapping, inplace=True)

    # Trim spaces and convert to lowercase for the rest of the columns.
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip().str.lower()

    # Save the transformed dataframe to a new CSV file.
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    # Define the command line arguments.
    parser = argparse.ArgumentParser(description='Clean up a CSV file.')
    parser.add_argument('-i', '--input', help='Input file name', required=True)
    parser.add_argument('-o', '--output', help='Output file name', required=True)
    args = parser.parse_args()

    main(args.input, args.output)
