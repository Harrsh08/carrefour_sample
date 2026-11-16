import requests
import json
from db_script import CarrefourDB
import time

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
  'longitude': '55.3613635',
  'mw_sellerflex_enabled': 'true',
  'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMzNTU3MjAiLCJhcCI6IjExMzQ2MDE0NDMiLCJpZCI6ImQ2N2E0MGE2NzNjNzgzMGEiLCJ0ciI6ImFmZThjMDk3Y2NhMGMzNjg5YzE3NGI4NjAzYWY0ZTEwIiwidGkiOjE3OTQ4MTc3NTUwNTl9fQ==',
  'origin': 'https://www.carrefouruae.com',
  'posinfo': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04',
  'posinfo2': 'nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04',
  'priority': 'u=1, i',
  'producttype': 'ANY',
  'referer': 'https://www.carrefouruae.com/mafuae/en/nail-polish-removers/broadway-n-pol-remov-s-berry-36b/p/1357771?offer=offer_carrefour_&sid=SLOTTED&sellerId=0000',
  'sec-ch-ua': '"Not-A.Brand";v="99", "Google Chrome";v="157", "Chromium";v="157"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'servicetypes': 'SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL',
  'storeid': 'mafuae',
  'traceparent': '00-afe8c097cca0c3689c174b8603af4e10-d67a40a673c7830a-01',
  'tracestate': '3355720@nr=0-1-3355720-1134601443-d67a40a673c7830a----1794817755059',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
  'userid': 'anonymous',
  'x-maf-account': 'carrefour',
  'x-maf-env': 'prod',
  'x-maf-revamp': 'true',
  'x-maf-tenant': 'mafretail',
  'x-requested-with': 'XMLHttpRequest',
  'Cookie': 'cart_api=v2; common.mw_sellerflex.enabled=true; __privaci_latest_published_version={"v":10,"sync":0,"kn":"","cid":0}; __privaci_cookie_consent_uuid=892b288d-b4ac-46ef-a2ce-3aba9ac8388f:4,05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consent_generated=05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consents={"ts":1793962667,"consents":{"249":1,"250":1,"251":1,"252":1},"location":"GJ#IN","lang":"en","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":false,"status":"record-consent-success","implicit_consent":false,"ct":3,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}; posInfo=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04; posInfo2=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04; emirate-code=DUBAI; selectedTabData={"selectedTabId":"80","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL","pagePath":"New_homepage_standard_June_2025","pageType":"Homepage","pageId":"4044","pageUid":"Scheduled"}; tabInfo=SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY; mafuae-preferred-delivery-area=DubaiFestivalCity-Dubai; maf-session-id=B0CEDE29-32FE-4D51-ACB8-B5E62BA13370; device-id=40ff88317e022fbb14c2dfba0ed9246f; future-express-delivery=false; bm_mi=18F2BE75BA3C6FAE1EF31EB73D47DE60~YAAQp/naF2ljfsihAQAAPwwe4wF23rYxB685tBh/Rhy4taHuzPhHy11PsKVSwzGGAeZH1vaeOH2g/x7xCff3EIHoD0XCyFKmIfSUVSC4qNSjHET68rRdvCRHN+LlEGpWlUu5r6CT8vj/wx09mJ9aBjzLJ/ZFn8w4uhZ/6HXUPf9dW5doAkgPjFxSE6iGEhbzBEsFVxvAITBlswQA3rdaPrFscTwlfsj0ASQ4RsrIAAZAVsPM/mKSLchqzq1QJnx+U3Ccss4rUg/B3s5I+StY6IZczUpNLkJ/qFWcChrCxw13TKmw1wGd2+nBQa49x3Orh30+zPyIPbYN3tRD32xGX1u9mfCBbrgT1cARxNB1tDyoEGy6XzzoAAN7B0QR410buXCfQgeWMKZkzLIgzg==~1; bm_sv=045A92DDD4FDC90388BE6AED1B49A4D1~YAAQp/naF2xjfsihAQAAPwwe4wGvgEpaAq6JcIPfpUIxr/b7MiAEqegn3ysraWUVXXWSe0xTUrzTpwKdOVjnHBJsyIjewdXN7PfVe/fg8lnklmNQejc3GgHAeov/Etap4hg/veVn6mZ0EVA2tQcnAX56CiJ6J037V3mON2Bp9FOZ3RCLTXitqCn2rxhIBWa3Ng8tLmOXx6U69WeDeQHCWMg2KpWaP46uJmJD21ZHYkVx32/8M4V0vyLLIwiF5K8Z1/emdtyO~1; ak_bmsc=D495AA7F5416EE402C66C73C7A0CD823~000000000000000000000000000000~YAAQp/naF6yKfsihAQAAlIEe4wEEdoEikCKOjB8egVhDVkLzYuXc3AW+OPLPn9USE4GYMB+MmP2sekW61mTIEJcbg+nPjyhOAAoe6G2KIIBKPqrsKaVa/F8f1L+lymvvsEp2nmDj25UqulSTmfWmzBNaBpqrK3iYh2SV+jzRminE7gqgkclgcTnvWDBXoOezS73P8UFfo3TO/ENZkKvXER9BFKc4FWiToyd8xRez2SyCvMyKGrsFueiAWrJ+qw00tAyPVjkHCZHevZnB+VY0SMBJIc+CybLcw2O06O/kE2tivve/EBEKgLYBnoXj7Es8wszSAaC+H7GNCRIv47nX/SlacJuG+lvLjqnyK/v2HJsNgDye/5XA3FQSRahYe4xesoSxLrnKV0VdGA6snXnAgSdLUpMXBQwnuO7DJHp8AY/BdevIsNcPjX8D7eVTS1OfivK9mRSP3YFr0ys92xZ96OLVJh+lB7sqDOuWRtckXm4ADwgNHho=; gtoken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiJhMmY5OGY0Zi0wYjI3LTRjZDItODM1Zi0wNDEyODVjMDBmZWMiLCJpYXQiOjE3OTQ4MTYxNzEsImV4cCI6MTc5NDgxOTc3MX0.nGZawmJW3VVSWTr_hlMFmCKY9ZlMO7cEd86U2_OOoHaG5CGeni0Nz3hvXoGkMV3hyJ0iaWZG7hpAtgqdoBj9QERzQ99710UNwRLHrCXiJ_GbxZJXrPsdmh_Ta3Lrgj7N1AE5iHynTUNplkwrx-sJkyaBc1As7gkYRsgJlV9Pfiegti7UH4wSMEkNrD02FtFOkJEBNrZL4pYps2ihCe0hvCDdforfXg7OYc8Dck6Wgb_TrRZhgKGauqjOb85oM31bh1aaYZkIPaK2E2VWLQqgP_3nbmw7ZSeuVT8o6nooB9F-czgdq_mB_-PCuGhs8QYVYEc0guhE4LngAk8L-5c_UA; guid=7e8ec713f5bcbd744b75f2ebbe042759; AKA_A2=A; JSESSIONID=D901A9AE0DF1F3A9B6980613821D7C4A; storeInfo=mafuae|en|AED; bm_s=YAAQp/naF7nilMihAQAAuHR54wbyZmDgp/pAaRiU0oKqMcJDyXwJQJc2JVOAFxoQLkSWZsOtLUgRxdhQKHUJ1mthxzmeE/AMR6xW4fPBKW26gl3WobOzR8zASUJ5ZJui5Qv9/OtVP8ySnrO/t1Zyo1u7flRkv5L5nTsg9jrGLPyHVs9iWBEHHW7TzpFcWY+tu1y9UXfqWhpopUYUS0P/q/IxZMqtvFf9j5ayHl+Tbi3uV2NZ7+J5gqtdpvP58qtxlIUGGWjRshGH44s/cvlouUl4eljhAqMCsdc6dPa2D0mAQdBHm6dJJjeGb1gTqz1izZiQUjkM8v2BMdfjNfgZGWpKrk9sN6jT7Qpz8FJ2DaPj3WT1kfK3nns3FQe+XIQL1d8LVxWSu8j+Dd4aMuCxYLTbRFEyFQnSEOOMnHZZKjlZx4DEdzPw5fKnfyTFqQqf1NLp6tICSEXsvSatcfH05C4B9q6Vdqj48j5+fYuQvCHNx3/+zzhfAFZvbFXGE86zrwh2OZqdLIhVoqDv4JuYXjuiIYW5gOWztF81XIFY/Prsg9X+bZiWs/2MEuDUryYmpRKok7O/JmB/iXi6U8vpusMqKVsfBCJHP+M5k9eTfQVPcisQ29khYeY9o1BkJq7MX4udibm1StnUarvmcHalQBrrqVFBQ68yiOwEirfTa2ZA3rg9ZOhrt5heA92oDEd1aHTfvQDYeoIOR1es2xkCPcmF2O6JKClCyWcSK9ul9PfsFQYFgRdL6I+oi4Xe6o+9I+wiUugBJ+XcOX9EuHqtdA2QPMD6C5QHCMQ7V2ekDBussQHFbpWJJc16EDm4LjBn6ObCl1/yKcAXbPbYvg3eCUjB+4sWIcG2m6v1002KOSyIw2NzJOIj4kRsyM0EBvE785kmsfef8Ea/bn4y9YLf/msNmcY7rmwFvVs0rjz3Br5NwuSB3WN2wSuf56gkPJ75QxDOQldoN8t7UAxM5Qpr5RvHigrBY9ivnFfBrlKNTZbjlprvcvmjpHaPR8U6bYd3v9P/jfmpxHfmBKBHZ9rIWr1J0byhVCnUV5qsuGDyC3S0maEE3zaAcJuyAYAmvO8xgF+Ge0OZGLsILvIMtcU3Rb4l6onD3YS594sJUE0p2zyiWtXARL3XYdejEZKQAn99+4XdRQmxtA==; bm_so=9BBD76E52EA2D2947CC4FFB91D23FF273B500A8137E1C24504971C1F6224EFE6~YAAQp/naF7rilMihAQAAuHR54wk4vOXh6KxslwfZnlrJXROYHLiMB02pEp3ruqOIMrz7sw7gu07dJo+KrUjh8Lpw4gZ2RRGab0DBWoBp9ExBN3WtcENJF88O1IjwRwK9lLjvP8uJ9yNGZEDH1H+fc+MsUO4jThMJgbPRevUuEYx7eaqJmrWfZpNg1Pxemx1KkHQ6AYQVNQm6iOEofkdlMp4qlBwJYyZ7v9Px70Vv3SVCF4ny8/NQmxYnQ71sYApYBMasrf4uBCRUv8VhAWD6m7JjU4TsA16DGi6qDGrvg/ung/T/aMd7AwGC18QfNY++HaGXZ27BwWEpIuAAs6DVg6B+fzKoRblfob/5y3IbAYf98m1mEGBwOhxIXO1LeiceTU0UIyVnwuffH3zHHc8A7Pp4j1NcLS3hKmdD0GZiOQB38eml2Xrkpzrk5fXO3z8U4CkpnR2Ch9xiE2i872Z/O30ae/fGJ2vHXWac0Cqff8aT~3; bm_sz=A465F5E9CAA1AAA0A9F937EF00C5166C~YAAQp/naF7vilMihAQAAuHR54wG1C8h5/HO0WfIxfw06QLI5KZSW3nEy0jUWU9diSP8c3Gho/k5Zi5TriQDuLEvqM13AvLuUVesatCBlp2dQDOB2w8cW5lHLNoK2KUNr3d7p1P6cgFLrGAaFHGSyogImvPDkxoCCrsaPCtc44UIdyued/q0MA8mCgjTpD1C0CNRqRT+V607hEd9ozHBOoj0lhhagNS1EBVKePSuke7N3fxxuwwUelBRyaMpX9K86f1D0o+Usx622O35I1RAzp7Sk/CKewRPJPgpVk7wPMR00aK6l6/gc2qq7QVLuS24ZkcORjWsMk6DIbfmLZ3laC48iEadBNkccaAPFGpsE8+VVtH3ZQCaMFrjkoJgfRD4PGen+qQMaw2W+CAgftLt1OII5F7WHCoy0XjAd7iGZ/roRK1SsqctBQCg+4o/cjT1Bq81jsx1V5T/m8d4TaA5OaZbjczvaykbUCTdpF1Qf6u3BVospxDKiaeMDeTpGBIEzJpBA9xyCpga54t/e1iUh4fodG8Onr8OVukR7VdER+rCtK13+BwYn3zCWinQbyf594db4jrf6gqORqJ8=~3356738~3228982; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~0~YAAQp/naFxHjlMihAQAAG3Z54xD1le4LADl9b9FNedNpWPxMDUSR6mjNrDy4g+awJcgQmXRDGHB8a/Za7Zzcxc4+c7l09XHyr0CHiTwsKbRfE3WKQwheZwISQLbYdcFOLjEplVII3bf4KhLZ12GrlKyGeVsJ6mwCh9PeYMM7kEcPmhb136uQdaKFEy6bRnJUH3p9SDrh7E4BwCntI6zwxi6XAyzS/hmwRqwIqBm9ngiD5jl9nFLlhd5aIq9Pc7gVLLoGvw9blGLMgYTUMxWnAevY3l3VbcSVd4a60CRVZdHpGcFdEoN9BKjvaTUYjBLFLIgnat9gTwqY+EHVr/mSHg0TPiD5r+QxL0rWz4DwUZKodj91hhxsJRKE6cLbNU8DW0lhPGo/y1K//9Zi+dryjZLvtmiNFxS1htcZH+9wRYvkixyimJJdLC7OxrMDIcg1pBjg9mvSUHQ20Iuc/uT0fUmAfy61Xg07u14SUkVlLdzFUcOhkYT9wLzRAlgdoEVwZ4gDAFH+C1s0W7BgL5FtkKql4wL+dPr5sXs15L/F3QW2V4KZX5oZqYVUhCHKXK8MuBCorDcKDCP1sFxf6lkfXNrXtSQoXE54S2V8h+0rrYRLcPfoYsWHECnew92616IhzjTxOm7cEGx+fP2OpYhP/ymuTHeAaHtUEBJtqa66TEhrM75joCc/GzDGBhsqMerNW7xxGmwNJVR/iid1erRNY/HsIdEpzHH249qpMC63ahIGVWAStsW3NpRYdthKo/vUaNiRzFVcpiWWoKQ0pfJCpu5S6TXoQ5pldNktTPDSiDLsD5uLN+BdOxyovY9aC0PNNGTMgscRa6FSrvfNlstXgX2OKWGS0OxkJmo7Jd5ewSUajRIgQve6/GhsrGsYmSXltqEkd9Ix16pVb/nqM/WpYvT6O2b4ks5tkV9U2c8LWxAnX7VcLTTeo3ywgwrDZ9Bkfbhj2Q2oaNWLnElBikhhXeoLx/BTjsyCMcQvM2ClgBbfGU5hI8JAHio5Lc9+HgcUn93GrqEN0TmnhZ+EgBbVoFnRVHO69bGgD7k35Tu/PaAAQuyRmEVmDeCyWd/Hnfv+VTGQ0+EJ/d4eCbuYIHYqv5JbOm+MHNM=~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f7hQlh66QRCAAUzzlQtjplZXQaigveKT7M6U3Q+6267iIfx72aIyDNOAD8NA+2zl+qugC5VyuK8vw01ShTracy2S3G5KUWv48ULmsEcXmuxyAq58XDCM9ByjMkLZJi+v0T02GGbt0mv%2fq151DxkMZsaf5ZXfJ7tJ9pnH9EPZZx9+TmpKCb1TPsYF32nJ5+b7Q5xY8UiU1w%2fp4foJbmbFyLz6S7pbqyEyqEW0MfwYojwC%2flU%3d~-1; bm_lso=9BBD76E52EA2D2947CC4FFB91D23FF273B500A8137E1C24504971C1F6224EFE6~YAAQp/naF7rilMihAQAAuHR54wk4vOXh6KxslwfZnlrJXROYHLiMB02pEp3ruqOIMrz7sw7gu07dJo+KrUjh8Lpw4gZ2RRGab0DBWoBp9ExBN3WtcENJF88O1IjwRwK9lLjvP8uJ9yNGZEDH1H+fc+MsUO4jThMJgbPRevUuEYx7eaqJmrWfZpNg1Pxemx1KkHQ6AYQVNQm6iOEofkdlMp4qlBwJYyZ7v9Px70Vv3SVCF4ny8/NQmxYnQ71sYApYBMasrf4uBCRUv8VhAWD6m7JjU4TsA16DGi6qDGrvg/ung/T/aMd7AwGC18QfNY++HaGXZ27BwWEpIuAAs6DVg6B+fzKoRblfob/5y3IbAYf98m1mEGBwOhxIXO1LeiceTU0UIyVnwuffH3zHHc8A7Pp4j1NcLS3hKmdD0GZiOQB38eml2Xrkpzrk5fXO3z8U4CkpnR2Ch9xiE2i872Z/O30ae/fGJ2vHXWac0Cqff8aT~3~1794817752615; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQp/naF/eLlcihAQAAsrp74xDfiqU00c5z5K1Ib9bJsxCWZeVjb9KeNBC216pwUUgxwd1FgiFxbbFg4AFs4nh2kjVHrOo2KefEC5KGWfkg2mfDEzazaN1i30jee1l5D/bJxuLdF/O57xoEERpc/b6++9Pobjdf808Ke/wo5OUR8UiDJBDlGrxW9UpfARqnoQlXC40fCC1n1b0N3xbW349Y3fd+1xj2ghu+SUUaaQdHyzFikBDBDQJYiX6tCtja1B3NIWVtHiHWHTQD35lxe+dPut+EI7xou5y9CQo7fyQ9mwfLmG/Pf+Ul3VHOkiBM+lwvDhQJX//QUwxmPxg5QB8aYCmbuxb9TjQfeUDJJDECFICVOnEyEgVRv3p/oD/tliPAY3k2AwASXF1jHNpbovC3WY2Ar3d+/ApMXVoY0Pp5a3TQgTK7rxaF74WRCwgQYAqPbbSr1MsJV2AhfNuufrDm89PYDtQsxe3YpNn8sDPJ2A6297QeeB30AN/0bRSaYWAkIFy2Jf9MWN2HmHJqg/Z2m5Wiq2F3Zhyc4Wsf6WHwGNdQnOePD/eGLRuYHEK5NusDSswgeJXOIcRYc/X38Wr9tRtJhVP8w2h0kqWgvxTfxm/yhYRAi8QaqXKCuT/hwCGVs2G5rRghHO0TL3WKFs0sLXSfMyFhWjsPBpE0kM6A0VkEoc5aYcnGlCcxD3KAuuopxKijBea88u0reu1B5p05iT5IP1gfYo3iRSHJdWX31NatQbWfXsx/nTfWkU9CV6Qk1xRQ5e4kRcV/lgzygKzJQwvIk2Rbm7EKWNKiFFZiuRqvjcK6u1N5z3gg3vYOWJ64bMlzl2RPDToRYICpkWCqpVtrnwKVxT4kOdAjvV98FoTzkJhJOeCRcsQDFF4z31vpNBZAJFebcQs8PCGpIyW7JEtaXoQ/+AX7x6DYGPI19pncIAXSxhWKwt+3BUGv7cWm2Q58okJjF9dgUrVCRB5rg0WZvIPl5L5IxdN5Qb232n0KUezwPmB90KRDr6BBV+2FfqGLPtL6Rs2WeyAwoTMm52QC51+brbxuCGkYM8pngr2DL0YdFnJBLqpFCFlpfbFaixFv8bqWXRzwyog9WpAqEsU8uI86zpKxxI3mieTRcrF/smEQLiy7zwlllLcIp8WcfNKuZJjHm3+6eI4/KwUmazCPPg0n6L06ArlQVYn039rqXuSk~0~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f7hQlh66QRCAAUzzlQtjplZXQaigveKT7M6U3Q+6267iIfx72aIyDNOAD8NA+2zl+qugC5VyuK8vw01ShTracy2S3G5KUWv48ULmsEcXmuxyAq58XDCM9ByjMkLZJi+v0T02GGbt0mv%2fq151DxkMZsaf5ZXfJ7tJ9pnH9EPZZx9+TmpKCb1TPsYF32nJ5+b7Q5xY8UiU1w%2fp4foJbmbFyLz6S7pbqyEyqEW0MfwYojwC%2flU%3d~-1; bm_s=YAAQp/naF/iLlcihAQAAs7p74waqN2+03866sdeRwgZtvFAxrZQbzGO2qm7oVeLk2FsLKrd5JjmIwKHAKcNJzrJNkTUKU/GkwY3NWWjb6Sa2rZZEInw9QEZS3y+UkCcaXkvvPyVaFavJXcg0wMiiOWmdMAMCdfDfsJSBPsmipnDXEzMOFWnqRRR7gCsfAYWraX0c28XxyGddh8FwvDRBUSpLmPMh2kQwi5EmUI0NEK7fYIbtNt3fcZUHem7lVkL7FethfFdYPXDSx/W78AnwPRUZyXMdS7Y0MSJjLw3pLDakyEy4OI+O881LJG0sS8B/Bl1AgHtYJlBwj7xA5MMnbs7huIBdlWqmuQBxtVTvLkTaklUUxbqFYeMSU2Q7jnYwimdz2Hwe7k9lq+UDQ4kT/n4E7Y7n/HFQNrZyeBD6izaMsYEo8Xz3kqBS2klfozWlkHjE757Dq6xZ7KN9g5gdz9YUXB7IUiG0/qTSsjcL0HdKWdsEml+axRPfemU1Pfim00O/vkQvmPIRueN2xUApcNb1LnQvNI36aAxJbVWXd64dcotZEYMLRlriZ9n/Bc87E3t17h5dS39aL5zp66YkZVlJt0gb3O+aDuFW0FQdoYTDlF/l2E4t7moWh7MFnLoeYfijnIEmwd+VBc8LrLFH/r2j864PzQJ/+VgxCj5DgMJ3vjP39WsIjqeCHrvCurUuHV52dyzHG0LJ1pXCbzWYUG/JYp5uo7xKT/nJoZ4Rlh5UHZE=; bm_sz=A465F5E9CAA1AAA0A9F937EF00C5166C~YAAQp/naF/mLlcihAQAAs7p74wGsYHRLbZ1R/JP6Q/Vk/SdkWUNnr2JHfJL/bJSWuEdkAyNBWYNop3smRlh6zX0yDwYIlHUpRQHbTpLEKmCPAGYzMvLVOKmMDKIqijrWb9qaMce2EORRU4/XFEtTEh8okV4rsjFXXdZtT4gk/KEX0xXU/xsVRc2u68Jp7QDoQ2pSBkvkNKyVlk7PHlyC53MYr4SNPU51YNhrcLEt+gepP7+cFLLEuupw4ECAfUy1W5n1Yu5gvG1qSRDjnJX4TWj7VqZGKlOeNCZ1eNH+f0IPPIyfl+9eocabt0qzvJmzoxG73Q/+Z+PvnJJ8hHBff7ZGZKR5CxM0zof1mRlj6Zc9Ld1UQy96cu06zNslTjBBIoUcWk2HRPBj0CN5zHR10Ys/893YaDIKyWqCYxVv+ZdFbkpkKFAZgvEu07PCfN5i89TyJy0RBUcXuQcMXrzeuwd3CzGMIDgUafTy/GNRM4k2/x/0hjmvG/UFj8bZNTEtywsmq3BYRzVgRve089B5605cb5MfbK+gJUgYgZ+ATdNWqcRCxVUFBOgkyXH8c7WXVFCBdna3Mn4I17Q=~3356738~3228982; cart_api=v2'
}

def get_offers_data(product_sku):
  payload = json.dumps({
    "screen": "PDP",
    "sku": product_sku
  })

  response = requests.request("POST", url, headers=headers, data=payload)

  if response.status_code != 200:
    return {
      "message": f"not a valid response {response.status_code}",
      "text": response.text
    }
  
  voucher_data = []
  if "componentDTO" in response.text:
    json_data = response.json()
    if json_data:
      vouchers = json_data.get('data', {}).get('componentDTO',{}).get('applicableVoucher', {}).get('vouchers', [])
      for voucher in vouchers:
        voucher_data.append({
          "title": voucher.get('title'),
          "code": voucher.get('voucherCode'),
          "term_and_condition": voucher.get('termsAndConditions', {}).get('points', [])
        })
  
    return voucher_data


if __name__ == "__main__":
  with CarrefourDB() as db:
    products = db.execute_query("select * from pdp where offers is NULL or offers = ''")
  
  for product in products:
    get_offers_data(product.get('product_id'))
    time.sleep(10)


