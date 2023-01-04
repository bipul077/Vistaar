from django.shortcuts import render,redirect
from .models import Review
from .forms import ReviewForm
from django.contrib import messages

# Create your views here.
def submit_review(request,prod_id):
# if request.user.is_authenticated:
    url = request.META.get('HTTP_REFERER')#storing the current url of the page
    if request.method == "POST":
        try:
           # reviews = Review.objects.get(user__id=request.user.id,product__id=prod_id)#to check if the same user has reviewed or not
            reviews = Review.objects.get(product__id=prod_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Your reviews has been updated!!')
            return redirect(url)
        except Review.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = Review()
                data.uname = form.cleaned_data['name']
                data.email = form.cleaned_data['email']
                data.review = form.cleaned_data['message']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')#gets the ip address of the site
                data.product_id= prod_id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted')
                return redirect(url)
            