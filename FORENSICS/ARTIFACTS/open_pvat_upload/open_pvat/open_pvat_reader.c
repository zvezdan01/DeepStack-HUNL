/*
	Author: Josh Davidson
	Purpose: See open_pvat.h
*/

#include "open_pvat_reader.h"

//const int BLINDS[NUM_PLAYERS];
//const int BET_SIZES[NUM_ROUNDS];
//const int RAISES[NUM_ROUNDS];
//const int PLAYER_ORDER[NUM_ROUNDS];
//const int BOARD_CARDS_POSITION[NUM_ROUNDS];
//const int NUM_BOARD_CARDS[NUM_ROUNDS];
const int SUM_BOARD_CARDS[NUM_ROUNDS];
const char ACTION_CHAR_TABLE[3];


/*
	Get a line from the hand_history FILE convert it into a pvat_input hand.
	If the hand is bad, add	to the counter of bad hands, otherwise return 1 as
	to continue parsing hands from open_pvat.c
*/
int readHandHistory(FILE* hand_history, pvat_input* hand)
{
	char buffer[BUFFER_SIZE];
	int bad_hands;

	while(1) {
		if(fgets(buffer,BUFFER_SIZE, hand_history) == NULL) {
			return 0;
		}

		if(readDealerHandHistory(buffer, hand) > 0 && checkHand(hand) ) {
			return 1;
		} else {
			bad_hands++;
		}
	}
	return 0;
}

/*
	Reads in a line from the hand histroy file and converts it to gamestate, then
	back into a a pvat hand.	If the hand is of bad format, return -1.
*/
int readDealerHandHistory(char* buffer, pvat_input* hand)
{
	char* token;
	char* buffer_position;
	gamestate_t gamestate;
	int used, new_used, i;

	token = strtok_r(buffer, ":", &buffer_position);
	hand->hand_number = atoi(token);
	hand->num_players = NUM_PLAYERS;
	
	for(i=0; i<NUM_PLAYERS; i++) {
		token = strtok_r(NULL, ",:", &buffer_position);
    if (token == NULL) {
			fprintf(stderr, "Error reading player names\n");
      return -1;
    }
    strncpy( hand->player_names[i], token, strlen(token));
    hand->player_names[i][strlen(token)] = '\0';
  }

  token = strtok_r( NULL, "\n", &buffer_position );
	
  if((used = readGameState(token, &gamestate)) < 0) {
		fprintf(stderr, "Error reading gamestate %d\n",hand->hand_number);
		return -1;
	}
	
  convertGameState(&gamestate, hand);
	
  if (token[used] == ':')
    used++; //jump over the colon symbol
  for (i=0; i<NUM_PLAYERS; i++)
  {
    if (token[used] == ',')
      used++;
    sscanf( &(token[used]), "%lf%n", &(hand->net_win[i]), &new_used );
    used += new_used;
    hand->net_win[i] /= MIN_BET_SIZE;
  }
	
  return 1;
}

/*
	Check the hand for errors such as missing players, duplicate cards, missing cards, etc.
	(Any irregularities that might set off pvat)
*/
int checkHand(pvat_input* hand)
{
	int used_cards[DECK_SIZE];
	int current_card, i, j;

	memset(used_cards,0,sizeof(int)*DECK_SIZE);

	if(hand->num_players != NUM_PLAYERS) {
		return -1;
	}

	for(i=0; i<NUM_PLAYERS; i++) {
		for(j=0; j<NUM_PRIVATE_CARDS ;j++) {
			current_card = hand->pocket_cards[i][j];
			if(current_card < 0 ||  current_card >= DECK_SIZE || used_cards[current_card] != 0) {
				return -1;
			}
			used_cards[current_card] = 1;
		}
	}

	if(hand->num_board_cards != 0 && hand->num_board_cards != 3 && hand->num_board_cards != 4
		&& hand->num_board_cards != 5) {
		return -1;
	}
	for(i=0; i<hand->num_board_cards; i++) {
		current_card = hand->board_cards[i];
		if(current_card < 0 ||  current_card >= DECK_SIZE || used_cards[current_card] != 0) {
			return -1;
		}
		used_cards[current_card] = 1;
	}
	return 1;
}

/*
	Convert gamestate information into pvat hand information
*/
void convertGameState(const gamestate_t* gamestate, pvat_input* hand)
{
	int i,j;
	
	strncpy(hand->bet_sequence,"sB",2);
	hand->bet_sequence[2] = '\0';
	for(i=0; i<=gamestate->round; i++) {
		int raised;
		char c[2] = " ";
		raised = (i==0) ? 1:0;

		if(i) {
			strcat(hand->bet_sequence,"/");
		}

		for(j=0; j<gamestate->num_actions[i]; j++) {
			c[0] = ACTION_CHAR_TABLE[gamestate->actions[i][j]];
			strcat(hand->bet_sequence, c);
			if(gamestate->actions[i][j] == ACTION_RAISE) {
				raised = 1;
			}
		}
	}

	if(hand->bet_sequence[strlen(hand->bet_sequence)-1] != '/') {
		strcat(hand->bet_sequence,"/");
	}
	
	for(i=0; i<NUM_PLAYERS;i++) {
		for(j=0; j<NUM_PRIVATE_CARDS; j++) {
			hand->pocket_cards[i][j] = gamestate->player_cards[i][j];
		}
	}
	
	for(i=0; i<SUM_BOARD_CARDS[gamestate->round]; i++) {
		hand->board_cards[i] = gamestate->board_cards[i];
	}
	
	hand->num_board_cards = SUM_BOARD_CARDS[gamestate->round];
}
			
