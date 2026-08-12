-- D2 three-way experiment harness: run the RELEASED Lua resolver on the 200
-- reconstructed TrainSamples inputs, exactly replicating the per-sample
-- target computation of Source/DataGeneration/data_generation.lua:98-112.
-- COMPAT STUB (documented, numerically neutral): 'nn' is required at module
-- load by Nn/value_nn.lua but ValueNn is never constructed for street-2
-- resolves; the stub traps any accidental use.
package.preload['nn'] = function()
  return setmetatable({}, {__index = function() error('nn stub touched') end})
end
require 'torch'
local arguments = require 'Settings.arguments'
arguments.gpu = false
arguments.Tensor = torch.FloatTensor
torch.setdefaulttensortype('torch.FloatTensor')
local constants = require 'Settings.constants'
require 'Lookahead.resolving'

local scratch = arg[1]
local boards = torch.load(scratch .. '/d2_boards.t7')
local features = torch.load(scratch .. '/d2_features.t7')
local ranges = torch.load(scratch .. '/d2_ranges.t7')
local n = boards:size(1)
local out = arguments.Tensor(n, 2, 6)

for i = 1, n do
  local resolving = Resolving()
  local current_node = {}
  current_node.board = arguments.Tensor{boards[i]}
  current_node.street = 2
  current_node.current_player = constants.players.P1
  local pot_size = features[i] * arguments.stack        -- data_generation.lua:105
  current_node.bets = arguments.Tensor{pot_size, pot_size}
  local p1_range = ranges[i][1]
  local p2_range = ranges[i][2]
  resolving:resolve_first_node(current_node, p1_range, p2_range)
  local root_values = resolving:get_root_cfv_both_players()
  root_values:mul(1/pot_size)                           -- data_generation.lua:111
  out[i]:copy(root_values)
  if i % 20 == 0 then print('done', i) end
end

torch.save(scratch .. '/d2_lua_fresh.t7', out:float():contiguous())
print('D2 harness complete:', n, 'rows')
