from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from base.models import Item, Reservation
from django.contrib import messages

@login_required
def make_reservation(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if not request.user.is_premium:
        messages.error(request, "予約は有料会員のみ可能です。")
        return redirect('premium')

    # すでに予約済みか確認
    existing = Reservation.objects.filter(user=request.user, item=item)
    if existing.exists():
        messages.info(request, "このお店はすでに予約済みです。")
        return redirect('item_detail', pk=item.id)

    Reservation.objects.create(user=request.user, item=item)
    messages.success(request, "予約が完了しました！")
    return redirect('reservation_list')

@login_required
def reservation_list(request):
    if not request.user.is_premium:
        messages.error(request, "有料会員のみ予約リストを確認できます。")
        return redirect('premium')

    reservations = Reservation.objects.filter(user=request.user).select_related('item')
    return render(request, 'pages/reservation_list.html', {'reservations': reservations})
