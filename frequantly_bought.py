import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from db_script import CarrefourDB

with CarrefourDB() as db:
  products = db.execute_query("select * from pdp where frequantly_bought_products IS NULL or frequantly_bought_products = '' or frequantly_bought_products is NULL")

payload = "{\"placements\":[{\"placement\":\"item_page.echo_seed\"},{\"placement\":\"item_page.frequently_bought_together_web\"}],\"displayCurr\":\"AED\",\"locationParams\":{\"latitude\":\"25.2171003\",\"longitude\":\"55.3613635\"},\"lang\":\"en\",\"requireSponsProducts\":false}"

PAYLOAD = {
    "placements": [
        {"placement": "item_page.echo_seed"},
        {"placement": "item_page.frequently_bought_together_web"},
    ],
    "displayCurr": "AED",
    "locationParams": {"latitude": "25.2171003", "longitude": "55.3613635"},
    "lang": "en",
    "requireSponsProducts": False,
}



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
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMzNTU3MjAiLCJhcCI6IjExMzQ2MDE0NDMiLCJpZCI6IjZkMWIwYmI4MDg3MjI4OGUiLCJ0ciI6IjRlZGJlOTEwZjFhM2I4YWQ1ODIwMGNjM2VlOGNjMTYxIiwidGkiOjE3OTQ5MTE5NDU4NDN9fQ==',
    'origin': 'https://www.carrefouruae.com',
    'posinfo': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04',
    'posinfo2': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04',
    'priority': 'u=1, i',
    'referer': 'https://www.carrefouruae.com/mafuae/en/conditioners/nizoral-shampoo-100-ml-nizoral-care-conditioner-free-200-ml/p/6291108813447',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Google Chrome";v="157", "Chromium";v="157"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'servicetypes': 'SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL',
    'storeid': 'mafuae',
    'traceparent': '00-4edbe910f1a3b8ad58200cc3ee8cc161-6d1b0bb80872288e-01',
    'tracestate': '3355720@nr=0-1-3355720-1134601443-6d1b0bb80872288e----1794911945843',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
    'userid': 'anonymous',
    'x-maf-account': 'carrefour',
    'x-maf-env': 'prod',
    'x-maf-revamp': 'true',
    'x-maf-tenant': 'mafretail',
    'x-requested-with': 'XMLHttpRequest',
    'cookie': 'cart_api=v2; common.mw_sellerflex.enabled=true; __privaci_latest_published_version={"v":10,"sync":0,"kn":"","cid":0}; __privaci_cookie_consent_uuid=892b288d-b4ac-46ef-a2ce-3aba9ac8388f:4,05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consent_generated=05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consents={"ts":1793962667,"consents":{"249":1,"250":1,"251":1,"252":1},"location":"GJ#IN","lang":"en","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":false,"status":"record-consent-success","implicit_consent":false,"ct":3,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}; posInfo=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04; posInfo2=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04; emirate-code=DUBAI; selectedTabData={"selectedTabId":"80","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL","pagePath":"New_homepage_standard_June_2025","pageType":"Homepage","pageId":"4044","pageUid":"Scheduled"}; tabInfo=SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY; mafuae-preferred-delivery-area=DubaiFestivalCity-Dubai; maf-session-id=B0CEDE29-32FE-4D51-ACB8-B5E62BA13370; device-id=40ff88317e022fbb14c2dfba0ed9246f; future-express-delivery=false; storeInfo=mafuae|en|AED; gtoken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiIzMWFhMWM0NS1hZWMwLTQ3ZWMtYTE1Ny03NGQ3OWExOGEwMjYiLCJpYXQiOjE3OTQ5MTExOTksImV4cCI6MTc5NDkxNDc5OX0.BusLXbbBpaIKAtO2sPrS9yfN5adYE57Dxee5ibTt0MtOM0pJ8CtXLMkG5TH_DgmK8O6XboiuLfX45Z41HsCcSOgJojfgvPaWli0BvfdVqeH7SPSmgdlV_RCzHdhrg83F6bQWwPkG3DMhCRNtxbetOlEW-Jq8cVwXXdHYIOjjI6r1j9nidS210wnkJ7BoBEDtde-Zj_MCSBWVUvY5E7wmwbvjpIpYwXqaU6Icboz6voO0QpIiihfx9ykr-cKJXFCWAGMediaCwPOuhfq7ohLhowqcv0FZcFofMi0rqKoNUUQfgECpGwgw_iCDKQTPHjZTUOuN1GKWtGbaEml21ccbGA; guid=7e8ec713f5bcbd744b75f2ebbe042759; AKA_A2=A; bm_mi=27115C3F87021E3955F446F679D0921E~YAAQp/naFy7kJ8qhAQAA3MgT6QF7xYNjfED3OMY5PBqWFt5uRnPw1sqarThOjeeZMFPkL38idkQT1kb4NN7fZwwyYbIKHSkhrE1RmxPf478vUY7GljmHKhzMxo6IyyC9tzTaVQrhYYyJFyymU1zRoI6CvPN9BaZwNd2bkNRzWYnh5KvS+bLC/nnThNFQ18MgPlr67jOP0ShJSVzl0wS1tc9t+n1vUjaqEQL+TGT56KoU2fPSbEDYdzYrtpw+n4W7cfp+/0zkvB3GzvxWbAkFsxd8/ER+a5erU1wrDe5Iw/Zwcd9Na4/JJJGf0m3k/mYpqRUx0TFz9X7dl2TlDUQxiLiqVVPVCISfRlXHJbVPCjoIFDzUGvnIMi4g0dzy5XykDR2W0S3rhWaskAc8bLuAYFM4laapDsubbFA8yIvH91qNCuauL8tm+TvFifLZBdv8x1rOyAsR~1; bm_sv=BFFFA2972690B9ACD303ED056DE00C90~YAAQp/naF5TzJ8qhAQAA1f8T6QFe7BnYri1Vl66zkUieFV/OawSFn/NHzl/y8vR6euPuiTB4v+mW6felrrIapjUzWTBGM5ILAv9fs/hAe+MgdJ5m+Z7+VMowF5xlHXl+vwIdyBtBw4imDoOx8U66eYcZeHpJfuvTDqkjLmrtSQDEYvh3ry83vA8kgoP2zQNcNQD7/oDxSXjbQ97R7XYcXBmCaoFbMBflfSb2rC3Y/pP38iZk50NiE4FyYlkkIJcN0aHN8Mur4g==~1; ak_bmsc=F832036561F1630B83F461B7E2BC9197~000000000000000000000000000000~YAAQp/naF1z4J8qhAQAA7BAU6QHRwz+8flmtXnjEMndVibdA1LG1nAp/7DWXvZ1mv7IaiHZi4470YuwfKYLPZTTNMXlBelfVyubf8pbWZWb66CZsfq3XeRY7ljC0o5DvYlgU3K8AwYTkA2vNW+u98h20sfMr4umCfOc3T5B2INDcgBcKn9igiRmENLmYDmd0VDH0Dxm9QeakRY2mMdRFgEg1UKDUqKGSm2VMgggBXF3fmZyDZp/YxeEgXbIJBKHYctS0IGDUdr1w6eSIpE2njHmV8F3ruoROsPDgyikL7cj45S/5fottXQ5KIYEe30Es2o9Sl3ahL5AQpvJRL/XadHQP9enqUV74GQqbZfo+TlybCQAIJpHtPP5kCZA41EI/TrZ8UuIg9wMHJ30YlcbJsAvmHpUyQBhtBfNS+yfqZ0kADdEhFc+3cZAeFTmcHdSbPRmabohYRnaKPmy5F0b6I8qgrtA9m7PjLJeWrk1G0B8zwQkue5is7XIExHTht/nKz3v5AO1hwv7prH7qog63BZA7je4lJntFdKcY5jEBARvOoOJr9/ic8PU=; JSESSIONID=2B57182457B6B7092AF08A32681115BC; bm_s=YAAQp/naF0PPKMqhAQAALLUW6QbsX6YaNUfQBSAIrhPUQ8A/0TyUB7zvPL0yEWzJDYdMVk0qPQmpyn43abOvpB3J5Eef4770a8OTR8Abl+8gvY5KMrClmijXHhdpxfeNEDsNFcG0DS+dsJCgTZwxwfiZEGbswy57CZ8h8cy8bcFa86zegAf3TJnSosMmtr89xgyyGdYf/8Zs1wE5L43+RPadg2lBoWY9Uga93hA8mZwM30qV8E4exoQg8sbGiuYxeY+I7fmHic7ntTHMGoVTVOaMex2u9M09ZaadRUWwpeFg8SQI+lc1NNIMo7GwXqlwMI0gxEsC+ebhIBZZTol2hNdjvNqqt7GfXfcYQ9OYepbpqNQfutv6nzDTxy/plGOap01BT/jTW7bqI4VpGeU58vSGimtN9Wj5+71RqT2fLTdPnklU9dRqMDnoqkKARY0hvc/0jsfjkRITgnMOPPzQD2A6g0fJaDz9pUiP9mH0NgUrdLwtSrDo73M1/7gBQ2QafkHtiOA7LFWecy0VJI3yUuCixoSYxkSX784PzG92sZVF1MqBTV1e7rk+274Rh9f2ofC69qatg68OFpeMXmTxns9qJiJXKnS0MsoUfIex/RcNKvh1JOUSEyPlbgHC9Zq579hmqVI9rLqgdCXUkaLcIHjVvV2z99vbL9u5cBwpucgpk4UJbBefxdN2wZSJWaT5qVZCJNl0qlAW3o0PeCd06uuzK7R50upzrwjcnJW+X8CxnhdzmlTVPL0cc9Qq9RRCNSuKr8O23XpEJNBYP31D+cH9u8qsGw4eqA5UhsUECUwwePXz8bRx3YO8VX9rDvjnXrNuR4bAVxhwEV7o2RBzHT3+6iu8B7eIVCeKgcrwh1j6WhXpNFVMRleCr6nlvG4yc+YNa7oFtPlSpL7XhPo1HVm1F1PrgvDoYpLse3g02IEim5+CHlg2ouNQseqiNl5PEPLBNr4Wn3eboKiYD0zZtFXo5sst3xqN+oYDAcyUt3At2PTbEX42w47eCFMCgz9iOQDf2aGuqZpwHcePclIopTtDGW8JEAbbC7bxbYYD6YkxrD89JjaQ//29o4htf3dxI2lrGl1vnwtvz6ktAB4mNRRZwc6OhI9b7MJ/A1RX37tjkfQz09RczaNZc7H30imOSzF7ZhpW+AAC72GDxA==; bm_so=6518F6CF3F3BBAD0A7D4B8DBEB3B98B9051199D40FA1E2D38278E87A56862E6B~YAAQp/naF0TPKMqhAQAALLUW6Qn/kRwfuD+qUv3nn/UQQfyn83ZGojlyv7abwIp0tQbIG2w4WN5ZL+1oMd3/iVmi7cMOWjzt7zKCoV8Dr8bt26lh39GqCS6KSlGLwWI1muHJHjjEWeHw/49u129rLQO8ENNblVb9tneTldq1ibkmXpt8UEL8Rx5vdElYyI3R6B11cv7uymEVEyj4f6V7m7Gm3TPUnePZIcimqFxD756EKoAlMVg4YTtMRx+PBJGaWT4a8mZfqDj3RDY17ZuEEAxJWRBhQEvCJqRBKoPDJENIKy3ml8PsNPZdWp1QIPqozAG+P7MfZdx6DyDLw2agxhloULWf2rrbSVuV+S2/7MQJ2IgmMNzZJXebwxcUvNIuNb+Uw3hsMZ2g0DMVMsIQ0n0r5g9+gVp5bfnRQNNP0Lv45T2KJczw6UQvUDF6CHl24cqmy6XgCNm7CDb/WEqLYmT9ZAQnKyrC1kWMM3TYKU5F~3; bm_sz=C20D4CC2FD31F748DE6DF595A030D557~YAAQp/naF0XPKMqhAQAALLUW6QEieNCa4UPf9dAwbgC0wvAHVZGQIlhLKgXkBwfCrYsnr6Zy4Lfe9LW+ahBwGB3pFQA5QX4uaBf/rWXaQCX0WPQ8i7N6RAPFC1Pa7Nof1KBdIDJO+rCzaJnSm2dDx+Hk8iJk15BOPZhNlnML6XAy/SuZJZ0EaRoM1qF7sEjoZgIWcnbQfuOeFv82or4JKg1YQ3YmUHBOWxgEOxYcRKnLYBovjgLWKGACfQeN3DC2cze/k2OCKi9xo/q9moldkjvG+Ly68ntH+TPEwyitCU0dnA/n/p4vYb2PYbUhxctWQYVpZGZ1FeA6fJWW6rN9AaWeq93wCwUwHNUAPZOot9JGjC0eSUvZNF03fExTR8rG9NdPRfqDkTWKrAaC8tv5xrCBlOhtD6XD38V4TEko0Txqt2ggGFiChgt89BcsAHfJEV7QxgEJQtPuTsPmmsxu/ZKasub7wnc+AkMQ1fsD5yaXM3kcJJ6d/Rflh1sLOF/L0O53OzjBEHKTA/unFNJBfV2QprWO5KrDdx+GqX11gzszY2tHnzDO4SJCRQ727z/p3yfBp0A=~3224646~3227970; bm_lso=6518F6CF3F3BBAD0A7D4B8DBEB3B98B9051199D40FA1E2D38278E87A56862E6B~YAAQp/naF0TPKMqhAQAALLUW6Qn/kRwfuD+qUv3nn/UQQfyn83ZGojlyv7abwIp0tQbIG2w4WN5ZL+1oMd3/iVmi7cMOWjzt7zKCoV8Dr8bt26lh39GqCS6KSlGLwWI1muHJHjjEWeHw/49u129rLQO8ENNblVb9tneTldq1ibkmXpt8UEL8Rx5vdElYyI3R6B11cv7uymEVEyj4f6V7m7Gm3TPUnePZIcimqFxD756EKoAlMVg4YTtMRx+PBJGaWT4a8mZfqDj3RDY17ZuEEAxJWRBhQEvCJqRBKoPDJENIKy3ml8PsNPZdWp1QIPqozAG+P7MfZdx6DyDLw2agxhloULWf2rrbSVuV+S2/7MQJ2IgmMNzZJXebwxcUvNIuNb+Uw3hsMZ2g0DMVMsIQ0n0r5g9+gVp5bfnRQNNP0Lv45T2KJczw6UQvUDF6CHl24cqmy6XgCNm7CDb/WEqLYmT9ZAQnKyrC1kWMM3TYKU5F~3~1794911943975; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQp/naF3PTKMqhAQAASMMW6RCm+Ce+0q6WO9PU2/8a7agDlDZXkFyZ8KGp0hr2d8OKd9X0wRE2kQApC35i7+dE8K6o0WwrS5YR9n5k+Eer2GPjgpbmQ/jivPUeHaPpSL/adECwTjoeIDJ1t9UHxUlftQX3hjmI4GEEJAnVd9yWk/GRKMsJnvn94sq6n6hz/f8cm0MS8yA3gXmoRtv+sUE+A9LabVZHHKTf+iVozt4GWRxjfkPmTuiSJUhfd7AyeqqOc12ZVCk00z3lKVNSdt0Wk9WD9KoFkb1onWXvxMjjjrm13iLNIUBwEuOwWhxzoKXzrlszWtORa1oFb8banlPgUILsFvWtuTlH+bQqNMAVY6dMSeNKZhYOtctn9NFMOyRG3ZivvdEJi92pCRD6FijP+2NqZNg5t/OU3NdmiGTPb6YP51SjrBtGZT80DKwZiHCD00k1h5fGSssPnz/8BwkvZYN2+yX96FY0fvknar7RBzhpYgpPz190g0Zwj7x4tbuidGYLTsIHFAb32/OhM0IkLu5X3NpKLMdQ+bDedk0gmH643QL9D2YJ7qvGzbnNnPARjDdrevHuNARNzBGpjAZZOklq1z7IQ9FeDSSiLL05pSiHsDBs2BW8bwwaAPQqEaTLLP6RmOsak5+U16pVoGO2VCln+C4VXMk/HhwRws3XEl0gI5Y1fQeq5LNTpS5P28fSzCZLvZB8o2fW+//I6i3kC+DEMm1jFyZVJakGcHj4q1lbBgKHFCt9n796FWUaUiK84hKX5K+7F6Kk1sfuTWVMvuAWAaH/8RpbzhEYmgO3406fMQ35zvMfPbjSPdkmWRcK/5//gl9dTgTf+wPiOAQedOsAo2LzAS/xvl/wFJdOVKrq84Wg4KuOe7Ga0ui4cALlpXWwzpx1fjvGFbi/AS/xuCfFJQ25GXEnh89K1sHAl3r8qZNBZIfVaGwTScMZR7klavZwI9ZuM3474fQkUCMVr6261PARm0w6K45tFqmgE2/fo6RbYNXVgPYOr2Daira+/O8RQqEWI6CCB35NqhLy00OpxQQ9AB99/w2nvrsT0YZfUbXezemvG0ZhXsg0iQ8WMK/QMGJcrk9YmDE5P+6JCcBOx0WYWZxr91Q5KBksyw/ffOWqX912ZzjmKykiWR2JBZacmQGf0wV/kA==~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f3hOq4uND7lyNgd9S1dA54iFFZ1+DSCLaaRBQuD1anWUcpziTczgDr3MqdbmROs%2fX7mOnM%2fFp06mZDowI17IIsOK6bIIcnA%2ffcWPpa1Mq%2fpOSpVM%2fA0oNP%2fdmbXLzv8jFTvKHj0wG53DMxRkTpZMm5S4WDl8DMbI6uEj5d7W5N861hT+AFhMRz4iHzAEUUr4j%2f9aWZlYQfY4PSet%2fu3l4WZCskKmXXGu2sFqAREKLpVdlcI%3d~-1',
}


def get_frequantly_bounght(product_id):
  url = f"https://www.carrefouruae.com/api/v5/relevance/products/{product_id}?categoryId=Beauty%2520%2526%2520Personal%2520Care&latitude=25.2171003&longitude=55.3613635"

  # response = requests.post(
  #    "https://api.scrape.do/",
  #       params={                       # requests URL-encodes "url" correctly
  #           "token": config('SCRAPEDO_TOKEN'),
  #           "url": url,
  #           "super": "true",
  #           "geoCode": "ae",
  #           "customHeaders": "true",   # forward my headers to Carrefour
  #       },
  #       headers=headers,
  #       data=json.dumps(PAYLOAD),
  #       timeout=120,
  # )


  try:
    response = requests.request("POST", url, headers=headers, cookies=None, data=payload) 

    print(response.status_code, "for", product_id)

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
          if product.get('strategyMessage') in ["Frequently Bought Together"]:
            recomended_products = product.get('recommendedProducts')
            for recommended_product in recomended_products:
              freqantly_bought_products.append({
                "product_name" : recommended_product.get('name'),
                "currency": recommended_product.get('price', {}).get('currency'),
                "price": recommended_product.get('price', {}).get('discount', {}).get('price') or recommended_product.get('price', {}).get('price', 'N/A'),
                "mrp": recommended_product.get('price', {}).get('price', 'N/A'),
                "discount": recommended_product.get('price', {}).get('discount', {}).get('value')
              }) 
            break
    else:
      print(response.content)
    with open(f'./PAGESAVE/{product_id}_frequantly_bought.json', 'w') as f:
      json.dump(json_data, f, indent=2)
    return {
      "status_code": response.status_code,
      "response": freqantly_bought_products,
      "product_id": product_id
    }
  except Exception as e:
    print(str(e))
  finally:
    time.sleep(10)

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=1) as executor:
      futures = [
        executor.submit(get_frequantly_bounght, product.get('product_sku')) for product in products
      ]

      for future in as_completed(futures):
        result = future.result()
        response = result.get('response')
        status_code = result.get('status_code')
        product_id = result.get('product_id')
        if response:
          with CarrefourDB() as db:
            db.execute_query("UPDATE PDP set frequantly_bought_products=%s WHERE product_id=%s", (json.dumps(response, ensure_ascii=False) , product_id))
            print(f"{product_id} updated....")
        elif not response and status_code == 200:
          with CarrefourDB() as db:
            db.execute_query("UPDATE PDP set frequantly_bought_products=%s WHERE product_id=%s", (json.dumps({}), product_id))
            print(f"{product_id} updated....")