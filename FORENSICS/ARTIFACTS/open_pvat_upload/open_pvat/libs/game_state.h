/*
	Author: Josh Davidson
	Purpose: Holds all the information about a 2 player Heads Up Limit game
*/
#ifndef GAME_STATE_H
#define GAME_STATE_H

#include "pvat_defines.h"
#include "hand_strength.h"

void doActionAtChoiceNode(gamestate_t *state, int action);
void initBettingRound(gamestate_t *state);
int nextPlayer(gamestate_t *state);
void initGameState(gamestate_t *state);
void doDealCards(gamestate_t *state, const int *cards, int num_cards);
void cardDealingPreparation(gamestate_t *state, int **cards_ret, int *num_cards_ret);
int readGameState(const char *line, gamestate_t *state);
int readActionFragment(const char *line, gamestate_t *state);
int stateCanDoAction(const gamestate_t *state, const int action);
int readAction(const char *line, int *chars_consumed);
int readStateCardFragment(const char *line, gamestate_t *state);
int readStateHandFragment(const char *line, gamestate_t *state);
int readBoardFragment(const char *line, gamestate_t *state);
double valueOfGameState(const gamestate_t * state, int player);

#endif
