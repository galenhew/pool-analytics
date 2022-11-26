import numpy as np


# archie
def get_archie_score(df_match):
    df_archie = df_match[['match_name', 'imp_prob_weighted', 'win_ind']]
    num_bets = df_archie.shape[0]
    exp_win = df_archie['imp_prob_weighted'].sum()
    num_win_bets = df_archie[df_archie['win_ind'] == 1]['win_ind'].count()
    archie_score = np.round(num_bets * (num_win_bets - exp_win) ** 2 / (exp_win * (num_bets - exp_win)))

    if archie_score <= 0.3:
        chance = 0.58
    elif archie_score <= 0.5:
        chance = 0.48
    elif archie_score <= 1:
        chance = 0.32
    elif archie_score <= 1.5:
        chance = 0.22
    elif archie_score <= 2:
        chance = 0.16
    elif archie_score <= 2.5:
        chance = 0.11
    elif archie_score <= 3:
        chance = 0.08
    elif archie_score <= 4:
        chance = 0.05
    elif archie_score <= 5:
        chance = 0.03
    elif archie_score <= 8:
        chance = 0.01
    else:
        chance = 0

    return archie_score, chance
