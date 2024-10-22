from django.contrib import admin
from .models import Category, Movie, Cast, UserMovieInteraction, UserProfile, WatchedMovie, FavoriteMovie, Watchlist, Rating, Yorum, YorumSikayet, SikayetNedeni, Mesaj, Mesaj2, FriendRequest, Friendship, KullaniciTakibi, KullaniciEngelleme
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse
from django.urls import path
from . import views
from django.utils import timezone
from datetime import timedelta

# Register your models here.



class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', "related_movies") # Admin panelinde listede gözükecek alanlar
    search_fields = ('name',) # Arama yapılabilecek alanlar

    def related_movies(self, obj):
        movies_list = "".join([f"<li>{mov.film_adi}</li>" for mov in obj.filmler.all()])
        return mark_safe(movies_list)
    related_movies.short_description = "Filmler"
    
        





class MovieAdmin(admin.ModelAdmin):
    list_display = ("film_adi", "film_yapim_yili", "anasayfa", "basrol_oyunculari", "slug", "selected_categories")
    list_editable = ("anasayfa",)
    search_fields = ("film_adi", "film_yapim_yili", "basrol_oyunculari", "category")
    readonly_fields = ("slug",)
    list_filter = ("anasayfa","categories")

    def selected_categories(self, obj):
        html = "<ul>"

        for category in obj.categories.all():
            html += "<li>" + category.name + "</li>"
        
        html += "</ul>"
        
        return mark_safe(html)
        






class CastAdmin(admin.ModelAdmin):
    list_display = ("isim", "resim")







class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "biography", "hesap_donduruldu", "hesap_dondurulma_bitis_zamani")
    search_fields = ("user__username", "biography")
    actions = ['hesap_donduralım']


    def hesap_donduralım(self, request, secilenler):
        """ Seçilen kullanıcıları 1 günlüğüne dondur """
        for profil in secilenler:
            profil.hesap_dondur(sure_saat=24)  # Hesabı 1 gün (24 saat) dondur
        self.message_user(request, "Seçilen kullanıcıların hesapları 1 günlüğüne donduruldu.")
    







class WatchedMovieAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'watched_date')
    list_filter = ('user', 'movie', 'watched_date')
    search_fields = ('user__username', 'movie__film_adi')







class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_date')
    list_filter = ('user', 'movie', 'added_date')
    search_fields = ('user__username', 'movie__film_adi')







class FavoriteMovieAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_date')
    list_filter = ('user', 'movie', 'added_date')
    search_fields = ('user__username', 'movie__film_adi')







class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "rating", "rated_date")
    list_filter = ("movie", "rating")
    search_fields = ("user__username", "movie__film_adi")
    ordering = ["-rated_date"]







class YorumAdmin(admin.ModelAdmin):
    list_display = ("user", "film", "yorum_text", "created_at", "total_likes", "total_dislikes", "liked_users", "disliked_users", "sikayet_sayisi", "sikayet_edenleri_goster", "parent")
    list_filter = ("user", "film", "likes", "dislikes")
    search_fields = ("user__username",)
    ordering = ("-created_at",)


    def liked_users(self, obj):
        return ", ".join([kullanici.username for kullanici in obj.likes.all()])

    
    def disliked_users(self, obj):
        return ", ".join([kullanici.username for kullanici in obj.dislikes.all()])
    

    def sikayet_sayisi(self, obj):
        return obj.sikayet_edenler.count()
    
    
    def sikayet_edenleri_goster(self, obj):
        return ", ".join([kullanici.username for kullanici in obj.sikayet_edenler.all()])







class YorumSikayetAdmin(admin.ModelAdmin):
    list_display = ('sikayet_eden', 'yorum', 'neden', 'sikayet_tarihi', 'yorum_sahibi', 'mesaj_gonder')
    list_filter = ('neden',)
    search_fields = ('sikayet_eden__username', 'neden__name')


    def yorum_sahibi(self, obj):
        return obj.yorum.user.username
    yorum_sahibi.short_description = 'Yorumun Sahibi'


    def mesaj_gonder(self, obj):
        url = reverse('admin:mesaj_gonder', args=[obj.yorum.user.id])
        return format_html(f"<a class='button' href='{url}'>Uyarı Gönder</a>")
    mesaj_gonder.short_description = 'Uyarı Mesajı Gönder'


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('mesaj-gonder/<int:kullanici_id>/', views.mesaj_gonder_view, name='mesaj_gonder'),
        ]
        return custom_urls + urls







class MesajAdmin(admin.ModelAdmin):
    list_display = ("konu", "gonderen", "alici", "tarih_metod")
    list_filter = ("gonderen", "alici", "olusturulma_tarihi")
    search_fields = ("konu", "gonderen__username", "alici__username")

    def tarih_metod(self, obj):
        return obj.olusturulma_tarihi.strftime('%Y-%m-%d %H:%M')
    tarih_metod.admin_order_field = "olusturulma_tarihi"







class Mesaj2Admin(admin.ModelAdmin):
    list_display = ("konu", "gonderen", "alici", "tarih_metod_2")
    list_filter = ("gonderen", "alici", "tarih")
    search_fields = ("konu", "gonderen__username", "alici__username")

    def tarih_metod_2(self, obj):
        return obj.tarih.strftime('%Y-%m-%d %H:%M')
    tarih_metod_2.admin_order_field = "tarih"







class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at') 
    search_fields = ('sender__username', 'receiver__username')

 





class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at')  # Admin panelinde hangi sütunlar gösterilecek
    search_fields = ('user__username', 'friend__username')  # Kullanıcı adlarına göre arama yapılabilir
    list_filter = ('created_at',)  # Tarihe göre filtreleme eklenebilir
    ordering = ('-created_at',)  # En son oluşturulan arkadaşlıklar üstte görünecek şekilde sıralanır







class KullaniciTakibiAdmin(admin.ModelAdmin):
    list_display = ("takip_eden", "takip_edilen", "created_at")
    list_filter = ("takip_eden", "takip_edilen")
    search_fields = ("takip_eden__username", "takip_edilen__username")







class KullaniciEngellemeAdmin(admin.ModelAdmin):
    list_display = ("engelleyen", "engellenen", "created_at")
    list_filter = ("engelleyen", "engellenen")
    search_fields = ("engelleyen__username", "engellenen__username")

    
    




admin.site.register(Category, CategoryAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Cast, CastAdmin)
admin.site.register(UserMovieInteraction)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(WatchedMovie, WatchedMovieAdmin)
admin.site.register(FavoriteMovie, FavoriteMovieAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Yorum, YorumAdmin)
admin.site.register(YorumSikayet, YorumSikayetAdmin)
admin.site.register(SikayetNedeni) 
admin.site.register(Mesaj, MesajAdmin)
admin.site.register(Mesaj2, Mesaj2Admin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(KullaniciTakibi, KullaniciTakibiAdmin)
admin.site.register(KullaniciEngelleme, KullaniciEngellemeAdmin)