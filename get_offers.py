import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from db_script import CarrefourDB

url = "https://www.carrefouruae.com/api/v1/pdp/vouchers?latitude=25.2171003&longitude=55.3613635"

headers = {
  'accept': 'application/json',
  'accept-language': 'en-US,en;q=0.9,gu;q=0.8',
  'access-control-allow-credentials': 'true',
  'appflavour': 'carrefour',
  'appid': 'Reactweb',
  'channel': 'c4online',
  'content-type': 'application/json; charset=utf-8',
  'currency': 'AED',
  'emiratecode': 'DUBAI',
  'env': 'prod',
  'hashedemail': 'anonymous',
  'lang': 'en',
  'langcode': 'en',
  'latitude': '25.2171003',
  'loadbeaconspixel': 'true',
  'longitude': '55.3613635',
  'mw_sellerflex_enabled': 'true',
  'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMzNTU3MjAiLCJhcCI6IjExMzQ2MDE0NDMiLCJpZCI6IjEzZGE1MTFkMTdkNTcxNGYiLCJ0ciI6Ijg2NjdhYzJiOGYzZjUxMWY2YzU1ZTBlMzcxZjE4ZGI1IiwidGkiOjE3OTQ4ODIzOTUwNDh9fQ==',
  'origin': 'https://www.carrefouruae.com',
  'posinfo': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04',
  'posinfo2': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04',
  'priority': 'u=1, i',
  'referer': 'https://www.carrefouruae.com/mafuae/en/shampoos/pnt-suncare-sh-cd-dp-500/p/2292935',
  'sec-ch-ua': '"Not-A.Brand";v="99", "Google Chrome";v="157", "Chromium";v="157"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'servicetypes': 'SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL',
  'storeid': 'mafuae',
  'traceparent': '00-8667ac2b8f3f511f6c55e0e371f18db5-13da511d17d5714f-01',
  'tracestate': '3355720@nr=0-1-3355720-1134601443-13da511d17d5714f----1794882395048',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
  'userid': 'anonymous',
  'x-maf-account': 'carrefour',
  'x-maf-env': 'prod',
  'x-maf-revamp': 'true',
  'x-maf-tenant': 'mafretail',
  'x-requested-with': 'XMLHttpRequest',
  'Cookie': 'cart_api=v2; common.mw_sellerflex.enabled=true; __privaci_latest_published_version={"v":10,"sync":0,"kn":"","cid":0}; __privaci_cookie_consent_uuid=892b288d-b4ac-46ef-a2ce-3aba9ac8388f:4,05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consent_generated=05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consents={"ts":1793962667,"consents":{"249":1,"250":1,"251":1,"252":1},"location":"GJ#IN","lang":"en","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":false,"status":"record-consent-success","implicit_consent":false,"ct":3,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}; posInfo=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04; posInfo2=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04; emirate-code=DUBAI; selectedTabData={"selectedTabId":"80","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL","pagePath":"New_homepage_standard_June_2025","pageType":"Homepage","pageId":"4044","pageUid":"Scheduled"}; tabInfo=SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY; mafuae-preferred-delivery-area=DubaiFestivalCity-Dubai; maf-session-id=B0CEDE29-32FE-4D51-ACB8-B5E62BA13370; device-id=40ff88317e022fbb14c2dfba0ed9246f; future-express-delivery=false; gtoken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiJjMDBkMjRhMi04Yzc3LTRhZGYtYjQzYS1iZDkyZDZhMGRlNDAiLCJpYXQiOjE3OTQ4ODE1NjgsImV4cCI6MTc5NDg4NTE2OH0.FGEKts0_0zYWh-n9fw5785Wq5MGfY7aGO1gu6tMm7DK_gomykPH_a2lI67207WHpmJRV2KJ87PZhIjbBhEo3wrMNtaP12Nd42a2JS8XVff7vo50OeGYBL1reowm3qy51JVZza5pv1g5BwInNY4TsanKmm_jiBTtOXhUMNcoo6dzYymTcDu9iUjObPsXntFHK9agG3LMU18XVN4dyY62mWOOHC6FcxpBwjh8Mbow2Zvf09H-8kaBPctsAUxotXS_ZMCmhxrXHJliENuk5ug_pO4_VaY3mIFJqud7LcjMzhgla84OdppuAMgcKJrAouaJdrzEI6Ql39s6Myftl4s8x3A; guid=7e8ec713f5bcbd744b75f2ebbe042759; storeInfo=mafuae|en|AED; AKA_A2=A; bm_mi=D899BF440A71E8F73F5BA978FDDAE050~YAAQxPQ3F85UNMKhAQAAGRFT5wG5QI6AGCLkBdft+lF3SjvwRjODO8hWjlBbD4FE6nU1SwXGZSV7fBnPZAsT3ze7K5AuPTIXvjYNBcI4GsQdwSKODzuBLpXYR2p3oUu66vXt+gWak904ik6x6wGcAmDscCeODpC2qo3F8VbJq0chY24jZDgaBp+tgb4YsON0/N9fNYLxSB2pXBow4yYL0xxmvICVQ7yxnM4XG/JPUDWoKMd0O2fjH3wnYBpugSH3HknVv4q2Mmxbvj7W5GY/vBf4Brz84l1+vPdss07QokInnf7IIS8o5aeITanHnrBfEdnONudew0m0cvmvkR9YJ9BroOFQJkgGMsWJdTS2+3EZOyCa9pASM8GsOQluXPUtPpDlIqyfDcY=~1; bm_sv=7987F3B6EB71A8CEFC6380020B8B9BCC~YAAQxPQ3F39VNMKhAQAACz9T5wF4ZcAfLqiGr5CLdGxhoA9oTEiH8EWFAs4fi8q2twHfFhZRfn5MvyonBvcsmLPuPMIZKjDlvQJYdwWzRJBeuMf251lT96gCrBxLIHfRGLdnpHxmReYeqrUrOJouhfzv3vZ/oFc0ee+SaOKbc5geaGf+yRbhLzI9sYIkbqCQe2GbPBjF//eSFxbcQ7t4z+V2gJ1VE5eYNBCUcIPHXT8QSbJ2Fm2BE2SS/r2G74YavL8x4Rm7LA==~1; ak_bmsc=1C1825D4C0078D9FE1D47FEB720E44D6~000000000000000000000000000000~YAAQxPQ3F9VWNMKhAQAAJZdT5wEtbJ3LTS1ef1KLHwGCbmwjNWZZ+aTBMaHYAE6ImQEe2g797FCRJwb6O0WTMLM1brrHjHTCT1wxQ9VacycD40mvicE32L44qW09H6ZpjXAFzS8i3x7JEZoj3YtZsmTIB9SE0kPx39HjEU62m7zHTzV17Q8tYV7sUlUUSm/TcNBF/eHzU3vRgDhbGBtaVGl13azcrliJg71wjCtdF0vlt3YSlee+IiLeJtsa0+GpbQJbKidF78lquN9nkVc5xeNFnbdzHEznubQFGEWWW8AEsXgLDIsFCyvFjIegPrW73obbN0++fp9gkSi8RqP2lqB8TU5a9OKi2yZsC779+Ej89OV5OgWR0N1OJjqqAjqSfHy1tChyth44eRG1MtQ1Mav/F7bGZH2X+LSZb7rw7/x4rBG4Jl3rjwH5A/gX8tt1keadxv3jDHjs+Dft3NRM1NQ01Muk71n+9aJu+FVoNqbP/PtaLcPwEs4nFz9wzw05esXeOor3exKRJ/vlY8a7FXqIsvI=; bm_so=AA8133C93EF0708AFD52E5954507115FF5EAF530B46A7570693530DE7DF77E52~YAAQxPQ3F9dWNMKhAQAAJZdT5wkhutZ+yb7wD/RnK1v5ZcPShm6b9dKu6p76uuFxui1gvGHebuaEBlw11WjpCIGgTxPWGmpv8u09m7/FxRPuL85QaCshBOF1sjlhoBRyO4NSIQNTt/tQ6YCy2OPmU+QLRE7x/2NqAw0IZihW+vlweMOkFXNM9ttVlUL2NkIdh8UmCBb34k6gzY1MCIo6YSTUlt3A7v3olNPTldNkdItAb/C/s1PBSjEPO/C5yjQppgg0UOf2or7FRYBNtndbD+qfz6z5xwJxW/x0JL/LRQepVhudgTkw6B2LacnIioNaD+pxtEhMhjClVJGsoXHP/RlJEfTZM06WgoPXu7Y7ScRNl3DZTDDpVfNSHaHJHZNliLOQs/hLwRuiD+erlWZSB2C5lqAf14hdnON5Ox9E5K12jVVg9UFoTkBtR5Cf14nnjBGpU+bx59xWIYZmA13yl5SyfFCxPRqxvBsGC5PIWr+Do16ecHEhECobb/Hm3yr/Gy96nQu4UhM3~8; bm_lso=AA8133C93EF0708AFD52E5954507115FF5EAF530B46A7570693530DE7DF77E52~YAAQxPQ3F9dWNMKhAQAAJZdT5wkhutZ+yb7wD/RnK1v5ZcPShm6b9dKu6p76uuFxui1gvGHebuaEBlw11WjpCIGgTxPWGmpv8u09m7/FxRPuL85QaCshBOF1sjlhoBRyO4NSIQNTt/tQ6YCy2OPmU+QLRE7x/2NqAw0IZihW+vlweMOkFXNM9ttVlUL2NkIdh8UmCBb34k6gzY1MCIo6YSTUlt3A7v3olNPTldNkdItAb/C/s1PBSjEPO/C5yjQppgg0UOf2or7FRYBNtndbD+qfz6z5xwJxW/x0JL/LRQepVhudgTkw6B2LacnIioNaD+pxtEhMhjClVJGsoXHP/RlJEfTZM06WgoPXu7Y7ScRNl3DZTDDpVfNSHaHJHZNliLOQs/hLwRuiD+erlWZSB2C5lqAf14hdnON5Ox9E5K12jVVg9UFoTkBtR5Cf14nnjBGpU+bx59xWIYZmA13yl5SyfFCxPRqxvBsGC5PIWr+Do16ecHEhECobb/Hm3yr/Gy96nQu4UhM3~8~1794882379326; JSESSIONID=29242A6BE84F8FB00CA9969C32DC8726; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~0~YAAQxPQ3F1VXNMKhAQAAdsxT5xCilcRuADraH1acJns8c/Vc0XJQCk871Fgt9TD25B82ELq2+rIJlY8aAa16RWr+lR9tZMdW/74aor0EYeTYL4lCxAzhUTkKuzwWYOQw8KreJO3hrDmYdrxomGTnF10Dze8Ojp++Stpmvk8ZEkYWhgSamIY88qcXDIEYZ1SxIuq7aXucqDk2gI9JMGLYDgCREE8fvDSkcADNZkXCe6nH2zW/TMOJ669g0XmbhYV4jHRLp+BXHIA4jLbzZJteVAXsjH/jCNPo7+mcAaR+gYDHKSMZb809d4NFKU1iYh7/31+mke3QSFRSBfQR7A8+P1vLSkcEFPY1Cz5Rl4bgDGDx2nKSSiq03lcv/InKyG5N4hITpBetqWw1EgayY3INTIt5cR587V+g6CcN2lRsrkbtOesiUvEDYdEkuz1hP7LiSfOKFcCj9STr0H7YLNDQZqYxz4PREfVQ8VV3DnJjb/CXzGW6Szm0e/Oqrh534TkhgvxdnXxAueNmxXcTrjn95LqyBSYjhqg0nd1mINkzIZJNGc02qExr3+g5IOtA0KbOnwM9gcpavuCUlwk+Q5x0uK7OIqZTRjBl13dr7ezaNUGWDdBdjexNkQmdgwLX+ShN9rtYqxGuGQzSPL9I7bk/B3qNopeM33qqeGjQDSrf0wrg+WMNIoRIwleDgKpGlxVHMokfXkEJ3/YsUgvGdJmQqfOyNgiVDklObp1e9xvXUqht1OR5SsHHszj87dfniESdzDNLuKq2wKVLRORshxm84vGE1dEV34Zbb1pPW6ky2ZW6cHIg+U3LpMzk2X+aLzIg9RJRUZNSqwJAcPUG7B98U6uIkwL5hq90xfrdC3Iw4WPTHExXWuMf5HzfdptF/QuCmlX7g3KjACeJPqDE+oAF5AKlHoAUi6Wfl24fMZ0qZHluWAcwCoU/1sP9FTveTzuRq/P3hv+Z~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f2LzrlboIgQLpoXC84vO%2fE49cQs9MwTSs4utmIx7MlQi2XdxSEt9tzx3gkkXdfBhvOnA0Ph3Uy8bbDfh8mY2UYIxglX%2fWDrXFHg8Y74ZxeLgEHRi94TWpCd+llRRKWcht69gRaQ%3d~-1; bm_s=YAAQxPQ3F2NXNMKhAQAANs9T5wZfDY9xCwGdW/4ReP0gGdyBqHk5z5kNX4VSzoE1QtftgsI26ugoX4/BQUM5xEP0bHRrHl3lsgSJDGvkIW/D886yNAVvapc1fDUnuxPkAk2rB0wR/2rgeWwBr3I+xet4PZSCoKDhLXyjzTctCeSjn6D+wKUGx48mz2uJJP6fubNE7VQyIs4q9jjK8sTNyB3NvYxDkIHVVFnHNKvbv/XXyrbaClvSi+QMJ6e1ddkSlFWr7QIDMx82cw1BMnFGgcfviMkUEYpjB+2tU6hcuiTYoAGi4TFXiVD/GryHbZEQe+tXwjQwXOmw2pv56kr6RnxkeVtB1p6eHuaT2LapWJq6tukAugekIeAhLWqn/kOg3KqVmxj+9mNwsvm3ZMmiQI83z3gb8691Yj/OPFnuXQjJx6i6EG2MUDpiOyba6+On8mFCbGDAjpVahkWiLFoEDxJDeHkalIngHhMmjJPpQ/R5YxC2BDpYIHV8qRlcl4HhFhCWiSXmW0FuXw1vHDimAngv1PnDQrw3qfRxKGgumYJ/ittTYv6OgO4Zt968YXV9PoqvdBWsh7M5P1RTxx6PrfcuiAQ+p7v1LyE65N70wCOKaJ2w3Jri2nVGuefHlS7TFnlVUrZplLVPlHSwKKftNT92OXv/hDTcFnFTGvAy4DztDvZRwnhkVs97Zk9xfCkrwpKaMKJPEFm16GTqgummI1DfVvh+/lIhCE7L9uME+ACIRAVYI3a8bKZ22Q7t/FUVAAYc+jfTtpoXJoEiPdsn4dAvuv7m8L+zU6bUsYZcv9J86vSUU3D3H450v/N2tUM2zubqtoYp7YW0ll96WS/MgEVL3Yk8pxRP6+z9eqQzOohfvjjy+oAE5zraaqdvr6j2ldA+l4xwX6gk1PYaIGvzLBX60Wd9h98n/qf4Ri76hpc6O0ZNIFgILa/yp0hiMGr6NoONZL7hQ0curjxcgdmIkeef3c/Gqn3gFKraWIuAlqZwuRaiOZamY0xpFEub+P4R7oTb9VUwTwFP0fwBahJtb3oGS5axh872UFECDQvM2hhwIwILEshXr7GRmrlZFlFyzndyRFQzAlUIG27tuNx3/gk/WGD+zDFmy1Kdn/u+AglVTn1JMOckl7feggYSJGzD1l7a0ckztZXTOvNkjXa5ELKZpuFNrGaftcVrV9A=; bm_sz=FDBF0A048B22C74CE3F723862774240B~YAAQxPQ3F2RXNMKhAQAANs9T5wEjwf07d5F0l3sNwcjOLvD6bpF5qKH61ZWKaA4h1Ip4d6xvIx88G1joj5L6cYbvz+VCVLbshMvSnc2D1JCxMolqMVo4l19WyDLTce7ZXuxLYGMYkB/c1oLgN0qZafpo7581+j5ldSOSedvSHWwU6kby2kX6gjGww+9MCmnt0AXLEMPSLcdFspT+VxOsMQHU9LUJBkV1LWaVfBqAxAl2EZ2uncIcLKX9WBz8VDwa4fPMonRvSVXlSplkYVfSsaJ+ipRXA5n/XZ79Z4uildSkoB/8Ylc0VEB9fBsII6PmyxQxDQH35Okn9rHnpbrZ35gmsrhBKRlObkdjmTXcVSrRy0nShHKNBW7vRX1IcmsqhJxuO1JRfqbhcb07IZVRgNjwIhXe0RWcDinEbCAAsW55j6Sa6oisxliipfPt1QfNoIvlWdUgN7hSCXLb1RURuAotWGyWmM0QPSDgfKqo9t5ccxgc9r79Je1QFOVF~3616836~3228740; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQxPQ3F6KxNMKhAQAADxJt5xBAXNgj1RIgygUTEevRey7pQ+XTzjrehUbYlJ2gKh5hxabqTtr8iZPRqwAibVkLGHX7EJ4lDy5ZbM/WOjZ6p063RSWlFuHmRNnVfCdCtw1eST/rqc+PEYOx8jXnBr4DrF64AAW83eUL8s/26FcbG/ZZuk+6rWG9tLYdQgPV4d7xdEh+9gIKV3l4EYUun9c3O4rOynRUVvo40sZcoXGoqkG4fol0JbDqxzX4WJ+eY0A38nspb/BB7qS6PUPuPZxYinkwB+ZUQ36c91XWIa3pFlvbTe9o1UBnJm3gJ8W/fSIZx3s1jZdHk0eXp19G5YivrLIM9Ql7W0l2ZVrLxgrPWT/uRUYgDi1p73yfoojMrl3hb/xByD0zMOuMa/L8dpffEZnBpCjZsK5v/54lHaadEdDd2EOtiO68i+QqDuNIoysx8F6V2+xiRi74ZLYLwKFBnfLQpmdy2j9glrUvz/rPVYERGUQ06M+/36WOluORDXeu6fa3xx+xo97ezawWwzR3atfRShMCdYQbdL6Mk4tuHSL79XBKtDnCDOA1P8iN5AxPbjLb/WTPIPNCnaoA4qAq6hhyNxJDftLugIa8jH2c6NAXOTlJ/gBV/PGbivn8K5KwZfYMiaXGBzhtdJjw4cGcuZi13oy0jGHfa8vWB3dS/60GypH72bGo6/AvTo1Lhach/csrocRJEm2LgstX93Adt2KQGcPyelpoS91kB3aslTP96c5M80ooqXoD4ayMsYQFyMRWCst5iSfrhy7V8ZpUzsY/XMqFN1TACugaUwwdmPGvfKDXr4FKTwPZ7FE+3+x+kG2LMa+sZzaQ2MZG+aI0wb/xykJkfTYXDBV5UvQa8HTachsFfoQdVTRTazmAPhXY3kdwjTSPcL+Bxg93dRvPYC6p+VU2vpvSQKblRKAi5uxqH5c9NGLCXeJSLDMJTK1g6lA3oXsKRmP9+dY7qK2bvgHrIGzG/YRCHtfL4bM=~0~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f2LzrlboIgQLpoXC84vO%2fE49cQs9MwTSs4utmIx7MlQi2XdxSEt9tzx3gkkXdfBhvOnA0Ph3Uy8bbDfh8mY2UYIxglX%2fWDrXFHg8Y74ZxeLgEHRi94TWpCd+llRRKWcht69gRaQ%3d~-1; ak_bmsc=1C1825D4C0078D9FE1D47FEB720E44D6~000000000000000000000000000000~YAAQxPQ3F1VWNMKhAQAAO35T5wHNeMGlHWgxpX1a/VLRZMxzdXmdojI+z5r9WcTOGmLRHe1rBLz8/WRO8kiBc367Hgcz8v7o0P/B615GkfqXTG9UiYWgMDDMie3p2Xc9iCKAlFsLWV1lQ9dnJTzzxbhvlOlnTcOzO3Rj8oa98BUx0hSrAE43cezRJCYFSUrz3NoPjYPKla4jzhaTPFjpGVpP8wyXviS72NupvcO8KyGverSXPoE+O/KlIeWRWRgQ4N174e83VtMch6dvleiiXa0e4eOWY6GyUgZYi74DttmiSEBVAhE/UJTI5wvCN566GtjeYDqK8PTV4yJsasEG7freBamtyn9tTOTesO7E7mVJwuK94F6YijsBQvAJEddIaVkxPIc9NP0kr5GL31nlI5jmyP5OQGmhMVkBrKNOxVP7UY6IDlfXvjC0mSt9ezi0i22hfQDc4yhS65ou1/UiOLEWTZdug2e4gem0JWcLzFo+SMbr7A==; bm_s=YAAQxPQ3F6OxNMKhAQAADxJt5wYJ7XwMdUlpDxOypW+lkJclXRnIKGQSzZBg90Mw03Gtr4tu8OtVs+W5z4s3yUlNj14VlA3I6aZPWP5IAEw2JIQp2rshsANsSFifp4OStb4XptSt4u3tlRhs/m09oIEVFWp0+FnBSLFeDYByoc9vwQz0tqmyE+kGrB9hNn6FA4CtjJNt3NlsbyEuacNh8w75HEYx579D+YJ2U/iOJnYD1IT/xVvKbWg1GA5TlE3d6jiW6C9P2gMjJBketmWqBdYcPXNxxGmS6+g7VUDz/rhpNKfuXE8taoOJkwg4jXrspjpSQT893Cqs0LncGUwZSDoPkFtYZXRJl+JsD5cSRjeM0ugHHb2EZyq22do51vW94UT/sLylSpsEjqWqGLZkCeEtyxJxgr30/vMLYspol3gqqLIX6Ekt68N5WhPinK2dQ4VKX9rg74hyAJcUfpORFzf+uywyHrR5CyQq/P4GeTqmVM4fPc274r8ileW8jhboa/7gZPQNNcou2MVcTGtBmu1iLV9Y1G07bsL9XGU0Bv3MZXo+59vczwQ9LKBdLp+E09fZN1WZNUbCo0lfPvp8xI0UsE0iYfT37tQ4eEa4jq+ZwBNgj1bmt0CYndvHWT2mtFjc8CviyRV/2yUUtCU2Z54l/Ovy52FV3mpBmymr7eLD37RF3OOua1eSk3MD2eIQzY+JlS8adTWwS4TvL+U5092PQHn8GhJQgMhs9G367Zug1QY=; bm_sv=7987F3B6EB71A8CEFC6380020B8B9BCC~YAAQxPQ3F1gzNMKhAQAAJtdH5wG4PyIc2/m81ypnytGdh/Zc5aJYlDZhsXu8RXEJMEYfV5okE5qXCnS0aOuzKe1tgK9p++YjEavK1VdqEaYCQk00JCRxmMutnZXjKEhrSHbfHbiK+AJnkoaJlJ4Kc+tJzRsc+X7E6nnKg5vcKZcUPH9XiUfJesykWvsBfCN/W2wk6dpDg5Ny2ZzkrWOgOdXUaZ5UJcQ+N4oSKOY7SL6MLYQGDvADZlCXOUNCL4V9AcX/wi2e~1; bm_sz=FDBF0A048B22C74CE3F723862774240B~YAAQxPQ3F6SxNMKhAQAADxJt5wHl0wdET7MsPLdBnyyiK5bk5xQcL9/lTuYITj0FcGYVRtZgF/49u1kXKStjYAnbJygbEhggApyb3jXStWIQ4AxPh7Akxqd1RFQzwPYWKVeIdLGOFllscHXx/YlP+RDR1lqq2GplFvvBcdCxycnke8TCeoKP0sjGFPl/OxtjIEDLkUhiDHoIapzpY5wvPJe0SfgCakdQiYxfC7xRfjgRR/4y2GeL8KwkYyaZlYXeIlIeAyFXcCdNs62+FGi/WhHeIZ4f05jcpqOC/UvyoJx46V1q6sw/k3xbY5kfc0+DU2DSnS68GpV6Tjn746XEOv2iNRnpS2F4fLoqxoxH2oUL79Kn2RrEO9BkkdpMHsTjFqNIQ4W+owHiX9YTrlntn3zqGdbY24H7ik9mWL89UVshJWmD+ous9mBxUPl0ZGKUJwPL4szhGVn+quKaBHkM0TVM4m7NZdYz6M8na9alMajcR2bpRkLS5rBv1e03th66jjimwiFQ~3616836~3228740; cart_api=v2'
}

with CarrefourDB() as db:
    products = db.execute_query(
        "select * from pdp where offers is NULL or offers = '' or offers = 'null'"
    )


def get_offers_data(product_id):
    payload = json.dumps({"screen": "PDP", "sku": product_id})

    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=60)
        print(response.status_code, "for", product_id)
        print(response.content)

        if response.status_code != 200:
            return {
                "product_id": product_id,
                "status_code": response.status_code,
                "response": None,
            }

        voucher_data = []
        json_data = response.json() or {}
        data = json_data.get("data") or {}
        component = data.get("componentDTO") or {}
        vouchers = (component.get("applicableVoucher") or {}).get("vouchers") or []

        for voucher in vouchers:
            voucher_data.append({
                "title": voucher.get("title"),
                "code": voucher.get("voucherCode"),
                "term_and_condition": (voucher.get("termsAndConditions") or {}).get("points", []),
            })

        return {
            "product_id": product_id,
            "status_code": response.status_code,
            "response": voucher_data,
        }

    except Exception as e:
        print(f"{product_id} error: {e}")
        return {"product_id": product_id, "status_code": None, "response": None}

    finally:
        time.sleep(10)


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [
            executor.submit(get_offers_data, product.get("product_id"))
            for product in products
        ]

        for future in as_completed(futures):
            result = future.result()
            response = result.get("response")
            status_code = result.get("status_code")
            product_id = result.get("product_id")

            if response:
                with CarrefourDB() as db:
                    db.execute_query(
                        "UPDATE PDP set offers=%s WHERE product_id=%s",
                        (json.dumps(response, ensure_ascii=False), product_id),
                    )
                    print(f"{product_id} updated....")
            elif status_code == 200:
                with CarrefourDB() as db:
                    db.execute_query(
                        "UPDATE PDP set offers=%s WHERE product_id=%s",
                        (json.dumps([]), product_id),
                    )
                    print(f"{product_id} updated (no offers)....")
