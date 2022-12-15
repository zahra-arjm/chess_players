# -*- coding: utf-8 -*-
import chess
import chess.engine
import chess.pgn
from datetime import datetime
import pandas as pd
import math
from tqdm import tqdm

def evaluate_game(board, engine, limit):
   info = engine.analyse(board, limit)
   return info['score'].white().score(mate_score=1000)

start = datetime.now()

engine = chess.engine.SimpleEngine.popen_uci('U:\chess\stockfish_15_win_x64_avx2\stockfish_15_x64_avx2') # put here your path to your engine on your computer

movetimesec = 999
depth = 20
limit=chess.engine.Limit(time=movetimesec, depth=depth)
worksheetColumns = ["Date",
                    "Event Name",
                    "Event Rounds",
                    "Round",
                    "White Name",
                    "Black Name",
                    "Result",
                    "White ELO",
                    "Black ELO",
                    "Moves",
                    "White Av CP Loss",
                    "Black Av CP Loss",
                    "Evaluations List",
                    "White CP Loss List",
                    "Black CP Loss List",
                    "PGN",
                    "Analysis Depth"]

finalDf = pd.DataFrame(columns=worksheetColumns)

f = open("database_file.pgn") # path to your database file in PGN. You can export filtered games from ChessBase, Publish it, download the Html, then download the PNG, and that's it

my_list = []

while True:
    game = chess.pgn.read_game(f)
    if game is None:
        break  # end of file

    my_list.append(game)



for game in tqdm(my_list):
    
    try:
        # Evaluate all moves
        print(game.headers)
        board = game.board()
        
        evaluations = []
        
        evaluation = engine.analyse(board, limit=limit)['score'].white().score()
        evaluations.append(evaluation)
        
        for move in game.mainline_moves():
            board.push(move)
            positionEvaluation = evaluate_game(board, engine, limit)
            evaluations.append(positionEvaluation)
        
        
        # Adjust evaluations
        evaluationsAdjusted = evaluations.copy()
        evaluationsAdjusted = [max(min(x, 1000), -1000) for x in evaluationsAdjusted]
        
        # Calculate metrics
        white_centipawn_loss_list = []
        black_centipawn_loss_list = []
        
        index = 0
        for singleEvaluation in evaluationsAdjusted:
            if index > 0:
                previous_state_evaluation = evaluationsAdjusted[index - 1]
                current_state_evaluation = evaluationsAdjusted[index]    
                if index % 2 != 0:
                    white_centipawn_loss_list.append(previous_state_evaluation - current_state_evaluation)
                else:
                    black_centipawn_loss_list.append(current_state_evaluation - previous_state_evaluation)
            index += 1
        
        white_centipawn_loss_list_adjusted = [0 if x < 0 else x for x in white_centipawn_loss_list]
        black_centipawn_loss_list_adjusted = [0 if x < 0 else x for x in black_centipawn_loss_list]
        
        white_average_centipawn_loss = round(sum(white_centipawn_loss_list_adjusted) / len(white_centipawn_loss_list_adjusted))
        black_average_centipawn_loss = round(sum(black_centipawn_loss_list_adjusted) / len(black_centipawn_loss_list_adjusted))
    
        print("White average centipawn loss: {}".format(white_average_centipawn_loss))
        print("Black average centipawn loss: {}".format(black_average_centipawn_loss))
    
        # Fill dataframe with game data and results
        gameDf = pd.DataFrame(columns=worksheetColumns, index=range(1))
        
        gameDf['Date'] = datetime.strptime(game.headers["Date"], "%Y.%m.%d")
        gameDf['Event Name'] = game.headers["Event"]
        gameDf['Event Rounds'] = game.headers["EventRounds"]
        gameDf['Round'] = game.headers["Round"]
        gameDf['Moves'] = math.ceil(int(game.headers["PlyCount"])/2)
        gameDf.at[0, 'Evaluations List'] = evaluationsAdjusted
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        pgn_string = game.accept(exporter)
        gameDf.at[0, 'PGN'] = pgn_string
        print(pgn_string)
        gameDf['Analysis Depth'] = depth 
    
        
        gameDf['White Name'] = game.headers["White"]
        gameDf['Black Name'] = game.headers["Black"]
        try:
            gameDf['White ELO'] = game.headers["WhiteElo"]
        except:
            pass
        try:
            gameDf['Black ELO'] = game.headers["BlackElo"]
        except:
            pass
        gameDf.at[0,'White Av CP Loss'] = white_average_centipawn_loss
        gameDf.at[0, 'Black Av CP Loss'] = black_average_centipawn_loss
        gameDf.at[0, 'White CP Loss List'] = white_centipawn_loss_list_adjusted
        gameDf.at[0, 'Black CP Loss List'] = black_centipawn_loss_list_adjusted
        gameDf['Result'] = game.headers['Result']
        
        
        concat = [finalDf, gameDf]
        finalDf = pd.concat(concat)
        finalDf.to_pickle('data_with_cent_loss.pkl') # you can store the results in a pickle or do whatever you want, export to BQ, etc
        
    except:
        pass


#####################
print("Done! Job complete!")
#####################
#####################
finish = datetime.now()
print('It took long but it\'s done! The entire job took: {}'.format(finish - start))
#####################
#####################

