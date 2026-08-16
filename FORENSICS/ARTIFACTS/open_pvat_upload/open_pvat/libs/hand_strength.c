/*
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.
	
	 This program is distributed in the hope that it will be useful,
	 but WITHOUT ANY WARRANTY; without even the implied warranty of
	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	 GNU General Public License for more details.
	 
	 You should have received a copy of the GNU General Public License
	 along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <stdlib.h>
#include <string.h>
#include "hand_strength.h"

#define DECK_SIZE 52
#define RANKS 13
#define TOTAL_BOARD_CARDS 5
#define TOTAL_PLAYER_CARDS 2
static const int SUM_BOARD_CARDS[ 4 ] = { 0, 3, 4, 5 };


static CardMask index_to_mask[DECK_SIZE];

static const int OPEN_NUM_CARD_COMBINATIONS[ 4 ]
[ DECK_SIZE + 1 ] = {
  { 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1 },
  { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
    19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
    36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52 },
  { 0, 0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120,
    136, 153, 171, 190, 210, 231, 253, 276, 300, 325, 351, 378, 406,
    435, 465, 496, 528, 561, 595, 630, 666, 703, 741, 780, 820, 861,
    903, 946, 990, 1035, 1081, 1128, 1176, 1225, 1275, 1326 },
  { 0, 0, 0, 1, 4, 10, 20, 35, 56, 84, 120, 165, 220, 286, 364, 455,
    560, 680, 816, 969, 1140, 1330, 1540, 1771, 2024, 2300, 2600, 2925,
    3276, 3654, 4060, 4495, 4960, 5456, 5984, 6545, 7140, 7770, 8436,
    9139, 9880, 10660, 11480, 12341, 13244, 14190, 15180, 16215, 17296,
    18424, 19600, 20825, 22100 } };

/* group_size must be <= MAX_UNFIXED_BOARD_CARDS */
static uint64_t numCardCombinations(int remaining_cards, int group_size)
{
  if(remaining_cards <= DECK_SIZE && group_size <= 3) {
    return (uint64_t)OPEN_NUM_CARD_COMBINATIONS[group_size][remaining_cards];
  } else {
    uint64_t ncc;
    int i;
		
    ncc = 1;
    for(i = 0; i < group_size; i++) {
      ncc *= remaining_cards - i;
    }
    for(i = 2; i <= group_size; i++) {
      ncc /= i;
    }
		
    return ncc;
  }
}


/* generate first hand with num_cards cards in the deck
   that currently has { x | used[x] == 1 } cards used */
static void firstCardGroup(int *cards, int num_cards, char *used)
{
  int i, start;
	
  for(start = 0, i = 0; i < num_cards; start = cards[i] + 1, i++) {
    cards[i] = start;
		while(used[cards[i]]) {
			cards[i]++;
		}
    used[cards[i]] = 1;
  }
}

/* returns 1 if there is a next card group
   returns 0 if current cards were the last group

   NOTE: used must be at least deck_size+1 wide, with used[deck_size] = 0 */
static int nextCardGroup(int *cards, int num_cards, char *used, int deck_size)
{
  int i, j;

  /* increment a card */
  i = num_cards;
  while(i-- > 0) {
    used[cards[i]] = 0;
    while(used[++cards[i]]);
    if(cards[i] < deck_size) {
      /* this card looks like it can be incremented - try it out */
			
      /* generate some cards after the one we just incremented */
      for(j = i + 1; j < num_cards; j++) {
				cards[j] = cards[j - 1]; while(used[++cards[j]]);
				if(cards[j] == deck_size) {
					/* we've run out of deck... */
					goto fail;
				}
      }
			
      /* successful increment - mark the cards as used and return */
      for(j = i; j < num_cards; j++) {
				used[cards[j]] = 1;
      }
      return 1;
			
    fail:
      0; /* ^@%# gcc >= 3.3 requires a statement... */
    }
  }
	
  /* no cards left to increment - this is the last group */
  return 0;
}


static void initIndexToMask(int suits)
{
  int i, rank, suit, t;

  for(i = 0; i < suits * RANKS; i++) {
    rank = i / suits;
    suit = i % suits;
    t = StdDeck_MAKE_CARD(rank, suit);
    index_to_mask[i] = StdDeck_MASK(t);
  }
}


/* find the all in equity for a pair of player hands */
void handEquities(int *pc[2], int player_folded[2], int *bc, int round, double equities_ret[2])
{
  int p, i, ranks[2], new_bc[TOTAL_BOARD_CARDS];
  char used[DECK_SIZE + 1];
  double p0_eq;
  CardMask hands[2], new_board, t;

	initIndexToMask(4);

  /* start with an empty deck */
  memset(used, 0, DECK_SIZE + 1);

  /* handle the fold case */
  if(player_folded[0]) {
    equities_ret[0] = 0.0;
    equities_ret[1] = 1.0;
    return;
  } else if(player_folded[1]) {
    equities_ret[1] = 0.0;
    equities_ret[0] = 1.0;
    return;
  }

  /* get ready for rollout */
  CardMask_RESET(t);
  for(i = 0; i < SUM_BOARD_CARDS[round]; ++i) {
    used[bc[i]] = 1;
    CardMask_OR(t, t, index_to_mask[bc[i]]);
  }
  p0_eq = 0.0;
  for(p = 0; p < 2; ++p) {
    hands[p] = t;
    for(i = 0; i < TOTAL_PLAYER_CARDS; ++i) {
      used[pc[p][i]] = 1;
      CardMask_OR(hands[p], hands[p], index_to_mask[pc[p][i]]);
      }
  }
	/*CHANGED ARRAY INDEXING, LOOK AT TOMORROW */
  firstCardGroup(&new_bc[SUM_BOARD_CARDS[round]], TOTAL_BOARD_CARDS - SUM_BOARD_CARDS[round], used);
  do {
    /* board cards rolled out */
    CardMask_RESET(new_board);
    for(i = SUM_BOARD_CARDS[round]; i < TOTAL_BOARD_CARDS; i++) {
      CardMask_OR(new_board, new_board, index_to_mask[new_bc[i]]);
    }

    /* get hand ranks */
    CardMask_OR(t, hands[0], new_board);
    ranks[0] = Hand_EVAL_N(t, TOTAL_PLAYER_CARDS + TOTAL_BOARD_CARDS);
    CardMask_OR(t, hands[1], new_board);
    ranks[1] = Hand_EVAL_N(t, TOTAL_PLAYER_CARDS + TOTAL_BOARD_CARDS);
    if(ranks[0] == ranks[1]) {
      p0_eq += 0.5;
    } else if(ranks[0] > ranks[1]) {
      p0_eq += 1.0;
    }
  } while(nextCardGroup(&new_bc[SUM_BOARD_CARDS[round]], TOTAL_BOARD_CARDS - SUM_BOARD_CARDS[round], used, DECK_SIZE));

  /* normalise and return */
  p0_eq /= (double) numCardCombinations(DECK_SIZE - TOTAL_PLAYER_CARDS * 2 - SUM_BOARD_CARDS[round], TOTAL_BOARD_CARDS - SUM_BOARD_CARDS[round]);
  equities_ret[0] = p0_eq;
  equities_ret[1] = 1.0 - p0_eq;
}

/* compute a value for a hand - greater value is the winning hand */
int rankHand( const int *pc, const int num_pc, const int *bc, const int num_bc )
{
  int i;
  CardMask eval_cards;

  CardMask_RESET( eval_cards );
  for( i = 0; i < num_pc; i++ ) {
    CardMask_OR( eval_cards, eval_cards, index_to_mask[ pc[ i ] ] );
  }
  for( i = 0; i < num_bc; i++ ) {
    CardMask_OR( eval_cards, eval_cards, index_to_mask[ bc[ i ] ] );
  }

  return Hand_EVAL_N( eval_cards, num_pc + num_bc );
}
