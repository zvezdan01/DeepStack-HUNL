/* G1.1 oracle harness around the UNTOUCHED author evalHandTables.
 *
 * The original file (with its rankCardset/Cardset/addCardToCardset code)
 * is #included verbatim — no author line is modified.
 *
 * Modes:
 *   rank_oracle all <out.bin>
 *       enumerate ALL C(52,7)=133,784,560 seven-card combinations in
 *       lexicographic order over ACPC card ids 0..51 (card = rank*4+suit),
 *       write each rankCardset result as little-endian uint32; print class
 *       counts (HANDCLASS boundaries) to stderr.
 *   rank_oracle boards <boards.bin> <n> <out.bin>
 *       read n boards of 5 uint8 card ids; for each board write 1326
 *       uint32 ranks for hole pairs (c0<c1 lexicographic); pairs colliding
 *       with the board get 0xFFFFFFFF.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "evalHandTables"   /* untouched author file */

static void add_card(Cardset *c, int card)
{
  addCardToCardset(c, card % 4, card / 4);
}

int main(int argc, char **argv)
{
  if (argc >= 3 && strcmp(argv[1], "all") == 0) {
    FILE *out = fopen(argv[2], "wb");
    if (!out) { perror("out"); return 1; }
    static uint32_t buf[1 << 16];
    size_t nbuf = 0;
    unsigned long long total = 0, classes[9] = {0};
    static const int bounds[8] = {1287, 5005, 8606, 9620, 9633, 10920,
                                  11934, 12103};
    int c0, c1, c2, c3, c4, c5, c6;
    for (c0 = 0; c0 < 52; ++c0)
    for (c1 = c0 + 1; c1 < 52; ++c1)
    for (c2 = c1 + 1; c2 < 52; ++c2)
    for (c3 = c2 + 1; c3 < 52; ++c3)
    for (c4 = c3 + 1; c4 < 52; ++c4)
    for (c5 = c4 + 1; c5 < 52; ++c5)
    for (c6 = c5 + 1; c6 < 52; ++c6) {
      Cardset cs = emptyCardset();
      add_card(&cs, c0); add_card(&cs, c1); add_card(&cs, c2);
      add_card(&cs, c3); add_card(&cs, c4); add_card(&cs, c5);
      add_card(&cs, c6);
      int r = rankCardset(cs);
      int k = 0;
      while (k < 8 && r >= bounds[k]) ++k;
      ++classes[k];
      buf[nbuf++] = (uint32_t)r;
      if (nbuf == (1 << 16)) { fwrite(buf, 4, nbuf, out); nbuf = 0; }
      ++total;
    }
    if (nbuf) fwrite(buf, 4, nbuf, out);
    fclose(out);
    fprintf(stderr, "total %llu\n", total);
    for (int k = 0; k < 9; ++k)
      fprintf(stderr, "class %d %llu\n", k, classes[k]);
    return 0;
  }
  if (argc >= 5 && strcmp(argv[1], "boards") == 0) {
    FILE *in = fopen(argv[2], "rb");
    FILE *out = fopen(argv[4], "wb");
    long n = atol(argv[3]);
    if (!in || !out) { perror("io"); return 1; }
    for (long b = 0; b < n; ++b) {
      uint8_t board[5];
      if (fread(board, 1, 5, in) != 5) { perror("board"); return 1; }
      Cardset base = emptyCardset();
      int on_board[52] = {0};
      for (int i = 0; i < 5; ++i) {
        add_card(&base, board[i]);
        on_board[board[i]] = 1;
      }
      static uint32_t ranks[1326];
      int idx = 0;
      for (int c0 = 0; c0 < 52; ++c0)
      for (int c1 = c0 + 1; c1 < 52; ++c1, ++idx) {
        if (on_board[c0] || on_board[c1]) {
          ranks[idx] = 0xFFFFFFFFu;
        } else {
          Cardset cs = base;
          add_card(&cs, c0); add_card(&cs, c1);
          ranks[idx] = (uint32_t)rankCardset(cs);
        }
      }
      fwrite(ranks, 4, 1326, out);
    }
    fclose(in); fclose(out);
    return 0;
  }
  fprintf(stderr, "usage: %s all <out.bin> | boards <boards.bin> <n> <out.bin>\n",
          argv[0]);
  return 2;
}
