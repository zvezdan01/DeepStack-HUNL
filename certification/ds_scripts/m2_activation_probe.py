#!/usr/bin/env python3
"""M2 activation probe: measures the maximum regret magnitudes reached
anywhere in representative worst-case resolves, to document how far the
certification corpus sits from the Lua saturation bound 999999
(tools.lua:29-31). Uses the production trace_callback hook — no engine
modification. Run from the DS repo root with LD_LIBRARY_PATH=$PWD PYTHONPATH=."""
import numpy as np

from deepstack_leduc.acpc import parse_matchstate
from deepstack_leduc.card_tools import normalize_range, uniform_range
from deepstack_leduc.continual_resolving import ContinualResolving
from deepstack_leduc.resolving import Resolving
from deepstack_leduc.tree import Node
from deepstack_leduc.value_model import load_original_value_net

STATS = {'regrets': 0.0, 'positive': 0.0, 'gadget': 0.0}


def probe(look, stage, iteration):
    if stage != 'regrets':
        return
    for d in range(2, look.depth + 1):
        r = look.regrets_data[d]
        p = look.positive_regrets_data[d]
        if r is not None:
            STATS['regrets'] = max(STATS['regrets'], float(np.max(r)))
        if p is not None:
            STATS['positive'] = max(STATS['positive'], float(np.max(p)))
    g = look.reconstruction_gadget
    if g is not None:
        STATS['gadget'] = max(
            STATS['gadget'],
            float(np.max(g.play_regrets)),
            float(np.max(g.terminate_regrets)),
        )


net = load_original_value_net()

from deepstack_leduc.lookahead import Lookahead
from deepstack_leduc.tree import PokerTreeBuilder

# 1) street-1 root resolve, full depth (mirrors resolving.py:resolve_first_node)
node = Node(1, 0, np.array([100.0, 100.0], dtype=np.float32), ())
tree1 = PokerTreeBuilder().build_tree(node, limit_to_street=True)
look1 = Lookahead(value_network=net)
look1.build_lookahead(tree1)
look1.trace_callback = probe
u = uniform_range(())
look1.resolve_first_node(u, u)

# 2) worst-pot gadget resolve: P2 street-2 after max escalation (pot 900)
cr = ContinualResolving(value_network=net)
state = parse_matchstate('MATCHSTATE:0:1::As|')
cr.start_new_hand(state)
s1 = parse_matchstate('MATCHSTATE:0:1::As|')
n1 = s1.to_node()
cr._resolve_node(n1, s1)
strat = cr.resolving.get_action_strategy(300)
cr.current_opponent_cfvs_bound = cr.resolving.get_action_cfv(300).copy()
cr.current_player_range *= strat
cr.current_player_range = normalize_range(n1.board, cr.current_player_range).astype(np.float32)
cr.last_bet = 300
cr.last_node = n1
s2 = parse_matchstate('MATCHSTATE:0:1:r300c/:As|/Ah')
n2 = s2.to_node()
cr._update_invariant(n2, s2)
look = None
# attach probe via monkey wiring: construct lookahead manually mirrors resolve()
from deepstack_leduc.lookahead import Lookahead  # noqa: E402

look = Lookahead(cr.cfg, net)
from deepstack_leduc.tree import PokerTreeBuilder  # noqa: E402

tree = PokerTreeBuilder(cr.cfg).build_tree(n2, limit_to_street=True)
look.build_lookahead(tree)
look.trace_callback = probe
look.resolve(cr.current_player_range, cr.current_opponent_cfvs_bound)

# 3) max-pot resolve: street-2 at pot 900 with skewed ranges (regret-heavy)
node9 = Node(2, 0, np.array([900.0, 900.0], dtype=np.float32), (1,))
tree9 = PokerTreeBuilder(cr.cfg).build_tree(node9, limit_to_street=True)
look9 = Lookahead(cr.cfg, net)
look9.build_lookahead(tree9)
look9.trace_callback = probe
p = np.array([0.94, 0.0, 0.02, 0.02, 0.01, 0.01], dtype=np.float32)
o = np.array([0.01, 0.0, 0.01, 0.02, 0.48, 0.48], dtype=np.float32)
look9.resolve_first_node(p, o)

print(f"max cumulative regret observed : {STATS['regrets']:.3f}")
print(f"max positive regret observed   : {STATS['positive']:.3f}")
print(f"max gadget regret observed     : {STATS['gadget']:.3f}")
print(f"Lua saturation bound           : 999999")
hit = max(STATS.values()) >= 999999.0
print('M2 CLAMP ACTIVATED:', 'YES' if hit else 'NO — corpus stays far below the bound')
