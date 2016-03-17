import json
import os
import random
import time

import pdfkit

import content_parser
import dream_images
import content_date

NUM_HTML_TEMPLATES = 3


class DreamJournal:
    def __init__(self):
        self.dir = os.path.dirname(os.path.realpath(__file__))
        self.dream_text = ""
        self.dreams = []
        self.dream_renders = []
        self._load_cover("html/cover.html")
        self.image_urls = set()

    def _load_cover(self, cover_file):
        with open(os.path.join(self.dir, cover_file), "r") as openfile:
            html_string = openfile.read().replace("{date}", time.strftime("%d.%m.%Y %H:%M:%S %p"))
            image = dream_images.get_photo("dream")
            html_string = html_string.replace("{image}", image)
            return html_string + "<div style='page-break-before:always'></div>"

    def generate_dreams(self, count, tmp=None, add_images=True, add_dates=True, verbose=True):
        if tmp is None:
            tmp = content_parser.DreamTemplate()
            tmp.load()
        cur_date = time.strftime("%d.%m.%Y")
        for i in range(0, count):
            if verbose: print "[Generating Dream %d]" % (i + 1)

            tmp.reset()
            dream = tmp.generate_dream()
            img = ""
            if add_images:
                noun = False
                if "noun#char" in tmp.content.components:
                    noun = tmp.content.get_component("noun#char")
                img = False
                if noun:
                    img = dream_images.get_photo(noun, surreal=False)
                if img in self.image_urls:
                    img = ""
                else:
                    self.image_urls.add(img)
            if add_dates:
                cur_date = content_date.generate_date(cur_date)
                dream = cur_date + "<br>\n" + dream
            self.add_dream(dream, img)

    def add_dream(self, dream, image=''):
        self.dream_text += dream + "\n\n"
        self.dreams.append((dream, image))

        template_file = os.path.join(self.dir, "html/entry%i.html" % random.randrange(1, NUM_HTML_TEMPLATES + 1))

        with open(template_file, "r") as openfile:
            html_string = openfile.read()

            html_string = html_string.replace("{content}", dream)
            if not image:
                image = ''
            html_string = html_string.replace("{image}", image)

            self.dream_renders.append(html_string)

    def render(self, out_file, pdf=True, verbose=True):
        if verbose: print "[Saving Text]"
        with open(out_file + ".txt", "w") as txtfile:
            txtfile.write(self.dream_text)

        if pdf:
            if verbose: print "[Generating PDF]"

            wrapping = ""
            with open(os.path.join(self.dir, "html/wrapper.html")) as openfile:
                wrapping = openfile.read()
            total_string = self._load_cover(os.path.join(self.dir, "html/cover.html"))
            for i, r in enumerate(self.dream_renders):
                if i % 2 == 1:
                    total_string += wrapping.replace("{entry}", self.dream_renders[i - 1] + r)
                    if i != len(self.dream_renders) - 1:
                        total_string += "<div style='page-break-before:always'></div>"

            options = {
                'page-size': 'Letter',
                'margin-top': '0in',
                'margin-right': '0in',
                'margin-bottom': '0in',
                'margin-left': '0in',
                'encoding': "UTF-8",
                'no-outline': None
            }

            if not verbose:
                options['quiet'] = ''

            cfg = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
            pdfkit.from_string(total_string, out_file + ".pdf", css=os.path.join(self.dir, "html/style.css"),
                               configuration=cfg,
                               options=options)

    def generateJSON(self):
        result = [{'dream': dream, 'image': image} for (dream, image) in self.dreams]
        return json.dumps(result)
