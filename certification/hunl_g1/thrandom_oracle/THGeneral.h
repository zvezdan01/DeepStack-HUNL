/* Minimal THGeneral.h shim for compiling the UNTOUCHED THRandom.c
 * (torch/torch7 @ 814ea4a, lib/TH/THRandom.c SHA-256 57524962…) as a
 * standalone certification oracle. Provides only the symbols THRandom.c
 * references; no Torch7 numerics are re-implemented here. Same pattern
 * as the Phase-2A oracle harness and the Tammelin rng.c oracle. */
#ifndef TH_GENERAL_INC
#define TH_GENERAL_INC

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define TH_API
#define THAlloc malloc
#define THFree free
#define THError(...) do { fprintf(stderr, __VA_ARGS__); fprintf(stderr, "\n"); exit(1); } while (0)
#define THArgCheck(cond, argn, msg) do { if (!(cond)) THError("bad arg %d: %s", (int)(argn), (msg)); } while (0)

#endif
