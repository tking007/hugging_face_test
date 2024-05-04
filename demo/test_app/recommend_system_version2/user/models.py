from django.db import models


# Create your models here.
class User(models.Model):
    sex_gender = (
        ('男', "男"),
        ('女', "女"),
    )
    province_gender = (
        ('北京', '北京'),
        ('天津', '天津'),
        ('河北', '河北'),
        ('山西', '山西'),
        ('内蒙古', '内蒙古'),
        ('辽宁', '辽宁'),
        ('吉林', '吉林'),
        ('黑龙江', '黑龙江'),
        ('上海', '上海'),
        ('江苏', '江苏'),
        ('浙江', '浙江'),
        ('安徽', '安徽'),
        ('福建', '福建'),
        ('江西', '江西'),
        ('山东', '山东'),
        ('河南', '河南'),
        ('湖北', '湖北'),
        ('湖南', '湖南'),
        ('广东', '广东'),
        ('广西', '广西'),
        ('海南', '海南'),
        ('重庆', '重庆'),
        ('四川', '四川'),
        ('贵州', '贵州'),
        ('云南', '云南'),
        ('西藏', '西藏'),
        ('陕西', '陕西'),
        ('甘肃', '甘肃'),
        ('青海', '青海'),
        ('宁夏', '宁夏'),
        ('新疆', '新疆'),
        ('台湾', '台湾'),
        ('香港', '香港'),
        ('澳门', '澳门'),
)
    subject_gender = (
        ('理科', '理科'),
        ('文科', '文科'),
    )

    username = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    sex = models.CharField(max_length=32, choices=sex_gender, default="男")
    province = models.CharField(max_length=64, choices=province_gender, default="四川")
    subject = models.CharField(max_length=64, choices=subject_gender, default="理科")
    score = models.IntegerField(default=500)
    personality_type = models.CharField(max_length=32, default=0)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["c_time"]
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"
