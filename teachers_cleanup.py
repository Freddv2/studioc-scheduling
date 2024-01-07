import pandas as pd
import argparse


def main(input_file, output_file):

    # Read the CSV file.
    df = pd.read_csv(input_file)
    # Trim whitespace from the column names
    df.columns = df.columns.str.strip()
    df['accept_new_student'] = df['accept_new_student'].apply(lambda x: True if x == 'Oui' else False)

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
