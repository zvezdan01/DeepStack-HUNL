/* RNG oracle generator: dumps raw genrand_int32 outputs from the original
 * CFR_plus rng.c (MT19937, init_genrand seeding) for fixed seeds.
 * Output: binary little-endian uint32 stream + text, one value per line. */
#include <stdio.h>
#include <stdlib.h>
#include "rng.h"

int main(int argc, char **argv) {
  if (argc != 4) {
    fprintf(stderr, "usage: %s <seed> <count> <outprefix>\n", argv[0]);
    return 1;
  }
  uint32_t seed = (uint32_t)strtoul(argv[1], NULL, 10);
  long count = strtol(argv[2], NULL, 10);
  rng_state_t state;
  init_genrand(&state, seed);

  char fname[4096];
  snprintf(fname, sizeof(fname), "%s.bin", argv[3]);
  FILE *fb = fopen(fname, "wb");
  snprintf(fname, sizeof(fname), "%s.txt", argv[3]);
  FILE *ft = fopen(fname, "w");
  if (!fb || !ft) { perror("fopen"); return 1; }

  for (long i = 0; i < count; ++i) {
    uint32_t v = genrand_int32(&state);
    fwrite(&v, sizeof(v), 1, fb);
    fprintf(ft, "%u\n", v);
  }
  fclose(fb); fclose(ft);
  return 0;
}
