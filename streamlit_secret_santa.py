import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import json
import os
import base64

# données uploadées, à None par défaut
liste_participants = None
config = {
    'exclusions':[],
    'obligations':[]}
df_resultats = None

# données exemples
file_participant_exemple = 'participants.csv'
df_participant_exemple = pd.read_csv(file_participant_exemple, header=None, names=['participants'])
liste_participants_exemple = df_participant_exemple['participants'].to_list()
file_config_exemple = 'config.json'
config_exemple = json.load(file_config_exemple)

# fonction pour générer les résultats du secret santa
def secret_santa(liste_participants, config):
    '''
    la fonction prend en arguments une liste de participants, et une configuration qui définit:
    - les relations offrant > recevant prédéfinies
    - les relations offrant > recevant à exclure  
    elle renvoie une liste de couples (offrant, recevant)
    '''
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

# fonction qui génère un lien de téléchargement
def get_file_downloader_html(bin_file, file_label='File'):
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
get_file_downloader_html('participants_exemple.csv', file_participant_exemple)

# uload du fichier de configuration
uploaded_config_file = st.file_uploader('Configuration', type = 'json', accept_multiple_files = False, 
                                        help = 'fichier json avec une clé "exclusions" et une clé "obligations" qui contiennent une liste de couples (offrant, recevant)')
if uploaded_config_file is not None:
    config = json.load(uploaded_config_file)

# téléchargement d'un fichier exemple de configuration
get_file_downloader_html('config_exemple.json', )

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

             