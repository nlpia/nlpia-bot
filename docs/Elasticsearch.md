# Relevance tuning in Elasticsearch

General search query form:

```
client.search(index='', body=query_body)
```

## Basic match query and results

```

query_body={"query": {"match": 
                        {"text": text}
                    }
            }
```

**Question: "Barak Obama**

Result 0:
Title: Ta-Nehisi Coates
Relevance score 6.412328
Result 1:
Title: Bill Clinton
Relevance score 6.4054484
Result 2:
Title: Jeff Mariotte
Relevance score 5.983801
Result 3:
Title: Sean Murphy (artist)
Relevance score 5.7749376
Result 4:
Title: Open information extraction
Relevance score 5.435918
Result 5:
Title: Named entity
Relevance score 4.9300184
Result 6:
Title: Information extraction
Relevance score 3.9993434
Result 7:
Title: Rashida Jones
Relevance score 3.972412
Result 8:
Title: Amber Benson
Relevance score 3.8804646
Result 9:
Title: Jason Rubin
Relevance score 3.7065945

**Question: "When Barack Obama was inaugurated?**

Result 0:
Title: Jeff Mariotte
Relevance score 12.389853
Result 1:
Title: Named entity
Relevance score 12.173271
Result 2:
Title: Ta-Nehisi Coates
Relevance score 11.393703
Result 3:
Title: Amber Benson
Relevance score 9.310086
Result 4:
Title: Eric Millikin
Relevance score 8.667373
Result 5:
Title: Jason Rubin
Relevance score 8.582391
Result 6:
Title: Information extraction
Relevance score 8.356649
Result 7:
Title: Rashida Jones
Relevance score 7.7038317
Result 8:
Title: Barack Obama
Relevance score 7.4432054
Result 9:
Title: Alex Ross
Relevance score 6.7125754


**Question: "Stan Lee"**
Result 0:
Title: Danny Fingeroth
Relevance score 7.5711374
Result 1:
Title: The Incredible Hulk (1978 TV series)
Relevance score 7.4405317
Result 2:
Title: Daniel Keyes
Relevance score 7.2441754
Result 3:
Title: Leon Lazarus
Relevance score 7.224835
Result 4:
Title: Jim Salicrup
Relevance score 7.04164
Result 5:
Title: Jack Kirby
Relevance score 6.9100504
Result 6:
Title: Mike Sekowsky
Relevance score 6.801542
Result 7:
Title: Tom Spurgeon
Relevance score 6.6907864
Result 8:
Title: Steve Ditko
Relevance score 6.6573367
Result 9:
Title: Colleen Doran
Relevance score 6.648614

## Multi-field match

```
query_body = \
{
  "query": {
    "multi_match" : {
      "query":    question, 
      "fields": [ "title", "text" ] 
    }
  }
}
```

**Question: "Barak Obama"**

Result 0:
Title: Ta-Nehisi Coates
Relevance score 6.412328
Result 1:
Title: Bill Clinton
Relevance score 6.4054484
Result 2:
Title: Jeff Mariotte
Relevance score 5.983801
Result 3:
Title: Sean Murphy (artist)
Relevance score 5.7749376
Result 4:
Title: Open information extraction
Relevance score 5.435918
Result 5:
Title: Named entity
Relevance score 4.9300184
Result 6:
Title: Information extraction
Relevance score 3.9993434
Result 7:
Title: Rashida Jones
Relevance score 3.972412
Result 8:
Title: Barack Obama
Relevance score 3.9296012
Result 9:
Title: Amber Benson
Relevance score 3.8804646

**Question: "Stan Lee"**
Result 0:
Title: Danny Fingeroth
Relevance score 7.5711374
Result 1:
Title: The Incredible Hulk (1978 TV series)
Relevance score 7.4405317
Result 2:
Title: Daniel Keyes
Relevance score 7.2441754
Result 3:
Title: Leon Lazarus
Relevance score 7.224835
Result 4:
Title: Jim Salicrup
Relevance score 7.04164
Result 5:
Title: Jack Kirby
Relevance score 6.9100504
Result 6:
Title: Mike Sekowsky
Relevance score 6.801542
Result 7:
Title: Tom Spurgeon
Relevance score 6.6907864
Result 8:
Title: Steve Ditko
Relevance score 6.6573367
Result 9:
Title: Colleen Doran
Relevance score 6.648614

## Multi-field query with dynamic boosting

```
query_body = \
    {
      "query": {
        "bool": {
          "should": [
            {
              "match": {
                "title": {
                  "query": question,
                  "boost": 3
                }
              }
            },
            {
              "match": { 
                "text": question
              }
            }
          ]
        }
      }
    }
```

**Question: "Stan Lee"**

Result 0:
Title: Stan Hart
Relevance score 23.337877
Result 1:
Title: Stan Sakai
Relevance score 23.046766
Result 2:
Title: Jim Lee
Relevance score 20.845459
Result 3:
Title: Elaine Lee
Relevance score 20.052559
Result 4:
Title: Jae Lee
Relevance score 20.046019
Result 5:
Title: Lee Weeks
Relevance score 19.805822
Result 6:
Title: Lee Kohse
Relevance score 18.244556
Result 7:
Title: Lee Falk
Relevance score 18.161747
Result 8:
Title: Stan Lee
Relevance score 16.223131
Result 9:
Title: Jen Lee (cartoonist)
Relevance score 15.996904

**Question:"Barack Obama"**

Result 0:
Title: Barack Obama
Relevance score 30.086086
Result 1:
Title: Jeff Mariotte
Relevance score 12.265584
Result 2:
Title: Ta-Nehisi Coates
Relevance score 10.39148
Result 3:
Title: Named entity
Relevance score 10.281631
Result 4:
Title: Amber Benson
Relevance score 7.9541693
Result 5:
Title: Jason Rubin
Relevance score 7.5977707
Result 6:
Title: Eric Millikin
Relevance score 7.534538
Result 7:
Title: Information extraction
Relevance score 6.822109
Result 8:
Title: Rashida Jones
Relevance score 6.6595664
Result 9:
Title: Sean Murphy (artist)
Relevance score 5.7749376

**Question: "When Barack Obama was enaugurated?**

Result 0:
Title: Barack Obama
Relevance score 31.020813
Result 1:
Title: Jeff Mariotte
Relevance score 12.389853
Result 2:
Title: Named entity
Relevance score 12.173271
Result 3:
Title: Ta-Nehisi Coates
Relevance score 11.393703
Result 4:
Title: Amber Benson
Relevance score 9.310086
Result 5:
Title: Eric Millikin
Relevance score 8.667373
Result 6:
Title: Jason Rubin
Relevance score 8.582391
Result 7:
Title: Information extraction
Relevance score 8.356649
Result 8:
Title: Rashida Jones
Relevance score 7.7038317
Result 9:
Title: Alex Ross
Relevance score 6.7125754

## Multi match boolean query

```
query_body = \
    {
  "query": {
      "bool": {
          "must": [
              {"match": {"title": quetion}},
              {"match": {"text": question}}
              ]
          }
      }
    }
```
**Question: when did stan lee become editor-in chief?**
Result 0:
Title: Jim Lee
Relevance score 16.174313
Result 1:
Title: Lee Falk
Relevance score 15.261215
Result 2:
Title: Ralph Macchio (editor)
Relevance score 13.557625
Result 3:
Title: Stan Hart
Relevance score 11.0070915
Result 4:
Title: Stan Sakai
Relevance score 10.720789
Result 5:
Title: Jae Lee
Relevance score 10.716596
Result 6:
Title: Elaine Lee
Relevance score 10.5024185
Result 7:
Title: Jen Lee (cartoonist)
Relevance score 10.088491
Result 8:
Title: Stan Lee
Relevance score 9.549194
Result 9:
Title: Machine learning in video games
Relevance score 9.171778

## Match_phrase query

```
query_body = \
    {
      "query": {"match_phrase": 
                    {"title": "stan lee"}
               }
    }
```

**Question: "Stan Lee"**

Result 0:
Title: Stan Lee
Relevance score 4.7342873

## Other questions (dymanic boosing with multifield query):

### When was Stan Lee born?

Jim Lee was born on August 11, 1964 in Seoul, South Korea. He grew up in St. Louis, Missouri, where he lived a "typical middle-class childhood". Though given a Korean name at birth, he chose the name Jim when he became a naturalized U.S. citizen at age 12. Lee attended River Bend Elementary School in Chesterfield and later St. Louis Country Day School, where he drew posters for school plays. Having had to learn English when he first came to the U.S. presented the young Lee with the sense of being an outsider, as did the "preppy, upper-class" atmosphere of Country Day. As a result, on the rare occasions that his parents bought him comics, Lee's favorite characters were the X-Men, because they were outsiders themselves. Lee says that he benefited as an artist by connecting with characters that were themselves disenfranchised, like Spider-Man, or who were born of such backgrounds, such as Superman, who was created by two Jewish men from Cleveland to lift their spirits during the Depression. His classmates predicted in his senior yearbook that he would found his own comic book company. Despite this, Lee was resigned to following his father's career in medicine, attending Princeton University to study psychology, with the intention of becoming a medical doctor.

Stan Lee (born Stanley Martin Lieber ; December 28, 1922 – November 12, 2018) was an American comic book writer, editor, publisher, and producer. He rose through the ranks of a family-run business to become Marvel Comics' primary creative leader for two decades, leading its expansion from a small division of a publishing house to a multimedia corporation that dominated the comics industry.
In collaboration with others at Marvel—particularly co-writer/artists Jack Kirby and Steve Ditko—he co-created numerous popular fictional characters, including superheroes Spider-Man, the X-Men, Iron Man, Thor, the Hulk, Black Widow, the Fantastic Four, Black Panther, Daredevil, Doctor Strange, Scarlet Witch and Ant-Man. In doing so, he pioneered a more naturalistic approach to writing superhero comics in the 1960s, and in the 1970s he challenged the restrictions of the Comics Code Authority, indirectly leading to changes in its policies. In the 1980s he pursued the development of Marvel properties in other media, with mixed results. Following his retirement from Marvel in the 1990s, he remained a public figurehead for the company, and frequently made cameo appearances in films and television shows based on Marvel characters, on which he received an executive producer credit. Meanwhile, he continued independent creative ventures into his 90s, until his death in 2018.
Lee was inducted into the comic book industry's Will Eisner Award Hall of Fame in 1994 and the Jack Kirby Hall of Fame in 1995. He received the NEA's National Medal of Arts in 2008.


Marriage and residences
From 1945 to 1947, Lee lived in the rented top floor of a brownstone in the East 90s in Manhattan. He married Joan Clayton Boocock, originally from Newcastle, England, on December 5, 1947, and in 1949, the couple bought a house in Woodmere, New York, on Long Island, living there through 1952. Their daughter Joan Celia "J. C." Lee was born in 1950. Another daughter, Jan Lee, died three days after delivery in 1953.The Lees resided in the Long Island town of Hewlett Harbor, New York, from 1952 to 1980. They also owned a condominium on East 63rd Street in Manhattan from 1975 to 1980, and during the 1970s owned a vacation home in Remsenburg, New York. For their move to the West Coast in 1981, they bought a home in West Hollywood, California, previously owned by comedian Jack Benny's radio announcer Don Wilson.


Bibliography
Books
Lee, Stan; Mair, George (2002). Excelsior!: The Amazing Life of Stan Lee. Simon & Schuster. ISBN 978-0-7432-2800-8.
Lee, Stan (1997) [Originally published by Simon & Schuster in 1974]. Origins of Marvel Comics. Marvel Entertainment Group. ISBN 978-0-7851-0551-0.
Lee, Stan; David, Peter (2015). Amazing, Fantastic, Incredible: A Marvelous Memoir. Simon & Schuster. ISBN 978-1501107771.


[(0.568334645395393, 'August 11, 1964'), (0.2906611847141775, 'December 28, 1922 – November 12, 2018'), (0.4591023499421871, '1950'), (0.7326211906538607, '1997')]

### When did Barak Obama become a president?

[(0.7960525325226014, '2009 to 2017'), (0.6890700298522906, '2008'), (0.9697688529574375, '2013'), (0.38578113263182123, 'August 4, 1961'), (0.24012024466078205, '1979'), (0.5906666366573299, '2, 2008'), (0.7726230736155529, '2005'), (0.7340978512348301, 'May 2017'), (0.6416860785019445, 'August 4, 2016'), (0.6423307604986394, 'May 2008'), (0.27621471869695874, 'June 1985 to May 1988'), (0.34565053972869436, '1991'), (0.3913345337267095, '1994 to 2002'), (0.5618360931039642, 'January 2003'), (0.34793283433229183, 'January 2003'), (0.6553188312306331, 'January 3, 2005'), (0.5845186971784818, '2007'), (0.821900972379522, '2008'), (0.8842083530099445, 'February 10, 2007'), (0.8266607446151348, 'June 19, 2008'), (0.7675966527477077, 'November 4'), (0.9743122922070971, '2012'), (0.6456458220047381, 'April 4, 2011'), (0.7677053262566054, 'November 6, 2012'), (0.6870128996677464, '2009–2017'), (0.9481390321356241, 'January 20, 2009'), (0.5763722561322409, 'May 9, 2012'), (0.9312194141524264, 'January 21, 2013'), (0.6320192629499681, 'February 17, 2009'), (0.5187826622540267, 'August 2, 2011'), (0.8878899388687131, 'December 17, 2010'), (0.6490939025628003, 'September 30, 2009'), (0.5447391510929324, 'March 23, 2010'), (0.41463545647805394, '2006'), (0.5629462359328564, '2010'), (0.27370891680649134, 'June 4, 2009'), (0.9231610017010089, 'September 24, 2009'), (0.41470647581703945, 'August 18, 2011'), (0.48262031319277965, 'March 2011'), (0.8053100687547176, 'March 2016'), (0.9168978107649091, 'July 29, 2015'), (0.9215422017186758, 'May 27, 2016'), (0.49735488273102835, '2016'), (0.31239756624048304, '1960s'), (0.6864327418435829, 'May 2009'), (0.9137575928276043, 'May 25, 2011'), (0.7754789265272802, 'January 20, 2017'), (0.8337143146506807, 'June 1'), (0.772223920341358, '2019'), (0.37607609014699667, '2009, Obama signed into law the National Defense Authorization Act for Fiscal Year 2010'), (0.4323452682554267, '2010'), (0.5105151942454804, '1995'), (0.9291113598902537, '2008'), (0.9375294246535842, '2012'), (0.9049577955713519, 'March 24, 2017'), (0.9833357799563165, '2018'), (0.6736861309698597, 'the Reconstruction Era'), (0.4483638698113282, 'June 16, 2014'), (0.5344770081027439, '35'), (0.7041361051048854, '1992'), (0.5926067215287861, '1787'), (0.4444230621027297, '1892'), (0.9153480482940678, '1965'), (0.27621048878137283, "1864, Arthur and Murphy raised funds from Republicans in New York, and they attended Abraham Lincoln's inauguration in 1865"), (0.6957544300809673, '1880'), (0.8103425932977263, 'March 4, 1881'), (0.4030516575476679, '1881–1885'), (0.2942174365383741, 'January 1868'), (0.5800036648319046, '1884')]