import os
import random

import pattern.en

TEMPLATE_PATH = os.path.join(".", "templates")


class TemplateComponent:
    def __init__(self):
        self.sections = {}

    def add_entry(self, section, entry):
        if section not in self.sections:
            self.sections[section] = []
        self.sections[section].append(entry)


class DreamContent:
    def __init__(self):
        self.components = {}

    def add_component(self, query, comp):
        if query not in self.components:
            self.components[query] = []
        self.components[query].append(comp)


class DreamTemplate:
    def __init__(self):
        self.components = {}
        self.content = DreamContent()

    def load(self):
        for i in os.listdir(TEMPLATE_PATH):
            if i.endswith(".txt"):
                self._load_template_file(i)

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

    def _load_component(self, args):
        if len(args) == 0:
            raise ValueError("Invalid number of arguments passed to load", args)

        while True:
            word = self._pick_random_component(args[0])

            if len(args) > 1:
                parts = word.split(" ")
                first = parts[0]
                rest = ' ' + ' '.join(parts[1:]) if len(parts) > 1 else ""

                if args[1] == "plur":
                    word = pattern.en.pluralize(word)
                elif args[1] == "ger":
                    word = pattern.en.conjugate(first, "part") + rest
                elif args[1] == "past":
                    word = pattern.en.conjugate(first, 'p') + rest

            if args[0] not in self.content.components or word not in self.content.components[args[0]]:
                break
        self.content.add_component(args[0], word)
        return word

    def _enum(self, args):
        text = ",".join(args)

        options = text.split("|")
        return self.parse_entry(random.sample(options, 1)[0])

    def _reuse(self, args):
        if len(args) == 0:
            raise ValueError("Invalid arguments given to reuse", args)

        strict = False
        if len(args) > 1 and args[1] == "strict":
            strict = True

        if args[0] not in self.content.components:
            if strict:
                return False
            else:
                return self._load_component(args)
        else:
            list = self.content.components[args[0]]
            return random.sample(list, 1)[0]

    def _prob(self, args):
        if len(args) == 0:
            raise ValueError("Invalid number of arguments for prob", args)
        prob = 0.5
        if len(args) == 2:
            prob = float(args[1])

        if random.random() < prob:
            return self.parse_entry(args[0])
        return ""
