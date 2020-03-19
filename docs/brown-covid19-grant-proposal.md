# Brown Institute Covid-19 Grant Proposal

Covid-19 Coach:  Conversational Interface to FAQs and Wellbeing Advice

## Budget

$4500: grants to interns and volunteers who are otherwise unemployed (see schedule below)
$500: compute cloud resources and subscription fees to cloud services for 3 months

## Schedule

Two components of our architecture will be developed in parallel. Both apps can be deployed independently and integrated once they each have been tested with beta users. All software and data will be pushed to GitLab daily. Features and milestones will be tracked within GitLab "issues".

All software development, data gathering and curation will be performed by volunteer data scientists from the San Diego Python User Group and Machine Learning Group. 
Volunteers who are not currently actively employed on salary will be given priority over other potential interns.
Training and mentoring of volunteers will be provided free of charge by TangibleAI staff.
All grant funding will be granted to volunteers and interns to deliver according to their portion of the implementation of the features described in the three parallel schedules below.

### State of the Art Question Answering Bot

- 8h: compile list of urls and API querys that provide authoritative unstructured natural language text on covid-19 
- 8h: build/test/deploy python script to scrape URLs and query APIs indexing documents in ellastic search at least daily (using crontab on totalgood.org)
- 8h: compile training set of at least 100 question/answer pairs based on authoritative resources (e.g. CDC, Johns Hopkins University, pubmed, arxiv.org, wikipedia)
- 16h: train (fine tune) ALBERT to answer 100+ covid-19 FAQs accurately
- 16h: create/test/deploy Django REST open API (urls.py, views.py, template.html, serializer.py, and models.py) for user interaction with COVID-19 chatbot 

### Deterministic Conversational Covid-19 Coach

- 8h: Build deterministic chatbot (using Landbot.io GUI or equivalent) for answering FAQ questions about COVID-19 i(from FAQs at CDC and Johns Hopkins websites)
- 16h: Add emotional well-being and self-help coaching features to Covid-19 Coach, including home isolation, social distancing, exercise, and productivity tips and tricks 
- 8h: test with beta users
- 8h: refine Covid-19 Coach
- 8h: deploy and maintain Covid-19 Coach webapp for 3 months

### Integrate Deterministic Chatbot web 

- 16h: Integrate Covid-19 Coach with SotA question answering chatbot REST API
- 4h: Purchase and integrate custom URL (or utilize a subdomain at Brown Institute's website)


## RFP from Brown Institute for Media Inovation

Recognizing a profound need for accurate information about the COVID-19 virus, the Brown Institute for Media Innovation is offering a “rapid” micro-grant to help support journalists, technologists, health researchers, data scientists, social scientists, and any and all communities involved in covering the virus. The grant is for $5000 and can be spent for just about any activity that helps inform the public. Examples include novel modes of tracking the progress of the virus, the responses by various governmental organizations, and predictions of its impact — the subject is open. Outcomes might include data and data visualizations, tools to spot and combat misinformation about the virus, a documentary or a reported story, a VR/AR experience or an interactive of some kind. 

Applications to the COVID-19 Reporting Micro-grant are due Friday, March 20 at midnight and we will announce a winner on Monday, March 23. The application itself consists of a 1-page PDF description of your project, together with a small budget outlining how you will spend the funds. Contact browninstitute@columbia.edu with any questions.

This Call for Proposals is open to the general public and an affiliation to Columbia or Stanford is not required. Proposals should follow strict CDC guidelines and not suggest activities that put the grantee or the public at greater risk.

