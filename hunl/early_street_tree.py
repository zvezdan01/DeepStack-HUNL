"""DeepStack HUNL sparse pre-flop/flop betting lookahead boundaries.

Scope is deliberately narrow: this module builds only the betting part of
DeepStack's pre-flop and flop lookaheads.  It does NOT implement a value
network, bucketing, chance-CFV boxes, or the pre-flop 22,100-flop
enumeration.  When the current round closes it emits a `next_street`
boundary; if betting ends all-in it emits an `allin_runout` terminal.

Sources/authority are intentionally separated:
  * Base no-limit legality/state transitions: the same ACPC/CPRG game.c
    predicates mirrored by the already-certified RiverTreeBuilder.
  * Sparse action menus: DeepStack supplementary Table 4, frozen in
    HunlConfig (pre-flop/flop rows).
  * Pot-sized fraction semantics: call first, then bet a fraction of the
    resulting two-player pot, hence pot-after-call = 2*max_spent and
    raise_to = max_spent + fraction*(2*max_spent).

No claim is made that this is source-code-identical to the private
DeepStack implementation.  It is a source-constrained reconstruction whose
legality/state semantics are differential-tested against untouched game.c.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

from .config import DEFAULT_CONFIG, HunlConfig
from .tree import RiverTreeBuilder

Action = tuple[str, int]


@dataclass
class EarlyStreetNode:
    street: str                    # "preflop" | "flop" | "boundary"
    player: int                    # acting seat, -1 on boundary/terminal
    spent: tuple[int, int]         # total chips committed this hand
    max_spent: int
    min_raise_to: int
    action_depth: int              # actions in current resolving lookahead
    round_depth: int               # actions in this betting round
    board: tuple[int, ...] = ()    # () preflop, 3 cards on flop
    terminal: str | None = None    # fold | allin_runout
    folder: int | None = None
    next_street: str | None = None # flop | turn for next_street boundary
    actions: list[Action] = field(default_factory=list)
    children: list["EarlyStreetNode"] = field(default_factory=list)

    @property
    def is_boundary(self) -> bool:
        return self.street == "boundary" and self.terminal is None


class EarlyStreetTreeBuilder:
    """Sparse single-street DeepStack tree for pre-flop or flop."""

    _NEXT = {"preflop": (1, "flop"), "flop": (2, "turn")}

    def __init__(self, street: str, cfg: HunlConfig = DEFAULT_CONFIG):
        if street not in self._NEXT:
            raise ValueError("street must be preflop or flop")
        self.street = street
        self.cfg = cfg
        self._rules = RiverTreeBuilder(cfg)  # frozen ACPC legality mirror

    def build_preflop(self) -> EarlyStreetNode:
        if self.street != "preflop":
            raise ValueError("builder is not preflop")
        cfg = self.cfg
        ms = max(cfg.blinds)
        root = EarlyStreetNode(
            street="preflop", player=cfg.first_player[0],
            spent=cfg.blinds, max_spent=ms, min_raise_to=2 * ms,
            action_depth=0, round_depth=0, board=())
        self._expand(root)
        return root

    def build_flop(self, board3, pot_half: int) -> EarlyStreetNode:
        if self.street != "flop":
            raise ValueError("builder is not flop")
        board = tuple(int(c) for c in board3)
        if len(board) != 3 or len(set(board)) != 3 or not all(0 <= c < 52 for c in board):
            raise ValueError("board3 must contain three distinct 0-based cards")
        cfg = self.cfg
        if not (cfg.big_blind <= pot_half <= cfg.stack):
            raise ValueError("pot_half outside stack/blind range")
        root = EarlyStreetNode(
            street="flop", player=cfg.first_player[1],
            spent=(pot_half, pot_half), max_spent=pot_half,
            min_raise_to=pot_half + cfg.big_blind,
            action_depth=0, round_depth=0, board=board)
        self._expand(root)
        return root

    def _menu(self, depth: int) -> tuple[Fraction, ...]:
        return self.cfg.menu_for_street(self.street, depth)

    def _allin_enabled(self) -> bool:
        return (self.cfg.preflop_allin if self.street == "preflop"
                else self.cfg.flop_allin)

    def _expand(self, node: EarlyStreetNode) -> None:
        cfg = self.cfg
        p = node.player
        opp = 1 - p

        # Fold: exactly where ACPC says it is legal.
        if self._rules.fold_valid(node):
            child = EarlyStreetNode(
                street=node.street, player=-1, spent=node.spent,
                max_spent=node.max_spent, min_raise_to=node.min_raise_to,
                action_depth=node.action_depth + 1,
                round_depth=node.round_depth + 1, board=node.board,
                terminal="fold", folder=p)
            node.actions.append(("fold", 0))
            node.children.append(child)

        # Check/call.
        call_to = min(node.max_spent, cfg.stack)
        spent = list(node.spent)
        spent[p] = call_to
        closes = node.round_depth >= 1
        if closes:
            child = self._round_closed(tuple(spent), node)
        else:
            child = EarlyStreetNode(
                street=node.street, player=opp, spent=tuple(spent),
                max_spent=node.max_spent, min_raise_to=node.min_raise_to,
                action_depth=node.action_depth + 1,
                round_depth=node.round_depth + 1, board=node.board)
            self._expand(child)
        node.actions.append(("call", 0))
        node.children.append(child)

        # Sparse Table-4 raises, then the explicit all-in action.
        window = self._rules.raise_window(node)
        if window is not None:
            mn, mx = window
            pot_after_call = 2 * node.max_spent
            cands: set[int] = set()
            for frac in self._menu(node.action_depth):
                delta = frac * pot_after_call
                if delta.denominator != 1:
                    raise AssertionError("non-integer chip bet")
                r = node.max_spent + int(delta)
                if mn <= r <= mx:
                    cands.add(r)
            if self._allin_enabled():
                cands.add(mx)
            for r in sorted(cands):
                spent = list(node.spent)
                spent[p] = r
                child = EarlyStreetNode(
                    street=node.street, player=opp, spent=tuple(spent),
                    max_spent=r,
                    min_raise_to=max(node.min_raise_to,
                                     2 * r - node.max_spent),
                    action_depth=node.action_depth + 1,
                    round_depth=node.round_depth + 1, board=node.board)
                node.actions.append(("raise", r))
                node.children.append(child)
                self._expand(child)

        if not node.actions:
            raise AssertionError("decision node with no legal action")

    def _round_closed(self, spent: tuple[int, int],
                      parent: EarlyStreetNode) -> EarlyStreetNode:
        cfg = self.cfg
        ms = max(spent)
        # ACPC game.c marks an all-in hand finished and advances its round
        # to the final round; future public cards are a forced runout.
        if ms >= cfg.stack:
            return EarlyStreetNode(
                street="boundary", player=-1, spent=spent, max_spent=ms,
                min_raise_to=ms + cfg.big_blind,
                action_depth=parent.action_depth + 1,
                round_depth=0, board=parent.board,
                terminal="allin_runout")
        _, next_name = self._NEXT[self.street]
        return EarlyStreetNode(
            street="boundary", player=-1, spent=spent, max_spent=ms,
            min_raise_to=ms + cfg.big_blind,
            action_depth=parent.action_depth + 1,
            round_depth=0, board=parent.board, next_street=next_name)


def count_early_nodes(root: EarlyStreetNode) -> dict[str, int]:
    out = {"total": 0, "decision": 0, "fold": 0,
           "allin_runout": 0, "next_street": 0, "actions": 0}
    def walk(n: EarlyStreetNode):
        out["total"] += 1
        if n.terminal == "fold":
            out["fold"] += 1
        elif n.terminal == "allin_runout":
            out["allin_runout"] += 1
        elif n.is_boundary:
            out["next_street"] += 1
        else:
            out["decision"] += 1
            out["actions"] += len(n.actions)
        for c in n.children:
            walk(c)
    walk(root)
    return out
