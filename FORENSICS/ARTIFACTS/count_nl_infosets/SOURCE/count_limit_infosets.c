/* count_limit_infosets.c
 * Mike Johanson, Feb 1, 02013
 *
 * A tool for counting the number of infosets and game states
 * in heads-up limit hold'em games and variants (like 2-1, 2-4, etc).
 * Much simpler than the NL counting program.
 */

/* C includes */
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <sys/time.h>
#include <signal.h>
#include <string.h>
#include <assert.h>

/* GNU MP library for arbitrary length integers */
#include <gmp.h>

/* count_infosets includes */
#include "constants.h"
#include "utility.h"

typedef struct {
  mpz_t infosets[ MAX_ROUNDS ];
  mpz_t infoset_actions[ MAX_ROUNDS ];
  mpz_t continuing[ MAX_ROUNDS ];
  mpz_t terminal[ MAX_ROUNDS ];
} limit_counts_t;


/* Global variables */
limit_counts_t *counts;
int rounds;
int bets;
int use_blinds; // 1 for blinds (small and big), 0 for ante (both the same)

void setup_counts()
{
  int r;
  for( r = 0; r < MAX_ROUNDS; r++ ) {
    mpz_init( counts->infosets[ r ] );
    mpz_init( counts->infoset_actions[ r ] );
    mpz_init( counts->continuing[ r ] );
    mpz_init( counts->terminal[ r ] );
  }

  for( r = 0; r < rounds; r++ ) {
    int round_bets = bets;
    if( ( r == 0 ) && ( bets > 1 ) ) {
      /* The ante/blinds counts as a bet, so there's one fewer
       * bet in the first round.  An exception is made for
       * games like [2-1] or [3-1] or Kuhn which only have one bet in the
       * first round, in which case one bet is allowed in addition
       * to the ante/blinds.
       */
      round_bets = bets - 1;
    }

    /* Continuing betting sequences: check-call, plus two per bet
     * ( rc and crc ), (rrc and crrc), etc.
     */
    if( r < rounds - 1 ) {
      if( r == 0 ) {
	mpz_set_si( counts->continuing[ r ],
		    1 + 2 * round_bets );
      } else {
	mpz_addmul_ui( counts->continuing[ r ], 
		       counts->continuing[ r - 1 ],
		       1 + 2 * round_bets );
      }
    }

    /* Terminal nodes.  First, count the ways to fold.
     * The small blind can fold preflop, giving one additional
     * terminal node compared to later rounds.
     */
    if( r == 0 ) {
      if( use_blinds ) {
	mpz_set_si( counts->terminal[ r ],
		    1 + 2 * round_bets );
      } else {
	mpz_set_si( counts->terminal[ r ],
		    2 * round_bets );
      }
    } else {
      mpz_addmul_ui( counts->terminal[ r ], 
		     counts->continuing[ r - 1 ],
		     2 * round_bets );
    }
    /* On the river, calls are also terminal nodes.
     * check-call, plus two per bet.
     */
    if( r == rounds - 1 ) {
      if( r == 0 ) {
	mpz_add_ui( counts->terminal[ r ], 
		    counts->terminal[ r ],
		    1 + 2 * round_bets );
      } else {
	mpz_addmul_ui( counts->terminal[ r ], 
		       counts->continuing[ r - 1 ],
		       1 + 2 * round_bets );
      }
    }
  }

  /* Infosets and infoset_actions.
   * We can compute this now that we've computed the continuing
   * sequences.  In each round, there are:
   * _, c, plus two per bet (r, cr), (rr, crr), etc.
   */
  for( r = 0; r < rounds; r++ ) {
    int round_bets = bets;
    if( ( r == 0 ) && ( bets > 1 ) ) {
      /* The ante/blinds counts as a bet, so there's one fewer
       * bet in the first round.  An exception is made for
       * games like [2-1] or [3-1] or Kuhn which only have one bet in the
       * first round, in which case one bet is allowed in addition
       * to the ante/blinds.
       */
      round_bets = bets - 1;
    }

    if( r == 0 ) {
      mpz_set_si( counts->infosets[ r ],
		  2 + 2 * round_bets );
      /* Actions in the round:
       * 3 (fold, call, raise) for the first action
       * 2 after a check (call, raise)
       * This leads to two betting sequences that get into raises:
       *   either it started with a check or not.
       * For all but the last bet, three actions are legal (fold, call, raise).
       * For the last bet, only two are legal (fold, call)
       */
      if( use_blinds ) {
	mpz_set_si( counts->infoset_actions[ r ],
		    3 + 2 + 2 * ( 3 * ( round_bets - 1 ) + 2 ) );
      } else {
	mpz_set_si( counts->infoset_actions[ r ],
		    2 + 2 + 2 * ( 3 * ( round_bets - 1 ) + 2 ) );
      }
    } else {
      mpz_addmul_ui( counts->infosets[ r ],
		     counts->continuing[ r - 1 ],
		     2 + 2 * round_bets );
      mpz_addmul_ui( counts->infoset_actions[ r ],
		     counts->continuing[ r - 1 ],
		     2 + 2 + 2 * ( 3 * ( round_bets - 1 ) + 2 ) );
    }
  }
}

void cleanup_counts()
{
  int r;
  for( r = 0; r < MAX_ROUNDS; r++ ) {
    mpz_clear( counts->infosets[ r ] );
    mpz_clear( counts->infoset_actions[ r ] );
    mpz_clear( counts->continuing[ r ] );
    mpz_clear( counts->terminal[ r ] );
  }
}

void print_limit_game_counts( card_counts_t *card_counts )
{
  /* Summed up over each round */
  mpz_t total_info, total_infoact, total_term;
  mpz_init( total_info );
  mpz_init( total_infoact );
  mpz_init( total_term );

  /* Used to compute numbers within each round */
  mpz_t info_with_cards, infoact_with_cards, cont_with_cards, term_with_cards;
  mpz_init( info_with_cards );
  mpz_init( infoact_with_cards );
  mpz_init( cont_with_cards );
  mpz_init( term_with_cards );


  printf( "Infosets, Canonical cards only:\n" );
  mpz_set_si( total_info, 0 );
  mpz_set_si( total_infoact, 0 );
  mpz_set_si( total_term, 0 );

  int r;
  for( r = 0; r < rounds; r++ ) {
    mpz_mul( info_with_cards, counts->infosets[ r ], card_counts->canonical_onesided[ r ] );
    mpz_mul( infoact_with_cards, counts->infoset_actions[ r ], card_counts->canonical_onesided[ r ] );
    mpz_mul( cont_with_cards, counts->continuing[ r ], card_counts->canonical_onesided[ r ] );
    mpz_mul( term_with_cards, counts->terminal[ r ], card_counts->canonical_onesided[ r ] );

    mpz_add( total_info, total_info, info_with_cards );
    mpz_add( total_infoact, total_infoact, infoact_with_cards );
    mpz_add( total_term, total_term, term_with_cards );

    printf( "  Round %d\n", r );
    print_round_stats( "Infoset",
                       &info_with_cards,
		       NULL,
                       &infoact_with_cards,
                       &cont_with_cards,
                       &term_with_cards );
  }

  printf( "  Total:\n" );
  print_round_stats( "Infoset",
                     &total_info,
		     NULL,
                     &total_infoact,
                     NULL,
                     &total_term );


  mpz_t strat_mem;
  mpz_t cfr_mem;
  mpz_init( strat_mem );
  mpz_init( cfr_mem );
  const char *units[ 9 ] = { "bytes", "kilobytes", "megabytes", "gigabytes", "terabytes", "petabytes", "exabytes", "zettabytes\
", "yottabytes" };

  mpz_mul_ui( cfr_mem, total_infoact, 2 * sizeof( double ) );

  mpz_t unit_cutoff;
  mpz_t unit_divisor;
  mpz_init( unit_cutoff );
  mpz_init( unit_divisor );
  mpz_set_si( unit_cutoff, 10000 );
  mpz_set_si( unit_divisor, 1 );

  int x = 0;
  do {
    if( mpz_cmp( total_infoact, unit_cutoff ) <= 0 ) {
      break;
    } else {
      mpz_mul_si( unit_cutoff, unit_cutoff, 1024 );
      mpz_mul_si( unit_divisor, unit_divisor, 1024 );
      x++;
    }
  } while( x < 8 );

  mpz_cdiv_q( strat_mem, total_infoact, unit_divisor );
  mpz_cdiv_q( cfr_mem, cfr_mem, unit_divisor );

  /* Assume strategy truncated down to use one char to represent                                                               
   * the probability of taking each action.                                                                                    
   */
  printf( "Memory required to store a strategy (one char per infoset-action): " );
  mpz_out_str( stdout, 10, strat_mem );
  printf( " %s\n", units[ x ] );

  /* Assume CFR is using two doubles per infoset-action.  This can                                                             
   * be done more efficiently using exotic variants like CFR-BR                                                                
   * (one variable per infoset action, and one player at a time)                                                               
   * or Oskari Tammelin's Pure CFR which uses integers.                                                                        
   */
  printf( "Memory required to solve with CFR (two double-precision floats per infoset-action): " );
  mpz_out_str( stdout, 10, cfr_mem );
  printf( " %s\n", units[ x ] );

  mpz_clear( strat_mem );
  mpz_clear( cfr_mem );
  printf( "\n" );
  printf( "\n" );
  printf( "Infosets, all cards:\n" );
  mpz_set_si( total_info, 0 );
  mpz_set_si( total_infoact, 0 );
  mpz_set_si( total_term, 0 );

  for( r = 0; r < rounds; r++ ) {
    mpz_mul( info_with_cards, counts->infosets[ r ], card_counts->onesided[ r ] );
    mpz_mul( infoact_with_cards, counts->infoset_actions[ r ], card_counts->onesided[ r ] );
    mpz_mul( cont_with_cards, counts->continuing[ r ], card_counts->onesided[ r ] );
    mpz_mul( term_with_cards, counts->terminal[ r ], card_counts->onesided[ r ] );

    mpz_add( total_info, total_info, info_with_cards );
    mpz_add( total_infoact, total_infoact, infoact_with_cards );
    mpz_add( total_term, total_term, term_with_cards );

    printf( "  Round %d\n", r );
    print_round_stats( "Infoset",
                       &info_with_cards,
		       NULL,
                       &infoact_with_cards,
                       &cont_with_cards,
                       &term_with_cards );
  }

  printf( "  Total:\n" );
  print_round_stats( "Infoset",
                     &total_info,
		     NULL,
                     &total_infoact,
                     NULL,
                     &total_term );

  printf( "\n" );
  printf( "\n" );
  printf( "Game states, unabstracted cards:\n" );
  mpz_set_si( total_info, 0 );
  mpz_set_si( total_infoact, 0 );
  mpz_set_si( total_term, 0 );
  for( r = 0; r < rounds; r++ ) {
    mpz_mul( info_with_cards, counts->infosets[ r ], card_counts->twosided[ r ] );
    mpz_mul( infoact_with_cards, counts->infoset_actions[ r ], card_counts->twosided[ r ] );
    mpz_mul( cont_with_cards, counts->continuing[ r ], card_counts->twosided[ r ] );
    mpz_mul( term_with_cards, counts->terminal[ r ], card_counts->twosided[ r ] );

    mpz_add( total_info, total_info, info_with_cards );
    mpz_add( total_infoact, total_infoact, infoact_with_cards );
    mpz_add( total_term, total_term, term_with_cards );
    printf( "  Round %d\n", r );
    print_round_stats( "State",
                       &info_with_cards,
		       NULL,
                       &infoact_with_cards,
                       &cont_with_cards,
                       &term_with_cards );
  }
  printf( "  Total:\n" );
  print_round_stats( "State",
                     &total_info,
		     NULL,
                     &total_infoact,
                     NULL,
                     &total_term );

}

int main( const int argc, const char *argv[] )
{
  if( argc < 3 ) {
    printf( "Usage: ./count_limit_infosets <rounds> <bets>\n" );
    printf( "Optional: --ante : use equal-sized antes instead of different sized blinds\n" );
    return 0;
  }

  rounds = atoi( argv[ 1 ] );
  bets = atoi( argv[ 2 ] );
  use_blinds = 1;
  int i;
  for( i = 3; i < argc; i++ ) {
    if( strcmp( argv[ i ], "--ante" ) == 0 ) {
      use_blinds = 0;
    } else {
      printf( "Unknown option [%s]\n", argv[ i ] );
      return 1;
    }
  }


  counts = ( limit_counts_t * ) malloc( sizeof( limit_counts_t ) );
  if( counts == NULL ) {
    printf( "Couldn't malloc limit_counts_t\n" );
    return 1;
  }

  setup_counts();
  
  init_card_counts();

  printf( "Betting sequences only (no cards):\n" );
  /* Summed up over each round */
  mpz_t total_info, total_infoact, total_term;
  mpz_init( total_info );
  mpz_init( total_infoact );
  mpz_init( total_term );

  int r;
  for( r = 0; r < rounds; r++ ) {
    
    printf( "  Round %d\n", r );
    print_round_stats( "Sequence",
		       &counts->infosets[ r ],
		       NULL,
                       &counts->infoset_actions[ r ],
                       &counts->continuing[ r ],
                       &counts->terminal[ r ] );

    mpz_add( total_info, total_info, counts->infosets[ r ] );
    mpz_add( total_infoact, total_infoact, counts->infoset_actions[ r ] );
    mpz_add( total_term, total_term, counts->terminal[ r ] );
  }

  printf( "  Total:\n" );
  print_round_stats( "Sequence",
                     &total_info,
		     NULL,
                     &total_infoact,
                     NULL,
                     &total_term );

  printf( "\n\n" );
  

  printf( "ROYAL HOLD'EM:\n" );
  print_limit_game_counts( &royal_counts );
  printf( "\n\n" );

  printf( "TEXAS HOLD'EM:\n" );
  print_limit_game_counts( &texas_counts );
  printf( "\n\n" );

  mpz_clear( total_info );
  mpz_clear( total_infoact );
  mpz_clear( total_term );

  cleanup_card_counts();

  cleanup_counts();

  return 0;
}
