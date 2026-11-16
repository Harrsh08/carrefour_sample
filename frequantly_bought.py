import json
import requests
from db_script import CarrefourDB
from concurrent.futures import as_completed, ThreadPoolExecutor
import time

with CarrefourDB() as db:
  products = db.execute_query("select * from pdp where frequantly_bought_products IS NULL or frequantly_bought_products = '' or frequantly_bought_products is NULL")

payload = "{\"placements\":[{\"placement\":\"item_page.echo_seed\"},{\"placement\":\"item_page.frequently_bought_together_web\"}],\"displayCurr\":\"AED\",\"locationParams\":{\"latitude\":\"25.2171003\",\"longitude\":\"55.3613635\"},\"lang\":\"en\",\"requireSponsProducts\":false}"



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
    'gtoken': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiI1MDQ4ZmMxYi1kNDAyLTQ5ZWYtOWExZC0wMWE3YWJkNzg5M2YiLCJpYXQiOjE3OTQ4MzEwNTIsImV4cCI6MTc5NDgzNDY1Mn0.g4_HIvWX7owAOWEUJJpQp_oTeWgTWnCbK6ryiVyKZZ4TMxK76-Duwlk_UgTfSY4K4rG_-l9ltgvDrpHGgNHX7a_Ywz_InmgH83FAwwkMBHpfEqQjGCht_b_Bm_dWDKlEh8BGGJZjSI2UsM86PmA2JSnucKRzEW7s_cfsc9ZulR8y6Bl1KskoZ462spYHhqzLvot9IM4gOi-1MiSF-W11NLoo1mA7wSkPd74gEz4x8vd3K6JIH5J9gPyaYncOfjoW8UIEiJH-lwO_CQHtzMgUem6RpKEODBy_6fnPEsbXYj_aGGDQUxBGEOoxUTCYqROxDAZZUwblyAaFYrku1zwYQw',
    'guid': '7e8ec713f5bcbd744b75f2ebbe042759',
    'AKA_A2': 'A',
    'bm_mi': '7AB703848C73505EC34FCE01C2CBBB1B~YAAQqSTDF5IGCt2hAQAAlQpw5AHRfDBJUi/qwMu9jk9VOYu6LGEIml2lvExWOY8fgdSubEuHnjK55OvgwANJZNFlCayJgc//nvkbwYLO/9B3QYEnVvA1BA/wRWUuLhNddv8xdUl1cPP8pdRm19mhYkA+tvUrjpxQnCLo+doDpAkpUTFQySNk3lfbVujeOqW9WkuXkrq6TGmyb5hJTLX+LKFKcmrOyBCOq8mUIkm4cgBK+HVWPWyR0XOA9Z7z+YgjRLtpG+VXeSC15D3YoZLTHlyVskuFEdDAmb854qY6oLoj03gK0YJSSIYmYqJMQ+dN4xVP/SDEV/ForuM6nVerdwA3hZIspdPKOVN+jgHwZpMczHTk/RWmVnN/+QaxqhyNfXaL2ygK1/g=~1',
    'bm_sv': '13AFF4F639508E572A40C9A0794B8AFC~YAAQp/naF0Ww2sihAQAAO0hw5AHcU9HGpgbL5Ia8Yjs6poXIY4eTmw6oTgreVgQX4DFRyV87mSm6SeBX0nEU8Rn3iGOR1YiOgyXVviuZZSL6eRbEsRbws9gdug8Nrh7UC2IVx41EI/LdhEllf2xfKl1yMPXIWyXTaqpwsvRtlLEFz0TTP/Rwz8eu5XvlWdZ2sVapWZSzqqeSMRtL/NkjnbkI4Iu+WcVWroWxyqyL6/U/4OCYrfbbOv+JU1K/44hbkDJ78a7jDQ==~1',
    'ak_bmsc': '7206AB253292E82CD4F4E808E83D18BB~000000000000000000000000000000~YAAQp/naF/O12sihAQAAp2Rw5AGCFdoZJsAYQfBi2ON7WH01rJ3683u5zRlRTSo/QsmV7D6EWPrFVe6ft3NsnXjgr78NpR9WK81/SZA4dlz215/QkAaF2qMQt4sxWIKuKHcOatwpcggq9k3Fku16JtcKsTx4QzBH55Vs3fJBKkPSb5endRLs4VOoe1a3eVKaB/zu7gF+AzGqZmy7log8i0bnSMDSMyfpdXjkZlLv9EvnZBxI18KySSQmI412kHAKnz4I3ddxPkCYc824Jw5RJSPVC1zotu2xpz2CNYKgYJySBPu9ZM4qsvNsR+6zCOhkkC+1f0kkAsWZh4gUNDZmug2a9vhSSwkMoKYTNC7ss5e+7RGau7EECWQu9ocIyVyn2FvczWKj4RxV0KCdfduOWa+2cRqJwjrIW9hlLh6l7OS4tEq/dWb6i0mgYV6HWszrVor298XS1ojMxIoCF+XVdFC1mA0acmZXcXhzY5733Uklzmy+2r0WCS30PVQ=',
    'JSESSIONID': '406D2D237810BA158B712E2E254EB674',
    'storeInfo': 'mafuae|en|AED',
    'bm_s': 'YAAQp/naF8zd2sihAQAAIBZx5AZ3IruEHqiUUqMACaR86120x8vRZKvHlzBYcSRq5458dbVTeXgss3x/bCH+VNwhHZeEh4pscEYMoELG0v/FyIOZYTVxrlvPz3JKaaavRmMpSCHyWjwZhISbAg3+zE/88vWw+NLa4CYaKYZJPE0kuOhArFj21wjaOZ9TVVEL4fqjsdyvSsA9XYMeASZM+BNZ/BK6wJljHKMPYvD1QTmh/zalVpbEN4gDlqqtS1v17RSMljYIwIoXv980DP+EmvLp6CBtIHAX4lyBRApIqbHYNv5nszxGQ1nbvCqgPFGWkZSryqrSB4YBdy7A1gFUT55LdcXJzjQqYKtwlTaGKR4Uuh/NhtX4/eHFSccN6fcPfXfHuIUY2mIkdwYjYNNGjL1jrZM0xLmF5W5b0s/3hAQimiJwK3KTi/rWiZ++p/aclsMn7lOKYVjs8f8mLV29tRm9XWHMGG2sL9oh7vM+fkzImMrErdbHY8+Yjg+CEIC3CShKGnYFyvWU6EH+5aT6rZy1djLRwV2T4hZMpyfkbKXCFzh4p9vK/L3KDTWVVtE1/IpAmoljs7aGfV8Mt9dx+8VSDzXU9J0ehbdpTe6d1zCzD5l2ah/A0YzmZjVCNSOuevJl/1ce878rFgBQ0CRt5KPQWb/Ye4JrvoKALjJhnhJddEp11fPAQst8fqPZMflBjRosDPYgPZ449LdmjaI6ZrSp9C6heT94BhwqhPSlCjRYCwUzulnGF7Sr/UW9mWrvTrTHOPpZN71NzLVG9PW0NU99DTV62PpDxecqKlEAhkOsGSyPc7WcX67STcPrzX4eJCUbSwzRbHVq5KvfJcwatgvvqH+zRe7hOvOR9fK+I+SDfh3A5+ghBjDMWO/j8JbIoRSb6Med99GeVJ9ONsMsbT5689/3bBsfj3T+honppHv0+iPrAQ36pxeqFyPzx0euWg0xpPDBKHqxaY7ZvSUyIKOGEv0dMAZ9yBRoiN8/VtfrIjWPnfobf5v3Pt73i1G5EMGh30+PP0j3A36iuxbn3JAvT/6QFoGqfXVf3cAGqHCJTTYDX9O2DYxvtQLjjpCzeIDVqw4I9y11Zm/klYIXY7r0dHR94gk89l+vd5CKcfvRDuFVNCXhxXRhmFVkB5ghlbParaTT7A==',
    'bm_so': '4BFFD3ACCCFBEC9B58718C9DAFA8050E6019A384BC1DE85E305028CB7DCDA720~YAAQp/naF87d2sihAQAAIBZx5Akgzzj4dlEEKguSQ7bl6Rsjsk7s+EjBZu9+J7875Ye1QcLSM7jhGO8ri7j6YBRrGz8m2s0A4u2e5Uw3fc6F+01u0T7J5SNcj5uFRFhyRlwT7Tn8Um7GbJ6PkoUObOsMekUtz3WkGqwMuz2LNZzCcbK2SXo4NBuqZkl1/CjnhhK9F9ONumir1URGAh1BbNtaPalOrfQafw++PT2VdvaPzU+wp5iUzh8HYAbDDoxCxZF8tIdVVoou9RJhV/DaqQ3AVGDh6fUy2BxpNRROelOIaqlro019OEj+Zm+kCdyr/hB89qecHPFVwfEd8ds7z1Hn7/3PGmZWAMyTvm+juHgsbEKGPfpea62+RwCviHf5y+nmOgIftzyVVNUzNS4ZbeHkOJ5YB9FlIA4JxxsBeR0ZZQiACfJUfDBNTnNcQHl2P+Ko1vcTVp3Z7nUCEJqLjBIIeGkXWDwxrnHGCklc5eV3~6',
    'bm_sz': '4D0C1C2A610597DB89E448A2D9658B64~YAAQp/naF8/d2sihAQAAIBZx5AGfLwfpSP8f45ecTfTzLvR4ILe08eIjn07dgjP43ZFFIYPUKB/Qu4O9TV8c+V9ut8mx/J0gROTAH6WqpGTnr7Kt/ZzZxIUnXqpuYin36tpEPoEptW6mKn8oP/u8rykFYZ0eANetUal4w+jh0F763vHojzTl4hrTmonrVM9kD42A15fEYgi4j+/tco+t3MtYb4iHrwlX7mUQc51ErPM0/D3e5VKmqo5l7BL/FUq4q5hPTpzblIei5eJjn2hbYV9CLAt+LC9lbStP1sz5qvkC1O/ymZHsLCHS9iEwZVVJjrDvp/TaGqBaYBYDC8ld9PUhYEzoniVwQ5OwqQXnMBiSY6koLVZ29G/VNuoT4YYMCrq0kD5nB5pFACpAVyKXwYChLtRpYoUh6O8MHZYWXBwXmK+bL4Gm0tFcL4fYMdAPa8Dp8h2K9O3OkYMRKrNoa85kzD17590BpkfJfnpejOzKvHaJ/ptEnIZevNHO2xlJLl/AYTdASd07dlwF299sz3+JMJmOw5h+JcFS22knlV7sTLDOHzMPz2h7fT+vAxHyFHz3OlfZy//D5sUeDsv/pxupEA==~4535365~3225396',
    'bm_lso': '4BFFD3ACCCFBEC9B58718C9DAFA8050E6019A384BC1DE85E305028CB7DCDA720~YAAQp/naF87d2sihAQAAIBZx5Akgzzj4dlEEKguSQ7bl6Rsjsk7s+EjBZu9+J7875Ye1QcLSM7jhGO8ri7j6YBRrGz8m2s0A4u2e5Uw3fc6F+01u0T7J5SNcj5uFRFhyRlwT7Tn8Um7GbJ6PkoUObOsMekUtz3WkGqwMuz2LNZzCcbK2SXo4NBuqZkl1/CjnhhK9F9ONumir1URGAh1BbNtaPalOrfQafw++PT2VdvaPzU+wp5iUzh8HYAbDDoxCxZF8tIdVVoou9RJhV/DaqQ3AVGDh6fUy2BxpNRROelOIaqlro019OEj+Zm+kCdyr/hB89qecHPFVwfEd8ds7z1Hn7/3PGmZWAMyTvm+juHgsbEKGPfpea62+RwCviHf5y+nmOgIftzyVVNUzNS4ZbeHkOJ5YB9FlIA4JxxsBeR0ZZQiACfJUfDBNTnNcQHl2P+Ko1vcTVp3Z7nUCEJqLjBIIeGkXWDwxrnHGCklc5eV3~6~1794833980834',
    '_abck': '20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQp/naF9jg2sihAQAAvSVx5BDfJx4BmI+B0md0SjLwN/eTjWRJNypDqe+UC1Pl0XR1Pzrvb9EH4vZxKSFEJ4gtJpKrsiKDDhe1Ydc3BEiAlFzcGlSFNX8oTl7n/PdZQgr7QTmUttESgnsa6MAQBYgAoLLyEA6Ve65i0x95EY7/zr/SRU2hcnABcJUcTr9S4tTs6qTsDDne4DMCKtn3gGMycBTqcR3zKIlPcV8rpMKw3JdpxcMNyhGKQB/B9rMwr8sogG1z5M/O8QpKE2HSYudjpF355qeGhfUQu62JvOM3Su//UkAJGSUSwOfDSSy4/YvbDgFPwSLsnFKBmGJCwkgzmue4cZq6eTCi4h14B39+sSO2h2SK5DTmPS1ysOCewCOhynVbkkBz9SRLceuJ0J4DWI+buBfC0JqzCipKRC1y4SUB+sj0ZbmRPSRS7agX9S2qLBitLNOzIcSda8ICdV8dpXWrT0hdTS1OSga0ezGFCj1OUfJZlnFL56P13Gm1MnB32Qj2fmqeNQBmDJqH8IVAHXDJsMOCfUoQEXs+R3TVi1i0KUFFWqyN+f1RkvsFf7IYYydRcqceW3c/GEaiS71pnk7PMip7UeoMiFCewQw8zmZ2hbNSgx8zCXPBgkTogM9FHxu7Ard/I6wz/cZUAfStb+gjs0j1qhbr++9VWdmDLnMP33PuwiqXKNKmbIf8Ef5BguE9jfbZT8zRP9+DS1y/WpqpFDoTI4GJa6R0im50Z3ZmKF35vxzo63FaAfgaT6HonEMBWFyySf3mgMvapU2AGYPYBBVCtFzQJIRZesvsL34sPFakWRCxS+no3iuAl2vsQG/pQjmjKZDbTNGCIGk8POAJBuhdQ6omNvs3Kh8rgKC1Ld7YOdEIAv5TJCefIrOD3hzJctXSVq0a+e+7g4yOBShtUxaxW1V76B471LCAX5SkvE7UAy8kgj+WO3nLh5+B+qKtJtcjl9/GrMI23C6xWCVvFSriBs8RIXVJWsN+Qfz7TGdVBHBtuef1e2588R80qgwYFJuDAu6s4jdMjVTCEsvs3Iq/rlVhCpvIk5vMKopS8S/wkG3A5Iy4iORYtvqCzI/cNiR3uk2iu9CZUkFeJLp/gQ5pTUGas9AXWhCK3c12FYSIrOLoyyOt7aFtAD2uXGkQESDZ8bVJxrXCmZk7XOrvC60iryORWcbHzPK3PJ1d+tKebO21UwY=~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2fyNOo+EfY5bdWYCxZDvd0xFP99dsGyjWkcmxmG74qVjwYl+KXefWa6nioYbHB4b2BBT8eFaQXWCaiU%2fc8H45RGyFL2ulBZoNeQqxaj3RIcYydk5s0UNsfQVUmKvYspAbEFgjfz756qngSgfMtF6OzDiQ%2fCLkZUKOEsGG3B2Sroh7ehTuemZrAmkZmR7PqT661DwHCkqo2jX1XqY8lvjKpsJBkSAf9iexoxthS2ARdY46Q6A%3d~-1',
}

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
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMzNTU3MjAiLCJhcCI6IjExMzQ2MDE0NDMiLCJpZCI6IjVhYTk0NzE5MzVjZGE1YzgiLCJ0ciI6IjRkODNhYzFjYmI5NjNlN2E3ZTM3NzA3MDJlODljZDRjIiwidGkiOjE3OTQ4MzM5ODMwMDF9fQ==',
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
    'traceparent': '00-4d83ac1cbb963e7a7e3770702e89cd4c-5aa9471935cda5c8-01',
    'tracestate': '3355720@nr=0-1-3355720-1134601443-5aa9471935cda5c8----1794833983001',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
    'userid': 'anonymous',
    'x-maf-account': 'carrefour',
    'x-maf-env': 'prod',
    'x-maf-revamp': 'true',
    'x-maf-tenant': 'mafretail',
    'x-requested-with': 'XMLHttpRequest',
    # 'cookie': 'cart_api=v2; common.mw_sellerflex.enabled=true; __privaci_latest_published_version={"v":10,"sync":0,"kn":"","cid":0}; __privaci_cookie_consent_uuid=892b288d-b4ac-46ef-a2ce-3aba9ac8388f:4,05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consent_generated=05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consents={"ts":1793962667,"consents":{"249":1,"250":1,"251":1,"252":1},"location":"GJ#IN","lang":"en","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":false,"status":"record-consent-success","implicit_consent":false,"ct":3,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}; posInfo=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04; posInfo2=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04; emirate-code=DUBAI; selectedTabData={"selectedTabId":"80","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL","pagePath":"New_homepage_standard_June_2025","pageType":"Homepage","pageId":"4044","pageUid":"Scheduled"}; tabInfo=SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY; mafuae-preferred-delivery-area=DubaiFestivalCity-Dubai; maf-session-id=B0CEDE29-32FE-4D51-ACB8-B5E62BA13370; device-id=40ff88317e022fbb14c2dfba0ed9246f; future-express-delivery=false; gtoken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiI1MDQ4ZmMxYi1kNDAyLTQ5ZWYtOWExZC0wMWE3YWJkNzg5M2YiLCJpYXQiOjE3OTQ4MzEwNTIsImV4cCI6MTc5NDgzNDY1Mn0.g4_HIvWX7owAOWEUJJpQp_oTeWgTWnCbK6ryiVyKZZ4TMxK76-Duwlk_UgTfSY4K4rG_-l9ltgvDrpHGgNHX7a_Ywz_InmgH83FAwwkMBHpfEqQjGCht_b_Bm_dWDKlEh8BGGJZjSI2UsM86PmA2JSnucKRzEW7s_cfsc9ZulR8y6Bl1KskoZ462spYHhqzLvot9IM4gOi-1MiSF-W11NLoo1mA7wSkPd74gEz4x8vd3K6JIH5J9gPyaYncOfjoW8UIEiJH-lwO_CQHtzMgUem6RpKEODBy_6fnPEsbXYj_aGGDQUxBGEOoxUTCYqROxDAZZUwblyAaFYrku1zwYQw; guid=7e8ec713f5bcbd744b75f2ebbe042759; AKA_A2=A; bm_mi=7AB703848C73505EC34FCE01C2CBBB1B~YAAQqSTDF5IGCt2hAQAAlQpw5AHRfDBJUi/qwMu9jk9VOYu6LGEIml2lvExWOY8fgdSubEuHnjK55OvgwANJZNFlCayJgc//nvkbwYLO/9B3QYEnVvA1BA/wRWUuLhNddv8xdUl1cPP8pdRm19mhYkA+tvUrjpxQnCLo+doDpAkpUTFQySNk3lfbVujeOqW9WkuXkrq6TGmyb5hJTLX+LKFKcmrOyBCOq8mUIkm4cgBK+HVWPWyR0XOA9Z7z+YgjRLtpG+VXeSC15D3YoZLTHlyVskuFEdDAmb854qY6oLoj03gK0YJSSIYmYqJMQ+dN4xVP/SDEV/ForuM6nVerdwA3hZIspdPKOVN+jgHwZpMczHTk/RWmVnN/+QaxqhyNfXaL2ygK1/g=~1; bm_sv=13AFF4F639508E572A40C9A0794B8AFC~YAAQp/naF0Ww2sihAQAAO0hw5AHcU9HGpgbL5Ia8Yjs6poXIY4eTmw6oTgreVgQX4DFRyV87mSm6SeBX0nEU8Rn3iGOR1YiOgyXVviuZZSL6eRbEsRbws9gdug8Nrh7UC2IVx41EI/LdhEllf2xfKl1yMPXIWyXTaqpwsvRtlLEFz0TTP/Rwz8eu5XvlWdZ2sVapWZSzqqeSMRtL/NkjnbkI4Iu+WcVWroWxyqyL6/U/4OCYrfbbOv+JU1K/44hbkDJ78a7jDQ==~1; ak_bmsc=7206AB253292E82CD4F4E808E83D18BB~000000000000000000000000000000~YAAQp/naF/O12sihAQAAp2Rw5AGCFdoZJsAYQfBi2ON7WH01rJ3683u5zRlRTSo/QsmV7D6EWPrFVe6ft3NsnXjgr78NpR9WK81/SZA4dlz215/QkAaF2qMQt4sxWIKuKHcOatwpcggq9k3Fku16JtcKsTx4QzBH55Vs3fJBKkPSb5endRLs4VOoe1a3eVKaB/zu7gF+AzGqZmy7log8i0bnSMDSMyfpdXjkZlLv9EvnZBxI18KySSQmI412kHAKnz4I3ddxPkCYc824Jw5RJSPVC1zotu2xpz2CNYKgYJySBPu9ZM4qsvNsR+6zCOhkkC+1f0kkAsWZh4gUNDZmug2a9vhSSwkMoKYTNC7ss5e+7RGau7EECWQu9ocIyVyn2FvczWKj4RxV0KCdfduOWa+2cRqJwjrIW9hlLh6l7OS4tEq/dWb6i0mgYV6HWszrVor298XS1ojMxIoCF+XVdFC1mA0acmZXcXhzY5733Uklzmy+2r0WCS30PVQ=; JSESSIONID=406D2D237810BA158B712E2E254EB674; storeInfo=mafuae|en|AED; bm_s=YAAQp/naF8zd2sihAQAAIBZx5AZ3IruEHqiUUqMACaR86120x8vRZKvHlzBYcSRq5458dbVTeXgss3x/bCH+VNwhHZeEh4pscEYMoELG0v/FyIOZYTVxrlvPz3JKaaavRmMpSCHyWjwZhISbAg3+zE/88vWw+NLa4CYaKYZJPE0kuOhArFj21wjaOZ9TVVEL4fqjsdyvSsA9XYMeASZM+BNZ/BK6wJljHKMPYvD1QTmh/zalVpbEN4gDlqqtS1v17RSMljYIwIoXv980DP+EmvLp6CBtIHAX4lyBRApIqbHYNv5nszxGQ1nbvCqgPFGWkZSryqrSB4YBdy7A1gFUT55LdcXJzjQqYKtwlTaGKR4Uuh/NhtX4/eHFSccN6fcPfXfHuIUY2mIkdwYjYNNGjL1jrZM0xLmF5W5b0s/3hAQimiJwK3KTi/rWiZ++p/aclsMn7lOKYVjs8f8mLV29tRm9XWHMGG2sL9oh7vM+fkzImMrErdbHY8+Yjg+CEIC3CShKGnYFyvWU6EH+5aT6rZy1djLRwV2T4hZMpyfkbKXCFzh4p9vK/L3KDTWVVtE1/IpAmoljs7aGfV8Mt9dx+8VSDzXU9J0ehbdpTe6d1zCzD5l2ah/A0YzmZjVCNSOuevJl/1ce878rFgBQ0CRt5KPQWb/Ye4JrvoKALjJhnhJddEp11fPAQst8fqPZMflBjRosDPYgPZ449LdmjaI6ZrSp9C6heT94BhwqhPSlCjRYCwUzulnGF7Sr/UW9mWrvTrTHOPpZN71NzLVG9PW0NU99DTV62PpDxecqKlEAhkOsGSyPc7WcX67STcPrzX4eJCUbSwzRbHVq5KvfJcwatgvvqH+zRe7hOvOR9fK+I+SDfh3A5+ghBjDMWO/j8JbIoRSb6Med99GeVJ9ONsMsbT5689/3bBsfj3T+honppHv0+iPrAQ36pxeqFyPzx0euWg0xpPDBKHqxaY7ZvSUyIKOGEv0dMAZ9yBRoiN8/VtfrIjWPnfobf5v3Pt73i1G5EMGh30+PP0j3A36iuxbn3JAvT/6QFoGqfXVf3cAGqHCJTTYDX9O2DYxvtQLjjpCzeIDVqw4I9y11Zm/klYIXY7r0dHR94gk89l+vd5CKcfvRDuFVNCXhxXRhmFVkB5ghlbParaTT7A==; bm_so=4BFFD3ACCCFBEC9B58718C9DAFA8050E6019A384BC1DE85E305028CB7DCDA720~YAAQp/naF87d2sihAQAAIBZx5Akgzzj4dlEEKguSQ7bl6Rsjsk7s+EjBZu9+J7875Ye1QcLSM7jhGO8ri7j6YBRrGz8m2s0A4u2e5Uw3fc6F+01u0T7J5SNcj5uFRFhyRlwT7Tn8Um7GbJ6PkoUObOsMekUtz3WkGqwMuz2LNZzCcbK2SXo4NBuqZkl1/CjnhhK9F9ONumir1URGAh1BbNtaPalOrfQafw++PT2VdvaPzU+wp5iUzh8HYAbDDoxCxZF8tIdVVoou9RJhV/DaqQ3AVGDh6fUy2BxpNRROelOIaqlro019OEj+Zm+kCdyr/hB89qecHPFVwfEd8ds7z1Hn7/3PGmZWAMyTvm+juHgsbEKGPfpea62+RwCviHf5y+nmOgIftzyVVNUzNS4ZbeHkOJ5YB9FlIA4JxxsBeR0ZZQiACfJUfDBNTnNcQHl2P+Ko1vcTVp3Z7nUCEJqLjBIIeGkXWDwxrnHGCklc5eV3~6; bm_sz=4D0C1C2A610597DB89E448A2D9658B64~YAAQp/naF8/d2sihAQAAIBZx5AGfLwfpSP8f45ecTfTzLvR4ILe08eIjn07dgjP43ZFFIYPUKB/Qu4O9TV8c+V9ut8mx/J0gROTAH6WqpGTnr7Kt/ZzZxIUnXqpuYin36tpEPoEptW6mKn8oP/u8rykFYZ0eANetUal4w+jh0F763vHojzTl4hrTmonrVM9kD42A15fEYgi4j+/tco+t3MtYb4iHrwlX7mUQc51ErPM0/D3e5VKmqo5l7BL/FUq4q5hPTpzblIei5eJjn2hbYV9CLAt+LC9lbStP1sz5qvkC1O/ymZHsLCHS9iEwZVVJjrDvp/TaGqBaYBYDC8ld9PUhYEzoniVwQ5OwqQXnMBiSY6koLVZ29G/VNuoT4YYMCrq0kD5nB5pFACpAVyKXwYChLtRpYoUh6O8MHZYWXBwXmK+bL4Gm0tFcL4fYMdAPa8Dp8h2K9O3OkYMRKrNoa85kzD17590BpkfJfnpejOzKvHaJ/ptEnIZevNHO2xlJLl/AYTdASd07dlwF299sz3+JMJmOw5h+JcFS22knlV7sTLDOHzMPz2h7fT+vAxHyFHz3OlfZy//D5sUeDsv/pxupEA==~4535365~3225396; bm_lso=4BFFD3ACCCFBEC9B58718C9DAFA8050E6019A384BC1DE85E305028CB7DCDA720~YAAQp/naF87d2sihAQAAIBZx5Akgzzj4dlEEKguSQ7bl6Rsjsk7s+EjBZu9+J7875Ye1QcLSM7jhGO8ri7j6YBRrGz8m2s0A4u2e5Uw3fc6F+01u0T7J5SNcj5uFRFhyRlwT7Tn8Um7GbJ6PkoUObOsMekUtz3WkGqwMuz2LNZzCcbK2SXo4NBuqZkl1/CjnhhK9F9ONumir1URGAh1BbNtaPalOrfQafw++PT2VdvaPzU+wp5iUzh8HYAbDDoxCxZF8tIdVVoou9RJhV/DaqQ3AVGDh6fUy2BxpNRROelOIaqlro019OEj+Zm+kCdyr/hB89qecHPFVwfEd8ds7z1Hn7/3PGmZWAMyTvm+juHgsbEKGPfpea62+RwCviHf5y+nmOgIftzyVVNUzNS4ZbeHkOJ5YB9FlIA4JxxsBeR0ZZQiACfJUfDBNTnNcQHl2P+Ko1vcTVp3Z7nUCEJqLjBIIeGkXWDwxrnHGCklc5eV3~6~1794833980834; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQp/naF9jg2sihAQAAvSVx5BDfJx4BmI+B0md0SjLwN/eTjWRJNypDqe+UC1Pl0XR1Pzrvb9EH4vZxKSFEJ4gtJpKrsiKDDhe1Ydc3BEiAlFzcGlSFNX8oTl7n/PdZQgr7QTmUttESgnsa6MAQBYgAoLLyEA6Ve65i0x95EY7/zr/SRU2hcnABcJUcTr9S4tTs6qTsDDne4DMCKtn3gGMycBTqcR3zKIlPcV8rpMKw3JdpxcMNyhGKQB/B9rMwr8sogG1z5M/O8QpKE2HSYudjpF355qeGhfUQu62JvOM3Su//UkAJGSUSwOfDSSy4/YvbDgFPwSLsnFKBmGJCwkgzmue4cZq6eTCi4h14B39+sSO2h2SK5DTmPS1ysOCewCOhynVbkkBz9SRLceuJ0J4DWI+buBfC0JqzCipKRC1y4SUB+sj0ZbmRPSRS7agX9S2qLBitLNOzIcSda8ICdV8dpXWrT0hdTS1OSga0ezGFCj1OUfJZlnFL56P13Gm1MnB32Qj2fmqeNQBmDJqH8IVAHXDJsMOCfUoQEXs+R3TVi1i0KUFFWqyN+f1RkvsFf7IYYydRcqceW3c/GEaiS71pnk7PMip7UeoMiFCewQw8zmZ2hbNSgx8zCXPBgkTogM9FHxu7Ard/I6wz/cZUAfStb+gjs0j1qhbr++9VWdmDLnMP33PuwiqXKNKmbIf8Ef5BguE9jfbZT8zRP9+DS1y/WpqpFDoTI4GJa6R0im50Z3ZmKF35vxzo63FaAfgaT6HonEMBWFyySf3mgMvapU2AGYPYBBVCtFzQJIRZesvsL34sPFakWRCxS+no3iuAl2vsQG/pQjmjKZDbTNGCIGk8POAJBuhdQ6omNvs3Kh8rgKC1Ld7YOdEIAv5TJCefIrOD3hzJctXSVq0a+e+7g4yOBShtUxaxW1V76B471LCAX5SkvE7UAy8kgj+WO3nLh5+B+qKtJtcjl9/GrMI23C6xWCVvFSriBs8RIXVJWsN+Qfz7TGdVBHBtuef1e2588R80qgwYFJuDAu6s4jdMjVTCEsvs3Iq/rlVhCpvIk5vMKopS8S/wkG3A5Iy4iORYtvqCzI/cNiR3uk2iu9CZUkFeJLp/gQ5pTUGas9AXWhCK3c12FYSIrOLoyyOt7aFtAD2uXGkQESDZ8bVJxrXCmZk7XOrvC60iryORWcbHzPK3PJ1d+tKebO21UwY=~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2fyNOo+EfY5bdWYCxZDvd0xFP99dsGyjWkcmxmG74qVjwYl+KXefWa6nioYbHB4b2BBT8eFaQXWCaiU%2fc8H45RGyFL2ulBZoNeQqxaj3RIcYydk5s0UNsfQVUmKvYspAbEFgjfz756qngSgfMtF6OzDiQ%2fCLkZUKOEsGG3B2Sroh7ehTuemZrAmkZmR7PqT661DwHCkqo2jX1XqY8lvjKpsJBkSAf9iexoxthS2ARdY46Q6A%3d~-1',
}

def get_frequantly_bounght(product_id):

  url = f"https://www.carrefouruae.com/api/v5/relevance/products/{product_id}?categoryId=Beauty%2520%2526%2520Personal%2520Care&latitude=25.2171003&longitude=55.3613635".encode()

  response = requests.request("POST", url, headers=headers, cookies=cookies, data=payload) 
  print(response.status_code)

  if response.status_code != 200:
    return {
      "message": f"not a valid response {response.status_code}",
      "text": response.text
    }
  freqantly_bought_products = []
  if "placements" in response.text:
    json_data = response.json()
    if json_data:
      products = json_data.get('placements')
      for product in products:
        if product.get('strategyMessage') in ["Frequently Bought Together", "People with similar carts also bought"]:
          recomended_products = product.get('recommendedProducts')
          for recommended_product in recomended_products:
            freqantly_bought_products.append({
              "product_name" : recommended_product.get('name'),
              "currency": recommended_product.get('price', {}).get('currency'),
              "price": recommended_product.get('price', {}).get('price'),
              "mrp": recommended_product.get('price', {}).get('basePrice', {}).get('value', 'N/A'),
              "discount": recommended_product.get('price', {}).get('loyaltyDiscount', {}).get('value', 'N/A')
            }) 
          break

  else:
    print(response.content)
  return {
    "status_code": response.status_code,
    "response": freqantly_bought_products,
    "product_id": product_id
  }

if __name__ == "__main__":
  with ThreadPoolExecutor(max_workers=1) as executor:
    futures = [
      executor.submit(get_frequantly_bounght, product.get('product_sku')) for product in products[:100]
    ]

    for future in as_completed(futures):
      result = future.result()
      response = result.get('response')
      status_code = result.get('status_code')
      if response:
        product_id = result.get('product_id')
        with CarrefourDB() as db:
          db.execute_query("UPDATE PDP set frequantly_bought_products=%s WHERE product_id=%s", (json.dumps(response, ensure_ascii=False) , product_id))
          print(f"{product_id} updated....")
      elif not response and status_code == 200:
        with CarrefourDB() as db:
          db.execute_query("UPDATE PDP set frequantly_bought_products=%s WHERE product_id=%s", ('N/A', product_id))
          print(f"{product_id} updated....")