from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def money_format(value):
    """تبدیل اعداد به فرمت پول با جداکننده هزارگان"""
    try:
        # تبدیل به float و گرد کردن به عدد صحیح
        value = round(float(value))
        # فرمت‌بندی با جداکننده هزارگان
        formatted = "{:,.0f}".format(value)
        # تبدیل اعداد انگلیسی به فارسی
        persian_numbers = str(formatted).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))
        return persian_numbers
    except (ValueError, TypeError):
        return value

@register.filter
def persian_number(value):
    """تبدیل اعداد انگلیسی به فارسی"""
    try:
        return str(value).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))
    except (ValueError, TypeError):
        return value