/* constants.h
 * Mike Johanson, Feb 1, 02013
 * A set of constants for the number of ways to deal
 * out the cards in heads-up hold'em games.
 */

#ifndef __CONSTANTS_H__
#define __CONSTANTS_H__

/* C includes */

/* GNU MP library for arbitrary length integers */
#include <gmp.h>

/* Max rounds in a game */
#define MAX_ROUNDS 4

typedef struct {
  mpz_t canonical_onesided[ MAX_ROUNDS ];
  mpz_t onesided[ MAX_ROUNDS ];
  mpz_t twosided[ MAX_ROUNDS ];
} card_counts_t;

/* Constants.  Must call the initialization function before using. */
extern card_counts_t texas_counts;
extern card_counts_t royal_counts;

/* Initialization function */
void init_card_counts();

/* Cleanup function */
void cleanup_card_counts();

#endif
