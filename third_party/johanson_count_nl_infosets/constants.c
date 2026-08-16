/* constants.c
 * Mike Johanson, Feb 1, 02013
 * 
 * A set of constants for the number of ways to deal the cards
 * in heads-up hold'em games.
 */

/* C includes */

/* Gnu MP includes */
#include <gmp.h>

/* count_infosets includes */
#include "constants.h"

card_counts_t texas_counts;
card_counts_t royal_counts;

void init_card_counts()
{
  int r;
  for( r = 0; r < MAX_ROUNDS; r++ ) {
    mpz_init( texas_counts.canonical_onesided[ r ] );
    mpz_init( texas_counts.onesided[ r ] );
    mpz_init( texas_counts.twosided[ r ] );

    mpz_init( royal_counts.canonical_onesided[ r ] );
    mpz_init( royal_counts.onesided[ r ] );
    mpz_init( royal_counts.twosided[ r ] );
  }

  /*****************
   * TEXAS HOLD'EM *
   *****************/

  /* Canonical One-sided */
  mpz_set_str( texas_counts.canonical_onesided[ 0 ],
               "169",
               10 );

  mpz_set_str( texas_counts.canonical_onesided[ 1 ],
               "1286792",
               10 );

  mpz_set_str( texas_counts.canonical_onesided[ 2 ],
               "55190538",
               10 );

  mpz_set_str( texas_counts.canonical_onesided[ 3 ],
               "2428287420",
               10 );

  /* One-sided */
  /* (52 choose 2) */
  mpz_set_str( texas_counts.onesided[ 0 ],
               "1326",
               10 );

  /* (52 choose 2)*(50 choose 3) */
  mpz_set_str( texas_counts.onesided[ 1 ],
               "25989600",
               10 );

  /* (52 choose 2)*(50 choose 3)*(47 choose 1) */
  mpz_set_str( texas_counts.onesided[ 2 ],
               "1221511200",
               10 );

  /* (52 choose 2)*(50 choose 3)*(47 choose 1)*(46 choose 1) */
  mpz_set_str( texas_counts.onesided[ 3 ],
               "56189515200",
               10 );

  /* Two-sided */
  /* (52 choose 2)*(50 choose 2) */
  mpz_set_str( texas_counts.twosided[ 0 ],
               "1624350",
               10 );

  /* (52 choose 2)*(50 choose 2)*(48 choose 3) */
  mpz_set_str( texas_counts.twosided[ 1 ],
               "28094757600",
               10 );

  /* (52 choose 2)*(50 choose 2)*(48 choose 3)*(45 choose 1) */
  mpz_set_str( texas_counts.twosided[ 2 ],
               "1264264092000",
               10 );

  /* (52 choose 2)*(50 choose 2)*(48 choose 3)*(45 choose 1)*(44 choose 1) */
  mpz_set_str( texas_counts.twosided[ 3 ],
               "55627620048000",
               10 );

  /*****************
   * ROYAL HOLD'EM *
   *****************/


  /* Canonical One-sided */
  mpz_set_str( royal_counts.canonical_onesided[ 0 ],
               "25",
               10 );

  mpz_set_str( royal_counts.canonical_onesided[ 1 ],
               "7760",
               10 );

  mpz_set_str( royal_counts.canonical_onesided[ 2 ],
               "104750",
               10 );

  mpz_set_str( royal_counts.canonical_onesided[ 3 ],
               "1398100",
               10 );

  /* One-sided */
  /* (52 choose 2) */
  mpz_set_str( royal_counts.onesided[ 0 ],
               "190",
               10 );

  /* (52 choose 2)*(50 choose 3) */
  mpz_set_str( royal_counts.onesided[ 1 ],
               "155040",
               10 );

  /* (52 choose 2)*(50 choose 3)*(47 choose 1) */
  mpz_set_str( royal_counts.onesided[ 2 ],
               "2325600",
               10 );

  /* (52 choose 2)*(50 choose 3)*(47 choose 1)*(46 choose 1) */
  mpz_set_str( royal_counts.onesided[ 3 ],
               "32558400",
               10 );

  /* Two-sided */
  /* (52 choose 2)*(50 choose 2) */
  mpz_set_str( royal_counts.twosided[ 0 ],
               "29070",
               10 );

  /* (52 choose 2)*(50 choose 2)*(48 choose 3) */
  mpz_set_str( royal_counts.twosided[ 1 ],
	       "16279200",
               10 );

  /* (52 choose 2)*(50 choose 2)*(48 choose 3)*(45 choose 1) */
  mpz_set_str( royal_counts.twosided[ 2 ],
	       "211629600",
               10 );

  /* (52 choose 2)*(50 choose 2)*(48 choose 3)*(45 choose 1)*(44 choose 1) */
  mpz_set_str( royal_counts.twosided[ 3 ],
	       "2539555200",
               10 );
}

void cleanup_card_counts()
{
  int r;
  for( r = 0; r < MAX_ROUNDS; r++ ) {
    mpz_clear( texas_counts.canonical_onesided[ r ] );
    mpz_clear( texas_counts.onesided[ r ] );
    mpz_clear( texas_counts.twosided[ r ] );

    mpz_clear( royal_counts.canonical_onesided[ r ] );
    mpz_clear( royal_counts.onesided[ r ] );
    mpz_clear( royal_counts.twosided[ r ] );
  }
}
