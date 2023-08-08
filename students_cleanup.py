import pandas as pd
import argparse


def main(input_file, output_file):
    # Mapping of old column names to new ones.
    column_mapping = {
        "Courriel": "email",
        "Numéro(s) de Téléphone Cellulaire": "phone_number",
        "Prénom ET Nom de famille de l'élève": "student_name",
        "Je souhaite m'inscrire à la session Automne 2023": "want_lesson",
        "Suivez-vous actuellement des cours avec nous?": "current_student",
        "Je désire faire une inscription aux cours de :": "instrument",
        "Durée des cours (Pour les nouveaux élèves de 10 ans et moins, nous suggérons fortement de débuter avec des cours de 30 minutes) ": "lesson_duration",
        "Si vous êtes un élève actuel, qui est votre enseignant? ": "preferred_teacher",
        "À quelle école aimeriez-vous suivre vos cours?": "location",
        "Est-il possible pour vous de vous déplacer à l'autre école si nous n'avons aucune place à votre premier choix?": "can_be_realocated",
        "#1 - Plage horaire idéale : Quelle journée de la semaine? ": "ideal_day",
        "#1 - Plage horaire idéale : À partir de quelle heure êtes-vous disponible pour débuter votre cours? (Exemple : 19h30)": "ideal_start_time",
        "#1 - Plage horaire idéale :  Quelle est l'heure la plus tard à laquelle vous pourriez débuter votre cours? (Exemple : 21h00)": "ideal_end_time",
        "#2 - Plage horaire alternative : Quelle journée de la semaine? ": "alternative_day_1",
        "#2 - Plage horaire alternative :  À partir de quelle heure êtes-vous disponible pour débuter votre cours? (Exemple : 16h00)": "alternative_start_time_1",
        "#2 - Plage horaire alternative :  Quelle est l'heure la plus tard à laquelle vous pourriez débuter votre cours? (Exemple : 21h00)": "alternative_end_time_1",
        "OPTIONNEL #3 - Plage horaire alternative : Quelle journée de la semaine? ": "alternative_day_2",
        "OPTIONNEL #3 - Plage horaire alternative :  À partir de quelle heure êtes-vous disponible pour débuter votre cours? (Exemple : 16h00)": "alternative_start_time_2",
        "OPTIONNEL #3 -  Plage horaire alternative :  Quelle est l'heure la plus tard à laquelle vous pourriez débuter votre cours? (Exemple : 21h00)": "alternative_end_time_2",
        "OPTIONNEL #4 - Plage horaire alternative : Quelle journée de la semaine? ": "alternative_day_3",
        "OPTIONNEL #4 - Plage horaire alternative :  À partir de quelle heure êtes-vous disponible pour débuter votre cours? (Exemple : 16h00)": "alternative_start_time_3",
        "OPTIONNEL #4 -  Plage horaire alternative :  Quelle est l'heure la plus tard à laquelle vous pourriez débuter votre cours? (Exemple : 21h00)": "alternative_end_time_3",
        "Dans l'éventualité où nous n'aurions pas exactement la plage horaire que vous souhaitez, qu'aimeriez-vous que nous priorisions?": "time_slot_priority_1",
        "Dans l'éventualité où nous n'aurions pas exactement la plage horaire que vous souhaitez, qu'aimeriez-vous que nous priorisions? [Choix 2]": "time_slot_priority_2",
        "Souhaitez vous prendre un cours en même temps qu'un autre membre de la famille?  Prendre note que vous devrez tout de même remplir l'inscription pour l'autre élève.": "simultaneous_family_class"
    }

    # Read the CSV file.
    df = pd.read_csv(input_file)

    # Select the columns from the dataframe based on the keys in column_mapping.
    df = df[list(column_mapping.keys())]

    # Rename the columns based on the mapping.
    df.rename(columns=column_mapping, inplace=True)

    # Clean up values.
    df['want_lesson'] = df['want_lesson'].apply(lambda x: True if x == 'Oui' else False)
    df['current_student'] = df['current_student'].apply(lambda x: True if x == 'Oui, je suis un élève actuel.' else False)
    df['preferred_teacher'] = df['preferred_teacher'].apply(lambda x: '' if x in ['Je ne sais pas / Pas de préférence', 'Je suis un nouvel élève'] else x)
    df['location'] = df['location'].apply(lambda x: 'Rosemere' if x == 'École de Rosemère - 399 Chemin de la Grande-Côte, Local A' else ('Lorraine' if x == 'École de Lorraine - 95 Boul. de Gaulle, Suite 205' else ''))
    df['lesson_duration'] = df['lesson_duration'].apply(lambda x: 60 if x == '60 Minutes' else (45 if x == 'École de Lorraine - 95 Boul. de Gaulle, Suite 205' else 30))

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
