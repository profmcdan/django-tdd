from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from django.core.mail import send_mail
from .models import Post
from .forms import PostForm
import stripe
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
# Create your views here.


class HomeView(generic.TemplateView):
    template_name = "birdie/home.html"


class AdminView(generic.TemplateView):
    template_name = "birdie/admin.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminView, self).dispatch(request, *args, **kwargs)


class PostUpdateView(generic.UpdateView):
    template_name = 'birdie/update.html'
    model = Post
    form_class = PostForm
    success_url = "/"

    def post(self, request, *args, **kwargs):
        if getattr(request.user, 'first_name', None) == 'Martin':
            raise Http404()
        return super(PostUpdateView, self).post(request, *args, **kwargs)


class PaymentView(generic.View):
    def post(self, request, *args, **kwargs):
        charge = stripe.Charge.create(
            amount=100, currency="usd", description="Some Item", token=request.POST.get('token'))
        send_mail('Payment received', 'Charge {0} succeeded'.format(
            charge['id']), 'server@example.com', ['admin@example.com'])
        return redirect('/')
