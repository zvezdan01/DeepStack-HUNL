/*
	Author: Josh Davidson
	Purpose: Handle state information for a 2 player Heads Up Limit Texas Holdem
	game.
*/
#include "game_state.h"

/*
	Convert a string representing a card to its corrisponding integer.
	Return -1 on failure
*/
int stringToCard(const char string[2])
{
  int rank, suit;

	rank = -1;
	switch(string[0]) {
		case 'A':
		case 'a':
			rank = 12;
			break;
		case 'K':
		case 'k':
			rank = 11;
			break;
		case 'Q':
		case 'q':
			rank = 10;
			break;
		case 'J':
		case 'j':
			rank = 9;
			break;
		case 'T':
		case 't':
			rank = 8;
			break;
		default:
			rank = atoi(&string[0])-2;
	}

	if(rank>12 || rank<0) {
		return -1;
	}

	switch(string[1]) {
		case 'S':
		case 's':
			suit = 0;
			break;
		case 'H':
		case 'h':
			suit = 1;
			break;
		case 'D':
		case 'd':
			suit = 2;
			break;
		case 'C':
		case 'c':
			suit = 3;
			break;
		default:
			return -1;
	}
	
	return rank * SUITS + suit;
}

/*
	Read in a string and convert them into a card array
	Returns the number of cards read in.
*/
int stringToCards(const char *string, int num_cards, int *cards_ret)
{
  int i, pos;

  for(pos = 0, i = 0; i < num_cards; i++) {
    while(string[pos] == ' ') {++pos;}
    cards_ret[i] = stringToCard(&string[pos]);
    if(cards_ret[i] < 0) {
      return i;
    }
    pos += 2;
  }
  return i;
}


/*
	Initialize the gamestate to the defaults.
*/
void initGameState(gamestate_t *state)
{
  int i;

  state->game_over = 0;
  state->round = 0;
  state->max_spent = -1;
  state->pot_size = 0;
	state->num_called = 0;

  for(i = 0; i < NUM_PLAYERS; i++) {
    state->player_folded[i] = 0;
		state->money_spent[i] = BLINDS[i];
    state->pot_size += state->money_spent[i];		
    if(state->money_spent[i] > state->max_spent) {
      state->max_spent = state->money_spent[i];
    }
  }
	
  initBettingRound(state);

	state->dealing = DEALING_P1;

	state->num_unused_cards = DECK_SIZE;
	for(i = 0; i <= DECK_SIZE; i++) {
		state->cards_used[i] = 0;
	}
	
}

/*
	Initialize the betting round variables in the gamestate.
*/
void initBettingRound(gamestate_t *state)
{
  state->player = PLAYER_ORDER[state->round];
	
	if(state->player_folded[state->player]) {
    state->player = nextPlayer(state);
	}
	
  state->num_actions[state->round] = 0;
  state->raises[state->round] = 0;
	state->num_called = 0;
}

/*
	This performs the action at a choice node in the state.  It will	determine
	if the state is at a Game Over situation, and also it accumulates the money
	speant for each player and the current potsize as raises and calls are
	performed.
*/
void doActionAtChoiceNode(gamestate_t *state, int action)
{
  state->actions[state->round][state->num_actions[state->round]] = action;
	state->num_actions[state->round]++;

  if(action == ACTION_FOLD) {
		/*GAME_OVER*/
    state->player_folded[state->player] = 1;
		state->game_over = 1;
  } else if(action == ACTION_CALL) {
		state->pot_size -= state->money_spent[state->player];
		state->money_spent[state->player] = state->max_spent;
		state->pot_size += state->money_spent[state->player];
		++state->num_called;
		if(state->num_called == NUM_PLAYERS) {
			if(state->round + 1 == NUM_ROUNDS) {
				/*GAME_OVER*/
				state->game_over = 1;
			} else {
				/*ROUND_OVER*/
				++state->round;
				initBettingRound(state);
				state->dealing = DEALING_BOARD;
				return;
			}
		}
	} else {
		/*RAISE*/
		int bet_size;
		bet_size = BET_SIZES[state->round];
		state->max_spent += bet_size;
		state->pot_size -= state->money_spent[state->player];
		state->money_spent[state->player] = state->max_spent;
		state->pot_size += state->money_spent[state->player];
		state->raises[state->round]++;
		state->num_called = 1;
	}
	state->player = nextPlayer(state);
}

/*
	Move the player pointer to the next player to act, return that player.
*/
int nextPlayer(gamestate_t *state)
{
	int player;
	player = state->player;
	do {
		player++;
		if(player == NUM_PLAYERS)
			player = 0;
	}while(state->player_folded[player]);
	return player;
}

/*
	Deal the num_cards out into the state, marking the used ones off.
*/
void doDealCards(gamestate_t *state, const int *cards, int num_cards)
{
  int nc, *dest_cards, i;

  cardDealingPreparation(state, &dest_cards, &nc);
  if(num_cards == nc) {
    memcpy(dest_cards, cards, sizeof(int) * nc);
	}

  for(i = 0; i < nc; i++) {
    state->cards_used[dest_cards[i]] = 1;
  }
  state->num_unused_cards -= nc;
}

/*
	Prepare the gamestate for a deal. Sets up the number of cards to be dealt
	given the round.
*/
void cardDealingPreparation(gamestate_t *state, int **cards_ret, int *num_cards_ret)
{
  int nc, *cards;
	
  if(state->dealing == DEALING_BOARD) {
		nc = NUM_BOARD_CARDS[state->round];
    cards = &state->board_cards[BOARD_CARDS_POSITION[state->round]];
    state->dealing = NOT_DEALING;
  } else {
    cards = &state->player_cards[state->dealing - DEALING_P1][0];
    nc = TOTAL_PLAYER_CARDS;
    state->dealing++;
    if(state->dealing == DEALING_P1 + NUM_PLAYERS) {
      state->dealing = DEALING_BOARD;
    }
  }

  *num_cards_ret = nc;
  *cards_ret = cards;
}

/*
	Read a gamestate in from a formatted string
*/
int readGameState(const char *line, gamestate_t *state)
{
  int used, p, i;
	
  used = 0;
  if(sscanf(&line[used], "%d%n", &p, &i) < 1) {
    return -1;
  }
  p--;
  used += i;

  i = readActionFragment(&line[used], state);
  if(i < 0) {
    return -1;
  }
  used += i;
  if(p < 0) {
    if(!state->game_over) {
      return -1;
    }
  } else {
    if(state->dealing == NOT_DEALING && state->player != p) {
      return -1;
    }
  }

	i = readStateCardFragment(&line[used], state);
	
  if(i < 0) {
    return -1;
  }
  used += i;

  return used;
}

/*
	Read in an the action fragment of the hand string into the gamestate
	First it initializes the state, then it check to see if the action is valid.
	Next, execute the action performed in the string.
*/
int readActionFragment(const char *line, gamestate_t *state)
{
  int used, c, action, t;

  used = 0;
  initGameState(state);

  while(1) {
    c = line[used];

    if(c == ':') {
      ++used;
      break;
    } else if(c == '/') {

      if(state->dealing == NOT_DEALING) {
				return -1;
      }
      ++used;
      continue;
    }
		
    action = readAction(&line[used], &t);
    if(action < 0) {
      return -1;
    }
    used += t;
		
    while(state->dealing != NOT_DEALING) {
			int nc, *dest_cards;
			cardDealingPreparation(state, &dest_cards, &nc);
    }
		
		if(!stateCanDoAction(state, action)) {
      return -1;
    }
		
    doActionAtChoiceNode(state, action);
  }

  return used;
}

/*
	Checks to see if a state is allowed to perform a particular action
*/
int stateCanDoAction(const gamestate_t *state, const int action)
{
  int bet_size;

  if(action == ACTION_FOLD) {
    return (state->money_spent[state->player] < state->max_spent);
  } else if(action == ACTION_CALL) {
    return 1;
  } else if(action < 0 || action >= NUM_ACTIONS) {
    return 0;
  }
	
  if(state->raises[state->round] >= RAISES[state->round]) {
    return 0;
  }
  if(state->num_actions[state->round] + NUM_PLAYERS > NUM_ACTIONS) {
    return 0;
  }

	bet_size = BET_SIZES[state->round];
	
  return 1;
}

/*
	Read an action in from the hand string. (RCF are the possible actions)
*/
int readAction(const char *line, int *chars_consumed)
{
  int action, i;
	switch(line[0]) {
		case 'R':
		case 'r':
			action = ACTION_RAISE;
			break;
		case 'C':
		case 'c':
			action = ACTION_CALL;
			break;
		case 'F':
		case 'f':
			action = ACTION_FOLD;
			break;
	}
	
  i = 1;

  if(chars_consumed) {
    *chars_consumed = i;
  }
  return action;
}

/*
	Read in the cards from the hand string.
	First read in the player cards, then read in the board cards
*/
int readStateCardFragment(const char *line, gamestate_t *state)
{
	int used, i;
	
	used = 0;
	
  i = readStateHandFragment(&line[used], state);
  if(i < 0) {
    return -1;
  }
  used += i;

  if(line[used++] != '|') {
    return -1;
  }

  i = readBoardFragment(&line[used], state);
  if(i < 0) {
    return -1;
  }
  used += i;

  return used;
}

/*
	Read in the player cards from the given hand history string
	Update used cards in the gamestate
*/
int readStateHandFragment(const char *line, gamestate_t *state)
{
  int used, p, final;

  used = 0;
  final = NUM_PLAYERS;

  for(p = 0; p < NUM_PLAYERS; p++) {
    if(p) {
      if(line[used++] != ',') {
				return -1;
      }
    }
		
    if(p >= final) {			
      if(line[used++] != '?') {
				return -1;
      }
    } else if(stringToCards(&line[used], TOTAL_PLAYER_CARDS, state->player_cards[p]) != TOTAL_PLAYER_CARDS) {
      if(state->round != 0 || state->num_actions[0] != 0) {
				return -1;
      }
			
      final = p;
      p--;
    } else {
      int i;

      used += 2 * TOTAL_PLAYER_CARDS;
			
      for(i = 0; i < TOTAL_PLAYER_CARDS; i++) {
				if(state->cards_used[state->player_cards[p][i]]) {					
					return -1;
				}
				state->cards_used[state->player_cards[p][i]] = 1;
				state->num_unused_cards--;
      }
    }
  }
	
  while((state->dealing>=DEALING_P1) && (state->dealing-DEALING_P1 < final)) {
		int nc, *dest_cards;
    cardDealingPreparation(state, &dest_cards, &nc);
  }
	
  return used;
}

/*
	Read in the board cards from the hand.
	Update the used cards, update the state in which we are in for dealing.
*/
int readBoardFragment(const char *line, gamestate_t *state)
{
  int used, i, r, dealt;

  used = 0;
  dealt = 1;

  for(r = 0; r <= state->round; r++) {
    if(r) {
      if(line[used] != '/' && line[used] != ',') {
				return -1;
      }
      used++;
    }
		
    if(r == state->round && state->num_actions[r] == 0 && line[used] == '?') {
      used++;
      dealt = 0;
    } else if(stringToCards(&line[used], NUM_BOARD_CARDS[r], &state->board_cards[BOARD_CARDS_POSITION[r]]) != NUM_BOARD_CARDS[r]) {
      return -1;
    }

		used += 2 * NUM_BOARD_CARDS[r];
		
		for(i = 0; i < NUM_BOARD_CARDS[r]; i++) {
			if(state->cards_used[state->board_cards[BOARD_CARDS_POSITION[r] + i]]) {
				return -1;
			}
			state->cards_used[state->board_cards[BOARD_CARDS_POSITION[r] + i]] = 1;
			state->num_unused_cards--;
		}
	}
	
  if(dealt) {
    if(state->dealing >= DEALING_P1) {
      return -1;
    }
    if(state->dealing == DEALING_BOARD) {
			int nc, *dest_cards;
			cardDealingPreparation(state, &dest_cards, &nc);
    } else {
      if(state->num_actions[state->round] == 0) {
				return -1;
      }
    }
  }
	return used;
}

/*
	Calculate the value of a game over gamestate
	(1 player folded or a showdown)
*/
double valueOfGameState(const gamestate_t * state, int player)
{
	if(state->player_folded[player]) {   
		return -state->money_spent[player];
  }
	
  if(state->player_folded[player+1%NUM_PLAYERS]) {
		return (double)(state->pot_size - state->money_spent[player]);
	}
	
	int player_rank, opponent_rank;

	player_rank = rankHand(state->player_cards[player], TOTAL_PLAYER_CARDS, state->board_cards, TOTAL_BOARD_CARDS);
	opponent_rank = rankHand(state->player_cards[player+1%NUM_PLAYERS], TOTAL_PLAYER_CARDS, state->board_cards, TOTAL_BOARD_CARDS);

	if(player_rank < opponent_rank) {
		return -state->money_spent[player];
	} else if(player_rank > opponent_rank) {
		return (double)(state->pot_size - state->money_spent[player]);
	} else {
		return 0;//state->money_spent[player];
	}
}
