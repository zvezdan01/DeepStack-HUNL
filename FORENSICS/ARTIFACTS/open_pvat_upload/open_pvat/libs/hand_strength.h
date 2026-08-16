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

/*
	Author: Josh Davidson
	Purpose: Used to evaluate the hand strength of a given Texas Holedm Poker
	Hand.
*/

#ifndef HAND_STRENGTH_H
#define HAND_STRENGTH_H

#include "inlines/eval.h"

/* given player one cards in pc[ 0 ][ 0 ] and pc[ 0 ][ 1 ],
   and player two cards in pc[ 1 ][ 0 ] and pc[ 1 ][ 1 ],
   the necessary number of board cards in bc[ 0 ... ] for the given round,
   return the hand equity for player one and two in
   equities_ret[ 0 ] and equities_ret[ 1 ] respectively */
void handEquities(int *pc[2], int player_folded[2], int *bc, int round, double equities_ret[2]);

/* given the player cards in pc[ 0 ...  num_pc-1 ]
   and the board cards in bc[ 0 ... bc-1 ]
   return an integer such that any hand with value X will beat
   any hand with value Y<X, lose to any hand J>X, and tie
   any other hand with value X */
int rankHand( const int *pc, const int num_pc, const int *bc, const int num_bc );

#endif
