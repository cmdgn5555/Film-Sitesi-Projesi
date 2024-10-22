from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import LoginForm
from django.contrib import messages
from movies.models import UserProfile

# Create your views here.


def login_request(request):
    if request.user.is_authenticated:
        return redirect("anasayfa")
    
    # Başarısız giriş denemelerini takip ediyoruz 
    attempt_count = request.session.get("girisim_sayisi", 0)
    last_attempt_time_str = request.session.get("son_girisim_zamani")
    
    # Giriş denemeleri arasındaki süreyi kontrol et
    if last_attempt_time_str:
        last_attempt_time = datetime.fromisoformat(last_attempt_time_str)
        time_diff = timezone.now() - last_attempt_time
        
        if time_diff < timedelta(seconds=60):
            remaining_time = 60 - int(time_diff.total_seconds())
            return render(request, "account/login.html", {
                "error1": f"Üç kere yanlış kullanıcı adı veya şifre girdiğiniz için {remaining_time} saniye bekleyin",
                "remaining_time": remaining_time,
                "form": LoginForm()
            })
        
        else:
            request.session["son_girisim_zamani"] = None
            attempt_count = 0
            
            
    
    # 3 başarısız giriş denemesinden sonra Captcha'yı göster
    show_captcha = attempt_count >= 3
    
    if request.method == "POST":

        form = LoginForm(request.POST, show_captcha=show_captcha) # Captcha'yı sadece gerekirse gösteriyoruz
        
        if form.is_valid():
            kullanici_adi = form.cleaned_data["username"]
            sifre = form.cleaned_data["password"]

            kullanici = authenticate(request, username=kullanici_adi, password=sifre)

            if kullanici is not None:
                # Kullanıcı profilini kontrol ediyoruz
                try:
                    user_profile = UserProfile.objects.get(user=kullanici)
                    
                    # Hesap dondurulmuş mu kontrolü
                    if user_profile.hesap_donduruldu and not user_profile.hesap_dondurulma_suresi_bitti_mi():
                        remaining_time = user_profile.hesap_dondurulma_suresi_bitis_zamani()  # Kalan süreyi hesapla
                        messages.error(request, f"Hesabınız dondurulmuştur. Sisteme tekrar giriş yapabilmek için beklemeniz gereken süre : {remaining_time}")
                        return render(request, "account/login.html", {
                            "form": form
                        })

                except UserProfile.DoesNotExist:
                    # Kullanıcının profili yoksa devam et
                    pass


                login(request, kullanici)
                request.session["girisim_sayisi"] = 0
                request.session["basari_mesaji"] = "Sisteme başarıyla giriş yaptınız"
                return redirect("anasayfa")
        
            else:
                attempt_count += 1
                request.session["girisim_sayisi"] = attempt_count
           
                if attempt_count >= 3:
                    
                    return render(request, "account/login.html", {
                        "error2": "Üç kere yanlış kullanıcı adı veya şifre girdiğiniz için 60 saniye sonra tekrar sisteme giriş yapmayı deneyin",
                        "remaining_time": 60,
                        "form": form
                    })
            
                return render(request, "account/login.html", {
                    "error3": "Kullanıcı adı yada şifre yanlış",
                    "form": form
                })
            
        else:
            return render(request, "account/login.html", {
                "error4": "Form geçersiz, captcha alanını doğrulayın",
                "form": form
            })
    else:
        form = LoginForm(show_captcha=show_captcha)

    return render(request, "account/login.html", {
        "form": form
        
    })





def register_request(request):
    if request.user.is_authenticated:
        return redirect("anasayfa") 
    
    if request.method == "POST":
        kullanici_adi = request.POST["username"] 
        eposta = request.POST["email"]
        ad = request.POST["firstname"]
        soyad = request.POST["lastname"]
        sifre = request.POST["password"]
        sifre_tekrar = request.POST["re-password"]

        if sifre == sifre_tekrar:
            if User.objects.filter(username=kullanici_adi).exists():
                return render(request, "account/register.html", {
                    "error": "Böyle bir kullanıcı adı zaten var",
                    "kul_adi": kullanici_adi,
                    "mail": eposta,
                    "ad": ad,
                    "soyad": soyad})
            
            else:
                if User.objects.filter(email=eposta).exists():
                    return render(request, "account/register.html", {
                        "error": "Böyle bir eposta zaten var",
                        "kul_adi": kullanici_adi,
                        "mail": eposta,
                        "ad": ad,
                        "soyad": soyad})
                
                else:
                    kullanici_olustur = User.objects.create_user(
                                                    username=kullanici_adi,
                                                    email=eposta,
                                                    first_name=ad,
                                                    last_name=soyad,
                                                    password=sifre)
                    kullanici_olustur.save()
                    return redirect("giris")

                
        else:
            return render(request, "account/register.html", {
                "error": "Parola eşleşmiyor",
                "kul_adi": kullanici_adi,
                "mail": eposta,
                "ad": ad,
                "soyad": soyad})
    
    return render(request, "account/register.html")





def logout_request(request):
    logout(request)
    return redirect("anasayfa")



