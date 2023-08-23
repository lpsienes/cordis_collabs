import pandas as pd
from selenium import webdriver
import csv

file_path = 'cordis_links.csv'

cordis_links = pd.read_csv(file_path)
cordis_links = cordis_links[['Project-Acronym', 'Cordis']]


c = 0
rows = []
max_partners = 0

for n, url in enumerate(cordis_links.Cordis):
    url = cordis_links['Cordis'][n]
    row = [cordis_links['Project-Acronym'][n]]
    print('\n', n, url, row)
    
    if n > 5: break
    try:
        # URL & SEARCH ENGINE
        driver = webdriver.Firefox()

        # WEB ACCESS
        driver.get(url)


        ############################################
        # COORDINATOR
        ############################################
        
        coordinator = driver.find_elements(by=By.XPATH, value='//p[@class="coordinated coordinated-name"]')
        for i in range(len(coordinator)):
            coordinator_name, coordinator_country = coordinator[i].text.split('\n')
        
        coordinator_contribution = driver.find_elements(by=By.XPATH, value='//div[@class="c-part-info__content "]')
        coordinator_contribution = float(coordinator_contribution[0].text[2:].replace(' ', '').replace(',', '.'))
        row += [coordinator_name, coordinator_country, coordinator_contribution]
        
        # Este me da la lista de participantes
        institutions = driver.find_elements(by=By.XPATH, value='//div[@class="col-12 c-organizations-list__item"]')

        institutions_list = []
        for i in range(len(institutions)):
            institutions_list.append(institutions[i].text)

        if len(institutions_list) > max_partners:
            max_partners = len(institutions_list)
        
        ############################################
        # PARTNERS
        ############################################
        
        for i in range(len(institutions_list)):
            l = institutions_list[i].split('\n')
            
            if institutions_list[i].split('\n')[0] == 'INTERNATIONAL PARTNER':
                row += [l[1], l[2], '']
                
            else:
                partner_name = l[-4]
                partner_country = l[-3]
                partner_contribution = l[-1][2:].replace(' ', '').replace(',', '.')
                row += [partner_name, partner_country, partner_contribution]

        c+=1
        rows += [row]
        print(row)
        driver.close()

    except Exception as e: 
        print(e)
        row += ''
        rows += ['']
        driver.close();


df = pd.DataFrame()

for r in rows:
    row = r + ['' for i in range((max_partners+1)*3+1-len(r))]
    df = df.append([row])
    
columns = ['Project-Acronym', 'Coordinator', 'Country', 'Contribution'] + \
            sum([[f'partner {p+1}', 'country', 'contribution'] for p in range(max_partners)], []) #flatten the list

df.columns = columns
df = df.reset_index(drop=True)
df.to_csv('projects_collaborators_info.csv', index=False)
