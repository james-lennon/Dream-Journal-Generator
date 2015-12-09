# http://www.gilesthomas.com/2010/05/generating-political-news-using-nltk/

import content_parser
import content_render
import dream_images

# load dreams from file
# with open("data/dream_data.txt", "r") as dream_file:
#     dream_text = dream_file.read()

# split into individual entries
# dreams = dream_text.split("####")
# context = dream_generator.DreamContext()
# for d in dreams:
#     context.add_dream_text(d)

# print dream_generator.generate_dream(context)
# print dream_generator.mutate_dream(dreams[1], context)

# dream_generator.test(dreams)


# content_render.render("html/entry1.html", dream)

# print dream

journal = content_render.DreamJournal()

journal.generate_dreams(10, add_images=False)

journal.render("out")
