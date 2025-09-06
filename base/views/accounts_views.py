import json
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from django import forms
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from base.models import Item

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # 無効な payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # 署名検証エラー
        return HttpResponse(status=400)

    # checkout.session.completed イベントを処理
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_details', {}).get('email') or session.get('customer_email')
        subscription_id = session.get('subscription')

        if customer_email and subscription_id:
            try:
                user = User.objects.get(email=customer_email)
                user.is_premium = True
                user.save()
            except User.DoesNotExist:
                pass

    return HttpResponse(status=200)

# カスタムユーザー作成フォーム（UserCreationForm を拡張）
class CustomUserCreationForm(UserCreationForm):
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('M', '男性'), ('F', '女性'), ('O', 'その他')], required=False)

    class Meta:
        model = User
        fields = ("username", "email", "gender", "birth_date", "password1", "password2")

@login_required
def premium_view(request):
    user = request.user  # 新規ユーザー作成は不要

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Stripe Checkout セッションを作成
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'jpy',
                'product_data': {'name': '有料会員（月額550円）'},
                'unit_amount': 550,  # 550円
                'recurring': {'interval': 'month'},
            },
            'quantity': 1,
        }],
        mode='subscription',
        customer_email=user.email,  # 現在ログイン中のユーザーのメールを使う
        success_url=request.build_absolute_uri(
            reverse('premium_success')
         ) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('premium_cancel')),
    )
    return redirect(session.url, code=303)


@login_required
def premium_success(request):
    """
    決済成功後にログイン中ユーザーを premium 化
    """
    session_id = request.GET.get('session_id')
    if session_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # セッション確認（任意: エラーハンドリング用）
            session = stripe.checkout.Session.retrieve(session_id)

            # ログイン中ユーザーを更新
            user = request.user
            user.is_premium = True
            user.save()

        except Exception as e:
            print("Stripe session retrieve error:", e)

    return render(request, 'pages/premium_success.html')


def premium_cancel(request):
    return render(request, 'pages/premium_cancel.html')



    # checkout.session.completed イベントを捕まえてユーザーを更新
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_details', {}).get('email') or session.get('customer_email')
        subscription_id = session.get('subscription')
        if customer_email and subscription_id:
            try:
                user = User.objects.get(email=customer_email)
                user.is_premium = True
                user.save()
            except User.DoesNotExist:
                pass

    return HttpResponse(status=200)


def top_view(request):
    keyword = request.GET.get('keyword', '')

    items = Item.objects.filter(is_published=True)

    if keyword:
        # 検索処理
        items = items.filter(
            Q(name__icontains=keyword) |
            Q(category__name__icontains=keyword) |
            Q(address__icontains=keyword)
        )

        # 検索結果が1件だけなら item_detail にリダイレクト
        if items.count() == 1:
            item = items.first()
            return redirect('item_detail', pk=item.pk)

        # 検索結果が0件なら search.html を表示
        if not items.exists():
            return render(request, "snippets/search.html", {
                "keyword": keyword,
                "not_found": True
            })


    # 通常のトップページ表示（レビュー付きのお店も渡す）
    reviewed_items = Item.objects.annotate(review_count=Count("reviews")).filter(review_count__gt=0)

    return render(request, "top.html", {
        "items": items,
        "keyword": keyword,
        "reviewed_items": reviewed_items
    })



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
               user = form.get_user()
               login(request, user)
               return redirect('top')
    else:
        form = AuthenticationForm()
    return render(request, 'pages/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    ログアウトしてトップページにリダイレクト
    """
    logout(request)
    return redirect('top')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('top')
    else:
            form = CustomUserCreationForm()        
    return render(request, 'pages/signup.html', {'form': form})




