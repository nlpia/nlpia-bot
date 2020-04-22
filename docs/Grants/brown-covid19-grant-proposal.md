# [Brown Institute RFP](https://brown.submittable.com/submit/162874/2020-covid-19-micro-grant)

## Background
Chatbots, or conversational assistants are one of the most effective public engagement and education tools, providing timely information in 24/7 manner.
Since the beginning of COVID-19 outbreak, several chatbots have been released to provide the public with information regarding the virus. However, the assistants available today to the public are based on curated answers to pre-defined questions, either by giving the user a list of questions to choose from ([1](https://thenextweb.com/apps/2020/03/20/world-health-organizations-whatsapp-bot-texts-you-coronavirus-facts/)), or matching a open-text question to a pre-defined set of question intents ([1](https://www.forbes.com/sites/leahrosenbaum/2020/03/12/worried-about-coronavirus-now-you-can-text-message-a-chatbot-with-questions/#aeca3b7825e9), [2](https://gyant.com/)). Therefore, they often unable to answer the questions posed with satisfactory accuracy, or to address questions that are not related directly to the medical aspect of the epidemic, leading users to consult other, potentially unreliable, sources.


## Project Description
We propose to leverage cutting-edge natural language processing (NLP) technology to create a Web-based chatbot to assist those affected by a coronavirus lockdown in three domains:

- Answer open domain questions about COVID-19 using authoritative reference corpora such as Wikipedia, the CDC, and PubMed
- Provide updates on the global status of the pandemic (using up-to-date, verified news sources)
- Provide tips for wellness and self-care while working in isolation

The project will be based on the technology developed as a part of ["qary" open-source project](https://gitlab.com/tangibleai/qary). All training of the bot and software development will be performed by interns and volunteers contributing to open-source repository.


## Project outcomes and impact evaluation
The main deliverable of the project will be a mobile web application for Covid-19 question-answering and wellness coaching to mitigate the psychological strains of isolation and promote pro-social behaviors and habits. We will evaluate the success of the project using the following parameters:
- **Chatbot accuracy**: the accuracy of the chatbot will be benchmarked with a list of questions collected from the public forums, such as reddit, Quora and similar sources. Chatbot's answers will be scored using USE metric using answers collected as a benchmark. The chatbot will not be released to public use until reaching the F1 score of X.
In addition, the chatbot accuracy would be evaluated using similar benchmarking method after the release.
- **User engagement**: the engagement of the public with the chatbot will be measured using internal analytics tools. Usage metrics, such as number of users, sessions, and user satisfaction from the conversation with the bot, will be collected to analyze and improve the chatbot's performance.


## Project timeline and budget

Total budget is estimated at **$5000** to be expended as grants to volunteers over three weeks beginning March 23, 2020.

## Budget
- **$4200**: grants to interns and volunteers who are otherwise unemployed (see schedule below)
- **$800**: compute cloud resources and subscription fees to cloud services for 6 months

### Approach
Two components of our architecture will be developed in parallel as separate mobile web applications. Both apps can be deployed  independently and integrated once they each have been tested and verfied with beta users. All software and data will be pushed to GitLab daily and can be run by anyone from the general public familiar with the installation of python packages. Features and milestones will be tracked within GitLab "issues" allowing the general public to provide feedback and feature suggestions.

All software development, data gathering and curation will be performed by volunteer data scientists from the San Diego Python User Group and Machine Learning Group.
Volunteers who are not currently actively employed on salary will be given priority over other potential interns.
Training and mentoring of volunteers will be provided free of charge by TangibleAI staff.
All grant funding will be granted to volunteers and interns to deliver according to their portion of the implementation of the features described in the three parallel schedules below.

### Estimate
Total volunteer and intern effort is estimated at 120 person-hours.
This will allow for $35/hr grants to be provided to volunteers according the schedule below.
Four of our volunteers are currently contributing to the software package, "qary".
These volunteers will are expected to volunteer for these additional tasks and be allocated funds in proportion to the hour estimates below.
Tangible AI professional software development effort as well as mentoring of volunteers will be donated to the project at no cost as part of our core mission to develop AI tools for nonprofits.

#### State of the Art Question Answering App
Total volunteer effort is estimated at 52 person-hours (approximately 2 weeks) to build and deploy the Question Answering mobile web application.

- 8h ($280): compile list of urls and API querys that provide authoritative unstructured natural language text on covid-19
- 8h ($280): build/test/deploy python script to scrape URLs and query APIs indexing documents in ellastic search at least daily (using crontab on totalgood.org)
- 8h ($280): compile training set of at least 100 question/answer pairs based on authoritative resources (e.g. CDC, Johns Hopkins University, pubmed, arxiv.org, wikipedia)
- 16h ($560): train (fine tune) ALBERT to answer 100+ covid-19 FAQs accurately
- 12h ($420): create/test/deploy Django REST open API (urls.py, views.py, template.html, serializer.py, and models.py) for user interaction with COVID-19 chatbot

### Deterministic Conversational Covid-19 Coach
Total volunteer effort is estimated at 48 person-hours (approximately 1 week) to build and deploy the Covid-19 Coach for Isolation wellbeing support.

- 8h ($280): Build deterministic chatbot (using Landbot.io GUI or equivalent) for answering FAQ questions about COVID-19 i(from FAQs at CDC and Johns Hopkins websites)
- 16h ($560): Add emotional well-being and self-help coaching features to Covid-19 Coach, including home isolation, social distancing, exercise, and productivity tips and tricks
- 8h ($280): test with beta users
- 8h ($280): refine Covid-19 Coach
- 8h ($280): deploy and maintain Covid-19 Coach webapp for 3 months

### Integrate Deterministic Chatbot web
Total effort required to integrate the Covid-19 Coach with the Question Answering App is estimated at 20 hours.

- 16h ($560): Integrate Covid-19 Coach with SotA question answering chatbot REST API
- 4h ($140): Purchase and integrate custom URL (or utilize a subdomain at Brown Institute's website)


## RFP from Brown Institute for Media Inovation

Recognizing a profound need for accurate information about the COVID-19 virus, the Brown Institute for Media Innovation is offering a “rapid” micro-grant to help support journalists, technologists, health researchers, data scientists, social scientists, and any and all communities involved in covering the virus. The grant is for $5000 and can be spent for just about any activity that helps inform the public. Examples include novel modes of tracking the progress of the virus, the responses by various governmental organizations, and predictions of its impact — the subject is open. Outcomes might include data and data visualizations, tools to spot and combat misinformation about the virus, a documentary or a reported story, a VR/AR experience or an interactive of some kind.

Applications to the COVID-19 Reporting Micro-grant are due Friday, March 20 at midnight and we will announce a winner on Monday, March 23. The application itself consists of a 1-page PDF description of your project, together with a small budget outlining how you will spend the funds. Contact browninstitute@columbia.edu with any questions.

This Call for Proposals is open to the general public and an affiliation to Columbia or Stanford is not required. Proposals should follow strict CDC guidelines and not suggest activities that put the grantee or the public at greater risk.
