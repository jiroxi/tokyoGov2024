#!/usr/bin/python3

import re

def main(candidate="ＡＩメイヤー"):
    with open("data.txt") as inputf:
        lines = [line.rstrip() for line in inputf.readlines()]

    # extract useful data
    raw_data = []
    counter = 0
    results_started = False
    while counter < len(lines):
        if re.search("[市区町村]投票率", lines[counter]):
            raw_data.append(lines[counter:counter+7])
            results_started = True
            counter+=7
        # Enter any other candidate
        elif re.search(candidate, lines[counter]) and results_started:
            raw_data[-1].extend(lines[counter:counter+2])
            counter+=2
        else:
            counter+=1

    # format raw data and print to csv
    with open("data.csv", "w") as outputf:
        outputf.write(f"Municipality,Turnout,Candidate1,Votes,Percentage,Candidate2,Votes,Percentage,Candidate3,Votes,Percentage,CandidateOther,Votes,Percentage,Others,Votes,Percentages\n")
        for datum in raw_data:
            elements = []
            turnout = re.search("^(.*?[市区町村])投票率([\d.]+%)開票終了", datum[0])
            elements.extend([turnout.group(1), turnout.group(2)])
            # candidate 1
            elements.append(datum[1])
            candidate1 = re.search("(^[\d,]+?)（([\d.]+%)", datum[2])
            elements.extend([candidate1.group(1).replace(",", ""), str(float(candidate1.group(2).replace("%", ""))/100)])
            # candidate 2
            elements.append(datum[3])
            candidate2 = re.search("(^[\d,]+?)（([\d.]+%)", datum[4])
            elements.extend([candidate2.group(1).replace(",", ""), str(float(candidate2.group(2).replace("%", ""))/100)])
            # candidate 3
            elements.append(datum[5])
            candidate3 = re.search("(^[\d,]+?)（([\d.]+%)", datum[6])
            elements.extend([candidate3.group(1).replace(",", ""), str(float(candidate3.group(2).replace("%", ""))/100)])
            # candidate 4 - manually entered candidate
            elements.append(datum[7])
            candidate_other = re.search("(^[\d,]+?)（([\d.]+%)", datum[8])
            elements.extend([candidate_other.group(1).replace(",", ""), str(float(candidate_other.group(2).replace("%", ""))/100)])
            # all others
            elements.extend(['その他', 'N/A', str(1 - float(elements[4]) - float(elements[7]) - float(elements[10]))])

            outputf.write(','.join(elements)+"\n")

if __name__ == "__main__": 
    main() 