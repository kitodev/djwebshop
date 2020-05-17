from allauth.account.utils import send_email_confirmation
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
# from django.shortcuts import redirect
from stripe.api_resources import charge

from .filter import ItemFilter

from .forms import CheckoutForm, ContactForm
from .models import Item, OrderItem, Order, BillingAddress, Payment

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def product(request):

    items = Item.objects.all()
    itemFilter = ItemFilter(request.GET, queryset=items)
    items = itemFilter.qs

    context = {
        'items': items,
        'itemFilter': itemFilter
    }

    return render(request, "product-page.html", context)

def checkout(request):
    return render(request, "checkout-page.html")

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')

                # same_billing_address = form.cleaned_data('same_billing_address')
                # save_info = form.cleaned_data('save_info')
                # use_default_shipping = form.cleaned_data.get('use_default_shipping ')
                # shipping_address1 = form.cleaned_data.get('shipping_address1')
                # shipping_address2 = form.cleaned_data.get('shipping_address2')
                # shipping_country = form.cleaned_data.get('shipping_country ')
                # shipping_zip = form.cleaned_data.get('shipping_zip')
                # set_default_shipping = form.cleaned_data.get('set_default_shipping')
                # use_default_billing = form.cleaned_data.get('use_default_billing')
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # billing_address1 = form.cleaned_data.get('billing_address1')
                # billing_address2 = form.cleaned_data.get('billing_address2')
                # billing_country = form.cleaned_data.get('billing_country')
                # billing_zip = form.cleaned_data.get('billing_zip')
                # set_default_billing = form.cleaned_data.get('set_default_billing')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option select.")
                    return redirect('core:checkout-page')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active orders")
            return redirect("core:order-summary")

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token
            )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('err', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API

            messages.error(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authanticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Failed network communication")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email

            messages.error(self.request, "Generic error. Please try again")
            return redirect("/")

        except Exception as e:
            # Something else happened, completely unrelated to Stripe

            messages.error(self.request, "Serious error occured. We have been notifed")
            return redirect("/")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order-summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active orders")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"
    # query = Item.objects.filter(name__contains='Item 1')

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
    return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,
                                    ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
        else:
            messages.info(request, "This item was removed from your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "This item was removed from your cart")
    return redirect("core:product", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,
                                    ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quanity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was removed from your cart")
            return redirect("core:order-summary", slug=slug)
    else:
        messages.info(request, "This item was removed from your cart")
    return redirect("core:order-summary", slug=slug)

@login_required
def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
    return redirect("core:product", slug=slug)


@login_required
def add_to_wishlist(request, slug):
    item = get_object_or_404(Item, slug=slug)
    wished_item, created = Wishlsit.objects.get_or_create(wished_item=item,
                                                          slug=item.slug,
                                                          user=request.user
                                                          )
    messages.info(request, "The item was added to your wishlist")
    return redirect("core:product_detail", slug=slug)

# def get_coupon(request, code):
#     try:
#         coupon = Coupon.objects.get(
#             code=code)
#     except ObjectDoesNotExist:
#         messages.info(request, "You do not have an active order")
#         return redirect("core:checkout")
#
# def add_coupon(request, code):
#     try:
#         order = Order.objects.get(
#             user=request.user, ordered=False)
#         order.coupon = get_coupon(request, code)
#         order.save()
#         messages.info(request, "Succesfully added coupon")
#         return redirect("core:checkout")
#     except ObjectDoesNotExist:
#         messages.info(request, "You do not have an active order")
#         return redirect("core:checkout")

def contactView(request):
    if request.method == "GET":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

        try:
            send_mail(subject, message, email, ['admin@gmail.com'])
        except BadHeaderError:
            return HttpResponse('Invalid header found')
        return redirect('success')
    return render(request, 'contact.html', {'form':form})

def successView(request):
    return HttpResponse('Success! Thank You for your message.')