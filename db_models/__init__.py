from os.path import dirname, basename, isfile, join
import glob

# This is a hack to set __all__ to a list of all files in current directory
# That way when doing "from db_models import *" it will bring all files into scope
# needed because the file creating all tables needs every db_model imported

# the legit alternative is importing every model here explicitly. Might be the more proper way later

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")]  # type: ignore
