/* utility.h
 * Mike Johanson, February 20, 02013
 * Simple utility functions used by count_nl_infosets and count_limit_infosets
 */

#ifndef __UTILITY_H__
#define __UTILITY_H__

/* C includes */
#include <stdio.h>
#include <string.h>

/* Gnu MP includes */
#include <gmp.h>

void print_spaces( int spaces );

void print_round_stats( const char *count_type, 
			mpz_t *infosets,
			mpz_t *nontrivial_infosets,
			mpz_t *infoset_actions,
			mpz_t *continuing,
			mpz_t *terminal );

#endif
