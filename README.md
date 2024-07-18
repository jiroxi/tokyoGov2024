This project attempts to create a NY Times-style interactive election results tool for the 2024 Tokyo gubernational elections as both a tool for personal use, and for practice in Python, SVG/XML, and data visualization. 


--- BACKGROUND ---
After the PM of Japan, the governor of Tokyo Prefecture (pop. 14 million) is the most important position in the country. Many elections in Japan are not competitive, with the right-wing LDP holding power nationally for the entirety of the post-WWII era save for 4 years.

This election was expected to be a proxy match-up between Koike Yuriko, the incumbent and first female governor of Tokyo being supported by right-wing parties, and Renho, a former leader of an opposition party and notably also female, supported by a left-wing coalition. The biggest electoral surprise was the breakneck rise of Ishimaru Shinji, an obscure small-town mayor from Hiroshima who managed to place second in almost every municipality (and handing Koike a landslide victory in the process). 

Besides the top 3, the other 53 candidates included many xenophobic and/or joke candidates including virtual avatars, a porn star, the Joker, and many candidates from a party with an unmitigated vendetta against the national broadcaster (see meme: https://x.com/nagystephen1/status/1806605483282727190). This is par for the course for Japanese elections given the nature of their often foregone outcomes.

Geographically, roughly speaking in the eastern third of Tokyo lie the hyper-populated former wards of the former Tokyo City; in the middle third are the post-war growth and populous inner suburbs, while the western third represents more industrial and rural areas of Tokyo. The islands are represented by boxes in the lower left corner. 

--- HOW TO RUN ---
`run.py` is a Python script run on the Terminal in a continuous loop, creating and opening an SVG map of Tokyo based on options it is supplied and opened in the default web browser. These options can be changed at the end of each cycle. The map is mostly unlabeled but hovering over each municipality reveals general and option-specific information. 

The flow is as follows:
[Locale]  -->  [Result type]  (-->  [Candidate list])  -->  [Scale]  -->  [Exclude islands?]  -->  [Repeat]

- [Locale]: Choose between English, Japanese, Spanish (all menu options and data)
- [Result type]: Choose between an individual candidate's data, all non-top3 candidates combined, or voter turnout
    - [Candidate list]: If the individual candidate option is selected, each candidate will be shown in order of votes along with noteworthy comments. However, vote numbers fall sharply after the top 3 and many fringe candidates will basically have no data to show. 
- [Scale]: Choose between scaled or unscaled maps, where percentage is equal to color opacity for each municipality. The MaxMin scaled map is recommended for maximum gradient difference, especially with any candidate other than the top 3.
- [Exclude islands?]: Tokyo is home to 9 outlying island municipalities on a technicality, the farthest inhabited island of which lies 1028km/638mi from mainland Tokyo. These small communities can heavily skew the data so there is an option to exclude their data. 
- [Repeat]: At the end of the loop, a choice is given to end the loop, restart the loop, or change individual options


--- HOW IT WORKS ---
`data.txt` is the result of copying and pasting all text from https://www3.nhk.or.jp/senkyo2/shutoken/20336/skh54664.html after municipal data is expanded. Results seem to be final, but if there was to be a change in data, repeating the copy-paste process would theoretically automatically update the map data.

`extract_data.py` looks for relevant data and outputs it to `data.csv`. 

`localize.json` contains localization options for the 3 supported languages.

`tokyo.svg` is a modified version of an existing SVG found here courtesy of Danyel Koca: https://www.danyelkoca.com/tokyo.svg 

`run.py` collects all options, creates all data necessary including weighted scores, and edits the SVG map line-by-line in tandem with the CSV file and generated data and outputs it into `tokyo_edited.svg` which opens automatically. 


--- EXAMPLE RESULTS ---
1. Individual Candidates  -->  2. Ishimaru Shinji  -->  2. MaxMin-scaled  -->  1 Yes (exclude)
This result shows how Ishimaru's support was stronger in the younger and richer inner wards which tracks well with his apparent support from younger men.

1. Individual Candidates  -->  3. Renho  -->  2. MaxMin-scaled  -->  1 Yes (exclude)
In contrast, Renho's support is concentrated in the outer wards and the inner suburbs west of the old city center. About half of the municipalities she came in second are also clustered here.

2. Minor candidates combined  -->  2. MaxMin-scaled  -->  2. No (include)
This result shows a deep contrast between the inner wards and the rural areas (extreme west and the islands) in their willingness to support candidates that are highly unlikely to win. While the two westernmost rural municipalities have Renho coming in 2nd, this is deceptive as these same communities gave Koike the highest support and rather it belies their reluctance to vote for non-established candidates (including the newly legitimized Ishimaru).

3. Voter turnout  -->  2. MaxMin-scaled  -->  Toggle between both
This result shows how the islands can skew the results in weighted graphs. Max voter turnout jumps from 68% to 84% when including the islands. I guess Election Day really breaks the monotony of life on these slow-paced islands! 

1. Individual Candidates  -->  9. Sakurai Makoto  -->  2. Max-scaled  -->  2. No (include)
This result shows a clear pattern that support for Sakurai Makoto, the most high-profile of the ultra-right xenophobic candidates, is concentrated in Shitamachi (the oldest area of Tokyo which is associated with the working class and native Tokyo roots). His max support still stands at only 1.7% though.


--- FUTURE STEPS ---
・ In a future similar project, I will use BeautifulSoup or another web scraper to scrape javascript objects from the site to eliminate the need to copy-paste for real-time results, and to safeguard against a simple UI change breaking the whole program. 
・ Learning some javascript and hosting this on a web server would make it far less cumbersome and reliant on fugly SVG text objects. At the time of this writing I have zero javascript skills to rely on. 
