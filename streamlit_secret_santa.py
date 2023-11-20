import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import json
import os
import base64
import networkx as nx
import itertools

# données uploadées, à None par défaut
liste_participants = None
config = {
    'exclusions':[],
    'obligations':[]}
df_resultats = None

# données exemples
file_participant_exemple = 'participants_exemple.csv'
df_participant_exemple = pd.read_csv(file_participant_exemple, header=None, names=['participants'])
liste_participants_exemple = df_participant_exemple['participants'].to_list()
file_config_exemple = 'config_exemple.json'
with open(file_config_exemple) as f:
    config_exemple = json.load(f)

# fonction pour générer les résultats du secret santa
def secret_santa(liste_participants, config):
    '''
    la fonction prend en arguments une liste de participants, et une configuration qui définit:
    - les relations offrant > recevant prédéfinies
    - les relations offrant > recevant à exclure  
    elle renvoie une liste de couples (offrant, recevant)
    '''
    # création du graphe avec les participants
    exclusions = config['exclusions'].copy()
    edge_list = pd.DataFrame(
        [[item[0], item[1], 0] for item in itertools.product(liste_participants, liste_participants) if item[0] != item[1] and [item[0], item[1]] not in exclusions], 
        columns = ['source', 'target', 'retenu'])
    G = nx.from_pandas_edgelist(
        edge_list, 
        edge_attr = 'retenu',
        create_using = nx.DiGraph())
    
    # on traite d'abord les obligations
    obligations = config['obligations'].copy()
    offrants_obliges = []
    recevants_obliges = []
    for offrant, recevant in obligations:
        nx.set_edge_attributes(G, {(offrant, recevant): {'retenu': 1}})
        offrants_obliges.append(offrant)
        recevants_obliges.append(recevant)
       
    # on parcours au hasard la liste des participants
    cadeaux_a_faire = len(liste_participants) - len(obligations)
    parcours_offrant = []
    parcours_recevant = []
    while len(parcours_offrant) < cadeaux_a_faire and len(parcours_recevant) < cadeaux_a_faire:
        offrants_possibles = [offrant for offrant in liste_participants if (offrant not in parcours_offrant and offrant not in offrants_obliges)]
        offrant_a_traiter = offrants_possibles[np.random.randint(len(offrants_possibles))]
        recevants_possibles = [recevant for recevant in list(G[offrant_a_traiter]) if (recevant not in parcours_recevant and recevant not in recevants_obliges)]
        if len(recevants_possibles) > 0:
            # on tire au hasard les recevants restants parmi les target 
            recevant_a_traiter = recevants_possibles[np.random.randint(len(recevants_possibles))]
            nx.set_edge_attributes(G, {(offrant_a_traiter, recevant_a_traiter): {'retenu': 1}})
            parcours_offrant.append(offrant_a_traiter)
            parcours_recevant.append(recevant_a_traiter)
        else:
            # retour arrière
            nx.set_edge_attributes(G, {(parcours_offrant.pop(), parcours_recevant.pop()): {'retenu': 0}})
    return([(offrant, recevant) for offrant, recevant, edge in G.edges(data=True) if edge['retenu'] == 1])

# fonction qui génère un lien de téléchargement
def get_file_downloader_html(bin_file, file_label):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">télécharger un exemple {file_label}</a>'
    st.markdown(href, unsafe_allow_html=True)

# titre de l'application
st.title('Générateur secret santa')

# upload du fichier avec la liste des participants
uploaded_participants_file = st.file_uploader('Participants', type = 'csv', accept_multiple_files = False, help = 'liste des noms des participants au format csv')
if uploaded_participants_file is not None:
    df_participants = pd.read_csv(uploaded_participants_file, header=None, names=['participants'])
    liste_participants = df_participants['participants'].to_list()

# téléchargement d'un fichier exemple de liste de participants
get_file_downloader_html(file_participant_exemple, 'exemple de fichier participants')

# uload du fichier de configuration
uploaded_config_file = st.file_uploader('Configuration', type = 'json', accept_multiple_files = False, 
                                        help = 'fichier json avec une clé "exclusions" et une clé "obligations" qui contiennent une liste de couples (offrant, recevant)')
if uploaded_config_file is not None:
    config = json.load(uploaded_config_file)

# téléchargement d'un fichier exemple de configuration
get_file_downloader_html(file_config_exemple, 'exemple de fichier config')

# bouton pour lancer le calcul du secret santa
if st.button('Générer') :
    if liste_participants is not None:
        resultats = secret_santa(liste_participants, config)
        st.write('résultats:')
    else:
        # s'il n'y a pas de fichier uploadé, on génère avec les exemples
        resultats = secret_santa(liste_participants_exemple, config_exemple)
        st.write('pas de fichiers uploadés, résultats avec les données exemple:')
    df_resultats = pd.DataFrame(resultats, columns = ['offrant', 'recevant'])
    st.write(df_resultats)
    st.download_button(
        label = 'télécharger les résultats',
        data = df_resultats.to_csv().encode('utf-8'),
        file_name = 'secret_santa.csv',
        mime = 'text/csv',
    )

             