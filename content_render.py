import pdfkit
import time
import content_parser
import dream_images


class DreamJournal:
    def __init__(self):
        self.content = ""
        self._load_cover("html/cover.html")
        self.image_urls = set()

    def _load_cover(self, cover_file):
        with open(cover_file, "r") as openfile:
            html_string = openfile.read().replace("{date}", time.strftime("%d.%m.%Y %H:%M:%S %p"))
            self.content += html_string + "<div style='page-break-before:always'></div>"

    def generate_dreams(self, count, tmp=None):
        if tmp is None:
            tmp = content_parser.DreamTemplate()
            tmp.load()
        for i in range(0, count):
            tmp.reset()
            dream = tmp.generate_dream()
            noun = False
            if "noun#char" in tmp.content.components:
                noun = tmp.content.components["noun#char"][0]
            img = False
            if noun:
                img = dream_images.get_photo(noun, surreal=False)
            if img not in self.image_urls:
                self.image_urls.add(img)
                self.add_dream(dream, img)

    def add_dream(self, dream, image=''):
        template_file = "html/entry1.html"

        with open(template_file, "r") as openfile:
            html_string = openfile.read()

            html_string = html_string.replace("{content}", dream)
            if not image:
                image = ''
            html_string = html_string.replace("{image}", image)
            self.content += html_string + "<div style='page-break-before:always'></div>"

    def render(self, out_file):
        cfg = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        pdfkit.from_string(self.content, out_file, css="html/style.css", configuration=cfg)


def render(template_file, content, image=''):
    with open(template_file, "r") as openfile:
        html_string = openfile.read()

        html_string = html_string.replace("{content}", content)
        html_string = html_string + "<div style='page-break-before:always'></div>" + html_string

        pdf = pdfkit.from_string(html_string, False, css="html/style.css")

    with open("out.pdf", "w") as outfile:
        outfile.write(pdf)


if __name__ == '__main__':
    render("html/entry1.html", "yo this is a dream, man.")
