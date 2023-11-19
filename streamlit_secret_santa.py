import streamlit as st
import pandas as pd
from io import StringIO
import json

liste_participants = None
config = None

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

uploaded_participants_file = st.file_uploader('Participants', type = 'csv', accept_multiple_files = False)
if uploaded_participants_file is not None:
    df_participants = pd.read_csv(uploaded_participants_file, header=None, names=['participants'])
    liste_participants = df_participants['participants']

uploaded_config_file = st.file_uploader('Configuration', type = 'json', accept_multiple_files = False)
if uploaded_config_file is not None:
    config = json.load(uploaded_config_file)

if st.button('Générer') and liste_participants is not None and config is not None:
    resultats = secret_santa(liste_participants, config)
    df_resultats = pd.DataFrame(resultats, columns = ['offrant', 'recevant'])
    st.write(df_resultats)
else:
    st.write('en attente des données ...')
             