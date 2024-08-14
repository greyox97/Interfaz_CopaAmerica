from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo"})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"})

    if file and allowed_file(file.filename):
        try:
            # Leer el CSV
            df = pd.read_csv(file)

            # Verificar que el CSV no esté vacío
            if df.empty:
                return jsonify({"error": "El archivo CSV está vacío"})
            
            # Procesar los datos del CSV
            groups, playoffs = process_csv_data(df)

            # Verificar si se han procesado correctamente los datos
            if not groups or not playoffs:
                return jsonify({"error": "Error al procesar los datos del CSV"})
            
            # Enviar datos procesados al frontend
            return jsonify({"groups": groups, "playoffs": playoffs})
        except Exception as e:
            print(f"Error procesando el archivo: {e}")
            return jsonify({"error": f"Error procesando el archivo: {str(e)}"})
    else:
        return jsonify({"error": "Archivo no permitido"})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

def process_csv_data(df):
    groups = []
    playoffs = []

    try:
        # Obtener los grupos únicos
        unique_groups = df['Group'].dropna().unique()

        # Procesar los grupos
        for group in unique_groups:
            group_data = {
                "groupName": group,
                "teams": [],
                "matches": []
            }

            group_teams = df[df['Group'] == group]

            for team in group_teams['TeamName'].unique():
                team_data = group_teams[group_teams['TeamName'] == team].iloc[0]
                team_info = {
                    "TeamName": team,
                    "StarterPlayers": team_data['StarterPlayers'],
                    "SubstitutePlayers": team_data['SubstitutePlayers'],
                    "Coach": team_data['Coach']
                }
                group_data["teams"].append(team_info)

            group_matches = df[(df['Group'] == group) & df['Team1'].notna() & df['Team2'].notna()]
            for _, match in group_matches.iterrows():
                match_info = {
                    "Team1": match['Team1'],
                    "Team2": match['Team2'],
                    "MatchDate": match['MatchDate'],
                    "MatchTime": match['MatchTime'],
                    "Score1": match['Score1'],
                    "Score2": match['Score2']
                }
                group_data["matches"].append(match_info)

            groups.append(group_data)

        # Procesar los playoffs
        playoffs_data = df[df['PlayoffPlace'].notna()]

        for _, row in playoffs_data.iterrows():
            match_data = {
                "MatchDate": row['MatchDate'],
                "MatchTime": row['MatchTime'],
                "Team1": row['Team1'],
                "Team2": row['Team2'],
                "PlayoffPlace": row['PlayoffPlace']
            }
            playoffs.append(match_data)

    except Exception as e:
        print(f"Error procesando datos del CSV: {e}")
        return None, None

    return groups, playoffs

if __name__ == '__main__':
    app.run(debug=True)
