# http://www.gilesthomas.com/2010/05/generating-political-news-using-nltk/

import content_parser
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

tmp = content_parser.DreamTemplate()
tmp.load()
print tmp.parse_command("load(sent#intro)")
print tmp.parse_command("load(sent#action)")
print tmp.parse_command("load(sent#action)")
print tmp.parse_command("load(sent#end)")

# noun = tmp.content.components["noun#char"][0]
# print dream_images.get_photo(noun, surreal=True)
