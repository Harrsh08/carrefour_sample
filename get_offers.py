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
  'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMzNTU3MjAiLCJhcCI6IjExMzQ2MDE0NDMiLCJpZCI6IjFhZGQyMmE0ZWNjOGFkZDIiLCJ0ciI6ImEwMWRlYTNjOWUyOGU5MGVmYjVkY2I2NTBmNzM4NTA2IiwidGkiOjE3OTQ5MTE1NDE4NTR9fQ==',
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
  'traceparent': '00-a01dea3c9e28e90efb5dcb650f738506-1add22a4ecc8add2-01',
  'tracestate': '3355720@nr=0-1-3355720-1134601443-1add22a4ecc8add2----1794911541854',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36',
  'userid': 'anonymous',
  'x-maf-account': 'carrefour',
  'x-maf-env': 'prod',
  'x-maf-revamp': 'true',
  'x-maf-tenant': 'mafretail',
  'x-requested-with': 'XMLHttpRequest',
  'Cookie': 'cart_api=v2; common.mw_sellerflex.enabled=true; __privaci_latest_published_version={"v":10,"sync":0,"kn":"","cid":0}; __privaci_cookie_consent_uuid=892b288d-b4ac-46ef-a2ce-3aba9ac8388f:4,05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consent_generated=05923948-9e4d-4706-8a48-e390632c991d:4; __privaci_cookie_consents={"ts":1793962667,"consents":{"249":1,"250":1,"251":1,"252":1},"location":"GJ#IN","lang":"en","gpcInBrowserOnConsent":false,"gpcStatusInPortalOnConsent":false,"status":"record-consent-success","implicit_consent":false,"ct":3,"gcm":{"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1}}; posInfo=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01,QMKP=F01_Zone04; posInfo2=nonfood=099_Zone01,BULK=072_Zone01,food=072_Zone01,QCOMM=072_Zone01,express=003_Zone01,QELEC=003_Zone01,QMKP=F04_Zone01|F01_Zone04; emirate-code=DUBAI; selectedTabData={"selectedTabId":"80","productType":"ANY","serviceTypes":"SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL","pagePath":"New_homepage_standard_June_2025","pageType":"Homepage","pageId":"4044","pageUid":"Scheduled"}; tabInfo=SLOTTED|DEFAULT|MKP_GLOBAL|QMKP|QELEC|DIGITAL#ANY,EXPRESS|QELEC|QMKP|DIGITAL#ANY,QCOMM|DIGITAL#ANY,BULK#ANY; mafuae-preferred-delivery-area=DubaiFestivalCity-Dubai; maf-session-id=B0CEDE29-32FE-4D51-ACB8-B5E62BA13370; device-id=40ff88317e022fbb14c2dfba0ed9246f; future-express-delivery=false; storeInfo=mafuae|en|AED; gtoken=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI1NmI4NjFjNDc1MzljZWZiNjg5NTY0YTdjYTc2NmVkIn0.eyJpc3MiOiJodHRwczovL2F1dGgtbWFuYWdlci5tYWZyc2VydmljZXMuY29tIiwic3ViIjoiZ3Vlc3R8N2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJhdWQiOiJ1cm46bWFmOnJlc291cmNlOnBsYXRmb3JtIiwidWlkIjoiN2U4ZWM3MTNmNWJjYmQ3NDRiNzVmMmViYmUwNDI3NTkiLCJqdGkiOiIzMWFhMWM0NS1hZWMwLTQ3ZWMtYTE1Ny03NGQ3OWExOGEwMjYiLCJpYXQiOjE3OTQ5MTExOTksImV4cCI6MTc5NDkxNDc5OX0.BusLXbbBpaIKAtO2sPrS9yfN5adYE57Dxee5ibTt0MtOM0pJ8CtXLMkG5TH_DgmK8O6XboiuLfX45Z41HsCcSOgJojfgvPaWli0BvfdVqeH7SPSmgdlV_RCzHdhrg83F6bQWwPkG3DMhCRNtxbetOlEW-Jq8cVwXXdHYIOjjI6r1j9nidS210wnkJ7BoBEDtde-Zj_MCSBWVUvY5E7wmwbvjpIpYwXqaU6Icboz6voO0QpIiihfx9ykr-cKJXFCWAGMediaCwPOuhfq7ohLhowqcv0FZcFofMi0rqKoNUUQfgECpGwgw_iCDKQTPHjZTUOuN1GKWtGbaEml21ccbGA; guid=7e8ec713f5bcbd744b75f2ebbe042759; ak_bmsc=F832036561F1630B83F461B7E2BC9197~000000000000000000000000000000~YAAQDTZ8aLd/xdKhAQAAI1MQ6QG7TSHtcqbojbdHfzaw/6H2EllCiboa4wSdSeGzRW37LV2qoNeZOM9mzV4wAs/ln/Svwt+7Bbnh298UYtvDPocoJ7nnxOCONXWIR+/o3zirs8YcT67ew5bkoaY8O/WuupqAExkg/ICbfveYwob5Sgqch2DSewCMNh6p0KZ1WglHg0MRAdXRxT2QIkHy6OfF+ui8k+zICmxu6SNkQclSOTCB3A5BWdP3fWQkauYCYYCqelsGYvAvsALGeerl9vYy4gwOh10estTg+vt5qGQBJg0mHmX9s86TSzLsIPBDf2JgdLrCFX6/i8r3hg6xxsPHoLSS6FzUNSOJGUODMxxv2Ik8zrwG5pzbor/mzIYnTZ8kChAhClhXpbiYjQNFDcDe; bm_mi=27115C3F87021E3955F446F679D0921E~YAAQDTZ8aD2AxdKhAQAA21sQ6QHKoRRYXWOonUUvPV6ZmIcYVJ9ZJdTmrI261ZWX+2orsiNt4+qV22Wi1vDVah3C13NKBgvDR1Yc8xov+Jw4+257WwZNLtIUx8YwpfZPCuvfse3p1YEplcByV1UMEaUmkPbn1WQjSj+8K4mhcP8SOByxgmAG3mofZ1fg7auMiwfuPbLOfDwfn02KIGuGAA2erRaqxeqU9c7yptJNDLWZlS8tuZecoSmxYOfczGRBEHLq+jJn/gBJqV4WalyN+GNp0Ni2AFTN7tOsOAzKGq4oSP1TSRiW9I+8lkznZqrbzJX5yL1sOhN1lT3jwiMau2zgAIirwHiAWfld95RZzTHbCHh+kpdAflete8xB8WuSoBVtFZkQJYw7L6SgPkh3Z01qbiD0SsSoVYB/XDh3TpjKkBspAC5BjRd87MEO+bEu/SER41LS~1; AKA_A2=A; bm_so=2459CAE025EB3EF0C6BFDEC66DDF9836A900D47FEE7E9CF726C05DF09B5C8A5C~YAAQDTZ8aGyBxdKhAQAAHnEQ6QnMoTaS1QNOk1FNiBDF+pUMQwDARFWRq2Bt7JwvBBies5NqvsfDR91EdDLgS+6jFmlgFSCMcTcMKlWmRvvJnR4swR1Ftf6pDWJES0ACReoaC2HtqDLz1COhEjcrDGKnBkQm9l+wAcSfCzn8JelfdsbKqHr+uSMg9c8tNlrPzxRu+HDsnizuKlho+qCKDQe9tzn0oPbdXoaki0NU21E8HElCnSo+XmdtT5DHYh44P2gzdsz3p1+RP9JIsbWEGNq48FDYEEVTYkrCmS46HfZZ2vsoNx5NTpQDziA277ufwfPhTUNsX1QERGg7muYCHcto0MEbcAeVLiH1EVDQok6FbwthVnqfmLhHN0p/PcfWKLRn+lxK7/KlemmjykmqEVP35vB5NGL2bGzaTxRaAUl9OiJjubFOETEq8y9Z5Y5nwdpDfiVlng5eW4f0Gfmbsu8h1BHB8omOSxCz9pS7sUAE~3; bm_lso=2459CAE025EB3EF0C6BFDEC66DDF9836A900D47FEE7E9CF726C05DF09B5C8A5C~YAAQDTZ8aGyBxdKhAQAAHnEQ6QnMoTaS1QNOk1FNiBDF+pUMQwDARFWRq2Bt7JwvBBies5NqvsfDR91EdDLgS+6jFmlgFSCMcTcMKlWmRvvJnR4swR1Ftf6pDWJES0ACReoaC2HtqDLz1COhEjcrDGKnBkQm9l+wAcSfCzn8JelfdsbKqHr+uSMg9c8tNlrPzxRu+HDsnizuKlho+qCKDQe9tzn0oPbdXoaki0NU21E8HElCnSo+XmdtT5DHYh44P2gzdsz3p1+RP9JIsbWEGNq48FDYEEVTYkrCmS46HfZZ2vsoNx5NTpQDziA277ufwfPhTUNsX1QERGg7muYCHcto0MEbcAeVLiH1EVDQok6FbwthVnqfmLhHN0p/PcfWKLRn+lxK7/KlemmjykmqEVP35vB5NGL2bGzaTxRaAUl9OiJjubFOETEq8y9Z5Y5nwdpDfiVlng5eW4f0Gfmbsu8h1BHB8omOSxCz9pS7sUAE~3~1794911533261; JSESSIONID=957F0FBBA247FE473B545389C9CA1978; bm_s=YAAQDTZ8aEqDxdKhAQAAsosQ6QZoejA9tDwhCpn+5nCHSpZSsNkRv+XRbc5Y8hgVgTklLQvL5+CCflnWTtA20siGADQGmS+ADGwgQ5W5PAcpmeKaxfCipXWORd53KXL0X5P+IgpLtnnUfa0tAKHXw25PiqxDLA4vKfZybBSHEUES7CgPDuDkPSTf5MHyjLGPLhSLgSHTMefhXdGPS1r8Hb5l6adqMgRRYgu4OD6H1OncRERedabIHs8DA+hbDmYuwoo48OdwtCi+PzEmVqRm3awQ2cbBqKx1e6mQN5wBuK8YNt2hIdv3JkvAQKSteem9mrU8qCLD5lOaybeERzi2CRr8uOtbd3VJqcRIm9M89prG7uySriF32APUt5id71EyPXYbWF735mtKz0iy1Q7UqfoohODJZ8oL2ga9PFTANCci3j7RuPAZ8hTO0Mn9nsCQ6jwe8u0nmbNOhsON8En5DExgg450l7LZp2buIIGpn1THFlVE3Vt1Tul0+nHF71/QV50rGn5DcJBpxhYmovvftOpiJfWJtX3CcQ/HjJISoIiQ2a+g3OY0pE57pExZNdvHT0AWlrIes/t+aF0BpixJgvxrLBqPm4legV2ZeDEME3bDX3YRAvpLR3Oer/2N0/DyiYLSpLdpbH1XFQnrz4K0GXuZ5kL4kgbOrYvNuqscmxJlpkFSZj+G9sgU34iYyalJozspAHqoOD0d8O0GWLMMZgLz1couHrRj1GEe0QbTYIgaWbJ+hcPQTet2y3OnEH0Ucxc2aZ7OqHHKOvOn5Lr0MgOjkR6shyZgOxHpaF/thxLNckCDkVw+53OSzjR1bqJGGYEhS7zsGlcUjopv+2MsdbRdgc59IvPY4FN9g3fVzRGf+uHPnLqhh1QrpN68P3aQHy8xbefg4xbYet5TX9h0bzVOd1JTFQUwJNJ9+Di/2hC5yTaXLrBDt3SY5sJ5TaRNv8oQDU+3Qw1+B0vezeBKMBb64s+Wd8JCVmYz6sQH8oZ93s34mPJ2anmbsWOwDbFmRUYRAUIxpYbxNGENlo8xaH8DgdNNJUSCVLwTx+sGhh2N5LYySl6BHqIGutqgmzVaDU6oCgdZy0XufWO8Gb7g4bIRMyWL7yJbHFa4n3V8LhbMmPmMlpEwEsdnXB2FYBw7pqNA9wKFR29pfyDPDw==; bm_sv=BFFFA2972690B9ACD303ED056DE00C90~YAAQDTZ8aEuDxdKhAQAAsosQ6QE86+/YL3ZX8jb5NCxIOU8Syt442aEshqtdjL4/3g95ebmpURuZtIuok9BzaoKoOhaDyadWmafIefoRVF3iRjuEbrAC1BNYkIF+shik8RD3g3XhS5Wqb3SYgNrwyd1TIsQ1GuW7NoS9nCPBxbkG5gX5PCvH/pQquR+hY3J2me/OBoH9SRCSEq8M3IkRdVrS2/yw2YvxrPXcyN3cHYg/xQ30kIorDnigk+Ad5dJ71r7TEja03A==~1; bm_sz=6F1E9D9A55374D931222DFD3FB8FF816~YAAQDTZ8aEyDxdKhAQAAsosQ6QGW+eq/Jt+CMH2dDM/OFav0fionv1LRsDc37flwHPzMMKaKK4hH1hvtIC04p6/TrX18901G3ZE6WqaS653/2ZK5F1jq5AHmNV+GcdLhK68RxjHOzg98HMG0J0xT8R/j0eX3TkdmSO47Y2Zyg9jC7UZY1agpkcWWJX77omQ69OTCA1kFND+B6w1j+mS6SGeSDDaAT1j+IPFMzvOamUEoU/6bstx9qFpkQC64nVMuhSW48jRoR1x0wLVPNs9O/FhvnbqwwXqlvoNrqCwDhAOYo3p/72TlS+FbyAmAGH/cJxiTVYux55w3wJgxOBvsvuYsN5LBjrphs+l5sXZ7OjJ2P+9qfTMzpaXshwVakdG4XJwkPuCVeeVhdSU83YeSSedkYXLsiTPmq2Xyc4Blv941sI6aYBM3boLpIiq7+CLAymcsEwnToLwaUgE5Tfxw2zyi+cHnbVfy/3TbowltE2LfBScZ4p//6Kk0IDYpNcdvpXm7H6nA/RD1ePKsm7WG9h8teJXOImPEYTQ49tuZKzxYQGWaxgzBdxYLdRR9MQHZMGhdELI=~3229236~3225668; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQDTZ8aBaExdKhAQAA8pkQ6RCY1tXuYfdNq96lEFvmwTg9tESl3kkCqFtOxf7bRlm2DVcEYTvFqK0Zm6W9V2MeDCQRr3bbIoV1JWaBYbAIQQ+3MAzFpvUgswpod3xF44ahkSE2eA53M5WBALL+p4xOzBJ4xplbvDbdClg+GkoGdHl5egDDe6NNZWPa6N94T0HlliUcAGuu17K91ToGoWnsV4voYyVS2SGEcS960GD6XvAeWFZX5DPgxnGdKDxz3gHl3I45j3Ae4/hhVpneM5FR5/YT2pcYUvvCsC20ova+tPPGA9GThelqnUwwJ/wvw/5Ik6CStumgP1co7WgFNJ1+9BzUBnWXVB+YS4t8dT2YqOlYer1punuXzEgyAoGF1CLsMlsIMAhgzHLb3aLz+qirT28CJG2SWan4YpdePKqsVclxn0KTVfzPNsBfOFOXFuzhAkmvBSyVNnwRHM4e6pOiNV0h1qhGyhyfK37UIriRrs0XUEly47346XoHTuUHrJ9JLscfalY6B66Txr+gK/B47nm3Gn4aWZsqJb2au7aQep36xG0FVKIs98CajdY/rmmCgm5FQUxSJ4og3yr4qUgdgLC6f4qaIuyiRi9UAjWrFu+bptq+EojKFkYp4rBG10EPNswsLMT8KeJsiDxDNM65dCD7XXhplE0mGkEAKhRQsd15E5+F2hseac7GRyLoQXXeNMZaG3/H0tUWiv1fcGgMug1wj16Kz50qLEnnSC2SvQ6Whc/mkhkS0yXUVMQEWaAga2PFc0aYBw6ftOz/UbYPmNG0QX7X34t6l9qnbXQrTbyP25alYAPy9h3zKyVyang2v/s3k+vkvcF7ZTQf+LhtO9a7gcljj4rdnVSuJ6UmeOrVEh8sefAv77Vt2i/mVLKJIlUKfwQtsbI7MMlRPdLqC5Itud97uZxGMneZ4tvrD2jDFRS7qAiRFhnHNzNH06EU+zVn/vAZ6e3MkAtve5cc5K/dgra1qfwlWM9bj/LF/CUlshXobqZIRJHLKVbpe+rs76cHmvRgyjq9BsvYpLrDCaKGhj72kz9s7ci5h4GN0UpPTFQwN3eHSfeY5SGEx6uBTBA/hG+qJQnNsd/g6TIUrqP2oF2a9HYRpjaHSKT9rGY/vj62tJ+UP88SoQMZzREOKkdnYwiy9uKAqQ==~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f5gs%2fH2ee5wk2RzQwu3ea+AODIt9owJaYoaU+kQAmyp%2fkQB+WHdT9XfhcCkWSFfzvwAO7IzyX%2fOn9Onl1mTUIXcvVhyndYPyiDalckEKxSLK9an7cSSNt41l+WyQsTBRBwbC6MY+HS%2fONNPjn5qB53zaXIDTfu46+g0zcSIwvLiVtHeL+ivRglSKPNnHJVOZU84Afimcqxkl5VsHYyZSpf3B3%2fUVDHppMDUAMKlw9j+jGfY%3d~-1; _abck=20E3EEE906C4D4CF4C197A940EF9E3DE~-1~YAAQp/naF7lhJ8qhAQAA0PQR6RBRvblKxrXbPSXNHF3aoeCyK6b5PclTWmWCG3dg9T42QoxKYhbM7TKmVWVR9IgkZopQIVZa4DSkG7D7fw+Waq3j93x6ouAel8/t/0log6viq0k0V0n0HoJGA1VGQqtPbgsvZIMxSfZj1xSfATGCRRW4HaSLvGLbs6Q1wj0bv+su5x5+50F7sfwYrlG1Ofkj2Ia7er+tgn/h7nPRSXel3j57XArpdCffVhPb5PNibBz82yOyKqOLGKexzC7QoZa47K+0HlI96IiT65LSkGAF9ZG06IAgT4ALk7ywWENDeac/0Miity5KfDvw9x0c+cgRX30gTM6U7FsR/NoP5XmN3vJblMsQ/ZpBvUUUP50LSAMjOQYN9q0re561wblq4gOF/PIocbXWloDunqzq9Z8y9GwLta68J40zis+iaqOSVM4jDRNg8CvV+DNFdlqEOAiIyNI5J0o5wS9KngB5s0sGfXg4pTd9QC5vZ0U6+MyhHRiA86BzQePsNQ52RNA9Zv2/rjEr95BjvKLqw4wbsYjixLqe868XoCffB1Bq78gEdLWhyaXgIY0QlFfUwG3Xtgyoof6isf4RPiIzGyLSpvmpmXJ9rH2BHYWq2vevNNeDgT+zcKYF+SFwyOaFAlw5P0C7oItM/AchF6OeUWxEhLHF8bA2ddYG+X/cfsOhE1nqSZccxwE3eEXDZTcVNNQ9NJ3pX+De1uzYjjjcNrk1PU6lYgEvx7y7YA+oOflKVSkQpJEhlpAATEGGjQyJHzdgXb5QXROcMCD1jQ/nUaLJThNkKRP0mHTxTUdnKRPQyOr58l1KoHIol9y+/ork8/TNwWpK5B6vfItD0JO2U2zMOKim3GEieXExH0OuuSj9S1xnFWDBKohLO+ULM9zf+QCNHlUJfsi7IVj8RfrBz0NwLxrAWeMwL7UCMW9EFrHC3BG3vbtyXU1VSqF8bYoScUQ3IkKPfpSVKsz2r4bJaVt0qdthGpsVnOvaTDMzCHXpfkH4g/WpYYdl9fjt5XXQk8FtL7PJZq5+IZ2jMMQKAGNpe4v7vIVX5Oxt64+qJ3uuE8KzPCY3PRcdLO5Goaiq8xdYEMPvo5DFRffeeFHBDMDEleb2vdP8kp/areXH4LT1XdWg/25n9B5Ndj4TXEIhdyDOCHHDCg/BmoMAby7CLXefl/Gk6JKkv9DjCjY=~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f5gs%2fH2ee5wk2RzQwu3ea+AODIt9owJaYoaU+kQAmyp%2fkQB+WHdT9XfhcCkWSFfzvwAO7IzyX%2fOn9Onl1mTUIXcvVhyndYPyiDalckEKxSLK9an7cSSNt41l+WyQsTBRBwbC6MY+HS%2fONNPjn5qB53zaXIDTfu46+g0zcSIwvLiVtHeL+ivRglSKPNnHJVOZU84Afimcqxkl5VsHYyZSpf3B3%2fUVDHppMDUAMKlw9j+jGfY%3d~-1; bm_s=YAAQp/naF7phJ8qhAQAA0PQR6QZYP/1rh3Fh89xCil+ZNqplqIkb9uZJ9du79noKTD7FYuhDhKdCP/FooK14XwBSVk9mBTgwHpB1NggahLns7DM6snPoEAqukDZLNvYwvvpl7v3NdRJyAiDQC93wfHWcK8dzb7qXaa6IkfT2ZJUMmtKXT2Z0qe7v5MC87C4GmempuNPfQh2axAkNfPd96oQbupITX23UjhP9TmnmwESOjnJ8/X98EgRt/ZMudi1DcB6StJs3v/OE88HXUy69kw7wfQRS9WIAUEU+/uoK4mqW6kITrqnDsZyjOxDjiUnqlwVcaP4nfJS5qgA1VXRZGNrgFjO1joyEUfnAOUONQmvjiRURrJaA3Zo4C9MK21B+2WUg1j9dWDs6/Jal8fm8K87jYL/QDdm7aSVKYyUFCBP3fAZ240Tml7N4G1jP1oJMinAUnhogtc3o8bufi8Cin1H7ua8aigU3lSjS2RThAE1C5QlPgJunC2yUvFLUQzWAHYGMhzXDHjW55OvZdmyUdSPhjWvgsLaW7Nc3kJhb68l9CA69FQt2JqDCMc74uxTIlfSojPOl3W6GoJKEFt2Ak/wGovFmSE33kktEf+7hshMJA2knUkvzWaOsIorO9h7aWX4DZr3kLoNhBjAKWhsHpy6uPEzjEx9uURTrJYs9aKUTlLFCY39WwOhke2hsiwc72y6b+Xnl108+ohU+va6V9pkonyJefOvSMNIc1mFdpyAMGdg=; bm_sv=BFFFA2972690B9ACD303ED056DE00C90~YAAQp/naF7thJ8qhAQAA0PQR6QFsghAwOMsC+S96RDwM+VTBsuCU9lG6jbeehk/rLxw7FlNtdhJ0pn96lj+G+bZeG5VWcxCw5lTeHthkrysmUWltuN9xkAMyOmkUa5tdTnLVkwsg1GxOjQ5AcdVC0VGko0OUKyG0lm453ZwlyeEmwWjPFFaC3Ss9nhg8Ofi3WZqjRhd6tAkOlUyPI9DzWxrbiWd2dUmvOG1T025eNRn88+uII6HqRPPXSPg5lnRRKejLRPl8sw==~1; bm_sz=6F1E9D9A55374D931222DFD3FB8FF816~YAAQp/naF7xhJ8qhAQAA0PQR6QHLxEcGMCDYe0rAKPd90vJpzX3+RLQRGQe9ms2B4Hzso6WDZthqCG0RU1MSIu52bKcs1HyUjkpZrADeJkQk4rc/K4XKaEHd+LjmA2hkx565fPkCtusl9GKsrMrNPmN0XjkNf8UcVYjqdF/eM1qwmqdqMh7SEoBATLLcL+P0tvz70vBwoYkU72GqoHWtynpfCcTz6AQtUbXHnR4bR0+DLsKWcmBaPZpO5HQtRICoNorouo+E2ElCwAAslQRTWIXpfhNobTOmiCR50Mezh9qqkksTNu+SnJI6iRmGIp9tkbHXlsWtOTn3uobtnvWRZgq7FC0Mh9yWoY5vjEddZs18F9nB+X2fMmfk5GK9g8gpL8PQ9Ja9VEu8MYt4wBI52FyxMFGxMCH+937WgNDpqNda2DBOKEX4go1wndGy8Mj3bdfV4uWCE24hlWTDh8IHlEjW2pVQGXg7jOYIaX57oaygH2U0WTlZKuKL9ni0Ie2a2D6RJ8Qu4v9d7eZ/iJUPg4/eh55pqOdcF4R2vYXeDjbbwPkYZSPDZOLJT72tCSB85oxvK0c=~3229236~3225668; cart_api=v2'
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

        with open(f'./PAGESAVE/{product_id}_get_offers.json', 'w') as f:
          json.dump(json_data, f, indent=2)
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
