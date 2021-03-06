#!/usr/bin/env python3

import json
import os
import urllib.request
import pybtex.database

base_filename = "serverless-literature-base.json"
biblio_filename = "serverless-literature-bibliography.json"

forced = False

def populate_bibliography(base_filename, biblio_filename, forced):
	f = open(base_filename)
	literature = json.load(f)

	if os.path.isfile(biblio_filename):
		f = open(biblio_filename)
		biblio = json.load(f)
	else:
		biblio = {}

	header = {"Accept": "text/bibliography; style=bibtex"}

	for ident in literature:
		if not "doi" in literature[ident]:
			if ident in biblio and "title" in biblio[ident]:
				print("## work {} has no doi but a manual entry".format(ident))
			else:
				print("!! work {} has no doi".format(ident))
			continue
		if not ident in biblio or forced:
			doi = literature[ident]["doi"]
			print("Retrieving {}: {}".format(ident, doi))
			req = urllib.request.Request(doi, headers=header)
			res = urllib.request.urlopen(req)
			bib = res.read().decode("utf-8")
			db =pybtex.database.parse_string(bib, "bibtex")
			for entry in db.entries:
				ft = db.entries[entry].fields["title"]
				fa = db.entries[entry].fields["author"]
				fy = db.entries[entry].fields["year"]
				if "journal" in db.entries[entry].fields:
					fj = db.entries[entry].fields["journal"]
				else:
					fj = None
				biblio[ident] = {}
				biblio[ident]["title"] = ft
				biblio[ident]["author"] = fa
				biblio[ident]["year"] = fy
				if fj:
					biblio[ident]["journal"] = fj
				print("- Updated '{}'".format(ft))

	f = open(biblio_filename, "w")
	json.dump(biblio, f, indent=2, ensure_ascii=False, sort_keys=True)
	f.close()

	return biblio

def check_consistency(biblio):
	allkeys = [int(x) for x in biblio.keys()]
	allkeys.sort()
	if allkeys[-1] != len(allkeys):
		print("!! Inconsistency: keys={}".format(allkeys))

biblio = populate_bibliography(base_filename, biblio_filename, forced)
check_consistency(biblio)
