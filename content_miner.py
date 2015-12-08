from pattern.en import parsetree, conjugate, singularize
import content_parser
import content_render

content = """
Mr. and Mrs. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people you'd expect to be involved in anything strange or mysterious, because they just didn't hold with such nonsense.
Mr. Dursley was the director of a firm called Grunnings, which made drills. He was a big, beefy man with hardly any neck, although he did have a very large mustache. Mrs. Dursley was thin and blonde and had nearly twice the usual amount of neck, which came in very useful as she spent so much of her time craning over garden fences, spying on the neighbors. The Dursleys had a small son called Dudley and in their opinion there was no finer boy anywhere.
The Dursleys had everything they wanted, but they also had a secret, and their greatest fear was that somebody would discover it. They didn't think they could bear it if anyone found out about the Potters. Mrs. Potter was Mrs. Dursley's sister, but they hadn't met for several years;
in fact, Mrs. Dursley pretended she didn't have a sister, because her
sister and her good-for-nothing husband were as unDursleyish as it was possible to be. The Dursleys shuddered to think what the neighbors would say if the Potters arrived in the street. The Dursleys knew that the
Potters had a small son, too, but they had never even seen him. This boy was another good reason for keeping the Potters away; they didn't want Dudley mixing with a child like that.
Then Mr. and Mrs. Dursley woke up on the dull, gray Tuesday our story starts, there was nothing about the cloudy sky outside to suggest that strange and mysterious things would soon be happening all over the country. Mr. Dursley hummed as he picked out his most boring tie for work, and Mrs. Dursley gossiped away happily as she wrestled a screaming Dudley into his high chair.
None of them noticed a large, tawny owl flutter past the window
"""


def mine(text):
    result = {"noun#item": set(), "noun#char": set(), "verb#actionobj": set(), "verb#action": set(), "prep": set()}
    tree = parsetree(text, relations=True)
    for sentence in tree:
        result["prep"] = set([p.string for p in sentence.pnp])
        for p in sentence.phrases:
            if p.type == "VP":
                print p, p.subject, p.object

                has_obj = False
                if p.subject is not None:
                    result["noun#char"].add(singularize(p.subject.string))
                if p.object is not None:
                    has_obj = True
                    result["noun#item"].add(singularize(p.object.string))
                key = "verb#actionobj" if has_obj else "verb#action"
                result[key].add(conjugate(p.string))
        #
        # for chunk in sentence.chunks:
        #     print chunk.type, [(w.string, w.type) for w in chunk.words]
        print
    return result


def load(text, template):
    dict = mine(text)
    for key in dict:
        print key
        try:
            template.replace_content(key, dict[key])
        except ValueError as e:
            print e


if __name__ == '__main__':
    tmp = content_parser.DreamTemplate()
    tmp.load()

    with open("data/dream_data.txt", "r") as openfile:
        content = openfile.read()

    load(content, tmp)

    journal = content_render.DreamJournal()

    journal.generate_dreams(5, tmp)

    journal.render("out")

