#include "open_pvat.h"

const char *rank_names = "23456789TJQKA";
const char *suit_names = "shdc";


void printUsage()
{
  fprintf(stderr,"Usage: ./open_pvat hand_history\n");
}

void printCard(FILE *file, const int card, const int suits)
{
  fprintf(file, "%c%c", rank_names[card/suits], suit_names[card % suits]);
}

void printCards(FILE *file, const int num_cards, const int *cards, const int suits)
{
  int i;

  for(i = 0; i <= num_cards; ++i ) {
    printCard(file, cards[i], suits);
  }
}


void parseArgs(int argc, char** argv, pvat_parameters* params )
{
	
  if(argc < 2) {
		printUsage();
		exit(-1);
	}

	params->hand_history_file = argv[1];

	/*Setup Defaults*/
  params->suffix[0] = '\0';
  params->policy = ALWAYS_CALL;
  params->sample_num = 1;
	
}

void singleRound(pvat_parameters* params, gamestate_t* gamestate, int round, char* bet_sequence, pvat_results* results )
{
	double baseline_result, actual_result, difference;
	int i, char_constant = 1;
	gamestate_t tmp_gamestate;
	
	if(DEBUG) {
		fprintf(stderr, "Baseline Sequence = %s\nActual Sequence = %s\n",getBaseline(gamestate, params->policy), bet_sequence);
	}
	baseline_result = rollout(gamestate, params->policy);
	
	memcpy(&tmp_gamestate, gamestate, sizeof(gamestate_t));
	
	for(i=0; i<strlen(bet_sequence); i+=char_constant) {
		doActionAtChoiceNode(gamestate, readAction(&(bet_sequence[i]), &char_constant));
	}
	actual_result = rollout(gamestate, params->policy);
	
	memcpy(gamestate, &tmp_gamestate, sizeof(gamestate_t));
	
	difference = actual_result - baseline_result;
	
	results->temp_difference[0][round] = difference;
	results->temp_difference[1][round] = -difference;
	results->temp_difference[0][NUM_ROUNDS] += difference;
	results->temp_difference[1][NUM_ROUNDS] += -difference;

	if(DEBUG) {
		fprintf(stderr, "\tActual: %lf \n\tBaseline: %lf\n", actual_result, baseline_result );
		fprintf(stderr, "\tDifference for player 1: %lf\n", difference);
	}
}

void calculatePVATResults(pvat_parameters* params, pvat_input* hand, pvat_results* results)
{
	gamestate_t gamestate;
	char* betstring_token;
	char* tmp;
	int round, i, char_constant = 1;
	char betstring_copy[MAX_BET_STRING_LENGTH];

	strncpy(betstring_copy, hand->bet_sequence, MAX_BET_STRING_LENGTH);

	memset(results->temp_difference[0], 0, sizeof(double)*(NUM_ROUNDS+1) );
  memset(results->temp_difference[1], 0, sizeof(double)*(NUM_ROUNDS+1) );
	
  initGameState(&gamestate);
	
	if(DEBUG) {
		fprintf(stderr, "----------\nStarting hand: %d\nBet String; %s\n", hand->hand_number, betstring_copy);
		fprintf(stderr, "Dealing hole cards:");
	}

	for(i=0; i<NUM_PLAYERS; i++) {
		doDealCards(&gamestate, hand->pocket_cards[i], NUM_PRIVATE_CARDS);
		if(DEBUG) {
			fprintf(stderr, "\t%d:%s: ", i+1, hand->player_names[i]);
			printCards(stderr,NUM_PRIVATE_CARDS, gamestate.player_cards[i],SUITS);
		}
	}
	
	if(DEBUG) {
		fprintf(stderr, "\n");
	}
	
	doDealCards(&gamestate, NULL, 0);

	betstring_token = strtok_r(betstring_copy, "/", &tmp);
	for(round = 0; round<NUM_ROUNDS; round++) {
		if(round == 0) {
			singleRound(params, &gamestate, round, &(betstring_token[2]), results);
		} else {
			singleRound(params, &gamestate, round, betstring_token, results);
		}
		
		for(i=(round==0)?2:0; i<strlen(betstring_token); i+=char_constant) {
      doActionAtChoiceNode(&gamestate, readAction(&(betstring_token[i]), &char_constant) );
    }

		betstring_token = strtok_r(NULL, "/", &tmp);
		if(betstring_token ==NULL) {
			break;
		}

		if(round+1 < NUM_ROUNDS) {
			doDealCards(&gamestate, &(hand->board_cards[SUM_BOARD_CARDS[round]]),
				NUM_BOARD_CARDS[round+1] );
			if(DEBUG) {
				fprintf(stderr, "Dealing board card(s):" );
				printCards(stderr, SUM_BOARD_CARDS[round+1], gamestate.board_cards, SUITS );
				fprintf(stderr, "\n" );
			}
		}
	}
}

int createGraphFile(pvat_parameters* params, char* name, pvat_summary* summary)
{
	char filename[PATH_MAX];
	int index = summary->num_players;

  filename[0] = '\0';
  strcat(filename, "graphs/" );
  strcat(filename, name );
  strcat(filename, params->suffix );
  strcat(filename, ".graph" );

  summary->graph_files[index] = fopen(filename, "w" );
	summary->hand_count[index] = 0;
  assert(summary->graph_files[index] != NULL );
	summary->num_players++;
	summary->bankroll[index] = 0.0;

	
  memset(summary->difference[index], 0, sizeof(double)*(NUM_ROUNDS+1) );

  fprintf(summary->graph_files[index], "#           HandID     MONEY     DDiff     Dpref     Dflop     Dturn    Driver\n" );
  fprintf(summary->graph_files[index], "%6d  %10d  %8.3lf  %8.3lf  %8.3lf  %8.3lf  %8.3lf  %8.3lf\n", 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 );

	strcpy(summary->player_names[index], name);
  return index;
}


void postProcess(pvat_parameters* params, pvat_results* results, pvat_summary* summary)
{
	int i,j,bet_value, index;
	
	for(i=0;i<2;i++) {
		index = -1;
		for(j=0;j<summary->num_players;j++) {
			if(strcmp(results->player_names[i], summary->player_names[j]) == 0) {
				index = j;
			}
		}

		if(index < 0) {
			index = createGraphFile(params, results->player_names[i], summary);
		}

		summary->hand_count[index]++;
		summary->bankroll[index]+= results->bankroll[i];

		for(j=0;j<NUM_ROUNDS;j++) {
			bet_value = MIN_BET_SIZE;
			if(bet_value <= 0) {
				bet_value = 1;
			}
			summary->difference[index][j+1] += results->difference[i][j] / bet_value;
			summary->difference[index][0] += results->difference[i][j] / bet_value;
		}
		printResults(summary, index, results->hand_number);
	}
}


void printResults(pvat_summary* summary, int index, int hand_number)
{
	int j;

	fprintf(summary->graph_files[index], "%6d", summary->hand_count[index] );
	fprintf(summary->graph_files[index], "  %10d", hand_number );
	fprintf(summary->graph_files[index], "  %8.3lf", summary->bankroll[index] );
	
	for (j=0; j<NUM_ROUNDS+1; j++) {
		fprintf(summary->graph_files[index], "  %8.3lf", summary->difference[index][j] );
	}
	
	fprintf(summary->graph_files[index], "\n" );
}



void cleanup(pvat_summary* summary)
{
	int i;
	for(i=0;i<summary->num_players; i++) {
		fclose(summary->graph_files[i]);
	}
}

void run(pvat_parameters* params)
{
	FILE* hand_history;
	time_t start_time;
	pvat_results results;
	pvat_input hand;
	pvat_summary summary;
	int i,j;
	
	summary.num_players = 0;

	if((hand_history = fopen(params->hand_history_file, "r")) == NULL) {
		fprintf(stderr,"Could not open hand history file [%s]\n", params->hand_history_file);
		exit(-1);
	}

	start_time = time(0);

	while(readHandHistory(hand_history, &hand)) {
		
		memset(results.difference[0], 0, sizeof(double)*NUM_ROUNDS);
		memset(results.difference[1], 0, sizeof(double)*NUM_ROUNDS);

		results.player_names[0] = hand.player_names[0];
		results.player_names[1] = hand.player_names[1];

		results.bankroll[0] = hand.net_win[0];
		results.bankroll[1] = hand.net_win[1];

		results.hand_number = hand.hand_number;
		
		for(i=0; i<params->sample_num; i++) {
			memset(results.temp_difference[0], 0, sizeof(double)*NUM_ROUNDS);
			memset(results.temp_difference[1], 0, sizeof(double)*NUM_ROUNDS);
			
			calculatePVATResults(params,&hand,&results);
			for(j=0; j<=NUM_ROUNDS; j++) {
				results.difference [0][j] += results.temp_difference[0][j]/params->sample_num;
				results.difference [1][j] += results.temp_difference[1][j]/params->sample_num;
			}
		}
		postProcess(params, &results, &summary);
	}
	fclose(hand_history);
	cleanup(&summary);
	fprintf(stdout, "Total time = %d\n", (int)(time(0)-start_time));
}

int main(int argc, char** argv)
{
  pvat_parameters params;
	parseArgs(argc, argv, &params);
	initializeUtils(params.policy);
	run(&params);
  return 0;
}
