#!/usr/bin/env python3
"""Differential test: Johanson count_nl_infosets betting-rule semantics
(author-oracle round-1 report, FORENSICS/ARTIFACTS/count_nl_infosets/)
vs the UNTOUCHED restored ACPC game.c oracle, on random legal HUNL
action sequences (50/100 blinds, stack 20000, reverse blinds).

Fully batch design (no interactivity): a Python walker simulates the
game with its own bookkeeping, pre-generates the complete stdin script
for certification/hunl_g1/betting_oracle.c (G/N/S/R/Q/A protocol), runs
the oracle ONCE, and diffs every response line against predictions.

Two prediction layers, kept separate on purpose:
  * S-line predictions replicate ACPC bookkeeping (walk sync check);
  * Q/R predictions use ONLY the author-rule formulas from the report:
      fold legal        iff faced > 0
      check/call        always legal
      min raise INCREMENT = max(bigblind, faced_increment)
      short all-in      if stack cannot cover the minimum, raise-to =
                        stack remains the one legal raise
      max raise-to      = stack
    computed from (spent, maxSpent, last increment) history — never from
    the oracle's minNoLimitRaiseTo field.
Any Q/R mismatch is a genuine semantic divergence between the author
rules and ACPC; any S mismatch is a walker sync bug (fail loudly).
"""
import random
import subprocess
import sys
import tempfile
from pathlib import Path

DS = Path("/workspace/deepstack_leduc_v1.1-bitexact-certified/reference_lua/ACPCServer")
QT = Path("/home/user/quant-trade")
GAMEDEF = DS / "holdem.nolimit.2p.reverse_blinds.game"

BB, SB, STACK, ROUNDS = 100, 50, 20000, 4
FIRST = [1, 0, 0, 0]  # 0-indexed first actor per round (gamedef: firstPlayer = 2 1 1 1)

SEED = 20260816
N_GAMES = 600


class Walk:
    """One hand: ACPC-faithful bookkeeping + author-rule predictions."""

    def __init__(self):
        self.spent = [BB, SB]  # blind = 100 50 -> p0 big blind, p1 small blind
        self.max_spent = BB
        self.folded = [0, 0]
        self.round = 0
        self.cur = FIRST[0]
        self.finished = 0
        self.min_raise_to = 2 * BB       # ACPC init: maxSpent * 2
        self.last_inc = BB               # author-side: increment currently faced
        self.acts = []                   # this round's (type, actor, all_in_after)

    # --- ACPC round/game-end bookkeeping (ports of game.c helpers) ---
    def num_acting(self):
        return sum(1 for p in (0, 1)
                   if not self.folded[p] and self.spent[p] < STACK)

    def num_called(self):
        ret = 0
        for typ, p, _ in reversed(self.acts):
            if typ == "r":
                if self.spent[p] < STACK:
                    ret += 1
                return ret
            if typ == "c" and self.spent[p] < STACK:
                ret += 1
        return ret

    # --- author-rule predictions (independent formulas) ---
    def author_fold_valid(self):
        return 1 if self.spent[self.cur] < self.max_spent else 0

    def author_raise_window(self):
        """(valid, min_raise_to, max_raise_to) per the author report."""
        if self.max_spent >= STACK or self.num_acting() <= 1:
            return (0, None, None)
        want = self.max_spent + max(BB, self.last_inc)
        if want > STACK:
            return (1, STACK, STACK)   # short all-in exception
        return (1, want, STACK)

    # --- transitions (ACPC doAction port) ---
    def do(self, act):
        p = self.cur
        if act == "f":
            self.folded[p] = 1
            self.acts.append(("f", p, False))
        elif act == "c":
            self.spent[p] = self.max_spent
            self.acts.append(("c", p, self.spent[p] >= STACK))
        else:
            to = int(act[1:])
            if 2 * to - self.max_spent > self.min_raise_to:
                self.min_raise_to = 2 * to - self.max_spent
            self.last_inc = to - self.max_spent
            self.max_spent = to
            self.spent[p] = to
            self.acts.append(("r", p, to >= STACK))
        # round / game end (game.c tail of doAction)
        if sum(self.folded) + 1 >= 2:
            self.finished = 1
        elif self.num_called() >= self.num_acting():
            if self.num_acting() > 1:
                if self.round + 1 < ROUNDS:
                    self.round += 1
                    self.min_raise_to = self.max_spent + BB
                    self.last_inc = BB
                    self.acts = []
                    self.cur = FIRST[self.round]
                    return
                self.finished = 1
            else:
                self.finished = 1
                self.round = ROUNDS - 1
        if not self.finished:
            self.cur = 1 - p


def build_and_predict(rng):
    """Return (script_lines, expected) for one full batch run."""
    script = [f"G {GAMEDEF}"]
    expected = []  # (kind, payload, context)

    for g in range(N_GAMES):
        script.append("N")
        w = Walk()
        step = 0
        while not w.finished and step < 200:
            ctx = f"game {g} step {step} r{w.round} cur{w.cur} spent={w.spent} max={w.max_spent}"
            # sync probe (ACPC bookkeeping)
            script.append("S")
            expected.append(("S", (0, w.round, w.cur, w.spent[0], w.spent[1],
                                   w.max_spent, w.min_raise_to,
                                   w.folded[0], w.folded[1]), ctx))
            # author-rule probes
            rv, rmin, rmax = w.author_raise_window()
            script.append("R")
            expected.append(("R", (rv, rmin, rmax), ctx))
            fv = w.author_fold_valid()
            script.append("Q f")
            expected.append(("Q", fv, ctx + " probe=f"))
            script.append("Q c")
            expected.append(("Q", 1, ctx + " probe=c"))
            if rv:
                probes = [(rmin, 1), (rmax, 1), (rmax + 1, 0)]
                if rmin - 1 > w.max_spent:
                    probes.append((rmin - 1, 0))
            else:
                probes = [(STACK, 0)]
            for amt, want in probes:
                script.append(f"Q r{amt}")
                expected.append(("Q", want, ctx + f" probe=r{amt} want={want}"))
            # pick an action (author-legal by construction)
            opts = ["c", "c", "c"]
            if fv:
                opts.append("f")
            if rv:
                opts += [f"r{rmin}", f"r{rmin}",
                         f"r{rmax}", f"r{rng.randint(rmin, rmax)}",
                         f"r{rng.randint(rmin, rmax)}"]
                if rmax - 1 >= rmin:
                    opts.append(f"r{rmax - 1}")  # drives short all-in next
            act = rng.choice(opts)
            script.append(f"A {act}")
            w.do(act)
            step += 1
        # terminal probe: loose compare (fin + spent + folded)
        script.append("S")
        expected.append(("S_FIN", (w.spent[0], w.spent[1],
                                   w.folded[0], w.folded[1]),
                         f"game {g} terminal"))
    return script, expected


def main():
    tmp = Path(tempfile.mkdtemp(prefix="jrules_"))
    exe = tmp / "betting_oracle"
    subprocess.run(
        ["cc", "-O2", "-o", str(exe),
         str(QT / "certification/hunl_g1/betting_oracle.c"),
         str(DS / "game.c"), str(DS / "rng.c"), "-I", str(DS)],
        check=True)

    rng = random.Random(SEED)
    script, expected = build_and_predict(rng)
    proc = subprocess.run([str(exe)], input="\n".join(script) + "\n",
                          capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        print(f"ORACLE EXIT {proc.returncode}: {proc.stderr.strip()[:400]}")
        print("=> an 'A' action the author rules deem legal was rejected "
              "by ACPC (or protocol error); divergence at output line "
              f"{len(proc.stdout.splitlines())}")
    lines = proc.stdout.splitlines()

    sync_bad = author_bad = checked_author = 0
    for i, (kind, want, ctx) in enumerate(expected):
        if i >= len(lines):
            print(f"OUTPUT TRUNCATED at expected #{i} ({kind}) [{ctx}]")
            break
        got = lines[i].split()
        if kind == "S":
            vals = tuple(int(x) for x in got[1:])
            if got[0] != "S" or vals != want:
                sync_bad += 1
                if sync_bad <= 10:
                    print(f"S SYNC MISMATCH [{ctx}]\n  want {want}\n  got  {vals}")
        elif kind == "S_FIN":
            fin, sp0, sp1 = int(got[1]), int(got[4]), int(got[5])
            f0, f1 = int(got[8]), int(got[9])
            if got[0] != "S" or fin != 1 or (sp0, sp1, f0, f1) != want:
                sync_bad += 1
                if sync_bad <= 10:
                    print(f"S_FIN MISMATCH [{ctx}] want fin=1 {want} got {got}")
        elif kind == "R":
            checked_author += 1
            rv, rmin, rmax = want
            ok = (got[0] == "R" and int(got[1]) == rv and
                  (rv == 0 or (int(got[2]) == rmin and int(got[3]) == rmax)))
            if not ok:
                author_bad += 1
                if author_bad <= 20:
                    print(f"R AUTHOR-RULE MISMATCH [{ctx}]\n"
                          f"  author want {want}\n  ACPC   got  {got}")
        elif kind == "Q":
            checked_author += 1
            if got[0] != "Q" or int(got[1]) != want:
                author_bad += 1
                if author_bad <= 20:
                    print(f"Q AUTHOR-RULE MISMATCH [{ctx}] want {want} got {got}")

    n_states = sum(1 for k, _, _ in expected if k == "R")
    print(f"\ngames={N_GAMES} decision-states={n_states} "
          f"author-rule checks={checked_author} "
          f"author mismatches={author_bad} sync mismatches={sync_bad}")
    if author_bad == 0 and sync_bad == 0 and proc.returncode == 0:
        print("PASS: author betting rules == untouched ACPC game.c on all "
              "sampled states (fold legality, raise window incl. short "
              "all-in, min-raise tracking, round transitions)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
