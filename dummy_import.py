import sys
sys.path.append('server')
from server.games.scopa.game import ScopaOptions
opts = ScopaOptions()
print(opts.manual_selection)
