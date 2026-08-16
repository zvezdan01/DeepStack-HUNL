/* utility.c
 * Mike Johanson, February 20, 02013
 * Simple utility functions used by count_nl_infosets and count_limit_infosets
 */

/* C includes */
#include <stdio.h>
#include <string.h>

/* Gnu MP includes */
#include <gmp.h>

void print_spaces( int spaces )
{
  while( spaces > 0 ) {
    printf( " " );
    spaces--;
  }
}


void print_round_stats( const char *count_type, 
			mpz_t *infosets, 
			mpz_t *nontrivial_infosets, 
			mpz_t *infoset_actions, 
			mpz_t *continuing, 
			mpz_t *terminal )
{
  if( infosets != NULL ) {
    double is_dbl = mpz_get_d( *infosets );
    printf( "    %ss", count_type );
    print_spaces( 20 - strlen( count_type ) - 1 );
    printf( ": %g\t ", is_dbl );
    mpz_out_str( stdout, 10, *infosets );
    printf( "\n" );
  }

  if( nontrivial_infosets != NULL ) {
    double nis_dbl = mpz_get_d( *nontrivial_infosets );
    printf( "    Nontrivial %ss", count_type );
    print_spaces( 20 - strlen( count_type ) - 12 );
    printf( ": %g\t ", nis_dbl );
    mpz_out_str( stdout, 10, *nontrivial_infosets );
    printf( "\n" );
  }

  if( infoset_actions != NULL ) {
    double isa_dbl = mpz_get_d( *infoset_actions );
    printf( "    %s-Actions", count_type );
    print_spaces( 20 - strlen( count_type ) - 8 );
    printf( ": %g\t ", isa_dbl );
    mpz_out_str( stdout, 10, *infoset_actions );
    printf( "\n" );
  }

  if( continuing != NULL ) {
    double cont_dbl = mpz_get_d( *continuing );
    printf( "    Continuing          : %g\t ", cont_dbl );
    mpz_out_str( stdout, 10, *continuing );
    printf( "\n" );
  }

  if( terminal != NULL ) {
    double term_dbl = mpz_get_d( *terminal );
    printf( "    Terminal            : %g\t ", term_dbl );
    mpz_out_str( stdout, 10, *terminal );
    printf( "\n" );
  }
}
