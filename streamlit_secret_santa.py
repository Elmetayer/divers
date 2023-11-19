import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import json
import os
import base64

liste_participants = None
config = {
    'exclusions':[],
    'obligations':[]}
df_resultats = None

def secret_santa(liste_participants, config):
    resultats = []
    offrants_restant = liste_participants.copy()
    recevants_restant = liste_participants.copy()
    exclusions = config['exclusions'].copy()
    obligations = config['obligations'].copy()

    # on traite d'abord les obligations
    for offrant, recevant in obligations:
        resultats.append((offrant, recevant))
        offrants_restant.pop(offrants_restant.index(offrant))
        recevants_restant.pop(recevants_restant.index(recevant))
        
    # on parcours au hasard la liste des participants
    for i_donnant_a_traiter in np.random.permutation(len(offrants_restant)):
        donnant_a_traiter = offrants_restant[i_donnant_a_traiter]
        # on tire au hasard les recevants restants
        for i_recevant_possible in np.random.permutation(len(recevants_restant)):
            # vérification des exclusions
            if (donnant_a_traiter, recevants_restant[i_recevant_possible]) not in exclusions and donnant_a_traiter != recevants_restant[i_recevant_possible]:
                resultats.append((donnant_a_traiter, recevants_restant[i_recevant_possible]))
                recevants_restant.pop(i_recevant_possible)
                break
            else:
                continue
    return(resultats)

def get_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">télécharger un exemple {file_label}</a>'
    st.markdown(href, unsafe_allow_html=True)

st.title('Générateur secret santa')

uploaded_participants_file = st.file_uploader('Participants', type = 'csv', accept_multiple_files = False, help = 'liste des noms des participants au format csv')
if uploaded_participants_file is not None:
    df_participants = pd.read_csv(uploaded_participants_file, header=None, names=['participants'])
    liste_participants = df_participants['participants'].to_list()

get_file_downloader_html('participants_exemple.csv', 'participants.csv')

uploaded_config_file = st.file_uploader('Configuration', type = 'json', accept_multiple_files = False, 
                                        help = 'fichier json avec une clé "exclusions" et une clé "obligations" qui contiennent une liste de couples (offrant, recevant)')
if uploaded_config_file is not None:
    config = json.load(uploaded_config_file)

get_file_downloader_html('config_exemple.json', 'config.json')

if st.button('Générer') and liste_participants is not None:
    resultats = secret_santa(liste_participants, config)
    df_resultats = pd.DataFrame(resultats, columns = ['offrant', 'recevant'])
    st.write('résultats:')
    st.write(df_resultats)
    st.download_button(
        label = 'télécharger les résultats',
        data = df_resultats.to_csv().encode('utf-8'),
        file_name = 'secret_santa.csv',
        mime = 'text/csv',
    )

             