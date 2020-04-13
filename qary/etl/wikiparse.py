import wikipediaapi
from qary import constants

log = constants.logging.getLogger(__name__)

wiki_wiki = wikipediaapi.Wikipedia('en')

def parse_article(article):
    ''' 
    Parse full wikipedia article into sections:
    - content sections (summary, History, Applications, etc.)
    - reference section (References, Bibliography, See Also, Notes, etc)
    '''
    
    text = article.text
    # get section titles for the existing sections
    section_titles = [sec.title for sec in article.sections]
    
    # initiate the sections dictionary with a summary (0th section) 
    sections = [{'section_num': 0,
                'section_title': "Summary",
                'section_content': article.summary}]
    
    for i, title in enumerate(section_titles[::-1]):

        num = len(section_titles)-i
        if len(text.split(f"\n\n{title}")) == 2:
            section_dict = {"section_num": num,
                            "section_title": title,
                            "section_content": text.split(f"\n\n{title}")[-1]}
            sections.append(section_dict)
            text = text.split(f"\n\n{title}")[0]
        else:
            pass
            
        
    return sections

def get_references(mylist):
    '''
    Get reference sections' headers
    '''
    reference_list = []
    content_list = []
    
    for d in mylist:
        if d['section_title'].lower() in ' '.join(['see also references external links bibliography notes']):
            reference_list.append(d)
        else:
            content_list.append(d)
            
    return (content_list, reference_list)  



if __name__=="__main__":
    
    def test():
        page = wiki_wiki.page('Artificial intelligence')
        print(page.summary)

    test()