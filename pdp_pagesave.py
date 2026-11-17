import gzip
import os

import requests
from rich import print

from db_script import CarrefourDB

cookies = {
    'cart_api': 'v2',
    'common.mw_sellerflex.enabled': 'true',
    '__privaci_latest_published_version': '{"v":10,"sync":0,"kn":"","cid":0}',
    '__privaci_cookie_consent_uuid': '892b288d-b4ac-46ef-a2ce-3aba9ac8388f:4,05923948-9e4d-4706-8a48-e390632c991d:4',
    '__privaci_cookie_consent_generated': '05923948-9e4d-4706-8a48-e390632c991d:4',
    '__privaci_cookie_consents': '{"ts":1793962667,"consents":{"249":1,"250":1,"251":1,"252":1},"location":"GJ#IN","lang":"en","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":false,"status":"record-consent-success","implicit_consent":false,"ct":3,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}',
    'posInfo': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04',
    'posInfo2': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04',
    'emirate-code': 'DUBAI',
    'selectedTabData': '{"selectedTabId":"80","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL","pagePath":"New_homepage_standard_June_2025","pageType":"Homepage","pageId":"4044","pageUid":"Scheduled"}',
    'tabInfo': 'SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY',
    'mafuae-preferred-delivery-area': 'DubaiFestivalCity-Dubai',
    'maf-session-id': 'B0CEDE29-32FE-4D51-ACB8-B5E62BA13370',
    'device-id': '40ff88317e022fbb14c2dfba0ed9246f',
    'future-express-delivery': 'false',
    'bm_mi': '39C9E3BF768769EB5C290D20CBD37E1B~YAAQnPnaF/MbScShAQAAiam76AGM6sQ8Mng8mV0QNeOF0kJJa1kR7KwZ8nDpp87+d2izTOqzW1azUORyHfAuUQ+6A7tj/MacvtjbUmTFV8EnT3BCNpBJOlykRW0BS6dWQrtSjUohg0apeAS3xSNb5XbH7/HU7dTZ6M/n7kb9RIYaJJGgRtTJWvOZl3hQ412ySGBsK5xYybFEr57+EGTI9qjU8Y3hAJd6ssO8B7a1YBJcUOdYUwH33eb5mt3jGfSZExdILA/VGGJzKwb/Y0Cg+XFmNJ/PREsUpNS0/gsT4eR+Z9Fj94PoRBi82vBswgfmAkKZwNY3l+17xjG0SCFVrihnDvKXMse1+MPfht8qu60NMqwSfDf13JLldqNwvqx1yVjaXfH2pyFeCeDyhtTaGuQL2CY3dlhlEhnOnslNuCcCVE+3xzuo4Rhhy/Khx4Q8B/pimWHvAhQyuWEroiqZ~1',
    'bm_sv': 'BFFFA2972690B9ACD303ED056DE00C90~YAAQnPnaF90gScShAQAAary76AGnfRu5SdjRXIB7Dp2dmzEGhK8ToBqZJgythGLWwP9FRJ4EzC4JkkNYwE5wQVmTvwqMK+xh5phdX1ZVR9BYjOCh/w/mqpEdCjAIp2s75X77SQdbw5rSDfnJTykOiflks6PKDePj9/EF90BztLB5bJQTcRwkxiBZkhQLeIif/d2Z4e6W8tcaBV93J5eoqBNMqEezIJXGX7LWFG6rbeaUhG4bDm6mfD7LFd1jemcsEbGHTRJp/w==~1',
    'ak_bmsc': 'B0396A42C507CFE2D1BAF47EBB084096~000000000000000000000000000000~YAAQnPnaF+BLScShAQAAcWG86AFjiWMWUXykBfZlvwLkg42qzWw9q3KvueLlb1PabuUNDru39FmG1SE3r0bA8A+Kp32CRyEHXK3PoLzBSAnFtJiICdhCvhJ4rlmupslUmFpoc6p59uEBrfDO3vl5XHttYl3bzHPt6LEAohA3zMyPXjbcq82iwwPIbmt1lvtTZBdMAdrZ1NQZ2GRzSTn47jmHbppDVDDfeA9VXvfAGwl2AG5BwU6iGE+8emi5jmRY/EsvrfTzlR2xzuYrAdTeZo/yjTDxwg6SUB2ZdX1wk7jE4m4xlz9bmyL4h+prA+Z9zETJPKuqFZ45uwdKF3JIsvvuSnHNXUlnFIMol1gUVvhtMZgmA0nwKP5je4R3kpOg5m1cAy/SQCKEyeca8ynGwXBN1UKOTFG6LOewBa2U20lqiBqI2uff9irHB/zraWXsD/6U9dL3EUV4ATOseWlrolCHydRDVQiuTWkNPI4eOsvTiuu7TXYKRywEb4AxjZHDXNClVeVCDwXCYsXrRdVeDCZe4KxQm2KDioSQ39jYwQYHobXwT2JZFqjMwYRNBrXgrWw=',
    'AKA_A2': 'A',
    'gtoken': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiI5MjUyODNjNC01MWQ1LTQ2NzctYWViZS04NDg4ODc2NTRjNGYiLCJpYXQiOjE3OTQ5MDc5MjksImV4cCI6MTc5NDkxMTUyOX0.ZJYpB6EUxYAolBaxWE9P991QqqY62RqxpXYRnOvNnFCYv0j6AMGfkuUGlF8oGs_7YFemdPrTdVQf5HDAuEBYFVpoC9ROHP1IT7Guve3ZqMpsM4JOSfX0Y2OkpBnSgnDPmeSQ8WM4ZilHGkqs2FYWTOnmEFWWKtzJ2fzP5swJvh48EgTP5CZYsaHWmBCkIVeIjVpREATiNbs0uZ4ZHXdgfbEot2pVqtjhbxwtaEK2t4KCGFEzqjsjGGivRHj7a20pvaGdcPc7GeTeAoV1VkxsFPy3E4wYGaKNf1uSFaTcYqlGXk2OtIYZk5RknfVtuKsxSk5LeLa2RLHwI059G81fJA',
    'guid': '7e8ec713f5bcbd744b75f2ebbe042759',
    'storeInfo': 'mafuae|en|AED',
    'JSESSIONID': 'B8F7C566365796464C5EA66413F7B3AC',
    'bm_sz': '6F1E9D9A55374D931222DFD3FB8FF816~YAAQnPnaF49WWMShAQAAuMj46AF42zgj9h3YlHTtt8JIZjRAUtVeI6UDtK4Xp+1Ct8WQIY/mJ3bBmFCqsFCglWL8ivu+NuQYR0wLBVL740xqTCKDXQucTD64SyX9t9TJ2U/pfl6fz1W2A7CP92dhKQG3zLm/Oh7fBa3jujGvGGKA1x/IE9UFn9mm2koOXy0qbtcdULZ7bWTH2+YKPwL9QXcoOgwPILcSFa1ss7BPQuxvzutURFfgROyR0q+OqCcPElneNv/yteI4FumqRWuGmC3KoGviOInnORz+T2bcJjFU4SJDJcp7URcvMQSfddfEGTkIVYdFp2Iq8h8gpWp/KGUQgSmH4w7EeQPezmDj+oGJsPBK7eThxOq52IGXv+jqXVul5m8gjPPLYeaeGtUFwhbOcODvCgkDRvrStqSWO3UAWqjmajM/D3FgFor6zBYznXGgmzLBdDBE48xLHGlgGX8ACUDeA1CvebW777Wka34BYAOBzG8tHO+vS1RxBfRjA2GCE4PUvPwny0KtLZAs9eWWQqmD9ghQieD6V+jUGWDOWPBi1TfK8eUX7bL0969c8nBlDX/B~3229236~3225668',
    '_abck': '20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQnPnaF4z3WcShAQAAatv/6BC8yzy+iYkT3ImzSgublUaO4UtgQeNDsV0LBZtFixtT3olTeSK5CJBC4UI2XYI5TIG0FrYlms8yYK3V8RYolj/KVgPOLrS2DYZT2GSew/ona9AVDibZS/P61KRRpWZJf465EaIHyC/WH5lxDAXPbU/xQtQ8XlVbDQuXHG9tlXIUg93/XKwLHgEZYj5MrwlKXfo4EflGO7EPf4Y5eMGIktrsX4DJkFtGE08X+I9auR0zGGGa0xoH8mYIIaDGlFAn9Nn9VRbeIpmZ+HJ4tJyaHnHHDav8Xjaw/JZiTEBuUDgObYLfAdnv+bxtSx0IHlzfkR4xZcfo+RMmhxT6EafFZ+IyeuA9UA7LBn8VFJ+UjvCzMXqwqqXbzDheahPIBebS68lhNDpfFJjIYy+DEpsroAspVpax2rPCjbsfYXpVN0ISUJerDsi5W1OtZJ7/8EsgfK5GhSJZOr32Vm7C1WQ5pG408FeSYoHjLU0F7Qm6JDgh683ylau5YqgjWHqGvCGn4SHOy5YVbKcmKdgPee8xB1ETzW3c4KSTMjgcEYPn1f0sr4ezSqtyIojGIPKdDq3MtaXjs1f7VUq2+QQI+7OXve0Qe1Wv8N3g7H8Vz30mQg9aOKLJU2ngOJvSglK+XCmJP6kuH3tw/DlkgnejrVSVgpkCnxGdPx0zwG47n9RvUOz+zu61VZJ4gej3gtsQlBLA+cRBuBJz291nUsC1jtWgoiyfKn6ONrIi4O0Yn68wrpYFbfFQmi9uD6NHulx8p5CNWmmNpgriyA8qplOtn/CvJAAXNYEOCfaZ5WIXzmgf+/cyBGREudr2sEmQM7ohMhUsNXYXiPKJipAs4ucBZR3/xy973qWSu76bTR2ri9yDRPeDeEfxQmc3atDc6iYjDy8H8I/gF2Q/N2vm6g+RV95cHUA58K5DaX+564ur/6MKUdtRTglY7UJAmwP3UvKLKUZsDpfXAG2jzIPopyadXE+1NDX0fN5yXqJdMriMuex6BrZJYhr+cwnqFsi54LchZWdDQaTmlLy9yOf9AYEamB6263Lyk3GPg/Vszw5D0b0/qR5ALXFB4+ofaa+qvKXYSnZ+gSFEIJHmoKr6Q7Txjw==~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f+Jke7uy4pjM%2fYRbROlEFp83b%2fCD8brixVTJYQlsGaqf0Vso64Z0AnieFfFesNn%2fUnmZj5kdhPV9AR3Z8lziz6CRbPkZHY1LqYk0BOLMt4UozsiGquow+5df2cqlVN8jjGiR%2fdSLBoTjDb4+Lqnr53dMOymMwKT+2GnjkdZhRJ0jWN7iXwyxEGK4J+6HFgF2gJzMgtciV1rds4E6m4zHg+OIvXkLptaEPVjbGLqcZvCYe3k%3d~-1',
    'bm_s': 'YAAQnPnaF433WcShAQAAatv/6AZjWBFVePqu+IuZJmEqtdmWyODQ8PppjqOzorQ9hHO5hecfkWRhcv/v53kqsTR/ioLsbPN+WChj96qWKym0bo4tKc+STCgoqsjbMcal+uG3GRgRXW2HtI/fiDW4ZeZu8+EJ4Xv4i3ycEpVw0wNH+VckTkEi+YDBAoAStpqigrYqMfC+cJO2tW9tzeKq3Cn3e/qOWpAa6H4UNU1nPviNkk8evk2d6Yk105HPiupddpJD2IqHtCt928BJbNH4XdAO1hop20JMO0Vjcr+dkFqr0l4QAQDBzNaRT6Kr+8aFp8qh1dXSCPXQiJK187WUjdC6aEHxM4UyIFWjNj89l/hhIS+WJjgHncla0pngsPNk3H+iYekPRlW5Dxz5G376j3TBZILZpAhdRwD8KHiYsURlXhW3KJFh2hAdpTMvpcAZnWWwSnaV8WW405I3iHwMW4BlAtvNS1NKLWjS6qPtTNGPjYaALkTeopiWvBHdhwDikJgIkDHRCmaZvOEzXmTDYaPc/0t4q4NCku2hpsRzv0Wa0SQ9BdzeAZLN8pkyL9ibMwVYTofcRStuQIJ3/uBNyOiccWO7/PlWoDjX78L107InT3TR71VQQD9GZLsIhZ/9RXHfkFqGsA8vd/BzvQeaIVj6ePNXCLYEJgRS6XMarmAzclrzndZQlzO/SvVRzIj4uKzggDA7ZtLv9pk1WZl5DvW6FbcI7a/W/3txY58kaJjVl4dtT4KjyWK/dp3MDZefKrlsNS7+3Yb96uDq2gMo6aQUz5JJcAF+kNFOZWO3oN/L5UO/GQBuuckbJUEzb9gb3pGJRoTEfinTI2mzsVZF0W+027wAYDUNrs8yBcjz3zibohU8QMr5e4aOrf6G0/7JPCtUu37suEvf0r0WcRG7zKSnphCiu81H2+8fQgEXG6DvMlo92QtkWR24nLKyAoKkfzKJOjhpc+Y/+3z6Tf415gYhk1uFqZgXCpFDSkwlqos20vmA5+UEy+ZereeWqvVikkvmh+YHzmKTBuFUVl2geDnsb411jw61Vyw0ODHUEcpYL8EAXZvBjQ4AkRwBxmV0L8bxvIXMMP84mtJ8AruvB9wjTRDkvvcpn5iIW0G3r7UNZMqaW/SCH5ruIFCgSZsY5n3JRpuqEDYWM+L9BA==',
    'bm_so': '4A2470A95071B89D8C6C630B5359D82918D8CBE9797AED5460DCF024CFEF6856~YAAQnPnaF473WcShAQAAatv/6AmmtiGMrqh/seY/3yxRMBV2kBbElkiPHzrcEzU7Fsph4CtRfj3KMiPT3m5DwJYY2FZUvs0EUDuOdDF94QuVHymOvwrF/EPcySL5X1FdIMjlKauLNMkCNrxw88v/+NF8Vlz46kLVTBCfTr6SGv/U9TmgaTNte9dDTcryPwo03f5TC7uwaUHUljZMqkQRxFGP7uwer8CmzqsZ+2rSiFwOZdXDaZzWKfMEb9E8Phbi+FmGDZKXMtFVmtjVP4BtVndwuWq3izpG7CtPTGHkqiMljE/DnakC31WKT5MuCqTtlOyFWySagiI8a8WQyGTSB9det2/5ejjSkIShkTixnyaQw0nvoERIiiQPgr6j2Jaq2O9bPGI9j/trWSwq0nHjyigy8AvjZGdN5DZdblDaa3nXXDcXf7exmtTfPW/1RqxEBTSLspRi8m9of5BQmFjBNwwdbNRSOEe0jL6O6/LRyO0j~0',
    'bm_lso': '4A2470A95071B89D8C6C630B5359D82918D8CBE9797AED5460DCF024CFEF6856~YAAQnPnaF473WcShAQAAatv/6AmmtiGMrqh/seY/3yxRMBV2kBbElkiPHzrcEzU7Fsph4CtRfj3KMiPT3m5DwJYY2FZUvs0EUDuOdDF94QuVHymOvwrF/EPcySL5X1FdIMjlKauLNMkCNrxw88v/+NF8Vlz46kLVTBCfTr6SGv/U9TmgaTNte9dDTcryPwo03f5TC7uwaUHUljZMqkQRxFGP7uwer8CmzqsZ+2rSiFwOZdXDaZzWKfMEb9E8Phbi+FmGDZKXMtFVmtjVP4BtVndwuWq3izpG7CtPTGHkqiMljE/DnakC31WKT5MuCqTtlOyFWySagiI8a8WQyGTSB9det2/5ejjSkIShkTixnyaQw0nvoERIiiQPgr6j2Jaq2O9bPGI9j/trWSwq0nHjyigy8AvjZGdN5DZdblDaa3nXXDcXf7exmtTfPW/1RqxEBTSLspRi8m9of5BQmFjBNwwdbNRSOEe0jL6O6/LRyO0j~0~1794910444520',
}



headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,gu;q=0.8',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Google Chrome";v="157", "Chromium";v="157"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
    # 'cookie': 'cart_api=v2; common.mw_sellerflex.enabled=true; __privaci_latest_published_version={"v":10,"sync":0,"kn":"","cid":0}; __privaci_cookie_consent_uuid=892b288d-b4ac-46ef-a2ce-3aba9ac8388f:4,05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consent_generated=05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consents={"ts":1793962667,"consents":{"249":1,"250":1,"251":1,"252":1},"location":"GJ#IN","lang":"en","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":false,"status":"record-consent-success","implicit_consent":false,"ct":3,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}; posInfo=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04; posInfo2=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04; AKA_A2=A; emirate-code=DUBAI; selectedTabData={"selectedTabId":"80","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL","pagePath":"New_homepage_standard_June_2025","pageType":"Homepage","pageId":"4044","pageUid":"Scheduled"}; tabInfo=SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY; mafuae-preferred-delivery-area=DubaiFestivalCity-Dubai; maf-session-id=B0CEDE29-32FE-4D51-ACB8-B5E62BA13370; device-id=40ff88317e022fbb14c2dfba0ed9246f; guid=7e8ec713f5bcbd744b75f2ebbe042759; gtoken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiIzOTMzMTIyYS05N2FlLTQ1YzAtOTAwNS03MDBmNDAzNjk5MmQiLCJpYXQiOjE3OTQ3NDUzMTcsImV4cCI6MTc5NDc0ODkxN30.DZq3lvImEDCIuoCpKQPvwYvVRJGwN1IfQ1_8zTYveFFrCr7DF7sT2BfoemNi1kVBjRjHKXXC93ZJCCoAe_FaLTGVat7RjJsyvdiTSwOAeFJq47Da_M2HSlh6QwDlvnMn4lAGfMs2J8_uKJL9YiAzjp-vGczeEfumuN-jF-PRk6AZefkSzvakfeNeW_9Mmv5mdFH58YED8oro2Yg470uqPJ723XEeyB0VUoRaqpP2Zh7SwhN6plq_x_Al44qOP79YI0t6wGBxKbIfAkBaN2yL_tcWmFjLnky7llYnUP65CCy07m8DDtgFb2UibbtuUF-siJjZDX-wIYahH4feonKfbw; bm_mi=C63FAC721B00AB619E2601B6FBEB71DC~YAAQnPnaFwqpb8OhAQAAPegr3wHbU73NQa9aNgkgP88S5ZY4TWuPxgy0e8cxDm/0mv8O7MwNzmRlTEETRYW/Ol6wWHm0nit71EbP4awDYdO4NN51QB7h9VwxhPQ7j69Zyd20nscckB3wkYvoEiDlIl8u/77Fqz7arMu2Dk2OxrbwAanIV/E5Zg8WER6con+F9TtDnulJHoWATUDsKjRU9o6VdbKF3hpX1LhXciQiZgNUhxZ4znsJReR8kqW5ePXoAvRMROf5XkcShq/0aW/yk7TiU7Ihnh3xxJzEPXbCYiM9gY/BuQ/9PSZdF7JmOL8jMXn7Pan0NniErPxoTbSreibbvU6Rgi9fy7D42QDha/qB1Lif+LPksef4JJirM6KL7R0MomXMC6p2yThbI90ZgeJ56Vcs0ik=~1; bm_sv=4800B7F50D500FF6A1AD5513C7A5688D~YAAQnPnaFwCsb8OhAQAAxyUs3wE+2Ymw+NVKjZpIw0C6o6A/pDsTskBVCWMpJrjx7clhgRrpDXrdUBp6I1IWlKbyLvRZa/rr6pd79FWsAT0VtEUK9FxiR+Ck5pgmPZVa4zptVHU/r62DlKf6wTwi7+rFBe7R7l8EJNqEkjb7DDFIVif3nOzgNMazJTont5nytsmKEQAcFZWbp9aJCuUFVyWvaiUgR8bysJutbM6M20aQWhBqsPb0A0KVpI8wPnPVyENkJ0HzpQ==~1; ak_bmsc=3022358A5FAAA79B88A621376336724F~000000000000000000000000000000~YAAQnPnaF5Gtb8OhAQAAhVMs3wEikTSs2TwmUb84PfrGoLTkDcjrEEstf19H1hf/b6C1eVmfdiiMT7imUxkuQnKLMjbWLwkNs4tr52V9VqMons4BYXxF6rXNIiHlCu0TF4WOKVGmgnVpBbfb6HhHk7E7rRDtPpBnhrGZt31OZKaeLXGg5fP9SBtAbNMhz3pratzkJFhOyKQdqCaSfGf7YwkTa1Ig4WBUXVroaJ6uvPjq/seIqsTN5Vro+2McQQw7nwN5vVwgYgK2EwhRsrCETiqNq3Kg/iVrLBsykr823O6QZFDz3L0dtMPtLxPkPBjg3RRcdW+k7aADKmDI4R7FlCbgRy5C/qeiw+t3c+/99YvKILUCKskqiAIELCu18ZLVXyzAennPx8v/aQpQhlxg8X2yrlUB3ZwEulwi2KA/CKTOGhfmNNyXXiDTJAo1nHTwm9rhzVJdnel63UAuUEj3gFUs+V5xtGRwxMa4l5vHW0QfEKJ/cvjdO6HVFb/PKX26TJQ/ED79RV45VA==; storeInfo=mafuae|en|AED; future-express-delivery=false; bm_so=A8DF01331665CDAA3339F1C6B7CF0FB1C36C896D69144A477EC5386A03CB5D05~YAAQnPnaF806cMOhAQAAqv813wmHNvsS+wF2ZsJWCIeb03KHhQGcvNa9Y6mImW9bqWOQiHnHrfZC3JJyVmQG3gVTVR+dck/86tuAHjE+hgAH0o/ldwxCy9tJjzdvj2QU2xlHRaygK+ZkwbpVeoXdaBz8RpB4NJCgK7+2pbGftKiopgTIiqQOYGwTXxXcckOQCMpkjcgrl6b+2i4JEsdXUPvWYYU4Ay5PLQJzY7sgh5V545SG4jW3mH7XmD2BzgdxbhZ6oJ2ndBDs9s7zY/HS/SJK0QHrDlNaBj2BT0MxMY2RUnXgi5+Tof6wsHtxHcAPTYZMWtZ/Tn7+WDlZ7MyPblzssckpLW70sbgjWEwe2ep3UBa+0M1DKTMo9miVSVStXvUZAxkioqa6DEqrOnf1cYF0MOZVdXxdh7gOBm+bwhI3azj5jAb1V7QQD7/fJ7mxkTs5yUKYVW7loDobwFfUBRDhCmC6BFnYO8x/bhrBb3s=~5; bm_lso=A8DF01331665CDAA3339F1C6B7CF0FB1C36C896D69144A477EC5386A03CB5D05~YAAQnPnaF806cMOhAQAAqv813wmHNvsS+wF2ZsJWCIeb03KHhQGcvNa9Y6mImW9bqWOQiHnHrfZC3JJyVmQG3gVTVR+dck/86tuAHjE+hgAH0o/ldwxCy9tJjzdvj2QU2xlHRaygK+ZkwbpVeoXdaBz8RpB4NJCgK7+2pbGftKiopgTIiqQOYGwTXxXcckOQCMpkjcgrl6b+2i4JEsdXUPvWYYU4Ay5PLQJzY7sgh5V545SG4jW3mH7XmD2BzgdxbhZ6oJ2ndBDs9s7zY/HS/SJK0QHrDlNaBj2BT0MxMY2RUnXgi5+Tof6wsHtxHcAPTYZMWtZ/Tn7+WDlZ7MyPblzssckpLW70sbgjWEwe2ep3UBa+0M1DKTMo9miVSVStXvUZAxkioqa6DEqrOnf1cYF0MOZVdXxdh7gOBm+bwhI3azj5jAb1V7QQD7/fJ7mxkTs5yUKYVW7loDobwFfUBRDhCmC6BFnYO8x/bhrBb3s=~5~1794746222970; JSESSIONID=8CFEAD4EF66161B60A285A2C639EEE43; bm_s=YAAQnPnaF/Q7cMOhAQAAjBE23wZ8dsvphfAW3eYhFR2+KnXkHp22K1VPvLN0+e47zE4Wzb8MEqYvNpNVyS8Sfbf0AysNo7jMElLBpDvRYujqdC+GYV6POTvVX1z6iqBEE2rUri+pT0fn8Jhgd1p04fkb4AmxsvIxpp+HsTPr8UlA9T4lZNcb+1g7BvUQZk6Ze4blQbI9uKmrEu5fD84bVkNMOnzpy8hkLck/QeF4LPQfPGJCx9oRZE6RLAP9ohiggc8KpRDRwbTIhIrhvW3TzrFKA4bWv81dpUyiGA90K2zoVRLku5+0BUB+peUy7BWw7Htz5qT1JC4ct+3lvK8pIjL7bfw2SpeS9kuQku+OWGmflzuv7+W55xUMODw925uXC1Mi49opy+2+ZsxJkORoB74E2U9Z7qBRe9clDAsmbYPBYqkamNRyq3w8MlEGHjQdV6vFLfBFqnlGjFqv4N14AfpUnERgDPW/DWeH2isq4H4HluOMzfNxuR6j4gPaEjEOOwlcpS2F2up0sKBa1z21JWaJDAIMgbe1gNR8gkrk/ZJYROnOirXYscMz0lxq3Rh6EsK1UujO0uZJx+KTopwtqexnbrmu6iW5bOBccgt1VMJE0zKKCX0WfgQXNMbFfvZqHDMwvMFHHgDvyJjCBhIGgsXsgC4UQzvQ76hTnvAAt6/KN8bgZdL7ZB+AXT0uBb3ThltcDGvxYvNNjQdQIrruLqkFJf5bPlhFH1ScxjOig+DL0gBKKrFANiBrcKfwQDdpmTGeNJrz23sxldMouRzluB7oLpzlnmS6Wi3p54U63ZrHbo7sAiEbKSL9UNEjR9ndXV/t8M4juYmLBLUAMCL4tkm9fmYTvhgYZl4+D/B4kiIdrNbfsMFKaOIi3rXaA6Q+DlLfjegpObYP1vpSB7J9Pt52xAF7BX5/5efTp18tnrDXAq6AHwbuB3mZqTvKZs0YNd53C9fDAG5Kuj5dJxTd6aC4QdmEfUWPLzJao0njbz9ildgTb9oSZmCn9RAGV22xRhSY1xfUWFWWPAE4zLLW7xds922Qpi/3WuY6+l8xeFFf2jXITuV3q6GcLkhvSs6xqy6imXmwcNm6OiTJpZSSIGeimWttdqKiksgru66OEfhN0BhrjN/fT8EWIfK3SmSi2YzVcQ==; bm_sz=6A1EDE8ECA2DF7972B72456026E8DE65~YAAQnPnaF/U7cMOhAQAAjBE23wGHK8cmcJSdhwPhnrMTs4K0sESV+AF1orCILoZWugLDZJQQZ7MQ92xMD5Ogrfw/9dMM1wj5ced7x/S20VsPqfSdqG1obdaQh6YnDtuiUvNP9CXUvEiVr/nzhItL0aqM+UZbz8MBaoXdgwLrFJTdCvigKhPjof+mk4PYpsp2tkgx7iHRZkvNdqkHRd7xfkp+rmwfniLeB4Kw9B9HCdonIlfaD1WFFDuVcyictKLQ9IPqaTCjidaa4YaD5liL1cngvSegCVvpvsLdXOHXOfwY5EvMZgrN4NWgm+3XH2PSsvW8GfsqOTB0eww5JOPQG31m6dqv3WbogEatGIDG4VKbEOyz/nZ0L+YYYPqC5maIWahI9e9FzY5+Cts/BjMkFMHK9b4K27pRssxh17fR8VcBDVrVDBVaZcjtBB755UezOLIHuWY+hN8/l8WtBGLwfULr6+MdnJMcc+G2WCHdB6lGOOjd1yzc0Tgs4WFRPbw4wylf5PoNfyiMSavrxmTSxa87W+vA8uagKhm4~3163441~4337713; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~0~YAAQnPnaF688cMOhAQAAwBw23xB6pCkfjpficLM39/+NGfPQS66HqSgVfgosuauXjyJdTvX42QCcKCFivE8MBWL7VBMS7YVd18MZYjJU7OKv/QfYiHipPOSytieEw51Kdsa4vPccyIwGsHMi56wITwZs+zd7D+EU0FXsPXADVtoTX04kr6WYNE3hOgdczLlOA47s66oyyLPQyNydDAC0/s2U7t5aBqhq5LhNU+I7K2bTO/Z/DjeKeMwAk/wYVaH5YJ9Eir+QNVrjEX7Jb7QDFSTz2i8pbhqs4rNqAYFwJaPgj6eR49eVXqc5Rw2NmaHLkOX0eCGL5LiokFYq5G09z/2Blks3cPGLVp87dBQVu1x3rb9jIN//X+LoesSXyU3yQuwMHS1FnHb4rRUBL0y0NkLgZ2ix+1SeufQLhd8Oopgv/ndLHN08GM/71Wi1R+Ta1gh66dys04ENzowyvvECSGPgocsII7Sn8n8KEKTZZtq/qeo8T/slg51hds2Q21DChGEXUCuko1RBT2ox0TpQ//GxsDUhJ/uk0qxdhF/B0Q0wiwPQDwgArn5s2A0GjZvf4NzcO+X4qVPovzb9vdJmXaJbkaeR+dcwbXEItqvpE6jn1F48W+BtxwsEey4gHVZPVP8O9UheklpaP+zx0ZmRcnVKHZ0me4QgF5yHxGJTXVidvt4q45TrcnfzUCTta/RPe3cdftfSL7gTiZjvoBwiaoNMY8yZ+0lxmqqJK2htIm05k8VGwPTWYu10KfHpnM7lJhrvwhQFsyRgqhftBda5h2UapEmpTP9q5FkH66CotETIm+QAJIQeRMTWkveJKdgdLCvDd5fCNZv0UdQyyQtRYeiJCSkHnvDeCX2KVTAVA6+q94vpJ/FKWnxVAw9p+bU2TZMAdHO8+lZ3R00JMbR4nQBoXC+ABLY4W/4OpOHrT+wu/Y6G/FN74aB2TssVgteDmhQQPSajOQYKiAEF8ovAvF5/baBzqbwCBiMzFGP38A8L70AZH4p0NIK2SAmT1BXdbEOnS/Fqe7hBHlAg7W4fbMRT17ek6Af4SfhIQkE6UA==~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f7AbV8dxTR5ddT4WzwQ%2f4gxtDCAb5yOp98jRZVl6Usf9H5WjkH5aTq7NxRTzDoDyRz6bsFoyX+OZK3FbOwLEB469GWoGUHKC0TGx9HUnJG4FsYr0g7v8Zbq+3YnVw9XYj+7DVzJ6Cem0lNB9VJzIukKe3aEiMTX+1XUQE48dOJsFg113wgyJmvy4wmOZNhI53wQ7XaD9t8Etdhov4MYpjwrCJQbiaaRh8V4y0BzexX+HlIM%3d~-1',
}

with CarrefourDB() as db:
    product_listing = db.execute_query("""
                    SELECT * FROM product_listing where status='429' or status='pending' or status='not_valid' or status='403'
                     """)

for product in product_listing:
    db_id = product.get('id')
    product_id = product.get('product_id')
    product_url = product.get('product_url')

    response = requests.get(
        product_url,
        cookies=cookies,
        headers=headers,
    )

    if response.status_code != 200:
        print(response.content[:200])
        with CarrefourDB() as db:
            db.execute_query("""
                            UPDATE product_listing SET STATUS=%s WHERE id=%s
                             """, (response.status_code, db_id))
    else:
        if "productId" in response.content.decode('utf-8'):
            FOLDER_PATH = "./PAGESAVE"
            os.makedirs(FOLDER_PATH, exist_ok=True)

            file_path = os.path.join(FOLDER_PATH, str(product_id) + ".html.gz")
            with gzip.open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"`{file_path}` SAVED SUCCESSFULLY. | DB_ID : {db_id} | STATUS : 'done'")
            with CarrefourDB() as db:
                db.execute_query("""
                                UPDATE product_listing SET STATUS=%s WHERE id=%s
                                """, ('done', db_id))
        else:
            print(f"DB_ID : {db_id} | STATUS : 'not valid response'")
            with CarrefourDB() as db:
                db.execute_query("""
                                UPDATE product_listing SET STATUS=%s WHERE id=%s
                                """, ('not_valid', db_id))
            

