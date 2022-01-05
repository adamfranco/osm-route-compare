# -*- coding: UTF-8 -*-

import re
import sys

class FlagRedundantWayNamesSimple(object):

    @classmethod
    def parse(cls, argv):
        return cls()

    def process(self, iterable):
        for route in iterable:
            if 'ref' in route['tags']:
                route_ref = ''
                if 'ref' in route['tags']:
                    route_ref = route['tags']['ref']

                route_name = ''
                if 'name' in route['tags']:
                    route_name = route['tags']['name']

                for way in route['ways']:
                    way['name_is_redundant'] = False

                    if 'name' in way['tags']:
                        way_name = way['tags']['name']

                        # Check if the name is redudant compared to the current relation
                        if self.name_is_redundant(way_name, route_name, route_ref):
                            way['name_is_redundant'] = True

                        # Check if the name is redudant compared to all relations it is a member of.
                        for relation_details in way['relations']:
                            if self.name_is_redundant(way_name, relation_details['name'], relation_details['ref']):
                                way['name_is_redundant'] = True

            else:
                if 'errors' not in route:
                    route['errors'] = []
                route['errors'].append('no route ref')

            yield(route)

    def name_is_redundant(self, way_name, route_name, route_ref):
        # if way_name == route_name:
        #     return True

        if way_name == route_ref:
            return True

        if route_ref == '':
            return False

        # Redundant if the way name...
        #   - Begins with the route ref followed by some non-word character.
        #   - Has the route ref stand-alone in the middle
        #   - Ends with some non-word character followed by the route ref.
        regex = re.compile("(^"+re.escape(route_ref)+"\W.*|.*\W"+re.escape(route_ref)+"\W.*|.*\W"+re.escape(route_ref)+"$)")
        if regex.match(way_name):
            return True

        return False
