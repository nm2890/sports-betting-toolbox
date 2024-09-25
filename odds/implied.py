"""
This module is intended to computing true probabilities/odds from bookmaker
probabilities following some methods known in the literature.


@TODO : 


@author: nm2890
"""

import pandas as pd 

def add_margin_column(df , columns_odds) :

    df['Margin'] = - 1
    for col in columns_odds :
        df['Margin'] += 1/df[col]

    return(df)

def compute_implied_probabilities(df : pd.DataFrame,
                    columns_odds : list,
                    method = 'WPO',
                    drop_margin = True,
                    output_mode = 'Odd' # odd or proba in output
                    ) :

    nb_outcomes = len(columns_odds)
    df = add_margin_column(df , columns_odds)

    if method == 'WPO' :
        for col in columns_odds :
            # see https://www.football-data.co.uk/wisdom_of_crowd_bets
            df[f'Prob_{col}'] = (nb_outcomes - df['Margin']*df[col]) / (nb_outcomes * df[col])


    elif method == 'GOTO' :
        #see https://github.com/gotoConversion/goto_conversion/tree/main
        eps = 1e-6
        total = 1
        prob_col = []
        se_col = []
        for col in columns_odds :
            df[f'Prob_{col}'] = 1/df[col] #initialize probabilities using inverse odds
            df[f'Se_{col}'] = pow((df[f'Prob_{col}']-df[f'Prob_{col}']**2)/df[f'Prob_{col}'],0.5)  #compute the standard error (SE) for each probability
            prob_col.append(f'Prob_{col}')
            se_col.append(f'Se_{col}')

        step = ((df[prob_col].sum(axis=1) - total)/ df[se_col].sum(axis=1))

        for col in columns_odds :
            df[f'Prob_{col}'] =(df[f'Prob_{col}']  - (df[f'Se_{col}']  *step)).clip(lower=eps).clip(upper=1)
            
        df.drop(columns = se_col,inplace=True)

        

    if drop_margin and 'Margin' in df.columns :
        
        df.drop(columns = 'Margin',inplace=True)

    if output_mode == 'Odd' :
        for col in columns_odds :
            df[f'{col}_{method}'] = 1/df[f'Prob_{col}']

            df.drop(columns = f'Prob_{col}',inplace=True)

    
    return(df)