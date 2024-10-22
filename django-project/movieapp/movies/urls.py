from django.urls import path
from . import views



urlpatterns = [
    path("", views.home, name="anasayfa"),
    path("home", views.home),
    path("movies", views.movies, name="filmler"),
    path("movies/<slug:sluginfo>", views.movie_detail, name="film_detay"),
    path("category/<slug:sluginfo>", views.movies_by_category, name="kategoriye_göre_filmler"),
    path("film_arama/", views.search_movie, name="film_arama"),
    path("like/<slug:sluginfo>/", views.like_movie, name="like_film"),
    path("dislike/<slug:sluginfo>/", views.dislike_movie, name="dislike_film"),
    path('profile/', views.profile_view, name='profil_görünüm'),
    path('profil/<int:kullanici_id>/', views.other_users_profile_view, name='kullanici_profil'),
    path('profile/edit/', views.edit_profile, name='profil_düzenle'),
    path("profile_reset/", views.reset_profile, name="profil_sıfırla"),
    path("add_watched_movie/<slug:sluginfo>/", views.add_watched_movie, name="izlenilen_filmi_ekle"),
    path("add_favorite_movie/<slug:sluginfo>/", views.add_favorite_movie, name="favorilere_film_ekle"),
    path('add_to_watchlist/<slug:sluginfo>/', views.add_to_watchlist, name='izlenecekler_listesine_ekle'),
    path("remove-watched/<slug:sluginfo>/", views.remove_watched_movie, name="izlenilen_film_sil"),
    path("remove-favorite/<slug:sluginfo>/", views.remove_favorite_movie, name="favori_film_sil"),
    path("remove-watchlist/<slug:sluginfo>/", views.remove_watchlist, name="izlenecek_film_sil"),
    path("movies_list/", views.movie_list, name="filmler_listesi"),
    path("movies/<slug:sluginfo>/rate", views.rate_movie, name='film_puanla'),
    path('yorum/sil/<int:id>/', views.yorum_sil, name='yorum_sil'),
    path('yorum/duzenle/<int:id>/', views.yorum_duzenle, name='yorum_duzenle'),
    path('yorum/<int:id>/like/', views.like_yorum, name='like_yorum'),
    path('yorum/<int:id>/dislike/', views.dislike_yorum, name='dislike_yorum'),
    path("yorum/<int:id>/sikayet/", views.sikayet_yorum, name="sikayet_yorum"),
    path('mesaj-gonder/<int:kullanici_id>/', views.mesaj_gonder_view2, name='mesaj_gonder2'),
    path('kullanici-listesi/', views.kullanici_listesi, name='kullanici_listesi'),
    path('uyari-mesajlarim/', views.uyari_mesajlarim, name='uyari_mesajlarim'),
    path('gelen-mesajlarim/', views.gelen_mesajlarim, name='gelen_mesajlarim'),
    path('gonderdigim-mesajlar/', views.gonderdigim_mesajlar, name='gonderdigim_mesajlar'),
    path('send_friend_request/<int:kullanici_id>/', views.send_friend_request, name='arkadaslik_istegi_gonder'),
    path('friend_requests/', views.friend_requests, name='arkadaslik_istekleri'),
    path('accept_friend_request/<int:istek_id>/', views.accept_friend_request, name='arkadaslik_istegi_kabul_et'),
    path('reject_friend_request/<int:istek_id>/', views.reject_friend_request, name='arkadaslik_istegi_reddet'),
    path('friends/', views.friends_view, name='arkadaslar'),  
    path('remove_friend/<int:arkadas_id>/', views.remove_friend, name='arkadas_sil'),
    path('takip-et/<int:user_id>/', views.takip_et, name='takip_et'),
    path('takipten-cik/<int:user_id>/', views.takipten_cik, name='takipten_cik'),
    path('takip-ettiklerim/', views.takip_ettiklerim, name='takip_ettiklerim'),
    path('beni-takip-edenler/', views.beni_takip_edenler, name='beni_takip_edenler'),
    path('engelle/<int:user_id>/', views.engelle, name='engelle'),
    path('engeli-kaldir/<int:user_id>/', views.engeli_kaldir, name='engeli_kaldir'),
]



