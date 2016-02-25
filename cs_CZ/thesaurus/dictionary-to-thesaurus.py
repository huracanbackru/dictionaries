#!/usr/bin/env python
# coding=utf-8
#
# This file is part of the LibreOffice project.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

# This utility translates a normal dictionary (in this case English/Czech)
# into a thesaurus for one of the languages (in this case Czech).
#
# Based on idea of Zdenek Zabokrtsky <zabokrtsky@ufal.mff.cuni.cz>, big
# thanks! :-)

import os
import re
import sys

# add here the Czech words we want to leave out from the thesaurus generation
# (misbehaving, mistranslated, etc.)
ignore_words = [
    '?',
    '(by the way)',
    '(po)štvat',
    '14. písmeno hebrejské abecedy',
]

def usage():
    message = """Usage: {program} slovnik_data_utf8.txt

  slovnik_data_utf8.txt: Dictionary data from http://slovnik.zcu.cz/download.php"""
    print(message.format(program = os.path.basename(sys.argv[0])))

def classify(typ):
    if typ == '':
        return ''
    elif typ == 'adj':
        return '(příd. jm.)'
    elif typ == 'adv':
        return '(přísl.)'
    elif typ == 'n':
        return '(podst. jm.)'
    elif typ == 'v':
        return '(slov.)'

    return ''

def parse(filename):
    synonyms = {}
    meanings = {}

    match_ignore = re.compile('(\[neprav\.\]|\[vulg\.\])')
    match_cleanup = re.compile('(\[.*\]|\*|:.*)')

    with open(filename, "r") as fp:
        for line in fp:
            if (line == ''):
                continue
            elif (line[0] == '#'):
                continue
            else:
                terms = line.split('\t')
                if (terms[0] == '' or len(terms) < 2):
                    continue

                index = terms[0].strip()
                if (index == ''):
                    continue

                word = terms[1].strip()
                if (word != '' and word[0] == '"' and word[len(word)-1] == '"'):
                    word = word.strip('" ')

                if (word == '' or word in ignore_words):
                    continue

                typ = ''
                if (len(terms) >= 2):
                    typ = terms[2]

                    # ignore non-translations
                    if match_ignore.search(typ) != None:
                        continue

                    typ = match_cleanup.sub('', typ)
                    typ = typ.strip()

                typ = classify(typ)

                if index in synonyms:
                    synonyms[index].append( (word, typ) )
                else:
                    synonyms[index] = [ (word, typ) ]

                if word in meanings:
                    meanings[word].append(index)
                else:
                    meanings[word] = [ index ]

    return (synonyms, meanings)

def buildThesaurus(synonyms, meanings):
    # for every word:
    #   find all the indexes, and then again map the indexes to words - these are the synonyms
    for word in sorted(meanings.keys()):
        # we assume that various indexes (english words here) are various
        # meanings; not generally true, but...
        indexes = meanings[word]

        # we want to output each word just once
        used_this_round = [ word ]

        output_lines = []
        for index in indexes:
            syns = synonyms[index]

            # collect types first
            types = []
            for (w, t) in syns:
                if not t in types:
                    types.append(t)

            line = {}
            for syn in syns:
                (w, t) = syn
                if not w in used_this_round:
                    if t in line:
                        line[t] += '|' + w
                    else:
                        line[t] = '|' + w
                    used_this_round.append(w)

            if len(line) != 0:
                for t in types:
                    if t in line:
                        output_lines.append(t + line[t])

        if len(output_lines) > 0:
            print word + '|' + str(len(output_lines))
            for line in output_lines:
                print line

def main(args):
    if (len(args) != 2):
        usage()
        sys.exit(1)

    (synonyms, meanings) = parse(args[1])

    print "UTF-8"
    buildThesaurus(synonyms, meanings)

if __name__ == "__main__":
    main(sys.argv)

# vim:set shiftwidth=4 softtabstop=4 expandtab:
