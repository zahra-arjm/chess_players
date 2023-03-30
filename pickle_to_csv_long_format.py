import pickle as pkl
import pandas as pd

with open("data_with_cent_loss.pkl", "rb") as f:
    object = pkl.load(f)
    
df = pd.DataFrame(object)
df.reset_index(drop=True, inplace=True)
df_long = pd.DataFrame(columns=
                       ['date',
                        'name',
                        'ELO',
                        'color',
                        'if_won',
                        'count_moves',
                        'move_no',
                        'CP_loss'
                        ])

for index, game in df.iterrows():
    for idx_player, player in enumerate(['White', 'Black']):
        cp_list = game[player + ' CP Loss List']
        if_won = game['Result'][idx_player * 2]

# df.to_csv('data_with_cent_loss.csv')