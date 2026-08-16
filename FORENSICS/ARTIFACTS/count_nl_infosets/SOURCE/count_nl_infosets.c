/* count_nl_infosets.c
 * Mike Johanson, Feb 1, 02013
 * 
 * A tool for counting the number of infosets and game states
 * in heads-up no-limit hold'em games with varying numbers of
 * rounds, stack sizes, and blinds.
 *
 * Uses a dynamic programming style trick to make the
 * computation fast and avoid redundant tree walks.
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

/* Max stack size, in dollars */
#define MAX_STACK 20000

/* counts_t: datastructure for holding the working array
 * that counts how many ways we can reach each (stack size),(bet faced)
 * situation.
 */
typedef struct {
  /* check_reaching and histories_reaching are temporary memory used
   * within the current round.
   */

  /* Indexed by current stack size */
  mpz_t check_reaching[ MAX_STACK + 1 ];
  /* indexed by current stack size, bet-faced */
  mpz_t histories_reaching[ MAX_STACK + 1 ][ MAX_STACK + 1 ];

  /* start_of_round_reach tracks how many ways there are to
   * reach the start of each round with a given stack size.
   */

  /* indexed by round, cur-stack */
  mpz_t start_of_round_reach[ MAX_ROUNDS + 1 ][ MAX_STACK + 1 ];

  /* Output variables.  Count up how many choice points (not counting cards)
   * there are in each round, how many betting sequences leave each round, and
   * how many terminal nodes there are in each round.
   */

  /* Number of times it's someone's turn */
  mpz_t infosets[ MAX_ROUNDS ];
  /* Number of times it's someone's turn and they have more than one action.
   * If it's forced (both players are already all-in, for example)
   * then it's technically a state/infoset but doesn't impact the difficulty of
   * solving the game.
   */
  mpz_t nontrivial_infosets[ MAX_ROUNDS ];
  /* For each infoset with more than one legal action, sum up the number of actions.
   * This tells us how much memory it would take to write down a strategy, since
   *   for a behavioral strategy, it takes one variable (typically a double, but can be
   *   coarsened to a char) per infoset-action to record the probability of taking
   *   that action.
   * Also tells us how much memory (typically RAM, but Eric Jackson's Slumbot does 
   *   it with disk) CFR would require to solve a game.  Two doubles per infoset-action.
   *   Oskari's PureCFR does it with ints instead of doubles.
   */
  mpz_t infoset_actions[ MAX_ROUNDS ];
  /* Number of betting sequences that continue on to the next round. */
  mpz_t continuing[ MAX_ROUNDS ];
  /* Number of terminal nodes in each round.  Before the final round,
   * this is just the number of ways that someone can fold.  On the
   * final round, this counts both folds and showdowns.
   */
  mpz_t terminal[ MAX_ROUNDS ];
} nolimit_counts_t;

/* Global variabless */

/* rounds - given on command line.  Number of rounds in the game. */
int rounds;
/* bigblind and smallblind - given on command line.  size of the big blind, in dollars.  
 * Must be integers.
 */
int bigblind, smallblind;
/* starting_stack - given on the command line.  size of each player's 
 * stack size, in dollars. 
 */
int starting_stack;

/* counts - stores working memory and final result. */
nolimit_counts_t *counts;

/* for() loop iterators.  Global, so that the spammy output alarm
 * can peek at their state.
 * r - round, s - stack_remaining, f - bet_faced
 */
int r, s, f;

/* Alarm handler for output messages.
 * Whenever SIGALRM goes off, print out current round, stack, and bet faced.
 */
void sig_handler( int sig )
{
  if( sig == SIGALRM ) {
    printf( "R%d S%d F%d\n", r, s, f );
    fflush( stdout );
  }
}

/* One of two main update functions.  This one handles the first action
 * in a round, when we're allowed to check.
 * For a given round, stack size, and bet faced,
 * look up the current number of betting sequences that reach this point,
 * which has already been computed and is stored in working memory.
 * For each child state, defined by (stack)x(bet faced), update the child's
 * table entry by incrementing it by the number of ways to get to this state.
 */
void push_check( int round, int stack, int faced ) {

  int a; /* action iterator */
  unsigned int num_actions = 0;

  /* Increment the number of infosets */
  mpz_add( counts->infosets[ round ], 
	   counts->infosets[ round ], 
	   counts->check_reaching[ stack ] );
  
  /* If we're facing a bet, we're allowed to fold.
   * Only happens in the preflop, when we can both fold or call the small blind
   * to check.
   */
  if( faced > 0 ) {
    mpz_add( counts->terminal[ round ], 
	     counts->terminal[ round ], 
	     counts->check_reaching[ stack ] );
    num_actions++;
  }

  /* Checks */	
  assert( stack >= faced );
  mpz_add( counts->histories_reaching[ stack - faced ][ 0 ], 
	   counts->histories_reaching[ stack - faced ][ 0 ], 
	   counts->check_reaching[ stack ] );
  num_actions++;

  /* Loop over all legal actions */
  int min_bet = bigblind;
  if( faced > min_bet ) {
    min_bet = faced;
  }
  if( stack - faced < min_bet ) {
    min_bet = stack - faced;
  }

  if( min_bet > 0 ) {
    for( a = min_bet; a <= stack - faced; a++ ) {
      mpz_add( counts->histories_reaching[ stack - faced ][ a ],
	       counts->histories_reaching[ stack - faced ][ a ],
	       counts->check_reaching[ stack ] );
      num_actions++;
    }
  }

  /* Player is always allowed to check/call.  Can't have a dead end with zero actions. */
  assert( num_actions > 0 );
  if( num_actions > 1 ) {
    /* If a player has only one action, we wouldn't have to allocate memory
     * for their strategy at this infoset.  It's a forced move.
     */
    mpz_addmul_ui( counts->infoset_actions[ round ], 
		   counts->check_reaching[ stack ],
		   num_actions );

    /* Also increase the number of nontrivial infosets. */
    mpz_add( counts->nontrivial_infosets[ round ], 
	     counts->nontrivial_infosets[ round ], 
	     counts->check_reaching[ stack ] );
  }
}

void push( int round, int stack, int faced ) {
  int a;

  unsigned int num_actions = 0;

  mpz_add( counts->infosets[ round ],
	   counts->infosets[ round ],
	   counts->histories_reaching[ stack ][ faced ] );
  
  /* Folds */
  if( faced > 0 ) {
    mpz_add( counts->terminal[ round ],
	     counts->terminal[ round ],
	     counts->histories_reaching[ stack ][ faced ] );
    num_actions++;
  }

  /* Call to the next round */
  mpz_add( counts->start_of_round_reach[ round + 1 ][ stack - faced ],
	   counts->start_of_round_reach[ round + 1 ][ stack - faced ],
	   counts->histories_reaching[ stack ][ faced ] );
  num_actions++;

  if( round < rounds - 1 ) {
    mpz_add( counts->continuing[ round ],
	     counts->continuing[ round ],
	     counts->histories_reaching[ stack ][ faced ] );
  } else {
    /* Call to showdown */
    mpz_add( counts->terminal[ round ],
	     counts->terminal[ round ],
	     counts->histories_reaching[ stack ][ faced ] );
  }
  
  /* Loop over all legal actions */
  int min_bet = bigblind;
  if( faced > min_bet ) {
    min_bet = faced;
  }
  if( stack - faced < min_bet ) {
    min_bet = stack - faced;
  }

  if( min_bet > 0 ) {
    for( a = min_bet; a <= stack - faced; a++ ) {
      mpz_add( counts->histories_reaching[ stack - faced ][ a ],
	       counts->histories_reaching[ stack - faced ][ a ],
	       counts->histories_reaching[ stack ][ faced ] );
      num_actions++;
    }
  }

  assert( num_actions > 0 );
  if( num_actions > 1 ) {
    mpz_addmul_ui( counts->infoset_actions[ round ],
		   counts->histories_reaching[ stack ][ faced ],
		   num_actions );
    
    mpz_add( counts->nontrivial_infosets[ round ],
	     counts->nontrivial_infosets[ round ],
	     counts->histories_reaching[ stack ][ faced ] );
  }
}

void print_time( FILE *stdout, int seconds )
{
  int days = ( seconds / 86400 );
  seconds -= days * 86400;
  if( days ) {
    fprintf( stdout, "%dd", days );
  }
  int hours = ( seconds / 3600 );
  seconds -= ( hours * 3600 );
  if( days || hours ) {
    fprintf( stdout, "%2dh", hours );
  }
  int minutes = ( seconds / 60 );
  seconds -= ( minutes * 60 );
  if( days || hours || minutes ) {
    fprintf( stdout, "%2dm", minutes );
  }
  fprintf( stdout, "%2ds", seconds );
}

void print_game_counts( card_counts_t *card_counts )
{
  /* Summed up over each round */
  mpz_t total_info, total_nt_info, total_infoact, total_term;
  mpz_init( total_info );
  mpz_init( total_nt_info );
  mpz_init( total_infoact );
  mpz_init( total_term );

  /* Used to compute numbers within each round */
  mpz_t info_with_cards, nt_info_with_cards, infoact_with_cards, cont_with_cards, term_with_cards;
  mpz_init( info_with_cards );
  mpz_init( nt_info_with_cards );
  mpz_init( infoact_with_cards );
  mpz_init( cont_with_cards );
  mpz_init( term_with_cards );


  printf( "Infosets, Canonical cards only:\n" );
  mpz_set_si( total_info, 0 );
  mpz_set_si( total_nt_info, 0 );
  mpz_set_si( total_infoact, 0 );
  mpz_set_si( total_term, 0 );

  for( r = 0; r < rounds; r++ ) {
    mpz_mul( info_with_cards, counts->infosets[ r ], card_counts->canonical_onesided[ r ] );
    mpz_mul( nt_info_with_cards, counts->nontrivial_infosets[ r ], card_counts->canonical_onesided[ r ] );
    mpz_mul( infoact_with_cards, counts->infoset_actions[ r ], card_counts->canonical_onesided[ r ] );
    mpz_mul( cont_with_cards, counts->continuing[ r ], card_counts->canonical_onesided[ r ] );
    mpz_mul( term_with_cards, counts->terminal[ r ], card_counts->canonical_onesided[ r ] );

    mpz_add( total_info, total_info, info_with_cards );
    mpz_add( total_nt_info, total_nt_info, nt_info_with_cards );
    mpz_add( total_infoact, total_infoact, infoact_with_cards );
    mpz_add( total_term, total_term, term_with_cards );

    printf( "  Round %d\n", r );
    print_round_stats( "Infoset",
		       &info_with_cards, 
		       &nt_info_with_cards, 
		       &infoact_with_cards, 
		       &cont_with_cards, 
		       &term_with_cards );
  }

  printf( "  Total:\n" );
  print_round_stats( "Infoset", 
		     &total_info, 
		     &total_nt_info,
		     &total_infoact, 
		     NULL, 
		     &total_term );

  mpz_t strat_mem;
  mpz_t cfr_mem;
  mpz_init( strat_mem );
  mpz_init( cfr_mem );
  const char *units[ 9 ] = { "bytes", "kilobytes", "megabytes", "gigabytes", "terabytes", "petabytes", "exabytes", "zettabytes", "yottabytes" };
  
  mpz_mul_ui( cfr_mem, total_infoact, 2 * sizeof( double ) );

  mpz_t unit_cutoff;
  mpz_t unit_divisor;
  mpz_init( unit_cutoff );
  mpz_init( unit_divisor );
  mpz_set_si( unit_cutoff, 10 );
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
  mpz_set_si( total_nt_info, 0 );
  mpz_set_si( total_infoact, 0 );
  mpz_set_si( total_term, 0 );
  
  for( r = 0; r < rounds; r++ ) {
    mpz_mul( info_with_cards, counts->infosets[ r ], card_counts->onesided[ r ] );
    mpz_mul( nt_info_with_cards, counts->nontrivial_infosets[ r ], card_counts->onesided[ r ] );
    mpz_mul( infoact_with_cards, counts->infoset_actions[ r ], card_counts->onesided[ r ] );
    mpz_mul( cont_with_cards, counts->continuing[ r ], card_counts->onesided[ r ] );
    mpz_mul( term_with_cards, counts->terminal[ r ], card_counts->onesided[ r ] );

    mpz_add( total_info, total_info, info_with_cards );
    mpz_add( total_nt_info, total_nt_info, nt_info_with_cards );
    mpz_add( total_infoact, total_infoact, infoact_with_cards );
    mpz_add( total_term, total_term, term_with_cards );

    printf( "  Round %d\n", r );
    print_round_stats( "Infoset",
		       &info_with_cards, 
		       &nt_info_with_cards,
		       &infoact_with_cards, 
		       &cont_with_cards, 
		       &term_with_cards );
  }
  printf( "  Total:\n" );
  print_round_stats( "Infoset",
		     &total_info, 
		     &total_nt_info,
		     &total_infoact, 
		     NULL, 
		     &total_term );

  printf( "\n" );
  printf( "\n" );
  printf( "Game states, unabstracted cards:\n" );
  mpz_set_si( total_info, 0 );
  mpz_set_si( total_nt_info, 0 );
  mpz_set_si( total_infoact, 0 );
  mpz_set_si( total_term, 0 );
  for( r = 0; r < rounds; r++ ) {
    mpz_mul( info_with_cards, counts->infosets[ r ], card_counts->twosided[ r ] );
    mpz_mul( nt_info_with_cards, counts->nontrivial_infosets[ r ], card_counts->twosided[ r ] );
    mpz_mul( infoact_with_cards, counts->infoset_actions[ r ], card_counts->twosided[ r ] );
    mpz_mul( cont_with_cards, counts->continuing[ r ], card_counts->twosided[ r ] );
    mpz_mul( term_with_cards, counts->terminal[ r ], card_counts->twosided[ r ] );

    mpz_add( total_info, total_info, info_with_cards );
    mpz_add( total_nt_info, total_nt_info, nt_info_with_cards );
    mpz_add( total_infoact, total_infoact, infoact_with_cards );
    mpz_add( total_term, total_term, term_with_cards );

    printf( "  Round %d\n", r );
    print_round_stats( "State",
		       &info_with_cards, 
		       &nt_info_with_cards,
		       &infoact_with_cards,
		       &cont_with_cards, 
		       &term_with_cards );
  }
  printf( "  Total:\n" );
  print_round_stats( "State",
		     &total_info, 
		     &total_nt_info,
		     &infoact_with_cards,
		     NULL, 
		     &total_term );



}

int main( const int argc, const char *argv[] )
{
  if( argc != 5 ) {
    printf( "Usage: ./count_nl_infosets <rounds> <smallblind> <bigblind> <starting_stack>\n" );
    int64_t mem_required = sizeof( nolimit_counts_t );
    mem_required /= 1024 * 1024; /* to mb */
    printf( "(Requires %jd megs of RAM for startup, more for operation)\n", 
	    (intmax_t) mem_required );
    return 1;
  }

  int i = 1;
  rounds = atoi( argv[ i++ ] );
  if( ( rounds < 0 ) || ( rounds > 4 ) ) {
    printf( "Rounds must be in [1..4]\n" );
    return 1;
  }

  smallblind = atoi( argv[ i++ ] );
  bigblind = atoi( argv[ i++ ] );

  if( smallblind > bigblind ) {
    printf( "Small blind must be <= big blind!  You gave [%d] and [%d]\n", smallblind, bigblind );
    return 1;
  }
  if( bigblind < 1 ) {
    printf( "Big blind must be >= 1!\n" );
    return 1;
  }

  starting_stack = atoi( argv[ i++ ] );
  if( ( starting_stack < bigblind ) || ( starting_stack > MAX_STACK ) ) {
    printf( "Starting stack must be in [%d,%d[\n", bigblind, MAX_STACK );
    return 1;
  }

  init_card_counts();

  /* Malloc */
  counts = ( nolimit_counts_t * ) malloc( sizeof( nolimit_counts_t ) );
  if( counts == NULL ) {
    printf( "Couldn't malloc %jd for counts!\n", 
	    (intmax_t) sizeof( nolimit_counts_t ) );
    return 1;
  }

  /* Initialize */
  for( s = 0; s <= MAX_STACK; s++ ) {
    mpz_init( counts->check_reaching[ s ] );
    for( f = 0; f <= MAX_STACK; f++ ) {
      mpz_init( counts->histories_reaching[ s ][ f ] );
    }
  }
  for( r = 0; r < MAX_ROUNDS + 1; r++ ) {
    for( s = 0; s <= MAX_STACK; s++ ) {
      mpz_init( counts->start_of_round_reach[ r ][ s ] );
    }
  }
  for( r = 0; r < MAX_ROUNDS; r++ ) {
    mpz_init( counts->infosets[ r ] );
    mpz_init( counts->nontrivial_infosets[ r ] );
    mpz_init( counts->infoset_actions[ r ] );
    mpz_init( counts->terminal[ r ] );
    mpz_init( counts->continuing[ r ] );
  }

  /* Init for start of game:
   * small blind player has one way to reach the start of the game.
   */
  mpz_set_si( counts->start_of_round_reach[ 0 ][ starting_stack - smallblind ], 1 );

  /* Start the spammy output timer,
   * so that we can try to estimate how long it'll take
   */
  signal( SIGALRM, sig_handler );
  struct itimerval freq;
  freq.it_value.tv_sec = 60;
  freq.it_value.tv_usec = 0;
  freq.it_interval.tv_sec = 60;
  freq.it_interval.tv_usec = 0;
  setitimer( ITIMER_REAL, &freq, NULL );

  struct timeval start_time, end_time;
  gettimeofday( &start_time, NULL );

  /* Start walking each round */
  for( r = 0; r < rounds; r++ ) {

    /* Initialize counts, set up the check cases for the start of this round */
    for( s = 0; s <= MAX_STACK; s++ ) {
      mpz_set_si( counts->check_reaching[ s ], 0 );
      for( f = 0; f <= MAX_STACK; f++ ) {
	mpz_set_si( counts->histories_reaching[ s ][ f ], 0 );
      }

      mpz_set( counts->check_reaching[ s ], counts->start_of_round_reach[ r ][ s ] );
    }

    /* Checks */
    if( r == 0 ) {
      push_check( r, starting_stack - smallblind, ( bigblind - smallblind ) );
    } else {
      for( s = starting_stack; s >= 0; s-- ) {
	if( mpz_sgn( counts->check_reaching[ s ] ) > 0 ) {
	  push_check( r, s, 0 );
	}
      }
    }

    /* Do normal actions */
    for( s = starting_stack; s >= 0; s-- ) {
      for( f = 0; f <= s; f++ ) {
	if( counts->histories_reaching[ s ][ f ] ) {
	  push( r, s, f );
	}
      }
    }
  }

  gettimeofday( &end_time, NULL );

  printf( "Elapsed time: " );
  print_time( stdout, end_time.tv_sec - start_time.tv_sec );
  printf( "\n" );

  /* Print sequence info (no cards) */
  printf( "Betting sequences only (no cards):\n" );

  /* Summed up over each round */
  mpz_t total_info, total_nt_info, total_infoact, total_term;
  mpz_init( total_info );
  mpz_init( total_nt_info );
  mpz_init( total_infoact );
  mpz_init( total_term );
  
  for( r = 0; r < rounds; r++ ) {

    printf( "  Round %d\n", r );
    print_round_stats( "Sequence",
		       &counts->infosets[ r ], 
		       &counts->nontrivial_infosets[ r ], 
		       &counts->infoset_actions[ r ], 
		       &counts->continuing[ r ], 
		       &counts->terminal[ r ] );

    mpz_add( total_info, total_info, counts->infosets[ r ] );
    mpz_add( total_nt_info, total_nt_info, counts->nontrivial_infosets[ r ] );
    mpz_add( total_infoact, total_infoact, counts->infoset_actions[ r ] );
    mpz_add( total_term, total_term, counts->terminal[ r ] );
  }

  printf( "  Total:\n" );
  print_round_stats( "Sequence",
		     &total_info, 
		     &total_nt_info,
		     &total_infoact, 
		     NULL, 
		     &total_term );

  printf( "\n\n" );


  /* Print Royal hold'em info */
  printf( "ROYAL HOLD'EM:\n" );
  print_game_counts( &royal_counts );
  printf( "\n\n" );

  /* Print Texas hold'em info */
  printf( "TEXAS HOLD'EM:\n" );
  print_game_counts( &texas_counts );
  printf( "\n\n" );

  /* Free allocated memory */
  for( s = 0; s <= MAX_STACK; s++ ) {
    mpz_clear( counts->check_reaching[ s ] );
    for( f = 0; f <= MAX_STACK; f++ ) {
      mpz_clear( counts->histories_reaching[ s ][ f ] );
    }
  }
  for( r = 0; r <= rounds; r++ ) {
    for( s = 0; s <= MAX_STACK; s++ ) {
      mpz_clear( counts->start_of_round_reach[ r ][ s ] );
    }
    mpz_clear( counts->infosets[ r ] );
    mpz_clear( counts->nontrivial_infosets[ r ] );
    mpz_clear( counts->infoset_actions[ r ] );
    mpz_clear( counts->continuing[ r ] );
    mpz_clear( counts->terminal[ r ] );
  }

  free( counts );

  cleanup_card_counts();

  return 0;
}
