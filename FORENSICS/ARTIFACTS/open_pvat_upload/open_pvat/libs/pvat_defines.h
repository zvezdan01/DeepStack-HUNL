#ifndef PVAT_DEFINES_H
#define PVAT_DEFINES_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <limits.h>
#include <assert.h>
#include <dlfcn.h>
#include <inttypes.h>
#include <math.h>

#define DEBUG 0
#define MAX_SUFFIX_SIZE 1000
#define BUFFER_SIZE 1000
#define NUM_PLAYERS 2
#define MAX_PLAYER_NAME_LENGTH 50
#define MAX_NAMES 10
#define MAX_BET_STRING_LENGTH 50
#define DECK_SIZE 52
#define NUM_PRIVATE_CARDS 2
#define RANKS 13
#define SUITS 4
#define NUM_ROUNDS 4
#define TOTAL_BOARD_CARDS 5
#define TOTAL_PLAYER_CARDS 2
#define MIN_BET_SIZE 10
#define NOT_DEALING 0
#define DEALING_BOARD 1
#define DEALING_P1 2
#define NUM_ACTIONS 20
#define ACTION_FOLD 0
#define ACTION_CALL 1
#define ACTION_RAISE 2

extern const int NUM_BOARD_CARDS[NUM_ROUNDS];
extern const int SUM_BOARD_CARDS[NUM_ROUNDS];
extern const int BOARD_CARDS_POSITION[NUM_ROUNDS];
extern const char ACTION_CHAR_TABLE[3];
extern const int BLINDS[NUM_PLAYERS];
extern const int BET_SIZES[NUM_ROUNDS];
extern const int RAISES[NUM_ROUNDS];
extern const int PLAYER_ORDER[NUM_ROUNDS];

typedef enum { ALWAYS_CALL, BET_CALL } rollout_policy;

typedef struct {
  char* hand_history_file;
  char output_dir[PATH_MAX];
  char suffix[MAX_SUFFIX_SIZE];
  rollout_policy policy;
	int sample_num;
} pvat_parameters;

typedef struct {
	char* player_names[NUM_PLAYERS];
	double difference[NUM_PLAYERS][NUM_ROUNDS +1];
	double temp_difference[NUM_PLAYERS][NUM_ROUNDS +1];
	double bankroll[NUM_PLAYERS];
	int hand_number;
} pvat_results;

typedef struct
{
  int num_players;
  char player_names[NUM_PLAYERS][MAX_PLAYER_NAME_LENGTH];
  double difference[NUM_PLAYERS][NUM_ROUNDS+1];
  double bankroll[NUM_PLAYERS];
  int hand_count[NUM_PLAYERS];
  FILE* graph_files[NUM_PLAYERS];
} pvat_summary;

typedef struct
{
  int num_players;
  int pocket_cards[NUM_PLAYERS][TOTAL_PLAYER_CARDS];
  int board_cards[TOTAL_BOARD_CARDS];
  int num_board_cards;
  char bet_sequence[MAX_BET_STRING_LENGTH];
  int hand_number;
  char player_names[NUM_PLAYERS][MAX_PLAYER_NAME_LENGTH];
  double net_win[NUM_PLAYERS];
} pvat_input;

typedef struct {
	int round;
	int game_over;
	int dealing;
	int player;
	int pot_size;
	int max_spent;
	int num_called;
	int money_spent[NUM_PLAYERS];
	int player_folded[NUM_PLAYERS];
	int num_actions[NUM_ROUNDS];
	int actions[NUM_ROUNDS][NUM_ACTIONS];
	int raises[NUM_ROUNDS];
	char cards_used[DECK_SIZE+1];
	int num_unused_cards;
	int board_cards[TOTAL_BOARD_CARDS];
	int player_cards[NUM_PLAYERS][TOTAL_PLAYER_CARDS];
}gamestate_t;

#endif
