/* G1 betting-legality oracle around the UNTOUCHED ACPC game.c.
 *
 * game.c (and its evalHandTables include) is compiled verbatim; this file
 * only drives it through a line protocol on stdin:
 *   G <gamefile>   load game definition (once, first line)
 *   N              initState(handId=0)
 *   A f|c|r<N>     assert isValidAction (no fixing) then doAction
 *   Q f|c|r<N>     print "Q <0|1>"  (isValidAction, no fixing)
 *   R              print "R <valid> <min> <max>"  (raiseIsValid)
 *   S              print "S <finished> <round> <cur> <spent0> <spent1>
 *                          <maxSpent> <minRaiseTo> <folded0> <folded1>"
 * Any invalid 'A' action or protocol error exits non-zero (fail-fast).
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "game.h"

int main(void)
{
  static char line[256];
  Game *game = NULL;
  State state;
  int have_state = 0;

  while (fgets(line, sizeof(line), stdin)) {
    size_t n = strlen(line);
    while (n && (line[n-1] == '\n' || line[n-1] == '\r')) line[--n] = 0;
    if (!n) continue;
    if (line[0] == 'G') {
      FILE *f = fopen(line + 2, "r");
      if (!f) { fprintf(stderr, "no game file\n"); return 2; }
      game = readGame(f);
      fclose(f);
      if (!game) { fprintf(stderr, "bad game file\n"); return 2; }
    } else if (line[0] == 'N') {
      if (!game) return 2;
      initState(game, 0, &state);
      have_state = 1;
    } else if (line[0] == 'A' || line[0] == 'Q') {
      Action a;
      if (!have_state) return 2;
      if (line[2] == 'f') { a.type = a_fold; a.size = 0; }
      else if (line[2] == 'c') { a.type = a_call; a.size = 0; }
      else if (line[2] == 'r') { a.type = a_raise; a.size = atoi(line + 3); }
      else { fprintf(stderr, "bad action '%s'\n", line); return 2; }
      int valid = isValidAction(game, &state, 0, &a);
      if (line[0] == 'Q') {
        printf("Q %d\n", valid);
      } else {
        if (!valid) { fprintf(stderr, "invalid A '%s'\n", line); return 3; }
        doAction(game, &a, &state);
      }
    } else if (line[0] == 'R') {
      int32_t mn = -1, mx = -1;
      int valid = raiseIsValid(game, &state, &mn, &mx);
      printf("R %d %d %d\n", valid, mn, mx);
    } else if (line[0] == 'S') {
      int fin = stateFinished(&state);
      int cur = fin ? -1 : currentPlayer(game, &state);
      printf("S %d %d %d %d %d %d %d %d %d\n", fin, state.round, cur,
             state.spent[0], state.spent[1], state.maxSpent,
             state.minNoLimitRaiseTo,
             state.playerFolded[0], state.playerFolded[1]);
    } else {
      fprintf(stderr, "bad line '%s'\n", line);
      return 2;
    }
  }
  fflush(stdout);
  return 0;
}
