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
    'guid': '7e8ec713f5bcbd744b75f2ebbe042759',
    'gtoken': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiI3N2E5MWY0ZC0yNGNiLTQyODgtYTk2NS05YzRlOTE4NWJmNmUiLCJpYXQiOjE3OTQ4MDQxNTAsImV4cCI6MTc5NDgwNzc1MH0.N_oNlkDxMTNl12w3aGXy_WtTczpd8Pd8GD4_EdVIhkXXzVHWlL7HhkYQZSJvuRGUReSik9Ctd7nNvNMEOj8-Cya1sOO1H2k_TPntIj8uWbQrdR4VwbxTZBY9oPW7vglKI0589nHahaB8FW_AkyHBn0Il3XDrFllim4DZwlsEm3WaGnQI7ZyMts_3BeRJO49_PCDPESnkkxTVAKByS2bi2QxpYpLfMkOV3guiL57I6uVZQJ2S9HWI95KkXpAD4RPSa55zEJmxxT5Kjm2bw6PgG8953eJy_2QG9T5Cm2BXjuXxWuLuiGuqOcK47LHebG1WIpG7vosotfiiK7eZ53uZRA',
    'AKA_A2': 'A',
    'bm_mi': 'C3D4FA3A1C474CAD1343F681243E9CC0~YAAQnPnaF4KhisOhAQAAAF2q4gEHxdS9kyMBBWV+NjnvTrzbyLTAQ4uZSpEtB+AE75jELKVtdVvllChIi6nrAYUcruUgzUh5QIwsuMhhr8+JFnP8V1YSkJ1d/ni4PvNuepM1osY/c7czEYxTvjPUCGsTZIXh9ZShz4126cSAVQgJXajwBlKE2YjfkKMAKaXJUhCWdjvyQ0gfGLvoIkHmAdM4Qifo395bYjKyv6zaEcH0CiUiUmUKluY61f9D42bBgJa7aQlE+sLdsk3lHQZknIuKyCg7Kr0op+kS9bbpNv1uYBNXuuZm7cNs4ZUXOCdFnSptk7utRfaZSpWQI+PA8rrtm1f/xaydvsZ/f7z9L+1Vb3E0lBLIhtNg+cAtJxrMbXAg0tCXCHEMq5M=~1',
    'bm_sv': '83501C4A623B71C2EE4021A3E4D494CB~YAAQnPnaF3eoisOhAQAAb52q4gGOs/lczT1LHJsp+1PWRpezaZcaBjuirvoE/De481GiyCsZB2iCZnsm8TGidFb1aYvyXLt7KsgPcSj9I2pZmyFedTLVUKw+kKB4+sPW5moQUr+Yv/B/a0zT91cCSfLNSBmzzznzk1psuRNxzaFWX02PiOj6EfQANUtJc9VUWppXzQJc8fEjPfHM6Zh1o2wPA4m1ns0n9lI+bAPDklCMKOq21X83VitB1pL5+44Guzo3Rg4fLQ==~1',
    'ak_bmsc': '2B74A74FA36EA121B72D240D8DE24A06~000000000000000000000000000000~YAAQnPnaFzmqisOhAQAAUqmq4gGT4b1CqgQoJr8exTAVaIQiOck/51p9BVDylEosYNIw6Fm/ybEBvkEmBoKqdy+DC12GCrkjJIIrqDzrEPy7B8uSGDboSdut8EuIyg7buxa/LXcMlm0BuuZtaMptcSqdqOuCwFfttnIY0kn7p1UHJe/eYrMly6yTsIIdDpiq9lfE40d4G0GGqWtU67JF6el9upv4pkO1lhLiTeQSmf4Nm7pLu1sjKyGr/Zd/BAox6vI5iT3liBs1qIxXiI1AVz9RtYjWyGFbTEPFs27yR2CSTTD+OGJxjuuxMEjFfZIrrpafiA0T2m7lGJemN19V8nF7h5J1HxZWBqpoIEN7yybz2S8jjj5/aFSzzQ9hUb+Xd8o4sOUVNQ39SyHa3o5LRzphmnovjy7GvGRGCUvWnSODyJIM5wrUMJCz0qr8zXe9rmUqaidAX2Wew1S2X94M8BRnDPSfTg21yay+fkxP/KQGmILRsTdMdZFCvzfoBw==',
    'storeInfo': 'mafuae|en|AED',
    'JSESSIONID': '60D100ACE1B71478B31A83967A24B830',
    '_abck': '20E3EEE906C4D4CF4C197A940EF9E3DE~0~YAAQp/naF1zTWcihAQAAGva64hDBPJ4v5sqZsbo+pomfayKBw0PnQXRsfBPsf9wbrMS2Nq+iZtnyI6AvTtHCQS7L5zpiERH19Vfaqfl65TXsKbMD7eklJ6fM/uiP+w4pRIF9MjWT4b0G84FW5SskMiSJvcS7kgBz4MFm+xbvGjU+tLBj2sqUpa6fB10IIQiMkYqctRHn/GscwN3WPVtFBCVlIqbwgmFFxp705Swj82bzb2B+BnmuxeyX8Ea/yQrSzp7faDEqeeuyS1gNp8/yPMtQaMi6R0+cWWirQi46G8wc/DesKmviWboTmTBNvQcLC81xP3UxmBfvnzIxmSPb7audei/e3boBdKM3U78Q4GJCYUHjzjbyH1Bu3N/OjyzsGoIT1PWg3npZP5oNUwIzi+jc5GcC4uFktMcqOW4nYgqofGDqm8uT1kDo4HpNktVP+QAhS0puj0C0XdVMNNgaXoqhho4J/xt2v6jmCxU4LQQ2oSDWfqs0wvgu59uAKCiVaVmwAvXPrO2NacLfWgttLRg1TukI15PYasvI9ntB185pbjVVd12mlkvaEPhYyYylc4cSCtV3hRGw86ZMHDaUgVd/SX/ihdoS1rKTfJuNb0eyv+fbMa1ySS+lfrisnsXbmFAOFOzw0wuJhsff38+pQZVAjc9fyyCiI31a0wCRhcpbbt4OSiPvNIW+J5j9BULaJjQ6pDjnTIHCWuGQjJfGI2KGTADcrYlc75odbBN42S6oR5YUCbBi3FpTC2lodJdoYr4/4b+OSL5N3+cwClW/jh/wPZjo2wG7dpGkT32Q4Zl4Rw+rCEGStoZcGEPX1qlAgByTuzpF5frLTC9vwGMXPlOT5ywbUqt5g4AVEecB9VTKjk/J9nM/nglZxJdz7O9ZFjvned+tqfKeA5O0ymQQeAbVtXDnEyR+Jw==~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f8ruBrF7vsoayyte3evUQKHfJA2ZG4rkss2UzwHfP0B+YAMHyJ71+id3j71IsNjYC%2fFDpUV9%2foH0CLrj38U%2f8cGLKoKPzLFxNu6q~-1',
    'bm_so': '817199438C93E3DC8C8A78FE3F84449E7A06A6F37402D67236F99A890D29A1E2~YAAQp/naF3KOYMihAQAAqe/N4gmo+gzoE5gEQe0lqgIalRdDJD4GHdFA+60WK046ABgNLdhYres7/P6PkO+6jdOnMBqvpsgXyAGTRxzo1+osa81zhSnfcdIhEEy6/alHXYYtcn2xvy9fbuqF4BvzK42DM6xh2REaimSXvCOOcJlmuvBNTJapgC+wVXHK1qECd41qWFdbDMehiL17+3leGZL6tnfcUHVQ0w8VJSeZDcToxlgsy+iSye/HFKlPiwahErn+K2I3JtGyAu/SmbA3aqcOmi9Z3fOuIYZIl3bLjqO6YbSAUcf1SVy7dZnJUiaaJH15CyLoVibKB/YF1TfSy3hqKD+bQqTqizFu8n4uybvISg9TW1zdlmnp6qSR0Wg/uM+IDkSU2LccSTL1RDdnsLjuXVDCzeTU3sMzHomsoS+ZcKgeNklQH022w3S+IRNe9TDemvrQOXJyLjQawrTWpP0gWjKDgRxBqNT047DQyn/W~4',
    'bm_lso': '817199438C93E3DC8C8A78FE3F84449E7A06A6F37402D67236F99A890D29A1E2~YAAQp/naF3KOYMihAQAAqe/N4gmo+gzoE5gEQe0lqgIalRdDJD4GHdFA+60WK046ABgNLdhYres7/P6PkO+6jdOnMBqvpsgXyAGTRxzo1+osa81zhSnfcdIhEEy6/alHXYYtcn2xvy9fbuqF4BvzK42DM6xh2REaimSXvCOOcJlmuvBNTJapgC+wVXHK1qECd41qWFdbDMehiL17+3leGZL6tnfcUHVQ0w8VJSeZDcToxlgsy+iSye/HFKlPiwahErn+K2I3JtGyAu/SmbA3aqcOmi9Z3fOuIYZIl3bLjqO6YbSAUcf1SVy7dZnJUiaaJH15CyLoVibKB/YF1TfSy3hqKD+bQqTqizFu8n4uybvISg9TW1zdlmnp6qSR0Wg/uM+IDkSU2LccSTL1RDdnsLjuXVDCzeTU3sMzHomsoS+ZcKgeNklQH022w3S+IRNe9TDemvrQOXJyLjQawrTWpP0gWjKDgRxBqNT047DQyn/W~4~1794806509576',
    'bm_s': 'YAAQp/naFwCQYMihAQAAhfPN4gamzH0EIJXy3rDbGHNySLKFB5+/qG2v2ObaM6yHbqbOt4UPjwJVSQRocuPBqJFgujKE3o7xAXpYsWYubO6YxYRxsuO2pKa0cYGT3cmYwE285VGewz8Bx0dGpE0VzXxwi/mUuU4W0UPyMgqG7hkADkiNSlWiFz1eO8kJoxUU6uOPjYBKu49pR+9MM8kqTYOVwJlyQlpwjwW5ChLSvVMXmBezWE+uF8siCR68evCOAVqLNh+d5EdebXkt3OYXgSTagwxiQbvQiPB5q9D7HfNr+sMGB8+7eidKJvo62utXz4HrH5Qg1rNa+w6GO+nxHuvVVePbGgsdfrIZxqFeAF9trZi9bQLdgjCovOlirIhHHQSbKVtVVlKSHHtyUsT33Qe4U8kw/tQeXWzWdbKSG+1cr4F1SXQNejGvdDTpoFWjH2vjFRvp23tSCmPvxitINZ6AqRM6JPmDxX+mmj5tWOeCekXyMoETmuSnF0AYEqj7Jc8QcYVRreL8pFGxIqy3dHPIf8X7ddDvk85NfK4hRp65US1+dyo1RHkCu7kot8uluis+R1isjlTt40a33Y32cUjQEZwW3d3ZbF0ShgAgb9EQn4uBiZtVnJYDZXTbcz+VwDeHiCOkpwvCFwqhjeA3Ig/a1qEHZaesFSihdKeo0B2d35zseHBAJn2q5W+HYGdGoizxItpiP96aqp48ytK1V0MMT7azlJMf4GinPnWnq3YPE/TVYITRKRRNqHVGMTw4Fe9+HWwsniXdMUhyMOaxJgSeDuddelCaKXwm8av6mIqV9KPeJcllsT+aNtZrizsUpV9UXUxyOzAdMTpfbnswL0DmFLGR8QUu8+5Dr7M1OAplUoXlty2MowjBmzmuS6lmoPq+Y3mPCR/manHE18GgLaiHoRP57/hNpFFnYpaRtyMOCLw3m8XcnLH000dtdks1aF9xb275vQdeZYLsoUAB0Q6d61Y9T3UCNLVB8kJHmhopPWjfNJS+++dtBBjkOubBO5/y8j7nwARv3DdBitG9FxqGM1umJyvlzg271icZv3cYujCvy253BEQV5DZNxNbeNxFMeBYEggsNNWrwBXKDWUcydUXMBfNntDDBMGdf+Kw1ceEU/AHfVcpJarRmQgiEJNBI/mwNbw==',
    'bm_sz': '45157FF4BFB453BCB7D48D8B81343329~YAAQp/naFwGQYMihAQAAhfPN4gGX+EjZfEPuWtUhxz9lWfC56nMjMW/fTr5beksYztuLa335uCMe1zOBsfsP+EZD/LLCZqKgvs4FQG4TcKH6DCZ3MXAc4KSk4wZWCijGJftL04nBf6A2cxmz9Sb3slQwHU8Wtpe6l3luyAXG0S745Mbgm4DLxezPj/vAKCEXrAXFkZcMdd9wO/GcQRxeL5IG3IOY0qZq8XvV9nAbLz0nxQ5Dy6tQ+LVtDvKG3clBGfYac2Y4FMas1Yi4yALTmRIwfhtxx1xZiWlqiE4Zy+0FCJQuSr9+OCcJZ7sBK0pWd5O7ni0PtT0vivVktMVw/AIaIb+gPrUtynqeuOEZQbQZSKHq9zTPJomV8EtCvdbJXTItcDGWI7Hm3XOYVzQ7Az8xzgvg2cun843+1vinqgImIJYsmcaF8yxiKE1FKptnB0MbUIDCB5E2DqNiEZoQq4tl4j2Y8KznJxZEXLMcnk6wvk1c0PT6OmIq/xMO/bGKDfu3TYcL5Z4WWN0pr5s5JOCy9JGijAIZekDDCKoHBA==~3684677~4338754',
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
                    SELECT * FROM product_listing where status='429'
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

            file_path = os.path.join(FOLDER_PATH, str(product_id) + "html.gz")
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
            

