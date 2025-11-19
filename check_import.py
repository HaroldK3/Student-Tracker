import importlib,traceback,sys
try:
    importlib.import_module('Backend.main')
    print('Imported Backend.main OK')
except Exception as e:
    traceback.print_exc()
    sys.exit(1)
