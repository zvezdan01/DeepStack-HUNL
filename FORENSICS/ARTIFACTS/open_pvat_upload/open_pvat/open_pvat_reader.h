/*
	Author: Josh Davidson
	Purpose: Parse the hand history file for the proper information needed to
	convert it into a gamestate and ensure the file is in the correct format.
*/

#ifndef OPEN_PVAT_READER_H
#define OPEN_PVAT_READER_H

#include "libs/game_state.h"
#include "libs/pvat_defines.h"

int readHandHistory(FILE* hand_history, pvat_input* hand);
int readDealerHandHistory(char* buffer, pvat_input* hand);
int checkHand(pvat_input* hand);
void convertGameState(const gamestate_t* gamestate, pvat_input* hand);

#endif
