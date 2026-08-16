/*
	Author: Josh Davidson
	Purpose: The main source header file.  open_pvat.c is the main driving
	program for open pvat.  It runs the bulk of the operations, passing off each
	round to the reader and then the open pvat library for state parseing.

*/

#ifndef OPEN_PVAT_H
#define OPEN_PVAT_H

#include "open_pvat_reader.h"
#include "open_pvat_utils.h"
#include "libs/game_state.h"
#include "libs/hand_strength.h"

void printUsage();
void parseArgs(int argc, char** argv, pvat_parameters* params);
void printOptions(pvat_parameters* params);
void singleRound(pvat_parameters* params, gamestate_t* gamestate, int round, char* bet_sequence, pvat_results* results);
void calculatePVATResults(pvat_parameters* params, pvat_input* hand, pvat_results* results);
int createGraphFile(pvat_parameters* params, char* name, pvat_summary* summary);
void postProcess(pvat_parameters* params, pvat_results* results, pvat_summary* summary);
void printResults(pvat_summary* summary, int index, int hand_number);
void cleanup(pvat_summary* summary);
void run(pvat_parameters* params);

extern const char *rank_names;
extern const char *suit_names;

#endif
