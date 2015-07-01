
#import re
from pytk.davos.core.damproject import DamProject

proj = DamProject("zombillenium")

print proj.getLibPath("public", "shot_lib")
print proj.getLibPath("private", "shot_lib")
print proj.getLibPath("public", "asset_lib", "texture_dir")
