#!/usr/bin/python3

import extract_data
import re
import json
import webbrowser
import os

with open("localize.json") as jsonf:
    l10n = json.load(jsonf)
bar = "\n-----------------"

def get_locale():
    locale = input("Choose a language ・ 言語を選択してください ・ Escoge un idioma:\n\n1. English\t2. 日本語\t3. Español\n")
    if locale == '1':
        return "en"
    elif locale == '2':
        return "jp"
    elif locale == '3':
        return "es"

def get_candidate(locale):
    # PROMPT: Which results would you like to see?  1. Individual candidates  2. Minor candidates combined  3. Voter turnout
    result_type = input(bar+"\n"+l10n["prompts"]["result_type"][locale])
    if result_type == '1':
        print(bar + "\n")
        for k, v in l10n["candidate_map"][locale].items():
            if len(v) == 2:
                print(f'{k}: {v[0]}\t({v[1]})')
            else:
                print(f'{k}: {v[0]}')
        # PROMPT: Choose a candidate:
        candidate_num = input(l10n["prompts"]["candidate_num"][locale])
        candidate = l10n["candidate_map"]["jp"][candidate_num][0]
        candidate_localized = l10n["candidate_map"][locale][candidate_num][0]
        if int(candidate_num) not in range(1, 4): # if not top 3
            extract_data.main(candidate)
            return candidate, candidate_localized
    elif result_type == '2':
        candidate = "others_combined"
        candidate_localized = l10n["misc"]["others_combined"][locale]
    elif result_type == '3':
        candidate = "voter_turnout"
        candidate_localized = l10n["misc"]["voter_turnout"][locale]
    extract_data.main()
    return candidate, candidate_localized

def get_scale(locale):
    print(bar + "\n")
    for k, v in l10n["scale_map"][locale].items():
        print(f'{k}: {v}')
    # PROMPT: Which scale would you like to use?
    scale = input(l10n["prompts"]["scale"][locale])
    scale_localized = l10n["scale_map"][locale][scale]
    return scale, scale_localized

def get_exclude_islands(locale):
    # PROMPT: Exclude outlying islands?  1. Yes  2. No
    exclude_islands = input(bar+l10n["prompts"]["exclude_islands"][locale])
    if re.match("[1Yy]", exclude_islands):
        return True
    elif re.match("[2Nn]", exclude_islands):
        return False

def get_max_and_min(csv_lines, candidate):
    if re.match(f"小池　百合子|石丸　伸二|蓮舫$", candidate): # top 3
        all_percents = [float(re.search(f"{candidate},\d+,([\d.]+)", line).group(1)) for line in csv_lines]
    else:
        lines_split = [line.split(",") for line in csv_lines]
        if candidate == "others_combined":
            all_percents = [float(line[16]) for line in lines_split]
        elif candidate == "voter_turnout":
            all_percents = [float(re.sub("^(\d\d)\.(\d\d)%", r"0.\1\2", line[1])) for line in lines_split]
        else:
            all_percents = [float(line[13]) for line in lines_split]
    max_percent = round(max(all_percents), 3)
    min_percent = round(min(all_percents), 3)
    return max_percent, min_percent

def get_data_block(candidate, scale, line, max_percent, min_percent):
    data_block={'candidate':candidate}
    # raw data
    if re.match(f"小池　百合子|石丸　伸二|蓮舫$", candidate): # top 3
        patt = re.search(f"{candidate},(\d+),([\d.]+),", line)
        data_block['raw votes'] = patt.group(1)
        data_block['raw percent'] = round(float(patt.group(2)), 3)
    else:
        line_split = line.split(",")
        if candidate == "others_combined":
            data_block['raw votes'] = line_split[15]
            data_block['raw percent'] = round(float(line_split[16]), 3)
        elif candidate == "voter_turnout":
            data_block['raw votes'] = "N/A"
            data_block['raw percent'] = round(float(re.sub("^(\d\d)\.(\d\d)%", r"0.\1\2", line_split[1])), 3)
        else:
            data_block['raw votes'] = line_split[12] # always N/A for now
            data_block['raw percent'] = round(float(line_split[13]), 3)
    # weighted percent: 1. MaxMin-scaled, 2. Max-scaled, 3. Unscaled
    diff = max_percent - min_percent
    try:
        if scale == "1":
            data_block['weighted percent'] = round(((data_block['raw percent'] - min_percent) / diff), 3)
        elif scale == "2":
            data_block['weighted percent'] = round((data_block['raw percent'] * (1 / max_percent)), 3)
        elif scale == "3":
            data_block['weighted percent'] = data_block['raw percent']
    except ZeroDivisionError:
        data_block['weighted percent'] = 0.0
    return data_block

def main():
    locale = get_locale()
    candidate, candidate_localized = get_candidate(locale)
    scale, scale_localized = get_scale(locale)
    exclude_islands = get_exclude_islands(locale)

    # repeat until loop broken
    while True:
        with open("data.csv") as dataf:
            if exclude_islands:
                csv_lines = [line.rstrip() for line in dataf.readlines()[1:54]]
            else:
                csv_lines = [line.rstrip() for line in dataf.readlines()[1:]]

        max_percent, min_percent = get_max_and_min(csv_lines, candidate)
        # fill in svg map
        with open("tokyo.svg") as svgf:
            svg_lines = [line for line in svgf.readlines()]

        data_line = 0
        max_svg_line = 64 if exclude_islands else 73
        with open("tokyo_edited.svg", "w") as svgf:
            for i, line in enumerate(svg_lines): # i = svg file line, data_line = data file line
                # fill in candidate, scale, and range on line 10
                if i == 10:
                    line = re.sub('(id="title">)(</tspan>)', rf'\1 {l10n["svg_data"]["title"][locale]}\2', line)
                    line = re.sub('(id="candidate">)(</tspan>)', rf'\1{l10n["svg_data"]["candidate"][locale]}: {candidate_localized}\2', line)
                    line = re.sub('(id="scale">)(</tspan>)', rf'\1{l10n["svg_data"]["scale"][locale]}: {scale_localized}\2', line)
                    line = re.sub('(id="range">)(</tspan>)', rf'\1{l10n["svg_data"]["vote_range"][locale]}: {round(min_percent*100, 3)}%{l10n["svg_data"]["range_marker"][locale]}{round(max_percent*100, 3)}%\2', line)
                # fill each municipality
                # elif 10 < i < 73:
                elif 10 < i < max_svg_line:
                    data_block = get_data_block(candidate, scale, csv_lines[data_line], max_percent, min_percent)
                    # fill opacity
                    weighted_percent = data_block['weighted percent'] # needed in order to avoid triple quotes
                    line = re.sub('fill-opacity=""', f'fill-opacity="{weighted_percent}"', line)
                    # fill in colors and/or stripes
                    color_code = "other_candidate" if not re.match("小池　百合子|石丸　伸二|蓮舫|others_combined|voter_turnout", candidate) else candidate
                    color_map = {'小池　百合子':'red', '石丸　伸二':'green', '蓮舫':'royalblue', 'other_candidate':'darkorange', 'others_combined':'darkmagenta', 'voter_turnout': 'hotpink'}
                    color = color_map[color_code]
                    line_split = csv_lines[data_line].replace("\u3000", " ").split(",") # replace() to avoid regex Unicode bug/error
                    if re.match("蓮舫", line_split[5]):
                        line = re.sub('fill=""', f'fill="url(#{color}-striped)"', line)    
                    else:
                        line = re.sub('fill=""', f'fill="{color}"', line)
                    # fill in hover text stats
                    line = re.sub('#population', f'{l10n["svg_data"]["population"][locale]}', line)
                    line = re.sub('#first_place:', f'{l10n["svg_data"]["first_place"][locale]} - {line_split[2]}: {line_split[3]} / {round(float(line_split[4]) * 100, 3)}%', line)
                    line = re.sub('#second_place:', f'{l10n["svg_data"]["second_place"][locale]} - {line_split[5]}: {line_split[6]} / {round(float(line_split[7]) * 100, 3)}%', line)
                    line = re.sub('#third_place:', f'{l10n["svg_data"]["third_place"][locale]} - {line_split[8]}: {line_split[9]} / {round(float(line_split[10]) * 100, 3)}%', line)
                    line = re.sub('#total_votes:', f'{l10n["svg_data"]["total_votes"][locale]}: {data_block["raw votes"]}', line)
                    line = re.sub('#percentage:', f'{l10n["svg_data"]["percentage"][locale]}: {round(data_block["raw percent"]*100, 3)}%', line)
                    # localize hard-coded JP
                    if locale != "jp":
                        municipality = re.search('name="(.*?)"', line).group(1)
                        line = re.sub('<title>.*?&', f'<title>{l10n["svg_data"]["municipalities"][municipality]}&', line)
                        # for islands in legend
                        line = re.sub('(text-anchor="end">).*?(</text>)', fr'\1{l10n["svg_data"]["municipalities"][municipality]}\2', line)
                        # for top 3 candidates
                        line = re.sub("小池 百合子", "Koike Yuriko", line)
                        line = re.sub("石丸 伸二", "Ishimaru Shinji", line)
                        line = re.sub("蓮舫", "Renho", line)
                    data_line+=1
                # delete islands
                elif exclude_islands and max_svg_line-1 < i < 73:
                    line = re.sub(".*", "", line)
                elif i == 74:
                    line = re.sub("#legend_2nd_place", f'{l10n["svg_data"]["legend_2nd_place"][locale]}', line)
                svgf.write(line)
        webbrowser.open('file://' + os.path.realpath('tokyo_edited.svg'))

        # PROMPT: Open another map?  1. No, exit  2. Start from top  3. Change candidate only  4. Change scale only  5. Toggle islands
        print(f'{bar}\n\n{l10n["misc"]["language"][locale]}, {l10n["svg_data"]["candidate"][locale]}: {candidate_localized}, {l10n["svg_data"]["scale"][locale]}: {scale_localized}, {l10n["misc"]["exclude_islands"][locale]}: {exclude_islands}')
        repeat = input(l10n["prompts"]["repeat"][locale])
        if repeat == '1':
            quit()
        elif repeat == '2':
            main()
        elif repeat == '3':
            candidate, candidate_localized = get_candidate(locale)
        elif repeat == '4':
            scale, scale_localized = get_scale(locale)
        elif repeat == '5':
            exclude_islands = False if exclude_islands else True

main()