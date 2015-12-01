import pdfkit


def render(template_file, content, image=None):
    with open(template_file, "r") as openfile:
        html_string = openfile.read()

        html_string = html_string.replace("{content}", content)

        pdfkit.from_string(html_string, "out.pdf", css="html/style.css")


if __name__ == '__main__':
    render("html/entry1.html", "yo this is a dream, man.")
