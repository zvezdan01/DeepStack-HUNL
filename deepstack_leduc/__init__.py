"""IMPORT-COMPATIBILITY SHIM — NOT the certified golden engine.

The bit-exact certified DeepStack-Leduc Python port (Golden Baseline
`2ab6dde…`, v1.1) lived in the container-local workspace
`/workspace/deepstack_leduc_v1.1-bitexact-certified` and was LOST with
the 2026-08-14 container reclaim. The frozen `hunl/` engine modules
import a handful of its names at module-import time (`Config`,
`CFRDGadget`, `Lookahead`, `LookaheadResults`, `tree.Node/CALL/FOLD`),
but the HUNL TURN DATAGEN runtime path (`TurnEngine.resolve_first_node`,
`all_in_equity`) never executes any of them — the turn engine is a
self-contained vectorized f64 CFR over `hunl/` certified components.

This shim exists ONLY to satisfy those imports so the frozen `hunl/`
files stay byte-identical to Golden Baseline v1 commit `34a50560…`.
Every solver entry point raises immediately (loud-fail): nothing here
can silently substitute for golden-engine math. Paths that DO need the
golden engine (RiverResolver, CFR-D gadget re-solves, the Leduc
regression battery) are NOT runnable in this container and are reported
as such in the forensic certification.

Because all frozen harnesses insert the DS workspace path BEFORE the
repo root in `sys.path`, a restored real workspace automatically takes
precedence over this shim.
"""

_LOST = (
    "golden DeepStack-Leduc engine not available in this container: the "
    "certified workspace /workspace/deepstack_leduc_v1.1-bitexact-certified "
    "was lost with the 2026-08-14 container reclaim. This shim only "
    "satisfies module imports; the {name} runtime path is NOT certified "
    "here and must not run."
)


def _lost(name: str) -> RuntimeError:
    return RuntimeError(_LOST.format(name=name))
