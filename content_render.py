import random
import time

import pdfkit

import content_parser
import dream_images

NUM_HTML_TEMPLATES = 3


class DreamJournal:
    def __init__(self):
        self.dream_text = ""
        self.content = ""
        self._load_cover("html/cover.html")
        self.image_urls = set()

    def _load_cover(self, cover_file):
        with open(cover_file, "r") as openfile:
            html_string = openfile.read().replace("{date}", time.strftime("%d.%m.%Y %H:%M:%S %p"))
            self.content += html_string + "<div style='page-break-before:always'></div>"

    def generate_dreams(self, count, tmp=None, add_images=True):
        if tmp is None:
            tmp = content_parser.DreamTemplate()
            tmp.load()
        for i in range(0, count):
            print "[Generating Dream %d]" % (i + 1)

            tmp.reset()
            dream = tmp.generate_dream()
            img = ""
            if add_images:
                noun = False
                if "noun#char" in tmp.content.components:
                    noun = tmp.content.components["noun#char"][0]
                img = False
                if noun:
                    img = dream_images.get_photo(noun, surreal=False)
                if img in self.image_urls:
                    img = ""
                else:
                    self.image_urls.add(img)
            self.add_dream(dream, img)

    def add_dream(self, dream, image=''):
        self.dream_text += dream + "\n\n"
        template_file = "html/entry%i.html" % random.randrange(1, NUM_HTML_TEMPLATES + 1)

        with open(template_file, "r") as openfile:
            html_string = openfile.read()

            html_string = html_string.replace("{content}", dream)
            if not image:
                image = ''
            html_string = html_string.replace("{image}", image)
            self.content += html_string + "<div style='page-break-before:always'></div>"

    def render(self, out_file, pdf=True):
        print "[Saving Text]"
        with open(out_file + ".txt", "w") as txtfile:
            txtfile.write(self.dream_text)

        if pdf:
            print "[Generating PDF]"

            options = {
                'page-size': 'Letter',
                'margin-top': '0in',
                'margin-right': '0in',
                'margin-bottom': '0in',
                'margin-left': '0in',
                'encoding': "UTF-8",
                'no-outline': None
            }

            cfg = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
            pdfkit.from_string(self.content, out_file + ".pdf", css="html/style.css", configuration=cfg)
