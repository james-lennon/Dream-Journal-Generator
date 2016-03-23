#!/usr/bin/env python
from optparse import OptionParser

import content_render

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename", default="out", help="output file")
parser.add_option("-n", "--number", type="int", dest="number", default=1, help="number of dreams to generate")
parser.add_option("-i", "--images", dest="images", action="store_true", default=True,
                  help="number of dreams to generate")
parser.add_option("-p", "--pdf", dest="pdf", action="store_true", default=False,
                  help="generate pdf file")
parser.add_option("-t", "--theme", dest="theme", default=False,
                  help="dream theme")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

journal = content_render.DreamJournal()

journal.generate_dreams(options.number, add_images=options.images, verbose=options.verbose, theme=options.theme)
journal.render(options.filename, pdf=options.pdf, text=False, verbose=options.verbose)
print journal.generateJSON()
