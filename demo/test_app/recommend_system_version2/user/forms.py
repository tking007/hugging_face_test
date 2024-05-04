from django import forms
from django.core.exceptions import ValidationError
from . import models


class RegisterForm(forms.Form):
    # 校验两次密码是否相同等
    def clean(self):
        username = self.cleaned_data.get('username')
        user = models.User.objects.filter(username=username).first()
        if user:
            raise ValidationError('用户名已存在')
        pwd = self.cleaned_data.get('password1')
        re_pwd = self.cleaned_data.get('password2')
        if pwd == re_pwd:
            return self.cleaned_data
        else:
            raise ValidationError('两次密码不一致')

    username = forms.CharField(label="用户名", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "请输入用户名小于30个字符"}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class LoginForm(forms.Form):
    # 校验账号密码
    def clean(self):
        username = self.cleaned_data.get('username')
        user = models.User.objects.filter(username=username).first()
        if not user:
            raise ValidationError('该用户名尚未注册')
        else:
            if user.password != self.cleaned_data.get('password'):
                raise ValidationError('密码输入错误')
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class StudentInfoForm(forms.Form):
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
    sex = forms.ChoiceField(label='性别', choices=sex_gender)
    province = forms.ChoiceField(label='省份', choices=province_gender)
    subject = forms.ChoiceField(label='科别', choices=subject_gender)
    score = forms.IntegerField(label='高考分数', max_value=800, min_value=0, widget=forms.NumberInput)
