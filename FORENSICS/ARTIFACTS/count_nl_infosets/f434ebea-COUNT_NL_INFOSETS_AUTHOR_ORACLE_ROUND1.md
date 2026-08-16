# Michael Johanson `count_nl_infosets` — author-oracle round 1

Date: 2026-08-16
Purpose: establish first-party structural oracles for HU no-limit Hold'em betting rules and game-size counts. This report does **not** claim identity with the missing DeepStack HUNL DataGenerator or with the internal FCPA solver.

## Source provenance

Uploaded archive: `count_nl_infosets.tar`

- SHA-256: `6fcf5fa41387ed71f720c9c850c47b7b111830b68f979853a8c3f998365ac0c8`
- tar owner: `johanson/johanson`
- source header: `Mike Johanson, Feb 1, 02013`
- `count_nl_infosets.c` SHA-256: `c4032c8db6220e703de3f98a8d3ce260861c3d64153ee50a5bf66b225e061cb7`
- accompanying technical report SHA-256: `4a6e9c6b472843e4f66a0cb3c622f9fb549b02fa6c405ae3261bc6c2c3fae598`

The archive includes exact historical output files for the 2007–2008, 2009, and 2010–2013 ACPC HUNL configurations.

## Exact betting-rule semantics encoded by the author source

For a state represented by current `stack`, `faced`, and whether the first action of a round can check:

1. Fold is legal iff `faced > 0`.
2. Check/call is always legal.
3. The minimum new bet/raise increment is:
   `min_bet = max(bigblind, faced)`.
4. If the remaining chips after calling are smaller than that minimum, the all-in amount remains legal:
   `min_bet = stack - faced`.
5. Every **integer** amount from `min_bet` through `stack - faced`, inclusive, is a legal bet/raise in this unabstracted game.
6. A call from a normal betting state advances to the next round; on the final round it advances to showdown.
7. Forced post-all-in decisions are excluded from the nontrivial infoset/action counts.

These semantics are useful as a base no-limit legality oracle. They are **not** an FCPA abstraction oracle: the program intentionally enumerates all legal integer bet sizes.

## Build note

The historical Makefile puts `-lgmp` before the object/source inputs. On the current GNU toolchain this fails because of modern linker `--as-needed` behavior. The source itself was not changed for this issue; test binaries were linked with the semantically equivalent modern command placing `-lgmp` last.

The original program also allocates a fixed `MAX_STACK=20000` table (~6.4 GB) even for tiny games. The sandbox could not allocate that. For executable verification of smaller historical configurations, the test copy changed **only** `MAX_STACK` to the tested stack size. `push_check`, `push`, arithmetic, counters, and all game rules were unchanged.

## Executable verification

### [2-$20] $1-$2 no-limit royal hold'em

Test command semantics: `rounds=2, smallblind=1, bigblind=2, stack=20`.

The run reproduces the paper's Table 7 values exactly for all 12 fields checked:

- preflop nontrivial betting sequences: `1188`
- preflop sequence-actions: `3561`
- preflop continuing: `1187`
- preflop terminal: `1187`
- flop nontrivial betting sequences: `19996`
- flop sequence-actions: `57616`
- flop terminal: `38807`
- Royal canonical preflop infosets: `29700`
- Royal canonical preflop infoset-actions: `89025`
- Royal canonical flop infosets: `155168960`
- Royal canonical flop infoset-actions: `447100160`
- Royal canonical flop terminal: `301142320`

Result: `12/12 EXACT`.

Normalized full-output SHA-256 (elapsed time removed):
`d6cd73ad4125fc4f38a14e181c670c007828a83da09e9fda591e183f06850251`

GCC and Clang outputs are byte-identical after normalizing elapsed time.

### 2009 ACPC HUNL — $1/$2, stack 400

The freshly executed output is byte-identical to the author-supplied `acpc-2009.txt` after removing only the elapsed-time line.

- exact reference/run SHA-256 without elapsed line: `ea6c0bcccc3116650d0f657b5ff7a0296bc33e25d25f80836b1bfc3a4433597d`
- normalized full run SHA-256: `b316b65a723b0e4bd6d11115935bfad5b274d8764e5b4c8d196b32f774c5e750`
- GCC == Clang: **EXACT**

### 2007–2008 ACPC HUNL — $1/$2, stack 1000

The freshly executed output is byte-identical to the author-supplied `acpc-2007-2008.txt` after removing only the elapsed-time line.

- exact reference/run SHA-256 without elapsed line: `dd60f478362a29f002b370ac0318b9ec18099aaa2b29548f13aaa21399f40588`
- normalized full run SHA-256: `18280543e7589a39827a63ecdd7cb4bdd38e3a375918e158d55cfc52e63eb996`
- GCC == Clang: **EXACT**

### 2010–2013 ACPC HUNL — $50/$100, stack 20000

The archive contains Michael Johanson's exact output file for this configuration, SHA-256:
`117b69f8d837c0fbd206b1f00ae430a02fc95c89d35f22394c3fe60b53fce35c`.

A full fresh execution was not attempted in this sandbox because the original source requires >6 GB initial allocation and the author reports a roughly two-day computation for this case. The supplied exact output is retained as a first-party reference artifact, but is not labelled as freshly reproduced here.

## Important boundary for HUHL/DeepStack reconstruction

What this author oracle can certify in our engine:

- blind initialization;
- integer-chip stack accounting;
- fold legality;
- check/call transitions;
- min-bet/min-raise rule;
- short all-in exception;
- round transition and showdown transition;
- unabstracted betting-tree counts for configurations we can compare.

What it cannot certify:

- FCPA action abstraction or pot-sized raise formula;
- DeepStack sparse lookahead action sets;
- `CFRplus_holdem_nolimit_FCPA` serialization;
- CFR/CFR+ values or regrets;
- range generation;
- pot-size sampling;
- CFV target generation;
- DeepStack training RNG/seeds;
- the missing HUNL DataGenerator.

## Next direct comparison target

The next useful operation is differential testing against the current HUHL betting engine:

1. feed identical `(round, stack, faced, check_allowed)` states;
2. compare fold/check/call legality;
3. compare minimum legal raise and all-in exception;
4. compare next-state stack/faced transitions;
5. for an unabstracted test configuration, compare whole betting-sequence/action counts against this oracle.

Only after the base game legality is exact should FCPA/pot-action logic be layered on and checked against a separate first-party FCPA oracle.
