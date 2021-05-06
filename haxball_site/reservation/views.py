from datetime import timedelta, datetime
from .forms import ReservationEntryForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import ReservationEntry, ReservationHost
from django.views.generic import ListView

from .templatetags.reservation_extras import teams_can_reserv


class ReservationList(ListView):
    queryset = ReservationEntry.objects.filter(match__is_played=False).order_by('time_date')
    context_object_name = 'reservations'
    template_name = 'reservation/reservation_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ReservationList, self).get_context_data()
        context['active_hosts'] = ReservationHost.objects.filter(is_active=True)
        return context

    def post(self, request):
        data = request.POST
        
        date_time_obj = datetime.strptime(data['time_date'], '%Y-%m-%dT%H:%M')
        d1 = date_time_obj - timedelta(minutes=25)
        d2 = date_time_obj + timedelta(minutes=25)
        reserved = ReservationEntry.objects.filter(time_date__range=[d1, d2])
        active_hosts = ReservationHost.objects.filter(is_active=True)
        if reserved.count() < active_hosts.count():
            hosts = set(active_hosts)
            for i in reserved:
                hosts.remove(i.host)
            h = hosts.pop()
            ReservationEntry.objects.create(author=request.user, time_date=date_time_obj,
                                            match_id=int(data['match']), host=h)
            return redirect('reservation:host_reservation')
        else:
            return render(request, 'reservation/reservation_list.html', {
                'reservations': ReservationEntry.objects.filter(match__is_played=False).order_by('-time_date'),
                'active_hosts': ReservationHost.objects.filter(is_active=True),
                'message': 'Выбранное время занято!!'})


@require_POST
def delete_entry(request, pk):
    reserved_match = get_object_or_404(ReservationEntry, pk=pk)
    t = teams_can_reserv(request.user)

    if (reserved_match.match.team_home in t) or (reserved_match.match.team_guest in t):
        reserved_match.delete()
        return redirect('reservation:host_reservation')
    else:
        return HttpResponse('Ошибка доступа')
