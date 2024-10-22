from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import PermissionDenied



# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True, unique=True, db_index=True, editable=False)

    
    def __str__(self):
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Kategoriler"







class Cast(models.Model):
    isim = models.CharField(max_length=200)
    resim = models.ImageField(upload_to="cast")

    
    def __str__(self): 
        return self.isim
    
    class Meta:
        verbose_name_plural = "Oyuncular"
    
    





class Movie(models.Model):
    film_adi = models.CharField(max_length=200)
    aciklama = RichTextField()
    detay_aciklama = RichTextField(null=True)
    resim = models.ImageField(upload_to="movies")
    anasayfa = models.BooleanField(default=False)
    film_yapim_yili = models.DateField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, unique=True, db_index=True, editable=False)
    basrol_oyunculari = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    video = models.FileField(upload_to="videos", null=True, blank=True)
    oyuncular = models.ManyToManyField(Cast)
    #category = models.ForeignKey(Category, default=1, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, blank=True, related_name="filmler")
    goruntulenme_sayisi = models.IntegerField(default=0)
    vizyon_tarihi = models.DateField(null=True, blank=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    
    
    def __str__(self):
        return f"{self.film_adi}"
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.film_adi)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Filmler"







class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="profile-pictures", blank=True, null=True)
    biography = models.TextField(max_length=500, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    birthday = models.DateField(null=True, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=255, blank=True)
    hesap_donduruldu = models.BooleanField(default=False)
    hesap_dondurulma_bitis_zamani = models.DateTimeField(null=True, blank=True)
    
    
    
    def __str__(self):
        return self.user.username
    

    def hesap_dondur(self, sure_saat=24):
        """ Hesabı belirtilen süre (saat cinsinden) dondur """
        self.hesap_donduruldu = True
        self.hesap_dondurulma_bitis_zamani = timezone.now() + timedelta(hours=sure_saat)
        self.save()
    

    def hesap_dondurulma_suresi_bitis_zamani(self):
        """Hesabın dondurulma süresinin bitiş zamanını hesaplar"""
        if self.hesap_dondurulma_bitis_zamani:
            remaining_time = self.hesap_dondurulma_bitis_zamani - timezone.now()
            return str(remaining_time).split(".")[0]  # Kalan süreyi "HH:MM:SS" formatında döner
        return "Bilinmiyor"
    

    def hesap_dondurulma_suresi_bitti_mi(self):
        """Hesap dondurma süresi dolmuş mu kontrol eder"""
        if self.hesap_dondurulma_bitis_zamani:
            return timezone.now() > self.hesap_dondurulma_bitis_zamani
        return True
    
    class Meta:
        verbose_name_plural = "Kullanıcı Profilleri"



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)







class UserMovieInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    disliked = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username} - {self.movie.film_adi}"
    
    class Meta:
        verbose_name_plural = "Kullanıcı ve Film Etkileşimleri"







class WatchedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watched_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_date = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.user.username} watched {self.movie.film_adi}"
    
    class Meta:
        verbose_name_plural = "İzlenilen Filmler"







class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.user.username}'s favorite movie is {self.movie.film_adi}"
    
    class Meta:
        verbose_name_plural = "Favori Filmler"







class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.user.username} - {self.movie.film_adi}"
    
    class Meta:
        verbose_name_plural = "İzlenecek Filmler"
    






class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField()
    rated_date = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        unique_together = ("user", "movie")
    
    def __str__(self):
        return f"{self.user.username} rated {self.movie.film_adi}"
    
    class Meta:
        verbose_name_plural = "Derecelendirmeler"
    






class Yorum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    yorum_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 
    likes = models.ManyToManyField(User, related_name="yorum_likes", blank=True)
    dislikes = models.ManyToManyField(User, related_name="yorum_dislikes", blank=True)
    sikayet_edenler = models.ManyToManyField(User, related_name="sikayet_ettigi_yorumlar", blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    
    
    def total_likes(self):
        return self.likes.count() 
    
    
    def total_dislikes(self):
        return self.dislikes.count()
    

    def toplam_sikayet_sayisi(self):
        return self.sikayet_edenler.count()
    
   
    def __str__(self):
        return f'{self.user.username} - {self.film.film_adi}'
    
    
    class Meta:
        verbose_name_plural = "Yorumlar"







class SikayetNedeni(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Şikayet Nedenleri"







class YorumSikayet(models.Model):
    sikayet_eden = models.ForeignKey(User, on_delete=models.CASCADE)
    yorum = models.ForeignKey(Yorum, on_delete=models.CASCADE, related_name="sikayetler")
    neden = models.ForeignKey(SikayetNedeni, on_delete=models.CASCADE)
    sikayet_tarihi = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.sikayet_eden.username} - {self.yorum.user.username} - {self.neden.name}"
    
    class Meta:
        verbose_name_plural = "Yorum Şikayetleri"







# Yöneticinin kullanıcılara gönderdiği uyarı mesajları
class Mesaj(models.Model):
    alici = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alici_mesajlari")
    gonderen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="gonderen_mesajlari")
    konu = models.CharField(max_length=255, default="Uyarı Mesajı")
    mesaj = models.TextField()
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.alici.username} - {self.konu}"
    
    class Meta:
        verbose_name_plural = "Uyarı Mesajları"
    
    def save(self, *args, **kwargs):
        # Mesajı gönderen yönetici mi kontrol ediyoruz
        if not self.gonderen.is_superuser:
            raise PermissionDenied("Sadece yöneticiler uyarı mesajı gönderebilir.")
        super().save(*args, **kwargs)







# Kullanıcıların birbirlerine gönderdiği mesajlar
class Mesaj2(models.Model):
    alici = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alici_mesajlari2')
    gonderen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gonderen_mesajlari2')
    konu = models.CharField(max_length=255)
    mesaj = models.TextField()
    tarih = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f'{self.konu} - {self.gonderen.username} -> {self.alici.username}'
    
    class Meta:
        verbose_name_plural = "Genel Mesajlaşmalar"
    






class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name="sent_friend_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_friend_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.sender.username} ----> {self.receiver.username} (Accepted: {self.is_accepted})"
    
    class Meta:
        verbose_name_plural = "Arkadaşlık İstekleri"
    

   




class Friendship(models.Model):
    user = models.ForeignKey(User, related_name="friendship_creator_set", on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name="friend_set", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.user.username} and {self.friend.username} are friends"
    
    class Meta:
        verbose_name_plural = "Arkadaşlıklar"







class KullaniciTakibi(models.Model):
    takip_eden = models.ForeignKey(User, on_delete=models.CASCADE, related_name='takip_ediyor')  # Takip eden kullanıcı
    takip_edilen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='takip_ediliyor')  # Takip edilen kullanıcı
    created_at = models.DateTimeField(auto_now_add=True)  # Takip etme tarihi

    
    def __str__(self):
        return f"{self.takip_eden.username} adlı kullanıcı {self.takip_edilen.username} adlı kullanıcıyı takip ediyor"
    
    class Meta:
        unique_together = ('takip_eden', 'takip_edilen')
        verbose_name_plural = "Kullanıcı Takipleri"







class KullaniciEngelleme(models.Model):
    engelleyen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engelliyor')  # Engelleyen kullanıcı
    engellenen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engelleniyor')  # Engellenen kullanıcı
    created_at = models.DateTimeField(auto_now_add=True)  # Engelleme tarihi

    
    def __str__(self):
        return f"{self.engelleyen.username} adlı kullanıcı {self.engellenen.username} adlı kullanıcıyı engelledi"

    class Meta:
        unique_together = ('engelleyen', 'engellenen')
        verbose_name_plural = "Kullanıcı Engellemeleri" 



    



