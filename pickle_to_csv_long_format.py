import pickle as pkl
import pandas as pd

with open("data_with_cent_loss.pkl", "rb") as f:
    object = pkl.load(f)
    
df = pd.DataFrame(object)
df.reset_index(drop=True, inplace=True)
df_long = pd.DataFrame(columns=
                       ['game_id',
                        'date',
                        'ELO',
                        'name',
                        'color',
                        'if_won',
                        'count_moves',
                        'move_no',
                        'CP_loss'
                        ])
current_row_idx = 0
start_row_idx = 0
for game_idx, game in df.iterrows():
    for idx_player, player in enumerate(['White', 'Black']):
        start_row_idx = current_row_idx
        # check if ELO is available for the player
        ELO = game[player + ' ELO']
        if ELO == 'NA':
            continue
        cp_list = game[player + ' CP Loss List']
        # check if there was not a tie
        if len(game['Result']) == 3:
            if_won = game['Result'][idx_player * 2]
        else:
            # if tie
            if_won = '2'
        count_moves = len(cp_list)
        for move_no, cp in enumerate(cp_list):
            df_long.loc[current_row_idx, ['move_no', 'CP_loss']] = \
                move_no + 1, cp
            current_row_idx += 1
        df_long.loc[start_row_idx : start_row_idx + count_moves,
                    ['game_id',
                        'date',
                        'ELO',
                        'name',
                        'color',
                        'if_won',
                        'count_moves']] = \
                        (game_idx,
                        game['Date'],
                        ELO,
                        game[player + ' Name'],
                        player,
                        if_won,
                        count_moves)
df_long.to_csv('data_with_cent_loss.csv')