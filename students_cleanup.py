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
        "Dans l'éventualité où nous n'aurions pas exactement la plage horaire que vous souhaitez, qu'aimeriez-vous que nous priorisions?": "prioritise",
        "Souhaitez vous prendre un cours en même temps qu'un autre membre de la famille?  Prendre note que vous devrez tout de même remplir l'inscription pour l'autre élève.": "simultaneous_family_class",
        "Si oui, veuillez écrire le prénom ET nom de famille de l'autre élève. Prendre note que vous devrez remplir l'inscription pour l'autre élève. Nous ne pouvons pas garantir que nous serons en mesure de placer les membres d'une même famille à la même plage horaire.": "sibling_name",
        "Si vous avez une suggestion ou un commentaire, n'hésitez pas à nous en faire part!": "comment",
        "Assigned_Teacher": "assigned_teacher",
        "Assigned_Day": "assigned_day",
        "Assigned_Start_Time": "assigned_start_time",
        "Assigned_Duration": "assigned_duration",
        "Âge de l'élève (requis pour les enfants seulement)": "age",
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
    df['preferred_teacher'] = df['preferred_teacher'].apply(
        lambda teacher_name: '' if teacher_name in ['Je ne sais pas / Pas de préférence', 'Je suis un nouvel élève', None] or pd.isna(teacher_name) else clean_preferred_teacher_name(teacher_name))
    df['location'] = df['location'].apply(lambda x: 'Rosemere' if x == 'École de Rosemère - 399 Chemin de la Grande-Côte, Local A' else ('Lorraine' if x == 'École de Lorraine - 95 Boul. de Gaulle, Suite 205' else ''))
    df['lesson_duration'] = df['lesson_duration'].apply(lambda x: 60 if x == '60 Minutes' else (45 if x == '45 Minutes' else 30))
    df['can_be_realocated'] = df['can_be_realocated'].apply(lambda x: False if x == 'Impossible' else True)
    df['alternative_day_2'] = df['alternative_day_2'].apply(lambda x: '' if x == "Non, pas d'autres possibilités" else x)
    df['alternative_day_3'] = df['alternative_day_3'].apply(lambda x: '' if x == "Non, pas d'autres possibilités" else x)
    df['simultaneous_family_class'] = df['simultaneous_family_class'].apply(lambda x: True if x == 'Oui' else False)
    df['ideal_start_time'] = df['ideal_start_time'].str.slice(0, -3)
    df['ideal_end_time'] = df['ideal_end_time'].str.slice(0, -3)
    df['alternative_start_time_1'] = df['alternative_start_time_1'].str.slice(0, -3)
    df['alternative_end_time_1'] = df['alternative_end_time_1'].str.slice(0, -3)
    df['alternative_start_time_2'] = df['alternative_start_time_2'].str.slice(0, -3)
    df['alternative_end_time_2'] = df['alternative_end_time_2'].str.slice(0, -3)
    df['alternative_start_time_3'] = df['alternative_start_time_3'].str.slice(0, -3)
    df['alternative_end_time_3'] = df['alternative_end_time_3'].str.slice(0, -3)
    df['assigned_teacher'] = df['assigned_teacher'].apply(lambda teacher_name: '' if pd.isna(teacher_name) else clean_preferred_teacher_name(teacher_name))
    df['assigned_duration'] = df['assigned_duration'].apply(lambda x: 60 if x == '60 Minutes' else (45 if x == '45 Minutes' else 30))
    # Trim spaces and convert to lowercase for the rest of the columns.
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.strip().str.lower()

    # Save the transformed dataframe to a new CSV file.
    df.to_csv(output_file, index=False)

    # Iterate through the rows, and for each non-empty sibling_name, check if it matches any student_name in other rows.
    for index, sibling_name in df['sibling_name'].items():
        if pd.notna(sibling_name) and sibling_name.strip():
            # Check if the sibling_name exists in student_name of other rows.
            if sibling_name not in df.loc[df.index != index, 'student_name'].values:
                print(f"Unmatched sibling name: {sibling_name}")


def clean_preferred_teacher_name(teacher_name):
    clean_teacher_name = teacher_name.split(".", 1)
    return clean_teacher_name[0] + "." if len(clean_teacher_name) > 1 else teacher_name


if __name__ == "__main__":
    # Define the command line arguments.
    parser = argparse.ArgumentParser(description='Clean up a CSV file.')
    parser.add_argument('-i', '--input', help='Input file name', required=True)
    parser.add_argument('-o', '--output', help='Output file name', required=True)
    args = parser.parse_args()

    main(args.input, args.output)
