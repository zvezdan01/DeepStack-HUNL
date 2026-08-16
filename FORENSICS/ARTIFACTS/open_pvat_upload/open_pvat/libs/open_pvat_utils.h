#ifndef OPEN_PVAT_UTILS_H
#define OPEN_PVAT_UTILS_H

#include "game_state.h"
#include "hand_strength.h"
#include "open_pvat_table.h"
#include "pvat_defines.h"

void initializeUtils(rollout_policy policy);
double rollout(gamestate_t* gamestate, rollout_policy policy);
double calculateEquity(gamestate_t* gamestate);
char* getBaseline(gamestate_t* gamestate, rollout_policy policy);

#endif
