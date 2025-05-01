from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0  # ในกรณีที่เกิดข้อผิดพลาดในการคำนวณ
