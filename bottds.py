# bot_tds.py - Bot Telegram cho Tool Trao Đổi Sub Facebook (Vòng lặp vô hạn)
import requests, json, base64, os, uuid, re, time, threading, logging, random
from time import sleep
from random import randint
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest

# ==================== CONFIG ====================
BOT_TOKEN = "8905860512:AAE2PQERvmATR_zcrFvPEtNTSkWHISeTfH8"

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== MÀU ====================
red = "\033[1;31m"
luc = "\033[1;32m"
vang = "\033[1;33m"
trang = "\033[1;37m"
tim = "\033[1;35m"
lam = "\033[1;36m"
thanh = f'{red}[{trang}</>{red}] {trang}=>'

# ==================== HÀM PARSE PROXY ====================
def parse_proxy(proxy_str):
    if not proxy_str:
        return None
    proxy_str = proxy_str.strip()
    if proxy_str.startswith('socks5://') or proxy_str.startswith('socks5h://'):
        return {'http': proxy_str, 'https': proxy_str}
    if proxy_str.startswith('http://') or proxy_str.startswith('https://'):
        return {'http': proxy_str, 'https': proxy_str}
    parts = proxy_str.split(':')
    if len(parts) == 4:
        h, p, u, pw = parts
        return {'http': f'http://{u}:{pw}@{h}:{p}', 'https': f'http://{u}:{pw}@{h}:{p}'}
    elif len(parts) == 2:
        h, p = parts
        return {'http': f'http://{h}:{p}', 'https': f'http://{h}:{p}'}
    return None

# ==================== CLASS FACEBOOK_API ====================
class Facebook_Api(object):
    def __init__(self, cookie, proxy=None):
        try:
            self.lsd = ''
            self.fb_dtsg = ''
            self.jazoest = ''
            self.cookie = cookie
            self.actor_id = self.cookie.split('c_user=')[1].split(';')[0]
            self.proxies = parse_proxy(proxy)
            self.headers = {
                'authority': 'www.facebook.com',
                'accept': '*/*',
                'cookie': self.cookie,
                'origin': 'https://www.facebook.com',
                'referer': 'https://www.facebook.com/',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin'
            }
            url = requests.get(f'https://www.facebook.com/{self.actor_id}', headers=self.headers, proxies=self.proxies).url
            response = requests.get(url, headers=self.headers, proxies=self.proxies).text
            matches = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', response)
            if len(matches) > 0:
                self.fb_dtsg += matches[0]
                self.jazoest += re.findall(r'jazoest=(.*?)\"', response)[0]
                self.lsd += re.findall(r'\["LSD",\[\],\{"token":"(.*?)"\}', response)[0]
        except:
            pass
    
    def info(self):
        get = requests.get('https://www.facebook.com/me', headers=self.headers, proxies=self.proxies).text
        try:
            name = get.split('<title>')[1].split('</title>')[0]
            return {'success': 200, 'id': self.actor_id, 'name': name}
        except:
            return {'error': 200}
    
    def reaction(self, id, type):
        reac = {"LIKE": "1635855486666999", "LOVE": "1678524932434102", "CARE": "613557422527858", 
                "HAHA": "115940658764963", "WOW": "478547315650144", "SAD": "908563459236466", "ANGRY": "444813342392137"}
        idreac = reac.get(type)
        data = {
            'av': self.actor_id, '__usid': r'6-Tsfgotwhb2nus:Psfgosvgerpwk:0-Asfgotw11gc1if-RV=6:F=',
            '__aaid': '0', '__user': self.actor_id, '__a': '1', '__req': '2c',
            '__hs': '19896.HYP:comet_pkg.2.1..2.1', 'dpr': '1', '__ccg': 'EXCELLENT',
            '__rev': '1014402108', '__s': '5vdtpn:wbz2hc:8r67q5',
            '__hsi': '7383159623287270781',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg5S3G2O5U4e2C17xt3odE98K361twYwJyE24wJwpUe8hwaG1sw9u0LVEtwMw65xO2OU7m221Fwgo9oO0-E4a3a4oaEnxO0Bo7O2l2Utwqo31wiE567Udo5qfK0zEkxe2GewyDwkUe9obrwKxm5oe8464-5pUfEdK261eBx_wHwdG7FoarCwLyES0Io88cA0z8c84q58jyUaUcojxK2B08-269wkopg6C13whEeE4WVU-4EdrxG1fy8bUaU',
            '__csr': 'gug_2A4A8gkqTf2Ih6RFnbk9mBqaBaTs8_tntineDdSyWqiGRYCiPi_SJuLCGcHBaiQXtLpXsyjIymm8oFJswG8CSGGLzAq8AiWZ6VGDgyQiiTBKU-8GczE9USmi4A9DBABHgWEK3K9y9prxaEa9KqQV8qUlxW22u4EnznDxSewLxq3W2K16BxiE5VqwbW1dz8qwCwjoeEvwaKVU6q0yo5a2i58aE7W0CE5O0fdw1jim0dNw7ewPBG0688025ew0bki0cow3c8C05Vo0aNF40BU0rmU3LDwaO06hU06RG6U1g82Bw0Gxw6Gw',
            '__comet_req': '15', 'fb_dtsg': self.fb_dtsg, 'jazoest': self.jazoest, 'lsd': self.lsd,
            '__spin_r': '1014402108', '__spin_b': 'trunk', '__spin_t': '1719025807',
            'fb_api_caller_class': 'RelayModern', 'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
            'variables': fr'{{"input":{{"attribution_id_v2":"CometHomeRoot.react,comet.home,tap_tabbar,1719027162723,322693,4748854339,,","feedback_id":"{base64.b64encode(("feedback:"+str(id)).encode()).decode()}","feedback_reaction_id":"{idreac}","feedback_source":"NEWS_FEED","is_tracking_encrypted":true,"tracking":["AZWUDdylhKB7Q-Esd2HQq9i7j4CmKRfjJP03XBxVNfpztKO0WSnXmh5gtIcplhFxZdk33kQBTHSXLNH-zJaEXFlMxQOu_JG98LVXCvCqk1XLyQqGKuL_dCYK7qSwJmt89TDw1KPpL-BPxB9qLIil1D_4Thuoa4XMgovMVLAXncnXCsoQvAnchMg6ksQOIEX3CqRCqIIKd47O7F7PYR1TkMNbeeSccW83SEUmtuyO5Jc_wiY0ZrrPejfiJeLgtk3snxyTd-JXW1nvjBRjfbLySxmh69u-N_cuDwvqp7A1QwK5pgV49vJlHP63g4do1q6D6kQmTWtBY7iA-beU44knFS7aCLNiq1aGN9Hhg0QTIYJ9rXXEeHbUuAPSK419ieoaj4rb_4lA-Wdaz3oWiWwH0EIzGs0Zj3srHRqfR94oe4PbJ6gz5f64k0kQ2QRWReCO5kpQeiAd1f25oP9yiH_MbpTcfxMr-z83luvUWMF6K0-A-NXEuF5AiCLkWDapNyRwpuGMs8FIdUJmPXF9TGe3wslF5sZRVTKAWRdFMVAsUn-lFT8tVAZVvd4UtScTnmxc1YOArpHD-_Lzt7NDdbuPQWQohqkGVlQVLMoJNZnF_oRLL8je6-ra17lJ8inQPICnw7GP-ne_3A03eT4zA6YsxCC3eIhQK-xyodjfm1j0cMvydXhB89fjTcuz0Uoy0oPyfstl7Sm-AUoGugNch3Mz2jQAXo0E_FX4mbkMYX2WUBW2XSNxssYZYaRXC4FUIrQoVhAJbxU6lomRQIPY8aCS0Ge9iUk8nHq4YZzJgmB7VnFRUd8Oe1sSSiIUWpMNVBONuCIT9Wjipt1lxWEs4KjlHk-SRaEZc_eX4mLwS0RcycI8eXg6kzw2WOlPvGDWalTaMryy6QdJLjoqwidHO21JSbAWPqrBzQAEcoSau_UHC6soSO9UgcBQqdAKBfJbdMhBkmxSwVoxJR_puqsTfuCT6Aa_gFixolGrbgxx5h2-XAARx4SbGplK5kWMw27FpMvgpctU248HpEQ7zGJRTJylE84EWcVHMlVm0pGZb8tlrZSQQme6zxPWbzoQv3xY8CsH4UDu1gBhmWe_wL6KwZJxj3wRrlle54cqhzStoGL5JQwMGaxdwITRusdKgmwwEQJxxH63GvPwqL9oRMvIaHyGfKegOVyG2HMyxmiQmtb5EtaFd6n3JjMCBF74Kcn33TJhQ1yjHoltdO_tKqnj0nPVgRGfN-kdJA7G6HZFvz6j82WfKmzi1lgpUcoZ5T8Fwpx-yyBHV0J4sGF0qR4uBYNcTGkFtbD0tZnUxfy_POfmf8E3phVJrS__XIvnlB5c6yvyGGdYvafQkszlRrTAzDu9pH6TZo1K3Jc1a-wfPWZJ3uBJ_cku-YeTj8piEmR-cMeyWTJR7InVB2IFZx2AoyElAFbMuPVZVp64RgC3ugiyC1nY7HycH2T3POGARB6wP4RFXybScGN4OGwM8e3W2p-Za1BTR09lHRlzeukops0DSBUkhr9GrgMZaw7eAsztGlIXZ_4"],"session_id":"{str(uuid.uuid4())}","actor_id":"{self.actor_id}","client_mutation_id":"3"}},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}}',
            'server_timestamps': 'true', 'doc_id': '7047198228715224',
        }
        response = requests.post('https://www.facebook.com/api/graphql/', headers=self.headers, data=data, proxies=self.proxies)
        return '{"data":{"feedback_react":{"feedback":{"id":' in response.text
    
    def reactioncmt(self, id, type):
        reac = {"LIKE": "1635855486666999", "LOVE": "1678524932434102", "CARE": "613557422527858", 
                "HAHA": "115940658764963", "WOW": "478547315650144", "SAD": "908563459236466", "ANGRY": "444813342392137"}
        g_now = datetime.now()
        timestamp = str(datetime.strptime(g_now.strftime("%Y-%m-%d %H:%M:%S.%f"), "%Y-%m-%d %H:%M:%S.%f").timestamp()).replace('.', '')
        id_reac = reac.get(type)
        data = {
            'av': self.actor_id, '__aaid': '0', '__user': self.actor_id, '__a': '1', '__req': '1a',
            '__hs': '19906.HYP:comet_pkg.2.1..2.1', 'dpr': '1', '__ccg': 'GOOD', '__rev': '1014619389',
            '__s': 'z5ciff:vre7af:23swxc', '__hsi': '7387045920424178191',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg5S3G2O5U4e2C1vgS3q2ibwyzE2qwJyE24wJwkEkwUx60GE5O0BU2_CxS320om78-221Rwwwqo462mcwfG12wOx62G5Usw9m1YwBgK7o6C2O0B84G1hx-3m1mzXw8W58jwGzEaE5e3ym2SUbElxm3y11xfxmu3W3rwxwjFovUaU3VBwFKq2-azo2NwwwOg2cwMwhEkxebwHwNxe6Uak0zU8oC1hxB0qo4e16wWwjHDzUiwRK6E4-8wLwHw',
            '__csr': 'gJ0AH5n4n4PhcQW4Oh4JFsIH4f5ji9iWuzqSltFlETn_trnbH_YIJX9iWiAiQBpeht9uYyhrvOOaiSV9CKmriyF4EzjBGh4XRqy8O4Z4HGypAaDAG8DzE-iKii5bUGaiXyocA22iayUOUG9BKUkxe2vBBxe5898S5k48fogxqQU9oO1bwiU9FpEowOBwYwLCw86u2y0Eo885-1uwFwOwpU1jo7-0IU108iw8i0kq0bVw6gBxa4E1g83tw0_yBw2hE012EoG0uG0gh068w23Q0dlw0wKw68Aw0huU0a7VU0jkw0E-w8W0cPK6U',
            '__comet_req': '15', 'fb_dtsg': self.fb_dtsg, 'jazoest': self.jazoest, 'lsd': self.lsd,
            '__spin_r': '1014619389', '__spin_b': 'trunk', '__spin_t': '1719930656',
            'fb_api_caller_class': 'RelayModern', 'fb_api_req_friendly_name': 'CometUFIFeedbackReactMutation',
            'variables': '{"input":{"attribution_id_v2":"CometVideoHomeNewPermalinkRoot.react,comet.watch.injection,via_cold_start,1719930662698,975645,2392950137,,","feedback_id":"'+base64.b64encode(("feedback:"+str(id)).encode()).decode()+'","feedback_reaction_id":"'+id_reac+'","feedback_source":"TAHOE","is_tracking_encrypted":true,"tracking":[],"session_id":"'+str(uuid.uuid4())+'","downstream_share_session_id":"'+str(uuid.uuid4())+'","downstream_share_session_origin_uri":"https://fb.watch/t3OatrTuqv/?mibextid=Nif5oz","downstream_share_session_start_time":"'+timestamp+'","actor_id":"'+self.actor_id+'","client_mutation_id":"1"},"useDefaultActor":false,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}',
            'server_timestamps': 'true', 'doc_id': '7616998081714004',
        }
        response = requests.post('https://www.facebook.com/api/graphql/', headers=self.headers, data=data, proxies=self.proxies)
        return '{"data":{"feedback_react":{"feedback":{"id":' in response.text
    
    def share(self, id):
        data = {
            'av': self.actor_id, '__usid': r'6-Tsftw3x1vqj8dz:Psftw2g2c595x:0-Asftw3x1etit7l-RV=6:F=',
            '__aaid': '0', '__user': self.actor_id, '__a': '1', '__req': '1o',
            '__hs': '19901.HYP:comet_pkg.2.1..2.1', 'dpr': '1', '__ccg': 'EXCELLENT', '__rev': '1014511729',
            '__s': '8zktjb:5quia4:fu1x9q', '__hsi': '7384980750065440159',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg5S3G2O5U4e2C17xt3odE98K360CEboG0x8bo6u3y4o2Gwn82nwb-q7oc81xoswMwto886C11wBz83WwgEcEhwGxu782lwv89kbxS1Fwc61awkovwRwlE-U2exi4UaEW2G1jwUBwJK2W5olwUwgojUlDw-wSU8o4Wm7-2K0-poarCwLyES0Io88cA0z8c84q58jyUaUcojxK2B08-269wkopg6C13whEeE4WVU-4EdrxG1fy8bUaU',
            '__csr': 'gdk8MPs4dNYQYp4iOSD9sG2fZqN79mKHYBH4qrNP5bifl8IyAF-CDQGFdBdlTmeimHGOWJKhCKRWDLjGmV94uVpprh6FaDD_GcG5F4ECVqgCqhqRAKhd2oGAUBzaUCibGVHy9EFeayEjCxim598oxmmCETxObKuuUyfzF8411e2e7VHyq-dG8AK4oW4ogK69XzEy7U4aFQ4EdE426UKdxm7E98sG15Cw8Oi1awgUaolwvUO8wrU3ewNwt9UOvwko16o1z81uo1gA0cww1pHxGQE2Kw0sv80Ii6E03c4U9olw1N21Cw1eu05rE1oUmxiew0iIU0e5k0m-02jW1RyU2pwPw3uU0u3w4wAo0Xi0Bk',
            '__comet_req': '15', 'fb_dtsg': self.fb_dtsg, 'jazoest': self.jazoest, 'lsd': self.lsd,
            '__spin_r': '1014511729', '__spin_b': 'trunk', '__spin_t': '1719449821',
            'fb_api_caller_class': 'RelayModern', 'fb_api_req_friendly_name': 'ComposerStoryCreateMutation',
            'variables': '{"input":{"composer_entry_point":"share_modal","composer_source_surface":"feed_story","composer_type":"share","idempotence_token":"'+str(uuid.uuid4())+'_FEED","source":"WWW","attachments":[{"link":{"share_scrape_data":"{\\"share_type\\":22,\\"share_params\\":['+id+']}"}}],"reshare_original_post":"RESHARE_ORIGINAL_POST","audience":{"privacy":{"allow":[],"base_state":"EVERYONE","deny":[],"tag_expansion_state":"UNSPECIFIED"}},"is_tracking_encrypted":true,"tracking":["AZWWGipYJ1gf83pZebtJYQQ-iWKc5VZxS4JuOcGWLeB-goMh2k74R1JxqgvUTbDVNs-xTyTpCI4vQw_Y9mFCaX-tIEMg2TfN_GKk-PnqI4xMhaignTkV5113HU-3PLFG27m-EEseUfuGXrNitybNZF1fKNtPcboF6IvxizZa5CUGXNVqLISUtAWXNS9Lq-G2ECnfWPtmKGebm2-YKyfMUH1p8xKNDxOcnMmMJcBBZkUEpjVzqvUTSt52Xyp0NETTPTVW4zHpkByOboAqZj12UuYSsG3GEhafpt91ThFhs7UTtqN7F29UsSW2ikIjTgFPy8cOddclinOtUwaoMaFk2OspLF3J9cwr7wPsZ9CpQxU21mcFHxqpz7vZuGrjWqepKQhWX_ZzmHv0LR8K07ZJLu8yl51iv-Ram7er9lKfWDtQsuNeLqbzEOQo0UlRNexaV0V2m8fYke8ubw3kNeR5XsRYiyr958OFwNgZ3RNfy-mNnO9P-4TFEF12NmNNEm4N6h0_DRZ-g74n-X2nGwx9emPv4wuy9kvQGeoCqc636BfKRE-51w2GFSrHAsOUJJ1dDryxZsxQOEGep3HGrVp_rTsVv7Vk3JxKxlzqt3hnBGDgi6suTZnJw69poVOIz6TPCTthRhj7XUu4heyKBSIeHsjBRC2_s3NwuZ4kKNCQ2JkVuBXz_hsRhDmbAnBi6WUFIJhLHO_bGgKbEASuU4vtj4FNKo_G8p-J1kYmCo0Pi72Csi3EikuocfjHFwfSD3cCbetr3V8Yp6OmSGkqX63FkSqzBoAcHFeD-iyCAkn0UJGqU-0o670ZoR-twkUDcSJPXDN2NYQfqiyb9ZknZ7j04w1ZfAyaE7NCiCc-lDt1ic79XyHunjOyLStgXIW30J4OEw_hAn86LlRHbYVhi-zBBTZWWnEl9piuUz0qtnN-qEd002DjNYaMy0aDAbL9oOYDdN8mHvnXq1aKove9I4Jy0WtlxeN8279ayz7NdDZZ9LrajY_YxIJJqdZtJIuRYTunEeDsFrORpu3RYRbFwpGnQbHeSLH1YvwOyOJRXhYYmVLJEGD2N9r5wkPbgbx2HoWsGjWj_DpkEAyg59eBJy4RYPJHvOsetBQABEWmGI7nhUDYTPdhrzVxqB_g4fQ9JkPzIbEhcoEZjmspGZcR4z4JxUDJCNdAz2aK4lR4P5WTkLtj2uXMDD_nzbl8r_DMcj23bjPiSe0Fubu-VIzjwr7JgPNyQ1FYhp5u4lpqkkBkGtfyAaUjCgFhg4FW-H3d3vPVMO--GxbhK9kN0QAcOE3ZqQR2dRz6NbhcvTyNfDxy0dFTRw-f-vxn04gjJB5ZEG3WfSzQv0VbqDYm6-NFYAzIxbDLoiCu34WAa2lckx5qxncXBhQj6Fro2gXGPXo4d32DvqQg7_RHQ-SF_WLqdxRCXF91NIqxYmFZsOJAuQ5m6TafzuNnQoJB3OQFoknv8Uy5O4FKuwazh1rvLrsj-1QEMi3sTrr9KxJkZy9EKXs92ndlb3edgfycLOffTil-gW2BvxeNiMQzqF1xJqFBKHDyatgwpXDX81HDwxkuMEaGPREIeQLuOlBJrL_20RD1e4Gu4tjQD8vRsb29UNG60DqpDvc-H4Z2oxeppm0KIwQNaCTtGUxxmvT807fXMnuVEf5QI5qTx9YRJh56GiWLoHC_zPMhoikMbAybIVWh9HtVgZGgImDmz0l9P4LgtpKNnKbQj_2ZKn2ZhOYKZLdt1P2Jq2Z2z76MtbRQTrpZpFb14zWVnh1LFCSFPAB7sqC1-u-KQOf2_SjEecztPccso8xZB2nkhLetyPn9aFuO-J_LCZydQeiroXx4Z8NxhDpbLoOpw2MbRCVB_TxfnLGNn1QD0To9TTChxK5AHNRRLDaj3xK1e0jd37uSmHTkT6QJVHFHEYMVLBcuV1MQcoy0wsvc1sRb",null],"logging":{"composer_session_id":"'+str(uuid.uuid4())+'"},"navigation_data":{"attribution_id_v2":"FeedsCometRoot.react,comet.most_recent_feed,tap_bookmark,1719641912186,189404,608920319153834,,"},"event_share_metadata":{"surface":"newsfeed"},"actor_id":"'+self.actor_id+'","client_mutation_id":"3"},"feedLocation":"NEWSFEED","feedbackSource":1,"focusCommentID":null,"gridMediaWidth":null,"groupID":null,"scale":1,"privacySelectorRenderLocation":"COMET_STREAM","checkPhotosToReelsUpsellEligibility":false,"renderLocation":"homepage_stream","useDefaultActor":false,"inviteShortLinkKey":null,"isFeed":true,"isFundraiser":false,"isFunFactPost":false,"isGroup":false,"isEvent":false,"isTimeline":false,"isSocialLearning":false,"isPageNewsFeed":false,"isProfileReviews":false,"isWorkSharedDraft":false,"hashtag":null,"canUserManageOffers":false,"__relay_internal__pv__CometIsAdaptiveUFIEnabledrelayprovider":true,"__relay_internal__pv__CometUFIShareActionMigrationrelayprovider":true,"__relay_internal__pv__IncludeCommentWithAttachmentrelayprovider":true,"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false,"__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider":false,"__relay_internal__pv__IsWorkUserrelayprovider":false,"__relay_internal__pv__IsMergQAPollsrelayprovider":false,"__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider":true,"__relay_internal__pv__StoriesRingrelayprovider":false,"__relay_internal__pv__EventCometCardImage_prefetchEventImagerelayprovider":false}',
            'server_timestamps': 'true', 'doc_id': '8167261726632010'
        }
        response = requests.post("https://www.facebook.com/api/graphql/", headers=self.headers, data=data, proxies=self.proxies)
        return '"errors"' not in response.text
    
    def like_page(self, id):
        data = {
            'av': self.actor_id, '__aaid': '0', '__user': self.actor_id, '__a': '1', '__req': 'v',
            '__hs': '20038.HYP:comet_pkg.2.1..2.1', 'dpr': '1', '__ccg': 'EXCELLENT', '__rev': '1018088939',
            '__s': 'z2jloc:ulhc8m:wfcq07', '__hsi': '7435892510460455151',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg5S3G2O5U4e2CE4i5QdwSwAyUco5S3O2Saw8i2S1DwUx60GE5O0BU2_CxS320qa2OU7m221Fwgo9oO0-E4a3a4oaEnxO0Bo7O2l2Utwqo31wiE567Udo5qfK0zEkxe2GewyDwkUe9obrwh8lwUwgojUlDw-wUwxwjFovUaU3qxW2-VEbUGdG0HE88cA0z8c84q58jyUaUcojxK2B08-269wkopg6C13xe3a3Gfw-Kufxa3mUqwjVqwLwHwea',
            '__csr': 'goMkMmFYnk44OdtsAixBEr5ndERq8jiFnqsLeGayYyWJmqOH9dhJW8XiXZ5GKl2aji8WjAmG8AWlBF5hFtVppFFLhVo-rWiJ4Az-l13hGAy5-qmFGKbp4AS8BBxCWAAz8y8UjyFpAV-cAKchoC8UO2afgmx-lUF1emeCBXyo88C6U8Egz41DK262O788UOfgC3m6oS2-i48Z3E9lxu69U8e2a4o4TwhEdo6q2y1Ywk84W1lweim1jwywj8fE1r80NK053E14aS01LRwuE0d2E02Xbwlo18A0iLg0g5w1f-091w2MU0NK1-w3WE0row0AXw0sNovwOK0lq0EU0nNw208',
            '__comet_req': '15', 'fb_dtsg': self.fb_dtsg, 'jazoest': self.jazoest, 'lsd': self.lsd,
            '__spin_r': '1018088939', '__spin_b': 'trunk', '__spin_t': '1731303639',
            'fb_api_caller_class': 'RelayModern', 'fb_api_req_friendly_name': 'CometProfilePlusLikeMutation',
            'variables': '{"input":{"is_tracking_encrypted":false,"page_id":"'+str(id)+'","source":null,"tracking":null,"actor_id":"'+str(self.actor_id)+'","client_mutation_id":"1"},"scale":1}',
            'server_timestamps': 'true', 'doc_id': '6716077648448761',
        }
        response = requests.post('https://www.facebook.com/api/graphql/', headers=self.headers, data=data, proxies=self.proxies)
        return '"subscribe_status":"IS_SUBSCRIBED"' in response.text
    
    def group(self, id):
        data = {
            'av': self.actor_id, '__user': self.actor_id, '__a': '1',
            '__dyn': '7AzHJ16U9ob8ng5K8G6EjBWo2nDwAxu13wsongS3q2ibwyzE2qwJyEiwsobo6u3y4o2Gwfi0LVEtwMw65xO321Rwwwg8a8465o-cwfG12wOKdwGxu782lwv89kbxS2218wc61axe3S1lwlE-U2exi4UaEW2G1jxS6FobrwKxm5oe8464-5pUfEe88o4Wm7-8xmcwfCm2CVEbUGdG1Fwh888cA0z8c84qifxe3u364UrwFg662S26',
            '__csr': 'gadNAIYllhsKOE8IpidFPhcIx34Omy9-O9OO8hZ_8-kAymHGAybJqGlvmWl7nWBWJ7GqaXHz7GFe9oy_KBl7h6h4KVah94QeKVHACDyryqKdF5GuXXBCgNpbJ5jjGm8yQEWrCixl6xWuiih5yo-8wAy84mq4poN0Vzbxe16whAufgO5U8UKi4Eyu4EjwGK78527o8411wgocU5u1MwSwFyU8Uf8igaElw8e9xK2GewNgy5o5m1nDwLwrokm16www8G03cy0arw0Zyw0aaC0mG0eJzl8ow2Jw6tw44w4uzo045W1UgSeg0z-07X81-E0cNo0By1Wwi8fE0lYw2h81a8gw9u',
            '__req': 'k', '__hs': '19363.HYP:comet_pkg.2.1.0.2.1', 'dpr': '2', '__ccg': 'EXCELLENT',
            '__rev': '1006794317', '__s': 'gtlvj8:fxbzro:f2kk19', '__hsi': '7185658639628512803',
            '__comet_req': '15', 'fb_dtsg': self.fb_dtsg, 'jazoest': self.jazoest, 'lsd': self.lsd,
            '__aaid': '1576489885859472', '__spin_r': '1006794317', '__spin_b': 'trunk', '__spin_t': '1673041526',
            'fb_api_caller_class': 'RelayModern', 'fb_api_req_friendly_name': 'GroupCometJoinForumMutation',
            'variables': '{"feedType":"DISCUSSION","groupID":"'+id+'","imageMediaType":"image/x-auto","input":{"action_source":"GROUP_MALL","attribution_id_v2":"CometGroupDiscussionRoot.react,comet.group,via_cold_start,1673041528761,114928,2361831622,","group_id":"'+id+'","group_share_tracking_params":{"app_id":"2220391788200892","exp_id":"null","is_from_share":false},"actor_id":"'+self.actor_id+'","client_mutation_id":"1"},"inviteShortLinkKey":null,"isChainingRecommendationUnit":false,"isEntityMenu":true,"scale":2,"source":"GROUP_MALL","renderLocation":"group_mall","__relay_internal__pv__GroupsCometEntityMenuEmbeddedrelayprovider":true,"__relay_internal__pv__GlobalPanelEnabledrelayprovider":false}',
            'server_timestamps': 'true', 'doc_id': '5853134681430324',
            'fb_api_analytics_tags': '["qpl_active_flow_ids=431626709"]',
        }
        response = requests.post('https://www.facebook.com/api/graphql/', headers=self.headers, data=data, proxies=self.proxies)
        return self.actor_id in response.text
    
    def follow(self, id):
        data = {
            'av': self.actor_id, '__aaid': '0', '__user': self.actor_id, '__a': '1', '__req': '3c',
            '__hs': '19904.HYP:comet_pkg.2.1..2.1', 'dpr': '1', '__ccg': 'GOOD', '__rev': '1014584891',
            '__s': 'my2e5i:sn3f24:bhs2dd', '__hsi': '7386333891453876768',
            '__dyn': '7AzHK4HwkEng5K8G6EjBAg5S3G2O5U4e2C1vgS3q2ibwNw9G2Saw8i2S1DwUx60GE5O0BU2_CxS320om78c87m221Fwgo9oO0-E4a3a4oaEnxO0Bo7O2l2Utwqo31wiE567Udo5qfK0zEkxe2GewGwkUe9obrwKxm5oe8464-5pUfEe88o4Wm7-2K0-poarCwLyES0Io88cA0z8c84q58jyUaUcojxK2B08-269wkopg6C13whEeE4WVU-4EdrxG1fy8bUaU',
            '__csr': 'g652tR6igD6PnsllELEhOn2WthkQARshlfPvfvlRiNePOWPLRFtv8QmQV94jqQ-VfrnZmih4z9Fp8CjBgxrDL-h5ATQaKiiaBBzqytoxartorHiyAES4oly47FUCu5lDzqwFCBxa4EyiQbjJe8Uy78b8izK26m5USu9yUhwAw-xG9wpFp8G4ojwMwr8jxW10wMwYwgEO1iz85i321ZwKwVwrUuBw4Ey8owt8S12wdq0nC0drw8-3C0VUoyUK3G1Hm0oS01ZBw2Lo034MwEw8l01sZ09a1Bw1hq05SU1c8W01aSw0XMg09CU14o3tw2iob80u5w',
            '__comet_req': '15', 'fb_dtsg': self.fb_dtsg, 'jazoest': self.jazoest, 'lsd': self.lsd,
            '__spin_r': '1014584891', '__spin_b': 'trunk', '__spin_t': '1719764873',
            'fb_api_caller_class': 'RelayModern', 'fb_api_req_friendly_name': 'CometUserFollowMutation',
            'variables': '{"input":{"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,comet.profile.timeline.list,unexpected,1719765181042,489343,250100865708545,,;SearchCometGlobalSearchDefaultTabRoot.react,comet.search_results.default_tab,unexpected,1719765155735,648442,391724414624676,,;SearchCometGlobalSearchDefaultTabRoot.react,comet.search_results.default_tab,tap_search_bar,1719765153341,865155,391724414624676,,","is_tracking_encrypted":false,"subscribe_location":"PROFILE","subscribee_id":"'+str(id)+'","tracking":null,"actor_id":"'+str(self.actor_id)+'","client_mutation_id":"5"},"scale":1}',
            'server_timestamps': 'true', 'doc_id': '25581663504782089',
        }
        response = requests.post('https://www.facebook.com/api/graphql/', headers=self.headers, data=data, proxies=self.proxies)
        return '"subscribe_status":"IS_SUBSCRIBED"' in response.text

# ==================== CLASS NEXT CAPTCHA ====================
class NextCaptcha:
    def __init__(self, apikey):
        self.apikey = apikey
        self.create_task_url = "https://api.3xcaptcha.com/createTask"
        self.get_result_url = "https://api.3xcaptcha.com/getTaskResult"

    def recaptchav2(self, sitekey, siteurl):
        data = {"clientKey": self.apikey, "task": {"type": "RecaptchaV2TaskProxyless", "websiteURL": siteurl, "websiteKey": sitekey}}
        try:
            response = requests.post(self.create_task_url, json=data, timeout=10).json()
            if response.get("errorId", 0) != 0:
                return False, None
            return True, response.get("taskId")
        except:
            return False, None

    def get_result(self, task_id, max_retries=10, delay=0):
        data = {"clientKey": self.apikey, "taskId": task_id}
        for x in range(max_retries):
            try:
                response = requests.post(self.get_result_url, json=data, timeout=10).json()
                if response.get("errorId", 0) != 0:
                    return False, None
                if response.get("status") == "ready":
                    return True, response["solution"]["gRecaptchaResponse"]
                sleep(delay)
            except:
                sleep(1)
        return False, None

# ==================== CLASS TRAODOISUB_API ====================
class TraoDoiSub_Api(object):
    def __init__(self, username, password, proxy=None):
        self.username = username
        self.password = password
        self.proxies = parse_proxy(proxy)
        self.session = requests.Session()
        self.headers = {'authority': 'traodoisub.com', 'accept': 'application/json, text/javascript, */*; q=0.01',
                       'cache-control': 'max-age=0', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'origin': 'https://traodoisub.com', 'referer': 'https://traodoisub.com/',
                       'x-requested-with': 'XMLHttpRequest'}
    
    def info(self):
        response = self.session.post('https://traodoisub.com/scr/login.php', headers=self.headers,
                                     data={'username': self.username, 'password': self.password}, proxies=self.proxies)
        if 'success' in response.text:
            self.cookie = response.headers['Set-cookie']
            headers = {'authority': 'traodoisub.com', 'accept': 'application/json, text/javascript, */*; q=0.01',
                      'accept-language': 'en-US,en;q=0.9', 'cookie': self.cookie,
                      'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
                      'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"',
                      'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
                      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49',
                      'x-requested-with': 'XMLHttpRequest'}
            response = self.session.get('https://traodoisub.com/view/setting/load.php', headers=headers).json()
            self.token = response['tokentds']
            self.xu = response['xu']
            self.name = response['user']
            return True, self.name, self.xu, self.token
        else:
            return False, None
        
    def facebook_configuration(self, id):
        try:
            response = self.session.post('https://traodoisub.com/scr/datnick.php', headers=self.headers,
                                        data={'iddat': id}, proxies=self.proxies).text
            return '1' in response
        except:
            return False

    def add_uid(self, id, g_recaptcha_response):
        headers = {'authority': 'traodoisub.com', 'accept': 'application/json, text/javascript, */*; q=0.01',
                  'accept-language': 'en-US,en;q=0.9', 'cookie': self.cookie,
                  'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
                  'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"',
                  'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49',
                  'x-requested-with': 'XMLHttpRequest'}
        response = self.session.post('https://traodoisub.com/scr/add_uid.php', headers=headers,
                                    data={'idfb': id, 'g-recaptcha-response': g_recaptcha_response}, proxies=self.proxies).text
        if 'success' in response:
            return True, None
        elif 'error' in response:
            return False, response
        else:
            return response

    def get_g_recaptcha_response(self, apikey):
        try:
            response = requests.get('https://traodoisub.com/view/cauhinh/', headers=self.headers, proxies=self.proxies)
            if response.status_code != 200:
                return False, None
            sitekey = response.text.split('data-sitekey="')[1].split('"')[0]
            captcha_solver = NextCaptcha(apikey)
            success, task_id = captcha_solver.recaptchav2(sitekey, 'https://traodoisub.com/view/cauhinh/')
            if success:
                success, g_recaptcha_response = captcha_solver.get_result(task_id)
                if success:
                    return True, g_recaptcha_response
        except:
            return False, 'Lỗi khi lấy reCAPTCHA'
        
    def get_nv_vip(self, fields, type):
        try:
            return self.session.get(f'https://traodoisub.com/api/?fields={fields}&access_token={self.token}&type={type}',
                                   proxies=self.proxies).json()
        except:
            return False
    
    def get_nv_thuong(self, fields):
        try:
            return self.session.get(f'https://traodoisub.com/api/?fields={fields}&access_token={self.token}',
                                   proxies=self.proxies).json()
        except:
            return False
    
    def get_xu_vip(self, type, id):
        try:
            return self.session.get(f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}',
                                   proxies=self.proxies).json()
        except:
            return False
    
    def get_xu_thuong(self, type, id):
        try:
            return self.session.get(f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}',
                                   proxies=self.proxies).json()
        except:
            return False
        
    def cache(self, type, id):
        try:
            return self.session.get(f'https://traodoisub.com/api/coin/?type={type}&id={id}&access_token={self.token}',
                                   proxies=self.proxies).json()
        except:
            return False

# ==================== BOT TELEGRAM ====================

# States
TDS_USERNAME, TDS_PASSWORD, TDS_PROXY, TDS_TASKS, TDS_DELAY, TDS_COOKIES = range(6)

# Biến toàn cục
running_jobs = {}
job_lock = threading.Lock()
stop_flags = {}

# Tên và emoji
TASK_NAMES = {
    'facebook_reaction': 'CẢM XÚC VIP',
    'facebook_reactioncmt': 'CẢM XÚC CMT VIP',
    'facebook_share': 'SHARE VIP',
    'facebook_follow': 'FOLLOW VIP',
    'facebook_page': 'LIKE PAGE VIP',
    'group': 'GROUP',
    'share': 'SHARE THƯỜNG',
    'page': 'LIKE PAGE THƯỜNG',
    'like': 'LIKE THƯỜNG',
    'reaction': 'CẢM XÚC THƯỜNG'
}

TASK_EMOJI = {
    'facebook_reaction': '😍',
    'facebook_reactioncmt': '💬',
    'facebook_share': '📤',
    'facebook_follow': '👤',
    'facebook_page': '📄',
    'group': '👥',
    'share': '📤',
    'page': '📄',
    'like': '👍',
    'reaction': '😍'
}

def format_job_message(job_id, task_name, action_name, xu_reward, balance):
    emoji = TASK_EMOJI.get(task_name, '✅')
    task_display = TASK_NAMES.get(task_name, task_name)
    return (
        f"┌─── [TDS] ✅ JOB {job_id} | {emoji} {task_display}\n"
        f"│ ├ {action_name}\n"
        f"│ ├ 💰 ĐƯỢC CỘNG: +{xu_reward}₫\n"
        f"└ ─ 💵 SỐ DƯ: {balance}₫"
    )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🚀 Bắt đầu TDS"],
        ["📋 Hướng dẫn", "📊 Trạng thái"],
        ["🛑 Dừng TDS"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 <b>BOT TRAO ĐỔI SUB FACEBOOK</b>\n\n"
        "📌 Tool chạy vòng lặp vô hạn, tự động quét job\n"
        "✅ Báo cáo job đẹp như tool gốc\n"
        "💰 Cập nhật số dư liên tục\n\n"
        "🔹 Bấm <b>Bắt đầu TDS</b> để bắt đầu\n"
        "🔹 Bấm <b>Dừng TDS</b> để dừng",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 <b>HƯỚNG DẪN SỬ DỤNG</b>\n\n"
        "1️⃣ Bấm <b>Bắt đầu TDS</b>\n"
        "2️⃣ Nhập tài khoản TraoDoiSub\n"
        "3️⃣ Nhập mật khẩu\n"
        "4️⃣ Nhập proxy (0 bỏ qua)\n"
        "5️⃣ Nhập số nhiệm vụ (VD: 12)\n"
        "6️⃣ Nhập delay (giây) VD: 2\n"
        "7️⃣ Nhập Cookie Facebook\n\n"
        "📌 Bot sẽ chạy vòng lặp vô hạn\n"
        "🔄 Tự động quét job mới\n"
        "✅ Báo cáo job khi có\n\n"
        "🛑 Bấm <b>Dừng TDS</b> để dừng"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    with job_lock:
        if user_id not in running_jobs:
            await update.message.reply_text("📊 Không có TDS nào đang chạy")
            return
        
        job_info = running_jobs.get(user_id, {})
        status = job_info.get('status', 'Đang chạy...')
        completed = job_info.get('completed', 0)
        xu = job_info.get('xu', 0)
        
        await update.message.reply_text(
            f"📊 <b>TRẠNG THÁI TDS</b>\n\n"
            f"🔄 <b>Trạng thái:</b> {status}\n"
            f"✅ <b>Job hoàn thành:</b> {completed}\n"
            f"💰 <b>Xu nhận:</b> {xu}\n",
            parse_mode=ParseMode.HTML
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🚀 Bắt đầu TDS":
        context.user_data.clear()
        await update.message.reply_text(
            "🔑 <b>BƯỚC 1/6: NHẬP TÀI KHOẢN TRAODOISUB</b>\n\n"
            "Nhập <b>tên đăng nhập</b>:",
            parse_mode=ParseMode.HTML
        )
        return TDS_USERNAME
    
    elif text == "🛑 Dừng TDS":
        user_id = update.effective_user.id
        with job_lock:
            if user_id in running_jobs:
                stop_flags[user_id] = True
                await update.message.reply_text("🛑 Đang dừng TDS...")
            else:
                await update.message.reply_text("❌ Không có TDS nào đang chạy")
        return ConversationHandler.END
    
    elif text == "📋 Hướng dẫn":
        await help_command(update, context)
        return ConversationHandler.END
    
    elif text == "📊 Trạng thái":
        await status_command(update, context)
        return ConversationHandler.END
    
    return ConversationHandler.END

async def tds_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tds_username'] = update.message.text.strip()
    await update.message.reply_text(
        "🔑 <b>BƯỚC 2/6: NHẬP MẬT KHẨU TDS</b>",
        parse_mode=ParseMode.HTML
    )
    return TDS_PASSWORD

async def tds_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tds_password'] = update.message.text.strip()
    await update.message.reply_text(
        "🌐 <b>BƯỚC 3/6: NHẬP PROXY</b>\n\n"
        "Nhập 0 để bỏ qua:",
        parse_mode=ParseMode.HTML
    )
    return TDS_PROXY

async def tds_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['tds_proxy'] = None if update.message.text.strip() == '0' else update.message.text.strip()
    await update.message.reply_text(
        "📋 <b>BƯỚC 4/6: CHỌN NHIỆM VỤ</b>\n\n"
        "1 - Cảm xúc VIP\n"
        "2 - Cảm xúc CMT VIP\n"
        "3 - Share VIP\n"
        "4 - Follow VIP\n"
        "5 - Like Page VIP\n"
        "6 - Tham gia Group\n"
        "7 - Share Thường\n"
        "8 - Like Page Thường\n"
        "9 - Like Thường\n"
        "0 - Cảm xúc Thường\n\n"
        "💡 Ví dụ: 123",
        parse_mode=ParseMode.HTML
    )
    return TDS_TASKS

async def tds_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks_str = update.message.text.strip()
    valid_tasks = set('1234567890')
    if not all(c in valid_tasks for c in tasks_str):
        await update.message.reply_text("❌ Nhập lại (0-9):")
        return TDS_TASKS
    context.user_data['tds_tasks'] = tasks_str
    await update.message.reply_text(
        "⏱️ <b>BƯỚC 5/6: NHẬP DELAY</b>\n\n"
        "Delay giữa các job (giây, VD: 2):",
        parse_mode=ParseMode.HTML
    )
    return TDS_DELAY

async def tds_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        delay = float(update.message.text.strip())
        if delay < 0.1:
            raise ValueError
        context.user_data['tds_delay'] = delay
    except:
        await update.message.reply_text("❌ Nhập số hợp lệ (VD: 2):")
        return TDS_DELAY
    
    await update.message.reply_text(
        "🍪 <b>BƯỚC 6/6: NHẬP COOKIE FACEBOOK</b>\n\n"
        "Cookie chứa c_user=...",
        parse_mode=ParseMode.HTML
    )
    return TDS_COOKIES

async def tds_cookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cookie = update.message.text.strip()
    if 'c_user=' not in cookie:
        await update.message.reply_text("❌ Cookie không có c_user=, nhập lại:")
        return TDS_COOKIES
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    username = context.user_data.get('tds_username')
    password = context.user_data.get('tds_password')
    proxy = context.user_data.get('tds_proxy')
    tasks_str = context.user_data.get('tds_tasks')
    delay = context.user_data.get('tds_delay', 2)
    
    context.user_data.clear()
    
    await update.message.reply_text(
        f"🚀 <b>KHỞI CHẠY TDS</b>\n\n"
        f"👤 Tài khoản: {username}\n"
        f"📋 Nhiệm vụ: {tasks_str}\n"
        f"⏱️ Delay: {delay}s\n\n"
        f"🔄 Bot sẽ chạy vòng lặp vô hạn...",
        parse_mode=ParseMode.HTML
    )
    
    if user_id in stop_flags:
        del stop_flags[user_id]
    
    threading.Thread(
        target=run_tds_loop,
        args=(user_id, chat_id, username, password, proxy, cookie, tasks_str, delay, context),
        daemon=True
    ).start()
    
    return ConversationHandler.END

def run_tds_loop(user_id, chat_id, username, password, proxy, cookie, tasks_str, delay, context):
    """Vòng lặp vô hạn - BÁO TRẠNG THÁI CHỜ JOB"""
    try:
        tds = TraoDoiSub_Api(username, password, proxy)
        profile = tds.info()
        
        if not profile[0]:
            send_message_sync(chat_id, context, "❌ Đăng nhập TDS thất bại!")
            return
        
        user, xu, token = profile[1], profile[2], profile[3]
        
        with job_lock:
            running_jobs[user_id] = {
                'status': 'Đang chạy',
                'completed': 0,
                'xu': xu,
                'username': user
            }
        
        send_message_sync(chat_id, context,
            f"✅ Đăng nhập TDS thành công!\n👤 User: {user}\n💰 Xu: {xu}")
        
        fb = Facebook_Api(cookie, proxy)
        info = fb.info()
        
        if 'error' in info:
            send_message_sync(chat_id, context, "❌ Cookie Facebook không hợp lệ!")
            return
        
        uid = info['id']
        name = info['name']
        
        send_message_sync(chat_id, context,
            f"✅ Cookie Facebook hợp lệ!\n👤 ID: {uid}\n📛 Tên: {name}")
        
        if not tds.facebook_configuration(uid):
            send_message_sync(chat_id, context, f"⚠️ Cấu hình UID {uid}...")
        
        task_map = {
            '1': ('facebook_reaction', 'Cảm xúc VIP', 'vip'),
            '2': ('facebook_reactioncmt', 'Cảm xúc CMT VIP', 'vip'),
            '3': ('facebook_share', 'Share VIP', 'vip'),
            '4': ('facebook_follow', 'Follow VIP', 'vip'),
            '5': ('facebook_page', 'Like Page VIP', 'vip'),
            '6': ('group', 'Tham gia Group', 'thuong'),
            '7': ('share', 'Share Thường', 'thuong'),
            '8': ('page', 'Like Page Thường', 'thuong'),
            '9': ('like', 'Like Thường', 'thuong'),
            '0': ('reaction', 'Cảm xúc Thường', 'thuong')
        }
        
        task_list = [task_map[c] for c in tasks_str if c in task_map]
        
        if not task_list:
            send_message_sync(chat_id, context, "⚠️ Không có nhiệm vụ hợp lệ!")
            return
        
        job_id = 0
        completed = 0
        total_xu = 0
        wait_counter = 0
        
        # Vòng lặp vô hạn
        while True:
            if stop_flags.get(user_id, False):
                send_message_sync(chat_id, context, "🛑 Đã dừng TDS theo yêu cầu")
                break
            
            wait_counter += 1
            
            # Báo trạng thái chờ job mỗi 30 giây
            if wait_counter % 10 == 0:
                send_message_sync(chat_id, context, 
                    f"🔄 Đang chờ job mới... (đã chạy {int(wait_counter * delay)}s)")
            
            for task_key, task_name, task_type in task_list:
                if stop_flags.get(user_id, False):
                    break
                
                if task_type == 'vip':
                    list_nv = tds.get_nv_vip(task_key, 'ALL' if task_key != 'facebook_follow' else '')
                else:
                    list_nv = tds.get_nv_thuong(task_key)
                
                if not list_nv or (isinstance(list_nv, dict) and 'error' in list_nv):
                    sleep(delay)
                    continue
                
                data_list = list_nv.get('data', list_nv) if isinstance(list_nv, dict) else list_nv
                
                if not data_list:
                    sleep(delay)
                    continue
                
                # Reset counter khi có job
                wait_counter = 0
                
                for job in data_list:
                    if stop_flags.get(user_id, False):
                        break
                    
                    if task_type == 'vip':
                        idpost = job.get('id', '')
                        code = job.get('code', '')
                        reac_type = job.get('type', 'LIKE')
                    else:
                        idpost = job.get('id', '')
                        code = idpost
                        reac_type = job.get('type', 'LIKE')
                    
                    if not idpost:
                        continue
                    
                    post_id = idpost.split('_')[1] if '_' in idpost else idpost
                    
                    success = False
                    try:
                        if task_key == 'facebook_reaction':
                            success = fb.reaction(post_id, reac_type)
                        elif task_key == 'facebook_reactioncmt':
                            success = fb.reactioncmt(post_id, reac_type)
                        elif task_key == 'facebook_share':
                            success = fb.share(post_id)
                        elif task_key == 'facebook_follow':
                            success = fb.follow(post_id)
                        elif task_key == 'facebook_page':
                            success = fb.like_page(post_id)
                        elif task_key == 'group':
                            success = fb.group(idpost)
                        elif task_key == 'share':
                            success = fb.share(idpost)
                        elif task_key == 'page':
                            success = fb.like_page(idpost)
                        elif task_key == 'like':
                            success = fb.reaction(post_id, 'LIKE')
                        elif task_key == 'reaction':
                            success = fb.reaction(post_id, reac_type)
                    except Exception as e:
                        logger.error(f"Lỗi {task_name}: {e}")
                    
                    if success:
                        job_id += 1
                        completed += 1
                        
                        try:
                            if task_type == 'vip':
                                xu_reward = tds.get_xu_vip(task_key, code)
                            else:
                                xu_reward = tds.get_xu_thuong(task_key.upper(), code)
                            
                            if xu_reward and 'success' in xu_reward:
                                xu_amount = xu_reward['data']['xu']
                                total_xu += xu_amount
                                
                                with job_lock:
                                    if user_id in running_jobs:
                                        running_jobs[user_id]['completed'] = completed
                                        running_jobs[user_id]['xu'] = total_xu
                                
                                action_name = f"{reac_type} {post_id}" if task_type == 'vip' else f"Job {job_id}"
                                msg = format_job_message(job_id, task_key, action_name, xu_amount, total_xu)
                                send_message_sync(chat_id, context, msg)
                        except Exception as e:
                            logger.error(f"Lỗi nhận xu: {e}")
                    
                    sleep(delay)
            
            sleep(delay)
            
    except Exception as e:
        logger.error(f"Lỗi TDS loop: {e}")
        send_message_sync(chat_id, context, f"❌ Lỗi: {str(e)[:200]}")
    finally:
        with job_lock:
            if user_id in running_jobs:
                del running_jobs[user_id]
        if user_id in stop_flags:
            del stop_flags[user_id]

def send_message_sync(chat_id, context, text):
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML
            )
        )
        loop.close()
    except Exception as e:
        logger.error(f"Lỗi gửi tin nhắn: {e}")

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Đã hủy")
    return ConversationHandler.END

# ==================== MAIN ====================

def main():
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0
    )
    
    app = Application.builder().token(BOT_TOKEN).request(request).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(🚀 Bắt đầu TDS)$"), button_handler)
        ],
        states={
            TDS_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, tds_username)],
            TDS_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, tds_password)],
            TDS_PROXY: [MessageHandler(filters.TEXT & ~filters.COMMAND, tds_proxy)],
            TDS_TASKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, tds_tasks)],
            TDS_DELAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, tds_delay)],
            TDS_COOKIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, tds_cookies)],
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)]
    )
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
    
    print("🤖 Bot TDS FREE đang chạy vòng lặp vô hạn...")
    app.run_polling()

if __name__ == "__main__":
    main()