# import pandas as pd
# import numpy as np
#
# pd = pd.read_csv('./input/rating.csv').drop('timestamp')
#
# print(pd.head(5))

import json

result = {"rec": "[{\"title\": \"Platoon (1986)\", \"urlId\": \"tt0091763\", \"storyline\": \"Chris Taylor is a young, naive American who gives up college and volunteers for combat in Vietnam. Upon arrival, he quickly discovers that his presence is quite nonessential, and is considered insignificant to the other soldiers, as he has not fought for as long as the rest of them and felt the effects of combat. Chris has two non-commissioned officers, the ill-tempered and indestructible Staff Sergeant Robert Barnes and the more pleasant and cooperative Sergeant Elias Grodin. A line is drawn between the two NCOs and a number of men in the platoon when an illegal killing occurs during a village raid. As the war continues, Chris himself draws towards psychological meltdown. And as he struggles for survival, he soon realizes he is fighting two battles, the conflict with the enemy and the conflict between the men within his platoon.\", \"poster\": \"https://m.media-amazon.com/images/M/MV5BMzRjZjdlMjQtODVkYS00N2YzLWJlYWYtMGVlN2E5MWEwMWQzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_.jpg\", \"playnum\": 0, \"commentnum\": 0, \"tag_id\": null, \"lang\": \"English\", \"duration\": 120, \"genres\": \"Drama|War\", \"rate\": 8.1, \"actors\": \"Charlie Sheen, Tom Berenger\", \"year\": 1986, \"web_name\": \"Platoon\"}, {\"title\": \"Brazil (1985)\", \"urlId\": \"tt0088846\", \"storyline\": \"Sam Lowry (Jonathan Pryce) is a harried technocrat in a futuristic society that is needlessly convoluted and inefficient. He dreams of a life where he can fly away from technology and overpowering bureaucracy, and spend eternity with the woman of his dreams. While trying to rectify the wrongful arrest of one Harry Buttle (Brian Miller), Lowry meets the woman he is always chasing in his dreams, Jill Layton (Kim Greist). Meanwhile, the bureaucracy has fingered him responsible for a rash of terrorist bombings, and Sam and Jill&#39;s lives are put in danger.\", \"poster\": \"https://m.media-amazon.com/images/M/MV5BMDM0YTM3Y2UtNzY5MC00OTc4LThhZTYtMmM0ZGZjMmU1ZjdmXkEyXkFqcGdeQXVyNjc1NTYyMjg@._V1_.jpg\", \"playnum\": 0, \"commentnum\": 0, \"tag_id\": null, \"lang\": \"English\", \"duration\": 132, \"genres\": \"Fantasy|Sci-Fi\", \"rate\": 7.9, \"actors\": \"Jonathan Pryce, Kim Greist\", \"year\": 1985, \"web_name\": \"Brazil\"}, {\"title\": \"Godfather: Part II, The (1974)\", \"urlId\": \"tt0071562\", \"storyline\": \"The continuing saga of the Corleone crime family tells the story of a young Vito Corleone growing up in Sicily and in 1910s New York; and follows Michael Corleone in the 1950s as he attempts to expand the family business into Las Vegas, Hollywood and Cuba.\", \"poster\": \"https://m.media-amazon.com/images/M/MV5BMWMwMGQzZTItY2JlNC00OWZiLWIyMDctNDk2ZDQ2YjRjMWQ0XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg\", \"playnum\": 0, \"commentnum\": 0, \"tag_id\": null, \"lang\": \"English\", \"duration\": 202, \"genres\": \"Crime|Drama\", \"rate\": 9.0, \"actors\": \"Al Pacino, Robert De Niro\", \"year\": 1974, \"web_name\": \"The Godfather: Part II\"}, {\"title\": \"Titanic (1997)\", \"urlId\": \"tt0120338\", \"storyline\": \"\", \"poster\": \"https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00ZTliLWIzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1_.jpg\", \"playnum\": 0, \"commentnum\": 0, \"tag_id\": null, \"lang\": \"English\", \"duration\": 194, \"genres\": \"Drama|Romance\", \"rate\": 7.9, \"actors\": \"Leonardo DiCaprio, Kate Winslet\", \"year\": 1997, \"web_name\": \"Titanic\"}, {\"title\": \"Big Lebowski, The (1998)\", \"urlId\": \"tt0118715\", \"storyline\": \"When &quot;the dude&quot; Lebowski is mistaken for a millionaire Lebowski, two thugs urinate on his rug to coerce him into paying a debt he knows nothing about. While attempting to gain recompense for the ruined rug from his wealthy counterpart, he accepts a one-time job with high pay-off. He enlists the help of his bowling buddy, Walter, a gun-toting Jewish-convert with anger issues. Deception leads to more trouble, and it soon seems that everyone from porn empire tycoons to nihilists want something from The Dude.\", \"poster\": \"https://m.media-amazon.com/images/M/MV5BMTQ0NjUzMDMyOF5BMl5BanBnXkFtZTgwODA1OTU0MDE@._V1_.jpg\", \"playnum\": 0, \"commentnum\": 0, \"tag_id\": null, \"lang\": \"English\", \"duration\": 117, \"genres\": \"Comedy|Crime\", \"rate\": 8.1, \"actors\": \"Jeff Bridges, John Goodman\", \"year\": 1998, \"web_name\": \"The Big Lebowski\"}, {\"title\": \"Ghostbusters (a.k.a. Ghost Busters) (1984)\", \"urlId\": \"tt0087332\", \"storyline\": \"When Louis Tully mingles with his party guests (commenting on the price of the salmon, and so on), the scene is one continuous shot, and almost entirely improvised.\", \"poster\": \"https://m.media-amazon.com/images/M/MV5BMmZiMjdlN2UtYzdiZS00YjgxLTgyZGMtYzE4ZGU5NTlkNjhhXkEyXkFqcGdeQXVyMTEyMjM2NDc2._V1_.jpg\", \"playnum\": 0, \"commentnum\": 0, \"tag_id\": null, \"lang\": \"English\", \"duration\": 105, \"genres\": \"Action|Comedy|Sci-Fi\", \"rate\": 7.8, \"actors\": \"Carrie Coon, Paul Rudd\", \"year\": 2021, \"web_name\": \"Ghostbusters: Afterlife\"}, {\"title\": \"Minority Report (2002)\", \"urlId\": \"tt0181689\", \"storyline\": \"In the year 2054 A.D. crime is virtually eliminated from Washington D.C. thanks to an elite law enforcing squad &quot;Precrime&quot;. They use three gifted humans (called &quot;Pre-Cogs&quot;) with special powers to see into the future and predict crimes beforehand. John Anderton heads Precrime and believes the system&#39;s flawlessness steadfastly. However one day the Pre-Cogs predict that Anderton will commit a murder himself in the next 36 hours. Worse, Anderton doesn&#39;t even know the victim. He decides to get to the mystery&#39;s core by finding out the &#39;minority report&#39; which means the prediction of the female Pre-Cog Agatha that &quot;might&quot; tell a different story and prove Anderton innocent.\", \"poster\": \"https://m.media-amazon.com/images/M/MV5BZTI3YzZjZjEtMDdjOC00OWVjLTk0YmYtYzI2MGMwZjFiMzBlXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_.jpg\", \"playnum\": 0, \"commentnum\": 0, \"tag_id\": null, \"lang\": \"English\", \"duration\": 145, \"genres\": \"Action|Crime|Mystery|Sci-Fi|Thriller\", \"rate\": 7.7, \"actors\": \"Tom Cruise, Colin Farrell\", \"year\": 2002, \"web_name\": \"Minority Report\"}, {\"title\": \"Not Your Typical Bigfoot Movie (2008)\", \"urlId\": \"tt1185384\", \"storyline\": \"Through the experiences of two amateur Bigfoot researchers in Appalachian Ohio, we see how the power of a dream can bring two men together and provide a source of hope and meaning that transcend the harsh realities of life in a dying steel town.\", \"poster\": \"https://m.media-amazon.com/images/M/MV5BMTMwODE3MzAyMV5BMl5BanBnXkFtZTcwOTMzMzk5MQ@@._V1_.jpg\", \"playnum\": 0, \"commentnum\": 0, \"tag_id\": null, \"lang\": \"English\", \"duration\": 63, \"genres\": \"Documentary\", \"rate\": 6.5, \"actors\": \"Dallas Gilbert, Wayne Burton\", \"year\": 2008, \"web_name\": \"Not Your Typical Bigfoot Movie\"}]"}