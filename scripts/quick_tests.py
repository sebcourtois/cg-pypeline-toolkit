
#import re
from pytk.davos.core.damproject import DamProject

proj = DamProject("zombillenium")

print proj.getRcPath("public", "shot_lib")
print proj.getRcPath("private", "shot_lib")
print proj.getRcPath("public", "asset_lib", "texture_dir")
