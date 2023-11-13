from tencentcloud.common import credential  # 这里需要安装腾讯翻译sdk
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models
import json


def fanyi(query):
    try:
        cred = credential.Credential("AKIDMZYJsENI2cyB9sQmtnY7UhYFiwwhPxGK", "we7MM8gz48xXs1xe7g7NPCm8F8h16yc5")  # "xxxx"改为SecretId，"yyyyy"改为SecretKey
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

        req = models.TextTranslateBatchRequest()
        req.SourceTextList  = query  # 要翻译的语句
        req.Source = 'en'  # 源语言类型
        req.Target = 'zh'  # 目标语言类型
        req.ProjectId = 0

        resp = client.TextTranslateBatch(req)
        data = json.loads(resp.to_json_string())
        print(query)
        print(data['TargetTextList'])

    except TencentCloudSDKException as err:
        print(err)

    return data['TargetTextList']


# if __name__ == "__main__":
#     source_texts = ["Hello", "How are you?", "Translate this text."]
#     fanyi(source_texts)