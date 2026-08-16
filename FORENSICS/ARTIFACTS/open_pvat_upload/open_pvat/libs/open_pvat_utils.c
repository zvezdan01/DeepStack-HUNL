/*
	Author: Josh Davidson
	Purpose: See open_pvat_utils.h
*/

#include "open_pvat_utils.h"

static char* POSTFLOP_BASELINES[6][6] = {
          {"11", "11", "120", "120", "120", "120"},
          {"11", "11", "121", "121", "121", "121"},
          {"20", "21", "21", "221", "221", "221"},
          {"20", "21", "21", "221", "221", "221"},
          {"20", "21", "21", "2221", "2221", "22221"},
          {"20", "21", "21", "2221", "2221", "22221"} };

static char* PREFLOP_BASELINES[6][6] = {
          {"0", "0", "0", "0", "0", "0"},
          {"11", "11", "121", "121", "121", "121"},
          {"20", "21", "21", "221", "221", "221"},
          {"20", "21", "21", "221", "221", "221"},
          {"20", "21", "21", "2221", "2221", "2221"},
          {"20", "21", "21", "2221", "2221", "2221"} };

static int FUTURE_BETS[4] = {10, 8, 4, 0};

/*
	Load in the preflop pot equity table
*/
void initializeUtils(rollout_policy policy)
{
  if (policy == ALWAYS_CALL || policy == BET_CALL) {
    loadPreflopPotEquity();
	} else {
		fprintf(stderr, "Failed to initialize utils, invalid policy\n");
		exit(-1);
	}	
}

/*
	Perform a rollout.
	What this does is for a given gamestate,	perform the baseline	action
	(the policy) for the given gamestate.  The equity that the policy obtains is
	then used to calculate the pvat result for the gamestate and returned.
*/
double rollout(gamestate_t* gamestate, rollout_policy policy) {

	double result, equity;
	int i, action, pot_size,contributed, undo_flag = 0;
	char* baseline;
	gamestate_t tmp_gamestate;

	memcpy(&tmp_gamestate, gamestate, sizeof(gamestate_t));

	if(gamestate->game_over) {
		result = valueOfGameState(gamestate, 0);
	} else if(gamestate->dealing == NOT_DEALING) {
		assert(gamestate->num_actions[gamestate->round] == 0);
		baseline = getBaseline(gamestate,policy);

		for(i=0;i<strlen(baseline); i++) {
			action = baseline[i] - '0';
			doActionAtChoiceNode(gamestate, action);
		}
		undo_flag = 1;
	}
	
	if(gamestate->game_over) {
		result = valueOfGameState(gamestate, 0);
	} else {
		pot_size = gamestate->pot_size;
		contributed = gamestate->money_spent[0];
		equity = calculateEquity(gamestate);
		
		if(policy == BET_CALL) {
			pot_size += FUTURE_BETS[gamestate->round-1]*MIN_BET_SIZE;
			contributed += FUTURE_BETS[gamestate->round-1]*MIN_BET_SIZE/2;
		}
		result = equity*pot_size - contributed;
	}
	
	if(undo_flag) {
		memcpy(gamestate, &tmp_gamestate, sizeof(gamestate_t));
	}
	
	return result;
}

/*
	For preflop, this function will lookup the equity of a given hand from the
	preflop pot equity table, otherwise it will calculate it using the hand
	strength equity calculation in hand_strength.c
*/
double calculateEquity(gamestate_t* gamestate)
{
	if(gamestate->game_over) {
		fprintf(stderr,"Equity calculating in gameover state\n");
		exit(-1);
	}
	
	if(gamestate->dealing == NOT_DEALING) {
		fprintf(stderr, "Equity calculating in non dealing state\n");
		exit(-1);
	}

	if(gamestate->round == 1) {
		double equity;
		equity = lookupPreflopPotEquity(gamestate->player_cards[0], gamestate->player_cards[1]);
		return equity;
	} else {
		double equities[2];
		int* pocket_cards[2];

		pocket_cards[0] = gamestate->player_cards[0];
		pocket_cards[1] = gamestate->player_cards[1];

		handEquities(pocket_cards, gamestate->player_folded, gamestate->board_cards,gamestate->round-1, equities);
		return equities[0];
	}
}

/*
	This returs the baseline for the given policy
*/
char* getBaseline(gamestate_t* gamestate, rollout_policy policy)
{
	int classes[2];

	if(policy == BET_CALL) {
		   classes[0] = 2;
    classes[1] = 1;
  } else if (policy == ALWAYS_CALL) {
    classes[0] = 1;
    classes[1] = 1;
  }
	
  if (gamestate->round == 0) {
		return PREFLOP_BASELINES[classes[1]][classes[0]];
	} else {
    return POSTFLOP_BASELINES[classes[0]][classes[1]];
	}
}




