#!/usr/bin/env python
from optparse import OptionParser

import content_render

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename", default="out.pdf", help="output file")
parser.add_option("-n", "--number", type="int", dest="number", default=1, help="number of dreams to generate")
parser.add_option("-img", "--images", dest="images", action="store_true", default=True,
                  help="number of dreams to generate")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

journal = content_render.DreamJournal()

journal.generate_dreams(options.number, add_images=options.images, verbose=options.verbose)
journal.render(options.filename, pdf=True)
