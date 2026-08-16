/* THRandom certification oracle harness (restoration re-run of the
 * Phase-2A method after the 2026-08-14 container loss).
 *
 * Compiled against the UNTOUCHED torch/torch7 @ 814ea4a THRandom.c.
 * For a given seed and count N, emits three binary streams:
 *   u32.bin   N x little-endian uint32   THRandom_random
 *   f32.bin   N x little-endian float32  (float)THRandom_uniform(gen,0,1)
 *             — the Torch7 FloatTensor store semantics (uniform double
 *             cast to float), one state draw per element;
 *   randint_1_6.bin / randint_1_52.bin / randint_0_4.bin
 *             N x little-endian int32 each, exercising the
 *             TensorMath.lua:773 mapping (u32 % (b+1-a)) + a
 *             over the Phase-2A range (1,6) and the two ranges the
 *             HUNL datagen actually draws: (1,52) board, (0,4) pot.
 * Each stream is generated from a FRESH manualSeed so streams are
 * independently comparable.
 *
 * Usage: harness <seed> <n> <outdir>
 */
#include "THRandom.h"
#include <stdint.h>

static void emit_u32(unsigned long seed, int n, const char *path)
{
  THGenerator *g = THGenerator_new();
  THRandom_manualSeed(g, seed);
  FILE *f = fopen(path, "wb");
  for (int i = 0; i < n; i++) {
    uint32_t v = (uint32_t)THRandom_random(g);
    fwrite(&v, 4, 1, f);
  }
  fclose(f);
  THGenerator_free(g);
}

static void emit_f32(unsigned long seed, int n, const char *path)
{
  THGenerator *g = THGenerator_new();
  THRandom_manualSeed(g, seed);
  FILE *f = fopen(path, "wb");
  for (int i = 0; i < n; i++) {
    float v = (float)THRandom_uniform(g, 0, 1);
    fwrite(&v, 4, 1, f);
  }
  fclose(f);
  THGenerator_free(g);
}

static void emit_randint(unsigned long seed, int n, long a, long b,
                         const char *path)
{
  THGenerator *g = THGenerator_new();
  THRandom_manualSeed(g, seed);
  FILE *f = fopen(path, "wb");
  for (int i = 0; i < n; i++) {
    /* TensorMath.lua:773: (THRandom_random(gen) % (b+1-a)) + a */
    int32_t v = (int32_t)((THRandom_random(g) % (unsigned long)(b + 1 - a)) + a);
    fwrite(&v, 4, 1, f);
  }
  fclose(f);
  THGenerator_free(g);
}

int main(int argc, char **argv)
{
  if (argc != 4) { fprintf(stderr, "usage: %s seed n outdir\n", argv[0]); return 1; }
  unsigned long seed = strtoul(argv[1], NULL, 10);
  int n = atoi(argv[2]);
  const char *out = argv[3];
  char path[4096];
  snprintf(path, sizeof path, "%s/seed%lu_u32.bin", out, seed);
  emit_u32(seed, n, path);
  snprintf(path, sizeof path, "%s/seed%lu_f32.bin", out, seed);
  emit_f32(seed, n, path);
  snprintf(path, sizeof path, "%s/seed%lu_randint_1_6.bin", out, seed);
  emit_randint(seed, n, 1, 6, path);
  snprintf(path, sizeof path, "%s/seed%lu_randint_1_52.bin", out, seed);
  emit_randint(seed, n, 1, 52, path);
  snprintf(path, sizeof path, "%s/seed%lu_randint_0_4.bin", out, seed);
  emit_randint(seed, n, 0, 4, path);
  return 0;
}
