import csv
import sys
import pinyin_jyutping
import hanzidentifier

if len(sys.argv) == 1:
    print("No input file was provided")
    exit(1)
elif len(sys.argv) == 2:
    print("No output file was provided")
    exit(1)

print("Loading sentences from \"" + sys.argv[1] + "\"")
with open(sys.argv[1], mode="r", encoding="utf-8-sig") as input:
    with open(sys.argv[2], mode="w") as output:

        reader = csv.reader(input, delimiter="\t", quotechar='"')
        writer = csv.writer(output, delimiter="\t", quotechar='"')
        writer.writerow(["simplified", "traditional", "pinyin", "translation"])
        p = pinyin_jyutping.PinyinJyutping()

        # we don't want duplicate translations so we need a set to keep
        # track of the already added sentence ids
        opened_sentence_ids = set()

        # check that we are actually parsing a csv file with 4 columns
        if len(next(reader)) != 4:
            print("The given csv file did not have 4 columns")
            exit(1)
        input.seek(0)

        for row in reader:

            # hopefully at least the first one was correct,
            # but there might be rows that are faulty. So
            # we skip those
            if len(row) != 4:
                print("Column count didn't match. Skipping.\n" + str(row))
                continue
            
            # add the id to the set so that we 
            # can skip duplicates
            if row[0] in opened_sentence_ids:
                continue
            opened_sentence_ids.add(row[0])

            # remove the dot at the end
            row[1] = row[1].removesuffix("。")

            # the only reason we need this is to make a string where all the
            # words in character form are separated. This makes it easier to search for
            words = p.pinyin_all_solutions(row[1])

            # make the character string from the tokens
            separated = ""
            for char in words["word_list"]:
                separated += char
                separated += " "
            separated = separated.removesuffix(" ")

            # check if the string is simplified or traditional.
            # or both?
            simplified = "NULL"
            traditional = "NULL"
            if hanzidentifier.is_simplified(row[1]):
                simplified = separated
            if hanzidentifier.is_traditional(row[1]):
                traditional = separated

            # write!
            writer.writerow([simplified, traditional, p.pinyin(row[1], tone_numbers=True), row[3]])

print("Done!")