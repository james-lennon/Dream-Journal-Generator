import os
import random

import pattern.en
import content_miner

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")

DREAM_SPECS = [
    ['intro', 'action', 'action', 'end'],
    ['loc', 'action', 'action', 'intro', 'action', 'action', 'end'],
    ['loc', 'action', 'action', 'chngloc', 'action', 'action', 'end'],
    ['intro', 'action', 'action', 'chngloc', 'action', 'action', 'end'],
    ['intro', 'action', 'action', 'chngloc', 'action', 'intro', 'action', 'action', 'end']
]


class TemplateComponent:
    def __init__(self):
        self.sections = {}
        self.theme_sections = {}

    def add_entry(self, section, entry):
        if section not in self.sections:
            self.sections[section] = []
        self.sections[section].append(entry)


class DreamContent:
    def __init__(self):
        self.components = {}
        self.iteration = 0

    def _apply_insert(self, query, comp):
        if query not in self.components:
            self.components[query] = []
        self.components[query].append((comp, self.iteration))

    def add_component(self, query, comp):
        self._apply_insert(query, comp)

    def get_component(self, query):
        arr = self.components[query]
        if len(arr) == 0:
            return False
        # return random.sample(arr, 1)[0][0]
        return arr[-1][0]

    def invalidate_last(self):
        for query in self.components:
            entry = self.components[query]
            new_entry = [(comp, i) for (comp, i) in entry if i != self.iteration]
            self.components[query] = new_entry

    def commit(self):
        self.iteration += 1


class DreamTemplate:
    def __init__(self):
        self.components = {}
        self.content = DreamContent()

    def load(self):
        for i in os.listdir(TEMPLATE_PATH):
            if i.endswith(".txt"):
                self._load_template_file(i)

    def _generate_strong(self, query):
        result = False
        while not result:
            result = self.parse_command(query)
            if not result:
                self.content.invalidate_last()
            else:
                self.content.commit()

        result = result[:1].capitalize() + result[1:]
        if result[-1] != '"':
            result += "."
        result += "  "
        return result

    def generate_dream(self):
        result = ""

        spec = random.sample(DREAM_SPECS, 1)[0]
        for entry in spec:
            result += self._generate_strong("load(sent#%s)" % entry)

        return result

    def replace_content(self, query, values):
        parts = query.split("#")
        comp = self._get_component(query)
        if parts[1] not in comp.sections:
            raise ValueError("Section doesn't exist", query)
        comp.sections[parts[1]] = values

    def _load_template_file(self, filename):
        full_filename = os.path.join(TEMPLATE_PATH, filename)

        current_section = ""
        component = TemplateComponent()

        with open(full_filename, "r") as openfile:
            lines = openfile.readlines()
            for line in lines:
                if len(line) <= 1:
                    continue
                if line[0] == "#":
                    section_name = line[1:len(line) - 1]
                    current_section = section_name
                else:
                    component.add_entry(current_section, line[0:len(line) - 1])
        self.components[filename.split(".")[0]] = component

    def _get_component(self, query):
        parts = query.split("#")
        if len(parts) > 2:
            raise ValueError('Bad query string', query)

        if parts[0] not in self.components:
            raise ValueError('Component not found', parts[0])
        return self.components[parts[0]]

    def _pick_random_component(self, query):
        parts = query.split("#")
        if len(parts) > 2:
            raise ValueError('Bad query string', query)

        if parts[0] not in self.components:
            raise ValueError('Component not found', parts[0])
        comp = self.components[parts[0]]

        section_name = "" if len(parts) == 1 else parts[1]
        if section_name not in comp.sections:
            raise ValueError('Section not found', section_name, query)
        if section_name in comp.theme_sections:
            values = comp.theme_sections[section_name]
        else:
            values = comp.sections[section_name]
        if len(values) < 1:
            return False
        return self.parse_entry(random.sample(values, 1)[0])

    def _find_close(self, str, pos, delim, cdelim):
        d = 0
        endpos = -1
        for i in range(pos + 1, len(str)):
            if str[i] == cdelim:
                if d == 0:
                    endpos = i
                    break
                else:
                    d -= 1
            elif str[i] == delim:
                d += 1
        return endpos

    def parse_entry(self, entry):
        result = ""

        pos = entry.find("{")
        endpos = -1
        if pos == -1:
            return entry

        while pos != -1:
            result += entry[endpos + 1:pos]

            endpos = self._find_close(entry, pos, "{", "}")

            cmd = entry[pos + 1:endpos]
            val = self.parse_command(cmd)
            if not val:
                return False
            result += val
            pos = entry.find("{", endpos)

        result += entry[endpos + 1:]

        return result

    def parse_command(self, cmd):
        paren1 = cmd.find("(")
        paren2 = cmd.rfind(")")

        if paren1 == -1 or paren2 == -1:
            raise ValueError('Bad command string', cmd)

        try:
            fxn = cmd[0:paren1]
            args = cmd[paren1 + 1:paren2].split(",")
            if fxn == "load":
                return self._load_component(args)
            elif fxn == "enum":
                return self._enum(args)
            elif fxn == "reuse":
                return self._reuse(args)
            elif fxn == "prob":
                return self._prob(args)
        except Exception as ex:
            print "Error with command:", cmd
            print ex
            return False

    def _apply_property(self, word, args):
        if not word:
            return False, False
        index_str = word[word.find("<"):word.rfind(">")]
        index = False
        if len(index_str) > 0:
            index = int(index_str[1:])

        result = word.split("<")[0]
        after = False if index is False else "<%i>" % index
        if len(args) > 1:
            parts = result.split(" ")
            first = parts[0]
            rest = ' ' + ' '.join(parts[1:]) if len(parts) > 1 else ""

            if args[1] == "plur":
                if index is not False:
                    result = ' '.join(parts[:index]) + pattern.en.pluralize(
                        pattern.en.singularize(parts[index])) + ' ' + ' '.join(parts[index + 1:])
                else:
                    result = pattern.en.pluralize(pattern.en.singularize(word))
            elif args[1] == "ger":
                result = pattern.en.conjugate(pattern.en.conjugate(first), "part") + rest
            elif args[1] == "past":
                result = pattern.en.conjugate(pattern.en.conjugate(first), 'p') + rest
        return result, after

    def _load_component(self, args):
        if len(args) == 0:
            raise ValueError("Invalid number of arguments passed to load", args)

        while True:
            word = self._pick_random_component(args[0])

            word, after = self._apply_property(word, args)

            if args[0] not in self.content.components or word not in self.content.components[args[0]]:
                break
        if after is not False:
            self.content.add_component(args[0], word+after)
        else:
            self.content.add_component(args[0], word)
        return word

    def _enum(self, args):
        text = ",".join(args)

        options = text.split("|")
        return self.parse_entry(random.sample(options, 1)[0])

    def _reuse(self, args):
        if len(args) == 0 or len(args) > 3:
            raise ValueError("Invalid arguments given to reuse", args)

        strict = False
        if len(args) > 1 and args[-1] == "strict":
            strict = True

        if args[0] not in self.content.components:
            if strict:
                return False
            else:
                return self._load_component(args)
        else:
            word = self.content.get_component(args[0])
            result, after = self._apply_property(word, args)
            return result

    def _prob(self, args):
        if len(args) == 0:
            raise ValueError("Invalid number of arguments for prob", args)
        prob = 0.5
        if len(args) == 2:
            prob = float(args[1])

        if random.random() < prob:
            return self.parse_entry(args[0])
        return ""

    def reset(self):
        self.content = DreamContent()

    def add_theme(self, theme_str):
        mined_content = content_miner.mine(theme_str)
        for query in mined_content:
            new_values = list(mined_content[query])
            if len(new_values) == 0:
                continue
            parts = query.split("#")
            comp = self._get_component(query)
            comp.theme_sections[parts[1]] = list(mined_content[query])
