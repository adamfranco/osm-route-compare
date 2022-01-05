import sys
import math
import resource
from copy import copy
import time
import osmium
from osmium._osmium import InvalidLocationError

# simple class that handles the parsed OSM data.
class RouteCollector(osmium.SimpleHandler):
    collections = []
    relations = {}
    ways = {}
    num_ways = 0
    num_relations = 0
    verbose = False
    roads = []

    def __init__(self):
        osmium.SimpleHandler.__init__(self)

    def log(self, msg):
        if self.verbose:
            sys.stderr.write("{}\t{mem:.1f}MB\n".format(msg, mem=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576))
            sys.stderr.flush()

    def parse(self, filename, callback):
        # Reinitialize if we have a new file
        self.relations = {}
        self.ways = {}
        num_ways = 0
        num_relations = 0
        start_time = time.time()
        self.log("Loading {}".format(filename))
        self.log("Loading ways and relations, each '-' is 100 ways, each '.' is 100 relations, each row is 10,000 ways or relations")

        self.apply_file(filename, locations=True, idx='sparse_mem_array')

        self.log("\nRelations and ways loaded matched in {}".format(filename))

        self.attach_relation_details_to_ways()
        self.attach_ways_to_relations()

        self.collections = self.relations.values()

        # Send our collected data to our callback function.
        self.log("Streaming collections, each '.' is 1% complete")
        if self.verbose:
            total = len(self.collections)
            if total < 100:
                collections_marker = 1
            else:
                collections_marker = round(total/100)
            i = 0
        for collection in self.collections:
            # status output
            if self.verbose:
                i += 1
                if not (i % collections_marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()
            callback(collection)
        self.log('\nStreaming completed in {time:.1f}'.format(time=(time.time() - start_time)))

    # Save route relations for later merging with ways.
    def relation(self, relation):
        if 'type' in relation.tags and relation.tags['type'] == 'route' and 'route' in relation.tags and relation.tags['route'] == 'road':
            new_relation = {'id': relation.id, 'tags': {}, 'members': []}
            for tag in relation.tags:
                new_relation['tags'][tag.k] = tag.v
            for member in relation.members:
                new_relation['members'].append({'ref': member.ref, 'role': member.role, 'type': member.type})
            self.relations[relation.id] = new_relation

            # status output
            if self.verbose:
                self.num_relations = self.num_relations + 1
                if not (self.num_relations % 100):
                    sys.stderr.write('.')
                    if not (self.num_relations % 10000):
                        sys.stderr.write('\n')
                    sys.stderr.flush()

    def way(self, way):
        # callback method for ways
        if 'highway' in way.tags and (not self.roads or way.tags['highway'] in self.roads):
            # Strip nodes and other details from the way.
            new_way = {'id': way.id, 'tags': {}}
            for tag in way.tags:
                new_way['tags'][tag.k] = tag.v

            self.ways[way.id] = new_way

            # status output
            if self.verbose:
                if not self.num_ways:
                    sys.stderr.write('\n')
                self.num_ways = self.num_ways + 1
                if not (self.num_ways % 100):
                    sys.stderr.write('-')
                    if not (self.num_ways % 10000):
                        sys.stderr.write('\n')
                    sys.stderr.flush()

    # Attach relation details to the member ways
    def attach_relation_details_to_ways(self):
        # status output
        start_time = time.time()
        i = 0
        total = len(self.relations)
        if total < 100:
            marker = 1
        else:
            marker = round(total/100)
        self.log("{} ways will have relations added '.' is 1% complete".format(total))

        for id in self.relations:
            relation = self.relations[id]
            relation_details = {'id': id, 'name':'', 'ref':''}
            if 'name' in relation['tags']:
                relation_details['name'] = relation['tags']['name']
            if 'ref' in relation['tags']:
                relation_details['ref'] = relation['tags']['ref']
            for member in relation['members']:
                if member['type'] == 'w' and member['ref'] in self.ways:
                    # Attach the relation details back to the ways so that they have a
                    # full list for name redundancy checking.
                    if 'relations' not in self.ways[member['ref']]:
                        self.ways[member['ref']]['relations'] = []
                    self.ways[member['ref']]['relations'].append(relation_details)

            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

        # status output
        if self.verbose:
            self.log('\nAdding relations completed in {time:.1f} seconds'.format(time=(time.time() - start_time)))

    # Attach ways to the relations that reference them.
    def attach_ways_to_relations(self):
        # status output
        start_time = time.time()
        i = 0
        total = len(self.relations)
        if total < 100:
            marker = 1
        else:
            marker = round(total/100)
        self.log("{} collections will have ways added '.' is 1% complete".format(total))

        for id in self.relations:
            relation = self.relations[id]
            relation['ways'] = []
            for member in relation['members']:
                if member['type'] == 'w' and member['ref'] in self.ways:
                    relation['ways'].append(self.ways[member['ref']])

            # status output
            if self.verbose:
                i = i + 1
                if not (i % marker):
                    sys.stderr.write('.')
                    sys.stderr.flush()

        # Remove remaining ways as they are no longer needed.
        del self.ways

        # status output
        if self.verbose:
            self.log('\nAdding ways completed in {time:.1f} seconds'.format(time=(time.time() - start_time)))
