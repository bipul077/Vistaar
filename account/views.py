from multiprocessing import connection
from django.db import reset_queries
from django.shortcuts import redirect, render
from django.contrib import messages
from django.shortcuts import render, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.shortcuts import get_object_or_404
from .forms import EditBusinessProfileForm, EditCompanyInfoForm, LeadsEditForm, MyPasswordChangeForm, UserRegistrationForm, UserEditForm, ProfileEditForm, RetailerForm, SupplierForm, CompanyForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from suppliers.models import Company, Supplier
from products.models import Products
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes,force_text,force_str,DjangoUnicodeDecodeError
# from .utils import generate_token

from django.core.mail import EmailMessage,get_connection, send_mail
from django.conf import settings as conf_settings

# import qrcode
from PIL import Image
from pathlib import Path
import os
from vistaar.settings import MEDIA_ROOT

# Create your views here.

#Activation email - SEND
def send_action_email(user,request):
    current_site = get_current_site(request)
    email_subject = 'Vistaar - Activate Your account!'
    email_body = render_to_string('account/activate.html',{
        'user':user,
        'domain':current_site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user),
    })
    
    email = EmailMessage(subject=email_subject,body=email_body,from_email=conf_settings.EMAIL_FROM_USER,to=[user.email])

    email.send()
    
    
#Lead notification Email
def send_lead_email(user,supplier,product,request):
    email_subject = 'Vistaar - You have a new lead!'
    email_body = render_to_string('supplier/new_lead.html',{
        'user':user,
        'supplier':supplier,
        'product':product,
    })
    
    email = EmailMessage(subject=email_subject,body=email_body,from_email=conf_settings.EMAIL_FROM_USER,to=[supplier.email,supplier.user.email])
    email.send()

def send_test_email(request):

    with get_connection(host='mail.vistaartrade.com', port=465, username='accounts@vistaartrade.com', password='A%9.yWxxY$bR', use_ssl=True) as connection:
        email = EmailMessage(subject='Tester',body='Tester',from_email='accounts@vistaartrade.com',to=['aashutosh83@hotmail.com'],connection=connection)
        email.send()

    print("Email sent!")

def register(request):

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name  = request.POST['last_name']
        username  = request.POST['username']
        email  = request.POST['email']
        password  = request.POST['password']
        confirm_password  = request.POST['confirm_password']
        phone_number = request.POST['phone_number']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken. Try a different one!')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered!')
                return redirect('register')
            else:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password
                )
                user.save()
                
                user.profile.mobile_number = phone_number
                
                user.profile.save()
                
                send_action_email(user,request)
                
                messages.success(request, 'Your account has been created. Login to continue!')
                
                return redirect('login')
        else:
            messages.error(request, 'Password fields do not match!')
            return redirect('register')
    else:

        send_test_email(request)
        return render(request,'account/register.html')
    

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Disabled account')
                return redirect('login')
        else:
            messages.error(request, 'Your username and password didn\'t match. Please try again.')
            return redirect('login')
    else:
        return render(request, 'account/login.html')

@login_required
def post_requirements(request):
    if request.method == 'POST':
        current_user = request.user.username
        buyer = User.objects.get(username=current_user)
        try:
            product_attribute = request.POST['product']
            products = Products.objects.all()
            product = products.filter(Q(product_name__icontains=product_attribute) | Q(description__icontains=product_attribute))
        except Products.DoesNotExist:
            product = None
        quantity_required = request.POST['quantity']
        request_description = request.POST['description']
        for pr in product:
            try:
                supplier_user = User.objects.get(username=pr.supplier.user.username)
                supplier = Supplier.objects.get(user=supplier_user)
            except Supplier.DoesNotExist:
                supplier = None

            primary_leads = Primary_leads(seller=supplier, buyer=buyer, product=pr,
                                        quantity_required=quantity_required,
                                        request_description=request_description)
            primary_leads.save()
            send_lead_email(current_user,supplier,pr,request)
        return redirect('home')
    else:
        return render(request, 'account/post_requirements.html')


@login_required
def dashboard(request):
    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    latest_buyleads = Primary_leads.objects.filter(seller = current_supplier)[:3]
    all_buyleads_count = Primary_leads.objects.filter(seller=current_supplier).count()

    latest_mbox = Message_box.objects.filter(seller = request.user)[:3]
    all_mbox_count = Message_box.objects.filter(seller = request.user).count()

    trending_products = Products.objects.filter(supplier=current_supplier).order_by('-id')[:3]

    print(request.get_full_path())
    return render(request,
                'dashboard/dashboard.html',
                {'section': 'dashboard','current_profile': current_profile,
                'current_supplier':current_supplier,'leads':latest_buyleads,'leads_count':all_buyleads_count, 'mboxes':latest_mbox,'mboxes_count':all_mbox_count
                ,'trending':trending_products}
                )


@login_required
def company_profile(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    current_company = Company.objects.get_or_create(supplier=current_supplier)

    try:
        company_form = CompanyForm(instance=current_company.id)
    except:
        company_form = CompanyForm(request.POST or None)

    if request.method == 'POST':
        try:
            company_form = CompanyForm(instance=current_company.id)
        except:
            company_form = CompanyForm(request.POST or None)

        if company_form.is_valid():
            company_details = company_form.save(commit=False)
            company_details.supplier = current_supplier
            company_details.save()

    return render(request,
                'dashboard/company_profile.html',
                {'section': 'dashboard','current_profile': current_profile,
                'current_supplier':current_supplier, 'company_form': company_form})
                

@login_required
def lead_manager(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    sent_messages = Lead_messages.objects.filter()

    return render(request,
                'dashboard/lead_manager.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})

@login_required
def manage_products(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    products = Products.objects.filter(supplier=current_supplier)

    return render(request,
                'dashboard/manage_products.html',
                {'section': 'dashboard','current_profile': current_profile,
                 'current_supplier':current_supplier,
                 'products': products})


@login_required
def buy_leads(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    latest_buyleads = Primary_leads.objects.filter(seller=current_supplier)[:3]

    return render(request,
                'dashboard/buy_leads.html',
                {'section': 'dashboard','current_profile': current_profile,
                 'current_supplier':current_supplier,
                 'latest_buyleads': latest_buyleads})


@login_required
def edit_leads(request, id):
    lead = Primary_leads.objects.get(pk=id)

    if request.method == 'POST':
        lead_edit_form = LeadsEditForm(instance=lead,
                                    data=request.POST)
        if lead_edit_form.is_valid():
            lead_edit_form.save()
    else:
        lead_edit_form = LeadsEditForm(instance=lead)
    return render(request,
                  'dashboard/edit_leads.html',
                  {'lead_edit_form': lead_edit_form})


@login_required
def collect_payments(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/collect_payments.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})

@login_required
def catalog_view(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/catalog_view.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})

@login_required
def photos_docs(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/photos&docs.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})


@login_required
def bills_invoice(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/bill&invoice.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})


@login_required
def buyer_tools(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/buyer_tools.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})


@login_required
def settings(request):

    current_profile = request.user.profile
    try:
        current_supplier = Supplier.objects.get(user=request.user)
    except Supplier.DoesNotExist:
        current_supplier = None

    return render(request,
                'dashboard/settings.html',
                {'section': 'dashboard','current_profile': current_profile,'current_supplier':current_supplier})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                    data=request.POST,
                                    files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        
        if not request.user.profile.email_verified:
            send_action_email(request.user,request)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


@login_required
def register_retailer(request):
    current_user = request.user

    if request.method == 'POST':
        retailer_form = RetailerForm(request.POST)

        if retailer_form.is_valid():
            new_retailer = retailer_form.save(commit=False)
            new_retailer.user = current_user
            new_retailer.save()

            current_user.linked = True
            current_user.save()

            user_profile = Profile.objects.filter(user=current_user).first()
            user_profile.linked = True
            user_profile.save()

            return render(request, 'account/verifying_you.html',{'new_retailer':new_retailer,'current_user':current_user})

    else:
        retailer_form = RetailerForm()

    return render(request,'account/get_verified_retailer.html',{'retailer_form':retailer_form})


def generate_qr(new_supplier):
# taking image which user wants
# in the QR code center

    BASE_DIR = Path(__file__).resolve().parent.parent
    Logo_link = 'static/images/faviconbg4.png'

    logo = Image.open(Logo_link)

# taking base width
    basewidth = 100

# adjust image size
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(
	error_correction=qrcode.constants.ERROR_CORRECT_H)


# taking url or text
    url = 'vistaartrade.com/'+'supplier/'+ str(new_supplier.id)

# adding URL or text to QRcode
    QRcode.add_data(url)

# generating QR code
    QRcode.make()

# taking color name from user
    QRcolor = '#00917c'

# adding color to QR code
    QRimg = QRcode.make_image(
	fill_color=QRcolor, back_color="white").convert('RGB')

# set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
	        (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)


    destination = ''.join(['media/suppliers/',new_supplier.company_name,'/','qr_code.png'])
    # save the QR code generated
    QRimg.save(destination)

    new_supplier.qr_code = ''.join(['suppliers/',new_supplier.company_name,'/','qr_code.png'])
    new_supplier.save()

    print('QR code generated!')


@login_required
def register_supplier(request):
    current_user = request.user

    if request.method == 'POST':
        supplier_form = SupplierForm(request.POST)
        print(request.POST)


        if supplier_form.is_valid():
            new_supplier = supplier_form.save(commit=False)
            new_supplier.user = current_user

            new_supplier.save()
    
            path = os.path.join(MEDIA_ROOT, 'suppliers/', new_supplier.company_name)

            os.makedirs(path,exist_ok=True)

            generate_qr(new_supplier)
            

            current_user.linked = True
            current_user.save()

            user_profile = Profile.objects.filter(user=current_user).first()
            user_profile.linked = True
            user_profile.save()

            return render(request, 'account/verifying_you.html',{'new_supplier':new_supplier,'current_user':current_user})

    else:
        supplier_form = SupplierForm()

    return render(request,'account/get_verified_supplier.html',{'supplier_form':supplier_form})


@login_required
def edit_company_info(request):
    if request.method == 'POST':
        company_info_form = EditCompanyInfoForm(instance=request.user.supplier,
                                 data=request.POST)
        if company_info_form.is_valid():
            company_info_form.save()
    else:
        company_info_form = EditCompanyInfoForm(instance=request.user.supplier)
    return render(request,
                  'dashboard/edit_company_info.html',
                  {'company_info_form': company_info_form})


@login_required
def edit_business_profile(request):
    if request.method == 'POST':
        business_profile_form = EditBusinessProfileForm(instance=request.user.supplier,
                                 data=request.POST)
        if business_profile_form.is_valid():
            business_profile_form.save()
    else:
        business_profile_form = EditBusinessProfileForm(instance=request.user.supplier)
    return render(request,
                  'dashboard/edit_company_info.html',
                  {'company_info_form': business_profile_form})


@login_required
def change_password(request):
    if request.method == 'POST':
        change_password_form = MyPasswordChangeForm(user=request.user, data=request.POST)
        if change_password_form.is_valid():
            change_password_form.save()
            # This will update the session and we won't be logged out after changing the password
            update_session_auth_hash(request, change_password_form.user)
            messages.success(request, 'Your password has been updated!')
            return redirect('password_change')
        else:
            messages.success(request, 'Something went wrong. Please try again.')
            return redirect('password_change')
    else:
        change_password_form = MyPasswordChangeForm(user=request.user)
    context = {
               'change_password_form':change_password_form,
               }
    return render(request, 'account/password_change_form.html', context)
    

#Activation email - Verification
def activate_user(request,uidb64,token):
    
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
        
    except Exception as e:
        user = None
        
    if user and generate_token.check_token(user,token):
        user.profile.email_verified=True
        user.save()
        
        messages.add_message(request, messages.SUCCESS, 'Your account has been successfully activated!')
        
        return redirect(reverse('home'))
        
    return render(request,'account/activation-failed.html',{'curuser':user,'userid':uid})
        
        
        
        
        
        
    