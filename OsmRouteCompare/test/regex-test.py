# -*- coding: UTF-8 -*-

import re
import sys

# Add our parent folder to our path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analysis.flag_redundant_way_names_simple import FlagRedundantWayNamesSimple

def test_name_ref(way_name, route_ref):
    flagger = FlagRedundantWayNamesSimple()
    result = flagger.name_is_redundant(way_name, 'Sample Route Name', route_ref)
    sys.stdout.write("{0:60s} {1}\n".format("Is 'name={}' redundant to 'ref={}'?".format(way_name, route_ref), result))

sys.stdout.write("Expected redundant:\n")
test_name_ref("25-Route", "25")
test_name_ref("SR-25", "25")
test_name_ref("SR-25;OH-4", "25")
test_name_ref("Highway 25", "25")
test_name_ref("Highway 25 bypass", "25")
test_name_ref("Highway D bypass", "D")
test_name_ref("Highway 25D", "25D")

sys.stdout.write("Expected not redundant:\n")
test_name_ref("Highway 25bypass", "25")
test_name_ref("Highway Dbypass", "D")
test_name_ref("Highway D205", "D")
test_name_ref("Main Street", "S")
test_name_ref("Highway 25D", "D")
test_name_ref("Highway 25D", "25")
