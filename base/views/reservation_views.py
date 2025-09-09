from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from base.models import Item, Reservation
from django.contrib import messages

@login_required
def make_reservation(request, item_id):
    if not request.user.is_premium:
        messages.error(request, "予約は有料会員のみ可能です。有料会員登録をお願いします。")
        return redirect("premium")

    item = get_object_or_404(Item, pk=item_id)

    if request.method == "POST":
        date_time = request.POST.get("date_time")
        num_people = request.POST.get("num_people")
        seat_type = request.POST.get("seat_type")
        comment = request.POST.get("comment")

        Reservation.objects.create(
            user=request.user,
            item=item,
            date_time=date_time,
            num_people=num_people,
            seat_type=seat_type,
            comment=comment
        )
        messages.success(request, "予約が完了しました。")
        return redirect("reservation_list")

    return render(request, "pages/reservation_write.html", {"item": item})


@login_required
def reservation_list(request):
    if not request.user.is_premium:
        messages.error(request, "予約リストは有料会員のみ表示可能です。")
        return redirect("premium")

    reservations = Reservation.objects.filter(user=request.user).order_by("-date_time")
    return render(request, "pages/reservation_list.html", {"reservations": reservations})


@login_required
def cancel_reservation(request, reservation_id):
    if not request.user.is_premium:
        messages.error(request, "予約のキャンセルは有料会員のみ可能です。")
        return redirect("premium")

    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    reservation.delete()
    messages.success(request, "予約をキャンセルしました。")
    return redirect("reservation_list")