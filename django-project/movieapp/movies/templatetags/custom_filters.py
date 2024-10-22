from django import template
from django.utils import timezone
from datetime import datetime, time, date
from dateutil.relativedelta import relativedelta


register = template.Library()

@register.filter
def remaining_time(vizyon_date):
    if vizyon_date is None:
        return "Tarih belirtilmemiş"
    
    
    now = timezone.now()

    if isinstance(vizyon_date, datetime):
        pass
    
    elif isinstance(vizyon_date, date):
        vizyon_date = datetime.combine(vizyon_date, time.min)
        vizyon_date = timezone.make_aware(vizyon_date)

    if vizyon_date < now:
        return "Vizyon tarihi geçti"
    

    delta = relativedelta(vizyon_date, now)

    result = []

    if delta.years > 0:
        result.append(f"{delta.years} yıl")
    if delta.months > 0:
        result.append(f"{delta.months} ay")
    if delta.days > 0:
        result.append(f"{delta.days} gün")
    if delta.hours > 0:
        result.append(f"{delta.hours} saat")
    if delta.minutes > 0:
        result.append(f"{delta.minutes} dak")
    if delta.seconds > 0:
        result.append(f"{delta.seconds} san")

    if not result:
        return "Bugün vizyona giriyor"
    
    return " ".join(result)



