import pdfkit


class DreamJournal:
    def __init__(self):
        self.content = ""

    def add_dream(self, dream, image=False):
        template_file = "html/entry1.html"

        with open(template_file, "r") as openfile:
            html_string = openfile.read()

            html_string = html_string.replace("{content}", dream)
            if image:
                html_string = html_string.replace("{image}", image)
            print html_string
            self.content += html_string + "<div style='page-break-before:always'></div>"

    def render(self, out_file):
        cfg = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        pdfkit.from_string(self.content, out_file, css="html/style.css", configuration=cfg)


def render(template_file, content, image=None):
    with open(template_file, "r") as openfile:
        html_string = openfile.read()

        html_string = html_string.replace("{content}", content)
        html_string = html_string + "<div style='page-break-before:always'></div>" + html_string

        pdf = pdfkit.from_string(html_string, False, css="html/style.css")

    with open("out.pdf", "w") as outfile:
        outfile.write(pdf)


if __name__ == '__main__':
    render("html/entry1.html", "yo this is a dream, man.")
