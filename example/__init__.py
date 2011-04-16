### -*- coding: utf-8 -*- ####################################################

try:
    import ajax_select
except ImportError:
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))