from flask import Flask, render_template, request, jsonify
import pandas as pd
import networkx as nx

app = Flask(__name__)

def read_data():
    edges_file_path = 'jarakdesa_test.xlsx'
    master_desa_file_path = 'master_desa.xlsx'
    edges_df = pd.read_excel(edges_file_path)
    master_desa_df = pd.read_excel(master_desa_file_path)
    return edges_df, master_desa_df

def calculate_shortest_path(edges_df, desa_df, source_desa, target_desa):
    merged_df1 = pd.merge(edges_df, desa_df, left_on='iddesa1', right_on='iddesa')
    merged_df2 = pd.merge(merged_df1, desa_df, left_on='iddesa2', right_on='iddesa', suffixes=('_desa1', '_desa2'))

    G = nx.Graph()
    for index, row in merged_df2.iterrows():
        G.add_edge(row['nmdesa_desa1'], row['nmdesa_desa2'], jarak=row['jarak'])

    shortest_path_length = nx.dijkstra_path_length(G, source_desa, target_desa, weight='jarak')
    shortest_path = nx.shortest_path(G, source_desa, target_desa, weight='jarak')
    return shortest_path, shortest_path_length

@app.route('/')
def index():
    master_desa_df = pd.read_excel('master_desa.xlsx')
    kecamatan_names = master_desa_df['nmkec'].unique().tolist()
    return render_template('index.html', kecamatan_names=kecamatan_names)

@app.route('/calculate', methods=['GET'])
def calculate():
    source_kec = request.args.get('source_kec')
    source_desa = request.args.get('source_desa')
    target_kec = request.args.get('target_kec')
    target_desa = request.args.get('target_desa')

    edges_df, master_desa_df = read_data()
    shortest_path, shortest_path_length = calculate_shortest_path(edges_df, master_desa_df, source_desa, target_desa)

    return render_template('result.html', source_desa=source_desa, target_desa=target_desa,
                           shortest_path=shortest_path, shortest_path_length=shortest_path_length)

@app.route('/get_desa', methods=['POST'])
def get_desa():
    data = request.get_json()
    kecamatan = data['kecamatan']
    master_desa_df = pd.read_excel('master_desa.xlsx')
    desa_list = master_desa_df.loc[master_desa_df['nmkec'] == kecamatan, 'nmdesa'].tolist()
    return jsonify({'desa_list': desa_list})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
