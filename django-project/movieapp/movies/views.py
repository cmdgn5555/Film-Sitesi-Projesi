from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Movie, UserMovieInteraction, UserProfile, WatchedMovie, FavoriteMovie, Watchlist, Rating, Yorum, YorumSikayet, SikayetNedeni, Mesaj, Mesaj2, FriendRequest, Friendship, KullaniciTakibi, KullaniciEngelleme
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import UserProfileForm, RatingForm, YorumForm, SikayetFormu
from django.contrib import messages
from django.contrib.auth.models import User
from better_profanity import profanity
from datetime import datetime


# Create your views here.

#kategori_liste = ["macera", "romantik", "dram", "bilim kurgu"]
#film_liste = [

#    {
#        "id": 1,
#        "film_adi": "film 1",
#        "aciklama": "film 1 açıklama",
#        "resim": "1.jpg",
#        "anasayfa": True
#    },
#
#    {
#        "id": 2,
#        "film_adi": "film 2",
#        "aciklama": "film 2 açıklama",
#        "resim": "2.jpeg",
#        "anasayfa": True
#    },
#
#    {
#        "id": 3,
#        "film_adi": "film 3",
#        "aciklama": "film 3 açıklama",
#        "resim": "3.jpeg",
#        "anasayfa": False
#    },
#
#    {
#        "id": 4,
#        "film_adi": "film 4",
#        "aciklama": "film 4 açıklama",
#        "resim": "4.jpg",
#        "anasayfa": False
#    }
#]

profanity.load_censor_words()

def home(request):
    
    filmler_listesi = Movie.objects.filter(anasayfa=True)
    paginator = Paginator(filmler_listesi, 3)

    sayfa_numarasi = request.GET.get("sayfa", 1)
    sayfa_objesi = paginator.get_page(sayfa_numarasi)
    
    data = {
        "kategoriler": Category.objects.all(),
        "filmler": sayfa_objesi
    }

    if "basari_mesaji" in request.session:
        messages.info(request, request.session.pop("basari_mesaji"))
    
    return render(request, "movies/index.html", data) 







def movies(request):
    
    filmler_listesi = Movie.objects.all()
    paginator = Paginator(filmler_listesi, 3)

    sayfa_numarasi = request.GET.get("sayfa", 1)
    sayfa_objesi = paginator.get_page(sayfa_numarasi)

    data = {
        "kategoriler": Category.objects.all(),
        "filmler": sayfa_objesi
        
    }
    
    return render(request, "movies/movies.html", data)







# Herhangi bir filmin detay sayfasını içeren fonksiyonu tanımlıyoruz

def movie_detail(request, sluginfo):
    
    if not request.user.is_authenticated:
        messages.info(request, "Herhangi bir filmin detayını görmek için giriş yapınız 5 saniye sonra login sayfasına yönlendirileceksiniz")
        return redirect("anasayfa")
    
    movie = get_object_or_404(Movie, slug=sluginfo)
    movie.goruntulenme_sayisi += 1
    movie.save()

    user_rating = Rating.objects.filter(user=request.user, movie=movie).first()
    
    yorumlar = movie.comments.filter(parent__isnull=True).all()

    yanitlanan_yorum = None 
    
    if request.method == "GET" and "cevap" in request.GET:
        yanitlanan_yorum_id = request.GET.get("cevap")
        yanitlanan_yorum = get_object_or_404(Yorum, id=yanitlanan_yorum_id)

    
    if request.method == "POST":
        yorum_form = YorumForm(request.POST) 
        
        if yorum_form.is_valid():
            yorum = yorum_form.save(commit=False)
            yorum.user = request.user
            yorum.film = movie

            if profanity.contains_profanity(yorum.yorum_text):
                messages.warning(request, "Yorumunuzda yasaklı kelimeler bulunmaktadır. Yorumunuz yönetici tarafından silinebilir.")
                yorum.yorum_text = profanity.censor(yorum.yorum_text)

            yorum.save()
            
            messages.success(request, "Yorumunuz başarıyla eklendi.")
            return redirect('film_detay', sluginfo=movie.slug)
    else:
        rating_form = RatingForm()
        yorum_form = YorumForm() 
    

    data = {
        "movie": movie,
        "user_rating": user_rating,
        "rating_form": rating_form,
        "yorum_form": yorum_form,
        "yorumlar": yorumlar,
        "yanitlanan_yorum": yanitlanan_yorum
    }
    
    return render(request, "movies/details.html", data)







# Filmleri kategorilerine göre listeliyoruz

def movies_by_category(request, sluginfo):

    kategori = Category.objects.get(slug=sluginfo)
    
    data = {
        "filmler": kategori.filmler.all(),
        "kategoriler": Category.objects.all(),
        #"filmler": Movie.objects.filter(category__slug=sluginfo),
        "secilen_kategori": sluginfo
    }
    
    return render(request, "movies/movies.html", data)







# Arama çubuğunda bir filmi film adına yapım yılına yada başrol oyuncularına göre aratıyoruz

@login_required(login_url="/account/login")
def search_movie(request):
    
    query = request.GET.get('q') 
    
    if query:
       filmler = Movie.objects.filter(Q(film_adi__icontains=query) | Q(film_yapim_yili__icontains=query) | Q(basrol_oyunculari__icontains=query))
    
    else:
        filmler = Movie.objects.none()
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "partials/_film_arama_partial.html", {
            'filmler': filmler
        })

    return render(request, "movies/film_arama_sonuclari.html", {
        'filmler': filmler, 
        'sorgu': query
    })







# Bir film için like butonuna bastığımızda tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def like_movie(request, sluginfo):
    
    movie = get_object_or_404(Movie, slug=sluginfo)
    
    interaction = UserMovieInteraction.objects.get_or_create(user=request.user, movie=movie)[0]

    if not interaction.liked:
        movie.likes += 1
        interaction.liked = True
        
        if interaction.disliked:
            movie.dislikes -= 1
            interaction.disliked = False
                
        movie.save()
        
        interaction.save()

    return redirect(request.META.get("HTTP_REFERER"))







# Bir film için dislike butonuna bastığımızda tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def dislike_movie(request, sluginfo):
    
    movie = get_object_or_404(Movie, slug=sluginfo)
    
    interaction = UserMovieInteraction.objects.get_or_create(user=request.user, movie=movie)[0]

    if not interaction.disliked:
        movie.dislikes += 1
        interaction.disliked = True
        
        if interaction.liked:
            movie.likes -= 1
            interaction.liked = False
        
        movie.save()
        
        interaction.save()

    return redirect(request.META.get("HTTP_REFERER"))







# Bir kullanıcının profilinin görünümü için fonksiyonumuzu tanımlıyoruz

@login_required(login_url="/account/login")
def profile_view(request):
    
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not (profile.profile_picture and profile.biography):
            return render(request, "movies/profile_incomplete.html")
        
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    watched_movies = WatchedMovie.objects.filter(user=request.user)
    favorite_movies = FavoriteMovie.objects.filter(user=request.user)
    watchlist_movies = Watchlist.objects.filter(user=request.user)

    # Kullanıcıların engellenme durumu kontrolü
    users = User.objects.exclude(id=request.user.id)
    
    # Kullanıcıların engellendiği durumu tutacak liste
    user_block_status = []

    for user in users:
        is_blocked = KullaniciEngelleme.objects.filter(engelleyen=user, engellenen=request.user).exists()
        user_block_status.append((user, is_blocked))
    
    data = {
        'profilimiz': profile,
        'izlenilen_filmler': watched_movies,
        'favori_filmler': favorite_movies,
        'izlenecek_filmler': watchlist_movies,
        'users': users,
        'user_block_status': user_block_status
        
    }
    
    return render(request, 'movies/profile.html', data)







# Bir kullanıcının diğer kullanıcıların profillerini görüntüleyebilmesi için gerekli olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def other_users_profile_view(request, kullanici_id):
    
    kullanici = get_object_or_404(User, id=kullanici_id)

    if KullaniciEngelleme.objects.filter(engelleyen=kullanici, engellenen=request.user).exists():
       messages.warning(request, f"{kullanici.username} adlı kullanıcı sizi engellediği için bu kullanıcının profil sayfasını görüntüleyemezsiniz")
       return redirect('kullanici_listesi')
    
    profili = get_object_or_404(UserProfile, user=kullanici)
    
    izledigi_filmler = WatchedMovie.objects.filter(user=kullanici)
    
    favori_filmleri = FavoriteMovie.objects.filter(user=kullanici)
    
    izleyecegi_filmler = Watchlist.objects.filter(user=kullanici)

    data = {
        'kullanici': kullanici,
        'profili': profili,
        'izledigi_filmler': izledigi_filmler,
        'favori_filmleri': favori_filmleri,
        'izleyecegi_filmler': izleyecegi_filmler,
    }
    
    return render(request, 'movies/other_users_profile.html', data)







# Bir kullanıcının profilini düzenleyebilmesi için gerekli fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def edit_profile(request):
    
    profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profiliniz başarıyla güncellendi.")
            return redirect('profil_görünüm')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'movies/edit_profile.html', {'form': form})







# Bir kullanıcının profilindeki alanları sıfırlaması için tetiklenecek olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def reset_profile(request):
    if request.method == "POST":
        profile = UserProfile.objects.get(user=request.user)
        profile.biography = ""
        profile.profile_picture = None
        profile.email = ""
        profile.city = ""
        profile.country = ""
        profile.birthday = None
        profile.occupation = ""
        profile.education = ""
        profile.save()

        messages.success(request, "Profiliniz başarıyla sıfırlandı")
        
        return redirect("profil_düzenle")
    






# Bir kullanıcının izlediği filmler listesine film ekleyebilmesi için tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def add_watched_movie(request, sluginfo):
    
    if request.method == "POST":
        movie = Movie.objects.get(slug=sluginfo)
        
        
        # Eğer bir filmi izlediğim filmler listemize eklemek istiyorsak bu filmin izlenecek filmler listemizde olup olmadığını kontrol ediyoruz
        # Senaryomuzda bir filmi hem izlediğim filmler hemde izlenecek filmler listemize eklemenin önüne geçiyoruz
        
        if Watchlist.objects.filter(user=request.user, movie=movie).exists():
            messages.warning(request, f"{movie.film_adi} adlı film izlenecek filmler listenizde var. Filmi izlediğim filmler listenize ekleyebilmek için izlenecek filmler listenizden çıkarılmalısınız")
        
        else:

            if not WatchedMovie.objects.filter(user=request.user, movie=movie).exists():
                WatchedMovie.objects.create(user=request.user, movie=movie)
                messages.success(request, f"{movie.film_adi} adlı film izlediğim filmler listenize eklendi")
            else:
                messages.warning(request, f"{movie.film_adi} adlı film zaten izlediğim filmler listenizde var")
        
        return redirect("profil_görünüm")







# Bir kullanıcının izlediği filmler listesinden film silebilmesi için tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def remove_watched_movie(request, sluginfo):
    movie = get_object_or_404(Movie, slug=sluginfo)
    watched_movie = get_object_or_404(WatchedMovie, user=request.user, movie=movie)
    watched_movie.delete()
    messages.success(request, f"{movie.film_adi} adlı film izlediğim filmler listenizden kaldırıldı")
    
    return redirect("profil_görünüm")







# Bir kullanıcının izleyeceği filmler listesine film ekleyebilmesi için tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def add_to_watchlist(request, sluginfo):
    
    if request.method == "POST":
        movie = get_object_or_404(Movie, slug=sluginfo)

        
        # Eğer bir filmi izlenecek filmler listemize eklemek istiyorsak bu filmin izlediğim filmler listemizde olup olmadığını kontrol ediyoruz
        # Senaryomuzda bir filmi hem izlediğim filmler hemde izlenecek filmler listemize eklemenin önüne geçiyoruz

        if WatchedMovie.objects.filter(user=request.user, movie=movie).exists():
            messages.warning(request, f"{movie.film_adi} adlı film izlediğim filmler listenizde var. Filmi izlenecek filmler listenize ekleyebilmek için izlediğim filmler listenizden çıkarılmalısınız.")
        
        else:

            if not Watchlist.objects.filter(user=request.user, movie=movie).exists():
                Watchlist.objects.create(user=request.user, movie=movie)
                messages.success(request, f"{movie.film_adi} adlı film izlenecek filmler listenize eklendi")
            
            else:
                messages.warning(request, f"{movie.film_adi} adlı film zaten izlenecek filmler listenizde var")

        return redirect("profil_görünüm")
    






# Bir kullanıcının izleyeceği filmler listesinden film silebilmesi için tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def remove_watchlist(request, sluginfo):
    movie = get_object_or_404(Movie, slug=sluginfo)
    watchlist_movie = get_object_or_404(Watchlist, user=request.user, movie=movie)
    watchlist_movie.delete()
    messages.success(request, f"{movie.film_adi} adlı film izlenecek filmler listenizden kaldırıldı")
    
    return redirect("profil_görünüm")
    






# Bir kullanıcının favori filmler listesine film ekleyebilmesi için tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def add_favorite_movie(request, sluginfo):
    if request.method == "POST":
        movie = Movie.objects.get(slug=sluginfo)

        if not FavoriteMovie.objects.filter(user=request.user, movie=movie).exists():
            FavoriteMovie.objects.create(user=request.user, movie=movie)
            messages.success(request, f"{movie.film_adi} adlı film favori filmlerim listenize eklendi")
        else:
            messages.warning(request, f"{movie.film_adi} adlı film zaten favori filmlerim listenizde var")

        return redirect("profil_görünüm")







# Bir kullanıcının favori filmler listesinden film silebilmesi için tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def remove_favorite_movie(request, sluginfo):
    movie = get_object_or_404(Movie, slug=sluginfo)
    favorite_movie = get_object_or_404(FavoriteMovie, user=request.user, movie=movie)
    favorite_movie.delete()
    messages.success(request, f"{movie.film_adi} adlı film favori filmlerim listenizden kaldırıldı")
    
    return redirect("profil_görünüm")
    






# Bir kullanıcının bir filmi izlediği filmler, izleyeceği filmler yada favori filmler listesine ekleyebilmesi için 
# görüntülenmesi gereken filmler listesine ait fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def movie_list(request):
    movies = Movie.objects.all().order_by("id")
    paginator = Paginator(movies, 6)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    watched_movies = WatchedMovie.objects.filter(user=request.user)
    favorite_movies = FavoriteMovie.objects.filter(user=request.user)

    data = {
        "movies": page_obj,
        "watched_movies": watched_movies,
        "favorite_movies": favorite_movies,
       }

    return render(request, "movies/movies_list.html", data)







# Bir kullanıcının bir filme puan verebilmesi için gereken fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def rate_movie(request, sluginfo):
    
    movie = get_object_or_404(Movie, slug=sluginfo)

    if request.method == "POST":
        form = RatingForm(request.POST) 

        if form.is_valid():
            rating_value = form.cleaned_data["rating"]
            existing_rating = Rating.objects.filter(user=request.user, movie=movie).first()

            if existing_rating:
                existing_rating.rating = rating_value
                existing_rating.save()
                messages.success(request, f"{movie.film_adi} filmine verdiğiniz puan güncellendi.")
            
            else:
                Rating.objects.create(user=request.user, movie=movie, rating=rating_value)
                messages.success(request, f"{movie.film_adi} filmine puan verdiniz")
            
            return redirect("film_detay", sluginfo=movie.slug)
    
    else:
        form = RatingForm()
    
    data = {
        "movie": movie,
        "rating_form": form
    }

    return render(request, "movies/details.html", data)







# Bir kullanıcının yapmış olduğu yorumu silebilmesi için gereken fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def yorum_sil(request, id):
    
    yorum = get_object_or_404(Yorum, id=id)

    if yorum.user == request.user:
        yorum.delete()
        messages.success(request, "Yorumunuz başarıyla silindi")
    
    else:
        messages.error(request, "Bu yorumu silmeye yetkiniz yok")
    
    return redirect("film_detay", sluginfo=yorum.film.slug)







# Bir kullanıcının yapmış olduğu yorumu düzenleyebilmesi için gereken fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def yorum_duzenle(request, id):
    
    yorum = get_object_or_404(Yorum, id=id)
    
    if yorum.user != request.user:
        messages.error(request, "Bu yorumu düzenlemeye yetkiniz yok.")
        return redirect('film_detay', sluginfo=yorum.film.slug)

    
    if request.method == "POST":
        form = YorumForm(request.POST, instance=yorum)
        if form.is_valid():
            form.save()
            messages.success(request, "Yorumunuz başarıyla güncellendi.")
            return redirect('film_detay', sluginfo=yorum.film.slug)
    
    else:
        form = YorumForm(instance=yorum)

    return render(request, 'movies/yorum_duzenle.html', {'form': form, 'yorum': yorum})







# Bir kullanıcının diğer kullanıcıların yapmış olduğu yorum yada yorumlara like atabilmesi için gerekli fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def like_yorum(request, id):
    
    yorum = get_object_or_404(Yorum, id=id)
    
    if request.user in yorum.likes.all():
        yorum.likes.remove(request.user)
        messages.info(request, "Yoruma verdiğiniz Like geri çekildi")
    
    else:
        yorum.likes.add(request.user)
        messages.success(request, "Yoruma Like verdiniz")
        if request.user in yorum.dislikes.all():
            yorum.dislikes.remove(request.user)  # Beğendiği zaman beğenmeyi geri alır.
    
    return redirect('film_detay', sluginfo=yorum.film.slug)







# Bir kullanıcının diğer kullanıcıların yapmış olduğu yorum yada yorumlara dislike atabilmesi için gerekli fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def dislike_yorum(request, id):
    
    yorum = get_object_or_404(Yorum, id=id)
    
    if request.user in yorum.dislikes.all():
        yorum.dislikes.remove(request.user)
        messages.info(request, "Yoruma verdiğiniz Dislike geri çekildi")
    
    else:
        yorum.dislikes.add(request.user)
        messages.success(request, "Yoruma Dislike verdiniz")
        if request.user in yorum.likes.all():
            yorum.likes.remove(request.user) # Beğenmediği zaman beğenmeyi geri alır.
    
    return redirect('film_detay', sluginfo=yorum.film.slug)







# Bir kullanıcının diğer kullanıcıların yapmış olduğu yorum yada yorumları şikayet edebilmesi için gerekli fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def sikayet_yorum(request, id):
    
    yorum = get_object_or_404(Yorum, id=id)

    mevcut_sikayet = YorumSikayet.objects.filter(sikayet_eden=request.user, yorum=yorum).exists()

    if mevcut_sikayet:
        messages.warning(request, "Bu yorumu zaten daha önceden şikayet etmişsiniz")
        return redirect("film_detay", sluginfo=yorum.film.slug)

    if request.method == 'POST':
        form = SikayetFormu(request.POST)
        if form.is_valid():
            sikayet = form.save(commit=False)
            sikayet.sikayet_eden = request.user
            sikayet.yorum = yorum
            sikayet.save()
            yorum.sikayet_edenler.add(request.user)
            messages.success(request, 'Yorum başarıyla şikayet edildi.')
            return redirect('film_detay', sluginfo=yorum.film.slug)
    else:
        form = SikayetFormu()

    return render(request, 'movies/sikayet_yorum.html', {'form': form, 'yorum': yorum})







# Yöneticinin kullanıcılara uyarı mesajı gönderebilmesi için gerekli olan fonksiyonu tanımlıyoruz

def mesaj_gonder_view(request, kullanici_id):
    
    if request.method == 'POST':
        
        mesaj_text = request.POST.get('mesaj')
        
        Mesaj.objects.create(
            alici_id=kullanici_id,
            gonderen=request.user,
            mesaj=mesaj_text,
            konu="Bu bir uyarı mesajıdır"
        )
        messages.success(request, 'Mesaj başarıyla gönderildi.')
        return redirect('admin:movies_yorumsikayet_changelist')

    return render(request, 'admin/mesaj_gonder.html', {'kullanici_id': kullanici_id})







# Kullanıcıların birbirlerine mesaj gönderebilmesi için gerekli olan fonksiyonu tanımlıyoruz

def mesaj_gonder_view2(request, kullanici_id):
    
    if not request.user.is_authenticated:
        messages.warning(request, "Mesaj gönderebilmek için giriş yapmanız gerekmektedir")
        return redirect("giris")
    
    alici = get_object_or_404(User, id=kullanici_id)

    
    # Alıcı, bu kullanıcıyı engellemiş mi?
    if KullaniciEngelleme.objects.filter(engelleyen=alici, engellenen=request.user).exists():
        messages.warning(request, f"{alici.username} adlı kullanıcı sizi engellediği için bu kullanıcıya mesaj gönderemezsiniz.")
        return redirect("kullanici_listesi")

    
    if alici == request.user:
        messages.warning(request, "Kendinize mesaj gönderemezsiniz")
        return redirect("kullanici_listesi")

    
    if request.method == 'POST':
        konu = request.POST.get('konu')
        mesaj_text = request.POST.get('mesaj')
                                                                                                              
        
        if mesaj_text and konu:
            Mesaj2.objects.create(
                alici=alici,
                gonderen=request.user,
                konu=konu,
                mesaj=mesaj_text
            )
            messages.success(request, 'Mesaj başarıyla gönderildi.')
            return redirect('anasayfa')

    return render(request, 'movies/mesaj_gonder2.html', {'alici': alici})







# Siteye kayıtlı olan kullanıcıları görüntülemek için gerekli olan fonksiyonu tanımlıyoruz

def kullanici_listesi(request):
    
    if not request.user.is_authenticated:
        messages.warning(request, "Kullanıcıları görüntülemek için giriş yapmanız gerekmektedir")
        return redirect("giris")
    
    kullanici_listesi = User.objects.exclude(id=request.user.id)  # Oturum açan kullanıcıyı hariç tut

    kullanici_takip_durumu = []
    
    for kullanici in kullanici_listesi:
        takip_ediliyor_mu = KullaniciTakibi.objects.filter(takip_eden=request.user, takip_edilen=kullanici).exists()
        engellendi_mi = KullaniciEngelleme.objects.filter(engelleyen=request.user, engellenen=kullanici).exists()
        
        kullanici_takip_durumu.append((kullanici, takip_ediliyor_mu, engellendi_mi))
    
    return render(request, 'movies/kullanici_listesi.html', {'kullanici_takip_durumu': kullanici_takip_durumu})







# Bir kullanıcının kendisine yönetici tarafından gönderilen uyarı mesajı yada 
# uyarı mesajlarını görüntüleyebilmesi için gerekli olan fonksiyonu tanımlıyoruz

def uyari_mesajlarim(request):
    
    if not request.user.is_authenticated:
        messages.warning(request, "Uyarı mesajlarını görebilmek için lütfen giriş yapınız")
        return redirect("giris")
    
    uyari_mesajlari = Mesaj.objects.filter(alici=request.user)
    
    return render(request, 'movies/mesajlarım.html', {'uyari_mesajlari': uyari_mesajlari})







# Bir kullanıcının kendisine diğer kullanıcılar tarafından gönderilen mesajı yada
# mesajları görüntüleyebilmesi için gerekli olan fonksiyonu tanımlıyoruz

def gelen_mesajlarim(request):
    
    if not request.user.is_authenticated:
        messages.warning(request, "Gelen kutusundaki mesajları görebilmek için lütfen giriş yapınız")
        return redirect("giris")
    
    gelen_mesajlar = Mesaj2.objects.filter(alici=request.user)
    
    return render(request, 'movies/mesajlarım2.html', {'gelen_mesajlar': gelen_mesajlar})

 





# Bir kullanıcının diğer kullanıcılara gönderdiği mesajı yada
# mesajları görüntüleyebilmesi için gerekli olan fonksiyonu tanımlıyoruz

def gonderdigim_mesajlar(request):
    
    if not request.user.is_authenticated:
        messages.warning(request, "Giden kutusundaki mesajları görebilmek için lütfen giriş yapınız")
        return redirect("giris")
    
    gonderdigim_mesajlar = request.user.gonderen_mesajlari2.all() # Sisteme giriş yapan kullanıcının gönderdiği mesajlar
    
    return render(request, 'movies/gonderdigim_mesajlar.html', {'gonderdigim_mesajlar': gonderdigim_mesajlar})







# Bir kullanıcının diğer kullanıcılara arkadaşlık isteği gönderebilmesi için gerekli olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def send_friend_request(request, kullanici_id): 
    
    # İstek gönderilecek kullanıcıyı bul
    istek_alan = User.objects.get(id=kullanici_id)

    # Kullanıcıyı engelleyip engellemediğini kontrol et
    engelleme_kontrol = KullaniciEngelleme.objects.filter(engelleyen=request.user, engellenen=istek_alan).exists()
    if engelleme_kontrol:
        messages.error(request, f"{istek_alan.username} adlı kullanıcıyı engellediğiniz için bu kullanıcıya arkadaşlık isteği gönderemezsiniz.")
        return redirect('profil_görünüm') 

    # Zaten arkadaş olup olmadıklarını kontrol et
    if Friendship.objects.filter(user=request.user, friend=istek_alan).exists():
        messages.warning(request, f"{istek_alan.username} kullanıcısı ile zaten arkadaşsınız.")
        return redirect('profil_görünüm') 
    
    # Arkadaşlık isteğinin daha önce gönderilip gönderilmediğini kontrol et
    friend_request, created = FriendRequest.objects.get_or_create(sender=request.user, receiver=istek_alan)
    
    if created:
        messages.success(request, f"{istek_alan.username} kullanıcısına arkadaşlık isteği gönderdiniz.") 
    
    else:
        messages.warning(request, f"{istek_alan.username} kullanıcısına zaten bir arkadaşlık isteği gönderdiniz.")
    
    return redirect('profil_görünüm')







# Bir kullanıcının kendisine gönderilen arkadaşlık isteklerini görüntüleyebilmesi için gerekli olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def friend_requests(request):
    
    alinan_arkadaslik_istekleri = FriendRequest.objects.filter(receiver=request.user)
    
    return render(request, 'movies/friend_requests.html', {
        'alinan_arkadaslik_istekleri': alinan_arkadaslik_istekleri,
        })







# Bir kullanıcının kendisine gönderilen arkadaşlık isteği yada isteklerini kabul ettiği anda tetiklenen fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def accept_friend_request(request, istek_id): 
    
    # Arkadaşlık isteğini bul
    arkadaslik_istegi = get_object_or_404(FriendRequest, id=istek_id)
    
    if arkadaslik_istegi.receiver == request.user:
        istegi_gonderen = arkadaslik_istegi.sender

        
        # Arkadaşlık oluştur
        Friendship.objects.create(user=request.user, friend=istegi_gonderen)
        Friendship.objects.create(user=istegi_gonderen, friend=request.user)
        
        
        # İlgili diğer arkadaşlık isteğini sil (karşılıklı isteği)
        FriendRequest.objects.filter(sender=istegi_gonderen, receiver=request.user).delete()
        FriendRequest.objects.filter(sender=request.user, receiver=istegi_gonderen).delete()

        
        messages.success(request, f"{istegi_gonderen.username} adlı kullanıcı ile artık arkadaşsınız!")
        return redirect('anasayfa')
    
    
    else:
        messages.error(request, "Bu arkadaşlık isteğini kabul etme yetkiniz yok.")
        return redirect('anasayfa')
    






# Bir kullanıcının arkadaşlarını listelemek için gerekli olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def friends_view(request):
    
    # Giriş yapan kullanıcının arkadaşlarını listeleme
    arkadaslar = Friendship.objects.filter(user=request.user).values_list('friend')
    
    arkadaslar_listesi = User.objects.filter(id__in=arkadaslar)

    data = {
        'arkadaslar_listesi': arkadaslar_listesi,
    }
    return render(request, 'movies/friends.html', data)
        
 





# Bir kullanıcının kendisine gelen arkadaşlık isteği yada isteklerini reddettiği anda tetiklenecek olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def reject_friend_request(request, istek_id):
    
    arkadaslik_istegi = FriendRequest.objects.get(id=istek_id)
    
    if arkadaslik_istegi.receiver == request.user:
        arkadaslik_istegi.delete()
        messages.success(request, f"{arkadaslik_istegi.sender.username} kullanıcısının arkadaşlık isteğini reddettiniz.")
    
    return redirect('anasayfa')







# Bir kullanıcının hali hazırda arkadaş olduğu bir kullanıcıyı yada kullanıcıları
# arkadaşlıktan çıkardığı anda tetiklenecek olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def remove_friend(request, arkadas_id):
    
    try:
        # Hem kullanıcıyı hem de arkadaşını arkadaşlıktan çıkar
        arkadaslik = Friendship.objects.get(user=request.user, friend=arkadas_id)
        arkadas_ismi = arkadaslik.friend.username
        arkadaslik.delete()

        ters_arkadaslik = Friendship.objects.get(user=arkadas_id, friend=request.user)
        ters_arkadaslik.delete()

        messages.success(request, f"{arkadas_ismi} adlı kullanıcı arkadaşlarım listenizden başarıyla çıkarıldı.")
        return redirect('anasayfa')
    
    except Friendship.DoesNotExist:
        messages.error(request, "Arkadaş listenizde böyle bir kullanıcı bulunamadı.")







# Bir kullanıcının bir başka kullanıcıyı takip etmek için takip et butonuna bastığı anda tetiklenecek olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def takip_et(request, user_id): 
    
    takip_edilecek_kullanici = get_object_or_404(User, id=user_id)

    if KullaniciEngelleme.objects.filter(engelleyen=takip_edilecek_kullanici, engellenen=request.user).exists():
       messages.warning(request, f"{takip_edilecek_kullanici.username} adlı kullanıcı sizi engellediği için bu kullanıcıyı takip edemezsiniz")
       return redirect('kullanici_listesi')
    
    if takip_edilecek_kullanici != request.user:
        
        takip, created = KullaniciTakibi.objects.get_or_create(takip_eden=request.user, takip_edilen=takip_edilecek_kullanici)
        
        if created:
            messages.success(request, f"{takip_edilecek_kullanici.username} adlı kullanıcıyı takip ediyorsunuz.")
        else:
            messages.warning(request, "Zaten bu kullanıcıyı takip ediyorsunuz.")
    
    return redirect('kullanici_listesi')







# Bir kullanıcının hali hazırda takip ettiği kullanıcı yada kullanıcılar için 
# takipten çık butonuna bastığı anda tetiklenecek olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def takipten_cik(request, user_id):
    
    takipten_cikilacak_kullanici = get_object_or_404(User, id=user_id)
    
    KullaniciTakibi.objects.filter(takip_eden=request.user, takip_edilen=takipten_cikilacak_kullanici).delete()
    
    messages.success(request, f"{takipten_cikilacak_kullanici.username} adlı kullanıcıyı takipten çıktınız.")
    
    return redirect('kullanici_listesi')







# Bir kullanıcının takip ettiği diğer kullanıcıları görüntüleyebilmesi için gerekli olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def takip_ettiklerim(request):

    # Engellediğiniz kullanıcıların ID'lerini alın
    engellediklerim = KullaniciEngelleme.objects.filter(engelleyen=request.user).values_list('engellenen', flat=True)
    
    # Engellediğiniz kullanıcıları hariç tutarak takip ettiklerinizi bulun
    takip_ettiklerim = KullaniciTakibi.objects.filter(takip_eden=request.user).exclude(takip_edilen__id__in=engellediklerim)
    
    return render(request, 'movies/takip_ettiklerim.html', {'takip_ettiklerim': takip_ettiklerim})







# Bir kullanıcının kendisini takip eden diğer kullanıcıları görüntüleyebilmesi için gerekli olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def beni_takip_edenler(request):
    
    # Sizi engelleyen kullanıcıların ID'lerini alın
    beni_engelleyenler = KullaniciEngelleme.objects.filter(engellenen=request.user).values_list('engelleyen', flat=True)

    # Sizi engelleyen kullanıcıları hariç tutarak sizi takip edenleri bulun
    beni_takip_edenler = KullaniciTakibi.objects.filter(takip_edilen=request.user).exclude(takip_eden__id__in=beni_engelleyenler)
    
    return render(request, 'movies/beni_takip_edenler.html', {'beni_takip_edenler': beni_takip_edenler})







# Bir kullanıcının başka bir kullanıcıyı engellediği anda tetiklenecek olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def engelle(request, user_id):
    
    # Engellenecek kullanıcıyı bul
    engellenecek_kullanici = get_object_or_404(User, id=user_id)
    
    if engellenecek_kullanici != request.user:
        
        # Engelleme işlemini oluştur
        engelleme, created = KullaniciEngelleme.objects.get_or_create(engelleyen=request.user, engellenen=engellenecek_kullanici)
        
        if created:
            # Eğer arkadaşlık isteği varsa, sil
            FriendRequest.objects.filter(sender=request.user, receiver=engellenecek_kullanici).delete()
            FriendRequest.objects.filter(sender=engellenecek_kullanici, receiver=request.user).delete()

            # Eğer arkadaşlık ilişkisi varsa, sil
            Friendship.objects.filter(user=request.user, friend=engellenecek_kullanici).delete()
            Friendship.objects.filter(user=engellenecek_kullanici, friend=request.user).delete()
            
            # Eğer takip ilişkisi varsa, sil
            KullaniciTakibi.objects.filter(takip_eden=request.user, takip_edilen=engellenecek_kullanici).delete()
            KullaniciTakibi.objects.filter(takip_eden=engellenecek_kullanici, takip_edilen=request.user).delete()
            
            messages.success(request, f"{engellenecek_kullanici.username} adlı kullanıcıyı engellediniz.")
        
        else:
            messages.warning(request, "Bu kullanıcıyı zaten engellediniz.")
    
    return redirect('kullanici_listesi')







# Bir kullanıcının engellediği başka bir kullanıcı için engeli kaldırdığı anda tetiklenecek olan fonksiyonu tanımlıyoruz

@login_required(login_url="/account/login")
def engeli_kaldir(request, user_id):
    
    engeli_kaldirilacak_kullanici = get_object_or_404(User, id=user_id)
    
    KullaniciEngelleme.objects.filter(engelleyen=request.user, engellenen=engeli_kaldirilacak_kullanici).delete()
    
    messages.success(request, f"{engeli_kaldirilacak_kullanici.username} adlı kullanıcının engelini kaldırdınız.")
    
    return redirect('kullanici_listesi')













    






























