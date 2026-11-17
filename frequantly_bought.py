import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from db_script import CarrefourDB

with CarrefourDB() as db:
  products = db.execute_query("select * from pdp where frequantly_bought_products IS NULL or frequantly_bought_products = '' or frequantly_bought_products is NULL or product_id=2233343")

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
  'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMzNTU3MjAiLCJhcCI6IjExMzQ2MDE0NDMiLCJpZCI6IjA0ZTE3MTNiYjAzMDhmNGQiLCJ0ciI6IjU4N2FiNTdiNzM2N2VmM2VkYWRlNjUxOGY4ODkxNDM5IiwidGkiOjE3OTQ4ODE1NzM3MTR9fQ==',
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
  'traceparent': '00-587ab57b7367ef3edade6518f8891439-04e1713bb0308f4d-01',
  'tracestate': '3355720@nr=0-1-3355720-1134601443-04e1713bb0308f4d----1794881573714',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
  'userid': 'anonymous',
  'x-maf-account': 'carrefour',
  'x-maf-env': 'prod',
  'x-maf-revamp': 'true',
  'x-maf-tenant': 'mafretail',
  'x-requested-with': 'XMLHttpRequest',
  'Cookie': 'cart_api=v2; common.mw_sellerflex.enabled=true; __privaci_latest_published_version={"v":10,"sync":0,"kn":"","cid":0}; __privaci_cookie_consent_uuid=892b288d-b4ac-46ef-a2ce-3aba9ac8388f:4,05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consent_generated=05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consents={"ts":1793962667,"consents":{"249":1,"250":1,"251":1,"252":1},"location":"GJ#IN","lang":"en","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":false,"status":"record-consent-success","implicit_consent":false,"ct":3,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}; posInfo=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04; posInfo2=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04; emirate-code=DUBAI; selectedTabData={"selectedTabId":"80","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL","pagePath":"New_homepage_standard_June_2025","pageType":"Homepage","pageId":"4044","pageUid":"Scheduled"}; tabInfo=SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY; mafuae-preferred-delivery-area=DubaiFestivalCity-Dubai; maf-session-id=B0CEDE29-32FE-4D51-ACB8-B5E62BA13370; device-id=40ff88317e022fbb14c2dfba0ed9246f; future-express-delivery=false; JSESSIONID=4340FE12182BEE0830357362CCB5DD58; ak_bmsc=1C1825D4C0078D9FE1D47FEB720E44D6~000000000000000000000000000000~YAAQxPQ3F+keNMKhAQAA/klA5wH1l42bbqBvO9WI7cnnf+cNc3ohNx7s3MD2kto2WNXmUZTrkFgjpftjLfLHqWbBk+mKe77LbY6oPXM/YO1IDckPsywfb/tqcjV50Hzm4EGB1FgrAem62WuaJoKAtSlmtLVTcNq0se4itzH61cNbJ/lkH5EMQQpF0zJ/D4YuqTWR8/QZf7VrCTVni8iDPBzMJqEVkwOsfwABFnFk+o5oP2gR+N1RNy+kpoXCrknSgXSUko3+lnijrEojbh+0mu7+HsB+vfQSAFXtM38taCvgSAsCiouWC3yqnX0DfFmzhixJGL8QKtHc6v1njvIQIlQ3+h1FCfpdhz8zzQq8VsMUCCLJHIBYyPr5pRnDHrqVtP5/i2xR4TBBbodsMN5MfpDj3Cl9ZQwVpLZ5DWoLbZA=; gtoken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiJjMDBkMjRhMi04Yzc3LTRhZGYtYjQzYS1iZDkyZDZhMGRlNDAiLCJpYXQiOjE3OTQ4ODE1NjgsImV4cCI6MTc5NDg4NTE2OH0.FGEKts0_0zYWh-n9fw5785Wq5MGfY7aGO1gu6tMm7DK_gomykPH_a2lI67207WHpmJRV2KJ87PZhIjbBhEo3wrMNtaP12Nd42a2JS8XVff7vo50OeGYBL1reowm3qy51JVZza5pv1g5BwInNY4TsanKmm_jiBTtOXhUMNcoo6dzYymTcDu9iUjObPsXntFHK9agG3LMU18XVN4dyY62mWOOHC6FcxpBwjh8Mbow2Zvf09H-8kaBPctsAUxotXS_ZMCmhxrXHJliENuk5ug_pO4_VaY3mIFJqud7LcjMzhgla84OdppuAMgcKJrAouaJdrzEI6Ql39s6Myftl4s8x3A; guid=7e8ec713f5bcbd744b75f2ebbe042759; storeInfo=mafuae|en|AED; AKA_A2=A; bm_mi=D899BF440A71E8F73F5BA978FDDAE050~YAAQxPQ3F9YxNMKhAQAALUJH5wFNeeHW34/DbVSFTcg+mG/c7WpO6aeQ+H30pBLQdeqt2na9inl83FESX/4hkjKh+di1hk8gW0Edmf6ynHUhBr/m2HzHHddUcuxUCAt8wLNYXNhuMk+xTfT+M+lxhPdC+vzi/yy6leJ6R4JJXoUUy/mwWBuZxiyE7KFGbcrAcScMRhO7dju2N8DnAX2j9eSNZIWvAvtToqMYzfcN2uZjRLHebcF8sT1cyQdbkEw1N7sdUOK8e9865N0cVE+QZ8VHqM99ou0pU4HRC6tx6aYS2Oz4ZdM5bkIjxxTE66mOWATSB9YKPBkXvw9y000iM+6PtamA0Dy8SnvlkwU6uLU2KzcjxxYp9yg8fNZQu9H5d7YyFY1QzW0=~1; bm_s=YAAQxPQ3F9cxNMKhAQAALUJH5waAZdw+vW6zODxjKSjLuaEu1iXLy8qgwV0JHwKG3vRhlmQ8TR82NTtY0i7l53XhCLxw81Qy6s3rM7s956XYIQn3c008/O94Cqpf8Mn7TRLeegsOV+oeDHxkTdVUflHVjyu6Tq0bFS/sZQ9hlEJY9AhlM7BltDbY1daD0hoSrEppJ0ThFKD2ITDLwQG0HKUMNZMCeX8AbFg6PvN23zsap/McgfEcfe8lZd+0u5SvPFpXeV4Bnrqq4yR1STAhiILUONJHYQp1LqZSxcUGz/2rPFAc3SgJWbbtpF9TFXsBZwsLwAkg1tQkSZpLuv/c6mBxMsQkUXqbkItzEf7arETtt+u1mOu4SEwKahEuGa12JqDwQP9AV1oaNCKM6BLQkB9dIzQkDjsqNVHw53udyWa9p0JM99hciKToAoceeYT/lqGk75LS9Q0OCdpT1ot3oWk0wQ8Qpc4T9EK6jFjJDhvG8UY2fLAZtDGf8WYDfap4Mb0De/qQTx9J53/2MG62zRmP/PfxmkisdSGI0mBYP7VJoFO0IXqTXMLvee4AthvIkweXU/9nDeChM0YC1KZlLBcmkMFYbUSu6RlH9MClD7OkZqQ1UiNVD/HAs2cOae+/HYfJd1+JdVvtt7K8bRVCTIafrv92GNihsQNs6At1jbUeb5ltqgpqPWkLYnKRUFM5gnue35pb0cBs3zgildTZkEy9kLLLw6pnZlV+VutkFHAgW6g2ZvoVlMw0io//vFdGiiz9mruZN0S0wV+o2Tc3AJu4zTGhm+sgKBjSjsoqZUZt+0mEkEPrCNLlYqH+2tYMSi6qEP0s6XhPezoSnUfJPurUkyEBffJMZT/T2zBb7fRTPGmi/ML/vFiUPDfxPY8B+iB/u4aVYjYH2d3pUj0ZVy+3RR5lIh7rseQD3g9HMGXsIzsdhBCpTITTHUyIyNGpnmn2xlze24wK6LCDfBVyFFuwVP+icJyJBeB88dNzF9XTeym/BqqoY9U9eudAwGzz6O52LZ77z/1JRArtTzc9vC6GG/r+/0fjQT6088CUf/BLdbNuJuKJKllmwoAyp7HdsDQ9vT4DiHLNuuLCY+aDMY9eqFtAgFbbAwgl0wGCbZNefjo3DhiqAYJIM+IE4Ib3DY+z8BC2uVb+k64340jEO3WDNEpX5h9k5DnEfIQ=; bm_so=C06D84014152625B943587F26CC3C7702DDA19074AD74384DBFE6B33B2832EE5~YAAQxPQ3F9gxNMKhAQAALUJH5wmKWQWuXt4eT4nE+eubmZUx5Uhjc5FeNu7POJ1+8owsZpfP+9A1glDRoErD0g9T5Q1NWyMRUI9qazO43/AlJu9B0q5YVdc+pK9MDO9JslL4UeMtad/1hXyIrof4EuMmXGkpr/GIgH0EiBpomunVl1kPpfPHmgc4E3v2IbI1MZ1doqUnqLE5e8bb1pQl2LnFAoxwn2IzMT7pWFt69bDT9+01EmA1BvyTtUzHt46BmIYc8nHkStPse6+doa6B1bekLJWvxgoLuVRN97KG/1fz4PWh8wEGnhd8DK0FUqbVU0bZLq/quGlZOYOIn2hItEXtOFSs12uNW1WJU/LbUsl7HmxvIj/Nm2kqlSq/kecapleFdDuWjG8vEwsLsSUkHuVIimCEGBFmH6Hj9HZdfHYR2am1lWwTofBneAtmMxxBBFpoBliZKFoW0aWe1uaFdy/2z/Hn0c1YJwNvR19avX55KhwAZQUoOlXde/WS6aS6c4Uyf0JRk7iD~8; bm_sv=7987F3B6EB71A8CEFC6380020B8B9BCC~YAAQxPQ3F9kxNMKhAQAALUJH5wFUy5NeqGXvnv6aK+/Q/k3jmpuPmadlZEWCwG8dZX4L6Zo4Of04vC6EWox5cl5KCAyNqi/j5YvgkITPQYgAT+Oa8hI06lu5bctyR6Q5a422cjm1pvZpqV21wSqYKhczh37Yx3WbgjebzTsiFR96G/8ygCwFENZBF9fIPHYJ/w2l+It64Cv5dWgiugic4aLoESKSYjTQYifL5mRs0yJKf8y3jnhj4bj4mY0nvqB8QLVFSioi~1; bm_sz=FDBF0A048B22C74CE3F723862774240B~YAAQxPQ3F9oxNMKhAQAALUJH5wHCJQ0LQLAZNrUIhsZYX0TZFiyJy69RFT8+Dz060X1iWXuuFIqdUw2Ga8n14aFZoWG/QxTAkDoT38GjYffDbyLKPYe4wFlPY4tQI9rc39yVMDeoBTiDufFFMXl58uN28fS27KUZhp4cSHXc3WfBBHObqrcezTEnop0IpjlLsHzLttVlJRxeMLZ7QP3Sm4v2FlWnRyA33fuD8cxnE8u6Yb3550kAtP3kHS+AZGPNb4Wo9QyzZ3WxPvdFuYMV4GoAJ4++f6umPvdd31mE43HjgPkfAlfAjbfgPk3LWVmLcYzeqgdOVhLwULJ41bMfZJSyu93MAPyuYCfNtGAg64hnZax6jWrZP72PIdS72jGNe+3Ql4QothTpzW4PYOOP/Ffq/TIDZwh1Qt0V8+LLGMs17emuKwqs9vcZ9MBbsXwq~3616836~3228740; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~0~YAAQxPQ3F+AxNMKhAQAA10RH5xDzqkDfgh5GySVjiDZ67Nj70zrLRCadOa3hqsgZJ1aDcMXl7RmXwAuY19K6I1/0EDWT6XM0hIs7jUZTGv3Y+kkcUtLfZe13Bx12uKVLITKmIpM8Hjzhu954cZVlZJUmW+WKyI1AaK3HTQg+iBNDLBD0FLDmVsH37bkiBJFrernK+ABMNvWrYgWwcvFGf0eNT755BWIvH4El7xOl+EdrqlAq20fydi+Hipl1yOvnMRTzO6Ey5UQyLObJ/lUtmdq/KasDoHP6Q+JyulDXKoRJmwcx0qJFz8j6JWucA8IJOxEo0/xIW/bLT3XfJ3yXHGWc56FYclO3KbLaoy3BLPAdQKNWvJ1OSREMA2q7xoDztjCodFZFqvfVNN0OK7sqwSsWTaa3VuTeybZChvcU2MEixhOFf13QC5bikXEPlLsBwgjvIE2jmXIShfifLEiIJFg3vplUZJ7doNaF9U+NiPYan5V3v6cLesyr0yD3SvUV10gqlAFpH3xyRMbwqah1GjBTU2VrI2qHy+fgfTkAle8Ihbyu/P+3uPG6qZxA/6WV+X9QppiAspw18aeelaSrWuLaP5VXk1OfQQXt/hTZQQ35W2gvteb8EaLTqynyQKOUpPSYw4Ms/NlmMFSN7nnzUaV1BbDy2YTjDtogFq0PaM/QFQS5IvdoekSTt+2al4QEJDBRtiCax7FesEAjBUragy0KRHn4fhbK139bKVSZc76CAKLXuDykSd+t9dWk4+hX+LS7dGIyW9oHOGLs5EvF8yvVb33eK9rc5vwaqQ97pHZjKWN9KgntMzN7Xlkw/jZYKsSEYZ+nbyZAW/m3QJd4zsGcs0GNKM+heETvPgd2K7jW8an0dvF2d0x+4cMdNea6f/m82i4V17GTepFshBQOAygzfBNmTfves9Bp9lUTRbsw0j33bd2bufLCSvyrWExSCbu+eSho1FPx72jJxgdVGuo=~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f9339eW+eM2gLRW0iDk4PiPDNtGLTSPXQAPTEpXgoxnz5t4h2Y5TBdQKaSDPLtVnoBUEE0S4bI63mQgBHYgE4nECd5vw3TAcEDkJ~-1; bm_lso=C06D84014152625B943587F26CC3C7702DDA19074AD74384DBFE6B33B2832EE5~YAAQxPQ3F9gxNMKhAQAALUJH5wmKWQWuXt4eT4nE+eubmZUx5Uhjc5FeNu7POJ1+8owsZpfP+9A1glDRoErD0g9T5Q1NWyMRUI9qazO43/AlJu9B0q5YVdc+pK9MDO9JslL4UeMtad/1hXyIrof4EuMmXGkpr/GIgH0EiBpomunVl1kPpfPHmgc4E3v2IbI1MZ1doqUnqLE5e8bb1pQl2LnFAoxwn2IzMT7pWFt69bDT9+01EmA1BvyTtUzHt46BmIYc8nHkStPse6+doa6B1bekLJWvxgoLuVRN97KG/1fz4PWh8wEGnhd8DK0FUqbVU0bZLq/quGlZOYOIn2hItEXtOFSs12uNW1WJU/LbUsl7HmxvIj/Nm2kqlSq/kecapleFdDuWjG8vEwsLsSUkHuVIimCEGBFmH6Hj9HZdfHYR2am1lWwTofBneAtmMxxBBFpoBliZKFoW0aWe1uaFdy/2z/Hn0c1YJwNvR19avX55KhwAZQUoOlXde/WS6aS6c4Uyf0JRk7iD~8~1794881572185'
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