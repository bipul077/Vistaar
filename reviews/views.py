from django.shortcuts import render,redirect
from .models import Review
from .forms import ReviewForm
from django.contrib import messages

# Create your views here.
def submit_review(request,product_id):
# if request.user.is_authenticated:
    print("hahaha")
    print(product_id)
    url = request.META.get('HTTP_REFERER')#storing the current url of the page
    # form = ReviewForm(request.POST)
    # print(form.cleaned_data['uname'])
    if request.method == "POST":
        # try:
        #    # reviews = Review.objects.get(user__id=request.user.id,product__id=prod_id)#to check if the same user has reviewed or not
        #     reviews = Review.objects.get(product__id=product_id)
        #     form = ReviewForm(request.POST, instance=reviews)
        #     # form.save()
        #     messages.success(request, 'Your reviews has been updated!!')
        #     return redirect(url)
        # except Review.DoesNotExist:
        form = ReviewForm(request.POST)
        print(form)
        if form.is_valid():
            print("wow")
            data = Review()
            data.uname = form.cleaned_data['uname']
            data.email = form.cleaned_data['email']
            data.review = form.cleaned_data['review']
            data.rating = form.cleaned_data['rating']
            print(data.uname,data.email,data.review,data.rating)
            
            # data.rating = form.cleaned_data['rating']
            data.ip = request.META.get('REMOTE_ADDR')#gets the ip address of the site
            data.product_id= product_id
            data.save()
            print("done")
            messages.success(request, 'Thank you! Your review has been submitted')
            return redirect(url)
    # return redirect(url)
        