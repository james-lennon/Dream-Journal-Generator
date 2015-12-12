#! /usr/bin/python

import content_render

journal = content_render.DreamJournal()

journal.generate_dreams(50, add_images=False)

journal.render("out", pdf=False)
