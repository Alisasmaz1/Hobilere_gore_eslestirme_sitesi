from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory,send_file
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import uuid 
from esleme_algoritma import GelismisHibritEslesmeMotoru

eslesme_motoru = None

def motor_baslat():
    global eslesme_motoru
    
    if eslesme_motoru is None:
        print("🚀 Eşleşme motoru başlatılıyor...")
        eslesme_motoru = GelismisHibritEslesmeMotoru(DB_CONFIG)
        basarili = eslesme_motoru.model_egit()
        
        if basarili:
            print("✅ Motor başarıyla eğitildi!")
        else:
            print("❌ Motor eğitimi başarısız!")
        
        return basarili
    
    return True
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ali173422',
    'database': 'esleme_sistemi'
}

def veritabani_baglantisi():
    """MySQL veritabanına bağlan"""
    try:
        baglanti = mysql.connector.connect(**DB_CONFIG)
        if baglanti.is_connected():
            return baglanti
    except Error as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return None


uygulama = Flask(__name__)
uygulama.secret_key = 'gizli-anahtar-buraya-rastgele-yaz'

GMAIL_ADRES = "alisasmazsaid@gmail.com"
GMAIL_SIFRE = "shvp qmaz yevh ujrg"


kullanici_verileri = {}
dogrulama_kodlari = {}


filmler = [
    {'id': 1, 'isim': 'The Shawshank Redemption', 'afis': 'https://image.tmdb.org/t/p/w500/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg'},
    {'id': 2, 'isim': 'The Godfather', 'afis': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg'},
    {'id': 3, 'isim': 'The Dark Knight', 'afis': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg'},
    {'id': 4, 'isim': 'Pulp Fiction', 'afis': 'https://image.tmdb.org/t/p/w500/vQWk5YBFWF4bZaofAbv0tShwBvQ.jpg'},
    {'id': 5, 'isim': 'Forrest Gump', 'afis': 'https://image.tmdb.org/t/p/w500/saHP97rTPS5eLmrLQEcANmKrsFl.jpg'},
    {'id': 6, 'isim': 'Inception', 'afis': 'https://image.tmdb.org/t/p/w500/xlaY2zyzMfkhk0HSC5VUwzoZPU1.jpg'},
    {'id': 7, 'isim': 'Fight Club', 'afis': 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'},
    {'id': 8, 'isim': 'The Matrix', 'afis': 'https://image.tmdb.org/t/p/w500/p96dm7sCMn4VYAStA6siNz30G1r.jpg'},
    {'id': 9, 'isim': 'Interstellar', 'afis': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg'},
    {'id': 10, 'isim': 'Goodfellas', 'afis': 'https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg'},
    {'id': 11, 'isim': "Schindler's List", 'afis': 'https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg'},        
    {'id': 12, 'isim': 'The Silence of the Lambs', 'afis': 'https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg'},
    {'id': 13, 'isim': 'Se7en', 'afis': 'https://image.tmdb.org/t/p/w1280/3qpOnTbxPK2HeHObBHttcvQHLGI.jpg'},
    {'id': 14, 'isim': 'Saving Private Ryan', 'afis': 'https://image.tmdb.org/t/p/w500/uqx37cS8cpHg8U35f9U5IBlrCV3.jpg'},
    {'id': 15, 'isim': 'The Green Mile', 'afis': 'https://image.tmdb.org/t/p/w500/o0lO84GI7qrG6XFvtsPOSV7CTNa.jpg'},
    {'id': 16, 'isim': 'American History X', 'afis': 'https://image.tmdb.org/t/p/w500/x2drgoXYZ8484lqyDj7L1CEVR4T.jpg'},
    {'id': 17, 'isim': 'The Usual Suspects', 'afis': 'https://image.tmdb.org/t/p/w500/99X2SgyFunJFXGAYnDv3sb9pnUD.jpg'},
    {'id': 18, 'isim': 'The Prestige', 'afis': 'https://image.tmdb.org/t/p/w500/bdN3gXuIZYaJP7ftKK2sU0nPtEA.jpg'},
    {'id': 19, 'isim': 'Gladiator', 'afis': 'https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg'},
    {'id': 20, 'isim': 'The Departed', 'afis': 'https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq20Qblg61T.jpg'},
    {'id': 21, 'isim': 'The Lord of the Rings: The Return of the King', 'afis': 'https://image.tmdb.org/t/p/w500/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg'},
    {'id': 22, 'isim': 'Spirited Away', 'afis': 'https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg'},
    {'id': 23, 'isim': 'Star Wars: Episode IV - A New Hope', 'afis': 'https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg'},
    {'id': 24, 'isim': 'The Pianist', 'afis': 'https://image.tmdb.org/t/p/w500/2hFvxCCWrTmCYwfy7yum0GKRi3Y.jpg'},
    {'id': 25, 'isim': 'Whiplash', 'afis': 'https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg'},
    {'id': 26, 'isim': 'Leon: The Professional', 'afis': 'https://image.tmdb.org/t/p/w500/bxB2q91nKYp8JNzqE7t7TWBVupB.jpg'},
    {'id': 27, 'isim': 'Django Unchained', 'afis': 'https://image.tmdb.org/t/p/w500/7oWY8VDWW7thTzWh3OKYRkWUlD5.jpg'},
    {'id': 28, 'isim': 'Memento', 'afis': 'https://image.tmdb.org/t/p/w500/fKTPH2WvH8nHTXeBYBVhawtRqtR.jpg'},
    {'id': 29, 'isim': 'Apocalypse Now', 'afis': 'https://image.tmdb.org/t/p/w500/gQB8Y5RCMkv2zwzFHbUJX3kAhvA.jpg'},
    {'id': 30, 'isim': 'The Wolf of Wall Street', 'afis': 'https://image.tmdb.org/t/p/w500/kW9LmvYHAaS9iA0tHmZVq8hQYoq.jpg'},
    {'id': 31, 'isim': 'Inglourious Basterds', 'afis': 'https://image.tmdb.org/t/p/w500/7sfbEnaARXDDhKm0CZ7D7uc2sbo.jpg'},
    {'id': 32, 'isim': 'The Truman Show', 'afis': 'https://image.tmdb.org/t/p/w500/vuza0WqY239yBXOadKlGwJsZJFE.jpg'},
    {'id': 33, 'isim': 'Shutter Island', 'afis': 'https://image.tmdb.org/t/p/w500/nrmXQ0zcZUL8jFLrakWc90IR8z9.jpg'},
    {'id': 34, 'isim': 'Mad Max: Fury Road', 'afis': 'https://image.tmdb.org/t/p/w500/hA2ple9q4qnwxp3hKVNhroipsir.jpg'},
    {'id': 35, 'isim': 'The Social Network', 'afis': 'https://image.tmdb.org/t/p/w500/n0ybibhJtQ5icDqTp8eRytcIHJx.jpg'},
    {'id': 36, 'isim': 'Her', 'afis': 'https://image.tmdb.org/t/p/w500/eCOtqtfvn7mxGl6nfmq4b1exJRc.jpg'},
    {'id': 37, 'isim': 'La La Land', 'afis': 'https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg'},
    {'id': 38, 'isim': 'Blade Runner 2049', 'afis': 'https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg'},
    {'id': 39, 'isim': 'The Irishman', 'afis': 'https://image.tmdb.org/t/p/w500/mbm8k3GFhXS0ROd9AD1gqYbIFbM.jpg'},
    {'id': 40, 'isim': '1917', 'afis': 'https://image.tmdb.org/t/p/w500/iZf0KyrE25z1sage4SYFLCCrMi9.jpg'},
    {'id': 41, 'isim': 'Joker', 'afis': 'https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg'},
    {'id': 42, 'isim': 'Dune', 'afis': 'https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg'},
    {'id': 43, 'isim': 'Tenet', 'afis': 'https://image.tmdb.org/t/p/w500/aCIFMriQh8rvhxpN1IWGgvH0Tlg.jpg'},
    {'id': 44, 'isim': 'The Imitation Game', 'afis': 'https://image.tmdb.org/t/p/w500/zSqJ1qFq8NXFfi7JeIYMlzyR0dx.jpg'},
    {'id': 45, 'isim': 'Arrival', 'afis': 'https://image.tmdb.org/t/p/w500/pEzNVQfdzYDzVK0XqxERIw2x2se.jpg'},
    {'id': 46, 'isim': 'Logan', 'afis': 'https://image.tmdb.org/t/p/w500/fnbjcRDYn6YviCcePDnGdyAkYsB.jpg'},
    {'id': 47, 'isim': 'Inside Out', 'afis': 'https://image.tmdb.org/t/p/w500/2H1TmgdfNtsKlU9jKdeNyYL5y8T.jpg'},
    {'id': 48, 'isim': 'Soul', 'afis': 'https://image.tmdb.org/t/p/w500/pEz5aROvfy5FBW1OTlrDO3VryWO.jpg'},
    {'id': 49, 'isim': 'Ratatouille', 'afis': 'https://image.tmdb.org/t/p/w500/t3vaWRPSf6WjDSamIkKDs1iQWna.jpg'},
    {'id': 50, 'isim': 'The Lion King', 'afis': 'https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg'},
    {'id': 51, 'isim': 'Braveheart', 'afis': 'https://image.tmdb.org/t/p/w500/or1gBugydmjToAEq7OZY0owwFk.jpg'},
    {'id': 52, 'isim': 'A Beautiful Mind', 'afis': 'https://image.tmdb.org/t/p/w500/rEIg5yJdNOt9fmX4P8gU9LeNoTQ.jpg'},
    {'id': 53, 'isim': 'Drive', 'afis': 'https://image.tmdb.org/t/p/w500/602vevIURmpDfzbnv5Ubi6wIkQm.jpg'},
    {'id': 54, 'isim': 'Hacksaw Ridge', 'afis': 'https://image.tmdb.org/t/p/w500/wuz8TjCIWR2EVVMuEfBnQ1vuGS3.jpg'},
    {'id': 55, 'isim': 'The Godfather Part II', 'afis': 'https://image.tmdb.org/t/p/w500/ecBRkXerAZqRRUfR8Lt3L3Dh6J5.jpg'},
    {'id': 56, 'isim': '12 Angry Men', 'afis': 'https://image.tmdb.org/t/p/w500/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg'},
    {'id': 57, 'isim': 'The Lord of the Rings: The Fellowship of the Ring', 'afis': 'https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg'},
    {'id': 58, 'isim': 'The Lord of the Rings: The Two Towers', 'afis': 'https://image.tmdb.org/t/p/w500/5VTN0pR8gcqV3EPUHHfMGnJYN9L.jpg'},
    {'id': 59, 'isim': 'Star Wars: Episode V - The Empire Strikes Back', 'afis': 'https://image.tmdb.org/t/p/w500/nNAeTmF4CtdSgMDplXTDPOpYzsX.jpg'},
    {'id': 60, 'isim': 'Back to the Future', 'afis': 'https://image.tmdb.org/t/p/w500/vN5B5WgYscRGcQpVhHl6p9DDTP0.jpg'},
    {'id': 61, 'isim': 'Terminator 2: Judgment Day', 'afis': 'https://image.tmdb.org/t/p/w500/jFTVD4XoWQTcg7wdyJKa8PEds5q.jpg'},
    {'id': 62, 'isim': 'Psycho', 'afis': 'https://image.tmdb.org/t/p/w500/yz4QVqPx3h1hD1DfqqQkCq3rmxW.jpg'},
    {'id': 63, 'isim': 'City of God', 'afis': 'https://image.tmdb.org/t/p/w500/k7eYdWvhYQyRQoU2TB2A2Xu2TfD.jpg'},
    {'id': 64, 'isim': 'Life Is Beautiful', 'afis': 'https://image.tmdb.org/t/p/w500/mfnkSeeVOBVheuyn2lo4tfmOPQb.jpg'},
    {'id': 65, 'isim': 'Star Wars: Episode VI - Return of the Jedi', 'afis': 'https://image.tmdb.org/t/p/w500/jQYlydvHm3kUix1f8prMucrplhm.jpg'},
    {'id': 66, 'isim': 'Alien', 'afis': 'https://image.tmdb.org/t/p/w500/vfrQk5IPloGg1v9Rzbh2Eg3VGyM.jpg'},
    {'id': 67, 'isim': 'Aliens', 'afis': 'https://image.tmdb.org/t/p/w500/r1x5JGpyqZU8PYhbs4UcrO1Xb6x.jpg'},
    {'id': 68, 'isim': '2001: A Space Odyssey', 'afis': 'https://image.tmdb.org/t/p/w500/ve72VxNqjGM69Uky4WTo2bK6rfq.jpg'},
    {'id': 69, 'isim': 'The Shining', 'afis': 'https://image.tmdb.org/t/p/w1280/yA02bdLNrd8Vbots5qiw9zAD2jC.jpg'},
    {'id': 70, 'isim': 'Wall-E', 'afis': 'https://image.tmdb.org/t/p/w1280/jzCpGwWHUwby14KPJJWla9ybY81.jpg'},
    {'id': 71, 'isim': 'Coco', 'afis': 'https://image.tmdb.org/t/p/w500/6Ryitt95xrO8KXuqRGm1fUuNwqF.jpg'},
    {'id': 72, 'isim': 'Avengers: Infinity War', 'afis': 'https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg'},
    {'id': 73, 'isim': 'Avengers: Endgame', 'afis': 'https://image.tmdb.org/t/p/w500/bR8ISy1O9XQxqiy0fQFw2BX72RQ.jpg'},
    {'id': 74, 'isim': 'Spider-Man: Into the Spider-Verse', 'afis': 'https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg'},
    {'id': 75, 'isim': 'Spider-Man: Across the Spider-Verse', 'afis': 'https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg'},
    {'id': 76, 'isim': 'Oppenheimer', 'afis': 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg'},
    {'id': 77, 'isim': 'The Dark Knight Rises', 'afis': 'https://image.tmdb.org/t/p/w500/hr0L2aueqlP2BYUblTTjmtn0hw4.jpg'},
    {'id': 78, 'isim': 'Batman Begins', 'afis': 'https://image.tmdb.org/t/p/w500/sPX89Td70IDDjVr85jdSBb4rWGr.jpg'},
    {'id': 79, 'isim': 'Reservoir Dogs', 'afis': 'https://image.tmdb.org/t/p/w500/xi8Iu6qyTfyZVDVy60raIOYJJmk.jpg'},
    {'id': 80, 'isim': 'Toy Story', 'afis': 'https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg'},
    {'id': 81, 'isim': 'Toy Story 3', 'afis': 'https://image.tmdb.org/t/p/w500/AbbXspMOwdvwWZgVN0nabZq03Ec.jpg'},
    {'id': 82, 'isim': 'Up', 'afis': 'https://image.tmdb.org/t/p/w500/mFvoEwSfLqbcWwFsDjQebn9bzFe.jpg'},
    {'id': 83, 'isim': 'Monsters, Inc.', 'afis': 'https://image.tmdb.org/t/p/w500/wFSpyMsp7H0ttERbxY7Trlv8xry.jpg'},
    {'id': 84, 'isim': 'Finding Nemo', 'afis': 'https://image.tmdb.org/t/p/w500/eHuGQ10FUzK1mdOY69wF5pGgEf5.jpg'},
    {'id': 85, 'isim': 'No Country for Old Men', 'afis': 'https://image.tmdb.org/t/p/w500/6d5XOczc226jECq0LIX0siKtgHR.jpg'},
    {'id': 86, 'isim': 'There Will Be Blood', 'afis': 'https://image.tmdb.org/t/p/w500/fa0RDkAlCec0STeMNAhPaF89q6U.jpg'},
    {'id': 87, 'isim': 'Prisoners', 'afis': 'https://image.tmdb.org/t/p/w500/jsS3a3ep2KyBVmmiwaz3LvK49b1.jpg'},
    {'id': 88, 'isim': 'Gone Girl', 'afis': 'https://image.tmdb.org/t/p/w500/ts996lKsxvjkO2yiYG0ht4qAicO.jpg'},
    {'id': 89, 'isim': 'Zodiac', 'afis': 'https://image.tmdb.org/t/p/w500/6YmeO4pB7XTh8P8F960O1uA14JO.jpg'},
    {'id': 90, 'isim': 'Eternal Sunshine of the Spotless Mind', 'afis': 'https://image.tmdb.org/t/p/w500/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg'},
    {'id': 91, 'isim': 'Amelie', 'afis': 'https://image.tmdb.org/t/p/w500/xMl2byt1R4fqGrG52fT2emLG3d0.jpg'},
    {'id': 92, 'isim': 'Cinema Paradiso', 'afis': 'https://image.tmdb.org/t/p/w500/gCI2AeMV4IHSewhJkzsur5MEp6R.jpg'},
    {'id': 93, 'isim': 'Grave of the Fireflies', 'afis': 'https://image.tmdb.org/t/p/w500/im6u58cPa9HlH5DqSnZGy0O37l5.jpg'},
    {'id': 94, 'isim': 'Princess Mononoke', 'afis': 'https://image.tmdb.org/t/p/w500/cMYCDADoLKLbB83g4WnJegaZimC.jpg'},
    {'id': 95, 'isim': "Howl's Moving Castle", 'afis': 'https://image.tmdb.org/t/p/w500/13kOl2v0nD2OLbVSHnHk8GUFEhO.jpg'},
    {'id': 96, 'isim': 'Your Name', 'afis': 'https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg'},
    {'id': 97, 'isim': 'Oldboy', 'afis': 'https://image.tmdb.org/t/p/w1280/pWDtjs568ZfOTMbURQBYuT4Qxka.jpg'},
    {'id': 98, 'isim': 'Train to Busan', 'afis': 'https://image.tmdb.org/t/p/w500/vNVFt6dtcqnI7hqa6LFBUibuFiw.jpg'},
    {'id': 99, 'isim': 'Taxi Driver', 'afis': 'https://image.tmdb.org/t/p/w500/ekstpH614fwDX8DUln1a2Opz0N8.jpg'},
    {'id': 100, 'isim': 'Raging Bull', 'afis': 'https://image.tmdb.org/t/p/w500/1WV7WlTS8LI1L5NkCgjWT9GSW3O.jpg'},
    {'id': 101, 'isim': 'Casino', 'afis': 'https://image.tmdb.org/t/p/w500/gziIkUSnYuj9ChCi8qOu2ZunpSC.jpg'},
    {'id': 102, 'isim': 'Scarface', 'afis': 'https://image.tmdb.org/t/p/w500/iQ5ztdjvteGeboxtmRdXEChJOHh.jpg'},
    {'id': 103, 'isim': 'Heat', 'afis': 'https://image.tmdb.org/t/p/w500/umSVjVdbVwtx5ryCA2QXL44Durm.jpg'},
    {'id': 104, 'isim': 'L.A. Confidential', 'afis': 'https://image.tmdb.org/t/p/w500/lWCgf5sD5FpMljjpkRhcC8pXcch.jpg'},
    {'id': 105, 'isim': 'Chinatown', 'afis': 'https://image.tmdb.org/t/p/w500/kZRSP3FmOcq0xnBulqpUQngJUXY.jpg'},
    {'id': 106, 'isim': 'Once Upon a Time in the West', 'afis': 'https://image.tmdb.org/t/p/w500/qbYgqOczabWNn2XKwgMtVrntD6P.jpg'},
    {'id': 107, 'isim': 'The Good, the Bad and the Ugly', 'afis': 'https://image.tmdb.org/t/p/w500/bX2xnavhMYjWDoZp1VM6VnU1xwe.jpg'},
    {'id': 108, 'isim': 'Unforgiven', 'afis': 'https://image.tmdb.org/t/p/w500/54roTwbX9fltg85zjsmrooXAs12.jpg'},
    {'id': 109, 'isim': 'Die Hard', 'afis': 'https://image.tmdb.org/t/p/w500/aJCpHDC6RoGz7d1Fzayl019xnxX.jpg'},
    {'id': 110, 'isim': 'Indiana Jones and the Raiders of the Lost Ark', 'afis': 'https://image.tmdb.org/t/p/w500/ceG9VzoRAVGwivFU403Wc3AHRys.jpg'},
    {'id': 111, 'isim': 'Indiana Jones and the Last Crusade', 'afis': 'https://image.tmdb.org/t/p/w500/sizg1AU8f8JDZX4QIgE4pjUMBvx.jpg'},
    {'id': 112, 'isim': 'Jurassic Park', 'afis': 'https://image.tmdb.org/t/p/w500/bRKmwU9eXZI5dKT11Zx1KsayiLW.jpg'},
    {'id': 113, 'isim': 'E.T. the Extra-Terrestrial', 'afis': 'https://image.tmdb.org/t/p/w500/an0nD6uq6byfxXCfk6lQBzdL2J1.jpg'},
    {'id': 114, 'isim': 'The Thing', 'afis': 'https://image.tmdb.org/t/p/w500/tzGY49kseSE9QAKk47uuDGwnSCu.jpg'},
    {'id': 115, 'isim': 'Blade Runner', 'afis': 'https://image.tmdb.org/t/p/w500/63N9uy8nd9j7Eog2axPQ8lbr3Wj.jpg'},
    {'id': 116, 'isim': 'Ex Machina', 'afis': 'https://image.tmdb.org/t/p/w500/dmJW8IAKHKxFNiUnoDR7JfsK7Rp.jpg'},
    {'id': 117, 'isim': 'Donnie Darko', 'afis': 'https://image.tmdb.org/t/p/w500/fhQoQfejY1hUcwyuLgpBrYs6uFt.jpg'},
    {'id': 118, 'isim': 'V for Vendetta', 'afis': 'https://image.tmdb.org/t/p/w500/piZOwjyk1g51oPHonc7zaQY3WOv.jpg'},
    {'id': 119, 'isim': 'The Sixth Sense', 'afis': 'https://image.tmdb.org/t/p/w500/vOyfUXNFSnaTk7Vk5AjpsKTUWsu.jpg'},
    {'id': 120, 'isim': 'Unbreakable', 'afis': 'https://image.tmdb.org/t/p/w500/mLuehrGLiK5zFCyRmDDOH6gbfPf.jpg'},
    {'id': 121, 'isim': 'Split', 'afis': 'https://image.tmdb.org/t/p/w500/lli31lYTFpvxVBeFHWoe5PMfW5s.jpg'},
    {'id': 122, 'isim': 'Get Out', 'afis': 'https://image.tmdb.org/t/p/w500/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg'},
    {'id': 123, 'isim': 'Hereditary', 'afis': 'https://image.tmdb.org/t/p/w500/hjlZSXM86wJrfCv5VKfR5DI2VeU.jpg'},
    {'id': 124, 'isim': 'Midsommar', 'afis': 'https://image.tmdb.org/t/p/w500/7LEI8ulZzO5gy9Ww2NVCrKmHeDZ.jpg'},
    {'id': 125, 'isim': 'The Witch', 'afis': 'https://image.tmdb.org/t/p/w500/zap5hpFCWSvdWSuPGAQyjUv2wAC.jpg'},
    {'id': 126, 'isim': 'A Quiet Place', 'afis': 'https://image.tmdb.org/t/p/w500/nAU74GmpUk7t5iklEp3bufwDq4n.jpg'},
    {'id': 127, 'isim': 'It', 'afis': 'https://image.tmdb.org/t/p/w500/9E2y5Q7WlCVNEhP5GiVTjhEhx1o.jpg'},
    {'id': 128, 'isim': 'The Exorcist', 'afis': 'https://image.tmdb.org/t/p/w500/5x0CeVHJI8tcDx8tUUwYHQSNILq.jpg'},
    {'id': 129, 'isim': "Rosemary's Baby", 'afis': 'https://image.tmdb.org/t/p/w500/uYgvlHceRFjAFbsNeMInYcLZLUb.jpg'},
    {'id': 130, 'isim': 'Halloween', 'afis': 'https://image.tmdb.org/t/p/w500/wijlZ3HaYMvlDTPqJoTCWKFkCPU.jpg'},
    {'id': 131, 'isim': 'Poltergeist', 'afis': 'https://image.tmdb.org/t/p/w500/4eMN3GANH5GG4kXdHkrTZEUuQ9M.jpg'},
    {'id': 132, 'isim': 'Scream', 'afis': 'https://image.tmdb.org/t/p/w500/lr9ZIrmuwVmZhpZuTCW8D9g0ZJe.jpg'},
    {'id': 133, 'isim': 'Titanic', 'afis': 'https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg'},
    {'id': 134, 'isim': 'Avatar', 'afis': 'https://image.tmdb.org/t/p/w500/gKY6q7SjCkAU6FqvqWybDYgUKIF.jpg'},
    {'id': 135, 'isim': 'Avatar: The Way of Water', 'afis': 'https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg'},
    {'id': 136, 'isim': 'Top Gun: Maverick', 'afis': 'https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg'},
    {'id': 137, 'isim': 'Everything Everywhere All At Once', 'afis': 'https://image.tmdb.org/t/p/w500/u68AjlvlutfEIcpmbYpKcdi09ut.jpg'},
    {'id': 138, 'isim': 'Knives Out', 'afis': 'https://image.tmdb.org/t/p/w500/pThyQovXQrw2m0s9x82twj48Jq4.jpg'},
    {'id': 139, 'isim': 'Glass Onion: A Knives Out Mystery', 'afis': 'https://image.tmdb.org/t/p/w500/vDGr1YdrlfbU9wxTOdpf3zChmv9.jpg'},
    {'id': 140, 'isim': 'Ford v Ferrari', 'afis': 'https://image.tmdb.org/t/p/w500/dR1Ju50iudrOh3YgfwkAU1g2HZe.jpg'},
    {'id': 141, 'isim': 'Spotlight', 'afis': 'https://image.tmdb.org/t/p/w500/8DPGG400FgaFWaqcv11n8mRd2NG.jpg'},
    {'id': 142, 'isim': 'Room', 'afis': 'https://image.tmdb.org/t/p/w500/2hHDMeYyZjbGWn0BeNH1cTMxuM7.jpg'},
    {'id': 143, 'isim': 'Green Book', 'afis': 'https://image.tmdb.org/t/p/w500/7BsvSuDQuoqhWmU2fL7W2GOcZHU.jpg'},
    {'id': 144, 'isim': 'Three Billboards Outside Ebbing, Missouri', 'afis': 'https://image.tmdb.org/t/p/w500/bRYLt8fV82tdVoDppSFTZIcJiLN.jpg'},
    {'id': 145, 'isim': 'Birdman', 'afis': 'https://image.tmdb.org/t/p/w1280/ueSmUbyr36raTlRKCLCT5WmvvwG.jpg'},
    {'id': 146, 'isim': 'The Grand Budapest Hotel', 'afis': 'https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg'},
    {'id': 147, 'isim': 'Moonrise Kingdom', 'afis': 'https://image.tmdb.org/t/p/w500/jH1qYtX1Ec4nZsoUJ0Y4DAZCaI.jpg'},
    {'id': 148, 'isim': 'Dead Poets Society', 'afis': 'https://image.tmdb.org/t/p/w500/erzbMlcNHOdx24AXOcn2ZKA7R1q.jpg'},
    {'id': 149, 'isim': 'Good Will Hunting', 'afis': 'https://image.tmdb.org/t/p/w500/z2FnLKpFi1HPO7BEJxdkv6hpJSU.jpg'},
    {'id': 150, 'isim': 'The Theory of Everything', 'afis': 'https://image.tmdb.org/t/p/w500/kJuL37NTE51zVP3eG5aGMyKAIlh.jpg'},
    {'id': 151, 'isim': 'Slumdog Millionaire', 'afis': 'https://image.tmdb.org/t/p/w500/5leCCi7ZF0CawAfM5Qo2ECKPprc.jpg'},
    {'id': 152, 'isim': 'Million Dollar Baby', 'afis': 'https://image.tmdb.org/t/p/w500/jcfEqKdWF1zeyvECPqp3mkWLct2.jpg'},
    {'id': 153, 'isim': 'Gran Torino', 'afis': 'https://image.tmdb.org/t/p/w500/zUybYvxWdAJy5hhYovsXtHSWI1l.jpg'},
    {'id': 154, 'isim': 'Mystic River', 'afis': 'https://image.tmdb.org/t/p/w500/hCHVDbo6XJGj3r2i4hVjKhE0GKF.jpg'},
    {'id': 155, 'isim': 'Catch Me If You Can', 'afis': 'https://image.tmdb.org/t/p/w500/sdYgEkKCDPWNU6KnoL4qd8xZ4w7.jpg'},
    {'id': 156, 'isim': 'The Terminal', 'afis': 'https://image.tmdb.org/t/p/w500/cPB3ZMM4UdsSAhNdS4c7ps5nypY.jpg'},
    {'id': 157, 'isim': 'Cast Away', 'afis': 'https://image.tmdb.org/t/p/w500/7lLJgKnAicAcR5UEuo8xhSMj18w.jpg'},
    {'id': 158, 'isim': 'Big Fish', 'afis': 'https://image.tmdb.org/t/p/w500/tjK063yCgaBAluVU72rZ6PKPH2l.jpg'},
    {'id': 159, 'isim': 'Edward Scissorhands', 'afis': 'https://image.tmdb.org/t/p/w500/e0FqKFvGPdQNWG8tF9cZBtev9Em.jpg'},
    {'id': 160, 'isim': 'Sweeney Todd: The Demon Barber of Fleet Street', 'afis': 'https://image.tmdb.org/t/p/w500/sAi3NFHYeuWOxZfEf3DonuoOytl.jpg'},
    {'id': 161, 'isim': 'Corpse Bride', 'afis': 'https://image.tmdb.org/t/p/w500/isb2Qow76GpqYmsSyfdMfsYAjts.jpg'},
    {'id': 162, 'isim': 'The Nightmare Before Christmas', 'afis': 'https://image.tmdb.org/t/p/w500/oQffRNjK8e19rF7xVYEN8ew0j7b.jpg'},
    {'id': 163, 'isim': 'Aladdin', 'afis': 'https://image.tmdb.org/t/p/w500/ykUEbfpkf8d0w49pHh0AD2KrT52.jpg'},
    {'id': 164, 'isim': 'Beauty and the Beast', 'afis': 'https://image.tmdb.org/t/p/w500/hUJ0UvQ5tgE2Z9WpfuduVSdiCiU.jpg'},
    {'id': 165, 'isim': 'Mulan', 'afis': 'https://image.tmdb.org/t/p/w500/bj3iSjLlkwHtJrPmvHXa8P7edI9.jpg'},
    {'id': 166, 'isim': 'Tarzan', 'afis': 'https://image.tmdb.org/t/p/w500/bTvHlcqiOjGa3lFtbrTLTM3zasY.jpg'},
    {'id': 167, 'isim': 'Hercules', 'afis': 'https://image.tmdb.org/t/p/w500/5X3VOy9lD44VclKsWTi8gHZGjhL.jpg'},
    {'id': 168, 'isim': 'Iron Man', 'afis': 'https://image.tmdb.org/t/p/w500/78lPtwv72eTNqFW9COBYI0dWDJa.jpg'},
    {'id': 169, 'isim': 'Guardians of the Galaxy', 'afis': 'https://image.tmdb.org/t/p/w500/r7vmZjiyZw9rpJMQJdXpjgiCOk9.jpg'},
    {'id': 170, 'isim': 'Captain America: The Winter Soldier', 'afis': 'https://image.tmdb.org/t/p/w500/tVFRpFw3xTedgPGqxW0AOI8Qhh0.jpg'},
    {'id': 171, 'isim': 'Thor: Ragnarok', 'afis': 'https://image.tmdb.org/t/p/w500/rzRwTcFvttcN1ZpX2xv4j3tSdJu.jpg'},
    {'id': 172, 'isim': 'Black Panther', 'afis': 'https://image.tmdb.org/t/p/w500/uxzzxijgPIY7slzFvMotPv8wjKA.jpg'},
    {'id': 173, 'isim': 'Deadpool', 'afis': 'https://image.tmdb.org/t/p/w500/3E53WEZJqP6aM84D8CckXx4pIHw.jpg'},
    {'id': 174, 'isim': 'Logan Lucky', 'afis': 'https://image.tmdb.org/t/p/w500/mQrhrBaaHvRfBQq0Px3HtVbH9iE.jpg'},
    {'id': 175, 'isim': 'Baby Driver', 'afis': 'https://image.tmdb.org/t/p/w500/tYzFuYXmT8LOYASlFCkaPiAFAl0.jpg'},
    {'id': 176, 'isim': 'Kingsman: The Secret Service', 'afis': 'https://image.tmdb.org/t/p/w500/r6q9wZK5a2K51KFj4LWVID6Ja1r.jpg'},
    {'id': 177, 'isim': 'Kick-Ass', 'afis': 'https://image.tmdb.org/t/p/w500/iHMbrTHJwocsNvo5murCBw0CwTo.jpg'},
    {'id': 178, 'isim': 'Superbad', 'afis': 'https://image.tmdb.org/t/p/w500/ek8e8txUyUwd2BNqj6lFEerJfbq.jpg'},
    {'id': 179, 'isim': 'The Hangover', 'afis': 'https://image.tmdb.org/t/p/w500/A0uS9rHR56FeBtpjVki16M5xxSW.jpg'},
    {'id': 180, 'isim': 'Tropic Thunder', 'afis': 'https://image.tmdb.org/t/p/w500/zAurB9mNxfYRoVrVjAJJwGV3sPg.jpg'},
    {'id': 181, 'isim': 'Zombieland', 'afis': 'https://image.tmdb.org/t/p/w500/dUkAmAyPVqubSBNRjRqCgHggZcK.jpg'},
    {'id': 182, 'isim': 'Shaun of the Dead', 'afis': 'https://image.tmdb.org/t/p/w500/dgXPhzNJH8HFTBjXPB177yNx6RI.jpg'},
    {'id': 183, 'isim': 'Hot Fuzz', 'afis': 'https://image.tmdb.org/t/p/w500/4Br5qhGrfIxlJmlnR2qfCRYioqq.jpg'},
    {'id': 184, 'isim': "The World's End", 'afis': 'https://image.tmdb.org/t/p/w500/kpglnOBYmKn0AkkWDzGxzKHDbds.jpg'},
    {'id': 185, 'isim': 'Scott Pilgrim vs. the World', 'afis': 'https://image.tmdb.org/t/p/w500/g5IoYeudx9XBEfwNL0fHvSckLBz.jpg'},
    {'id': 186, 'isim': 'Mean Girls', 'afis': 'https://image.tmdb.org/t/p/w500/2ZkuQXvVhh45uSvkBej4S7Ix1NJ.jpg'},
    {'id': 187, 'isim': 'Clueless', 'afis': 'https://image.tmdb.org/t/p/w500/8AwVTcgpTnmeOs4TdTWqcFDXEsA.jpg'},
    {'id': 188, 'isim': 'The Breakfast Club', 'afis': 'https://image.tmdb.org/t/p/w500/wM9ErA8UVdcce5P4oefQinN8VVV.jpg'},
    {'id': 189, 'isim': "Ferris Bueller's Day Off", 'afis': 'https://image.tmdb.org/t/p/w500/9LTQNCvoLsKXP0LtaKAaYVtRaQL.jpg'},
    {'id': 190, 'isim': 'Stand by Me', 'afis': 'https://image.tmdb.org/t/p/w500/vBv8iOFPLnXmtELUjcFc7OKHsR4.jpg'},
    {'id': 191, 'isim': 'Groundhog Day', 'afis': 'https://image.tmdb.org/t/p/w500/gCgt1WARPZaXnq523ySQEUKinCs.jpg'},
    {'id': 192, 'isim': 'The Big Lebowski', 'afis': 'https://image.tmdb.org/t/p/w500/9mprbw31MGdd66LR0AQKoDMoFRv.jpg'},
    {'id': 193, 'isim': 'Fargo', 'afis': 'https://image.tmdb.org/t/p/w500/rt7cpEr1uP6RTZykBFhBTcRaKvG.jpg'},
    {'id': 194, 'isim': 'No Time to Die', 'afis': 'https://image.tmdb.org/t/p/w500/iUgygt3fscRoKWCV1d0C7FbM9TP.jpg'},
    {'id': 195, 'isim': 'Mission: Impossible - Fallout', 'afis': 'https://image.tmdb.org/t/p/w500/AkJQpZp9WoNdj7pLYSj1L0RcMMN.jpg'},
    {'id': 196, 'isim': "Harry Potter and the Sorcerer's Stone", 'afis': 'https://image.tmdb.org/t/p/w500/wuMc08IPKEatf9rnMNXvIDxqP4W.jpg'},
    {'id': 197, 'isim': 'Harry Potter and the Chamber of Secrets', 'afis': 'https://image.tmdb.org/t/p/w500/sdEOH0992YZ0QSxgXNIGLq1ToUi.jpg'},
    {'id': 198, 'isim': 'Harry Potter and the Prisoner of Azkaban', 'afis': 'https://image.tmdb.org/t/p/w500/aWxwnYoe8p2d2fcxOqtvAtJ72Rw.jpg'},
    {'id': 199, 'isim': 'Harry Potter and the Goblet of Fire', 'afis': 'https://image.tmdb.org/t/p/w500/fECBtHlr0RB3foNHDiCBXeg9Bv9.jpg'},
    {'id': 200, 'isim': 'Harry Potter and the Order of the Phoenix', 'afis': 'https://image.tmdb.org/t/p/w500/5aOyriWkPec0zUDxmHFP9qMmBaj.jpg'},
    {'id': 201, 'isim': 'Harry Potter and the Half-Blood Prince', 'afis': 'https://image.tmdb.org/t/p/w500/z7uo9zmQdQwU5ZJHFpv2Upl30i1.jpg'},
    {'id': 202, 'isim': 'Harry Potter and the Deathly Hallows: Part 1', 'afis': 'https://image.tmdb.org/t/p/w500/iGoXIpQb7Pot00EEdwpwPajheZ5.jpg'},
    {'id': 203, 'isim': 'Harry Potter and the Deathly Hallows: Part 2', 'afis': 'https://image.tmdb.org/t/p/w500/c54HpQmuwXjHq2C9wmoACjxoom3.jpg'},
    {'id': 204, 'isim': 'The Hobbit: An Unexpected Journey', 'afis': 'https://image.tmdb.org/t/p/w500/yHA9Fc37VmpUA5UncTxxo3rTGVA.jpg'},
    {'id': 205, 'isim': 'The Hobbit: The Desolation of Smaug', 'afis': 'https://image.tmdb.org/t/p/w500/xQYiXsheRCDBA39DOrmaw1aSpbk.jpg'},
    {'id': 206, 'isim': 'The Hobbit: The Battle of the Five Armies', 'afis': 'https://image.tmdb.org/t/p/w500/xT98tLqatZPQApyRmlPL12LtiWp.jpg'},
    {'id': 207, 'isim': 'Pirates of the Caribbean: The Curse of the Black Pearl', 'afis': 'https://image.tmdb.org/t/p/w500/poHwCZeWzJCShH7tOjg8RIoyjcw.jpg'},
    {'id': 208, 'isim': "Pirates of the Caribbean: Dead Man's Chest", 'afis': 'https://image.tmdb.org/t/p/w500/lAhcKRt0ggTFkeFL95jrGQYaRXs.jpg'},
    {'id': 209, 'isim': 'The Hunger Games', 'afis': 'https://image.tmdb.org/t/p/w500/yXCbOiVDCxO71zI7cuwBRXdftq8.jpg'},
    {'id': 210, 'isim': 'The Hunger Games: Catching Fire', 'afis': 'https://image.tmdb.org/t/p/w500/vrQHDXjVmbYzadOXQ0UaObunoy2.jpg'},
    {'id': 211, 'isim': 'Twilight', 'afis': 'https://image.tmdb.org/t/p/w500/3Gkb6jm6962ADUPaCBqzz9CTbn9.jpg'},
    {'id': 212, 'isim': 'The Maze Runner', 'afis': 'https://image.tmdb.org/t/p/w500/ode14q7WtDugFDp78fo9lCsmay9.jpg'},
    {'id': 213, 'isim': 'Divergent', 'afis': 'https://image.tmdb.org/t/p/w500/aNh4Q3iuPKDMPi2SL7GgOpiLukX.jpg'},
    {'id': 214, 'isim': 'Fantastic Beasts and Where to Find Them', 'afis': 'https://image.tmdb.org/t/p/w500/fLsaFKExQt05yqjoAvKsmOMYvJR.jpg'},
    {'id': 215, 'isim': 'Chronicles of Narnia: The Lion, the Witch and the Wardrobe', 'afis': 'https://image.tmdb.org/t/p/w500/iREd0rNCjYdf5Ar0vfaW32yrkm.jpg'},
    {'id': 216, 'isim': 'John Wick', 'afis': 'https://image.tmdb.org/t/p/w500/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg'},
    {'id': 217, 'isim': 'John Wick: Chapter 2', 'afis': 'https://image.tmdb.org/t/p/w500/hXWBc0ioZP3cN4zCu6SN3YHXZVO.jpg'},
    {'id': 218, 'isim': 'John Wick: Chapter 3 - Parabellum', 'afis': 'https://image.tmdb.org/t/p/w500/ziEuG1essDuWuC5lpWUaw1uXY2O.jpg'},
    {'id': 219, 'isim': 'John Wick: Chapter 4', 'afis': 'https://image.tmdb.org/t/p/w500/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg'},
    {'id': 220, 'isim': 'Kill Bill: Vol. 1', 'afis': 'https://image.tmdb.org/t/p/w500/v7TaX8kXMXs5yFFGR41guUDNcnB.jpg'},
    {'id': 221, 'isim': 'Kill Bill: Vol. 2', 'afis': 'https://image.tmdb.org/t/p/w500/2yhg0mZQMhDyvUQ4rG1IZ4oIA8L.jpg'},
    {'id': 222, 'isim': 'Mission: Impossible', 'afis': 'https://image.tmdb.org/t/p/w500/z53D72EAOxGRqdr7KXXWp9dJiDe.jpg'},
    {'id': 223, 'isim': 'Mission: Impossible - Ghost Protocol', 'afis': 'https://image.tmdb.org/t/p/w500/eRZTGx7GsiKqPch96k27LK005ZL.jpg'},
    {'id': 224, 'isim': 'Mission: Impossible - Rogue Nation', 'afis': 'https://image.tmdb.org/t/p/w500/fRJLXQBHK2wyznK5yZbO7vmsuVK.jpg'},
    {'id': 225, 'isim': 'The Bourne Identity', 'afis': 'https://image.tmdb.org/t/p/w500/aP8swke3gmowbkfZ6lmNidu0y9p.jpg'},
    {'id': 226, 'isim': 'The Bourne Supremacy', 'afis': 'https://image.tmdb.org/t/p/w500/7IYGiDrquvX3q7e9PV6Pejs6b2g.jpg'},
    {'id': 227, 'isim': 'The Bourne Ultimatum', 'afis': 'https://image.tmdb.org/t/p/w500/15rMz5MRXFp7CP4VxhjYw4y0FUn.jpg'},
    {'id': 228, 'isim': 'Casino Royale', 'afis': 'https://image.tmdb.org/t/p/w500/lMrxYKKhd4lqRzwUHAy5gcx9PSO.jpg'},
    {'id': 229, 'isim': 'Quantum of Solace', 'afis': 'https://image.tmdb.org/t/p/w500/e3DXXLJHGqMx9yYpXsql1XNljmM.jpg'},
    {'id': 230, 'isim': 'Spectre', 'afis': 'https://image.tmdb.org/t/p/w500/zj8ongFhtWNsVlfjOGo8pSr7PQg.jpg'},
    {'id': 231, 'isim': 'Taken', 'afis': 'https://image.tmdb.org/t/p/w500/ognkaUSNgJe1a2pjB4UNdzEo5jT.jpg'},
    {'id': 232, 'isim': 'Nobody', 'afis': 'https://image.tmdb.org/t/p/w500/oBgWY00bEFeZ9N25wWVyuQddbAo.jpg'},
    {'id': 233, 'isim': 'The Equalizer', 'afis': 'https://image.tmdb.org/t/p/w500/9u4yW7yPA0BQ2pv9XwiNzItwvp8.jpg'},
    {'id': 234, 'isim': 'Man on Fire', 'afis': 'https://image.tmdb.org/t/p/w500/grCGLCcTHv9TChibzOwzUpykcjB.jpg'},
    {'id': 235, 'isim': 'Sicario', 'afis': 'https://image.tmdb.org/t/p/w500/lz8vNyXeidqqOdJW9ZjnDAMb5Vr.jpg'},
    {'id': 236, 'isim': 'Sicario: Day of the Soldado', 'afis': 'https://image.tmdb.org/t/p/w500/qcLYofEhNh51Sk1jUWjmKHLzkqw.jpg'},
    {'id': 237, 'isim': 'Collateral', 'afis': 'https://image.tmdb.org/t/p/w500/nV5316WUsVij8sVXLCF1g7TFitg.jpg'},
    {'id': 238, 'isim': 'Training Day', 'afis': 'https://image.tmdb.org/t/p/w500/bUeiwBQdupBLQthMCHKV7zv56uv.jpg'},
    {'id': 239, 'isim': 'American Psycho', 'afis': 'https://image.tmdb.org/t/p/w500/9uGHEgsiUXjCNq8wdq4r49YL8A1.jpg'},
    {'id': 240, 'isim': 'Nightcrawler', 'afis': 'https://image.tmdb.org/t/p/w500/j9HrX8f7GbZQm1BrBiR40uFQZSb.jpg'},
    {'id': 241, 'isim': 'Looper', 'afis': 'https://image.tmdb.org/t/p/w500/sNjL6SqErDBE8OUZlrDLkexfsCj.jpg'},
    {'id': 242, 'isim': 'Source Code', 'afis': 'https://image.tmdb.org/t/p/w500/nTr0lvAzeQmUjgSgDEHTJpnrxTz.jpg'},
    {'id': 243, 'isim': 'Edge of Tomorrow', 'afis': 'https://image.tmdb.org/t/p/w500/nBM9MMa2WCwvMG4IJ3eiGUdbPe6.jpg'},
    {'id': 244, 'isim': 'Oblivion', 'afis': 'https://image.tmdb.org/t/p/w500/eO3r38fwnhb58M1YgcjQBd3VNcp.jpg'},
    {'id': 245, 'isim': 'Minority Report', 'afis': 'https://image.tmdb.org/t/p/w500/qtgFcnwh9dAFLocsDk2ySDVS8UF.jpg'},
    {'id': 246, 'isim': 'Spider-Man', 'afis': 'https://image.tmdb.org/t/p/w500/gh4cZbhZxyTbgxQPxD0dOudNPTn.jpg'},
    {'id': 247, 'isim': 'Spider-Man 2', 'afis': 'https://image.tmdb.org/t/p/w500/aGuvNAaaZuWXYQQ6N2v7DeuP6mB.jpg'},
    {'id': 248, 'isim': 'Spider-Man 3', 'afis': 'https://image.tmdb.org/t/p/w500/qFmwhVUoUSXjkKRmca5yGDEXBIj.jpg'},
    {'id': 249, 'isim': 'The Amazing Spider-Man', 'afis': 'https://image.tmdb.org/t/p/w500/jexoNYnPd6vVrmygwF6QZmWPFdu.jpg'},
    {'id': 250, 'isim': 'X-Men', 'afis': 'https://image.tmdb.org/t/p/w500/ikA8UhYdTGpqbatFa93nIf6noSr.jpg'},
    {'id': 251, 'isim': 'X-Men 2', 'afis': 'https://image.tmdb.org/t/p/w500/bWMw0FMsY8DICgrQnrTSWbzEgtr.jpg'},
    {'id': 252, 'isim': 'X-Men: First Class', 'afis': 'https://image.tmdb.org/t/p/w500/hNEokmUke0dazoBhttFN0o3L7Xv.jpg'},
    {'id': 253, 'isim': 'X-Men: Days of Future Past', 'afis': 'https://image.tmdb.org/t/p/w500/tYfijzolzgoMOtegh1Y7j2Enorg.jpg'},
    {'id': 254, 'isim': 'The Wolverine', 'afis': 'https://image.tmdb.org/t/p/w500/t2wVAcoRlKvEIVSbiYDb8d0QqqS.jpg'},
    {'id': 255, 'isim': 'Iron Man 2', 'afis': 'https://image.tmdb.org/t/p/w500/6WBeq4fCfn7AN0o21W9qNcRF2l9.jpg'},
    {'id': 256, 'isim': 'Iron Man 3', 'afis': 'https://image.tmdb.org/t/p/w500/qhPtAc1TKbMPqNvcdXSOn9Bn7hZ.jpg'},
    {'id': 257, 'isim': 'Captain America: The First Avenger', 'afis': 'https://image.tmdb.org/t/p/w500/vSNxAJTlD0r02V9sPYpOjqDZXUK.jpg'},
    {'id': 258, 'isim': 'Captain America: Civil War', 'afis': 'https://image.tmdb.org/t/p/w500/rAGiXaUfPzY7CDEyNKUofk3Kw2e.jpg'},
    {'id': 259, 'isim': 'Thor', 'afis': 'https://image.tmdb.org/t/p/w500/prSfAi1xGrhLQNxVSUFh61xQ4Qy.jpg'},
    {'id': 260, 'isim': 'The Avengers', 'afis': 'https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg'},
    {'id': 261, 'isim': 'Avengers: Age of Ultron', 'afis': 'https://image.tmdb.org/t/p/w500/4ssDuvEDkSArWEdyBl2X5EHvYKU.jpg'},
    {'id': 262, 'isim': 'Guardians of the Galaxy Vol. 2', 'afis': 'https://image.tmdb.org/t/p/w500/y4MBh0EjBlMuOzv9axM4qJlmhzz.jpg'},
    {'id': 263, 'isim': 'Doctor Strange', 'afis': 'https://image.tmdb.org/t/p/w500/xf8PbyQcR5ucXErmZNzdKR0s8ya.jpg'},
    {'id': 264, 'isim': 'Ant-Man', 'afis': 'https://image.tmdb.org/t/p/w500/rQRnQfUl3kfp78nCWq8Ks04vnq1.jpg'},
    {'id': 265, 'isim': 'Man of Steel', 'afis': 'https://image.tmdb.org/t/p/w500/dksTL9NXc3GqPBRHYHcy1aIwjS.jpg'},
    {'id': 266, 'isim': 'Batman v Superman: Dawn of Justice', 'afis': 'https://image.tmdb.org/t/p/w500/5UsK3grJvtQrtzEgqNlDljJW96w.jpg'},
    {'id': 267, 'isim': 'Wonder Woman', 'afis': 'https://image.tmdb.org/t/p/w500/v4ncgZjG2Zu8ZW5al1vIZTsSjqX.jpg'},
    {'id': 268, 'isim': 'Aquaman', 'afis': 'https://image.tmdb.org/t/p/w500/ufl63EFcc5XpByEV2Ecdw6WJZAI.jpg'},
    {'id': 269, 'isim': 'Justice League', 'afis': 'https://image.tmdb.org/t/p/w500/eifGNCSDuxJeS1loAXil5bIGgvC.jpg'},
    {'id': 270, 'isim': 'Watchmen', 'afis': 'https://image.tmdb.org/t/p/w500/aVURelN3pM56lFM7Dgfs5TixcIf.jpg'},
    {'id': 271, 'isim': 'Constantine', 'afis': 'https://image.tmdb.org/t/p/w500/vPYgvd2MwHlxTamAOjwVQp4qs1W.jpg'},
    {'id': 272, 'isim': '300 Spartan', 'afis': 'https://image.tmdb.org/t/p/w500/h7Lcio0c9ohxPhSZg42eTlKIVVY.jpg'},
    {'id': 273, 'isim': 'Sin City', 'afis': 'https://image.tmdb.org/t/p/w500/i66G50wATMmPrvpP95f0XP6ZdVS.jpg'},
    {'id': 274, 'isim': 'Dredd', 'afis': 'https://image.tmdb.org/t/p/w500/wLx65gtGVnUFCxceHWGszcruCZj.jpg'},
    {'id': 275, 'isim': 'Elysium', 'afis': 'https://image.tmdb.org/t/p/w500/uiiXHBd9oUrtUa4YqZiAoy05cRz.jpg'},
    {'id': 276, 'isim': 'Chappie', 'afis': 'https://image.tmdb.org/t/p/w500/uuDUpzlMFomdSfNWlpEPS9nVZWV.jpg'},
    {'id': 277, 'isim': 'I Robot', 'afis': 'https://image.tmdb.org/t/p/w500/efwv6F2lGaghjPpBRSINHtoEiZB.jpg'},
    {'id': 278, 'isim': 'A.I. Artificial Intelligence', 'afis': 'https://image.tmdb.org/t/p/w500/8MZSGX5JORoO72EfuAEcejH5yHn.jpg'},
    {'id': 279, 'isim': 'The Martian', 'afis': 'https://image.tmdb.org/t/p/w500/3ndAx3weG6KDkJIRMCi5vXX6Dyb.jpg'},
    {'id': 280, 'isim': 'Gravity', 'afis': 'https://image.tmdb.org/t/p/w500/kZ2nZw8D681aphje8NJi8EfbL1U.jpg'},
    {'id': 281, 'isim': 'Moon', 'afis': 'https://image.tmdb.org/t/p/w500/mnYLkS2NB6676Whpl5VKU3J7oc7.jpg'},
    {'id': 282, 'isim': 'Sunshine', 'afis': 'https://image.tmdb.org/t/p/w500/3dmW9NWP80wnXln5IUoQTAmXbj5.jpg'},
    {'id': 283, 'isim': 'Contact', 'afis': 'https://image.tmdb.org/t/p/w500/bCpMIywuNZeWt3i5UMLEIc0VSwM.jpg'},
    {'id': 284, 'isim': 'Star Trek', 'afis': 'https://image.tmdb.org/t/p/w500/hN2ZtF3Uw6mhIHZiqL0SKzELtKn.jpg'},
    {'id': 285, 'isim': 'Star Trek Into Darkness', 'afis': 'https://image.tmdb.org/t/p/w500/Aim3kVNh1MPIxPEFeJrl9e9Uf1a.jpg'},
    {'id': 286, 'isim': 'Rise of the Planet of the Apes', 'afis': 'https://image.tmdb.org/t/p/w500/oqA45qMyyo1TtrnVEBKxqmTPhbN.jpg'},
    {'id': 287, 'isim': 'Dawn of the Planet of the Apes', 'afis': 'https://image.tmdb.org/t/p/w500/kScdQEwS9jPEdnO23XjGAtaoRcT.jpg'},
    {'id': 288, 'isim': 'War for the Planet of the Apes', 'afis': 'https://image.tmdb.org/t/p/w500/mMA1qhBFgZX8O36qPPTC016kQl1.jpg'},
    {'id': 289, 'isim': 'Ready Player One', 'afis': 'https://image.tmdb.org/t/p/w500/pU1ULUq8D3iRxl1fdX2lZIzdHuI.jpg'},
    {'id': 290, 'isim': 'Alita: Battle Angel', 'afis': 'https://image.tmdb.org/t/p/w500/xRWht48C2V8XNfzvPehyClOvDni.jpg'},
    {'id': 291, 'isim': 'Pacific Rim', 'afis': 'https://image.tmdb.org/t/p/w500/8wo4eN8dWKaKlxhSvBz19uvj8gA.jpg'},
    {'id': 292, 'isim': 'Transformers', 'afis': 'https://image.tmdb.org/t/p/w500/1P7w3AImoEOWJX7nn3fdaKDfEQA.jpg'},
    {'id': 293, 'isim': 'Shrek', 'afis': 'https://image.tmdb.org/t/p/w500/iB64vpL3dIObOtMZgX3RqdVdQDc.jpg'},
    {'id': 294, 'isim': 'Shrek 2', 'afis': 'https://image.tmdb.org/t/p/w500/2yYP0PQjG8zVqturh1BAqu2Tixl.jpg'},
    {'id': 295, 'isim': 'Kung Fu Panda', 'afis': 'https://image.tmdb.org/t/p/w500/wWt4JYXTg5Wr3xBW2phBrMKgp3x.jpg'},
    {'id': 296, 'isim': 'Kung Fu Panda 2', 'afis': 'https://image.tmdb.org/t/p/w500/A23nZfFBa7gFD40IsiV5gOadyIi.jpg'},
    {'id': 297, 'isim': 'How to Train Your Dragon', 'afis': 'https://image.tmdb.org/t/p/w500/q5pXRYTycaeW6dEgsCrd4mYPmxM.jpg'},
    {'id': 298, 'isim': 'How to Train Your Dragon 2', 'afis': 'https://image.tmdb.org/t/p/w500/d13Uj86LdbDLrfDoHR5aDOFYyJC.jpg'},
    {'id': 299, 'isim': 'Ice Age', 'afis': 'https://image.tmdb.org/t/p/w500/gLhHHZUzeseRXShoDyC4VqLgsNv.jpg'},
    {'id': 300, 'isim': 'Madagascar', 'afis': 'https://image.tmdb.org/t/p/w500/zMpJY5CJKUufG9OTw0In4eAFqPX.jpg'},
    {'id': 301, 'isim': 'Despicable Me', 'afis': 'https://image.tmdb.org/t/p/w500/9lOloREsAhBu0pEtU0BgeR1rHyo.jpg'},
    {'id': 302, 'isim': 'Minions', 'afis': 'https://image.tmdb.org/t/p/w500/dr02BdCNAUPVU07aOodwPYv6HCf.jpg'},
    {'id': 303, 'isim': 'The Incredibles', 'afis': 'https://image.tmdb.org/t/p/w500/2LqaLgk4Z226KkgPJuiOQ58wvrm.jpg'},
    {'id': 304, 'isim': 'Incredibles 2', 'afis': 'https://image.tmdb.org/t/p/w500/9lFKBtaVIhP7E2Pk0IY1CwTKTMZ.jpg'},
    {'id': 305, 'isim': 'Finding Dory', 'afis': 'https://image.tmdb.org/t/p/w500/3UVe8NL1E2ZdUZ9EDlKGJY5UzE.jpg'},
    {'id': 306, 'isim': 'Monsters University', 'afis': 'https://image.tmdb.org/t/p/w500/y7thwJ7z5Bplv6vwl6RI0yteaDD.jpg'},
    {'id': 307, 'isim': 'Frozen', 'afis': 'https://image.tmdb.org/t/p/w500/itAKcobTYGpYT8Phwjd8c9hleTo.jpg'},
    {'id': 308, 'isim': 'Frozen II', 'afis': 'https://image.tmdb.org/t/p/w500/mINJaa34MtknCYl5AjtNJzWj8cD.jpg'},
    {'id': 309, 'isim': 'Moana', 'afis': 'https://image.tmdb.org/t/p/w500/8IU5VxW5KaO5sxAphpSxNTYf7Rw.jpg'},
    {'id': 310, 'isim': 'Zootopia', 'afis': 'https://image.tmdb.org/t/p/w500/hlK0e0wAQ3VLuJcsfIYPvb4JVud.jpg'},
    {'id': 311, 'isim': 'Tangled', 'afis': 'https://image.tmdb.org/t/p/w500/ym7Kst6a4uodryxqbGOxmewF235.jpg'},
    {'id': 312, 'isim': 'Big Hero 6', 'afis': 'https://image.tmdb.org/t/p/w500/2mxS4wUimwlLmI1xp6QW6NSU361.jpg'},
    {'id': 313, 'isim': 'Wreck-It Ralph', 'afis': 'https://image.tmdb.org/t/p/w500/zWoIgZ7mgmPkaZjG0102BSKFIqQ.jpg'},
    {'id': 314, 'isim': 'Kubo and the Two Strings', 'afis': 'https://image.tmdb.org/t/p/w500/la6QA9tk4Foq8OBH2Dyh5dTcw6H.jpg'},
    {'id': 315, 'isim': 'Coraline', 'afis': 'https://image.tmdb.org/t/p/w500/4jeFXQYytChdZYE9JYO7Un87IlW.jpg'},
    {'id': 316, 'isim': 'Isle of Dogs', 'afis': 'https://image.tmdb.org/t/p/w500/m2q7oCHyH38y5bUiPWs6BI3T8Di.jpg'},
    {'id': 317, 'isim': 'Akira', 'afis': 'https://image.tmdb.org/t/p/w500/neZ0ykEsPqxamsX6o5QNUFILQrz.jpg'},
    {'id': 318, 'isim': 'Ghost in the Shell', 'afis': 'https://image.tmdb.org/t/p/w500/9gC88zYUBARRSThcG93MvW14sqx.jpg'},
    {'id': 319, 'isim': 'My Neighbor Totoro', 'afis': 'https://image.tmdb.org/t/p/w500/rtGDOeG9LzoerkDGZF9dnVeLppL.jpg'},
    {'id': 320, 'isim': 'Ponyo', 'afis': 'https://image.tmdb.org/t/p/w500/yp8vEZflGynlEylxEesbYasc06i.jpg'},
    {'id': 321, 'isim': "Kiki's Delivery Service", 'afis': 'https://image.tmdb.org/t/p/w500/Aufa4YdZIv4AXpR9rznwVA5SEfd.jpg'},
    {'id': 322, 'isim': 'Bohemian Rhapsody', 'afis': 'https://image.tmdb.org/t/p/w500/lHu1wtNaczFPGFDTrjCSzeLPTKN.jpg'},
    {'id': 323, 'isim': 'Rocketman', 'afis': 'https://image.tmdb.org/t/p/w500/f4FF18ia7yTvHf2izNrHqBmgH8U.jpg'},
    {'id': 324, 'isim': 'Elvis', 'afis': 'https://image.tmdb.org/t/p/w500/qBOKWqAFbveZ4ryjJJwbie6tXkQ.jpg'},
    {'id': 325, 'isim': "The King's Speech", 'afis': 'https://image.tmdb.org/t/p/w500/pVNKXVQFukBaCz6ML7GH3kiPlQP.jpg'},
    {'id': 326, 'isim': 'Darkest Hour', 'afis': 'https://image.tmdb.org/t/p/w500/xa6G3aKlysQeVg9wOb0dRcIGlWu.jpg'},
    {'id': 327, 'isim': 'Dunkirk', 'afis': 'https://image.tmdb.org/t/p/w500/b4Oe15CGLL61Ped0RAS9JpqdmCt.jpg'},
    {'id': 328, 'isim': 'The Revenant', 'afis': 'https://image.tmdb.org/t/p/w500/ji3ecJphATlVgWNY0B0RVXZizdf.jpg'},
    {'id': 329, 'isim': 'Black Swan', 'afis': 'https://image.tmdb.org/t/p/w500/viWheBd44bouiLCHgNMvahLThqx.jpg'},
    {'id': 330, 'isim': 'The Wrestler', 'afis': 'https://image.tmdb.org/t/p/w500/6OTR8dSoNGjWohJNo3UhIGd3Tj.jpg'},
    {'id': 331, 'isim': 'Lion', 'afis': 'https://image.tmdb.org/t/p/w500/iBGRbLvg6kVc7wbS8wDdVHq6otm.jpg'},
    {'id': 332, 'isim': 'Hotel Rwanda', 'afis': 'https://image.tmdb.org/t/p/w500/p3pHw85UMZPegfMZBA6dZ06yarm.jpg'},
    {'id': 333, 'isim': 'The Last King of Scotland', 'afis': 'https://image.tmdb.org/t/p/w500/mTtgpH6UnHUtD8moRJUzfGLOZTj.jpg'},
    {'id': 334, 'isim': 'Blood Diamond', 'afis': 'https://image.tmdb.org/t/p/w500/vL0TSMpKWx9UGJbKdYCKREEDukF.jpg'},
    {'id': 335, 'isim': 'Lord of War', 'afis': 'https://image.tmdb.org/t/p/w500/3MGQD4yXokufNlW1AyRXdiy7ytP.jpg'},
    {'id': 336, 'isim': 'The Last Samurai', 'afis': 'https://image.tmdb.org/t/p/w500/a8jmJPs5eZBARmnuEEvZwbjwyz4.jpg'},
    {'id': 337, 'isim': 'Troy', 'afis': 'https://image.tmdb.org/t/p/w500/a07wLy4ONfpsjnBqMwhlWTJTcm.jpg'},
    {'id': 338, 'isim': 'Kingdom of Heaven', 'afis': 'https://image.tmdb.org/t/p/w500/rNaBe4TwbMef71sgscqabpGKsxh.jpg'},
    {'id': 339, 'isim': '3 Idiots', 'afis': 'https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79z8Tew.jpg'},
    {'id': 340, 'isim': 'Taare Zameen Par', 'afis': 'https://image.tmdb.org/t/p/w500/puHRt6Raovm5ujGCdwLWvRv4NHU.jpg'},
    {'id': 341, 'isim': 'Dangal', 'afis': 'https://image.tmdb.org/t/p/w500/cJRPOLEexI7qp2DKtFfCh7YaaUG.jpg'},
    {'id': 342, 'isim': 'PK', 'afis': 'https://image.tmdb.org/t/p/w500/pzSN4XWmmU9uDeLu3aUw6OclGeD.jpg'},
    {'id': 343, 'isim': 'The Intouchables', 'afis': 'https://image.tmdb.org/t/p/w1280/tiyHlhIS4Tm6HK8XdwRZX4cc4tS.jpg'},
    {'id': 344, 'isim': 'Amour', 'afis': 'https://image.tmdb.org/t/p/w500/19hyCudualHxCD0GrEngqsi0wBF.jpg'},
    {'id': 345, 'isim': 'The Hunt', 'afis': 'https://image.tmdb.org/t/p/w500/wxPhn4ef1EAo5njxwBkAEVrlJJG.jpg'},
    {'id': 346, 'isim': 'Another Round', 'afis': 'https://image.tmdb.org/t/p/w500/aDcIt4NHURLKnAEu7gow51Yd00Q.jpg'},
    {'id': 347, 'isim': 'Marriage Story', 'afis': 'https://image.tmdb.org/t/p/w500/2JRyCKaRKyJAVpsIHeLvPw5nHmw.jpg'},
    {'id': 348, 'isim': 'Manchester by the Sea', 'afis': 'https://image.tmdb.org/t/p/w500/o9VXYOuaJxCEKOxbA86xqtwmqYn.jpg'},
    {'id': 349, 'isim': 'Moonlight', 'afis': 'https://image.tmdb.org/t/p/w500/qLnfEmPrDjJfPyyddLJPkXmshkp.jpg'},
    {'id': 350, 'isim': 'Little Women', 'afis': 'https://image.tmdb.org/t/p/w500/1ZzH1XMcKAe5NdrKL5MfcqZHHsZ.jpg'},
    {'id': 351, 'isim': 'Call Me by Your Name', 'afis': 'https://image.tmdb.org/t/p/w500/mZ4gBdfkhP9tvLH1DO4m4HYtiyi.jpg'},
    {'id': 352, 'isim': 'The Perks of Being a Wallflower', 'afis': 'https://image.tmdb.org/t/p/w500/aKCvdFFF5n80P2VdS7d8YBwbCjh.jpg'},
    {'id': 353, 'isim': 'Lost in Translation', 'afis': 'https://image.tmdb.org/t/p/w500/3jCLmYDIIiSMPujbwygNpqdpM8N.jpg'},
    {'id': 354, 'isim': 'The Hangover Part II', 'afis': 'https://image.tmdb.org/t/p/w500/cKZu0Fdkj7dmwbfMpgDqVVCkLJQ.jpg'},
    {'id': 355, 'isim': 'Ted', 'afis': 'https://image.tmdb.org/t/p/w500/tZPTcdGTpxq4yJx1YxqBl0gthNz.jpg'},
    {'id': 356, 'isim': '21 Jump Street', 'afis': 'https://image.tmdb.org/t/p/w500/8v3Sqv9UcIUC4ebmpKWROqPBINZ.jpg'},
    {'id': 357, 'isim': '22 Jump Street', 'afis': 'https://image.tmdb.org/t/p/w500/850chzYHYbT3IISl6Q7dbBuFP2B.jpg'},
    {'id': 358, 'isim': 'Crazy, Stupid, Love.', 'afis': 'https://image.tmdb.org/t/p/w500/p4RafgAPk558muOjnBMHhMArjS2.jpg'},
    {'id': 359, 'isim': 'The Notebook', 'afis': 'https://image.tmdb.org/t/p/w500/rNzQyW4f8B8cQeg7Dgj3n6eT5k9.jpg'},
    {'id': 360, 'isim': 'About Time', 'afis': 'https://image.tmdb.org/t/p/w500/iR1bVfURbN7r1C46WHFbwCkVve.jpg'},
    {'id': 361, 'isim': '500 Days of Summer', 'afis': 'https://image.tmdb.org/t/p/w500/qXAuQ9hF30sQRsXf40OfRVl0MJZ.jpg'},
    {'id': 362, 'isim': 'Love Actually', 'afis': 'https://image.tmdb.org/t/p/w500/7QPeVsr9rcFU9Gl90yg0gTOTpVv.jpg'},
    {'id': 363, 'isim': 'Notting Hill', 'afis': 'https://image.tmdb.org/t/p/w500/hHRIf2XHeQMbyRb3HUx19SF5Ujw.jpg'},
    {'id': 364, 'isim': 'Pretty Woman', 'afis': 'https://image.tmdb.org/t/p/w500/dvcarc7TMrRp1C3jXPpn7PKce99.jpg'},
    {'id': 365, 'isim': 'Dirty Dancing', 'afis': 'https://image.tmdb.org/t/p/w500/9Jw6jys7q9gjzVX5zm1z0gC8gY9.jpg'},
    {'id': 366, 'isim': 'Grease', 'afis': 'https://image.tmdb.org/t/p/w500/hPBIursfYm5ziEmNPrJXkKIDrdI.jpg'},
    {'id': 367, 'isim': 'Mamma Mia!', 'afis': 'https://image.tmdb.org/t/p/w500/zdUA4FNHbXPadzVOJiU0Rgn6cHR.jpg'},
    {'id': 368, 'isim': 'Les Miserables', 'afis': 'https://image.tmdb.org/t/p/w500/toQ6BJCiKVSnklpsma2GnJ6KKah.jpg'},
    {'id': 369, 'isim': 'Chicago', 'afis': 'https://image.tmdb.org/t/p/w500/3ED8cWCXY9zkx77Sd0N5qMbsdDP.jpg'},
    {'id': 370, 'isim': 'The Devil Wears Prada', 'afis': 'https://image.tmdb.org/t/p/w500/8912AsVuS7Sj915apArUFbv6F9L.jpg'},
    {'id': 371, 'isim': 'Legally Blonde', 'afis': 'https://image.tmdb.org/t/p/w500/9ohlMrJHQqKhfUKh7Zr3JQqHNLZ.jpg'},
    {'id': 372, 'isim': '10 Things I Hate About You', 'afis': 'https://image.tmdb.org/t/p/w500/ujERk3aKABXU3NDXOAxEQYTHe9A.jpg'},
    {'id': 373, 'isim': 'Home Alone', 'afis': 'https://image.tmdb.org/t/p/w500/onTSipZ8R3bliBdKfPtsDuHTdlL.jpg'},
    {'id': 374, 'isim': 'Home Alone 2: Lost in New York', 'afis': 'https://image.tmdb.org/t/p/w500/uuitWHpJwxD1wruFl2nZHIb4UGN.jpg'},
    {'id': 375, 'isim': 'Elf', 'afis': 'https://image.tmdb.org/t/p/w500/oOleziEempUPu96jkGs0Pj6tKxj.jpg'},
    {'id': 376, 'isim': 'Ghostbusters', 'afis': 'https://image.tmdb.org/t/p/w500/7E8nLijS9AwwUEPu2oFYOVKhdFA.jpg'},
    {'id': 377, 'isim': 'Beetlejuice', 'afis': 'https://image.tmdb.org/t/p/w500/nnl6OWkyPpuMm595hmAxNW3rZFn.jpg'},
    {'id': 378, 'isim': 'The Mask', 'afis': 'https://image.tmdb.org/t/p/w500/jPC2eYub74zwf2tPGVtzSlBW6Oy.jpg'},
    {'id': 379, 'isim': 'Ace Ventura: Pet Detective', 'afis': 'https://image.tmdb.org/t/p/w500/pqiRuETmuSybfnVZ7qyeoXhQyN1.jpg'},
    {'id': 380, 'isim': 'Dumb and Dumber', 'afis': 'https://image.tmdb.org/t/p/w500/4LdpBXiCyGKkR8FGHgjKlphrfUc.jpg'},
    {'id': 381, 'isim': 'Anchorman: The Legend of Ron Burgundy', 'afis': 'https://image.tmdb.org/t/p/w500/Rdzsh3s6waplhSD7PUaBJovB7v.jpg'},
    {'id': 382, 'isim': 'Step Brothers', 'afis': 'https://image.tmdb.org/t/p/w500/tY2FpgzPVx92JrYveWt4bn3cMyD.jpg'},
    {'id': 383, 'isim': 'Borat', 'afis': 'https://image.tmdb.org/t/p/w500/kfkyALfD4G1mlBJI1lOt2QCra4i.jpg'},
    {'id': 384, 'isim': 'The Dictator', 'afis': 'https://image.tmdb.org/t/p/w500/n0W7kajF4GFMRk2c0wWwMQqTaDM.jpg'},
    {'id': 385, 'isim': 'The Conjuring', 'afis': 'https://image.tmdb.org/t/p/w500/wVYREutTvI2tmxr6ujrHT704wGF.jpg'},
    {'id': 386, 'isim': 'The Conjuring 2', 'afis': 'https://image.tmdb.org/t/p/w500/zEqyD0SBt6HL7W9JQoWwtd5Do1T.jpg'},
    {'id': 387, 'isim': 'Insidious', 'afis': 'https://image.tmdb.org/t/p/w500/1egpmVXuXed58TH2UOnX1nATTrf.jpg'},
    {'id': 388, 'isim': 'Sinister', 'afis': 'https://image.tmdb.org/t/p/w500/nzx10sca3arCeYBAomHan4Q6wa1.jpg'},
    {'id': 389, 'isim': 'It Follows', 'afis': 'https://image.tmdb.org/t/p/w500/iwnQ1JH1wdWrGYkgWySptJ5284A.jpg'},
    {'id': 390, 'isim': 'The Babadook', 'afis': 'https://image.tmdb.org/t/p/w500/qt3fqapeo94TfvMyld8P7gkpXLz.jpg'},
    {'id': 391, 'isim': "Don't Breathe", 'afis': 'https://image.tmdb.org/t/p/w500/dSxHyPZ2nipSfvdft4IhQKjk5eZ.jpg'},
    {'id': 392, 'isim': 'Saw', 'afis': 'https://image.tmdb.org/t/p/w500/rLNSOudrayDBo1uqXjrhxcjODIC.jpg'},
    {'id': 393, 'isim': 'Final Destination', 'afis': 'https://image.tmdb.org/t/p/w500/1mXhlQMnlfvJ2frxTjZSQNnA9Vp.jpg'},
    {'id': 394, 'isim': 'The Ring', 'afis': 'https://image.tmdb.org/t/p/w500/AeRpUynJKDpJveklBJipOYrVxCS.jpg'},
    {'id': 395, 'isim': 'The Grudge', 'afis': 'https://image.tmdb.org/t/p/w500/5AGB8FVELnhMMw3nO372sw1xp58.jpg'},
    {'id': 396, 'isim': 'A Nightmare on Elm Street', 'afis': 'https://image.tmdb.org/t/p/w500/avHGIO93jgCZLf33ec2aahgZJX6.jpg'},
    {'id': 397, 'isim': 'Friday the 13th', 'afis': 'https://image.tmdb.org/t/p/w500/uGGpnWHOmWTARVN9wbC1nPxNgps.jpg'},
    {'id': 398, 'isim': 'The Texas Chain Saw Massacre', 'afis': 'https://image.tmdb.org/t/p/w500/mpgkRPH1GNkMCgdPk2OMyHzAks7.jpg'},
    {'id': 399, 'isim': 'Scream 2', 'afis': 'https://image.tmdb.org/t/p/w500/dORlVasiaDkJXTqt9bdH7nFNs6C.jpg'},
    {'id': 400, 'isim': 'I Know What You Did Last Summer', 'afis': 'https://image.tmdb.org/t/p/w500/6BfZLQYj97NO1yD5JkSAf5vWzGj.jpg'},
    {'id': 401, 'isim': 'The Cabin in the Woods', 'afis': 'https://image.tmdb.org/t/p/w500/zZZe5wn0udlhMtdlDjN4NB72R6e.jpg'},
    {'id': 402, 'isim': 'Tucker and Dale vs. Evil', 'afis': 'https://image.tmdb.org/t/p/w500/8shwLEDzajJGSfLgbpac8x8xn1U.jpg'},
    {'id': 403, 'isim': 'World War Z', 'afis': 'https://image.tmdb.org/t/p/w500/aCnVdvExw6UWSeQfr0tUH3jr4qG.jpg'},
    {'id': 404, 'isim': 'I Am Legend', 'afis': 'https://image.tmdb.org/t/p/w500/iPDkaSdKk2jRLTM65UOEoKtsIZ8.jpg'},
    {'id': 405, 'isim': '28 Days Later', 'afis': 'https://image.tmdb.org/t/p/w500/sQckQRt17VaWbo39GIu0TMOiszq.jpg'},
    {'id': 406, 'isim': 'Casablanca', 'afis': 'https://image.tmdb.org/t/p/w500/oyGRZVIthHJjc98ekKpeWpDh8Ws.jpg'},
    {'id': 407, 'isim': 'Gone with the Wind', 'afis': 'https://image.tmdb.org/t/p/w500/lNz2Ow0wGCAvzckW7EOjE03KcYv.jpg'},
    {'id': 408, 'isim': 'Citizen Kane', 'afis': 'https://image.tmdb.org/t/p/w500/sav0jxhqiH0bPr2vZFU0Kjt2nZL.jpg'},
    {'id': 409, 'isim': 'Vertigo', 'afis': 'https://image.tmdb.org/t/p/w500/15uOEfqBNTVtDUT7hGBVCka0rZz.jpg'},
    {'id': 410, 'isim': 'Rear Window', 'afis': 'https://image.tmdb.org/t/p/w500/zmbPjkZhlnt0JEOU9xMYtbjNXuL.jpg'},
    {'id': 411, 'isim': 'North by Northwest', 'afis': 'https://image.tmdb.org/t/p/w500/kNOFPQrel9YFCVzI0DF8FnCEpCw.jpg'},
    {'id': 412, 'isim': 'Sunset Boulevard', 'afis': 'https://image.tmdb.org/t/p/w500/oOZIN0sbRNLKQC4RRCQnmAx1PlV.jpg'},
    {'id': 413, 'isim': 'Some Like It Hot', 'afis': 'https://image.tmdb.org/t/p/w500/hVIKyTK13AvOGv7ICmJjK44DTzp.jpg'},
    {'id': 414, 'isim': 'Lawrence of Arabia', 'afis': 'https://image.tmdb.org/t/p/w500/AiAm0EtDvyGqNpVoieRw4u65vD1.jpg'},
    {'id': 415, 'isim': 'Ben-Hur', 'afis': 'https://image.tmdb.org/t/p/w500/m4WQ1dBIrEIHZNCoAjdpxwSKWyH.jpg'},
    {'id': 416, 'isim': 'Spartacus', 'afis': 'https://image.tmdb.org/t/p/w500/r0Fgg1GyZgzokaiw2HFQv3oPaL2.jpg'},
    {'id': 417, 'isim': 'The Great Dictator', 'afis': 'https://image.tmdb.org/t/p/w500/nhMXB8GTdswYMCL9nepDZymJCOr.jpg'},
    {'id': 418, 'isim': 'Modern Times', 'afis': 'https://image.tmdb.org/t/p/w500/7uoiKOEjxBBW0AgDGQWrlfGQ90w.jpg'},
    {'id': 419, 'isim': 'City Lights', 'afis': 'https://image.tmdb.org/t/p/w500/rrzypABFDyTpwbTLbmsXU9A8qEM.jpg'},
    {'id': 420, 'isim': 'Full Metal Jacket', 'afis': 'https://image.tmdb.org/t/p/w500/kMKyx1k8hWWscYFnPbnxxN4Eqo4.jpg'},
    {'id': 421, 'isim': 'Platoon', 'afis': 'https://image.tmdb.org/t/p/w500/m3mmFkPQKvPZq5exmh0bDuXlD9T.jpg'},
    {'id': 422, 'isim': 'The Deer Hunter', 'afis': 'https://image.tmdb.org/t/p/w500/bbGtogDZOg09bm42KIpCXUXICkh.jpg'},
    {'id': 423, 'isim': 'Rocky', 'afis': 'https://image.tmdb.org/t/p/w500/hEjK9A9BkNXejFW4tfacVAEHtkn.jpg'},
    {'id': 424, 'isim': 'Rocky II', 'afis': 'https://image.tmdb.org/t/p/w500/bZxQhPXTas4vtyyvZbL8D1ADJB2.jpg'},
    {'id': 425, 'isim': 'Creed', 'afis': 'https://image.tmdb.org/t/p/w500/1BfTsk5VWuw8FCocAhCyqnRbEzq.jpg'},
    {'id': 426, 'isim': 'Top Gun', 'afis': 'https://image.tmdb.org/t/p/w500/xUuHj3CgmZQ9P2cMaqQs4J0d4Zc.jpg'},
    {'id': 427, 'isim': 'Rain Man', 'afis': 'https://image.tmdb.org/t/p/w500/iTNHwO896WKkaoPtpMMS74d8VNi.jpg'},
    {'id': 428, 'isim': 'Scent of a Woman', 'afis': 'https://image.tmdb.org/t/p/w500/4adI7IaveWb7EidYXfLb3MK3CgO.jpg'},
    {'id': 429, 'isim': 'Awakenings', 'afis': 'https://image.tmdb.org/t/p/w500/9gztZXuHLG6AJ0fgqGd7Q43cWRI.jpg'},
    {'id': 430, 'isim': 'Barbie', 'afis': 'https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg'},
    {'id': 431, 'isim': 'The Batman', 'afis': 'https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg'},
    {'id': 432, 'isim': 'Black Panther: Wakanda Forever', 'afis': 'https://image.tmdb.org/t/p/w500/sv1xJUazXeYqALzczSZ3O6nkH75.jpg'},
    {'id': 433, 'isim': 'Doctor Strange in the Multiverse of Madness', 'afis': 'https://image.tmdb.org/t/p/w500/ddJcSKbcp4rKZTmuyWaMhuwcfMz.jpg'},
    {'id': 434, 'isim': 'Guardians of the Galaxy Vol. 3', 'afis': 'https://image.tmdb.org/t/p/w500/r2J02Z2OpNTctfOSN1Ydgii51I3.jpg'},
    {'id': 435, 'isim': 'Dungeons & Dragons: Honor Among Thieves', 'afis': 'https://image.tmdb.org/t/p/w500/v7UF7ypAqjsFZFdjksjQ7IUpXdn.jpg'},
    {'id': 436, 'isim': 'The Super Mario Bros. Movie', 'afis': 'https://image.tmdb.org/t/p/w500/qNBAXBIQlnOThrVvA6mA2B5ggV6.jpg'},
    {'id': 437, 'isim': 'Mission: Impossible - Dead Reckoning Part One', 'afis': 'https://image.tmdb.org/t/p/w500/NNxYkU70HPurnNCSiCjYAmacwm.jpg'},
    {'id': 438, 'isim': 'Fast Five', 'afis': 'https://image.tmdb.org/t/p/w500/gEfQjjQwY7fh5bI4GlG0RrBu7Pz.jpg'},
    {'id': 439, 'isim': 'Furious 7', 'afis': 'https://image.tmdb.org/t/p/w500/ktofZ9Htrjiy0P6LEowsDaxd3Ri.jpg'},
    {'id': 440, 'isim': 'The Fate of the Furious', 'afis': 'https://image.tmdb.org/t/p/w500/dImWM7GJqryWJO9LHa3XQ8DD5NH.jpg'},
    {'id': 441, 'isim': 'Sherlock Holmes', 'afis': 'https://image.tmdb.org/t/p/w500/vskIKrMNUAhns05dx8WYBQfcJEs.jpg'},
    {'id': 442, 'isim': 'Sherlock Holmes: A Game of Shadows', 'afis': 'https://image.tmdb.org/t/p/w500/vskIKrMNUAhns05dx8WYBQfcJEs.jpg'},
    {'id': 443, 'isim': 'Men in Black', 'afis': 'https://image.tmdb.org/t/p/w500/uLOmOF5IzWoyrgIF5MfUnh5pa1X.jpg'},
    {'id': 444, 'isim': 'Men in Black II', 'afis': 'https://image.tmdb.org/t/p/w500/enA22EPyzc2WQ1VVyY7zxresQQr.jpg'},
    {'id': 445, 'isim': 'National Treasure', 'afis': 'https://image.tmdb.org/t/p/w500/pxL6E4GBOPUG6CdkO9cUQN5VMwI.jpg'},
    {'id': 446, 'isim': 'National Treasure: Book of Secrets', 'afis': 'https://image.tmdb.org/t/p/w500/dc9F1vNOGbgeZrO9ejNkbgHPlfw.jpg'},
    {'id': 447, 'isim': 'Independence Day', 'afis': 'https://image.tmdb.org/t/p/w500/p0BPQGSPoSa8Ml0DAf2mB2kCU0R.jpg'},
    {'id': 448, 'isim': 'Armageddon', 'afis': 'https://image.tmdb.org/t/p/w500/eTM3qtGhDU8cvjpoa6KEt5E2auU.jpg'},
    {'id': 449, 'isim': 'Pearl Harbor', 'afis': 'https://image.tmdb.org/t/p/w500/y8A0Cvp8WQmZ3bjbnsL53lY0dsC.jpg'},
    {'id': 450, 'isim': 'The Little Mermaid', 'afis': 'https://image.tmdb.org/t/p/w500/ym1dxyOk4jFcSl4Q2zmRrA5BEEN.jpg'},
    {'id': 451, 'isim': 'Snow White and the Seven Dwarfs', 'afis': 'https://image.tmdb.org/t/p/w500/3VAHfuNb6Z7UiW12iYKANSPBl8m.jpg'},
    {'id': 452, 'isim': 'Cinderella', 'afis': 'https://image.tmdb.org/t/p/w500/clDFqATL4zcE7LzUwkrVj3zHvk7.jpg'},
    {'id': 453, 'isim': 'The Princess and the Frog', 'afis': 'https://image.tmdb.org/t/p/w500/v6nAUs62OJ4DXmnnmPFeVmMz8H9.jpg'},
    {'id': 454, 'isim': 'Lilo & Stitch', 'afis': 'https://image.tmdb.org/t/p/w500/ckQzKpQJO4ZQDCN5evdpKcfm7Ys.jpg'},
    {'id': 455, 'isim': "The Emperor's New Groove", 'afis': 'https://image.tmdb.org/t/p/w500/wwbgkXQBEKtnyIJapk6gUgWkVw8.jpg'},
    {'id': 456, 'isim': 'Megamind', 'afis': 'https://image.tmdb.org/t/p/w500/uZ9ytt3sPTx62XTfN56ILSuYWRe.jpg'},
    {'id': 457, 'isim': 'Cloudy with a Chance of Meatballs', 'afis': 'https://image.tmdb.org/t/p/w500/qhOhIKf7QEyQ5dMrRUqs5eTX1Oq.jpg'},
    {'id': 458, 'isim': 'Rango', 'afis': 'https://image.tmdb.org/t/p/w500/A5MP1guV8pbruieG0tnpPIbaJtt.jpg'},
    {'id': 459, 'isim': 'Chicken Run', 'afis': 'https://image.tmdb.org/t/p/w500/oYbVT9e0k2ZSrRhDSCw2Yqshe1n.jpg'},
    {'id': 460, 'isim': 'Despicable Me 2', 'afis': 'https://image.tmdb.org/t/p/w500/oyMPJJZoOpLHgJoFPUOn6DgkbWJ.jpg'},
    {'id': 461, 'isim': 'Sing', 'afis': 'https://image.tmdb.org/t/p/w500/xviEKU073QAzeFRzWDdW9xDHPbB.jpg'},
    {'id': 462, 'isim': 'Gangs of New York', 'afis': 'https://image.tmdb.org/t/p/w500/lemqKtcCuAano5aqrzxYiKC8kkn.jpg'},
    {'id': 463, 'isim': 'The Aviator', 'afis': 'https://image.tmdb.org/t/p/w500/lx4kWcZc3o9PaNxlQpEJZM17XUI.jpg'},
    {'id': 464, 'isim': 'American Gangster', 'afis': 'https://image.tmdb.org/t/p/w500/m7kJge9DG86Bj7hsBW6xFCMyDkY.jpg'},
    {'id': 465, 'isim': 'Public Enemies', 'afis': 'https://image.tmdb.org/t/p/w500/3KgtekisQBrHRsm2cD5UOB6Ce3k.jpg'},
    {'id': 466, 'isim': 'Law Abiding Citizen', 'afis': 'https://image.tmdb.org/t/p/w500/fcEXcip7v0O1ndV4VUdFqJSqbOg.jpg'},
    {'id': 467, 'isim': 'Shooter', 'afis': 'https://image.tmdb.org/t/p/w500/2aWGxo1E5polpBjPvtBRkWp7qaS.jpg'},
    {'id': 468, 'isim': 'Olympus Has Fallen', 'afis': 'https://image.tmdb.org/t/p/w500/u3GTFGwesNBNd0t1hiLaEk1iqZU.jpg'},
    {'id': 469, 'isim': 'The Italian Job', 'afis': 'https://image.tmdb.org/t/p/w500/eSkjK4kctyrWpFhxl35GPvSs6tI.jpg'},
    {'id': 470, 'isim': 'Collateral Beauty', 'afis': 'https://image.tmdb.org/t/p/w500/4vfqosgik5pLb32RpskYifp8PWJ.jpg'},
    {'id': 471, 'isim': 'Focus', 'afis': 'https://image.tmdb.org/t/p/w500/lOzGWjceYTd0kd5HyX7Ch46O9kh.jpg'},
    {'id': 472, 'isim': 'War Dogs', 'afis': 'https://image.tmdb.org/t/p/w500/mDcPRjZC1bb6LavFU3gwsWdVfCM.jpg'},
    {'id': 473, 'isim': 'Prometheus', 'afis': 'https://image.tmdb.org/t/p/w500/qsYQflQhOuhDpQ0W2aOcwqgDAeI.jpg'},
    {'id': 474, 'isim': 'Alien: Covenant', 'afis': 'https://image.tmdb.org/t/p/w500/zecMELPbU5YMQpC81Z8ImaaXuf9.jpg'},
    {'id': 475, 'isim': 'Cloverfield', 'afis': 'https://image.tmdb.org/t/p/w500/qIegUGJqyMMCRjkKV1s7A9MqdJ8.jpg'},
    {'id': 476, 'isim': '10 Cloverfield Lane', 'afis': 'https://image.tmdb.org/t/p/w500/84Dhwz93vCin6T1PX6ctSvWEuNE.jpg'},
    {'id': 477, 'isim': 'Super 8', 'afis': 'https://image.tmdb.org/t/p/w500/pUWIjaMMYJjeBm5bJyE3mIXdQ62.jpg'},
    {'id': 478, 'isim': 'Real Steel', 'afis': 'https://image.tmdb.org/t/p/w500/4GIeI5K5YdDUkR3mNQBoScpSFEf.jpg'},
    {'id': 479, 'isim': 'Tron: Legacy', 'afis': 'https://image.tmdb.org/t/p/w500/vuifSABRpSnxCAOxEnWpNbZSXpp.jpg'},
    {'id': 480, 'isim': "Ender's Game", 'afis': 'https://image.tmdb.org/t/p/w500/vmd3CNeG2B9FXsit61oc7oxabej.jpg'},
    {'id': 481, 'isim': 'The Curious Case of Benjamin Button', 'afis': 'https://image.tmdb.org/t/p/w500/26wEWZYt6yJkwRVkjcbwJEFh9IS.jpg'},
    {'id': 482, 'isim': 'Atonement', 'afis': 'https://image.tmdb.org/t/p/w500/hMRIyBjPzxaSXWM06se3OcNjIQa.jpg'},
    {'id': 483, 'isim': 'Pride & Prejudice', 'afis': 'https://image.tmdb.org/t/p/w500/vYkTUIyLRwOJnu3VUhdTEocuiWM.jpg'},
    {'id': 484, 'isim': 'The Great Gatsby', 'afis': 'https://image.tmdb.org/t/p/w500/tyxfCBQv6Ap74jcu3xd7aBiaa29.jpg'},
    {'id': 485, 'isim': 'Moulin Rouge!', 'afis': 'https://image.tmdb.org/t/p/w500/kYjdxRL2RJhFRLZBlL78xMT52GK.jpg'},
    {'id': 486, 'isim': 'Closer', 'afis': 'https://image.tmdb.org/t/p/w500/fGGaokx4k00S0J603VG53Qlr9jz.jpg'},
    {'id': 487, 'isim': 'Midnight in Paris', 'afis': 'https://image.tmdb.org/t/p/w500/4wBG5kbfagTQclETblPRRGihk0I.jpg'},
    {'id': 488, 'isim': 'School of Rock', 'afis': 'https://image.tmdb.org/t/p/w500/zXLXaepIBvFVLU25DH3wv4IPSbe.jpg'},
    {'id': 489, 'isim': 'Pineapple Express', 'afis': 'https://image.tmdb.org/t/p/w500/6E50WjeOYjDZg9HXgPjYdGtY2jG.jpg'},
    {'id': 490, 'isim': 'This Is the End', 'afis': 'https://image.tmdb.org/t/p/w500/tNIW0NhX1hKvUsy6PQ80DOKUhkD.jpg'},
    {'id': 491, 'isim': "We're the Millers", 'afis': 'https://image.tmdb.org/t/p/w500/qF2LJ0jwWrtXSuT4AFD5OS2IqaT.jpg'},
    {'id': 492, 'isim': 'Horrible Bosses', 'afis': 'https://image.tmdb.org/t/p/w500/uQkUwgyFHAm0jGQERPG6Z9o9Zbj.jpg'},
    {'id': 493, 'isim': 'Game Night', 'afis': 'https://image.tmdb.org/t/p/w500/85R8LMyn9f2Lev2YPBF8Nughrkv.jpg'},
    {'id': 494, 'isim': 'Tag', 'afis': 'https://image.tmdb.org/t/p/w500/eXXpuW2xaq5Aen9N5prFlARVIvr.jpg'},
    {'id': 495, 'isim': 'Spy', 'afis': 'https://image.tmdb.org/t/p/w500/vPBmfMHxQvRRNGYD5S5ko2KnX56.jpg'},
    {'id': 496, 'isim': 'American Pie', 'afis': 'https://image.tmdb.org/t/p/w500/5P68by2Thn8wHAziyWGEw2O7hco.jpg'},
    {'id': 497, 'isim': 'Project X', 'afis': 'https://image.tmdb.org/t/p/w1280/ckgxPDKixTnROPyYwEo4gRgJpxA.jpg'},
    {'id': 498, 'isim': 'Saw II', 'afis': 'https://image.tmdb.org/t/p/w500/gTnaTysN8HsvVQqTRUh8m35mmUA.jpg'},
    {'id': 499, 'isim': 'Paranormal Activity', 'afis': 'https://image.tmdb.org/t/p/w500/tmclkEpjeo4Zu564gf3KrwIOuKw.jpg'},
    {'id': 500, 'isim': 'The Blair Witch Project', 'afis': 'https://image.tmdb.org/t/p/w500/9050VGrYjYrEjpOvDZVAngLbg1f.jpg'}
]

diziler = [
    {'id': 1, 'isim': 'Breaking Bad', 'afis': 'https://image.tmdb.org/t/p/w500/ztkUQFLlC19CCMYHW9o1zWhJRNq.jpg'},
    {'id': 2, 'isim': 'Game of Thrones', 'afis': 'https://image.tmdb.org/t/p/w500/1XS1oqL89opfnbLl8WnZY1O1uJx.jpg'},
    {'id': 3, 'isim': 'Chernobyl', 'afis': 'https://image.tmdb.org/t/p/w500/hlLXt2tOPT6RRnjiUmoxyG1LTFi.jpg'},
    {'id': 4, 'isim': 'The Sopranos', 'afis': 'https://image.tmdb.org/t/p/w500/rTc7ZXdroqjkKivFPvCPX0Ru7uw.jpg'},
    {'id': 5, 'isim': 'Band of Brothers', 'afis': 'https://image.tmdb.org/t/p/w500/8JMXquNmdMUy2n2RgW8gfOM0O3l.jpg'},
    {'id': 6, 'isim': 'Sherlock', 'afis': 'https://image.tmdb.org/t/p/w500/7WTsnHkbA0FaG6R9twfFde0I9hl.jpg'},
    {'id': 7, 'isim': 'True Detective', 'afis': 'https://image.tmdb.org/t/p/w500/cuV2O5ZyDLHSOWzg3nLVljp1ubw.jpg'},
    {'id': 8, 'isim': 'Firefly', 'afis': 'https://image.tmdb.org/t/p/w500/vZcKsy4sGAvWMVqLluwYuoi11Kj.jpg'},
    {'id': 9, 'isim': 'The Office', 'afis': 'https://image.tmdb.org/t/p/w500/dg9e5fPRRId8PoBE0F6jl5y85Eu.jpg'},
    {'id': 10, 'isim': 'Batman: The Animated Series', 'afis': 'https://image.tmdb.org/t/p/w500/lBomQFW1vlm1yUYMNSbFZ45R4Ox.jpg'},
    {'id': 11, 'isim': 'Fargo', 'afis': 'https://image.tmdb.org/t/p/w500/6U9CPeD8obHzweikFhiLhpc7YBT.jpg'},
    {'id': 12, 'isim': 'Arcane', 'afis': 'https://image.tmdb.org/t/p/w500/zO5xURaYgMX6WpXolp83zVk03Yh.jpg'},
    {'id': 13, 'isim': 'Stranger Things', 'afis': 'https://image.tmdb.org/t/p/w500/cVxVGwHce6xnW8UaVUggaPXbmoE.jpg'},
    {'id': 14, 'isim': 'Black Mirror', 'afis': 'https://image.tmdb.org/t/p/w500/seN6rRfN0I6n8iDXjlSMk1QjNcq.jpg'},
    {'id': 15, 'isim': 'Peaky Blinders', 'afis': 'https://image.tmdb.org/t/p/w500/vUUqzWa2LnHIVqkaKVlVGkVcZIW.jpg'},
    {'id': 16, 'isim': 'The Mandalorian', 'afis': 'https://image.tmdb.org/t/p/w500/sWgBv7LV2PRoQgkxwlibdGXKz1S.jpg'},
    {'id': 17, 'isim': 'Dark', 'afis': 'https://image.tmdb.org/t/p/w500/apbrbWs8M9lyOpJYU5WXrpFbk1Z.jpg'},
    {'id': 18, 'isim': 'The Boys', 'afis': 'https://image.tmdb.org/t/p/w500/2zmTngn1tYC1AvfnrFLhxeD82hz.jpg'},
    {'id': 19, 'isim': 'The Last of Us', 'afis': 'https://image.tmdb.org/t/p/w500/dmo6TYuuJgaYinXBPjrgG9mB5od.jpg'},
    {'id': 20, 'isim': 'House of the Dragon', 'afis': 'https://image.tmdb.org/t/p/w500/oxmdHR5Ka28HAJuMmS2hk5K6QQY.jpg'},
    {'id': 21, 'isim': 'Mindhunter', 'afis': 'https://image.tmdb.org/t/p/w500/fbKE87mojpIETWepSbD5Qt741fp.jpg'},
    {'id': 22, 'isim': 'Narcos', 'afis': 'https://image.tmdb.org/t/p/w500/rTmal9fDbwh5F0waol2hq35U4ah.jpg'},
    {'id': 23, 'isim': 'Heartstopper', 'afis': 'https://image.tmdb.org/t/p/w500/dQc0QbDiHjGmWxTfKtBgYtS4bj5.jpg'},
    {'id': 24, 'isim': 'Severance', 'afis': 'https://image.tmdb.org/t/p/w500/pPHpeI2X1qEd1CS1SeyrdhZ4qnT.jpg'},
    {'id': 25, 'isim': 'Fleabag', 'afis': 'https://image.tmdb.org/t/p/w500/27vEYsRKa3eAniwmoccOoluEXQ1.jpg'},
    {'id': 26, 'isim': 'The Bear', 'afis': 'https://image.tmdb.org/t/p/w500/eKfVzzEazSIjJMrw9ADa2x8ksLz.jpg'},
    {'id': 27, 'isim': 'Invincible', 'afis': 'https://image.tmdb.org/t/p/w500/jBn4LWlgdsf6xIUYhYBwpctBVsj.jpg'},
    {'id': 28, 'isim': 'The Crown', 'afis': 'https://image.tmdb.org/t/p/w500/1DDE0Z2Y805rqfkEjPbZsMLyPwa.jpg'},
    {'id': 29, 'isim': 'Downton Abbey', 'afis': 'https://image.tmdb.org/t/p/w500/7HgDYRYjym4BwbhKaqTQq771SKb.jpg'},
    {'id': 30, 'isim': 'Mad Men', 'afis': 'https://image.tmdb.org/t/p/w500/yd4BrXPQZvin4XMDlXUP9JgQDUQ.jpg'},
    {'id': 31, 'isim': 'House', 'afis': 'https://image.tmdb.org/t/p/w500/3Cz7ySOQJmqiuTdrc6CY0r65yDI.jpg'},
    {'id': 32, 'isim': 'Dexter', 'afis': 'https://image.tmdb.org/t/p/w500/q8dWfc4JwQuv3HayIZeO84jAXED.jpg'},
    {'id': 33, 'isim': 'Lost', 'afis': 'https://image.tmdb.org/t/p/w500/og6S0aTZU6YUJAbqxeKjCa3kY1E.jpg'},
    {'id': 34, 'isim': 'Prison Break', 'afis': 'https://image.tmdb.org/t/p/w500/wnmNPaLvhnMeOqnWlhNkYCZxtda.jpg'},
    {'id': 35, 'isim': 'The Walking Dead', 'afis': 'https://image.tmdb.org/t/p/w500/ng3cMtxYKt1OSQYqFlnKWnVsqNO.jpg'},
    {'id': 36, 'isim': 'Vikings', 'afis': 'https://image.tmdb.org/t/p/w500/bQLrHIRNEkE3PdIWQrZHynQZazu.jpg'},
    {'id': 37, 'isim': 'Squid Game', 'afis': 'https://image.tmdb.org/t/p/w500/1QdXdRYfktUSONkl1oD5gc6Be0s.jpg'},
    {'id': 38, 'isim': 'Friends', 'afis': 'https://image.tmdb.org/t/p/w500/f496cm9enuEsZkSPzCwnTESEK5s.jpg'},
    {'id': 39, 'isim': 'Seinfeld', 'afis': 'https://image.tmdb.org/t/p/w500/aCw8ONfyz3AhngVQa1E2Ss4KSUQ.jpg'},
    {'id': 40, 'isim': 'Modern Family', 'afis': 'https://image.tmdb.org/t/p/w500/k5Qg5rgPoKdh3yTJJrLtyoyYGwC.jpg'},
    {'id': 41, 'isim': 'Brooklyn Nine-Nine', 'afis': 'https://image.tmdb.org/t/p/w500/A3SymGlOHefSKbz1bCOz56moupS.jpg'},
    {'id': 42, 'isim': 'Parks and Recreation', 'afis': 'https://image.tmdb.org/t/p/w500/dFs6yHxheEGoZSoA0Fdkgy6Jxh0.jpg'},
    {'id': 43, 'isim': 'New Girl', 'afis': 'https://image.tmdb.org/t/p/w500/v5S58vtEV0fM0Chf9Pws9yfXOXT.jpg'},
    {'id': 44, 'isim': 'Two and a Half Men', 'afis': 'https://image.tmdb.org/t/p/w500/xgfjxyV3g1S68opzuvG6G87muDp.jpg'},
    {'id': 45, 'isim': "That '70s Show", 'afis': 'https://image.tmdb.org/t/p/w500/laEZvTqM80UaplUaDSCCbWhlyEV.jpg'},
    {'id': 46, 'isim': 'Malcolm in the Middle', 'afis': 'https://image.tmdb.org/t/p/w500/ckLLIsNy3Z0Go1PYHA2PHzVymUA.jpg'},
    {'id': 47, 'isim': 'Freaks and Geeks', 'afis': 'https://image.tmdb.org/t/p/w500/tPqV63zcW6ZV0Hd48DMGb5UzQIG.jpg'},
    {'id': 48, 'isim': 'The Good Place', 'afis': 'https://image.tmdb.org/t/p/w500/qIhsuhoIYR5yTnDta0IL4senbeN.jpg'},
    {'id': 49, 'isim': 'Silicon Valley', 'afis': 'https://image.tmdb.org/t/p/w500/4ptpmWBVD9HY9hMh8Cbs6SMiy7p.jpg'},
    {'id': 50, 'isim': '30 Rock', 'afis': 'https://image.tmdb.org/t/p/w500/eYYQWACx7ttUzRwTNYuo6zveqpE.jpg'},
    {'id': 51, 'isim': 'Arrested Development', 'afis': 'https://image.tmdb.org/t/p/w500/p4r4RD7RsNcJVoz0H6z3dBoTBtW.jpg'},
    {'id': 52, 'isim': "Schitt's Creek", 'afis': 'https://image.tmdb.org/t/p/w500/iRfSzrPS5VYWQv7KVSEg2BZZL6C.jpg'},
    {'id': 53, 'isim': 'Curb Your Enthusiasm', 'afis': 'https://image.tmdb.org/t/p/w500/mZqWmSq1M61Jlre3furVDSXvdrN.jpg'},
    {'id': 54, 'isim': 'Shameless', 'afis': 'https://image.tmdb.org/t/p/w500/ifo31fMWLmyOVpdak9K0kY4jldQ.jpg'},
    {'id': 55, 'isim': 'South Park', 'afis': 'https://image.tmdb.org/t/p/w500/1CGwZCFX2qerXaXQJJUB3qUvxq7.jpg'},
    {'id': 56, 'isim': 'Family Guy', 'afis': 'https://image.tmdb.org/t/p/w500/8o8kiBkWFK3gVytHdyzEWUBXVfK.jpg'},
    {'id': 57, 'isim': 'The Simpsons', 'afis': 'https://image.tmdb.org/t/p/w500/uWpG7GqfKGQqX4YMAo3nv5OrglV.jpg'},
    {'id': 58, 'isim': 'Futurama', 'afis': 'https://image.tmdb.org/t/p/w500/6ZS8SOno6kTmWz4eQ8lX8EBXOMv.jpg'},
    {'id': 59, 'isim': 'Archer', 'afis': 'https://image.tmdb.org/t/p/w500/vhnrkTGYPqcB63ALcSJm0WoaKHT.jpg'},
    {'id': 60, 'isim': "Bob's Burgers", 'afis': 'https://image.tmdb.org/t/p/w500/iIHsQe3Qjs3NH62HdamyQEPeqTR.jpg'},
    {'id': 61, 'isim': 'Big Mouth', 'afis': 'https://image.tmdb.org/t/p/w500/1Zio9w1tAd3r5Gu4d9AzTSx2hnT.jpg'},
    {'id': 62, 'isim': 'Sex Education', 'afis': 'https://image.tmdb.org/t/p/w500/bc3bmTdnoKcRuO9xdQKgAbB7Y9Z.jpg'},
    {'id': 63, 'isim': 'Master of None', 'afis': 'https://image.tmdb.org/t/p/w500/AcJM86PhgHAfbrF4dMKBaqO3cHV.jpg'},
    {'id': 64, 'isim': 'Atlanta', 'afis': 'https://image.tmdb.org/t/p/w500/8HZyGMnPLVVb00rmrh6A2SbK9NX.jpg'},
    {'id': 65, 'isim': 'Barry', 'afis': 'https://image.tmdb.org/t/p/w500/j1XpwD11f0BAEI7pX6UdMhUVX2F.jpg'},
    {'id': 66, 'isim': 'What We Do in the Shadows', 'afis': 'https://image.tmdb.org/t/p/w500/wa3ZQE9kLnqwN3vQ0NNjg1NPsCa.jpg'},
    {'id': 67, 'isim': 'After Life', 'afis': 'https://image.tmdb.org/t/p/w500/6eJf4h9XcvqK64vbx27EFlLVURm.jpg'},
    {'id': 68, 'isim': 'Westworld', 'afis': 'https://image.tmdb.org/t/p/w500/8MfgyFHf7XEboZJPZXCIDqqiz6e.jpg'},
    {'id': 69, 'isim': 'The Witcher', 'afis': 'https://image.tmdb.org/t/p/w500/AoGsDM02UVt0npBA8OvpDcZbaMi.jpg'},
    {'id': 70, 'isim': "The Handmaid's Tale", 'afis': 'https://image.tmdb.org/t/p/w500/eGUT7j3n3rn5yGihlCgwUnD70HV.jpg'},
    {'id': 71, 'isim': 'Black Sails', 'afis': 'https://image.tmdb.org/t/p/w500/mZcSwrDdw6cdOVgXm496DgwrQcQ.jpg'},
    {'id': 72, 'isim': 'Outlander', 'afis': 'https://image.tmdb.org/t/p/w500/hXWGDEwPiEWqFesF5gZGImtPIWh.jpg'},
    {'id': 73, 'isim': 'Doctor Who', 'afis': 'https://image.tmdb.org/t/p/w500/w8enSKCf6Zm0topeQ2XPccDqsqp.jpg'},
    {'id': 74, 'isim': 'Battlestar Galactica', 'afis': 'https://image.tmdb.org/t/p/w500/99PJSbcO2LeM10uOGWeFihNp77j.jpg'},
    {'id': 75, 'isim': 'The Expanse', 'afis': 'https://image.tmdb.org/t/p/w500/8djpxDeWpINnGhjpFXQjnBe6zbx.jpg'},
    {'id': 76, 'isim': 'Fringe', 'afis': 'https://image.tmdb.org/t/p/w500/sY9hg5dLJ93RJOyKEiu1nAtBRND.jpg'},
    {'id': 77, 'isim': 'The X-Files', 'afis': 'https://image.tmdb.org/t/p/w500/rcBx0p8h51LHceyhquYMxbspJQu.jpg'},
    {'id': 78, 'isim': 'Twin Peaks', 'afis': 'https://image.tmdb.org/t/p/w500/lA9CNSdo50iQPZ8A2fyVpMvJZAf.jpg'},
    {'id': 79, 'isim': 'Supernatural', 'afis': 'https://image.tmdb.org/t/p/w500/u40gJarLPlIkwouKlzGdobQOV9k.jpg'},
    {'id': 80, 'isim': 'Buffy the Vampire Slayer', 'afis': 'https://image.tmdb.org/t/p/w500/y7fVZkyheCEQHDUEHwNmYENGfT2.jpg'},
    {'id': 81, 'isim': 'Charmed', 'afis': 'https://image.tmdb.org/t/p/w500/z4bPJ1BWU2EtV69NII2GVvsugQ2.jpg'},
    {'id': 82, 'isim': 'Smallville', 'afis': 'https://image.tmdb.org/t/p/w500/r9K5QQv1o9pLKSEEbfoMWOQwLl5.jpg'},
    {'id': 83, 'isim': 'Arrow', 'afis': 'https://image.tmdb.org/t/p/w500/u8ZHFj1jC384JEkTt3vNg1DfWEb.jpg'},
    {'id': 84, 'isim': 'The Flash', 'afis': 'https://image.tmdb.org/t/p/w500/yZevl2vHQgmosfwUdVNzviIfaWS.jpg'},
    {'id': 85, 'isim': 'Gotham', 'afis': 'https://image.tmdb.org/t/p/w500/4XddcRDtnNjYmLRMYpbrhFxsbuq.jpg'},
    {'id': 86, 'isim': 'Daredevil', 'afis': 'https://image.tmdb.org/t/p/w500/ig5sp7GzfQZw2dXgrM8OXUpOPri.jpg'},
    {'id': 87, 'isim': 'The Punisher', 'afis': 'https://image.tmdb.org/t/p/w1280/tM6xqRKXoloH9UchaJEyyRE9O1w.jpg'},
    {'id': 88, 'isim': 'Iron Fist', 'afis': 'https://image.tmdb.org/t/p/w500/4l6KD9HhtD6nCDEfg10Lp6C6zah.jpg'},
    {'id': 89, 'isim': 'The Defenders', 'afis': 'https://image.tmdb.org/t/p/w500/g4QCPffsJqElwCu8f1JvvuaRVsc.jpg'},
    {'id': 90, 'isim': 'Moon Knight', 'afis': 'https://image.tmdb.org/t/p/w500/vKDUmKO6F9bSKKyHhg7YGbgcEeF.jpg'},
    {'id': 91, 'isim': 'Andor', 'afis': 'https://image.tmdb.org/t/p/w500/khZqmwHQicTYoS7Flreb9EddFZC.jpg'},
    {'id': 92, 'isim': 'Obi-Wan Kenobi', 'afis': 'https://image.tmdb.org/t/p/w500/qJRB789ceLryrLvOKrZqLKr2CGf.jpg'},
    {'id': 93, 'isim': 'Ahsoka', 'afis': 'https://image.tmdb.org/t/p/w500/eiJeWeCAEZAmRppnXHiTWDcCd3Q.jpg'},
    {'id': 94, 'isim': 'Sense8', 'afis': 'https://image.tmdb.org/t/p/w500/kmyvlQ9QKzgdZY31rXaUlgCnzrB.jpg'},
    {'id': 95, 'isim': 'The OA', 'afis': 'https://image.tmdb.org/t/p/w500/rueY4slMeKtTGitm0raFUJvgaa5.jpg'},
    {'id': 96, 'isim': 'Altered Carbon', 'afis': 'https://image.tmdb.org/t/p/w500/66rKwpSexUZ3yTv5lBS1bjU4Ykk.jpg'},
    {'id': 97, 'isim': 'Love, Death & Robots', 'afis': 'https://image.tmdb.org/t/p/w500/asDqvkE66EegtKJJXIRhBJPxscr.jpg'},
    {'id': 98, 'isim': 'The Haunting of Hill House', 'afis': 'https://image.tmdb.org/t/p/w500/38PkhBGRQtmVx2drvPik3F42qHO.jpg'},
    {'id': 99, 'isim': 'Midnight Mass', 'afis': 'https://image.tmdb.org/t/p/w500/iYoMZYVD775MtBYJfv6OGY1FsnL.jpg'},
    {'id': 100, 'isim': 'Penny Dreadful', 'afis': 'https://image.tmdb.org/t/p/w500/hQSdrXBYTbLGHYDIseHkBOPXTgL.jpg'},
    {'id': 101, 'isim': 'Hannibal', 'afis': 'https://image.tmdb.org/t/p/w500/pbV2eLnKSIm1epSZt473UYfqaeZ.jpg'},
    {'id': 102, 'isim': 'Bates Motel', 'afis': 'https://image.tmdb.org/t/p/w500/xXKcfZE7ulYxgjjYv51s0zDG69s.jpg'},
    {'id': 103, 'isim': 'Grimm', 'afis': 'https://image.tmdb.org/t/p/w500/iOptnt1QHi6bIHmOq6adnZTV0bU.jpg'},
    {'id': 104, 'isim': 'Merlin', 'afis': 'https://image.tmdb.org/t/p/w500/8eR5Jg7CxsuCOEBU5wW0opObxpi.jpg'},
    {'id': 105, 'isim': 'Shadow and Bone', 'afis': 'https://image.tmdb.org/t/p/w500/mS9O9mjPlwpLTne4JgQlDkgREWA.jpg'},
    {'id': 106, 'isim': 'Money Heist', 'afis': 'https://image.tmdb.org/t/p/w500/reEMJA1uzscCbkpeRJeTT2bjqUp.jpg'},
    {'id': 107, 'isim': 'Lupin', 'afis': 'https://image.tmdb.org/t/p/w500/h6Z2oogE4mJk2uffdtIlLhb0EHx.jpg'},
    {'id': 108, 'isim': 'Ozark', 'afis': 'https://image.tmdb.org/t/p/w500/m73bD8VjibSKuTWg597GQVyVhSb.jpg'},
    {'id': 109, 'isim': 'Reacher', 'afis': 'https://image.tmdb.org/t/p/w500/31GlRQMiDunO8cl3NxTz34U64rf.jpg'},
    {'id': 110, 'isim': 'Jack Ryan', 'afis': 'https://image.tmdb.org/t/p/w500/cO4py3L3q5GNPrA0qr1wVDrosK1.jpg'},
    {'id': 111, 'isim': 'Bodyguard', 'afis': 'https://image.tmdb.org/t/p/w500/5DUJTrHTRLHLCKWriPhdusQogAv.jpg'},
    {'id': 112, 'isim': 'Luther', 'afis': 'https://image.tmdb.org/t/p/w500/hDxOMX8zzH1FiqKWVBzNaYGBkle.jpg'},
    {'id': 113, 'isim': 'Happy Valley', 'afis': 'https://image.tmdb.org/t/p/w500/xZK5iQSrn2mouZEk2PwyLPCwa4u.jpg'},
    {'id': 114, 'isim': 'Big Little Lies', 'afis': 'https://image.tmdb.org/t/p/w500/b4HNJOc2N6SGyEhf2RagdpAKBK6.jpg'},
    {'id': 115, 'isim': 'Sharp Objects', 'afis': 'https://image.tmdb.org/t/p/w500/1SGovj2qDdkJexvhFiXllj9EYfu.jpg'},
    {'id': 116, 'isim': 'True Blood', 'afis': 'https://image.tmdb.org/t/p/w500/ktEp6fzL4xzCWsSVtrcH8JaQNQy.jpg'},
    {'id': 117, 'isim': 'The Shield', 'afis': 'https://image.tmdb.org/t/p/w500/AfdZXqqlFsPUEfi6kWWWthxw7Nz.jpg'},
    {'id': 118, 'isim': 'Boardwalk Empire', 'afis': 'https://image.tmdb.org/t/p/w500/kL6SqlVPpfAof2nQbh1VxkUuXBQ.jpg'},
    {'id': 119, 'isim': 'Spartacus', 'afis': 'https://image.tmdb.org/t/p/w500/c2GKN4VHCj1dnjFMANRpGkCVBae.jpg'},
    {'id': 120, 'isim': 'Homeland', 'afis': 'https://image.tmdb.org/t/p/w500/6GAvS2e6VIRsms9FpVt33PsCoEW.jpg'},
    {'id': 121, 'isim': '24', 'afis': 'https://image.tmdb.org/t/p/w500/iq6yrZ5LEDXf1ArCOYLq8PIUBpV.jpg'},
    {'id': 122, 'isim': 'Person of Interest', 'afis': 'https://image.tmdb.org/t/p/w500/6FuKOyJgViZXgMDOq9djFJLWPqX.jpg'},
    {'id': 123, 'isim': 'The Blacklist', 'afis': 'https://image.tmdb.org/t/p/w500/4HTfd1PhgFUenJxVuBDNdLmdr0c.jpg'},
    {'id': 124, 'isim': 'Mentalist', 'afis': 'https://image.tmdb.org/t/p/w500/6WIXVOMUQvfM4RaWq138IBX5ioH.jpg'},
    {'id': 125, 'isim': 'Castle', 'afis': 'https://image.tmdb.org/t/p/w500/diXBeMzvfJb2iJg3G0kCUaMCzEc.jpg'},
    {'id': 126, 'isim': 'Bones', 'afis': 'https://image.tmdb.org/t/p/w500/eyTu5c8LniVciRZIOSHTvvkkgJa.jpg'},
    {'id': 127, 'isim': 'NCIS', 'afis': 'https://image.tmdb.org/t/p/w500/mBcu8d6x6zB1el3MPNl7cZQEQ31.jpg'},
    {'id': 128, 'isim': 'Law & Order: Special Victims Unit', 'afis': 'https://image.tmdb.org/t/p/w500/haJ9eHytVO3H3JooMJG1DiWwDNm.jpg'},
    {'id': 129, 'isim': 'Suits', 'afis': 'https://image.tmdb.org/t/p/w500/vQiryp6LioFxQThywxbC6TuoDjy.jpg'},
    {'id': 130, 'isim': 'White Collar', 'afis': 'https://image.tmdb.org/t/p/w500/417XNiGvdzCsG9kDnnQJYaBsIrx.jpg'},
    {'id': 131, 'isim': 'Burn Notice', 'afis': 'https://image.tmdb.org/t/p/w500/o2fnD3SNiQjGVgA2C3ezaeh2HK.jpg'},
    {'id': 132, 'isim': 'Chuck', 'afis': 'https://image.tmdb.org/t/p/w500/vEZvGVVMjk1TRs59nfypTI5lAXj.jpg'},
    {'id': 133, 'isim': 'Lucifer', 'afis': 'https://image.tmdb.org/t/p/w500/ekZobS8isE6mA53RAiGDG93hBxL.jpg'},
    {'id': 134, 'isim': 'Killing Eve', 'afis': 'https://image.tmdb.org/t/p/w500/4wKhTVw8aGq5AZMa0Q1spERdi7n.jpg'},
    {'id': 135, 'isim': 'You', 'afis': 'https://image.tmdb.org/t/p/w500/oANi0vEE92nuijiZQgPZ88FSxqQ.jpg'},
    {'id': 136, 'isim': 'How to Get Away with Murder', 'afis': 'https://image.tmdb.org/t/p/w500/bJs8Y6T88NcgksxA8UaVl4YX8p8.jpg'},
    {'id': 137, 'isim': 'Scandal', 'afis': 'https://image.tmdb.org/t/p/w500/4XmF8PMSqtHCGNoL15oHbjr5ZuO.jpg'},
    {'id': 138, 'isim': 'Death Note', 'afis': 'https://image.tmdb.org/t/p/w500/tCZFfYTIwrR7n94J6G14Y4hAFU6.jpg'},
    {'id': 139, 'isim': 'Attack on Titan', 'afis': 'https://image.tmdb.org/t/p/w500/hTP1DtLGFamjfu8WqjnuQdP1n4i.jpg'},
    {'id': 140, 'isim': 'Fullmetal Alchemist: Brotherhood', 'afis': 'https://image.tmdb.org/t/p/w500/5ZFUEOULaVml7pQuXxhpR2SmVUw.jpg'},
    {'id': 141, 'isim': 'Demon Slayer: Kimetsu no Yaiba', 'afis': 'https://image.tmdb.org/t/p/w500/xUfRZu2mi8jH6SzQEJGP6tjBuYj.jpg'},
    {'id': 142, 'isim': 'Cowboy Bebop', 'afis': 'https://image.tmdb.org/t/p/w500/xDiXDfZwC6XYC6fxHI1jl3A3Ill.jpg'},
    {'id': 143, 'isim': 'Neon Genesis Evangelion', 'afis': 'https://image.tmdb.org/t/p/w500/y2ah9t0navXyIvoHg1uIbIHO3tt.jpg'},
    {'id': 144, 'isim': 'Dragon Ball Z', 'afis': 'https://image.tmdb.org/t/p/w500/i1lMlxir5E4jyeLlqS2bK1Cn3Tt.jpg'},
    {'id': 145, 'isim': 'Naruto Shippuden', 'afis': 'https://image.tmdb.org/t/p/w500/71mASgFgSiPl9QUexVH8BubU0lD.jpg'},
    {'id': 146, 'isim': 'One Piece', 'afis': 'https://image.tmdb.org/t/p/w500/lXl3ZbY5TksOdt6eYgdyg6vsnFW.jpg'},
    {'id': 147, 'isim': 'Bleach', 'afis': 'https://image.tmdb.org/t/p/w500/2EewmxXe72ogD0EaWM8gqa0ccIw.jpg'},
    {'id': 148, 'isim': 'Hunter x Hunter', 'afis': 'https://image.tmdb.org/t/p/w500/i2EEr2uBvRlAwJ8d8zTG2Y19mIa.jpg'},
    {'id': 149, 'isim': 'Steins;Gate', 'afis': 'https://image.tmdb.org/t/p/w500/5zxePQEsUKLYDh2kpXGQAeInjUU.jpg'},
    {'id': 150, 'isim': 'Code Geass', 'afis': 'https://image.tmdb.org/t/p/w500/x316WCogkeIwNY4JR8zTCHbI2nQ.jpg'},
    {'id': 151, 'isim': 'Violet Evergarden', 'afis': 'https://image.tmdb.org/t/p/w500/61EwFPqc0r1uJo6la49J55F8bQ8.jpg'},
    {'id': 152, 'isim': 'Chainsaw Man', 'afis': 'https://image.tmdb.org/t/p/w500/npdB6eFzizki0WaZ1OvKcJrWe97.jpg'},
    {'id': 153, 'isim': 'Jujutsu Kaisen', 'afis': 'https://image.tmdb.org/t/p/w500/fHpKWq9ayzSk8nSwqRuaAUemRKh.jpg'},
    {'id': 154, 'isim': 'Tokyo Ghoul', 'afis': 'https://image.tmdb.org/t/p/w500/1m4RlC9BTCbyY549TOdVQ5NRPcR.jpg'},
    {'id': 155, 'isim': 'Sword Art Online', 'afis': 'https://image.tmdb.org/t/p/w500/9m8bFIXPg26taNrFSXGwEORVACD.jpg'},
    {'id': 156, 'isim': 'My Hero Academia', 'afis': 'https://image.tmdb.org/t/p/w500/phuYuzqWW9ru8EA3HVjE9W2Rr3M.jpg'},
    {'id': 157, 'isim': 'Haikyuu!!', 'afis': 'https://image.tmdb.org/t/p/w500/8WEr48swcqe89Zsy5sdrGCASlIg.jpg'},
    {'id': 158, 'isim': 'Erased', 'afis': 'https://image.tmdb.org/t/p/w500/EljUwZJhpuYfVuSfqY8Pt1xxpH.jpg'},
    {'id': 159, 'isim': 'Riverdale', 'afis': 'https://image.tmdb.org/t/p/w500/d8mmn9thQ5dBk2qbv6BCqGUXWK3.jpg'},
    {'id': 160, 'isim': 'The Vampire Diaries', 'afis': 'https://image.tmdb.org/t/p/w500/b3vl6wV1W8PBezFfntKTrhrehCY.jpg'},
    {'id': 161, 'isim': 'The Originals', 'afis': 'https://image.tmdb.org/t/p/w500/keJOhJXGiLL54EW6QocbyvQGquA.jpg'},
    {'id': 162, 'isim': 'Teen Wolf', 'afis': 'https://image.tmdb.org/t/p/w500/8Ij1O2nU8exLgwPXU8Eo6PZdCDC.jpg'},
    {'id': 163, 'isim': 'Pretty Little Liars', 'afis': 'https://image.tmdb.org/t/p/w500/aUPbHiLS3hCHKjtLsncFa9g0viV.jpg'},
    {'id': 164, 'isim': 'Gossip Girl', 'afis': 'https://image.tmdb.org/t/p/w500/mRvSUuU1VQQkZZ578jKJpcUCuL8.jpg'},
    {'id': 165, 'isim': 'The O.C.', 'afis': 'https://image.tmdb.org/t/p/w500/xDc6BMGDaeyalpSZ9KKk7RCBCz5.jpg'},
    {'id': 166, 'isim': 'One Tree Hill', 'afis': 'https://image.tmdb.org/t/p/w500/sOrelBaAhp7DZbPTivDwKEyPslC.jpg'},
    {'id': 167, 'isim': "Dawson's Creek", 'afis': 'https://image.tmdb.org/t/p/w500/arT93dBemanftfWTcf9I0JRIlxU.jpg'},
    {'id': 168, 'isim': 'Euphoria', 'afis': 'https://image.tmdb.org/t/p/w500/3Q0hd3heuWwDWpwcDkhQOA6TYWI.jpg'},
    {'id': 169, 'isim': 'Elite', 'afis': 'https://image.tmdb.org/t/p/w500/3NTAbAiao4JLzFQw6YxP1YZppM8.jpg'},
    {'id': 170, 'isim': 'Skins', 'afis': 'https://image.tmdb.org/t/p/w500/yaDeFXW7Lzv6fqGymsUctt1a5fs.jpg'},
    {'id': 171, 'isim': 'Misfits', 'afis': 'https://image.tmdb.org/t/p/w500/1yjmRIp8A92FlAw5JpouQ50ATUA.jpg'},
    {'id': 172, 'isim': 'Bridgerton', 'afis': 'https://image.tmdb.org/t/p/w500/zCEm0xrRMa5fLCQ9d0nvcw6tvcr.jpg'},
    {'id': 173, 'isim': "The Queen's Gambit", 'afis': 'https://image.tmdb.org/t/p/w500/zU0htwkhNvBQdVSIKB9s6hgVeFK.jpg'},
    {'id': 174, 'isim': 'Maid', 'afis': 'https://image.tmdb.org/t/p/w500/4brWcSXdH31BZUTtRTHj2BYFe6M.jpg'},
    {'id': 175, 'isim': 'Unbelievable', 'afis': 'https://image.tmdb.org/t/p/w500/jHOrNJNM03Lsjdw7nsw7TlqBOhd.jpg'},
    {'id': 176, 'isim': 'When They See Us', 'afis': 'https://image.tmdb.org/t/p/w500/oPv3nNtkuc6EPEql5lgdOuQNHuG.jpg'},
    {'id': 177, 'isim': 'This Is Us', 'afis': 'https://image.tmdb.org/t/p/w500/huxmY6Dmzwpv5Q2hnNft0UMK7vf.jpg'},
    {'id': 178, 'isim': 'The Good Doctor', 'afis': 'https://image.tmdb.org/t/p/w500/luhKkdD80qe62fwop6sdrXK9jUT.jpg'},
    {'id': 179, 'isim': 'House M.D.', 'afis': 'https://image.tmdb.org/t/p/w500/3Cz7ySOQJmqiuTdrc6CY0r65yDI.jpg'},
    {'id': 180, 'isim': 'Scrubs', 'afis': 'https://image.tmdb.org/t/p/w500/u1z05trCA7AuSuDhi365grwdos1.jpg'},
    {'id': 181, 'isim': 'Desperate Housewives', 'afis': 'https://image.tmdb.org/t/p/w500/4qeI51jDzH81PpUUNaJCBrfm7f6.jpg'},
    {'id': 182, 'isim': 'Wednesday', 'afis': 'https://image.tmdb.org/t/p/w500/36xXlhEpQqVVPuiZhfoQuaY4OlA.jpg'},
    {'id': 183, 'isim': 'Mr. Robot', 'afis': 'https://image.tmdb.org/t/p/w500/kv1nRqgebSsREnd7vdC2pSGjpLo.jpg'},
    {'id': 184, 'isim': 'Yellowstone', 'afis': 'https://image.tmdb.org/t/p/w500/s4QRRYc1V2e68Qy9Wel9MI8fhRP.jpg'},
    {'id': 185, 'isim': 'Fallout', 'afis': 'https://image.tmdb.org/t/p/w500/c15BtJxCXMrISLVmysdsnZUPQft.jpg'},
    {'id': 186, 'isim': 'Silo', 'afis': 'https://image.tmdb.org/t/p/w500/c2OijvbFEXBW1onbzuvENr4CGQB.jpg'},
    {'id': 187, 'isim': 'Foundation', 'afis': 'https://image.tmdb.org/t/p/w500/tg9I5pOY4M9CKj8U0cxVBTsm5eh.jpg'},
    {'id': 188, 'isim': 'The White Lotus', 'afis': 'https://image.tmdb.org/t/p/w500/gbSaK9v1CbcYH1ISgbM7XObD2dW.jpg'},
    {'id': 189, 'isim': 'Entourage', 'afis': 'https://image.tmdb.org/t/p/w500/kLKP8zrArBtBboGz3qJOuMGC7rL.jpg'},
    {'id': 190, 'isim': 'Californication', 'afis': 'https://image.tmdb.org/t/p/w500/jPqOY8cq9KXQN4bD7zJGHCNvcb4.jpg'},
    {'id': 191, 'isim': 'Billions', 'afis': 'https://image.tmdb.org/t/p/w500/edwYPQdZE998d748AdwWLsfy0rl.jpg'},
    {'id': 192, 'isim': 'Ray Donovan', 'afis': 'https://image.tmdb.org/t/p/w500/cwJ6nLNvX62By0yoLYWFhRelPkF.jpg'},
    {'id': 193, 'isim': 'The Wheel of Time', 'afis': 'https://image.tmdb.org/t/p/w500/ihBi24EIr5kwAeY2PqmsgAcCj4n.jpg'},
    {'id': 194, 'isim': 'American Gods', 'afis': 'https://image.tmdb.org/t/p/w500/3KCAZaKHmoMIN9dHutqaMtubQqD.jpg'},
    {'id': 195, 'isim': 'Legion', 'afis': 'https://image.tmdb.org/t/p/w500/xhJtYVTsdXQCIlB5hAXkMCPUG9y.jpg'},
    {'id': 196, 'isim': 'Watchmen', 'afis': 'https://image.tmdb.org/t/p/w500/m8rWq3j73ZGhDuSCZWMMoE9ePH1.jpg'},
    {'id': 197, 'isim': '11.22.63', 'afis': 'https://image.tmdb.org/t/p/w500/1fH41ccMKvgDTbbcCxWWH6fznah.jpg'},
    {'id': 198, 'isim': 'Gen V', 'afis': 'https://image.tmdb.org/t/p/w500/tEv842Nd5uMSavURG4aQO1pNtst.jpg'},
    {'id': 199, 'isim': 'Beef', 'afis': 'https://image.tmdb.org/t/p/w500/4b4v7RnPhNyPEaVGFarEuo74r8W.jpg'},
    {'id': 200, 'isim': 'Behind Her Eyes', 'afis': 'https://image.tmdb.org/t/p/w500/sfd90NIf778KoBFmpdBTow4xTm7.jpg'}
]

sarkilar = [
    {'id': 1, 'isim': '069', 'klasor': '069'},
    {'id': 2, 'isim': '12 Dev Adam', 'klasor': '12 Dev Adam'},
    {'id': 3, 'isim': '12 Horas  Pra Você Acreditar (Ao Vivo)', 'klasor': '12 Horas  Pra Você Acreditar (Ao Vivo)'},
    {'id': 4, 'isim': '12 to 12', 'klasor': '12 to 12'},
    {'id': 5, 'isim': '1999 Pt. III', 'klasor': '1999 Pt. III'},
    {'id': 6, 'isim': '360', 'klasor': '360'},
    {'id': 7, 'isim': '4h44', 'klasor': '4h44'},
    {'id': 8, 'isim': '505', 'klasor': '505'},
    {'id': 9, 'isim': '6 Months Later', 'klasor': '6 Months Later'},
    {'id': 10, 'isim': '7 Years', 'klasor': '7 Years'},
    {'id': 11, 'isim': 'A Bar Song (Tipsy)', 'klasor': 'A Bar Song (Tipsy)'},
    {'id': 12, 'isim': 'A Holly Jolly Christmas', 'klasor': 'A Holly Jolly Christmas'},
    {'id': 13, 'isim': 'A Little While', 'klasor': 'A Little While'},
    {'id': 14, 'isim': 'A Wizard Needs A Beard', 'klasor': 'A Wizard Needs A Beard'},
    {'id': 15, 'isim': 'AKON', 'klasor': 'AKON'},
    {'id': 16, 'isim': 'APPELLE TA COPINE', 'klasor': 'APPELLE TA COPINE'},
    {'id': 17, 'isim': 'APT', 'klasor': 'APT'},
    {'id': 18, 'isim': 'Abone', 'klasor': 'Abone'},
    {'id': 19, 'isim': 'Abracadabra', 'klasor': 'Abracadabra'},
    {'id': 20, 'isim': 'Addicted', 'klasor': 'Addicted'},
    {'id': 21, 'isim': 'Adorei', 'klasor': 'Adorei'},
    {'id': 22, 'isim': 'Adriano', 'klasor': 'Adriano'},
    {'id': 23, 'isim': 'Afedersin', 'klasor': 'Afedersin'},
    {'id': 24, 'isim': 'Affet', 'klasor': 'Affet'},
    {'id': 25, 'isim': 'Afili Yalnızlık', 'klasor': 'Afili Yalnızlık'},
    {'id': 26, 'isim': 'After All The Bars Are Closed', 'klasor': 'After All The Bars Are Closed'},
    {'id': 27, 'isim': 'Ai Se Eu Te Pego', 'klasor': 'Ai Se Eu Te Pego'},
    {'id': 28, 'isim': 'Aldatıldık', 'klasor': 'Aldatıldık'},
    {'id': 29, 'isim': 'All Day and All of the Night', 'klasor': 'All Day and All of the Night'},
    {'id': 30, 'isim': 'All I Want for Christmas Is You', 'klasor': 'All I Want for Christmas Is You'},
    {'id': 31, 'isim': 'All My Exes', 'klasor': 'All My Exes'},
    {'id': 32, 'isim': 'All die schönen Worte', 'klasor': 'All die schönen Worte'},
    {'id': 33, 'isim': 'All of Me', 'klasor': 'All of Me'},
    {'id': 34, 'isim': 'Alla fine del mondo (Final Version)', 'klasor': 'Alla fine del mondo (Final Version)'},
    {'id': 35, 'isim': 'Alone', 'klasor': 'Alone'},
    {'id': 36, 'isim': 'Am I Okay', 'klasor': 'Am I Okay'},
    {'id': 37, 'isim': 'Ama Um Maloqueiro', 'klasor': 'Ama Um Maloqueiro'},
    {'id': 38, 'isim': 'Amanhã  Loucura do Seu Coração (Ao Vivo)', 'klasor': 'Amanhã  Loucura do Seu Coração (Ao Vivo)'},
    {'id': 39, 'isim': 'Amigo Da Minha Saudade (Ao Vivo)', 'klasor': 'Amigo Da Minha Saudade (Ao Vivo)'},
    {'id': 40, 'isim': 'Amorfoda', 'klasor': 'Amorfoda'},
    {'id': 41, 'isim': 'Amárrame', 'klasor': 'Amárrame'},
    {'id': 42, 'isim': 'And When I Die', 'klasor': 'And When I Die'},
    {'id': 43, 'isim': 'Animals', 'klasor': 'Animals'},
    {'id': 44, 'isim': 'Another Love', 'klasor': 'Another Love'},
    {'id': 45, 'isim': 'Another Saturday Night', 'klasor': 'Another Saturday Night'},
    {'id': 46, 'isim': 'Anxiety', 'klasor': 'Anxiety'},
    {'id': 47, 'isim': 'Apaga Apaga Apaga (Ao Vivo)', 'klasor': 'Apaga Apaga Apaga (Ao Vivo)'},
    {'id': 48, 'isim': 'Apaguei Pra Todos (Ao Vivo)', 'klasor': 'Apaguei Pra Todos (Ao Vivo)'},
    {'id': 49, 'isim': 'Apologize', 'klasor': 'Apologize'},
    {'id': 50, 'isim': 'Apple', 'klasor': 'Apple'},
    {'id': 51, 'isim': 'Aquele Lugar (Ao Vivo)', 'klasor': 'Aquele Lugar (Ao Vivo)'},
    {'id': 52, 'isim': 'Arap Saçı', 'klasor': 'Arap Saçı'},
    {'id': 53, 'isim': 'Arnavut Kaldırımı', 'klasor': 'Arnavut Kaldırımı'},
    {'id': 54, 'isim': 'Arrullo De Estrellas', 'klasor': 'Arrullo De Estrellas'},
    {'id': 55, 'isim': 'As It Was', 'klasor': 'As It Was'},
    {'id': 56, 'isim': 'As Tears Go By (Original Single Mono Version)', 'klasor': 'As Tears Go By (Original Single Mono Version)'},
    {'id': 57, 'isim': 'Ateşini Yolla Bana', 'klasor': 'Ateşini Yolla Bana'},
    {'id': 58, 'isim': 'Atlantic Postcard', 'klasor': 'Atlantic Postcard'},
    {'id': 59, 'isim': 'Attention', 'klasor': 'Attention'},
    {'id': 60, 'isim': 'Ay İnanmıyorum', 'klasor': 'Ay İnanmıyorum'},
    {'id': 61, 'isim': 'Aya Benzer', 'klasor': 'Aya Benzer'},
    {'id': 62, 'isim': 'Azizam', 'klasor': 'Azizam'},
    {'id': 63, 'isim': 'Azul', 'klasor': 'Azul'},
    {'id': 64, 'isim': 'Aşk Nereden Nereye', 'klasor': 'Aşk Nereden Nereye'},
    {'id': 65, 'isim': 'Aşk Şarkısı', 'klasor': 'Aşk Şarkısı'},
    {'id': 66, 'isim': 'BEIBY (Remix)', 'klasor': 'BEIBY (Remix)'},
    {'id': 67, 'isim': 'BIRDS OF A FEATHER', 'klasor': 'BIRDS OF A FEATHER'},
    {'id': 68, 'isim': 'BLOQUÉ', 'klasor': 'BLOQUÉ'},
    {'id': 69, 'isim': 'BMF', 'klasor': 'BMF'},
    {'id': 70, 'isim': 'Back in the Saddle', 'klasor': 'Back in the Saddle'},
    {'id': 71, 'isim': 'Back to Black', 'klasor': 'Back to Black'},
    {'id': 72, 'isim': 'Backup Plan', 'klasor': 'Backup Plan'},
    {'id': 73, 'isim': 'Bad As I Used To Be (From F1® The Movie)', 'klasor': 'Bad As I Used To Be (From F1® The Movie)'},
    {'id': 74, 'isim': 'Bad Day', 'klasor': 'Bad Day'},
    {'id': 75, 'isim': 'Bad Dreams', 'klasor': 'Bad Dreams'},
    {'id': 76, 'isim': 'Bad Guy', 'klasor': 'Bad Guy'},
    {'id': 77, 'isim': 'Bad Habit', 'klasor': 'Bad Habit'},
    {'id': 78, 'isim': 'Baggage', 'klasor': 'Baggage'},
    {'id': 79, 'isim': 'Baila Conmigo', 'klasor': 'Baila Conmigo'},
    {'id': 80, 'isim': 'Bangır Bangır', 'klasor': 'Bangır Bangır'},
    {'id': 81, 'isim': 'Baqueado (Ao Vivo)', 'klasor': 'Baqueado (Ao Vivo)'},
    {'id': 82, 'isim': 'Batsın Bu Dünya', 'klasor': 'Batsın Bu Dünya'},
    {'id': 83, 'isim': 'Baytar', 'klasor': 'Baytar'},
    {'id': 84, 'isim': 'Be Adam', 'klasor': 'Be Adam'},
    {'id': 85, 'isim': 'Beard Revolution', 'klasor': 'Beard Revolution'},
    {'id': 86, 'isim': 'Beautiful People', 'klasor': 'Beautiful People'},
    {'id': 87, 'isim': 'Beautiful People (feat. Khalid)', 'klasor': 'Beautiful People (feat. Khalid)'},
    {'id': 88, 'isim': 'Beautiful Things', 'klasor': 'Beautiful Things'},
    {'id': 89, 'isim': 'Bebe e Vem Me Procurar  Quem Ama Sente Saudade (Ao Vivo)', 'klasor': 'Bebe e Vem Me Procurar  Quem Ama Sente Saudade (Ao Vivo)'},
    {'id': 90, 'isim': 'Because of You', 'klasor': 'Because of You'},
    {'id': 91, 'isim': 'Before You Go', 'klasor': 'Before You Go'},
    {'id': 92, 'isim': 'Behind Blue Eyes', 'klasor': 'Behind Blue Eyes'},
    {'id': 93, 'isim': 'Believer', 'klasor': 'Believer'},
    {'id': 94, 'isim': 'Belki Üstümüzden Bir Kuş Geçer', 'klasor': 'Belki Üstümüzden Bir Kuş Geçer'},
    {'id': 95, 'isim': 'Belong Together', 'klasor': 'Belong Together'},
    {'id': 96, 'isim': 'Ben Böyleyim', 'klasor': 'Ben Böyleyim'},
    {'id': 97, 'isim': 'Benimle Oynama', 'klasor': 'Benimle Oynama'},
    {'id': 98, 'isim': 'Better Me For You (Brown Eyes)', 'klasor': 'Better Me For You (Brown Eyes)'},
    {'id': 99, 'isim': 'Bi Tek Ben Anlarım', 'klasor': 'Bi Tek Ben Anlarım'},
    {'id': 100, 'isim': 'Big Bearded Bruce', 'klasor': 'Big Bearded Bruce'},
    {'id': 101, 'isim': 'Billie Jean', 'klasor': 'Billie Jean'},
    {'id': 102, 'isim': 'Bilmem Mi', 'klasor': 'Bilmem Mi'},
    {'id': 103, 'isim': 'Bilmiyorsun', 'klasor': 'Bilmiyorsun'},
    {'id': 104, 'isim': 'Bir Derdim Var', 'klasor': 'Bir Derdim Var'},
    {'id': 105, 'isim': 'Bir Kadın Çizeceksin', 'klasor': 'Bir Kadın Çizeceksin'},
    {'id': 106, 'isim': 'Bitter Sweet Symphony', 'klasor': 'Bitter Sweet Symphony'},
    {'id': 107, 'isim': 'Bizimkisi Bir Aşk Hikayesi', 'klasor': 'Bizimkisi Bir Aşk Hikayesi'},
    {'id': 108, 'isim': 'Black Magic Woman', 'klasor': 'Black Magic Woman'},
    {'id': 109, 'isim': 'Bleeding Love', 'klasor': 'Bleeding Love'},
    {'id': 110, 'isim': 'Blinding Lights', 'klasor': 'Blinding Lights'},
    {'id': 111, 'isim': 'Body', 'klasor': 'Body'},
    {'id': 112, 'isim': 'Body Splash (Ao Vivo)', 'klasor': 'Body Splash (Ao Vivo)'},
    {'id': 113, 'isim': 'Bonbon', 'klasor': 'Bonbon'},
    {'id': 114, 'isim': 'Boom (feat. MOTi, Ty Dolla $ign, Wizkid & Kranium)', 'klasor': 'Boom (feat. MOTi, Ty Dolla $ign, Wizkid & Kranium)'},
    {'id': 115, 'isim': 'Born in the U.S.A', 'klasor': 'Born in the U.S.A'},
    {'id': 116, 'isim': 'Bottle Rockets (feat. Hootie & The Blowfish)', 'klasor': 'Bottle Rockets (feat. Hootie & The Blowfish)'},
    {'id': 117, 'isim': 'Boulevard of Broken Dreams', 'klasor': 'Boulevard of Broken Dreams'},
    {'id': 118, 'isim': 'Breaking the Habit', 'klasor': 'Breaking the Habit'},
    {'id': 119, 'isim': 'Briller (Golden - version française)', 'klasor': 'Briller (Golden - version française)'},
    {'id': 120, 'isim': 'Bring Me To Life', 'klasor': 'Bring Me To Life'},
    {'id': 121, 'isim': 'Broken', 'klasor': 'Broken'},
    {'id': 122, 'isim': 'Bu Sabahların Bir Anlamı Olmalı', 'klasor': 'Bu Sabahların Bir Anlamı Olmalı'},
    {'id': 123, 'isim': 'Budapest', 'klasor': 'Budapest'},
    {'id': 124, 'isim': 'Burning Blue', 'klasor': 'Burning Blue'},
    {'id': 125, 'isim': 'Bênçãos Que Não Têm Fim (Counting My Blessings)', 'klasor': 'Bênçãos Que Não Têm Fim (Counting My Blessings)'},
    {'id': 126, 'isim': 'CARTIER SANTOS', 'klasor': 'CARTIER SANTOS'},
    {'id': 127, 'isim': 'CIEL', 'klasor': 'CIEL'},
    {'id': 128, 'isim': 'Caddelerde Rüzgar', 'klasor': 'Caddelerde Rüzgar'},
    {'id': 129, 'isim': 'Calma (Alan Walker Remix)', 'klasor': 'Calma (Alan Walker Remix)'},
    {'id': 130, 'isim': 'Cambaz', 'klasor': 'Cambaz'},
    {'id': 131, 'isim': 'Cantada Boba (Ao Vivo)', 'klasor': 'Cantada Boba (Ao Vivo)'},
    {'id': 132, 'isim': 'Caos De Alguém (Ao Vivo)', 'klasor': 'Caos De Alguém (Ao Vivo)'},
    {'id': 133, 'isim': 'Carrie Anne (Remastered)', 'klasor': 'Carrie Anne (Remastered)'},
    {'id': 134, 'isim': 'Carry On (from the Original Motion Picture POKÉMON Detective Pikachu)', 'klasor': 'Carry On (from the Original Motion Picture POKÉMON Detective Pikachu)'},
    {'id': 135, 'isim': 'Cartel', 'klasor': 'Cartel'},
    {'id': 136, 'isim': 'Catalina', 'klasor': 'Catalina'},
    {'id': 137, 'isim': 'Century', 'klasor': 'Century'},
    {'id': 138, 'isim': 'Cevapsız Sorular', 'klasor': 'Cevapsız Sorular'},
    {'id': 139, 'isim': 'Cevapsız Çınlama', 'klasor': 'Cevapsız Çınlama'},
    {'id': 140, 'isim': 'Chabos wissen wer der Babo ist', 'klasor': 'Chabos wissen wer der Babo ist'},
    {'id': 141, 'isim': 'Chandelier', 'klasor': 'Chandelier'},
    {'id': 142, 'isim': 'Charger (feat. MC YOSHI, Mauvais djo & Kokosvoice)', 'klasor': 'Charger (feat. MC YOSHI, Mauvais djo & Kokosvoice)'},
    {'id': 143, 'isim': 'Cheap Thrills', 'klasor': 'Cheap Thrills'},
    {'id': 144, 'isim': 'Cheerleader (Felix Jaehn Remix) (Radio Edit)', 'klasor': 'Cheerleader (Felix Jaehn Remix) (Radio Edit)'},
    {'id': 145, 'isim': 'Christmas (Baby Please Come Home)', 'klasor': 'Christmas (Baby Please Come Home)'},
    {'id': 146, 'isim': 'Christmas All Over Again', 'klasor': 'Christmas All Over Again'},
    {'id': 147, 'isim': 'Christmas Lights', 'klasor': 'Christmas Lights'},
    {'id': 148, 'isim': 'Christmas Tree Farm', 'klasor': 'Christmas Tree Farm'},
    {'id': 149, 'isim': 'Christmas Wrapping', 'klasor': 'Christmas Wrapping'},
    {'id': 150, 'isim': 'Classic', 'klasor': 'Classic'},
    {'id': 151, 'isim': 'Coco Chanel', 'klasor': 'Coco Chanel'},
    {'id': 152, 'isim': 'Coco Jamboo', 'klasor': 'Coco Jamboo'},
    {'id': 153, 'isim': 'Come As You Are', 'klasor': 'Come As You Are'},
    {'id': 154, 'isim': 'Complicated', 'klasor': 'Complicated'},
    {'id': 155, 'isim': 'Congratulations', 'klasor': 'Congratulations'},
    {'id': 156, 'isim': 'Coração Partido (Corazón Partío) (Ao Vivo)', 'klasor': 'Coração Partido (Corazón Partío) (Ao Vivo)'},
    {'id': 157, 'isim': 'Count on Me', 'klasor': 'Count on Me'},
    {'id': 158, 'isim': 'Counting Stars', 'klasor': 'Counting Stars'},
    {'id': 159, 'isim': 'Crawling', 'klasor': 'Crawling'},
    {'id': 160, 'isim': 'Crazy', 'klasor': 'Crazy'},
    {'id': 161, 'isim': 'Creep', 'klasor': 'Creep'},
    {'id': 162, 'isim': 'Cronômetro (Ao Vivo)', 'klasor': 'Cronômetro (Ao Vivo)'},
    {'id': 163, 'isim': 'Cry Me a River', 'klasor': 'Cry Me a River'},
    {'id': 164, 'isim': 'Cumhuriyet', 'klasor': 'Cumhuriyet'},
    {'id': 165, 'isim': 'Cópia Proibida', 'klasor': 'Cópia Proibida'},
    {'id': 166, 'isim': 'DAISIES', 'klasor': 'DAISIES'},
    {'id': 167, 'isim': 'DO U WANNA', 'klasor': 'DO U WANNA'},
    {'id': 168, 'isim': 'DUELE EL CORAZON (feat. Wisin)', 'klasor': 'DUELE EL CORAZON (feat. Wisin)'},
    {'id': 169, 'isim': 'Dance Monkey', 'klasor': 'Dance Monkey'},
    {'id': 170, 'isim': 'Dansöz', 'klasor': 'Dansöz'},
    {'id': 171, 'isim': 'Danza Kuduro', 'klasor': 'Danza Kuduro'},
    {'id': 172, 'isim': 'Dark Thoughts', 'klasor': 'Dark Thoughts'},
    {'id': 173, 'isim': 'Darkside', 'klasor': 'Darkside'},
    {'id': 174, 'isim': 'Dat Du Min Leefste Büst', 'klasor': 'Dat Du Min Leefste Büst'},
    {'id': 175, 'isim': 'Deixa Eu (Ao Vivo)', 'klasor': 'Deixa Eu (Ao Vivo)'},
    {'id': 176, 'isim': 'Delikanlım', 'klasor': 'Delikanlım'},
    {'id': 177, 'isim': 'Demet Akalın', 'klasor': 'Demet Akalın'},
    {'id': 178, 'isim': 'Demons', 'klasor': 'Demons'},
    {'id': 179, 'isim': 'Depresyondayım', 'klasor': 'Depresyondayım'},
    {'id': 180, 'isim': 'Değmesin Ellerimiz', 'klasor': 'Değmesin Ellerimiz'},
    {'id': 181, 'isim': 'Die On This Hill', 'klasor': 'Die On This Hill'},
    {'id': 182, 'isim': 'Die With A Smile', 'klasor': 'Die With A Smile'},
    {'id': 183, 'isim': 'Diet Pepsi', 'klasor': 'Diet Pepsi'},
    {'id': 184, 'isim': 'Diferentão', 'klasor': 'Diferentão'},
    {'id': 185, 'isim': 'Dinle Beni Bi', 'klasor': 'Dinle Beni Bi'},
    {'id': 186, 'isim': 'Do I Wanna Know', 'klasor': 'Do I Wanna Know'},
    {'id': 187, 'isim': 'Do You Hear What I Hear', 'klasor': 'Do You Hear What I Hear'},
    {'id': 188, 'isim': 'Doktor', 'klasor': 'Doktor'},
    {'id': 189, 'isim': 'Dolce Camara', 'klasor': 'Dolce Camara'},
    {'id': 190, 'isim': "Don't You Worry Child", 'klasor': "Don't You Worry Child"},
    {'id': 191, 'isim': 'Don’t Look Back in Anger', 'klasor': 'Don’t Look Back in Anger'},
    {'id': 192, 'isim': 'Don’t Start Now', 'klasor': 'Don’t Start Now'},
    {'id': 193, 'isim': 'Down Under', 'klasor': 'Down Under'},
    {'id': 194, 'isim': 'Dracula', 'klasor': 'Dracula'},
    {'id': 195, 'isim': 'Dripping Sun', 'klasor': 'Dripping Sun'},
    {'id': 196, 'isim': 'Driving Home for Christmas', 'klasor': 'Driving Home for Christmas'},
    {'id': 197, 'isim': 'DtMF', 'klasor': 'DtMF'},
    {'id': 198, 'isim': 'Duvido', 'klasor': 'Duvido'},
    {'id': 199, 'isim': 'Dönence', 'klasor': 'Dönence'},
    {'id': 200, 'isim': 'Düm Tek Tek', 'klasor': 'Düm Tek Tek'},
    {'id': 201, 'isim': 'Eastside', 'klasor': 'Eastside'},
    {'id': 202, 'isim': 'Ebony And Ivory', 'klasor': 'Ebony And Ivory'},
    {'id': 203, 'isim': 'Ein Stern (der deinen Namen trägt) (Radio Mix)', 'klasor': 'Ein Stern (der deinen Namen trägt) (Radio Mix)'},
    {'id': 204, 'isim': 'Ein letztes Mal', 'klasor': 'Ein letztes Mal'},
    {'id': 205, 'isim': 'Ela (Ao Vivo)', 'klasor': 'Ela (Ao Vivo)'},
    {'id': 206, 'isim': 'Elastic Heart', 'klasor': 'Elastic Heart'},
    {'id': 207, 'isim': 'Ele Güne Karşı', 'klasor': 'Ele Güne Karşı'},
    {'id': 208, 'isim': 'Elfida', 'klasor': 'Elfida'},
    {'id': 209, 'isim': 'Elizabeth Taylor', 'klasor': 'Elizabeth Taylor'},
    {'id': 210, 'isim': 'Em Busca Da Minha Sorte (Ao Vivo)', 'klasor': 'Em Busca Da Minha Sorte (Ao Vivo)'},
    {'id': 211, 'isim': 'End of Beginning', 'klasor': 'End of Beginning'},
    {'id': 212, 'isim': 'End of the World', 'klasor': 'End of the World'},
    {'id': 213, 'isim': 'Endamın Yeter', 'klasor': 'Endamın Yeter'},
    {'id': 214, 'isim': 'Es schneit', 'klasor': 'Es schneit'},
    {'id': 215, 'isim': 'Escondendo o Ouro (Ao Vivo)', 'klasor': 'Escondendo o Ouro (Ao Vivo)'},
    {'id': 216, 'isim': 'Espresso', 'klasor': 'Espresso'},
    {'id': 217, 'isim': 'Eternity', 'klasor': 'Eternity'},
    {'id': 218, 'isim': 'Eu Me Apaixonei', 'klasor': 'Eu Me Apaixonei'},
    {'id': 219, 'isim': 'Eu Te Seguro', 'klasor': 'Eu Te Seguro'},
    {'id': 220, 'isim': 'Eu Vou na Sua Casa', 'klasor': 'Eu Vou na Sua Casa'},
    {'id': 221, 'isim': 'Everyway That I Can', 'klasor': 'Everyway That I Can'},
    {'id': 222, 'isim': 'Eye of the Tiger', 'klasor': 'Eye of the Tiger'},
    {'id': 223, 'isim': 'FAMOSINHA', 'klasor': 'FAMOSINHA'},
    {'id': 224, 'isim': 'FASHION DESIGNA', 'klasor': 'FASHION DESIGNA'},
    {'id': 225, 'isim': 'FUXWAVE', 'klasor': 'FUXWAVE'},
    {'id': 226, 'isim': 'Faded', 'klasor': 'Faded'},
    {'id': 227, 'isim': 'Fairytale of New York (feat. Kirsty MacColl)', 'klasor': 'Fairytale of New York (feat. Kirsty MacColl)'},
    {'id': 228, 'isim': 'Fallen in Liebe', 'klasor': 'Fallen in Liebe'},
    {'id': 229, 'isim': 'Faut pas', 'klasor': 'Faut pas'},
    {'id': 230, 'isim': 'Feel Good', 'klasor': 'Feel Good'},
    {'id': 231, 'isim': 'Feel Good Inc', 'klasor': 'Feel Good Inc'},
    {'id': 232, 'isim': 'Felaket', 'klasor': 'Felaket'},
    {'id': 233, 'isim': 'Feliz Navidad', 'klasor': 'Feliz Navidad'},
    {'id': 234, 'isim': 'Fesuphanallah', 'klasor': 'Fesuphanallah'},
    {'id': 235, 'isim': 'Fica com Deus (Ao Vivo)', 'klasor': 'Fica com Deus (Ao Vivo)'},
    {'id': 236, 'isim': 'Fireflies', 'klasor': 'Fireflies'},
    {'id': 237, 'isim': 'Fix You', 'klasor': 'Fix You'},
    {'id': 238, 'isim': 'Flowers', 'klasor': 'Flowers'},
    {'id': 239, 'isim': 'Flying Blue', 'klasor': 'Flying Blue'},
    {'id': 240, 'isim': 'Frei wie der Wind', 'klasor': 'Frei wie der Wind'},
    {'id': 241, 'isim': 'Für immer', 'klasor': 'Für immer'},
    {'id': 242, 'isim': 'Fırtınam', 'klasor': 'Fırtınam'},
    {'id': 243, 'isim': 'Gabriela', 'klasor': 'Gabriela'},
    {'id': 244, 'isim': 'Galiba', 'klasor': 'Galiba'},
    {'id': 245, 'isim': 'Gangnam Style', 'klasor': 'Gangnam Style'},
    {'id': 246, 'isim': 'Gasolina', 'klasor': 'Gasolina'},
    {'id': 247, 'isim': 'Geceler', 'klasor': 'Geceler'},
    {'id': 248, 'isim': 'Gegenteil von Glück', 'klasor': 'Gegenteil von Glück'},
    {'id': 249, 'isim': 'Gel Gel', 'klasor': 'Gel Gel'},
    {'id': 250, 'isim': 'Georgina', 'klasor': 'Georgina'},
    {'id': 251, 'isim': 'Geri Dön', 'klasor': 'Geri Dön'},
    {'id': 252, 'isim': 'Get Lucky', 'klasor': 'Get Lucky'},
    {'id': 253, 'isim': 'Ghost', 'klasor': 'Ghost'},
    {'id': 254, 'isim': 'Girls Like You', 'klasor': 'Girls Like You'},
    {'id': 255, 'isim': 'Gitme', 'klasor': 'Gitme'},
    {'id': 256, 'isim': 'Give Me Everything', 'klasor': 'Give Me Everything'},
    {'id': 257, 'isim': 'Godzilla', 'klasor': 'Godzilla'},
    {'id': 258, 'isim': 'Golden', 'klasor': 'Golden'},
    {'id': 259, 'isim': 'Good Luck, Babe!', 'klasor': 'Good Luck, Babe!'},
    {'id': 260, 'isim': 'Good News', 'klasor': 'Good News'},
    {'id': 261, 'isim': 'Good Times & Tan Lines', 'klasor': 'Good Times & Tan Lines'},
    {'id': 262, 'isim': 'Grau de Maluca', 'klasor': 'Grau de Maluca'},
    {'id': 263, 'isim': 'Grenade', 'klasor': 'Grenade'},
    {'id': 264, 'isim': 'Growing A Beard', 'klasor': 'Growing A Beard'},
    {'id': 265, 'isim': 'Génération impolie', 'klasor': 'Génération impolie'},
    {'id': 266, 'isim': 'Gözlerin', 'klasor': 'Gözlerin'},
    {'id': 267, 'isim': 'Gülpembe', 'klasor': 'Gülpembe'},
    {'id': 268, 'isim': 'Gülümse', 'klasor': 'Gülümse'},
    {'id': 269, 'isim': 'Halts Maul und spiel', 'klasor': 'Halts Maul und spiel'},
    {'id': 270, 'isim': 'Happier', 'klasor': 'Happier'},
    {'id': 271, 'isim': 'Happy (From Despicable Me 2)', 'klasor': 'Happy (From Despicable Me 2)'},
    {'id': 272, 'isim': 'Happy Xmas (War Is Over) (Remastered 2010)', 'klasor': 'Happy Xmas (War Is Over) (Remastered 2010)'},
    {'id': 273, 'isim': 'Havana', 'klasor': 'Havana'},
    {'id': 274, 'isim': 'Haverá Sinais (Ao Vivo)', 'klasor': 'Haverá Sinais (Ao Vivo)'},
    {'id': 275, 'isim': 'Haydi Gel İçelim', 'klasor': 'Haydi Gel İçelim'},
    {'id': 276, 'isim': 'Haydi Söyle', 'klasor': 'Haydi Söyle'},
    {'id': 277, 'isim': 'Heart of Stone', 'klasor': 'Heart of Stone'},
    {'id': 278, 'isim': 'Heat Waves', 'klasor': 'Heat Waves'},
    {'id': 279, 'isim': 'Heathens', 'klasor': 'Heathens'},
    {'id': 280, 'isim': 'Heavy Cross', 'klasor': 'Heavy Cross'},
    {'id': 281, 'isim': 'Hele Bi Gel', 'klasor': 'Hele Bi Gel'},
    {'id': 282, 'isim': 'Her Şeyi Yak', 'klasor': 'Her Şeyi Yak'},
    {'id': 283, 'isim': 'Hercai', 'klasor': 'Hercai'},
    {'id': 284, 'isim': 'Here With Me', 'klasor': 'Here With Me'},
    {'id': 285, 'isim': 'Here Without You', 'klasor': 'Here Without You'},
    {'id': 286, 'isim': 'Hero', 'klasor': 'Hero'},
    {'id': 287, 'isim': 'Hey Ya!', 'klasor': 'Hey Ya!'},
    {'id': 288, 'isim': 'Hey, Soul Sister', 'klasor': 'Hey, Soul Sister'},
    {'id': 289, 'isim': 'Holly Jolly Christmas', 'klasor': 'Holly Jolly Christmas'},
    {'id': 290, 'isim': 'Holy Water', 'klasor': 'Holy Water'},
    {'id': 291, 'isim': 'Homage', 'klasor': 'Homage'},
    {'id': 292, 'isim': 'Home', 'klasor': 'Home'},
    {'id': 293, 'isim': 'Homem É Homem, Moleque É Moleque', 'klasor': 'Homem É Homem, Moleque É Moleque'},
    {'id': 294, 'isim': 'Honey, Honey', 'klasor': 'Honey, Honey'},
    {'id': 295, 'isim': 'Hot N Cold', 'klasor': 'Hot N Cold'},
    {'id': 296, 'isim': 'Hotline Bling', 'klasor': 'Hotline Bling'},
    {'id': 297, 'isim': 'Houdini', 'klasor': 'Houdini'},
    {'id': 298, 'isim': 'How It’s Done', 'klasor': 'How It’s Done'},
    {'id': 299, 'isim': 'How You Remind Me', 'klasor': 'How You Remind Me'},
    {'id': 300, 'isim': 'Hoşçakal', 'klasor': 'Hoşçakal'},
    {'id': 301, 'isim': 'Hurt', 'klasor': 'Hurt'},
    {'id': 302, 'isim': 'Hymn for the Weekend', 'klasor': 'Hymn for the Weekend'},
    {'id': 303, 'isim': 'I Can Do It With a Broken Heart', 'klasor': 'I Can Do It With a Broken Heart'},
    {'id': 304, 'isim': 'I Follow Rivers (The Magician Remix)', 'klasor': 'I Follow Rivers (The Magician Remix)'},
    {'id': 305, 'isim': 'I Got Better', 'klasor': 'I Got Better'},
    {'id': 306, 'isim': 'I Had Some Help', 'klasor': 'I Had Some Help'},
    {'id': 307, 'isim': 'I Kissed A Girl', 'klasor': 'I Kissed A Girl'},
    {'id': 308, 'isim': 'I Run', 'klasor': 'I Run'},
    {'id': 309, 'isim': 'I Want It That Way', 'klasor': 'I Want It That Way'},
    {'id': 310, 'isim': 'I Will Always Love You', 'klasor': 'I Will Always Love You'},
    {'id': 311, 'isim': 'I Wish It Could Be Christmas Everyday', 'klasor': 'I Wish It Could Be Christmas Everyday'},
    {'id': 312, 'isim': 'ILS ME RIENT TOUS AU NEZ', 'klasor': 'ILS ME RIENT TOUS AU NEZ'},
    {'id': 313, 'isim': 'If The World Burns Down', 'klasor': 'If The World Burns Down'},
    {'id': 314, 'isim': 'If You Want To Sing Out, Sing Out', 'klasor': 'If You Want To Sing Out, Sing Out'},
    {'id': 315, 'isim': 'Ilusão De Ótica (Ao Vivo)', 'klasor': 'Ilusão De Ótica (Ao Vivo)'},
    {'id': 316, 'isim': 'Impardonnable', 'klasor': 'Impardonnable'},
    {'id': 317, 'isim': 'In Da Club', 'klasor': 'In Da Club'},
    {'id': 318, 'isim': 'In The Shadows', 'klasor': 'In The Shadows'},
    {'id': 319, 'isim': 'In der Weihnachtsbäckerei', 'klasor': 'In der Weihnachtsbäckerei'},
    {'id': 320, 'isim': 'In the End', 'klasor': 'In the End'},
    {'id': 321, 'isim': 'Industry Baby', 'klasor': 'Industry Baby'},
    {'id': 322, 'isim': 'Instructions', 'klasor': 'Instructions'},
    {'id': 323, 'isim': 'Iris', 'klasor': 'Iris'},
    {'id': 324, 'isim': 'Islak Islak', 'klasor': 'Islak Islak'},
    {'id': 325, 'isim': 'It Only Takes A Fortnight To Grow A Decent Beard', 'klasor': 'It Only Takes A Fortnight To Grow A Decent Beard'},
    {'id': 326, 'isim': 'I’m Not the Only One', 'klasor': 'I’m Not the Only One'},
    {'id': 327, 'isim': 'JAMAIS TOI', 'klasor': 'JAMAIS TOI'},
    {'id': 328, 'isim': 'Jejum de Amor  Caixa Postal  Vida Vazia (Ao Vivo)', 'klasor': 'Jejum de Amor  Caixa Postal  Vida Vazia (Ao Vivo)'},
    {'id': 329, 'isim': 'Jennifer Eccles (Remastered)', 'klasor': 'Jennifer Eccles (Remastered)'},
    {'id': 330, 'isim': 'Jingle Bells Rock', 'klasor': 'Jingle Bells Rock'},
    {'id': 331, 'isim': 'Joe le taxi', 'klasor': 'Joe le taxi'},
    {'id': 332, 'isim': 'Johnny B Goode (Live At Arie Crown Theater, ChicagoMarch 26, 1965)', 'klasor': 'Johnny B Goode (Live At Arie Crown Theater, ChicagoMarch 26, 1965)'},
    {'id': 333, 'isim': 'João 20 + pra Sempre - Ao Vivo', 'klasor': 'João 20 + pra Sempre - Ao Vivo'},
    {'id': 334, 'isim': 'Juna', 'klasor': 'Juna'},
    {'id': 335, 'isim': 'Just Give Me A Reason', 'klasor': 'Just Give Me A Reason'},
    {'id': 336, 'isim': 'Just In Case', 'klasor': 'Just In Case'},
    {'id': 337, 'isim': 'Just One Look (Remastered)', 'klasor': 'Just One Look (Remastered)'},
    {'id': 338, 'isim': 'KONGOLESE SOUS BBL', 'klasor': 'KONGOLESE SOUS BBL'},
    {'id': 339, 'isim': 'KYKY2BONDY', 'klasor': 'KYKY2BONDY'},
    {'id': 340, 'isim': 'Kafama Göre', 'klasor': 'Kafama Göre'},
    {'id': 341, 'isim': 'Kalbimin Tek Sahibine', 'klasor': 'Kalbimin Tek Sahibine'},
    {'id': 342, 'isim': 'Kanatlarım Var Ruhumda', 'klasor': 'Kanatlarım Var Ruhumda'},
    {'id': 343, 'isim': 'Karabiberim', 'klasor': 'Karabiberim'},
    {'id': 344, 'isim': 'Karma Police', 'klasor': 'Karma Police'},
    {'id': 345, 'isim': 'Kids', 'klasor': 'Kids'},
    {'id': 346, 'isim': 'King of Watches', 'klasor': 'King of Watches'},
    {'id': 347, 'isim': 'Kippenautomat', 'klasor': 'Kippenautomat'},
    {'id': 348, 'isim': 'Kirschblüten', 'klasor': 'Kirschblüten'},
    {'id': 349, 'isim': 'Knowing Me, Knowing You', 'klasor': 'Knowing Me, Knowing You'},
    {'id': 350, 'isim': 'Koca Yaşlı Şişko Dünya', 'klasor': 'Koca Yaşlı Şişko Dünya'},
    {'id': 351, 'isim': 'Korkma Kalbim', 'klasor': 'Korkma Kalbim'},
    {'id': 352, 'isim': 'Kuzu Kuzu', 'klasor': 'Kuzu Kuzu'},
    {'id': 353, 'isim': 'Kırmızı', 'klasor': 'Kırmızı'},
    {'id': 354, 'isim': 'Kış Güneşi', 'klasor': 'Kış Güneşi'},
    {'id': 355, 'isim': 'LA CANCIÓN', 'klasor': 'LA CANCIÓN'},
    {'id': 356, 'isim': 'LOVE YOU', 'klasor': 'LOVE YOU'},
    {'id': 357, 'isim': 'La classe', 'klasor': 'La classe'},
    {'id': 358, 'isim': 'La montagne', 'klasor': 'La montagne'},
    {'id': 359, 'isim': 'Lapada Dela (Ao Vivo)', 'klasor': 'Lapada Dela (Ao Vivo)'},
    {'id': 360, 'isim': 'Last Christmas', 'klasor': 'Last Christmas'},
    {'id': 361, 'isim': 'Lay Back in the Arms of Someone', 'klasor': 'Lay Back in the Arms of Someone'},
    {'id': 362, 'isim': 'Le métèque', 'klasor': 'Le métèque'},
    {'id': 363, 'isim': 'Lemonade', 'klasor': 'Lemonade'},
    {'id': 364, 'isim': 'Let Alone The One You Love', 'klasor': 'Let Alone The One You Love'},
    {'id': 365, 'isim': 'Let It Snow', 'klasor': 'Let It Snow'},
    {'id': 366, 'isim': 'Levels', 'klasor': 'Levels'},
    {'id': 367, 'isim': 'Levitating', 'klasor': 'Levitating'},
    {'id': 368, 'isim': 'Lindo Momento (Ao Vivo)', 'klasor': 'Lindo Momento (Ao Vivo)'},
    {'id': 369, 'isim': 'Listen to Me (Remastered)', 'klasor': 'Listen to Me (Remastered)'},
    {'id': 370, 'isim': 'Little Honda (Live At Arie Crown Theater, ChicagoMarch 26, 1965)', 'klasor': 'Little Honda (Live At Arie Crown Theater, ChicagoMarch 26, 1965)'},{'id': 371, 'isim': 'Live is Life', 'klasor': 'Live is Life'},
    {'id': 372, 'isim': 'Lo Tienes Todo', 'klasor': 'Lo Tienes Todo'},
    {'id': 373, 'isim': 'Lose Control', 'klasor': 'Lose Control'},
    {'id': 374, 'isim': 'Lose Yourself', 'klasor': 'Lose Yourself'},
    {'id': 375, 'isim': 'Losing My Religion', 'klasor': 'Losing My Religion'},
    {'id': 376, 'isim': 'Love Me Again', 'klasor': 'Love Me Again'},
    {'id': 377, 'isim': 'Love Me Not', 'klasor': 'Love Me Not'},
    {'id': 378, 'isim': 'Love Me To Heaven', 'klasor': 'Love Me To Heaven'},
    {'id': 379, 'isim': 'Love Somebody', 'klasor': 'Love Somebody'},
    {'id': 380, 'isim': 'Love Story', 'klasor': 'Love Story'},
    {'id': 381, 'isim': 'Love You Like A Love Song', 'klasor': 'Love You Like A Love Song'},
    {'id': 382, 'isim': 'Love the Way You Lie', 'klasor': 'Love the Way You Lie'},
    {'id': 383, 'isim': 'Lovely', 'klasor': 'Lovely'},
    {'id': 384, 'isim': 'Lovers Rock', 'klasor': 'Lovers Rock'},
    {'id': 385, 'isim': 'Low', 'klasor': 'Low'},
    {'id': 386, 'isim': 'Lush Life', 'klasor': 'Lush Life'},
    {'id': 387, 'isim': 'ME POSTOU NO DAILY - FESTA DO BIG G', 'klasor': 'ME POSTOU NO DAILY - FESTA DO BIG G'},
    {'id': 388, 'isim': 'MONTAGEM CAMERA LENTA', 'klasor': 'MONTAGEM CAMERA LENTA'},
    {'id': 389, 'isim': 'MUTT', 'klasor': 'MUTT'},
    {'id': 390, 'isim': 'Man I Need', 'klasor': 'Man I Need'},
    {'id': 391, 'isim': 'Manchild', 'klasor': 'Manchild'},
    {'id': 392, 'isim': 'Maria', 'klasor': 'Maria'},
    {'id': 393, 'isim': 'Maria (From West Side Story)', 'klasor': 'Maria (From West Side Story)'},
    {'id': 394, 'isim': 'Marlboro Mann', 'klasor': 'Marlboro Mann'},
    {'id': 395, 'isim': 'Martılar', 'klasor': 'Martılar'},
    {'id': 396, 'isim': 'Masterclass', 'klasor': 'Masterclass'},
    {'id': 397, 'isim': 'Mavi Mavi', 'klasor': 'Mavi Mavi'},
    {'id': 398, 'isim': 'Me Ama Ou Me Larga (Ao Vivo)', 'klasor': 'Me Ama Ou Me Larga (Ao Vivo)'},
    {'id': 399, 'isim': 'Me Apaixonei Nessa Morena', 'klasor': 'Me Apaixonei Nessa Morena'},
    {'id': 400, 'isim': 'Me Atraiu (Ao Vivo)', 'klasor': 'Me Atraiu (Ao Vivo)'},
    {'id': 401, 'isim': 'Me Bloqueia (Ao Vivo)', 'klasor': 'Me Bloqueia (Ao Vivo)'},
    {'id': 402, 'isim': 'Me gustas tanto', 'klasor': 'Me gustas tanto'},
    {'id': 403, 'isim': 'Mekanın Sahibi', 'klasor': 'Mekanın Sahibi'},
    {'id': 404, 'isim': 'Mele Kalikimaka (Single Version)', 'klasor': 'Mele Kalikimaka (Single Version)'},
    {'id': 405, 'isim': 'Melhor Amigo  O Que Seria de Mim (feat. Dimy Francisco & Eunice Zumbuca) (Ao Vivo)', 'klasor': 'Melhor Amigo  O Que Seria de Mim (feat. Dimy Francisco & Eunice Zumbuca) (Ao Vivo)'},
    {'id': 406, 'isim': 'Melzinho', 'klasor': 'Melzinho'},
    {'id': 407, 'isim': 'Memories', 'klasor': 'Memories'},
    {'id': 408, 'isim': 'Mentira Estampada', 'klasor': 'Mentira Estampada'},
    {'id': 409, 'isim': 'Merry Christmas', 'klasor': 'Merry Christmas'},
    {'id': 410, 'isim': 'Merry Christmas Everyone', 'klasor': 'Merry Christmas Everyone'},
    {'id': 411, 'isim': 'Messy', 'klasor': 'Messy'},
    {'id': 412, 'isim': 'Mi Buen Amor', 'klasor': 'Mi Buen Amor'},
    {'id': 413, 'isim': 'Mia', 'klasor': 'Mia'},
    {'id': 414, 'isim': 'Miles On It', 'klasor': 'Miles On It'},
    {'id': 415, 'isim': 'Mistletoe', 'klasor': 'Mistletoe'},
    {'id': 416, 'isim': 'Mockingbird', 'klasor': 'Mockingbird'},
    {'id': 417, 'isim': 'Mon bijou', 'klasor': 'Mon bijou'},
    {'id': 418, 'isim': 'Monaco', 'klasor': 'Monaco'},
    {'id': 419, 'isim': 'Money, Money, Money', 'klasor': 'Money, Money, Money'},
    {'id': 420, 'isim': 'Monsoon', 'klasor': 'Monsoon'},
    {'id': 421, 'isim': 'Mood', 'klasor': 'Mood'},
    {'id': 422, 'isim': 'Moon Undah Water', 'klasor': 'Moon Undah Water'},
    {'id': 423, 'isim': 'Moonshadow', 'klasor': 'Moonshadow'},
    {'id': 424, 'isim': 'Morning Has Broken', 'klasor': 'Morning Has Broken'},
    {'id': 425, 'isim': 'Move On', 'klasor': 'Move On'},
    {'id': 426, 'isim': 'Mr. Brightside', 'klasor': 'Mr. Brightside'},
    {'id': 427, 'isim': 'Mr. Vain Recall (Radio Edit)', 'klasor': 'Mr. Vain Recall (Radio Edit)'},
    {'id': 428, 'isim': 'Mrs. Robinson', 'klasor': 'Mrs. Robinson'},
    {'id': 429, 'isim': 'My Love Mine All Mine', 'klasor': 'My Love Mine All Mine'},
    {'id': 430, 'isim': 'NINAO', 'klasor': 'NINAO'},
    {'id': 431, 'isim': 'Naber', 'klasor': 'Naber'},
    {'id': 432, 'isim': 'Natural', 'klasor': 'Natural'},
    {'id': 433, 'isim': 'Nedo', 'klasor': 'Nedo'},
    {'id': 434, 'isim': 'New Rules', 'klasor': 'New Rules'},
    {'id': 435, 'isim': 'New Soul', 'klasor': 'New Soul'},
    {'id': 436, 'isim': 'Nice To Each Other', 'klasor': 'Nice To Each Other'},
    {'id': 437, 'isim': 'Nilüfer', 'klasor': 'Nilüfer'},
    {'id': 438, 'isim': 'No Broke Boys', 'klasor': 'No Broke Boys'},
    {'id': 439, 'isim': 'No Good Deed', 'klasor': 'No Good Deed'},
    {'id': 440, 'isim': 'No One Noticed', 'klasor': 'No One Noticed'},
    {'id': 441, 'isim': 'Nostalgique', 'klasor': 'Nostalgique'},
    {'id': 442, 'isim': 'Nothing Compares 2 U', 'klasor': 'Nothing Compares 2 U'},
    {'id': 443, 'isim': 'Nothing On You (feat. Paulo Londra & Dave)', 'klasor': 'Nothing On You (feat. Paulo Londra & Dave)'},
    {'id': 444, 'isim': 'Numb', 'klasor': 'Numb'},
    {'id': 445, 'isim': 'O Meu Coração Em Suas Mãos (Colgando en tu manos) (Ao Vivo)', 'klasor': 'O Meu Coração Em Suas Mãos (Colgando en tu manos) (Ao Vivo)'},
    {'id': 446, 'isim': 'O Que Eu Faço Agora', 'klasor': 'O Que Eu Faço Agora'},
    {'id': 447, 'isim': 'OLHO MARROM - Ao Vivo em Lisboa', 'klasor': 'OLHO MARROM - Ao Vivo em Lisboa'},
    {'id': 448, 'isim': 'Ocean Eyes', 'klasor': 'Ocean Eyes'},
    {'id': 449, 'isim': 'Olha Onde Eu Tô', 'klasor': 'Olha Onde Eu Tô'},
    {'id': 450, 'isim': 'On My Way', 'klasor': 'On My Way'},
    {'id': 451, 'isim': 'On The Floor', 'klasor': 'On The Floor'},
    {'id': 452, 'isim': 'One More Sleep', 'klasor': 'One More Sleep'},
    {'id': 453, 'isim': 'Only Girl (In The World)', 'klasor': 'Only Girl (In The World)'},
    {'id': 454, 'isim': 'Only You (And You Alone)', 'klasor': 'Only You (And You Alone)'},
    {'id': 455, 'isim': 'Opa Cadê Eu (Ao Vivo)', 'klasor': 'Opa Cadê Eu (Ao Vivo)'},
    {'id': 456, 'isim': 'Opalite', 'klasor': 'Opalite'},
    {'id': 457, 'isim': 'Ordinary', 'klasor': 'Ordinary'},
    {'id': 458, 'isim': 'Other Side of Paradise', 'klasor': 'Other Side of Paradise'},
    {'id': 459, 'isim': 'Otro Trago', 'klasor': 'Otro Trago'},
    {'id': 460, 'isim': 'Outro Personagem (Ao Vivo)', 'klasor': 'Outro Personagem (Ao Vivo)'},
    {'id': 461, 'isim': 'Ovelhinha (Ao Vivo)', 'klasor': 'Ovelhinha (Ao Vivo)'},
    {'id': 462, 'isim': 'P do Pecado (Ao Vivo)', 'klasor': 'P do Pecado (Ao Vivo)'},
    {'id': 463, 'isim': 'PAS LE CHOIX', 'klasor': 'PAS LE CHOIX'},
    {'id': 464, 'isim': 'PAY!', 'klasor': 'PAY!'},
    {'id': 465, 'isim': 'POUR ELLE', 'klasor': 'POUR ELLE'},
    {'id': 466, 'isim': 'Padişah', 'klasor': 'Padişah'},
    {'id': 467, 'isim': 'Paint The Town Red', 'klasor': 'Paint The Town Red'},
    {'id': 468, 'isim': 'Paname', 'klasor': 'Paname'},
    {'id': 469, 'isim': 'Paradise', 'klasor': 'Paradise'},
    {'id': 470, 'isim': 'Paramparça', 'klasor': 'Paramparça'},
    {'id': 471, 'isim': 'Paris', 'klasor': 'Paris'},
    {'id': 472, 'isim': 'Party Rock Anthem', 'klasor': 'Party Rock Anthem'},
    {'id': 473, 'isim': 'Peace Train', 'klasor': 'Peace Train'},
    {'id': 474, 'isim': 'Pela Última Vez (Ao Vivo)', 'klasor': 'Pela Última Vez (Ao Vivo)'},
    {'id': 475, 'isim': 'Pensando Em Você  Carta Branca  Amantes (Ao Vivo)', 'klasor': 'Pensando Em Você  Carta Branca  Amantes (Ao Vivo)'},
    {'id': 476, 'isim': 'Perfect', 'klasor': 'Perfect'},
    {'id': 477, 'isim': 'Phantom', 'klasor': 'Phantom'},
    {'id': 478, 'isim': 'Photograph', 'klasor': 'Photograph'},
    {'id': 479, 'isim': 'Phénoménal', 'klasor': 'Phénoménal'},
    {'id': 480, 'isim': 'Piano', 'klasor': 'Piano'},
    {'id': 481, 'isim': 'Pilantra e Meio', 'klasor': 'Pilantra e Meio'},
    {'id': 482, 'isim': 'Pink Pony Club', 'klasor': 'Pink Pony Club'},
    {'id': 483, 'isim': 'Please Please Please', 'klasor': 'Please Please Please'},
    {'id': 484, 'isim': 'Poker Face', 'klasor': 'Poker Face'},
    {'id': 485, 'isim': 'Pompeii', 'klasor': 'Pompeii'},
    {'id': 486, 'isim': 'Posso Até Não Te Dar Flores', 'klasor': 'Posso Até Não Te Dar Flores'},
    {'id': 487, 'isim': 'Post Malone (feat. RANI)', 'klasor': 'Post Malone (feat. RANI)'},
    {'id': 488, 'isim': 'Postcards', 'klasor': 'Postcards'},
    {'id': 489, 'isim': 'Pot-Pourri Melhor Eu Ir  Ligando Os Fatos  Sonho de Amor  Deixa Eu Te Querer (Ao Vivo)', 'klasor': 'Pot-Pourri Melhor Eu Ir  Ligando Os Fatos  Sonho de Amor  Deixa Eu Te Querer (Ao Vivo)'},
    {'id': 490, 'isim': 'Prenses', 'klasor': 'Prenses'},
    {'id': 491, 'isim': 'Proibido Terminar', 'klasor': 'Proibido Terminar'},
    {'id': 492, 'isim': 'Promiscuous', 'klasor': 'Promiscuous'},
    {'id': 493, 'isim': 'Prusya Mavisi', 'klasor': 'Prusya Mavisi'},
    {'id': 494, 'isim': 'Pump It', 'klasor': 'Pump It'},
    {'id': 495, 'isim': 'Pumped Up Kicks', 'klasor': 'Pumped Up Kicks'},
    {'id': 496, 'isim': 'Pélican', 'klasor': 'Pélican'},
    {'id': 497, 'isim': 'Pétunias', 'klasor': 'Pétunias'},
    {'id': 498, 'isim': 'Pırlanta', 'klasor': 'Pırlanta'},
    {'id': 499, 'isim': 'Quem É Esse (Ao Vivo)', 'klasor': 'Quem É Esse (Ao Vivo)'},
    {'id': 500, 'isim': 'Queria Ser Tu  Interfone (Ao Vivo)', 'klasor': 'Queria Ser Tu  Interfone (Ao Vivo)'},
    {'id': 501, 'isim': 'R U Mine', 'klasor': 'R U Mine'},
    {'id': 502, 'isim': 'RADW', 'klasor': 'RADW'},
    {'id': 503, 'isim': 'RUINART', 'klasor': 'RUINART'},
    {'id': 504, 'isim': 'Radioactive', 'klasor': 'Radioactive'},
    {'id': 505, 'isim': 'Rein Me In', 'klasor': 'Rein Me In'},
    {'id': 506, 'isim': 'Renegades', 'klasor': 'Renegades'},
    {'id': 507, 'isim': 'Resim', 'klasor': 'Resim'},
    {'id': 508, 'isim': 'Retrovisor', 'klasor': 'Retrovisor'},
    {'id': 509, 'isim': 'Ride', 'klasor': 'Ride'},
    {'id': 510, 'isim': 'Riptide', 'klasor': 'Riptide'},
    {'id': 511, 'isim': 'Rolling in the Deep', 'klasor': 'Rolling in the Deep'},
    {'id': 512, 'isim': 'Romeo', 'klasor': 'Romeo'},
    {'id': 513, 'isim': 'Romântico (Ao Vivo)', 'klasor': 'Romântico (Ao Vivo)'},
    {'id': 514, 'isim': 'Royals', 'klasor': 'Royals'},
    {'id': 515, 'isim': 'Ruby Tuesday (Original Single Mono Version)', 'klasor': 'Ruby Tuesday (Original Single Mono Version)'},
    {'id': 516, 'isim': 'Runaway', 'klasor': 'Runaway'},
    {'id': 517, 'isim': 'SALE ÉTAT', 'klasor': 'SALE ÉTAT'},
    {'id': 518, 'isim': 'SEQUÊNCIA CARAMELO', 'klasor': 'SEQUÊNCIA CARAMELO'},
    {'id': 519, 'isim': 'SEQUÊNCIA FEITICEIRA', 'klasor': 'SEQUÊNCIA FEITICEIRA'},
    {'id': 520, 'isim': 'SET DO JAPA NK 2.0 (feat. MC LUUKY, Mc Jacaré, MC Rodrigo do CN, MC GH do 7, Mc Lele JP, Mc Jvila & Oruam)', 'klasor': 'SET DO JAPA NK 2.0 (feat. MC LUUKY, Mc Jacaré, MC Rodrigo do CN, MC GH do 7, Mc Lele JP, Mc Jvila & Oruam)'},
    {'id': 521, 'isim': 'SOIS PAS TIMIDE', 'klasor': 'SOIS PAS TIMIDE'},
    {'id': 522, 'isim': 'SOS', 'klasor': 'SOS'},
    {'id': 523, 'isim': 'SUBEME LA RADIO', 'klasor': 'SUBEME LA RADIO'},
    {'id': 524, 'isim': 'Safe And Sound', 'klasor': 'Safe And Sound'},
    {'id': 525, 'isim': 'Same Mistake', 'klasor': 'Same Mistake'},
    {'id': 526, 'isim': 'Santa Baby (feat. Helene Fischer)', 'klasor': 'Santa Baby (feat. Helene Fischer)'},
    {'id': 527, 'isim': 'Santa Tell Me', 'klasor': 'Santa Tell Me'},
    {'id': 528, 'isim': 'Sarı Laleler', 'klasor': 'Sarı Laleler'},
    {'id': 529, 'isim': 'Saturn', 'klasor': 'Saturn'},
    {'id': 530, 'isim': 'Saudade Burra (Ao Vivo)', 'klasor': 'Saudade Burra (Ao Vivo)'},
    {'id': 531, 'isim': 'Saudade De Quem Eu Sou (Ao Vivo)', 'klasor': 'Saudade De Quem Eu Sou (Ao Vivo)'},
    {'id': 532, 'isim': 'Saudade Proibida (Ao Vivo)', 'klasor': 'Saudade Proibida (Ao Vivo)'},
    {'id': 533, 'isim': 'Saudade do Carai', 'klasor': 'Saudade do Carai'},
    {'id': 534, 'isim': 'Save Your Tears', 'klasor': 'Save Your Tears'},
    {'id': 535, 'isim': 'Say My Name', 'klasor': 'Say My Name'},
    {'id': 536, 'isim': 'Saydım', 'klasor': 'Saydım'},
    {'id': 537, 'isim': 'Schief in jedem Chor', 'klasor': 'Schief in jedem Chor'},
    {'id': 538, 'isim': 'Se Eu Te Perdoar (Ao Vivo)', 'klasor': 'Se Eu Te Perdoar (Ao Vivo)'},
    {'id': 539, 'isim': 'Seco', 'klasor': 'Seco'},
    {'id': 540, 'isim': 'Secrets', 'klasor': 'Secrets'},
    {'id': 541, 'isim': 'See You Again', 'klasor': 'See You Again'},
    {'id': 542, 'isim': 'See You Again (feat. Charlie Puth)', 'klasor': 'See You Again (feat. Charlie Puth)'},
    {'id': 543, 'isim': 'Segundo Amor da Sua Vida', 'klasor': 'Segundo Amor da Sua Vida'},
    {'id': 544, 'isim': 'Seja Ex (Ao Vivo)', 'klasor': 'Seja Ex (Ao Vivo)'},
    {'id': 545, 'isim': 'Sen Sevda Mısın', 'klasor': 'Sen Sevda Mısın'},
    {'id': 546, 'isim': 'Senden Başka', 'klasor': 'Senden Başka'},
    {'id': 547, 'isim': 'Senden Daha Güzel', 'klasor': 'Senden Daha Güzel'},
    {'id': 548, 'isim': 'Seni Seviyorum', 'klasor': 'Seni Seviyorum'},
    {'id': 549, 'isim': 'Seni Yerler', 'klasor': 'Seni Yerler'},
    {'id': 550, 'isim': 'Sensível Demais  À Primeira Vista  Telegrama (Ao Vivo)', 'klasor': 'Sensível Demais  À Primeira Vista  Telegrama (Ao Vivo)'},
    {'id': 551, 'isim': 'Serrure #5', 'klasor': 'Serrure #5'},
    {'id': 552, 'isim': 'Set Fire to the Rain', 'klasor': 'Set Fire to the Rain'},
    {'id': 553, 'isim': 'Sex on Fire', 'klasor': 'Sex on Fire'},
    {'id': 554, 'isim': 'Shape Of My Heart', 'klasor': 'Shape Of My Heart'},
    {'id': 555, 'isim': 'Shape of You', 'klasor': 'Shape of You'},
    {'id': 556, 'isim': 'Shatta Confessions', 'klasor': 'Shatta Confessions'},
    {'id': 557, 'isim': 'She Got Caught', 'klasor': 'She Got Caught'},
    {'id': 558, 'isim': 'She Will Be Loved', 'klasor': 'She Will Be Loved'},
    {'id': 559, 'isim': 'Shivers', 'klasor': 'Shivers'},
    {'id': 560, 'isim': 'Show Me Love', 'klasor': 'Show Me Love'},
    {'id': 561, 'isim': 'Sil Baştan', 'klasor': 'Sil Baştan'},
    {'id': 562, 'isim': 'Sing Me to Sleep', 'klasor': 'Sing Me to Sleep'},
    {'id': 563, 'isim': 'Sink into the Floor', 'klasor': 'Sink into the Floor'},
    {'id': 564, 'isim': 'Skifoan', 'klasor': 'Skifoan'},
    {'id': 565, 'isim': 'Sleigh Ride', 'klasor': 'Sleigh Ride'},
    {'id': 566, 'isim': 'Slimane - Paname', 'klasor': 'Slimane - Paname'},
    {'id': 567, 'isim': 'Slow Motion', 'klasor': 'Slow Motion'},
    {'id': 568, 'isim': 'Smells Like Teen Spirit', 'klasor': 'Smells Like Teen Spirit'},
    {'id': 569, 'isim': 'Smooth Criminal', 'klasor': 'Smooth Criminal'},
    {'id': 570, 'isim': 'Snooze', 'klasor': 'Snooze'},
    {'id': 571, 'isim': 'Snow (Hey Oh)', 'klasor': 'Snow (Hey Oh)'},
    {'id': 572, 'isim': 'Snowfall', 'klasor': 'Snowfall'},
    {'id': 573, 'isim': 'Snowman', 'klasor': 'Snowman'},
    {'id': 574, 'isim': 'So Easy (To Fall In Love)', 'klasor': 'So Easy (To Fall In Love)'},
    {'id': 575, 'isim': 'So Far Away (Full Version)', 'klasor': 'So Far Away (Full Version)'},
    {'id': 576, 'isim': 'So rechts', 'klasor': 'So rechts'},
    {'id': 577, 'isim': 'Soda Pop', 'klasor': 'Soda Pop'},
    {'id': 578, 'isim': 'Soft Spot', 'klasor': 'Soft Spot'},
    {'id': 579, 'isim': 'Sol Nos Olhos', 'klasor': 'Sol Nos Olhos'},
    {'id': 580, 'isim': 'Soleil levant', 'klasor': 'Soleil levant'},
    {'id': 581, 'isim': 'Somebody That I Used To Know', 'klasor': 'Somebody That I Used To Know'},
    {'id': 582, 'isim': 'Someone Like You', 'klasor': 'Someone Like You'},
    {'id': 583, 'isim': 'Someone You Loved', 'klasor': 'Someone You Loved'},
    {'id': 584, 'isim': 'Somewhere Over Laredo', 'klasor': 'Somewhere Over Laredo'},
    {'id': 585, 'isim': 'Sonho de Amor (Ao Vivo)', 'klasor': 'Sonho de Amor (Ao Vivo)'},
    {'id': 586, 'isim': 'Sonsuz', 'klasor': 'Sonsuz'},
    {'id': 587, 'isim': 'Spiel nicht mit den Schmuddelkindern', 'klasor': 'Spiel nicht mit den Schmuddelkindern'},
    {'id': 588, 'isim': 'Sports car', 'klasor': 'Sports car'},
    {'id': 589, 'isim': 'Stand by Me (Live at the Late Show with David Letterman)', 'klasor': 'Stand by Me (Live at the Late Show with David Letterman)'},
    {'id': 590, 'isim': 'Starboy', 'klasor': 'Starboy'},
    {'id': 591, 'isim': 'Stargazing', 'klasor': 'Stargazing'},
    {'id': 592, 'isim': 'Stay', 'klasor': 'Stay'},
    {'id': 593, 'isim': 'Stay the Night', 'klasor': 'Stay the Night'},
    {'id': 594, 'isim': 'Step Into Christmas (Remastered 1995)', 'klasor': 'Step Into Christmas (Remastered 1995)'},
    {'id': 595, 'isim': 'Stick Season', 'klasor': 'Stick Season'},
    {'id': 596, 'isim': 'Stolen Dance', 'klasor': 'Stolen Dance'},
    {'id': 597, 'isim': 'Stop The Cavalry', 'klasor': 'Stop The Cavalry'},
    {'id': 598, 'isim': 'Stop and Stare', 'klasor': 'Stop and Stare'},
    {'id': 599, 'isim': 'Streets of Philadelphia', 'klasor': 'Streets of Philadelphia'},
    {'id': 600, 'isim': 'Stressed Out', 'klasor': 'Stressed Out'},
    {'id': 601, 'isim': 'Sugar', 'klasor': 'Sugar'},
    {'id': 602, 'isim': 'Sujeito Homem', 'klasor': 'Sujeito Homem'},
    {'id': 603, 'isim': 'Summer', 'klasor': 'Summer'},
    {'id': 604, 'isim': 'Summer Wind (Live in Hamburg)', 'klasor': 'Summer Wind (Live in Hamburg)'},
    {'id': 605, 'isim': 'Summertime Sadness', 'klasor': 'Summertime Sadness'},
    {'id': 606, 'isim': 'Suspus', 'klasor': 'Suspus'},
    {'id': 607, 'isim': 'Suzanne', 'klasor': 'Suzanne'},
    {'id': 608, 'isim': 'Sweater Weather', 'klasor': 'Sweater Weather'},
    {'id': 609, 'isim': 'Sweet Caroline (DJ Mix)', 'klasor': 'Sweet Caroline (DJ Mix)'},
    {'id': 610, 'isim': 'Sweet Caroline (Single Version)', 'klasor': 'Sweet Caroline (Single Version)'},
    {'id': 611, 'isim': 'Tabiat Ana', 'klasor': 'Tabiat Ana'},
    {'id': 612, 'isim': 'Take Me to Church', 'klasor': 'Take Me to Church'},
    {'id': 613, 'isim': 'Take On Me', 'klasor': 'Take On Me'},
    {'id': 614, 'isim': 'Takedown', 'klasor': 'Takedown'},
    {'id': 615, 'isim': 'Tal Vez', 'klasor': 'Tal Vez'},
    {'id': 616, 'isim': 'Tamirci Çırağı', 'klasor': 'Tamirci Çırağı'},
    {'id': 617, 'isim': 'Tarde Demais  Mágica  Oh! Chuva (Ao Vivo)', 'klasor': 'Tarde Demais  Mágica  Oh! Chuva (Ao Vivo)'},
    {'id': 618, 'isim': 'Taste', 'klasor': 'Taste'},
    {'id': 619, 'isim': 'Tears', 'klasor': 'Tears'},
    {'id': 620, 'isim': 'Tears in Heaven', 'klasor': 'Tears in Heaven'},
    {'id': 621, 'isim': 'Temperature', 'klasor': 'Temperature'},
    {'id': 622, 'isim': 'That’s So True', 'klasor': 'That’s So True'},
    {'id': 623, 'isim': 'The Beards Club', 'klasor': 'The Beards Club'},
    {'id': 624, 'isim': 'The Best', 'klasor': 'The Best'},
    {'id': 625, 'isim': 'The Chain (2004 Remaster)', 'klasor': 'The Chain (2004 Remaster)'},
    {'id': 626, 'isim': 'The Christmas Song (Merry Christmas To You) (Remastered 1999)', 'klasor': 'The Christmas Song (Merry Christmas To You) (Remastered 1999)'},      
    {'id': 627, 'isim': 'The Door', 'klasor': 'The Door'},
    {'id': 628, 'isim': 'The Emptiness Machine', 'klasor': 'The Emptiness Machine'},
    {'id': 629, 'isim': 'The Fall', 'klasor': 'The Fall'},
    {'id': 630, 'isim': 'The Fate of Ophelia', 'klasor': 'The Fate of Ophelia'},
    {'id': 631, 'isim': 'The Giver', 'klasor': 'The Giver'},
    {'id': 632, 'isim': 'The Great Pretender', 'klasor': 'The Great Pretender'},
    {'id': 633, 'isim': 'The Hills', 'klasor': 'The Hills'},
    {'id': 634, 'isim': 'The Less I Know the Better', 'klasor': 'The Less I Know the Better'},
    {'id': 635, 'isim': 'The Lion Sleeps Tonight', 'klasor': 'The Lion Sleeps Tonight'},
    {'id': 636, 'isim': 'The Little Drummer Boy', 'klasor': 'The Little Drummer Boy'},
    {'id': 637, 'isim': 'The Logical Song', 'klasor': 'The Logical Song'},
    {'id': 638, 'isim': 'The Nights', 'klasor': 'The Nights'},
    {'id': 639, 'isim': 'The Ocean', 'klasor': 'The Ocean'},
    {'id': 640, 'isim': 'TiK ToK', 'klasor': 'TiK ToK'},
    {'id': 641, 'isim': 'Tu Misterioso Alguien', 'klasor': 'Tu Misterioso Alguien'},
    {'id': 642, 'isim': 'Um Maluco Cowboy (Ao Vivo)', 'klasor': 'Um Maluco Cowboy (Ao Vivo)'},
    {'id': 643, 'isim': 'Vai Cair Água (Ao Vivo)', 'klasor': 'Vai Cair Água (Ao Vivo)'},
    {'id': 644, 'isim': 'Visions', 'klasor': 'Visions'},
    {'id': 645, 'isim': 'We Don’t Talk Anymore', 'klasor': 'We Don’t Talk Anymore'},
    {'id': 646, 'isim': 'Who Wants To Live Forever (Remastered 2011)', 'klasor': 'Who Wants To Live Forever (Remastered 2011)'},
    {'id': 647, 'isim': 'Worst Way', 'klasor': 'Worst Way'},
    {'id': 648, 'isim': 'Yankı', 'klasor': 'Yankı'},
    {'id': 649, 'isim': 'Çingenem', 'klasor': 'Çingenem'},
    {'id': 650, 'isim': 'Özledim', 'klasor': 'Özledim'}
]

kitaplar = [
    {'id': 1, 'isim': 'Suç ve Ceza', 'kapak': 'Suç ve Ceza.jpg'},
    {'id': 2, 'isim': 'Sefiller', 'kapak': 'Sefiller.jpg'},
    {'id': 3, 'isim': 'Anna Karenina', 'kapak': 'Anna Karenina.jpg'},
    {'id': 4, 'isim': 'Karamazov Kardeşler', 'kapak': 'Karamazov Kardeşler.jpg'},
    {'id': 5, 'isim': 'Gurur ve Önyargı', 'kapak': 'Gurur ve Önyargı.jpg'},      
    {'id': 6, 'isim': 'Uğultulu Tepeler', 'kapak': 'Uğultulu Tepeler.jpg'},      
    {'id': 7, 'isim': 'Büyük Umutlar', 'kapak': 'Büyük Umutlar.jpg'},
    {'id': 8, 'isim': 'Jane Eyre', 'kapak': 'Jane Eyre.jpg'},
    {'id': 9, 'isim': 'Madam Bovary', 'kapak': 'Madam Bovary.jpg'},
    {'id': 10, 'isim': 'Kırmızı ve Siyah', 'kapak': 'Kırmızı ve Siyah.jpg'},     
    {'id': 11, 'isim': 'Babalar ve Oğullar', 'kapak': 'Babalar ve Oğullar.jpg'}, 
    {'id': 12, 'isim': 'Budala', 'kapak': 'Budala.jpg'},
    {'id': 13, 'isim': 'Yeraltından Notlar', 'kapak': 'Yeraltından Notlar.jpg'}, 
    {'id': 14, 'isim': 'Kumarbaz', 'kapak': 'Kumarbaz.jpg'},
    {'id': 15, 'isim': 'Ecinniler', 'kapak': 'Ecinniler.jpg'},
    {'id': 16, 'isim': 'İvan İlyiç in Ölümü', 'kapak': 'İvan İlyiç in Ölümü.jpg'},
    {'id': 17, 'isim': 'Hacı Murat', 'kapak': 'Hacı Murat.jpg'},
    {'id': 18, 'isim': 'Vişne Bahçesi', 'kapak': 'Vişne Bahçesi.jpg'},
    {'id': 19, 'isim': 'Martı', 'kapak': 'Martı.jpg'},
    {'id': 20, 'isim': 'Vanya Dayı', 'kapak': 'Vanya Dayı.jpg'},
    {'id': 21, 'isim': 'Üç Kız Kardeş', 'kapak': 'Üç Kız Kardeş.jpg'},
    {'id': 22, 'isim': 'Doktor Jivago', 'kapak': 'Doktor Jivago.jpg'},
    {'id': 23, 'isim': 'Usta ve Margarita', 'kapak': 'Usta ve Margarita.jpg'},
    {'id': 24, 'isim': 'Dönüşüm', 'kapak': 'Dönüşüm.jpg'},
    {'id': 25, 'isim': 'Dava', 'kapak': 'Dava.jpg'},
    {'id': 26, 'isim': 'Şato', 'kapak': 'Şato.jpg'},
    {'id': 27, 'isim': 'Amerika', 'kapak': 'Amerika.jpg'},
    {'id': 28, 'isim': 'Genç Werther in Acıları', 'kapak': 'Genç Werther in Acıları.jpg'},
    {'id': 29, 'isim': 'Faust', 'kapak': 'Faust.jpg'},
    {'id': 30, 'isim': 'Siddhartha', 'kapak': 'Siddhartha.jpg'},
    {'id': 31, 'isim': 'Bozkırkurdu', 'kapak': 'Bozkırkurdu.jpg'},
    {'id': 32, 'isim': 'Boncuk Oyunu', 'kapak': 'Boncuk Oyunu.jpg'},
    {'id': 33, 'isim': 'Demian', 'kapak': 'Demian.jpg'},
    {'id': 34, 'isim': 'Büyülü Dağ', 'kapak': 'Büyülü Dağ.jpg'},
    {'id': 35, 'isim': 'Venedik te Ölüm', 'kapak': 'Venedik te Ölüm.jpg'},
    {'id': 36, 'isim': 'Buddenbrooklar', 'kapak': 'Buddenbrooklar.jpg'},
    {'id': 37, 'isim': 'Teneke Trampet', 'kapak': 'Teneke Trampet.jpg'},
    {'id': 38, 'isim': 'Niteliksiz Adam', 'kapak': 'Niteliksiz Adam.jpg'},
    {'id': 39, 'isim': 'Satranç', 'kapak': 'Satranç.jpg'},
    {'id': 40, 'isim': 'Bilinmeyen Bir Kadının Mektubu', 'kapak': 'Bilinmeyen Bir Kadının Mektubu.jpg'},
    {'id': 41, 'isim': 'Amok Koşucusu', 'kapak': 'Amok Koşucusu.jpg'},
    {'id': 42, 'isim': 'Ay Işığı Sokağı', 'kapak': 'Ay Işığı Sokağı.jpg'},
    {'id': 43, 'isim': 'Yakıcı Sır', 'kapak': 'Yakıcı Sır.jpg'},
    {'id': 44, 'isim': 'Üç Büyük Usta', 'kapak': 'Üç Büyük Usta.jpg'},
    {'id': 45, 'isim': 'Yabancı', 'kapak': 'Yabancı.jpg'},
    {'id': 46, 'isim': 'Veba', 'kapak': 'Veba.jpg'},
    {'id': 47, 'isim': 'Düşüş', 'kapak': 'Düşüş.jpg'},
    {'id': 48, 'isim': 'Başkaldıran İnsan', 'kapak': 'Başkaldıran İnsan.jpg'},
    {'id': 49, 'isim': 'Bulantı', 'kapak': 'Bulantı.jpg'},
    {'id': 50, 'isim': 'Duvar', 'kapak': 'Duvar.jpg'},
    {'id': 51, 'isim': 'Sözcükler', 'kapak': 'Sözcükler.jpg'},
    {'id': 52, 'isim': 'Akıl Çağı', 'kapak': 'Akıl Çağı.jpg'},
    {'id': 53, 'isim': 'Küçük Prens', 'kapak': 'Küçük Prens.jpg'},
    {'id': 54, 'isim': 'Notre Dame ın Kamburu', 'kapak': 'Notre Dame ın Kamburu.jpg'},
    {'id': 55, 'isim': 'Vadideki Zambak', 'kapak': 'Vadideki Zambak.jpg'},
    {'id': 56, 'isim': 'Goriot Baba', 'kapak': 'Goriot Baba.jpg'},
    {'id': 57, 'isim': 'Eugnie Grandet', 'kapak': 'Eugnie Grandet.jpg'},
    {'id': 58, 'isim': 'Kibar Fahişeler', 'kapak': 'Kibar Fahişeler.jpg'},
    {'id': 59, 'isim': 'Tılsımlı Deri', 'kapak': 'Tılsımlı Deri.jpg'},
    {'id': 60, 'isim': 'İki Şehrin Hikayesi', 'kapak': 'İki Şehrin Hikayesi.jpg'},
    {'id': 61, 'isim': 'Oliver Twist', 'kapak': 'Oliver Twist.jpg'},
    {'id': 62, 'isim': 'David Copperfield', 'kapak': 'David Copperfield.jpg'},
    {'id': 63, 'isim': 'Zaman Makinesi', 'kapak': 'Zaman Makinesi.jpg'},
    {'id': 64, 'isim': 'Görünmez Adam', 'kapak': 'Görünmez Adam.jpg'},
    {'id': 65, 'isim': 'Dünyalar Savaşı', 'kapak': 'Dünyalar Savaşı.jpg'},
    {'id': 66, 'isim': 'Dr Moreau nun Adası', 'kapak': 'Dr Moreau nun Adası.jpg'},
    {'id': 67, 'isim': 'Define Adası', 'kapak': 'Define Adası.jpg'},
    {'id': 68, 'isim': 'Dr Jekyll ve Mr Hyde', 'kapak': 'Dr Jekyll ve Mr Hyde.jpg'},
    {'id': 69, 'isim': 'Robinson Crusoe', 'kapak': 'Robinson Crusoe.jpg'},
    {'id': 70, 'isim': 'Gulliver in Gezileri', 'kapak': 'Gulliver in Gezileri.jpg'},
    {'id': 71, 'isim': 'Frankenstein', 'kapak': 'Frankenstein.jpg'},
    {'id': 72, 'isim': 'Drakula', 'kapak': 'Drakula.jpg'},
    {'id': 73, 'isim': 'Dorian Gray in Portresi', 'kapak': 'Dorian Gray in Portresi.jpg'},
    {'id': 74, 'isim': 'Mutlu Prens', 'kapak': 'Mutlu Prens.jpg'},
    {'id': 75, 'isim': 'Ciddi Olmanın Önemi', 'kapak': 'Ciddi Olmanın Önemi.jpg'},
    {'id': 76, 'isim': 'Alice Harikalar Diyarında', 'kapak': 'Alice Harikalar Diyarında.jpg'},
    {'id': 77, 'isim': 'Aynanın İçinden', 'kapak': 'Aynanın İçinden.jpg'},
    {'id': 78, 'isim': 'Peter Pan', 'kapak': 'Peter Pan.jpg'},
    {'id': 79, 'isim': 'Rüzgarın Adı', 'kapak': 'Rüzgarın Adı.jpg'},
    {'id': 80, 'isim': 'Hobbit', 'kapak': 'Hobbit.jpg'},
    {'id': 81, 'isim': 'Yüzüklerin Efendisi Yüzük Kardeşliği', 'kapak': 'Yüzüklerin Efendisi Yüzük Kardeşliği.jpg'},
    {'id': 82, 'isim': 'Yüzüklerin Efendisi İki Kule', 'kapak': 'Yüzüklerin Efendisi İki Kule.jpg'},
    {'id': 83, 'isim': 'Yüzüklerin Efendisi Kralın Dönüşü', 'kapak': 'Yüzüklerin Efendisi Kralın Dönüşü.jpg'},
    {'id': 84, 'isim': 'Silmarillion', 'kapak': 'Silmarillion.jpg'},
    {'id': 85, 'isim': 'Narnia Günlükleri', 'kapak': 'Narnia Günlükleri.jpg'},
    {'id': 86, 'isim': 'Yerdeniz Büyücüsü', 'kapak': 'Yerdeniz Büyücüsü.jpg'},
    {'id': 87, 'isim': 'Harry Potter ve Felsefe Taşı', 'kapak': 'Harry Potter ve Felsefe Taşı.jpg'},
    {'id': 88, 'isim': 'Taht Oyunları', 'kapak': 'Taht Oyunları.jpg'},
    {'id': 89, 'isim': 'Kralların Çarpışması', 'kapak': 'Kralların Çarpışması.jpg'},
    {'id': 90, 'isim': 'Kılıçların Fırtınası', 'kapak': 'Kılıçların Fırtınası.jpg'},
    {'id': 91, 'isim': 'Kargaların Ziyafeti', 'kapak': 'Kargaların Ziyafeti.jpg'},
    {'id': 92, 'isim': 'Ejderhaların Dansı', 'kapak': 'Ejderhaların Dansı.jpg'},
    {'id': 93, 'isim': 'Dune', 'kapak': 'Dune.jpg'},
    {'id': 94, 'isim': 'Dune Mesihi', 'kapak': 'Dune Mesihi.jpg'},
    {'id': 95, 'isim': 'Dune Çocukları', 'kapak': 'Dune Çocukları.jpg'},
    {'id': 96, 'isim': 'Vakıf', 'kapak': 'Vakıf.jpg'},
    {'id': 97, 'isim': 'Vakıf ve İmparatorluk', 'kapak': 'Vakıf ve İmparatorluk.jpg'},
    {'id': 98, 'isim': 'İkinci Vakıf', 'kapak': 'İkinci Vakıf.jpg'},
    {'id': 99, 'isim': 'Ben Robot', 'kapak': 'Ben Robot.jpg'},
    {'id': 100, 'isim': 'Sonsuzluğun Sonu', 'kapak': 'Sonsuzluğun Sonu.jpg'},
    {'id': 101, 'isim': 'Cesur Yeni Dünya', 'kapak': 'Cesur Yeni Dünya.jpg'},
    {'id': 102, 'isim': '1984', 'kapak': '1984.jpg'},
    {'id': 103, 'isim': 'Hayvan Çiftliği', 'kapak': 'Hayvan Çiftliği.jpg'},
    {'id': 104, 'isim': 'Fahrenheit 451', 'kapak': 'Fahrenheit 451.jpg'},
    {'id': 105, 'isim': 'Otomatik Portakal', 'kapak': 'Otomatik Portakal.jpg'},
    {'id': 106, 'isim': 'Biz', 'kapak': 'Biz.jpg'},
    {'id': 107, 'isim': 'Demir Ökçe', 'kapak': 'Demir Ökçe.jpg'},
    {'id': 108, 'isim': 'Damızlık Kızın Öyküsü', 'kapak': 'Damızlık Kızın Öyküsü.jpg'},
    {'id': 109, 'isim': 'Mülksüzler', 'kapak': 'Mülksüzler.jpg'},
    {'id': 110, 'isim': 'Karanlığın Sol Eli', 'kapak': 'Karanlığın Sol Eli.jpg'},
    {'id': 111, 'isim': 'Androidler Elektrikli Koyun Düşler mi', 'kapak': 'Androidler Elektrikli Koyun Düşler mi.jpg'},
    {'id': 112, 'isim': 'Neuromancer', 'kapak': 'Neuromancer.jpg'},
    {'id': 113, 'isim': 'Otostopçunun Galaksi Rehberi', 'kapak': 'Otostopçunun Galaksi Rehberi.jpg'},
    {'id': 114, 'isim': 'Solaris', 'kapak': 'Solaris.jpg'},
    {'id': 115, 'isim': 'Yıldız Gemisi Askerleri', 'kapak': 'Yıldız Gemisi Askerleri.jpg'},
    {'id': 116, 'isim': 'Moby Dick', 'kapak': 'Moby Dick.jpg'},
    {'id': 117, 'isim': 'Tom Sawyer ın Maceraları', 'kapak': 'Tom Sawyer ın Maceraları.jpg'},
    {'id': 118, 'isim': 'Huckleberry Finn in Maceraları', 'kapak': 'Huckleberry Finn in Maceraları.jpg'},
    {'id': 119, 'isim': 'Beyaz Diş', 'kapak': 'Beyaz Diş.jpg'},
    {'id': 120, 'isim': 'Vahşetin Çağrısı', 'kapak': 'Vahşetin Çağrısı.jpg'},
    {'id': 121, 'isim': 'Deniz Kurdu', 'kapak': 'Deniz Kurdu.jpg'},
    {'id': 122, 'isim': 'Martin Eden', 'kapak': 'Martin Eden.jpg'},
    {'id': 123, 'isim': 'Muhteşem Gatsby', 'kapak': 'Muhteşem Gatsby.jpg'},
    {'id': 124, 'isim': 'Gazap Üzümleri', 'kapak': 'Gazap Üzümleri.jpg'},
    {'id': 125, 'isim': 'İnci', 'kapak': 'İnci.jpg'},
    {'id': 126, 'isim': 'Silahlara Veda', 'kapak': 'Silahlara Veda.jpg'},
    {'id': 127, 'isim': 'Yaşlı Adam ve Deniz', 'kapak': 'Yaşlı Adam ve Deniz.jpg'},
    {'id': 128, 'isim': 'Güneş de Doğar', 'kapak': 'Güneş de Doğar.jpg'},
    {'id': 129, 'isim': 'Ses ve Öfke', 'kapak': 'Ses ve Öfke.jpg'},
    {'id': 130, 'isim': 'Döşeğimde Ölürken', 'kapak': 'Döşeğimde Ölürken.jpg'},
    {'id': 131, 'isim': 'Ağustos Işığı', 'kapak': 'Ağustos Işığı.jpg'},
    {'id': 132, 'isim': 'Bülbülü Öldürmek', 'kapak': 'Bülbülü Öldürmek.jpg'},
    {'id': 133, 'isim': 'Çavdar Tarlasında Çocuklar', 'kapak': 'Çavdar Tarlasında Çocuklar.jpg'},
    {'id': 134, 'isim': 'Guguk Kuşu', 'kapak': 'Guguk Kuşu.jpg'},
    {'id': 135, 'isim': 'Yolda', 'kapak': 'Yolda.jpg'},
    {'id': 136, 'isim': 'Zen ve Motosiklet Bakım Sanatı', 'kapak': 'Zen ve Motosiklet Bakım Sanatı.jpg'},
    {'id': 137, 'isim': 'Kökler', 'kapak': 'Kökler.jpg'},
    {'id': 138, 'isim': 'Solgun Ateş', 'kapak': 'Solgun Ateş.jpg'},
    {'id': 139, 'isim': 'Ada ya da Arzu', 'kapak': 'Ada ya da Arzu.jpg'},
    {'id': 140, 'isim': 'Ulysses', 'kapak': 'Ulysses.jpg'},
    {'id': 141, 'isim': 'Dublinliler', 'kapak': 'Dublinliler.jpg'},
    {'id': 142, 'isim': 'Sanatçının Genç Bir Adam Olarak Portresi', 'kapak': 'Sanatçının Genç Bir Adam Olarak Portresi.jpg'},
    {'id': 143, 'isim': 'Mrs Dalloway', 'kapak': 'Mrs Dalloway.jpg'},
    {'id': 144, 'isim': 'Deniz Feneri', 'kapak': 'Deniz Feneri.jpg'},
    {'id': 145, 'isim': 'Kendine Ait Bir Oda', 'kapak': 'Kendine Ait Bir Oda.jpg'},
    {'id': 146, 'isim': 'Orlando', 'kapak': 'Orlando.jpg'},
    {'id': 147, 'isim': 'Dalgalar', 'kapak': 'Dalgalar.jpg'},
    {'id': 148, 'isim': 'Hindistan a Bir Geçit', 'kapak': 'Hindistan a Bir Geçit.jpg'},
    {'id': 149, 'isim': 'Karanlığın Yüreği', 'kapak': 'Karanlığın Yüreği.jpg'},
    {'id': 150, 'isim': 'Lord Jim', 'kapak': 'Lord Jim.jpg'},
    {'id': 151, 'isim': 'Casus', 'kapak': 'Casus.jpg'},
    {'id': 152, 'isim': 'Nostromo', 'kapak': 'Nostromo.jpg'},
    {'id': 153, 'isim': 'Paris ve Londra da Beş Parasız', 'kapak': 'Paris ve Londra da Beş Parasız.jpg'},
    {'id': 154, 'isim': 'Aspidistra', 'kapak': 'Aspidistra.jpg'},
    {'id': 155, 'isim': 'Burmese Günleri', 'kapak': 'Burmese Günleri.jpg'},
    {'id': 156, 'isim': 'Sineklerin Tanrısı', 'kapak': 'Sineklerin Tanrısı.jpg'},
    {'id': 157, 'isim': 'Serbest Düşüş', 'kapak': 'Serbest Düşüş.jpg'},
    {'id': 158, 'isim': 'Kule', 'kapak': 'Kule.jpg'},
    {'id': 159, 'isim': 'Yüzyıllık Yalnızlık', 'kapak': 'Yüzyıllık Yalnızlık.jpg'},
    {'id': 160, 'isim': 'Kırmızı Pazartesi', 'kapak': 'Kırmızı Pazartesi.jpg'},
    {'id': 161, 'isim': 'Başkan Babamızın Sonbaharı', 'kapak': 'Başkan Babamızın Sonbaharı.jpg'},
    {'id': 162, 'isim': 'Benim Hüzünlü Orospularım', 'kapak': 'Benim Hüzünlü Orospularım.jpg'},
    {'id': 163, 'isim': 'Alef', 'kapak': 'Alef.jpg'},
    {'id': 164, 'isim': 'Ficciones', 'kapak': 'Ficciones.jpg'},
    {'id': 165, 'isim': 'Kum Kitabı', 'kapak': 'Kum Kitabı.jpg'},
    {'id': 166, 'isim': 'Pedro Paramo', 'kapak': 'Pedro Paramo.jpg'},
    {'id': 167, 'isim': 'Seksek', 'kapak': 'Seksek.jpg'},
    {'id': 168, 'isim': 'Duygusal Eğitim', 'kapak': 'Duygusal Eğitim.jpg'},
    {'id': 169, 'isim': 'Bel-Ami', 'kapak': 'Bel-Ami.jpg'},
    {'id': 170, 'isim': 'Bir Kadının Yaşamı', 'kapak': 'Bir Kadının Yaşamı.jpg'},
    {'id': 171, 'isim': 'Nana', 'kapak': 'Nana.jpg'},
    {'id': 172, 'isim': 'Germinal', 'kapak': 'Germinal.jpg'},
    {'id': 173, 'isim': 'Hayvanlaşan İnsan', 'kapak': 'Hayvanlaşan İnsan.jpg'},
    {'id': 174, 'isim': 'Thrse Raquin', 'kapak': 'Thrse Raquin.jpg'},
    {'id': 175, 'isim': 'Kayıp Zamanın İzinde', 'kapak': 'Kayıp Zamanın İzinde.jpg'},
    {'id': 176, 'isim': 'Swann ın Bir Aşkı', 'kapak': 'Swann ın Bir Aşkı.jpg'},
    {'id': 177, 'isim': 'Çiçek Açmış Genç Kızların Gölgesinde', 'kapak': 'Çiçek Açmış Genç Kızların Gölgesinde.jpg'},
    {'id': 178, 'isim': 'Guermantes Tarafı', 'kapak': 'Guermantes Tarafı.jpg'},
    {'id': 179, 'isim': 'Sodom ve Gomorra', 'kapak': 'Sodom ve Gomorra.jpg'},
    {'id': 180, 'isim': 'Albertine Kayıp', 'kapak': 'Albertine Kayıp.jpg'},
    {'id': 181, 'isim': 'Yakalanan Zaman', 'kapak': 'Yakalanan Zaman.jpg'},
    {'id': 182, 'isim': 'Yolculuk', 'kapak': 'Yolculuk.jpg'},
    {'id': 183, 'isim': 'Kuzey', 'kapak': 'Kuzey.jpg'},
    {'id': 184, 'isim': 'Gecenin Sonuna Yolculuk', 'kapak': 'Gecenin Sonuna Yolculuk.jpg'},
    {'id': 185, 'isim': 'Taksitle Ölüm', 'kapak': 'Taksitle Ölüm.jpg'},
    {'id': 186, 'isim': 'Gargantua', 'kapak': 'Gargantua.jpg'},
    {'id': 187, 'isim': 'Pantagruel', 'kapak': 'Pantagruel.jpg'},
    {'id': 188, 'isim': 'Candide', 'kapak': 'Candide.jpg'},
    {'id': 189, 'isim': 'Zadig', 'kapak': 'Zadig.jpg'},
    {'id': 190, 'isim': 'Safdil', 'kapak': 'Safdil.jpg'},
    {'id': 191, 'isim': 'Tehlikeli İlişkiler', 'kapak': 'Tehlikeli İlişkiler.jpg'},
    {'id': 192, 'isim': 'Manon Lescaut', 'kapak': 'Manon Lescaut.jpg'},
    {'id': 193, 'isim': 'Atala', 'kapak': 'Atala.jpg'},
    {'id': 194, 'isim': 'Rene', 'kapak': 'Rene.jpg'},
    {'id': 195, 'isim': 'Carmen', 'kapak': 'Carmen.jpg'},
    {'id': 196, 'isim': 'Üç Silahşorlar', 'kapak': 'Üç Silahşorlar.jpg'},
    {'id': 197, 'isim': 'Demir Maskeli Adam', 'kapak': 'Demir Maskeli Adam.jpg'},
    {'id': 198, 'isim': 'Yirmi Yıl Sonra', 'kapak': 'Yirmi Yıl Sonra.jpg'},
    {'id': 199, 'isim': 'Siyah Lale', 'kapak': 'Siyah Lale.jpg'},
    {'id': 200, 'isim': 'Denizler Altında 20000 Fersah', 'kapak': 'Denizler Altında 20000 Fersah.jpg'},
    {'id': 201, 'isim': 'Aya Yolculuk', 'kapak': 'Aya Yolculuk.jpg'},
    {'id': 202, 'isim': 'Balonla Beş Hafta', 'kapak': 'Balonla Beş Hafta.jpg'},
    {'id': 203, 'isim': 'Dünyanın Merkezine Yolculuk', 'kapak': 'Dünyanın Merkezine Yolculuk.jpg'},
    {'id': 204, 'isim': 'Esrarlı Ada', 'kapak': 'Esrarlı Ada.jpg'},
    {'id': 205, 'isim': 'Kar', 'kapak': 'Kar.jpg'},
    {'id': 206, 'isim': 'Masumiyet Müzesi', 'kapak': 'Masumiyet Müzesi.jpg'},
    {'id': 207, 'isim': 'Suskunlar', 'kapak': 'Suskunlar.jpg'},
    {'id': 208, 'isim': 'Çalıkuşu', 'kapak': 'Çalıkuşu.jpg'},
    {'id': 209, 'isim': 'Acımak', 'kapak': 'Acımak.jpg'},
    {'id': 210, 'isim': 'Aşk-ı Memnu', 'kapak': 'Aşk-ı Memnu.jpg'},
    {'id': 211, 'isim': 'Mai ve Siyah', 'kapak': 'Mai ve Siyah.jpg'},
    {'id': 212, 'isim': 'Eylül', 'kapak': 'Eylül.jpg'},
    {'id': 213, 'isim': 'Genç Kız Kalbi', 'kapak': 'Genç Kız Kalbi.jpg'},
    {'id': 214, 'isim': 'Karanfil ve Yasemin', 'kapak': 'Karanfil ve Yasemin.jpg'},
    {'id': 215, 'isim': 'Yaban', 'kapak': 'Yaban.jpg'},
    {'id': 216, 'isim': 'Sodom ve Gomore', 'kapak': 'Sodom ve Gomore.jpg'},
    {'id': 217, 'isim': 'Ankara', 'kapak': 'Ankara.jpg'},
    {'id': 218, 'isim': 'Nur Baba', 'kapak': 'Nur Baba.jpg'},
    {'id': 219, 'isim': 'Panorama', 'kapak': 'Panorama.jpg'},
    {'id': 220, 'isim': 'Hep O Şarkı', 'kapak': 'Hep O Şarkı.jpg'},
    {'id': 221, 'isim': 'Sinekli Bakkal', 'kapak': 'Sinekli Bakkal.jpg'},
    {'id': 222, 'isim': 'Emile', 'kapak': 'Emile.jpg'},
    {'id': 223, 'isim': 'Ecce Homo', 'kapak': 'Ecce Homo.jpg'},
    {'id': 224, 'isim': 'Ahlakın Soykütüğü', 'kapak': 'Ahlakın Soykütüğü.jpg'},
    {'id': 225, 'isim': 'Tragedyanın Doğuşu', 'kapak': 'Tragedyanın Doğuşu.jpg'},
    {'id': 226, 'isim': 'Şen Bilim', 'kapak': 'Şen Bilim.jpg'},
    {'id': 227, 'isim': 'Varlık ve Hiçlik', 'kapak': 'Varlık ve Hiçlik.jpg'},
    {'id': 228, 'isim': 'Varlık ve Zaman', 'kapak': 'Varlık ve Zaman.jpg'},
    {'id': 229, 'isim': 'Sisyphus Söyleni', 'kapak': 'Sisyphus Söyleni.jpg'},
    {'id': 230, 'isim': 'Hapishanenin Doğuşu', 'kapak': 'Hapishanenin Doğuşu.jpg'},
    {'id': 231, 'isim': 'Deliliğin Tarihi', 'kapak': 'Deliliğin Tarihi.jpg'},
    {'id': 232, 'isim': 'Cinselliğin Tarihi', 'kapak': 'Cinselliğin Tarihi.jpg'},
    {'id': 233, 'isim': 'Simulakrlar ve Simülasyon', 'kapak': 'Simulakrlar ve Simülasyon.jpg'},
    {'id': 234, 'isim': 'Tüketim Toplumu', 'kapak': 'Tüketim Toplumu.jpg'},
    {'id': 235, 'isim': 'Gösteri Toplumu', 'kapak': 'Gösteri Toplumu.jpg'},
    {'id': 236, 'isim': 'Aydınlanmanın Diyalektiği', 'kapak': 'Aydınlanmanın Diyalektiği.jpg'},
    {'id': 237, 'isim': 'Minima Moralia', 'kapak': 'Minima Moralia.jpg'},
    {'id': 238, 'isim': 'Pasajlar', 'kapak': 'Pasajlar.jpg'},
    {'id': 239, 'isim': 'Komünist Manifesto', 'kapak': 'Komünist Manifesto.jpg'},
    {'id': 240, 'isim': 'Kapital', 'kapak': 'Kapital.jpg'},
    {'id': 241, 'isim': 'Devlet', 'kapak': 'Devlet.jpg'},
    {'id': 242, 'isim': 'Şölen', 'kapak': 'Şölen.jpg'},
    {'id': 243, 'isim': 'Phaidon', 'kapak': 'Phaidon.jpg'},
    {'id': 244, 'isim': 'Nikomakhos a Etik', 'kapak': 'Nikomakhos a Etik.jpg'},
    {'id': 245, 'isim': 'Poetika', 'kapak': 'Poetika.jpg'},
    {'id': 246, 'isim': 'Metafizik', 'kapak': 'Metafizik.jpg'},
    {'id': 247, 'isim': 'Politika', 'kapak': 'Politika.jpg'},
    {'id': 248, 'isim': 'Savaş Sanatı', 'kapak': 'Savaş Sanatı.jpg'},
    {'id': 249, 'isim': 'Tao Te Ching', 'kapak': 'Tao Te Ching.jpg'},
    {'id': 250, 'isim': 'Mesnevi', 'kapak': 'Mesnevi.jpg'},
    {'id': 251, 'isim': 'Bostan ve Gülistan', 'kapak': 'Bostan ve Gülistan.jpg'},
    {'id': 252, 'isim': 'Mantıku t-Tayr', 'kapak': 'Mantıku t-Tayr.jpg'},
    {'id': 253, 'isim': 'Gılgamış Destanı', 'kapak': 'Gılgamış Destanı.jpg'},
    {'id': 254, 'isim': 'İlyada', 'kapak': 'İlyada.jpg'},
    {'id': 255, 'isim': 'Odysseia', 'kapak': 'Odysseia.jpg'},
    {'id': 256, 'isim': 'Aeneis', 'kapak': 'Aeneis.jpg'},
    {'id': 257, 'isim': 'Kral Oidipus', 'kapak': 'Kral Oidipus.jpg'},
    {'id': 258, 'isim': 'Antigone', 'kapak': 'Antigone.jpg'},
    {'id': 259, 'isim': 'Medea', 'kapak': 'Medea.jpg'},
    {'id': 260, 'isim': 'Zincire Vurulmuş Prometheus', 'kapak': 'Zincire Vurulmuş Prometheus.jpg'},
    {'id': 261, 'isim': 'Lysistrata', 'kapak': 'Lysistrata.jpg'},
    {'id': 262, 'isim': 'Hamlet', 'kapak': 'Hamlet.jpg'},
    {'id': 263, 'isim': 'Romeo ve Juliet', 'kapak': 'Romeo ve Juliet.jpg'},
    {'id': 264, 'isim': 'Bir Yaz Gecesi Rüyası', 'kapak': 'Bir Yaz Gecesi Rüyası.jpg'},
    {'id': 265, 'isim': 'Venedik Taciri', 'kapak': 'Venedik Taciri.jpg'},
    {'id': 266, 'isim': 'Size Nasıl Geliyorsa', 'kapak': 'Size Nasıl Geliyorsa.jpg'},
    {'id': 267, 'isim': 'Windsor un Şen Kadınları', 'kapak': 'Windsor un Şen Kadınları.jpg'},
    {'id': 268, 'isim': 'Faust Marlowe', 'kapak': 'Faust Marlowe.jpg'},
    {'id': 269, 'isim': 'Gergedan', 'kapak': 'Gergedan.jpg'},
    {'id': 270, 'isim': 'Yaratma Cesareti', 'kapak': 'Yaratma Cesareti.jpg'},
    {'id': 271, 'isim': 'Ölümsüzlük', 'kapak': 'Ölümsüzlük.jpg'},
    {'id': 272, 'isim': 'Baudolino', 'kapak': 'Baudolino.jpg'},
    {'id': 273, 'isim': 'Kraliçe Loana nın Gizemli Alevi', 'kapak': 'Kraliçe Loana nın Gizemli Alevi.jpg'},
    {'id': 274, 'isim': 'Koku', 'kapak': 'Koku.jpg'},
    {'id': 275, 'isim': 'Körlük', 'kapak': 'Körlük.jpg'},
    {'id': 276, 'isim': 'Görmek', 'kapak': 'Görmek.jpg'},
    {'id': 277, 'isim': 'Kopyalanmış Adam', 'kapak': 'Kopyalanmış Adam.jpg'},
    {'id': 278, 'isim': 'Şeker Portakalı', 'kapak': 'Şeker Portakalı.jpg'},
    {'id': 279, 'isim': 'Güneşi Uyandıralım', 'kapak': 'Güneşi Uyandıralım.jpg'},
    {'id': 280, 'isim': 'Yüreğinin Götürdüğü Yere Git', 'kapak': 'Yüreğinin Götürdüğü Yere Git.jpg'},
    {'id': 281, 'isim': 'Portakal Kız', 'kapak': 'Portakal Kız.jpg'},
    {'id': 282, 'isim': 'Hayvanlardan Tanrılara Sapiens', 'kapak': 'Hayvanlardan Tanrılara Sapiens.jpg'},
    {'id': 283, 'isim': 'Homo Deus', 'kapak': 'Homo Deus.jpg'},
    {'id': 284, 'isim': 'Tüfek Mikrop ve Çelik', 'kapak': 'Tüfek Mikrop ve Çelik.jpg'},
    {'id': 285, 'isim': 'Çöküş', 'kapak': 'Çöküş.jpg'},
    {'id': 286, 'isim': 'Musa ve Tektanrıcılık', 'kapak': 'Musa ve Tektanrıcılık.jpg'},
    {'id': 287, 'isim': 'Leonardo da Vinci', 'kapak': 'Leonardo da Vinci.jpg'},
    {'id': 288, 'isim': 'Göz', 'kapak': 'Göz.jpg'},
    {'id': 289, 'isim': 'Maça Kızı', 'kapak': 'Maça Kızı.jpg'},
    {'id': 290, 'isim': 'Lolita Nabokov', 'kapak': 'Lolita Nabokov.jpg'},
    {'id': 291, 'isim': 'Pnin', 'kapak': 'Pnin.jpg'},
    {'id': 292, 'isim': 'Konuş Hafıza', 'kapak': 'Konuş Hafıza.jpg'},
    {'id': 293, 'isim': 'Açlık', 'kapak': 'Açlık.jpg'},
    {'id': 294, 'isim': 'Germinal Zola', 'kapak': 'Germinal Zola.jpg'},
    {'id': 295, 'isim': 'Nana Zola', 'kapak': 'Nana Zola.jpg'},
    {'id': 296, 'isim': 'Anna Karenina 2', 'kapak': 'Anna Karenina 2.jpg'},
    {'id': 297, 'isim': 'Savaş ve Barış 2', 'kapak': 'Savaş ve Barış 2.jpg'},
    {'id': 298, 'isim': 'Kayıp Adımlar', 'kapak': 'Kayıp Adımlar.jpg'},
    {'id': 299, 'isim': 'İnsanlığın Yıldızının Parladığı Anlar', 'kapak': 'İnsanlığın Yıldızının Parladığı Anlar.jpg'},
    {'id': 300, 'isim': 'Dünün Dünyası', 'kapak': 'Dünün Dünyası.jpg'},
    {'id': 301, 'isim': 'Üç Usta', 'kapak': 'Üç Usta.jpg'},
    {'id': 302, 'isim': 'Kendi Hayatının Şiirini Yazanlar', 'kapak': 'Kendi Hayatının Şiirini Yazanlar.jpg'},
    {'id': 303, 'isim': 'Rotterdamlı Erasmus', 'kapak': 'Rotterdamlı Erasmus.jpg'},
    {'id': 304, 'isim': 'Bab-ı Esrar', 'kapak': 'Bab-ı Esrar.jpg'},
    {'id': 305, 'isim': 'Patasana', 'kapak': 'Patasana.jpg'},
    {'id': 306, 'isim': 'Kavim', 'kapak': 'Kavim.jpg'},
    {'id': 307, 'isim': 'Sultanı Öldürmek', 'kapak': 'Sultanı Öldürmek.jpg'},
    {'id': 308, 'isim': 'Kukla', 'kapak': 'Kukla.jpg'},
    {'id': 309, 'isim': 'Huzur Sokağı', 'kapak': 'Huzur Sokağı.jpg'},
    {'id': 310, 'isim': 'Yolların Sonu', 'kapak': 'Yolların Sonu.jpg'},
    {'id': 311, 'isim': 'Osmancık', 'kapak': 'Osmancık.jpg'},
    {'id': 312, 'isim': 'Küçük Ağa', 'kapak': 'Küçük Ağa.jpg'},
    {'id': 313, 'isim': 'Firavun İmanı', 'kapak': 'Firavun İmanı.jpg'},
    {'id': 314, 'isim': 'Dönemeçte', 'kapak': 'Dönemeçte.jpg'},
    {'id': 315, 'isim': 'Yağmur Beklerken', 'kapak': 'Yağmur Beklerken.jpg'},
    {'id': 316, 'isim': 'Dünyanın En Pis Sokağı', 'kapak': 'Dünyanın En Pis Sokağı.jpg'},
    {'id': 317, 'isim': 'Araba Sevdası', 'kapak': 'Araba Sevdası.jpg'},
    {'id': 318, 'isim': 'Taaşşuk-ı Talat ve Fitnat', 'kapak': 'Taaşşuk-ı Talat ve Fitnat.jpg'},
    {'id': 319, 'isim': 'İntibah', 'kapak': 'İntibah.jpg'},
    {'id': 320, 'isim': 'Karabibik', 'kapak': 'Karabibik.jpg'},
    {'id': 321, 'isim': 'Zehra', 'kapak': 'Zehra.jpg'},
    {'id': 322, 'isim': 'Sergüzeşt', 'kapak': 'Sergüzeşt.jpg'},
    {'id': 323, 'isim': 'Mürebbiye', 'kapak': 'Mürebbiye.jpg'},
    {'id': 324, 'isim': 'Şıpsevdi', 'kapak': 'Şıpsevdi.jpg'},
    {'id': 325, 'isim': 'Gulyabani', 'kapak': 'Gulyabani.jpg'},
    {'id': 326, 'isim': 'Kuyruklu Yıldız Altında Bir İzdivaç', 'kapak': 'Kuyruklu Yıldız Altında Bir İzdivaç.jpg'},
    {'id': 327, 'isim': 'Cadı', 'kapak': 'Cadı.jpg'},
    {'id': 328, 'isim': 'İstanbul un İç Yüzü', 'kapak': 'İstanbul un İç Yüzü.jpg'},
    {'id': 329, 'isim': 'Sürgün', 'kapak': 'Sürgün.jpg'},
    {'id': 330, 'isim': 'Nilgün', 'kapak': 'Nilgün.jpg'},
    {'id': 331, 'isim': 'Anahtar', 'kapak': 'Anahtar.jpg'},
    {'id': 332, 'isim': 'Ago Paşa nın Hatıratı', 'kapak': 'Ago Paşa nın Hatıratı.jpg'},
    {'id': 333, 'isim': 'Guguklu Saat', 'kapak': 'Guguklu Saat.jpg'},
    {'id': 334, 'isim': 'Ay Peşinde', 'kapak': 'Ay Peşinde.jpg'},
    {'id': 335, 'isim': 'Oblomov', 'kapak': 'Oblomov.jpg'},
    {'id': 336, 'isim': 'Taras Bulba', 'kapak': 'Taras Bulba.jpg'},
    {'id': 337, 'isim': 'Müfettiş', 'kapak': 'Müfettiş.jpg'},
    {'id': 338, 'isim': 'Burun', 'kapak': 'Burun.jpg'},
    {'id': 339, 'isim': 'İnsancıklar', 'kapak': 'İnsancıklar.jpg'},
    {'id': 340, 'isim': 'Beyaz Geceler', 'kapak': 'Beyaz Geceler.jpg'},
    {'id': 341, 'isim': 'Öteki', 'kapak': 'Öteki.jpg'},
    {'id': 342, 'isim': 'Ev Sahibesi', 'kapak': 'Ev Sahibesi.jpg'},
    {'id': 343, 'isim': 'Bir Yufka Yürekli', 'kapak': 'Bir Yufka Yürekli.jpg'},
    {'id': 344, 'isim': 'İnsan Ne İle Yaşar', 'kapak': 'İnsan Ne İle Yaşar.jpg'},
    {'id': 345, 'isim': 'Efendi ile Uşağı', 'kapak': 'Efendi ile Uşağı.jpg'},
    {'id': 346, 'isim': 'Kazaklar', 'kapak': 'Kazaklar.jpg'},
    {'id': 347, 'isim': 'Polikuşka', 'kapak': 'Polikuşka.jpg'},
    {'id': 348, 'isim': 'Kroyçer Sonat', 'kapak': 'Kroyçer Sonat.jpg'},
    {'id': 349, 'isim': 'Ana', 'kapak': 'Ana.jpg'},
    {'id': 350, 'isim': 'Foma', 'kapak': 'Foma.jpg'},
    {'id': 351, 'isim': 'Benim Üniversitelerim', 'kapak': 'Benim Üniversitelerim.jpg'},
    {'id': 352, 'isim': 'Ekmeğimi Kazanırken', 'kapak': 'Ekmeğimi Kazanırken.jpg'},
    {'id': 353, 'isim': 'Çocukluğum', 'kapak': 'Çocukluğum.jpg'},
    {'id': 354, 'isim': 'Eugene Onegin', 'kapak': 'Eugene Onegin.jpg'},
    {'id': 355, 'isim': 'Yüzbaşının Kızı', 'kapak': 'Yüzbaşının Kızı.jpg'},
    {'id': 356, 'isim': 'Zamanımızın Bir Kahramanı', 'kapak': 'Zamanımızın Bir Kahramanı.jpg'},
    {'id': 357, 'isim': 'Step', 'kapak': 'Step.jpg'},
    {'id': 358, 'isim': 'Duygusal Yolculuk', 'kapak': 'Duygusal Yolculuk.jpg'},
    {'id': 359, 'isim': 'Tristram Shandy', 'kapak': 'Tristram Shandy.jpg'},
    {'id': 360, 'isim': 'Tom Jones', 'kapak': 'Tom Jones.jpg'},
    {'id': 361, 'isim': 'Villette', 'kapak': 'Villette.jpg'},
    {'id': 362, 'isim': 'Agnes Eyre', 'kapak': 'Agnes Eyre.jpg'},
    {'id': 363, 'isim': 'Emma', 'kapak': 'Emma.jpg'},
    {'id': 364, 'isim': 'Akıl ve Tutku', 'kapak': 'Akıl ve Tutku.jpg'},
    {'id': 365, 'isim': 'Mansfield Parkı', 'kapak': 'Mansfield Parkı.jpg'},
    {'id': 366, 'isim': 'Northanger Manastırı', 'kapak': 'Northanger Manastırı.jpg'},
    {'id': 367, 'isim': 'İkna', 'kapak': 'İkna.jpg'},
    {'id': 368, 'isim': 'Lady Susan', 'kapak': 'Lady Susan.jpg'},
    {'id': 369, 'isim': 'Tess', 'kapak': 'Tess.jpg'},
    {'id': 370, 'isim': 'Çılgın Kalabalıktan Uzak', 'kapak': 'Çılgın Kalabalıktan Uzak.jpg'},
    {'id': 371, 'isim': 'Jude', 'kapak': 'Jude.jpg'},
    {'id': 372, 'isim': 'Eve Dönüş', 'kapak': 'Eve Dönüş.jpg'},
    {'id': 373, 'isim': 'Gurur Dünyası', 'kapak': 'Gurur Dünyası.jpg'},
    {'id': 374, 'isim': 'Dorian Gray', 'kapak': 'Dorian Gray.jpg'},
    {'id': 375, 'isim': 'De Profundis', 'kapak': 'De Profundis.jpg'},
    {'id': 376, 'isim': 'Salome', 'kapak': 'Salome.jpg'},
    {'id': 377, 'isim': 'Reading Zindanı Baladı', 'kapak': 'Reading Zindanı Baladı.jpg'},
    {'id': 378, 'isim': 'Dr Jekyll ve Bay Hyde', 'kapak': 'Dr Jekyll ve Bay Hyde.jpg'},
    {'id': 379, 'isim': 'Kaçırılan Çocuk', 'kapak': 'Kaçırılan Çocuk.jpg'},
    {'id': 380, 'isim': 'Justine', 'kapak': 'Justine.jpg'},
    {'id': 381, 'isim': 'Kaderci Jacques ve Efendisi', 'kapak': 'Kaderci Jacques ve Efendisi.jpg'},
    {'id': 382, 'isim': 'Rameau nun Yeğeni', 'kapak': 'Rameau nun Yeğeni.jpg'},
    {'id': 383, 'isim': 'İzlanda Balıkçısı', 'kapak': 'İzlanda Balıkçısı.jpg'},
    {'id': 384, 'isim': 'Piyango', 'kapak': 'Piyango.jpg'},
    {'id': 385, 'isim': 'Maymun Kral', 'kapak': 'Maymun Kral.jpg'},
    {'id': 386, 'isim': 'Kör Suikastçi', 'kapak': 'Kör Suikastçi.jpg'},
    {'id': 387, 'isim': 'Nam-ı Diğer Grace', 'kapak': 'Nam-ı Diğer Grace.jpg'},
    {'id': 388, 'isim': 'Tufan Zamanı', 'kapak': 'Tufan Zamanı.jpg'},
    {'id': 389, 'isim': 'Antilop ve Flurya', 'kapak': 'Antilop ve Flurya.jpg'},
    {'id': 390, 'isim': 'Uçurtma Avcısı', 'kapak': 'Uçurtma Avcısı.jpg'},
    {'id': 391, 'isim': 'Bin Muhteşem Güneş', 'kapak': 'Bin Muhteşem Güneş.jpg'},
    {'id': 392, 'isim': 'Ve Dağlar Yankılandı', 'kapak': 'Ve Dağlar Yankılandı.jpg'},
    {'id': 393, 'isim': 'Semerkant', 'kapak': 'Semerkant.jpg'},
    {'id': 394, 'isim': 'Tanios Kayası', 'kapak': 'Tanios Kayası.jpg'},
    {'id': 395, 'isim': 'Doğunun Limanları', 'kapak': 'Doğunun Limanları.jpg'},
    {'id': 396, 'isim': 'Afrikalı Leo', 'kapak': 'Afrikalı Leo.jpg'},
    {'id': 397, 'isim': 'Yüzüncü Ad', 'kapak': 'Yüzüncü Ad.jpg'},
    {'id': 398, 'isim': 'Işık Bahçeleri', 'kapak': 'Işık Bahçeleri.jpg'},
    {'id': 399, 'isim': 'İmkansızın Şarkısı', 'kapak': 'İmkansızın Şarkısı.jpg'},
    {'id': 400, 'isim': 'Sahilde Kafka', 'kapak': 'Sahilde Kafka.jpg'},
    {'id': 401, 'isim': 'Zemberekkuşu nun Güncesi', 'kapak': 'Zemberekkuşu nun Güncesi.jpg'},
    {'id': 402, 'isim': '1Q84', 'kapak': '1Q84.jpg'},
    {'id': 403, 'isim': 'Sputnik Sevgilim', 'kapak': 'Sputnik Sevgilim.jpg'},
    {'id': 404, 'isim': 'Renksiz Tsukuru Tazaki nin Hac Yılları', 'kapak': 'Renksiz Tsukuru Tazaki nin Hac Yılları.jpg'},
    {'id': 405, 'isim': 'Koşmasaydım Yazamazdım', 'kapak': 'Koşmasaydım Yazamazdım.jpg'},
    {'id': 406, 'isim': 'Uyku', 'kapak': 'Uyku.jpg'},
    {'id': 407, 'isim': 'Karanlıktan Sonra', 'kapak': 'Karanlıktan Sonra.jpg'},
    {'id': 408, 'isim': 'Haşlanmış Harikalar Diyarı', 'kapak': 'Haşlanmış Harikalar Diyarı.jpg'},
    {'id': 409, 'isim': 'Sırça Fanus', 'kapak': 'Sırça Fanus.jpg'},
    {'id': 410, 'isim': 'Ariel', 'kapak': 'Ariel.jpg'},
    {'id': 411, 'isim': 'Colossus', 'kapak': 'Colossus.jpg'},
    {'id': 412, 'isim': 'Sevilen', 'kapak': 'Sevilen.jpg'},
    {'id': 413, 'isim': 'En Mavi Göz', 'kapak': 'En Mavi Göz.jpg'},
    {'id': 414, 'isim': 'Süleyman ın Şarkısı', 'kapak': 'Süleyman ın Şarkısı.jpg'},
    {'id': 415, 'isim': 'Cezire', 'kapak': 'Cezire.jpg'},
    {'id': 416, 'isim': 'Sevgili', 'kapak': 'Sevgili.jpg'},
    {'id': 417, 'isim': 'Hiroşima Sevgilim', 'kapak': 'Hiroşima Sevgilim.jpg'},
    {'id': 418, 'isim': 'Yengeç Dönencesi', 'kapak': 'Yengeç Dönencesi.jpg'},
    {'id': 419, 'isim': 'Sexus', 'kapak': 'Sexus.jpg'},
    {'id': 420, 'isim': 'Plexus', 'kapak': 'Plexus.jpg'},
    {'id': 421, 'isim': 'Nexus', 'kapak': 'Nexus.jpg'},
    {'id': 422, 'isim': 'Postane', 'kapak': 'Postane.jpg'},
    {'id': 423, 'isim': 'Kadınlar', 'kapak': 'Kadınlar.jpg'},
    {'id': 424, 'isim': 'Factotum', 'kapak': 'Factotum.jpg'},
    {'id': 425, 'isim': 'Ekmek Arası', 'kapak': 'Ekmek Arası.jpg'},
    {'id': 426, 'isim': 'Pis Moruğun Notları', 'kapak': 'Pis Moruğun Notları.jpg'},
    {'id': 427, 'isim': 'Gülüşün ve Unutuşun Kitabı', 'kapak': 'Gülüşün ve Unutuşun Kitabı.jpg'},
    {'id': 428, 'isim': 'Ayrılık Valsi', 'kapak': 'Ayrılık Valsi.jpg'},
    {'id': 429, 'isim': 'Şaka', 'kapak': 'Şaka.jpg'},
    {'id': 430, 'isim': 'Kimlik', 'kapak': 'Kimlik.jpg'},
    {'id': 431, 'isim': 'Bilgisizlik', 'kapak': 'Bilgisizlik.jpg'},
    {'id': 432, 'isim': 'Perde', 'kapak': 'Perde.jpg'},
    {'id': 433, 'isim': 'Karanlıkta Kahkaha', 'kapak': 'Karanlıkta Kahkaha.jpg'},
    {'id': 434, 'isim': 'Mars Yıllıkları', 'kapak': 'Mars Yıllıkları.jpg'},
    {'id': 435, 'isim': 'Resimli Adam', 'kapak': 'Resimli Adam.jpg'},
    {'id': 436, 'isim': 'Uğursuz Bir Şey Geliyor Bu Yana', 'kapak': 'Uğursuz Bir Şey Geliyor Bu Yana.jpg'},
    {'id': 437, 'isim': 'Karahindiba Şarabı', 'kapak': 'Karahindiba Şarabı.jpg'},
    {'id': 438, 'isim': 'Yakma Zevki', 'kapak': 'Yakma Zevki.jpg'},
    {'id': 439, 'isim': 'Çocukluğun Sonu', 'kapak': 'Çocukluğun Sonu.jpg'},
    {'id': 440, 'isim': 'Şehir ve Yıldızlar', 'kapak': 'Şehir ve Yıldızlar.jpg'},
    {'id': 441, 'isim': 'Vakıf Kurulurken', 'kapak': 'Vakıf Kurulurken.jpg'},
    {'id': 442, 'isim': 'Vakıf İleri', 'kapak': 'Vakıf İleri.jpg'},
    {'id': 443, 'isim': 'Kaplan Kaplan', 'kapak': 'Kaplan Kaplan.jpg'},
    {'id': 444, 'isim': 'Yıkıma Giden Adam', 'kapak': 'Yıkıma Giden Adam.jpg'},
    {'id': 445, 'isim': 'Yüksek Şatodaki Adam', 'kapak': 'Yüksek Şatodaki Adam.jpg'},
    {'id': 446, 'isim': 'Azınlık Raporu', 'kapak': 'Azınlık Raporu.jpg'},
    {'id': 447, 'isim': 'Ubik', 'kapak': 'Ubik.jpg'},
    {'id': 448, 'isim': 'Karanlığı Taramak', 'kapak': 'Karanlığı Taramak.jpg'},
    {'id': 449, 'isim': 'Sürgün Gezegeni', 'kapak': 'Sürgün Gezegeni.jpg'},
    {'id': 450, 'isim': 'Yerdeniz Öyküleri', 'kapak': 'Yerdeniz Öyküleri.jpg'},
    {'id': 451, 'isim': 'En Uzak Sahil', 'kapak': 'En Uzak Sahil.jpg'},
    {'id': 452, 'isim': 'Tehanu', 'kapak': 'Tehanu.jpg'},
    {'id': 453, 'isim': 'Rüzgarın On İki Köşesi', 'kapak': 'Rüzgarın On İki Köşesi.jpg'},
    {'id': 454, 'isim': 'Yokyer', 'kapak': 'Yokyer.jpg'},
    {'id': 455, 'isim': 'Koralin', 'kapak': 'Koralin.jpg'},
    {'id': 456, 'isim': 'Mezarlık Kitabı', 'kapak': 'Mezarlık Kitabı.jpg'},
    {'id': 457, 'isim': 'Yıldız Tozu', 'kapak': 'Yıldız Tozu.jpg'},
    {'id': 458, 'isim': 'Kıyamet Gösterisi', 'kapak': 'Kıyamet Gösterisi.jpg'},
    {'id': 459, 'isim': 'Diskdünya', 'kapak': 'Diskdünya.jpg'},
    {'id': 460, 'isim': 'Renklerin Büyüsü', 'kapak': 'Renklerin Büyüsü.jpg'},
    {'id': 461, 'isim': 'Fantastik Işık', 'kapak': 'Fantastik Işık.jpg'},
    {'id': 462, 'isim': 'Eşit Haklar', 'kapak': 'Eşit Haklar.jpg'},
    {'id': 463, 'isim': 'Mort', 'kapak': 'Mort.jpg'},
    {'id': 464, 'isim': 'Hareketli Resimler', 'kapak': 'Hareketli Resimler.jpg'},
    {'id': 465, 'isim': 'Zaman Çarkı', 'kapak': 'Zaman Çarkı.jpg'},
    {'id': 466, 'isim': 'Dünyanın Gözü', 'kapak': 'Dünyanın Gözü.jpg'},
    {'id': 467, 'isim': 'Büyük Av', 'kapak': 'Büyük Av.jpg'},
    {'id': 468, 'isim': 'Gölge Yükseliyor', 'kapak': 'Gölge Yükseliyor.jpg'},
    {'id': 469, 'isim': 'Göğün Ateşleri', 'kapak': 'Göğün Ateşleri.jpg'},
    {'id': 470, 'isim': 'Kaos Lordu', 'kapak': 'Kaos Lordu.jpg'},
    {'id': 471, 'isim': 'Kılıçtan Taç', 'kapak': 'Kılıçtan Taç.jpg'},
    {'id': 472, 'isim': 'Hançer Yolu', 'kapak': 'Hançer Yolu.jpg'},
    {'id': 473, 'isim': 'Kışın Yüreği', 'kapak': 'Kışın Yüreği.jpg'},
    {'id': 474, 'isim': 'Alacakaranlık Kavşağı', 'kapak': 'Alacakaranlık Kavşağı.jpg'},
    {'id': 475, 'isim': 'Düş Hançeri', 'kapak': 'Düş Hançeri.jpg'},
    {'id': 476, 'isim': 'Fırtına Toplanıyor', 'kapak': 'Fırtına Toplanıyor.jpg'},
    {'id': 477, 'isim': 'Işığın Anısı', 'kapak': 'Işığın Anısı.jpg'},
    {'id': 478, 'isim': 'Kralların Yolu', 'kapak': 'Kralların Yolu.jpg'},
    {'id': 479, 'isim': 'Parlayan Sözler', 'kapak': 'Parlayan Sözler.jpg'},
    {'id': 480, 'isim': 'Oathbringer', 'kapak': 'Oathbringer.jpg'},
    {'id': 481, 'isim': 'Elantris', 'kapak': 'Elantris.jpg'},
    {'id': 482, 'isim': 'Sissoylu', 'kapak': 'Sissoylu.jpg'},
    {'id': 483, 'isim': 'Kumpanya', 'kapak': 'Kumpanya.jpg'},
    {'id': 484, 'isim': 'Az Şekerli', 'kapak': 'Az Şekerli.jpg'},
    {'id': 485, 'isim': 'Havuz Başı', 'kapak': 'Havuz Başı.jpg'},
    {'id': 486, 'isim': 'Alemdağ da Var Bir Yılan', 'kapak': 'Alemdağ da Var Bir Yılan.jpg'},
    {'id': 487, 'isim': 'Babil Kulesi', 'kapak': 'Babil Kulesi.jpg'},
    {'id': 488, 'isim': 'Toros Canavarı', 'kapak': 'Toros Canavarı.jpg'},
    {'id': 489, 'isim': 'Keşanlı Ali Destanı', 'kapak': 'Keşanlı Ali Destanı.jpg'},
    {'id': 490, 'isim': 'Gözlerimi Kaparım Vazifemi Yaparım', 'kapak': 'Gözlerimi Kaparım Vazifemi Yaparım.jpg'},
    {'id': 491, 'isim': 'Sersem Kocanın Kurnaz Karısı', 'kapak': 'Sersem Kocanın Kurnaz Karısı.jpg'},
    {'id': 492, 'isim': 'Ayışığında Çalışkur', 'kapak': 'Ayışığında Çalışkur.jpg'},
    {'id': 493, 'isim': 'Fazilet Eczanesi', 'kapak': 'Fazilet Eczanesi.jpg'},
    {'id': 494, 'isim': 'Hayır', 'kapak': 'Hayır.jpg'},
    {'id': 495, 'isim': 'Fikrimin İnce Gülü', 'kapak': 'Fikrimin İnce Gülü.jpg'},
    {'id': 496, 'isim': 'Gece Hayatım', 'kapak': 'Gece Hayatım.jpg'},
    {'id': 497, 'isim': 'Romantik Bir Viyana Yazı', 'kapak': 'Romantik Bir Viyana Yazı.jpg'},
    {'id': 498, 'isim': 'Dert Dinleme Uzmanı', 'kapak': 'Dert Dinleme Uzmanı.jpg'},
    {'id': 499, 'isim': 'Parasız Yatılı', 'kapak': 'Parasız Yatılı.jpg'},
    {'id': 500, 'isim': 'Kuşatma', 'kapak': 'Kuşatma.jpg'},
    {'id': 501, 'isim': 'Benim Sinemalarım', 'kapak': 'Benim Sinemalarım.jpg'},
    {'id': 502, 'isim': 'Gül Mevsimidir', 'kapak': 'Gül Mevsimidir.jpg'},
    {'id': 503, 'isim': 'Kinyas ve Kayra', 'kapak': 'Kinyas ve Kayra.jpg'},
    {'id': 504, 'isim': 'Kayıp Hayaller Kitabı', 'kapak': 'Kayıp Hayaller Kitabı.jpg'},
    {'id': 505, 'isim': 'Heba', 'kapak': 'Heba.jpg'},
    {'id': 506, 'isim': 'Kuşlar Yasına Gider', 'kapak': 'Kuşlar Yasına Gider.jpg'},
    {'id': 507, 'isim': 'Beni Kör Kuyularda', 'kapak': 'Beni Kör Kuyularda.jpg'},
    {'id': 508, 'isim': 'Sonsuzluğa Nokta', 'kapak': 'Sonsuzluğa Nokta.jpg'},
    {'id': 509, 'isim': 'Uykuların Doğusu', 'kapak': 'Uykuların Doğusu.jpg'},
    {'id': 510, 'isim': 'Har', 'kapak': 'Har.jpg'},
    {'id': 511, 'isim': 'Yüksek Topuklar', 'kapak': 'Yüksek Topuklar.jpg'},
    {'id': 512, 'isim': 'Karanlıkta Sabah Kuşları', 'kapak': 'Karanlıkta Sabah Kuşları.jpg'},
    {'id': 513, 'isim': 'Nefes Nefese', 'kapak': 'Nefes Nefese.jpg'},
    {'id': 514, 'isim': 'Veda', 'kapak': 'Veda.jpg'},
    {'id': 515, 'isim': 'Umut', 'kapak': 'Umut.jpg'},
    {'id': 516, 'isim': 'Hayat', 'kapak': 'Hayat.jpg'},
    {'id': 517, 'isim': 'Gizli Anların Yolcusu', 'kapak': 'Gizli Anların Yolcusu.jpg'},
    {'id': 518, 'isim': 'Bora nın Kitabı', 'kapak': 'Bora nın Kitabı.jpg'},
    {'id': 519, 'isim': 'Dönüş', 'kapak': 'Dönüş.jpg'},
    {'id': 520, 'isim': 'Kardelenler', 'kapak': 'Kardelenler.jpg'},
    {'id': 521, 'isim': 'Tek ve Tek', 'kapak': 'Tek ve Tek.jpg'},
    {'id': 522, 'isim': 'Serenad', 'kapak': 'Serenad.jpg'},
    {'id': 523, 'isim': 'Kardeşimin Hikayesi', 'kapak': 'Kardeşimin Hikayesi.jpg'},
    {'id': 524, 'isim': 'Mutluluk', 'kapak': 'Mutluluk.jpg'},
    {'id': 525, 'isim': 'Son Ada', 'kapak': 'Son Ada.jpg'},
    {'id': 526, 'isim': 'Leyla nın Evi', 'kapak': 'Leyla nın Evi.jpg'},
    {'id': 527, 'isim': 'Huzursuzluk', 'kapak': 'Huzursuzluk.jpg'},
    {'id': 528, 'isim': 'Balıkçı ve Oğlu', 'kapak': 'Balıkçı ve Oğlu.jpg'},
    {'id': 529, 'isim': 'Konstantiniyye Oteli', 'kapak': 'Konstantiniyye Oteli.jpg'},
    {'id': 530, 'isim': 'Kaplanın Sırtında', 'kapak': 'Kaplanın Sırtında.jpg'},
    {'id': 531, 'isim': 'Engereğin Gözü', 'kapak': 'Engereğin Gözü.jpg'},
    {'id': 532, 'isim': 'Aşk', 'kapak': 'Aşk.jpg'},
    {'id': 533, 'isim': 'Baba ve Piç', 'kapak': 'Baba ve Piç.jpg'},
    {'id': 534, 'isim': 'Mahrem', 'kapak': 'Mahrem.jpg'},
    {'id': 535, 'isim': 'Bit Palas', 'kapak': 'Bit Palas.jpg'},
    {'id': 536, 'isim': 'Araf', 'kapak': 'Araf.jpg'},
    {'id': 537, 'isim': 'Siyah Süt', 'kapak': 'Siyah Süt.jpg'},
    {'id': 538, 'isim': 'İskender', 'kapak': 'İskender.jpg'},
    {'id': 539, 'isim': 'Ustam ve Ben', 'kapak': 'Ustam ve Ben.jpg'},
    {'id': 540, 'isim': 'Havva nın Üç Kızı', 'kapak': 'Havva nın Üç Kızı.jpg'},
    {'id': 541, 'isim': 'On Dakika Otuz Sekiz Saniye', 'kapak': 'On Dakika Otuz Sekiz Saniye.jpg'},
    {'id': 542, 'isim': 'Öteki Renkler', 'kapak': 'Öteki Renkler.jpg'},
    {'id': 543, 'isim': 'İstanbul Hatıralar ve Şehir', 'kapak': 'İstanbul Hatıralar ve Şehir.jpg'},
    {'id': 544, 'isim': 'Yeşil Yol', 'kapak': 'Yeşil Yol.jpg'},
    {'id': 545, 'isim': 'Hayvan Mezarlığı', 'kapak': 'Hayvan Mezarlığı.jpg'},
    {'id': 546, 'isim': 'İhanet Noktası', 'kapak': 'İhanet Noktası.jpg'},
    {'id': 547, 'isim': 'Kayıp Sembol', 'kapak': 'Kayıp Sembol.jpg'},
    {'id': 548, 'isim': 'Cehennem', 'kapak': 'Cehennem.jpg'},
    {'id': 549, 'isim': 'Başlangıç', 'kapak': 'Başlangıç.jpg'},
    {'id': 550, 'isim': 'Ejderha Dövmeli Kız', 'kapak': 'Ejderha Dövmeli Kız.jpg'},
    {'id': 551, 'isim': 'Ateşle Oynayan Kız', 'kapak': 'Ateşle Oynayan Kız.jpg'},
    {'id': 552, 'isim': 'Arı Kovanına Çomak Sokan Kız', 'kapak': 'Arı Kovanına Çomak Sokan Kız.jpg'},
    {'id': 553, 'isim': 'Örümcek Ağındaki Kız', 'kapak': 'Örümcek Ağındaki Kız.jpg'},
    {'id': 554, 'isim': 'Trendeki Kız', 'kapak': 'Trendeki Kız.jpg'},
    {'id': 555, 'isim': 'Kayıp Kız', 'kapak': 'Kayıp Kız.jpg'},
    {'id': 556, 'isim': 'Sessiz Hasta', 'kapak': 'Sessiz Hasta.jpg'},
    {'id': 557, 'isim': 'Kafes', 'kapak': 'Kafes.jpg'},
    {'id': 558, 'isim': 'Gece Yarısı Kütüphanesi', 'kapak': 'Gece Yarısı Kütüphanesi.jpg'},
    {'id': 559, 'isim': 'Kazanan Yalnızdır', 'kapak': 'Kazanan Yalnızdır.jpg'},
    {'id': 560, 'isim': 'Elif', 'kapak': 'Elif.jpg'},
    {'id': 561, 'isim': 'Aldatmak', 'kapak': 'Aldatmak.jpg'},
    {'id': 562, 'isim': 'Akılsız Sokrates', 'kapak': 'Akılsız Sokrates.jpg'},
    {'id': 563, 'isim': 'Bir İdam Mahkumunun Son Günü', 'kapak': 'Bir İdam Mahkumunun Son Günü.jpg'},
    {'id': 564, 'isim': 'Nişanlıya Mektuplar', 'kapak': 'Nişanlıya Mektuplar.jpg'},
    {'id': 565, 'isim': 'Yalnız Gezerin Düşleri', 'kapak': 'Yalnız Gezerin Düşleri.jpg'},
    {'id': 566, 'isim': 'Bilimler ve Sanatlar Üzerine Söylev', 'kapak': 'Bilimler ve Sanatlar Üzerine Söylev.jpg'},
    {'id': 567, 'isim': 'İnsanlar Arasındaki Eşitsizliğin Kaynağı', 'kapak': 'İnsanlar Arasındaki Eşitsizliğin Kaynağı.jpg'},
    {'id': 568, 'isim': 'Yeni Heloise', 'kapak': 'Yeni Heloise.jpg'},
    {'id': 569, 'isim': 'Mikromegas', 'kapak': 'Mikromegas.jpg'},
    {'id': 570, 'isim': 'Ütopya', 'kapak': 'Ütopya.jpg'},
    {'id': 571, 'isim': 'Güneş Ülkesi', 'kapak': 'Güneş Ülkesi.jpg'},
    {'id': 572, 'isim': 'Yeni Atlantis', 'kapak': 'Yeni Atlantis.jpg'},
    {'id': 573, 'isim': 'Deliliğe Övgü', 'kapak': 'Deliliğe Övgü.jpg'},
    {'id': 574, 'isim': 'Hükümdar', 'kapak': 'Hükümdar.jpg'},
    {'id': 575, 'isim': 'Söylevler', 'kapak': 'Söylevler.jpg'},
    {'id': 576, 'isim': 'Altıncı Koğuş', 'kapak': 'Altıncı Koğuş.jpg'},
    {'id': 577, 'isim': 'Üç Yıl', 'kapak': 'Üç Yıl.jpg'},
    {'id': 578, 'isim': 'Düello', 'kapak': 'Düello.jpg'},
    {'id': 579, 'isim': 'Jacob ın Odası', 'kapak': 'Jacob ın Odası.jpg'},
    {'id': 580, 'isim': 'Perde Arası', 'kapak': 'Perde Arası.jpg'},
    {'id': 581, 'isim': 'Kızıl Dosya', 'kapak': 'Kızıl Dosya.jpg'},
    {'id': 582, 'isim': 'Dörtlerin İmzası', 'kapak': 'Dörtlerin İmzası.jpg'},
    {'id': 583, 'isim': 'Baskerville Tazısı', 'kapak': 'Baskerville Tazısı.jpg'},
    {'id': 584, 'isim': 'Korku Vadisi', 'kapak': 'Korku Vadisi.jpg'},
    {'id': 585, 'isim': 'Akıl Oyunlarının Gölgesinde', 'kapak': 'Akıl Oyunlarının Gölgesinde.jpg'},
    {'id': 586, 'isim': 'On Küçük Zenci', 'kapak': 'On Küçük Zenci.jpg'},
    {'id': 587, 'isim': 'Doğu Ekspresinde Cinayet', 'kapak': 'Doğu Ekspresinde Cinayet.jpg'},
    {'id': 588, 'isim': 'Nil de Ölüm', 'kapak': 'Nil de Ölüm.jpg'},
    {'id': 589, 'isim': 'Roger Ackroyd Cinayeti', 'kapak': 'Roger Ackroyd Cinayeti.jpg'},
    {'id': 590, 'isim': 'Ve Perde İndi', 'kapak': 'Ve Perde İndi.jpg'},
    {'id': 591, 'isim': 'Morgue Sokağı Cinayetleri', 'kapak': 'Morgue Sokağı Cinayetleri.jpg'},
    {'id': 592, 'isim': 'Kuzgun', 'kapak': 'Kuzgun.jpg'},
    {'id': 593, 'isim': 'Altın Böcek', 'kapak': 'Altın Böcek.jpg'},
    {'id': 594, 'isim': 'Kara Kedi', 'kapak': 'Kara Kedi.jpg'},
    {'id': 595, 'isim': 'Cthulhu nun Çağrısı', 'kapak': 'Cthulhu nun Çağrısı.jpg'},
    {'id': 596, 'isim': 'Deliliğin Dağlarında', 'kapak': 'Deliliğin Dağlarında.jpg'},
    {'id': 597, 'isim': 'Dagon', 'kapak': 'Dagon.jpg'},
    {'id': 598, 'isim': 'Innsmouth un Üzerindeki Gölge', 'kapak': 'Innsmouth un Üzerindeki Gölge.jpg'},
    {'id': 599, 'isim': 'Operadaki Hayalet', 'kapak': 'Operadaki Hayalet.jpg'},
    {'id': 600, 'isim': 'Otranto Şatosu', 'kapak': 'Otranto Şatosu.jpg'},
    {'id': 601, 'isim': 'Vampir', 'kapak': 'Vampir.jpg'},
    {'id': 602, 'isim': 'Carmilla', 'kapak': 'Carmilla.jpg'},
    {'id': 603, 'isim': 'Golem', 'kapak': 'Golem.jpg'},
    {'id': 604, 'isim': 'Malta Şahini', 'kapak': 'Malta Şahini.jpg'},
    {'id': 605, 'isim': 'Büyük Uyku', 'kapak': 'Büyük Uyku.jpg'},
    {'id': 606, 'isim': 'Postacı Kapıyı İki Kere Çalar', 'kapak': 'Postacı Kapıyı İki Kere Çalar.jpg'},
    {'id': 607, 'isim': 'Dövüş Kulübü', 'kapak': 'Dövüş Kulübü.jpg'},
    {'id': 608, 'isim': 'Tıkanma', 'kapak': 'Tıkanma.jpg'},
    {'id': 609, 'isim': 'Görünmez Canavarlar', 'kapak': 'Görünmez Canavarlar.jpg'},
    {'id': 610, 'isim': 'Gösteri Peygamberi', 'kapak': 'Gösteri Peygamberi.jpg'},
    {'id': 611, 'isim': 'Trainspotting', 'kapak': 'Trainspotting.jpg'},
    {'id': 612, 'isim': 'Porno', 'kapak': 'Porno.jpg'},
    {'id': 613, 'isim': 'Baba', 'kapak': 'Baba.jpg'},
    {'id': 614, 'isim': 'Kelebek', 'kapak': 'Kelebek.jpg'},
    {'id': 615, 'isim': 'Kuzuların Sessizliği', 'kapak': 'Kuzuların Sessizliği.jpg'},
    {'id': 616, 'isim': 'Hannibal', 'kapak': 'Hannibal.jpg'},
    {'id': 617, 'isim': 'Kızıl Ejder', 'kapak': 'Kızıl Ejder.jpg'},
    {'id': 618, 'isim': 'Ben Efsaneyim', 'kapak': 'Ben Efsaneyim.jpg'},
    {'id': 619, 'isim': 'Kuşlar', 'kapak': 'Kuşlar.jpg'},
    {'id': 620, 'isim': 'Jaws', 'kapak': 'Jaws.jpg'},
    {'id': 621, 'isim': 'Jurassic Park', 'kapak': 'Jurassic Park.jpg'},
    {'id': 622, 'isim': 'Forrest Gump', 'kapak': 'Forrest Gump.jpg'},
    {'id': 623, 'isim': 'Rüzgar Gibi Geçti', 'kapak': 'Rüzgar Gibi Geçti.jpg'},
    {'id': 624, 'isim': 'Love Story', 'kapak': 'Love Story.jpg'},
    {'id': 625, 'isim': 'Ben-Hur', 'kapak': 'Ben-Hur.jpg'},
    {'id': 626, 'isim': 'Son Mohikan', 'kapak': 'Son Mohikan.jpg'},
    {'id': 627, 'isim': 'Yeşil Işık', 'kapak': 'Yeşil Işık.jpg'},
    {'id': 628, 'isim': 'Benjamin Button ın Tuhaf Hikayesi', 'kapak': 'Benjamin Button ın Tuhaf Hikayesi.jpg'},
    {'id': 629, 'isim': 'Prestij', 'kapak': 'Prestij.jpg'},
    {'id': 630, 'isim': 'V for Vendetta', 'kapak': 'V for Vendetta.jpg'},
    {'id': 631, 'isim': 'Maus', 'kapak': 'Maus.jpg'},
    {'id': 632, 'isim': 'Watchmen', 'kapak': 'Watchmen.jpg'},
    {'id': 633, 'isim': 'Persepolis', 'kapak': 'Persepolis.jpg'},
    {'id': 634, 'isim': 'Sandman', 'kapak': 'Sandman.jpg'},
    {'id': 635, 'isim': 'Batman Öldüren Şaka', 'kapak': 'Batman Öldüren Şaka.jpg'},
    {'id': 636, 'isim': 'Günah Şehri', 'kapak': 'Günah Şehri.jpg'},
    {'id': 637, 'isim': 'Killing Joke', 'kapak': 'Killing Joke.jpg'},
    {'id': 638, 'isim': 'Görünmez Kentler', 'kapak': 'Görünmez Kentler.jpg'},
    {'id': 639, 'isim': 'Bir Kış Gecesi Eğer Bir Yolcu', 'kapak': 'Bir Kış Gecesi Eğer Bir Yolcu.jpg'},
    {'id': 640, 'isim': 'İkiye Bölünen Vikont', 'kapak': 'İkiye Bölünen Vikont.jpg'},
    {'id': 641, 'isim': 'Ağaca Tüneyen Baron', 'kapak': 'Ağaca Tüneyen Baron.jpg'},
    {'id': 642, 'isim': 'Marcovaldo', 'kapak': 'Marcovaldo.jpg'},
    {'id': 643, 'isim': 'Amerika Dersleri', 'kapak': 'Amerika Dersleri.jpg'},
    {'id': 644, 'isim': 'Palomar', 'kapak': 'Palomar.jpg'},
    {'id': 645, 'isim': 'Zorba', 'kapak': 'Zorba.jpg'},
    {'id': 646, 'isim': 'Günaha Son Çağrı', 'kapak': 'Günaha Son Çağrı.jpg'},
    {'id': 647, 'isim': 'Kaptan Mihalis', 'kapak': 'Kaptan Mihalis.jpg'},
    {'id': 648, 'isim': 'El Greco ya Mektuplar', 'kapak': 'El Greco ya Mektuplar.jpg'},
    {'id': 649, 'isim': 'İskenderiye Dörtlüsü', 'kapak': 'İskenderiye Dörtlüsü.jpg'},
    {'id': 650, 'isim': 'Balthazar', 'kapak': 'Balthazar.jpg'},
    {'id': 651, 'isim': 'Mountolive', 'kapak': 'Mountolive.jpg'},
    {'id': 652, 'isim': 'Clea', 'kapak': 'Clea.jpg'},
    {'id': 653, 'isim': 'Yengeç Yürüyüşü', 'kapak': 'Yengeç Yürüyüşü.jpg'},
    {'id': 654, 'isim': 'Artemio Cruz un Ölümü', 'kapak': 'Artemio Cruz un Ölümü.jpg'},
    {'id': 655, 'isim': 'Teke Şenliği', 'kapak': 'Teke Şenliği.jpg'},
    {'id': 656, 'isim': 'Kent ve Köpekler', 'kapak': 'Kent ve Köpekler.jpg'},
    {'id': 657, 'isim': 'Masalcı', 'kapak': 'Masalcı.jpg'},
    {'id': 658, 'isim': 'And Dağlarında Terör', 'kapak': 'And Dağlarında Terör.jpg'},
    {'id': 659, 'isim': 'Yukarı Mahalle', 'kapak': 'Yukarı Mahalle.jpg'},
    {'id': 660, 'isim': 'Sardalye Sokağı', 'kapak': 'Sardalye Sokağı.jpg'},
    {'id': 661, 'isim': 'Al Midilli', 'kapak': 'Al Midilli.jpg'},
    {'id': 662, 'isim': 'Bir Maskenin İtirafları', 'kapak': 'Bir Maskenin İtirafları.jpg'},
    {'id': 663, 'isim': 'Altın Köşk Tapınağı', 'kapak': 'Altın Köşk Tapınağı.jpg'},
    {'id': 664, 'isim': 'Denizi Yitiren Denizci', 'kapak': 'Denizi Yitiren Denizci.jpg'},
    {'id': 665, 'isim': 'İnsanlığımı Yitirirken', 'kapak': 'İnsanlığımı Yitirirken.jpg'},
    {'id': 666, 'isim': 'Karlar Ülkesi', 'kapak': 'Karlar Ülkesi.jpg'},
    {'id': 667, 'isim': 'Kiraz Çiçekleri', 'kapak': 'Kiraz Çiçekleri.jpg'},
    {'id': 668, 'isim': 'Rashomon', 'kapak': 'Rashomon.jpg'},
    {'id': 669, 'isim': 'Narziss ve Goldmund', 'kapak': 'Narziss ve Goldmund.jpg'},
    {'id': 670, 'isim': 'Doğu Yolculuğu', 'kapak': 'Doğu Yolculuğu.jpg'},
    {'id': 671, 'isim': 'Rosshalde', 'kapak': 'Rosshalde.jpg'},
    {'id': 672, 'isim': 'Knulp', 'kapak': 'Knulp.jpg'},
    {'id': 673, 'isim': 'Gertrud', 'kapak': 'Gertrud.jpg'},
    {'id': 674, 'isim': 'Momo', 'kapak': 'Momo.jpg'},
    {'id': 675, 'isim': 'Bitmeyecek Öykü', 'kapak': 'Bitmeyecek Öykü.jpg'},
    {'id': 676, 'isim': 'Charlie nin Çikolata Fabrikası', 'kapak': 'Charlie nin Çikolata Fabrikası.jpg'},
    {'id': 677, 'isim': 'Matilda', 'kapak': 'Matilda.jpg'},
    {'id': 678, 'isim': 'Koca Sevimli Dev', 'kapak': 'Koca Sevimli Dev.jpg'},
    {'id': 679, 'isim': 'Cadılar', 'kapak': 'Cadılar.jpg'},
    {'id': 680, 'isim': 'Bay ve Bayan Kıl', 'kapak': 'Bay ve Bayan Kıl.jpg'},
    {'id': 681, 'isim': 'Dev Şeftali', 'kapak': 'Dev Şeftali.jpg'},
    {'id': 682, 'isim': 'Heidi', 'kapak': 'Heidi.jpg'},
    {'id': 683, 'isim': 'Polyanna', 'kapak': 'Polyanna.jpg'},
    {'id': 684, 'isim': 'Küçük Kadınlar', 'kapak': 'Küçük Kadınlar.jpg'},
    {'id': 685, 'isim': 'Siyah İnci', 'kapak': 'Siyah İnci.jpg'},
    {'id': 686, 'isim': 'Lassie', 'kapak': 'Lassie.jpg'},
    {'id': 687, 'isim': 'Demiryolu Çocukları', 'kapak': 'Demiryolu Çocukları.jpg'},
    {'id': 688, 'isim': 'Gizli Bahçe', 'kapak': 'Gizli Bahçe.jpg'},
    {'id': 689, 'isim': 'Küçük Lord', 'kapak': 'Küçük Lord.jpg'},
    {'id': 690, 'isim': 'Robin Hood', 'kapak': 'Robin Hood.jpg'},
    {'id': 691, 'isim': 'Kral Arthur ve Yuvarlak Masa Şövalyeleri', 'kapak': 'Kral Arthur ve Yuvarlak Masa Şövalyeleri.jpg'},
    {'id': 692, 'isim': 'Pinokyo', 'kapak': 'Pinokyo.jpg'},
    {'id': 693, 'isim': 'Bambi', 'kapak': 'Bambi.jpg'},
    {'id': 694, 'isim': 'Orman Çocuğu', 'kapak': 'Orman Çocuğu.jpg'},
    {'id': 695, 'isim': 'Oz Büyücüsü', 'kapak': 'Oz Büyücüsü.jpg'},
    {'id': 696, 'isim': 'Pıtırcık', 'kapak': 'Pıtırcık.jpg'},
    {'id': 697, 'isim': 'Pıtırcık Tatilde', 'kapak': 'Pıtırcık Tatilde.jpg'},
    {'id': 698, 'isim': 'Uyumsuz', 'kapak': 'Uyumsuz.jpg'},
    {'id': 699, 'isim': 'Kuralsız', 'kapak': 'Kuralsız.jpg'},
    {'id': 700, 'isim': 'Yandaş', 'kapak': 'Yandaş.jpg'},
    {'id': 701, 'isim': 'Labirent Ölümcül Kaçış', 'kapak': 'Labirent Ölümcül Kaçış.jpg'},
    {'id': 702, 'isim': 'Açlık Oyunları', 'kapak': 'Açlık Oyunları.jpg'},
    {'id': 703, 'isim': 'Ateşi Yakalamak', 'kapak': 'Ateşi Yakalamak.jpg'},
    {'id': 704, 'isim': 'Karşı', 'kapak': 'Karşı.jpg'},
    {'id': 705, 'isim': 'Sevda Sözleri', 'kapak': 'Sevda Sözleri.jpg'},
    {'id': 706, 'isim': 'Beni Öp Sonra Doğur Beni', 'kapak': 'Beni Öp Sonra Doğur Beni.jpg'},
    {'id': 707, 'isim': 'Üvercinka', 'kapak': 'Üvercinka.jpg'},
    {'id': 708, 'isim': 'Göçebe', 'kapak': 'Göçebe.jpg'},
    {'id': 709, 'isim': 'Sıcak Nal', 'kapak': 'Sıcak Nal.jpg'},
    {'id': 710, 'isim': 'Büyük Saat', 'kapak': 'Büyük Saat.jpg'},
    {'id': 711, 'isim': 'Dünyanın En Güzel Arabistanı', 'kapak': 'Dünyanın En Güzel Arabistanı.jpg'},
    {'id': 712, 'isim': 'Divan', 'kapak': 'Divan.jpg'},
    {'id': 713, 'isim': 'Tragedyalar', 'kapak': 'Tragedyalar.jpg'},
    {'id': 714, 'isim': 'Umutsuzlar Parkı', 'kapak': 'Umutsuzlar Parkı.jpg'},
    {'id': 715, 'isim': 'Körfez', 'kapak': 'Körfez.jpg'},
    {'id': 716, 'isim': 'Yaşayıp Ölmek', 'kapak': 'Yaşayıp Ölmek.jpg'},
    {'id': 717, 'isim': 'Avare Çalı', 'kapak': 'Avare Çalı.jpg'},
    {'id': 718, 'isim': 'Çile', 'kapak': 'Çile.jpg'},
    {'id': 719, 'isim': 'Örümcek Ağı', 'kapak': 'Örümcek Ağı.jpg'},
    {'id': 720, 'isim': 'Kaldırımlar', 'kapak': 'Kaldırımlar.jpg'},
    {'id': 721, 'isim': 'Dublörün Dilemması', 'kapak': 'Dublörün Dilemması.jpg'},
    {'id': 722, 'isim': 'Korkma Ben Varım', 'kapak': 'Korkma Ben Varım.jpg'},
    {'id': 723, 'isim': 'Ruhi Mücerret', 'kapak': 'Ruhi Mücerret.jpg'},
    {'id': 724, 'isim': 'Antika Titanik', 'kapak': 'Antika Titanik.jpg'},
    {'id': 725, 'isim': 'Şeyh ve Hükümdar', 'kapak': 'Şeyh ve Hükümdar.jpg'},
    {'id': 726, 'isim': 'Oğullar ve Rencide Ruhlar', 'kapak': 'Oğullar ve Rencide Ruhlar.jpg'},
    {'id': 727, 'isim': 'Gizliajans', 'kapak': 'Gizliajans.jpg'},
    {'id': 728, 'isim': 'Cehennem Çiçeği', 'kapak': 'Cehennem Çiçeği.jpg'},
    {'id': 729, 'isim': 'Tatlı Rüyalar', 'kapak': 'Tatlı Rüyalar.jpg'},
    {'id': 730, 'isim': 'Kan ve Gül', 'kapak': 'Kan ve Gül.jpg'},
    {'id': 731, 'isim': 'Piç', 'kapak': 'Piç.jpg'},
    {'id': 732, 'isim': 'Daha', 'kapak': 'Daha.jpg'},
    {'id': 733, 'isim': 'Tol', 'kapak': 'Tol.jpg'},
    {'id': 734, 'isim': 'Yara', 'kapak': 'Yara.jpg'},
    {'id': 735, 'isim': 'Unutma Bahçesi', 'kapak': 'Unutma Bahçesi.jpg'},
    {'id': 736, 'isim': 'Yaz Yağmuru', 'kapak': 'Yaz Yağmuru.jpg'},
    {'id': 737, 'isim': 'Hikayeler Tanpınar', 'kapak': 'Hikayeler Tanpınar.jpg'},
    {'id': 738, 'isim': 'Dost', 'kapak': 'Dost.jpg'},
    {'id': 739, 'isim': 'Bay Muannit Sahtegi nin Notları', 'kapak': 'Bay Muannit Sahtegi nin Notları.jpg'},
    {'id': 740, 'isim': 'Korku', 'kapak': 'Korku.jpg'},
    {'id': 741, 'isim': 'Yedi Kapılı Kırk Oda', 'kapak': 'Yedi Kapılı Kırk Oda.jpg'},
    {'id': 742, 'isim': 'Gecenin Kapıları', 'kapak': 'Gecenin Kapıları.jpg'},
    {'id': 743, 'isim': 'Kılavuz', 'kapak': 'Kılavuz.jpg'},
    {'id': 744, 'isim': 'Masal Masal İçinde', 'kapak': 'Masal Masal İçinde.jpg'},
    {'id': 745, 'isim': 'Aritmetik İyi Kuşlar Pekiyi', 'kapak': 'Aritmetik İyi Kuşlar Pekiyi.jpg'},
    {'id': 746, 'isim': 'Kadın', 'kapak': 'Kadın.jpg'},
    {'id': 747, 'isim': 'Sessiz Bir Ölüm', 'kapak': 'Sessiz Bir Ölüm.jpg'},
    {'id': 748, 'isim': 'Yürüme', 'kapak': 'Yürüme.jpg'},
    {'id': 749, 'isim': 'Sivil İtaatsizlik', 'kapak': 'Sivil İtaatsizlik.jpg'},
    {'id': 750, 'isim': 'Walden', 'kapak': 'Walden.jpg'},
    {'id': 751, 'isim': 'Doğal Yaşam ve Başkaldırı', 'kapak': 'Doğal Yaşam ve Başkaldırı.jpg'},
    {'id': 752, 'isim': 'Kışın', 'kapak': 'Kışın.jpg'},
    {'id': 753, 'isim': 'İnsanın Anlam Arayışı', 'kapak': 'İnsanın Anlam Arayışı.jpg'},
    {'id': 754, 'isim': 'Cinsel Aşkın Metafiziği', 'kapak': 'Cinsel Aşkın Metafiziği.jpg'},
    {'id': 755, 'isim': 'Aşkın Metafiziği', 'kapak': 'Aşkın Metafiziği.jpg'},
    {'id': 756, 'isim': 'Okumak Yazmak ve Yaşamak Üzerine', 'kapak': 'Okumak Yazmak ve Yaşamak Üzerine.jpg'},
    {'id': 757, 'isim': 'Mutlu Olma Sanatı', 'kapak': 'Mutlu Olma Sanatı.jpg'},
    {'id': 758, 'isim': 'Yaşam Bilgeliği Üzerine Aforizmalar', 'kapak': 'Yaşam Bilgeliği Üzerine Aforizmalar.jpg'},
    {'id': 759, 'isim': 'Tarih Felsefesi', 'kapak': 'Tarih Felsefesi.jpg'},
    {'id': 760, 'isim': 'Fragmanlar', 'kapak': 'Fragmanlar.jpg'},
    {'id': 761, 'isim': 'Herakleitos', 'kapak': 'Herakleitos.jpg'},
    {'id': 762, 'isim': 'Sokrates in Savunması', 'kapak': 'Sokrates in Savunması.jpg'},
    {'id': 763, 'isim': 'Euthyphron', 'kapak': 'Euthyphron.jpg'},
    {'id': 764, 'isim': 'Sofist', 'kapak': 'Sofist.jpg'},
    {'id': 765, 'isim': 'Parmenides', 'kapak': 'Parmenides.jpg'},
    {'id': 766, 'isim': 'Theaetetus', 'kapak': 'Theaetetus.jpg'},
    {'id': 767, 'isim': 'Protagoras', 'kapak': 'Protagoras.jpg'},
    {'id': 768, 'isim': 'Gorgias', 'kapak': 'Gorgias.jpg'},
    {'id': 769, 'isim': 'Meno', 'kapak': 'Meno.jpg'},
    {'id': 770, 'isim': 'Timaios', 'kapak': 'Timaios.jpg'},
    {'id': 771, 'isim': 'Metafizik Üzerine Konuşma', 'kapak': 'Metafizik Üzerine Konuşma.jpg'},
    {'id': 772, 'isim': 'Monadoloji', 'kapak': 'Monadoloji.jpg'},
    {'id': 773, 'isim': 'Teodise', 'kapak': 'Teodise.jpg'},
    {'id': 774, 'isim': 'Yöntem Üzerine Konuşma', 'kapak': 'Yöntem Üzerine Konuşma.jpg'},
    {'id': 775, 'isim': 'Meditasyonlar', 'kapak': 'Meditasyonlar.jpg'},
    {'id': 776, 'isim': 'Felsefenin İlkeleri', 'kapak': 'Felsefenin İlkeleri.jpg'},
    {'id': 777, 'isim': 'Ruhun Tutkuları', 'kapak': 'Ruhun Tutkuları.jpg'},
    {'id': 778, 'isim': 'Aklın Yönetimi İçin Kurallar', 'kapak': 'Aklın Yönetimi İçin Kurallar.jpg'},
    {'id': 779, 'isim': 'Ethica', 'kapak': 'Ethica.jpg'},
    {'id': 780, 'isim': 'Teolojik-Politik İnceleme', 'kapak': 'Teolojik-Politik İnceleme.jpg'},
    {'id': 781, 'isim': 'Anlama Yetisinin Düzeltilmesi Üzerine', 'kapak': 'Anlama Yetisinin Düzeltilmesi Üzerine.jpg'},
    {'id': 782, 'isim': 'Yarının Tarihi', 'kapak': 'Yarının Tarihi.jpg'},
    {'id': 783, 'isim': 'Yıldızın Parladığı Anlar', 'kapak': 'Yıldızın Parladığı Anlar.jpg'},
    {'id': 784, 'isim': 'Vicdan Zorbalığa Karşı', 'kapak': 'Vicdan Zorbalığa Karşı.jpg'},
    {'id': 785, 'isim': 'Bir Kadının Yirmi Dört Saati', 'kapak': 'Bir Kadının Yirmi Dört Saati.jpg'},
    {'id': 786, 'isim': 'Olağanüstü Bir Gece', 'kapak': 'Olağanüstü Bir Gece.jpg'},
    {'id': 787, 'isim': 'Geçmişe Yolculuk', 'kapak': 'Geçmişe Yolculuk.jpg'},
    {'id': 788, 'isim': 'Clarissa', 'kapak': 'Clarissa.jpg'},
    {'id': 789, 'isim': 'Gömülü Şamdan', 'kapak': 'Gömülü Şamdan.jpg'},
    {'id': 790, 'isim': 'Hayatın Mucizeleri', 'kapak': 'Hayatın Mucizeleri.jpg'},
    {'id': 791, 'isim': 'Arzu Tramvayı', 'kapak': 'Arzu Tramvayı.jpg'},
    {'id': 792, 'isim': 'Oyun Sonu', 'kapak': 'Oyun Sonu.jpg'},
    {'id': 793, 'isim': 'Ayı', 'kapak': 'Ayı.jpg'},
    {'id': 794, 'isim': 'Sandalyeler', 'kapak': 'Sandalyeler.jpg'},
    {'id': 795, 'isim': 'Balkon', 'kapak': 'Balkon.jpg'},
    {'id': 796, 'isim': 'Paravanlar', 'kapak': 'Paravanlar.jpg'},
    {'id': 797, 'isim': 'Fizikçiler', 'kapak': 'Fizikçiler.jpg'},
    {'id': 798, 'isim': 'Andorra', 'kapak': 'Andorra.jpg'},
    {'id': 799 , 'isim': 'Moravia' , 'kapak': 'Moravia.jpg'},
    {'id': 800 , 'isim': 'Girdap' , 'kapak': 'Girdap.jpg'}
]

hobiler = [
    {'id': 1, 'isim': '3D Yazıcı', 'klasor': '3D Yazıcı'},
    {'id': 2, 'isim': 'Acı Sos Yapımı', 'klasor': 'Acı Sos Yapımı'},
    {'id': 3, 'isim': 'Ahşap Yontma', 'klasor': 'Ahşap Yontma'},
    {'id': 4, 'isim': 'Ahşap İşçiliği', 'klasor': 'Ahşap İşçiliği'},
    {'id': 5, 'isim': 'Aikido', 'klasor': 'Aikido'},
    {'id': 6, 'isim': 'Airsoft', 'klasor': 'Airsoft'},
    {'id': 7, 'isim': 'Akordeon Çalmak', 'klasor': 'Akordeon Çalmak'},
    {'id': 8, 'isim': 'Akraba Ziyareti', 'klasor': 'Akraba Ziyareti'},
    {'id': 9, 'isim': 'Akrobatik Yoga', 'klasor': 'Akrobatik Yoga'},
    {'id': 10, 'isim': 'Aksiyon Figürü Koleksiyonu', 'klasor': 'Aksiyon Figürü Koleksiyonu'},
    {'id': 11, 'isim': 'Akvaryum Dizaynı', 'klasor': 'Akvaryum Dizaynı'},
    {'id': 12, 'isim': 'Akvaryumculuk', 'klasor': 'Akvaryumculuk'},
    {'id': 13, 'isim': 'Akıllı Ev Sistemleri Kurma', 'klasor': 'Akıllı Ev Sistemleri Kurma'},
    {'id': 14, 'isim': 'Akşam Yemeği Pişirmek', 'klasor': 'Akşam Yemeği Pişirmek'},
    {'id': 15, 'isim': 'Albüm Yapımı (Scrapbook)', 'klasor': 'Albüm Yapımı (Scrapbook)'},
    {'id': 16, 'isim': 'Alışveriş Yapmak', 'klasor': 'Alışveriş Yapmak'},
    {'id': 17, 'isim': 'Amerikan Futbolu', 'klasor': 'Amerikan Futbolu'},
    {'id': 18, 'isim': 'Amigurumi (Örgü Bebek)', 'klasor': 'Amigurumi (Örgü Bebek)'},
    {'id': 19, 'isim': 'Anahtarlık Koleksiyonu', 'klasor': 'Anahtarlık Koleksiyonu'},
    {'id': 20, 'isim': 'Analog Fotoğrafçılık (Film)', 'klasor': 'Analog Fotoğrafçılık (Film)'},
    {'id': 21, 'isim': 'Animasyon Yapımı', 'klasor': 'Animasyon Yapımı'},
    {'id': 22, 'isim': 'Anime İzlemek', 'klasor': 'Anime İzlemek'},
    {'id': 23, 'isim': 'Antika Koleksiyonu', 'klasor': 'Antika Koleksiyonu'},
    {'id': 24, 'isim': 'Antika Mobilya Yenileme', 'klasor': 'Antika Mobilya Yenileme'},
    {'id': 25, 'isim': 'Araba Modifiye', 'klasor': 'Araba Modifiye'},
    {'id': 26, 'isim': 'Araba Sürmek', 'klasor': 'Araba Sürmek'},
    {'id': 27, 'isim': 'Arkadaşlarla Takılmak', 'klasor': 'Arkadaşlarla Takılmak'},
    {'id': 28, 'isim': 'Aromaterapi', 'klasor': 'Aromaterapi'},
    {'id': 29, 'isim': 'Arp Çalmak', 'klasor': 'Arp Çalmak'},
    {'id': 30, 'isim': 'Artistik Buz Pateni', 'klasor': 'Artistik Buz Pateni'},
    {'id': 31, 'isim': 'Artırılmış Gerçeklik (AR)', 'klasor': 'Artırılmış Gerçeklik (AR)'},
    {'id': 32, 'isim': 'Arıcılık', 'klasor': 'Arıcılık'},
    {'id': 33, 'isim': 'Astral Seyahat', 'klasor': 'Astral Seyahat'},
    {'id': 34, 'isim': 'Astroloji', 'klasor': 'Astroloji'},
    {'id': 35, 'isim': 'Astronomi', 'klasor': 'Astronomi'},
    {'id': 36, 'isim': 'At Bakımı (Tımar)', 'klasor': 'At Bakımı (Tımar)'},
    {'id': 37, 'isim': 'Atari Salonu Oyunları', 'klasor': 'Atari Salonu Oyunları'},
    {'id': 38, 'isim': 'Ateş Dansı (Poi)', 'klasor': 'Ateş Dansı (Poi)'},
    {'id': 39, 'isim': 'Ateş Püskürtme', 'klasor': 'Ateş Püskürtme'},
    {'id': 40, 'isim': 'Atkı Örmek', 'klasor': 'Atkı Örmek'},
    {'id': 41, 'isim': 'Atıksız Yaşam', 'klasor': 'Atıksız Yaşam'},
    {'id': 42, 'isim': 'Ayak Voleybolu', 'klasor': 'Ayak Voleybolu'},
    {'id': 43, 'isim': 'Ayakkabı Yapımı', 'klasor': 'Ayakkabı Yapımı'},
    {'id': 44, 'isim': 'BMX Yarışı', 'klasor': 'BMX Yarışı'},
    {'id': 45, 'isim': 'Badminton', 'klasor': 'Badminton'},
    {'id': 46, 'isim': 'Bahçecilik', 'klasor': 'Bahçecilik'},
    {'id': 47, 'isim': 'Bakırcılık', 'klasor': 'Bakırcılık'},
    {'id': 48, 'isim': 'Bale', 'klasor': 'Bale'},
    {'id': 49, 'isim': 'Balina Gözlemciliği', 'klasor': 'Balina Gözlemciliği'},
    {'id': 50, 'isim': 'Balon Katlama Sanatı', 'klasor': 'Balon Katlama Sanatı'},
    {'id': 51, 'isim': 'Baloncuk Üflemek', 'klasor': 'Baloncuk Üflemek'},
    {'id': 52, 'isim': 'Balık Tutma', 'klasor': 'Balık Tutma'},
    {'id': 53, 'isim': 'Banjo Çalmak', 'klasor': 'Banjo Çalmak'},
    {'id': 54, 'isim': 'Baristalık', 'klasor': 'Baristalık'},
    {'id': 55, 'isim': 'Bas Gitar Çalmak', 'klasor': 'Bas Gitar Çalmak'},
    {'id': 56, 'isim': 'Basketbol', 'klasor': 'Basketbol'},
    {'id': 57, 'isim': 'Basınçlı Yıkama Yapmak', 'klasor': 'Basınçlı Yıkama Yapmak'},
    {'id': 58, 'isim': 'Bateri Çalmak', 'klasor': 'Bateri Çalmak'},
    {'id': 59, 'isim': 'Batik Boyama', 'klasor': 'Batik Boyama'},
    {'id': 60, 'isim': 'Batik Tişört Boyama', 'klasor': 'Batik Tişört Boyama'},
    {'id': 61, 'isim': 'Bavul Hazırlamak', 'klasor': 'Bavul Hazırlamak'},
    {'id': 62, 'isim': 'Beer Pong', 'klasor': 'Beer Pong'},
    {'id': 63, 'isim': 'Belgesel İzlemek', 'klasor': 'Belgesel İzlemek'},
    {'id': 64, 'isim': 'Berberlik', 'klasor': 'Berberlik'},
    {'id': 65, 'isim': 'Beyzbol', 'klasor': 'Beyzbol'},
    {'id': 66, 'isim': 'Bez Bebek Yapımı', 'klasor': 'Bez Bebek Yapımı'},
    {'id': 67, 'isim': 'Bilardo', 'klasor': 'Bilardo'},
    {'id': 68, 'isim': 'Bilgisayar Tamiri', 'klasor': 'Bilgisayar Tamiri'},
    {'id': 69, 'isim': 'Bilgisayar Toplama', 'klasor': 'Bilgisayar Toplama'},
    {'id': 70, 'isim': 'Binicilik', 'klasor': 'Binicilik'},
    {'id': 71, 'isim': 'Bira Yapımı', 'klasor': 'Bira Yapımı'},
    {'id': 72, 'isim': 'Bira İçmek', 'klasor': 'Bira İçmek'},
    {'id': 73, 'isim': 'Bisiklet', 'klasor': 'Bisiklet'},
    {'id': 74, 'isim': 'Bisiklet Sürmek (Gezinti)', 'klasor': 'Bisiklet Sürmek (Gezinti)'},
    {'id': 75, 'isim': 'Bitki Bilimi', 'klasor': 'Bitki Bilimi'},
    {'id': 76, 'isim': 'Bitki Budama Sanatı (Şekilli)', 'klasor': 'Bitki Budama Sanatı (Şekilli)'},
    {'id': 77, 'isim': 'Blog Okumak', 'klasor': 'Blog Okumak'},
    {'id': 78, 'isim': 'Blog Yazmak', 'klasor': 'Blog Yazmak'},
    {'id': 79, 'isim': 'Bobsled', 'klasor': 'Bobsled'},
    {'id': 80, 'isim': 'Bocce', 'klasor': 'Bocce'},
    {'id': 81, 'isim': 'Boks', 'klasor': 'Boks'},
    {'id': 82, 'isim': 'Bongo Çalmak', 'klasor': 'Bongo Çalmak'},
    {'id': 83, 'isim': 'Bonsai Şekillendirme', 'klasor': 'Bonsai Şekillendirme'},
    {'id': 84, 'isim': 'Botanik', 'klasor': 'Botanik'},
    {'id': 85, 'isim': 'Bowling Oynamak', 'klasor': 'Bowling Oynamak'},
    {'id': 86, 'isim': 'Boyama Kitabı Boyamak', 'klasor': 'Boyama Kitabı Boyamak'},
    {'id': 87, 'isim': 'Boğa Biniciliği (Rodeo)', 'klasor': 'Boğa Biniciliği (Rodeo)'},
    {'id': 88, 'isim': 'Braille Alfabesi Öğrenme', 'klasor': 'Braille Alfabesi Öğrenme'},
    {'id': 89, 'isim': 'Break Dans', 'klasor': 'Break Dans'},
    {'id': 90, 'isim': 'Bulmaca Çözmek', 'klasor': 'Bulmaca Çözmek'},
    {'id': 91, 'isim': 'Bulutları İzlemek', 'klasor': 'Bulutları İzlemek'},
    {'id': 92, 'isim': 'Bungee Jumping', 'klasor': 'Bungee Jumping'},
    {'id': 93, 'isim': 'Buz Heykeltraşlığı', 'klasor': 'Buz Heykeltraşlığı'},
    {'id': 94, 'isim': 'Buz Hokeyi', 'klasor': 'Buz Hokeyi'},
    {'id': 95, 'isim': 'Buz Tırmanışı', 'klasor': 'Buz Tırmanışı'},
    {'id': 96, 'isim': 'Buzda Balık Avı', 'klasor': 'Buzda Balık Avı'},
    {'id': 97, 'isim': 'Böcek Bilimi', 'klasor': 'Böcek Bilimi'},
    {'id': 98, 'isim': 'Bıçak Bileme', 'klasor': 'Bıçak Bileme'},
    {'id': 99, 'isim': 'Bıçak Fırlatma', 'klasor': 'Bıçak Fırlatma'},
    {'id': 100, 'isim': 'Bıçak Yapımı', 'klasor': 'Bıçak Yapımı'},
    {'id': 101, 'isim': 'Cam Boyama', 'klasor': 'Cam Boyama'},
    {'id': 102, 'isim': 'Cam Silmek (Tatmin Edici)', 'klasor': 'Cam Silmek (Tatmin Edici)'},
    {'id': 103, 'isim': 'Canlı Heykel', 'klasor': 'Canlı Heykel'},
    {'id': 104, 'isim': 'Canlı Rol Yapma Oyunu (LARP)', 'klasor': 'Canlı Rol Yapma Oyunu (LARP)'},
    {'id': 105, 'isim': 'Capoeira', 'klasor': 'Capoeira'},
    {'id': 106, 'isim': 'Cilt Bakımı Yapmak', 'klasor': 'Cilt Bakımı Yapmak'},
    {'id': 107, 'isim': 'Cosplay', 'klasor': 'Cosplay'},
    {'id': 108, 'isim': 'Coğrafya Çalışmak', 'klasor': 'Coğrafya Çalışmak'},
    {'id': 109, 'isim': "DJ'lik", 'klasor': "DJ'lik"},
    {'id': 110, 'isim': 'Daktilo Koleksiyonu', 'klasor': 'Daktilo Koleksiyonu'},
    {'id': 111, 'isim': 'Daktilo Yazmak', 'klasor': 'Daktilo Yazmak'},
    {'id': 112, 'isim': 'Dalış', 'klasor': 'Dalış'},
    {'id': 113, 'isim': 'Dans', 'klasor': 'Dans'},
    {'id': 114, 'isim': 'Dantel Yapımı', 'klasor': 'Dantel Yapımı'},
    {'id': 115, 'isim': 'Dart', 'klasor': 'Dart'},
    {'id': 116, 'isim': 'Dedektörle Hazine Arama', 'klasor': 'Dedektörle Hazine Arama'},
    {'id': 117, 'isim': 'Dekorasyon Yapmak', 'klasor': 'Dekorasyon Yapmak'},
    {'id': 118, 'isim': 'Demircilik', 'klasor': 'Demircilik'},
    {'id': 119, 'isim': 'Deniz Kabuğu Koleksiyonu', 'klasor': 'Deniz Kabuğu Koleksiyonu'},
    {'id': 120, 'isim': 'Deniz Kabuğu Toplamak', 'klasor': 'Deniz Kabuğu Toplamak'},
    {'id': 121, 'isim': 'Deniz Paraşütü', 'klasor': 'Deniz Paraşütü'},
    {'id': 122, 'isim': 'Dergi Okumak', 'klasor': 'Dergi Okumak'},
    {'id': 123, 'isim': 'Deri İşçiliği', 'klasor': 'Deri İşçiliği'},
    {'id': 124, 'isim': 'Didgeridoo Çalmak', 'klasor': 'Didgeridoo Çalmak'},
    {'id': 125, 'isim': 'Dijital Boyama', 'klasor': 'Dijital Boyama'},
    {'id': 126, 'isim': 'Dijital Göçebelik', 'klasor': 'Dijital Göçebelik'},
    {'id': 127, 'isim': 'Dikey Bahçecilik', 'klasor': 'Dikey Bahçecilik'},
    {'id': 128, 'isim': 'Dikiş', 'klasor': 'Dikiş'},
    {'id': 129, 'isim': 'Dil Öğrenmek', 'klasor': 'Dil Öğrenmek'},
    {'id': 130, 'isim': 'Direk Dansı (Fitness)', 'klasor': 'Direk Dansı (Fitness)'},
    {'id': 131, 'isim': 'Disk İtme Oyunu', 'klasor': 'Disk İtme Oyunu'},
    {'id': 132, 'isim': 'Dizi İzlemek', 'klasor': 'Dizi İzlemek'},
    {'id': 133, 'isim': 'Djembe Çalmak', 'klasor': 'Djembe Çalmak'},
    {'id': 134, 'isim': 'Dokumacılık', 'klasor': 'Dokumacılık'},
    {'id': 135, 'isim': 'Dolma Kalemle Yazmak', 'klasor': 'Dolma Kalemle Yazmak'},
    {'id': 136, 'isim': 'Domino', 'klasor': 'Domino'},
    {'id': 137, 'isim': 'Dondurma Yemek', 'klasor': 'Dondurma Yemek'},
    {'id': 138, 'isim': 'Doğa Yürüyüşü', 'klasor': 'Doğa Yürüyüşü'},
    {'id': 139, 'isim': 'Doğada Yaşam (Bushcraft)', 'klasor': 'Doğada Yaşam (Bushcraft)'},
    {'id': 140, 'isim': 'Drift Yapmak', 'klasor': 'Drift Yapmak'},
    {'id': 141, 'isim': 'Drone Uçurmak', 'klasor': 'Drone Uçurmak'},
    {'id': 142, 'isim': 'Drone Yarışı', 'klasor': 'Drone Yarışı'},
    {'id': 143, 'isim': 'Duvar Sanatı (Grafiti)', 'klasor': 'Duvar Sanatı (Grafiti)'},
    {'id': 144, 'isim': 'Dövme Yapmak', 'klasor': 'Dövme Yapmak'},
    {'id': 145, 'isim': 'Döşemecilik', 'klasor': 'Döşemecilik'},
    {'id': 146, 'isim': 'Düzenlemek (Organizasyon)', 'klasor': 'Düzenlemek (Organizasyon)'},
    {'id': 147, 'isim': 'Düğme Koleksiyonu', 'klasor': 'Düğme Koleksiyonu'},
    {'id': 148, 'isim': 'Ebru Sanatı', 'klasor': 'Ebru Sanatı'},
    {'id': 149, 'isim': 'Ekmek Yapımı (Ekşi Maya)', 'klasor': 'Ekmek Yapımı (Ekşi Maya)'},
    {'id': 150, 'isim': 'El Falı', 'klasor': 'El Falı'},
    {'id': 151, 'isim': 'Elektronik Lehimleme', 'klasor': 'Elektronik Lehimleme'},
    {'id': 152, 'isim': 'Engel Parkuru', 'klasor': 'Engel Parkuru'},
    {'id': 153, 'isim': 'Eski Kamera Koleksiyonu', 'klasor': 'Eski Kamera Koleksiyonu'},
    {'id': 154, 'isim': 'Eskrim', 'klasor': 'Eskrim'},
    {'id': 155, 'isim': 'Esneme Hareketleri', 'klasor': 'Esneme Hareketleri'},
    {'id': 156, 'isim': 'Et Tütsüleme (Smoking)', 'klasor': 'Et Tütsüleme (Smoking)'},
    {'id': 157, 'isim': 'Ev Tamiratı Yapmak', 'klasor': 'Ev Tamiratı Yapmak'},
    {'id': 158, 'isim': 'Evcil Hayvan Sevmek', 'klasor': 'Evcil Hayvan Sevmek'},
    {'id': 159, 'isim': 'Evde Şarap Yapımı', 'klasor': 'Evde Şarap Yapımı'},
    {'id': 160, 'isim': 'Eğitim Videosu İzlemek', 'klasor': 'Eğitim Videosu İzlemek'},
    {'id': 161, 'isim': 'Eşya Yenileme', 'klasor': 'Eşya Yenileme'},
    {'id': 162, 'isim': 'Eşyaların Yerini Değiştirmek', 'klasor': 'Eşyaların Yerini Değiştirmek'},
    {'id': 163, 'isim': 'FRP (Dungeons & Dragons)', 'klasor': 'FRP (Dungeons & Dragons)'},
    {'id': 164, 'isim': 'Fantezi Futbol Ligi', 'klasor': 'Fantezi Futbol Ligi'},
    {'id': 165, 'isim': 'Fantezi Spor Ligi Yönetmek', 'klasor': 'Fantezi Spor Ligi Yönetmek'},
    {'id': 166, 'isim': 'Felsefe Okumaları', 'klasor': 'Felsefe Okumaları'},
    {'id': 167, 'isim': 'Feng Shui Düzenleme', 'klasor': 'Feng Shui Düzenleme'},
    {'id': 168, 'isim': 'Festivale Katılmak', 'klasor': 'Festivale Katılmak'},
    {'id': 169, 'isim': 'Film İzlemek', 'klasor': 'Film İzlemek'},
    {'id': 170, 'isim': 'Fitness', 'klasor': 'Fitness'},
    {'id': 171, 'isim': 'Fizik Deneyleri', 'klasor': 'Fizik Deneyleri'},
    {'id': 172, 'isim': 'Flyboard', 'klasor': 'Flyboard'},
    {'id': 173, 'isim': 'Flüt Çalmak', 'klasor': 'Flüt Çalmak'},
    {'id': 174, 'isim': 'Fotoğrafçılık', 'klasor': 'Fotoğrafçılık'},
    {'id': 175, 'isim': 'Frizbi Golfü', 'klasor': 'Frizbi Golfü'},
    {'id': 176, 'isim': 'Frizbi Oynamak', 'klasor': 'Frizbi Oynamak'},
    {'id': 177, 'isim': 'Funko Pop Figür Koleksiyonu', 'klasor': 'Funko Pop Figür Koleksiyonu'},
    {'id': 178, 'isim': 'Futbol', 'klasor': 'Futbol'},
    {'id': 179, 'isim': 'Fırtına Avcılığı', 'klasor': 'Fırtına Avcılığı'},
    {'id': 180, 'isim': 'Gayda Çalmak', 'klasor': 'Gayda Çalmak'},
    {'id': 181, 'isim': 'Gazete Okumak', 'klasor': 'Gazete Okumak'},
    {'id': 182, 'isim': 'Gemi Gözlemciliği', 'klasor': 'Gemi Gözlemciliği'},
    {'id': 183, 'isim': 'Gereksiz Bilgiler Öğrenmek', 'klasor': 'Gereksiz Bilgiler Öğrenmek'},
    {'id': 184, 'isim': 'Gerilla Bahçecilik', 'klasor': 'Gerilla Bahçecilik'},
    {'id': 185, 'isim': 'Geçici Hayvan Bakıcılığı', 'klasor': 'Geçici Hayvan Bakıcılığı'},
    {'id': 186, 'isim': 'Gitar Çalmak', 'klasor': 'Gitar Çalmak'},
    {'id': 187, 'isim': 'Go Oyunu', 'klasor': 'Go Oyunu'},
    {'id': 188, 'isim': 'Go-Kart', 'klasor': 'Go-Kart'},
    {'id': 189, 'isim': 'Golf', 'klasor': 'Golf'},
    {'id': 190, 'isim': 'Grafiti', 'klasor': 'Grafiti'},
    {'id': 191, 'isim': 'Gönüllülük', 'klasor': 'Gönüllülük'},
    {'id': 192, 'isim': 'Gümüş İşçiliği', 'klasor': 'Gümüş İşçiliği'},
    {'id': 193, 'isim': 'Gün Batımını İzlemek', 'klasor': 'Gün Batımını İzlemek'},
    {'id': 194, 'isim': 'Gün Doğumunu İzlemek', 'klasor': 'Gün Doğumunu İzlemek'},
    {'id': 195, 'isim': 'Güneş Enerjisi Projeleri', 'klasor': 'Güneş Enerjisi Projeleri'},
    {'id': 196, 'isim': 'Güneşlenmek', 'klasor': 'Güneşlenmek'},
    {'id': 197, 'isim': 'Günlük Tutmak', 'klasor': 'Günlük Tutmak'},
    {'id': 198, 'isim': 'Günlük Yazmak', 'klasor': 'Günlük Yazmak'},
    {'id': 199, 'isim': 'Güreş', 'klasor': 'Güreş'},
    {'id': 200, 'isim': 'Güvercin Yarıştırma', 'klasor': 'Güvercin Yarıştırma'},
    {'id': 201, 'isim': 'Güç Kaldırma (Powerlifting)', 'klasor': 'Güç Kaldırma (Powerlifting)'},
    {'id': 202, 'isim': 'Hafif Koşu', 'klasor': 'Hafif Koşu'},
    {'id': 203, 'isim': 'Hafıza Teknikleri Çalışmak', 'klasor': 'Hafıza Teknikleri Çalışmak'},
    {'id': 204, 'isim': 'Haiku Yazma', 'klasor': 'Haiku Yazma'},
    {'id': 205, 'isim': 'Halat Çekme', 'klasor': 'Halat Çekme'},
    {'id': 206, 'isim': 'Hamburger Yemek', 'klasor': 'Hamburger Yemek'},
    {'id': 207, 'isim': 'Hamur İşi', 'klasor': 'Hamur İşi'},
    {'id': 208, 'isim': 'Harita Koleksiyonu', 'klasor': 'Harita Koleksiyonu'},
    {'id': 209, 'isim': 'Hasır Örmeciliği', 'klasor': 'Hasır Örmeciliği'},
    {'id': 210, 'isim': 'Hava Hokeyi', 'klasor': 'Hava Hokeyi'},
    {'id': 211, 'isim': 'Havai Fişek İzlemek', 'klasor': 'Havai Fişek İzlemek'},
    {'id': 212, 'isim': 'Hayal Kurmak', 'klasor': 'Hayal Kurmak'},
    {'id': 213, 'isim': 'Hayalet Avcılığı', 'klasor': 'Hayalet Avcılığı'},
    {'id': 214, 'isim': 'Hayatta Kalma Becerileri (Survival)', 'klasor': 'Hayatta Kalma Becerileri (Survival)'},
    {'id': 215, 'isim': 'Hayran Kurgusu Yazma', 'klasor': 'Hayran Kurgusu Yazma'},
    {'id': 216, 'isim': 'Hayır Kurumu Çalışması', 'klasor': 'Hayır Kurumu Çalışması'},
    {'id': 217, 'isim': 'Hazine Avcılığı', 'klasor': 'Hazine Avcılığı'},
    {'id': 218, 'isim': 'Hentbol', 'klasor': 'Hentbol'},
    {'id': 219, 'isim': 'Heykel', 'klasor': 'Heykel'},
    {'id': 220, 'isim': 'Hip Hop Dansı', 'klasor': 'Hip Hop Dansı'},
    {'id': 221, 'isim': 'Hiyeroglif Okumak', 'klasor': 'Hiyeroglif Okumak'},
    {'id': 222, 'isim': 'Hula Hoop Çevirme', 'klasor': 'Hula Hoop Çevirme'},
    {'id': 223, 'isim': 'Hurling', 'klasor': 'Hurling'},
    {'id': 224, 'isim': 'Hızlı Okuma', 'klasor': 'Hızlı Okuma'},
    {'id': 225, 'isim': 'Hızlı Oyun Bitirme (Speedrun)', 'klasor': 'Hızlı Oyun Bitirme (Speedrun)'},
    {'id': 226, 'isim': 'Hızlı Puzzle Yapma', 'klasor': 'Hızlı Puzzle Yapma'},
    {'id': 227, 'isim': "Instagram'da Gezinmek", 'klasor': "Instagram'da Gezinmek"},
    {'id': 228, 'isim': 'Jenga', 'klasor': 'Jenga'},
    {'id': 229, 'isim': 'Jet Ski', 'klasor': 'Jet Ski'},
    {'id': 230, 'isim': 'Jiu Jitsu', 'klasor': 'Jiu Jitsu'},
    {'id': 231, 'isim': 'Jonglörlük', 'klasor': 'Jonglörlük'},
    {'id': 232, 'isim': 'Judo', 'klasor': 'Judo'},
    {'id': 233, 'isim': 'Kafe Gezmek', 'klasor': 'Kafe Gezmek'},
    {'id': 234, 'isim': 'Kahvaltı Hazırlamak', 'klasor': 'Kahvaltı Hazırlamak'},
    {'id': 235, 'isim': 'Kahve Demleme', 'klasor': 'Kahve Demleme'},
    {'id': 236, 'isim': 'Kahve Kavurma', 'klasor': 'Kahve Kavurma'},
    {'id': 237, 'isim': 'Kahve İçmek', 'klasor': 'Kahve İçmek'},
    {'id': 238, 'isim': 'Kaktüs Koleksiyonu', 'klasor': 'Kaktüs Koleksiyonu'},
    {'id': 239, 'isim': 'Kalem Koleksiyonu', 'klasor': 'Kalem Koleksiyonu'},
    {'id': 240, 'isim': 'Kaligrafi', 'klasor': 'Kaligrafi'},
    {'id': 241, 'isim': 'Kalistenik (Vücut Ağırlığı)', 'klasor': 'Kalistenik (Vücut Ağırlığı)'},
    {'id': 242, 'isim': 'Kamp Yapmak', 'klasor': 'Kamp Yapmak'},
    {'id': 243, 'isim': 'Kanaviçe', 'klasor': 'Kanaviçe'},
    {'id': 244, 'isim': 'Kanepe Sörfü (Misafirlik)', 'klasor': 'Kanepe Sörfü (Misafirlik)'},
    {'id': 245, 'isim': 'Kano', 'klasor': 'Kano'},
    {'id': 246, 'isim': 'Kar Motoru Sürme', 'klasor': 'Kar Motoru Sürme'},
    {'id': 247, 'isim': 'Kar Yürüyüşü', 'klasor': 'Kar Yürüyüşü'},
    {'id': 248, 'isim': 'Karalama Yapmak', 'klasor': 'Karalama Yapmak'},
    {'id': 249, 'isim': 'Karanlık Oda (Film Banyo)', 'klasor': 'Karanlık Oda (Film Banyo)'},
    {'id': 250, 'isim': 'Karaoke', 'klasor': 'Karaoke'},
    {'id': 251, 'isim': 'Karate', 'klasor': 'Karate'},
    {'id': 252, 'isim': 'Kart Numaraları (Cardistry)', 'klasor': 'Kart Numaraları (Cardistry)'},
    {'id': 253, 'isim': 'Kartpostal Koleksiyonu', 'klasor': 'Kartpostal Koleksiyonu'},
    {'id': 254, 'isim': 'Karınca Çiftliği (Formicarium)', 'klasor': 'Karınca Çiftliği (Formicarium)'},
    {'id': 255, 'isim': 'Kasaplık', 'klasor': 'Kasaplık'},
    {'id': 256, 'isim': 'Kaset Dinlemek', 'klasor': 'Kaset Dinlemek'},
    {'id': 257, 'isim': 'Kayak', 'klasor': 'Kayak'},
    {'id': 258, 'isim': 'Kaykay', 'klasor': 'Kaykay'},
    {'id': 259, 'isim': 'Kaykay Hareketleri', 'klasor': 'Kaykay Hareketleri'},
    {'id': 260, 'isim': 'Kaçış Odası', 'klasor': 'Kaçış Odası'},
    {'id': 261, 'isim': 'Kağıt Kıvırma Sanatı', 'klasor': 'Kağıt Kıvırma Sanatı'},
    {'id': 262, 'isim': 'Kağıt Oynamak (İskambil)', 'klasor': 'Kağıt Oynamak (İskambil)'},
    {'id': 263, 'isim': 'Kağıt Yapımı', 'klasor': 'Kağıt Yapımı'},
    {'id': 264, 'isim': 'Kaşık Oymacılığı', 'klasor': 'Kaşık Oymacılığı'},
    {'id': 265, 'isim': 'Kefir Yapmak', 'klasor': 'Kefir Yapmak'},
    {'id': 266, 'isim': 'Kelebek Gözlemciliği', 'klasor': 'Kelebek Gözlemciliği'},
    {'id': 267, 'isim': 'Keman Çalmak', 'klasor': 'Keman Çalmak'},
    {'id': 268, 'isim': 'Kement Atma', 'klasor': 'Kement Atma'},
    {'id': 269, 'isim': 'Kestirmek (Şekerleme)', 'klasor': 'Kestirmek (Şekerleme)'},
    {'id': 270, 'isim': 'Keçe Yapımı', 'klasor': 'Keçe Yapımı'},
    {'id': 271, 'isim': 'Kick Boks', 'klasor': 'Kick Boks'},
    {'id': 272, 'isim': 'Kilit Açma Hobbisi', 'klasor': 'Kilit Açma Hobbisi'},
    {'id': 273, 'isim': 'Kimya Deneyleri', 'klasor': 'Kimya Deneyleri'},
    {'id': 274, 'isim': 'Kitap Okumak', 'klasor': 'Kitap Okumak'},
    {'id': 275, 'isim': 'Klarnet Çalmak', 'klasor': 'Klarnet Çalmak'},
    {'id': 276, 'isim': 'Klasik Araba Kullanmak', 'klasor': 'Klasik Araba Kullanmak'},
    {'id': 277, 'isim': 'Klasik Araba Restorasyonu', 'klasor': 'Klasik Araba Restorasyonu'},
    {'id': 278, 'isim': 'Kokteyl Yapımı', 'klasor': 'Kokteyl Yapımı'},
    {'id': 279, 'isim': 'Kombucha Yapmak', 'klasor': 'Kombucha Yapmak'},
    {'id': 280, 'isim': 'Konsere Gitmek', 'klasor': 'Konsere Gitmek'},
    {'id': 281, 'isim': 'Konserve Yapımı', 'klasor': 'Konserve Yapımı'},
    {'id': 282, 'isim': 'Koroda Şarkı Söylemek', 'klasor': 'Koroda Şarkı Söylemek'},
    {'id': 283, 'isim': 'Kovalamaca Oynamak', 'klasor': 'Kovalamaca Oynamak'},
    {'id': 284, 'isim': 'Koyun Gütme (Çobanlık)', 'klasor': 'Koyun Gütme (Çobanlık)'},
    {'id': 285, 'isim': 'Koşu', 'klasor': 'Koşu'},
    {'id': 286, 'isim': 'Kriket', 'klasor': 'Kriket'},
    {'id': 287, 'isim': 'Kripto Para Ticareti', 'klasor': 'Kripto Para Ticareti'},
    {'id': 288, 'isim': 'Kristal Koleksiyonu', 'klasor': 'Kristal Koleksiyonu'},
    {'id': 289, 'isim': 'Ksilenofon Çalmak', 'klasor': 'Ksilenofon Çalmak'},
    {'id': 290, 'isim': 'Kuklacılık', 'klasor': 'Kuklacılık'},
    {'id': 291, 'isim': 'Kung Fu', 'klasor': 'Kung Fu'},
    {'id': 292, 'isim': 'Kupa Koleksiyonu', 'klasor': 'Kupa Koleksiyonu'},
    {'id': 293, 'isim': 'Kupon Biriktirme', 'klasor': 'Kupon Biriktirme'},
    {'id': 294, 'isim': 'Kurabiye Yapmak', 'klasor': 'Kurabiye Yapmak'},
    {'id': 295, 'isim': 'Kutu Bulma Oyunu (Geocaching)', 'klasor': 'Kutu Bulma Oyunu (Geocaching)'},
    {'id': 296, 'isim': 'Kutu Oyunları', 'klasor': 'Kutu Oyunları'},
    {'id': 297, 'isim': 'Kuş Gözlemciliği', 'klasor': 'Kuş Gözlemciliği'},
    {'id': 298, 'isim': 'Kuş Yemlemek', 'klasor': 'Kuş Yemlemek'},
    {'id': 299, 'isim': 'Köpek Eğitimi', 'klasor': 'Köpek Eğitimi'},
    {'id': 300, 'isim': 'Köpek Gezdirmek', 'klasor': 'Köpek Gezdirmek'},
    {'id': 301, 'isim': 'Köpük Banyosu', 'klasor': 'Köpük Banyosu'},
    {'id': 302, 'isim': 'Kümes Hayvanı Yetiştirme', 'klasor': 'Kümes Hayvanı Yetiştirme'},
    {'id': 303, 'isim': 'Kürek Çekme', 'klasor': 'Kürek Çekme'},
    {'id': 304, 'isim': 'Kütüphaneye Gitmek', 'klasor': 'Kütüphaneye Gitmek'},
    {'id': 305, 'isim': 'Küvet Keyfi Yapmak', 'klasor': 'Küvet Keyfi Yapmak'},
    {'id': 306, 'isim': 'Kına Sanatı (Hint Kınası)', 'klasor': 'Kına Sanatı (Hint Kınası)'},
    {'id': 307, 'isim': 'Kırbaç Şovu', 'klasor': 'Kırbaç Şovu'},
    {'id': 308, 'isim': 'Kırkyama (Yorgancılık)', 'klasor': 'Kırkyama (Yorgancılık)'},
    {'id': 309, 'isim': 'Kıyafet Tadilatı', 'klasor': 'Kıyafet Tadilatı'},
    {'id': 310, 'isim': 'Kızak Kayma', 'klasor': 'Kızak Kayma'},
    {'id': 311, 'isim': 'Lakros', 'klasor': 'Lakros'},
    {'id': 312, 'isim': 'Langırt', 'klasor': 'Langırt'},
    {'id': 313, 'isim': 'Latince Öğrenmek', 'klasor': 'Latince Öğrenmek'},
    {'id': 314, 'isim': 'Latte Sanatı', 'klasor': 'Latte Sanatı'},
    {'id': 315, 'isim': 'Lazer Savaşı', 'klasor': 'Lazer Savaşı'},
    {'id': 316, 'isim': 'Lego Yapmak', 'klasor': 'Lego Yapmak'},
    {'id': 317, 'isim': 'Lucid Rüya (Bilinçli Rüya)', 'klasor': 'Lucid Rüya (Bilinçli Rüya)'},
    {'id': 318, 'isim': 'Magnet Koleksiyonu', 'klasor': 'Magnet Koleksiyonu'},
    {'id': 319, 'isim': 'Maket Yapımı', 'klasor': 'Maket Yapımı'},
    {'id': 320, 'isim': 'Makrome', 'klasor': 'Makrome'},
    {'id': 321, 'isim': 'Makyaj Yapmak', 'klasor': 'Makyaj Yapmak'},
    {'id': 322, 'isim': 'Mandolin Çalmak', 'klasor': 'Mandolin Çalmak'},
    {'id': 323, 'isim': 'Manga Okumak', 'klasor': 'Manga Okumak'},
    {'id': 324, 'isim': 'Mangal Yapmak (Barbekü)', 'klasor': 'Mangal Yapmak (Barbekü)'},
    {'id': 325, 'isim': 'Mantar Avcılığı', 'klasor': 'Mantar Avcılığı'},
    {'id': 326, 'isim': 'Mantar Bilimi (İnceleme)', 'klasor': 'Mantar Bilimi (İnceleme)'},
    {'id': 327, 'isim': 'Marangozluk', 'klasor': 'Marangozluk'},
    {'id': 328, 'isim': 'Masa Tenisi', 'klasor': 'Masa Tenisi'},
    {'id': 329, 'isim': 'Masaj Yaptırmak', 'klasor': 'Masaj Yaptırmak'},
    {'id': 330, 'isim': 'Matematik Problemi Çözmek', 'klasor': 'Matematik Problemi Çözmek'},
    {'id': 331, 'isim': 'Maç İzlemek', 'klasor': 'Maç İzlemek'},
    {'id': 332, 'isim': 'Meditasyon Yapmak', 'klasor': 'Meditasyon Yapmak'},
    {'id': 333, 'isim': 'Mekanik Klavye Yapımı', 'klasor': 'Mekanik Klavye Yapımı'},
    {'id': 334, 'isim': 'Mektup Arkadaşlığı', 'klasor': 'Mektup Arkadaşlığı'},
    {'id': 335, 'isim': 'Mektup Yazmak', 'klasor': 'Mektup Yazmak'},
    {'id': 336, 'isim': 'Mesajlaşmak', 'klasor': 'Mesajlaşmak'},
    {'id': 337, 'isim': 'Meteoroloji', 'klasor': 'Meteoroloji'},
    {'id': 338, 'isim': 'Mikroskop İncelemesi', 'klasor': 'Mikroskop İncelemesi'},
    {'id': 339, 'isim': 'Mineral Koleksiyonu', 'klasor': 'Mineral Koleksiyonu'},
    {'id': 340, 'isim': 'Mini Golf Oynamak', 'klasor': 'Mini Golf Oynamak'},
    {'id': 341, 'isim': 'Minimalist Yaşam', 'klasor': 'Minimalist Yaşam'},
    {'id': 342, 'isim': 'Minimalizm', 'klasor': 'Minimalizm'},
    {'id': 343, 'isim': 'Minyatür Boyama (Warhammer)', 'klasor': 'Minyatür Boyama (Warhammer)'},
    {'id': 344, 'isim': 'Minyatür Sanatı', 'klasor': 'Minyatür Sanatı'},
    {'id': 345, 'isim': 'Mitoloji Araştırmak', 'klasor': 'Mitoloji Araştırmak'},
    {'id': 346, 'isim': 'Mobil Oyun Oynamak', 'klasor': 'Mobil Oyun Oynamak'},
    {'id': 347, 'isim': 'Mobil Uygulama Geliştirme', 'klasor': 'Mobil Uygulama Geliştirme'},
    {'id': 348, 'isim': 'Moda Bloggerlığı', 'klasor': 'Moda Bloggerlığı'},
    {'id': 349, 'isim': 'Model Araba Koleksiyonu (Diecast)', 'klasor': 'Model Araba Koleksiyonu (Diecast)'},
    {'id': 350, 'isim': 'Model Roketçilik', 'klasor': 'Model Roketçilik'},
    {'id': 351, 'isim': 'Model Uçak Uçurma', 'klasor': 'Model Uçak Uçurma'},
    {'id': 352, 'isim': 'Monopoly Oynamak', 'klasor': 'Monopoly Oynamak'},
    {'id': 353, 'isim': 'Mors Alfabesi Öğrenme', 'klasor': 'Mors Alfabesi Öğrenme'},
    {'id': 354, 'isim': 'Motokros', 'klasor': 'Motokros'},
    {'id': 355, 'isim': 'Motosiklet', 'klasor': 'Motosiklet'},
    {'id': 356, 'isim': 'Mozaik Sanatı', 'klasor': 'Mozaik Sanatı'},
    {'id': 357, 'isim': 'Muay Thai', 'klasor': 'Muay Thai'},
    {'id': 358, 'isim': 'Mum Yapımı', 'klasor': 'Mum Yapımı'},
    {'id': 359, 'isim': 'Mücevher Tasarımı', 'klasor': 'Mücevher Tasarımı'},
    {'id': 360, 'isim': 'Mühür Mumu Basmak', 'klasor': 'Mühür Mumu Basmak'},
    {'id': 361, 'isim': 'Münazara', 'klasor': 'Münazara'},
    {'id': 362, 'isim': 'Müze Gezmek', 'klasor': 'Müze Gezmek'},
    {'id': 363, 'isim': 'Müzik Dinlemek', 'klasor': 'Müzik Dinlemek'},
    {'id': 364, 'isim': 'Müzik Prodüksiyonu', 'klasor': 'Müzik Prodüksiyonu'},
    {'id': 365, 'isim': 'Mısır Patlatmak', 'klasor': 'Mısır Patlatmak'},
    {'id': 366, 'isim': 'Mızıka Çalmak', 'klasor': 'Mızıka Çalmak'},
    {'id': 367, 'isim': 'Nakış İşleme', 'klasor': 'Nakış İşleme'},
    {'id': 368, 'isim': 'Nefes Egzersizleri', 'klasor': 'Nefes Egzersizleri'},
    {'id': 369, 'isim': 'Off-Road', 'klasor': 'Off-Road'},
    {'id': 370, 'isim': 'Okçuluk', 'klasor': 'Okçuluk'},
    {'id': 371, 'isim': 'Olumlama Yapmak', 'klasor': 'Olumlama Yapmak'},
    {'id': 372, 'isim': 'Opera Söylemek', 'klasor': 'Opera Söylemek'},
    {'id': 373, 'isim': 'Origami', 'klasor': 'Origami'},
    {'id': 374, 'isim': 'Orkestra Şefliği', 'klasor': 'Orkestra Şefliği'},
    {'id': 375, 'isim': 'Orkide Yetiştiriciliği', 'klasor': 'Orkide Yetiştiriciliği'},
    {'id': 376, 'isim': 'Otostop Çekmek', 'klasor': 'Otostop Çekmek'},
    {'id': 377, 'isim': 'Oyun Geliştirme', 'klasor': 'Oyun Geliştirme'},
    {'id': 378, 'isim': 'Oyun Oynamak', 'klasor': 'Oyun Oynamak'},
    {'id': 379, 'isim': 'Oyuncak Koleksiyonu', 'klasor': 'Oyuncak Koleksiyonu'},
    {'id': 380, 'isim': 'Oyuncak Yapımı', 'klasor': 'Oyuncak Yapımı'},
    {'id': 381, 'isim': 'Oyunculuk', 'klasor': 'Oyunculuk'},
    {'id': 382, 'isim': 'Paintball', 'klasor': 'Paintball'},
    {'id': 383, 'isim': 'Palyaçoluk', 'klasor': 'Palyaçoluk'},
    {'id': 384, 'isim': 'Pan Flüt Çalmak', 'klasor': 'Pan Flüt Çalmak'},
    {'id': 385, 'isim': 'Para Koleksiyonu', 'klasor': 'Para Koleksiyonu'},
    {'id': 386, 'isim': 'Paraşütle Atlama', 'klasor': 'Paraşütle Atlama'},
    {'id': 387, 'isim': 'Parfüm Yapımı', 'klasor': 'Parfüm Yapımı'},
    {'id': 388, 'isim': 'Parkta Oturmak', 'klasor': 'Parkta Oturmak'},
    {'id': 389, 'isim': 'Parkur', 'klasor': 'Parkur'},
    {'id': 390, 'isim': 'Parmak Güreşi', 'klasor': 'Parmak Güreşi'},
    {'id': 391, 'isim': 'Partide Dans Etmek', 'klasor': 'Partide Dans Etmek'},
    {'id': 392, 'isim': 'Paten', 'klasor': 'Paten'},
    {'id': 393, 'isim': 'Patika Koşusu', 'klasor': 'Patika Koşusu'},
    {'id': 394, 'isim': 'Pazar Kahvaltısı (Brunch)', 'klasor': 'Pazar Kahvaltısı (Brunch)'},
    {'id': 395, 'isim': 'Peruk Yapımı', 'klasor': 'Peruk Yapımı'},
    {'id': 396, 'isim': 'Peynir Yapımı', 'klasor': 'Peynir Yapımı'},
    {'id': 397, 'isim': 'Pilates', 'klasor': 'Pilates'},
    {'id': 398, 'isim': 'Pinball (Tilt)', 'klasor': 'Pinball (Tilt)'},
    {'id': 399, 'isim': 'Pipo İçmek', 'klasor': 'Pipo İçmek'},
    {'id': 400, 'isim': 'Piyano Çalmak', 'klasor': 'Piyano Çalmak'},
    {'id': 401, 'isim': 'Pizza Yapımı', 'klasor': 'Pizza Yapımı'},
    {'id': 402, 'isim': 'Pizza Yemek', 'klasor': 'Pizza Yemek'},
    {'id': 403, 'isim': 'Plak Dinlemek', 'klasor': 'Plak Dinlemek'},
    {'id': 404, 'isim': 'Plak Koleksiyonu', 'klasor': 'Plak Koleksiyonu'},
    {'id': 405, 'isim': 'Plak Miksleme (Scratch)', 'klasor': 'Plak Miksleme (Scratch)'},
    {'id': 406, 'isim': 'Planör Uçuşu', 'klasor': 'Planör Uçuşu'},
    {'id': 407, 'isim': 'Plastik Makyaj (SFX)', 'klasor': 'Plastik Makyaj (SFX)'},
    {'id': 408, 'isim': 'Podcast Dinlemek', 'klasor': 'Podcast Dinlemek'},
    {'id': 409, 'isim': 'Podcast Hazırlamak', 'klasor': 'Podcast Hazırlamak'},
    {'id': 410, 'isim': 'Poker', 'klasor': 'Poker'},
    {'id': 411, 'isim': 'Psikoloji Öğrenmek', 'klasor': 'Psikoloji Öğrenmek'},
    {'id': 412, 'isim': 'Pul Koleksiyonu', 'klasor': 'Pul Koleksiyonu'},
    {'id': 413, 'isim': 'Puro Kültürü', 'klasor': 'Puro Kültürü'},
    {'id': 414, 'isim': 'Puzzle (Yapboz) Yapmak', 'klasor': 'Puzzle (Yapboz) Yapmak'},
    {'id': 415, 'isim': 'Radyo Dinlemek', 'klasor': 'Radyo Dinlemek'},
    {'id': 416, 'isim': 'Rafting', 'klasor': 'Rafting'},
    {'id': 417, 'isim': 'Ragbi', 'klasor': 'Ragbi'},
    {'id': 418, 'isim': 'Ralli', 'klasor': 'Ralli'},
    {'id': 419, 'isim': 'Rap Atışması', 'klasor': 'Rap Atışması'},
    {'id': 420, 'isim': 'Resim Yapmak', 'klasor': 'Resim Yapmak'},
    {'id': 421, 'isim': 'Reçel Yapımı', 'klasor': 'Reçel Yapımı'},
    {'id': 422, 'isim': 'Reçine Sanatı (Epoksi)', 'klasor': 'Reçine Sanatı (Epoksi)'},
    {'id': 423, 'isim': 'Robot Yapımı', 'klasor': 'Robot Yapımı'},
    {'id': 424, 'isim': 'Robotik', 'klasor': 'Robotik'},
    {'id': 425, 'isim': 'Rozet Koleksiyonu', 'klasor': 'Rozet Koleksiyonu'},
    {'id': 426, 'isim': 'Rubik Küpü Çözmek', 'klasor': 'Rubik Küpü Çözmek'},
    {'id': 427, 'isim': 'Rüzgar Sörfü', 'klasor': 'Rüzgar Sörfü'},
    {'id': 428, 'isim': 'Saat Koleksiyonu', 'klasor': 'Saat Koleksiyonu'},
    {'id': 429, 'isim': 'Saat Tamiri', 'klasor': 'Saat Tamiri'},
    {'id': 430, 'isim': 'Sabun Oyma', 'klasor': 'Sabun Oyma'},
    {'id': 431, 'isim': 'Sabun Yapımı', 'klasor': 'Sabun Yapımı'},
    {'id': 432, 'isim': 'Saklambaç Oynamak', 'klasor': 'Saklambaç Oynamak'},
    {'id': 433, 'isim': 'Saksafon Çalmak', 'klasor': 'Saksafon Çalmak'},
    {'id': 434, 'isim': 'Salıncakta Sallanmak', 'klasor': 'Salıncakta Sallanmak'},
    {'id': 435, 'isim': 'Sanal Gerçeklik (VR)', 'klasor': 'Sanal Gerçeklik (VR)'},
    {'id': 436, 'isim': 'Sanat Galerisi Gezmek', 'klasor': 'Sanat Galerisi Gezmek'},
    {'id': 437, 'isim': 'Saraçlık (Deri Eyer Yapımı)', 'klasor': 'Saraçlık (Deri Eyer Yapımı)'},
    {'id': 438, 'isim': 'Satranç', 'klasor': 'Satranç'},
    {'id': 439, 'isim': 'Saunaya Girmek', 'klasor': 'Saunaya Girmek'},
    {'id': 440, 'isim': 'Saç Örgüsü', 'klasor': 'Saç Örgüsü'},
    {'id': 441, 'isim': 'Saç Şekillendirmek', 'klasor': 'Saç Şekillendirmek'},
    {'id': 442, 'isim': 'Scrabble', 'klasor': 'Scrabble'},
    {'id': 443, 'isim': 'Selfie Çekmek', 'klasor': 'Selfie Çekmek'},
    {'id': 444, 'isim': 'Senaryo Yazarlığı', 'klasor': 'Senaryo Yazarlığı'},
    {'id': 445, 'isim': 'Senkronize Yüzme', 'klasor': 'Senkronize Yüzme'},
    {'id': 446, 'isim': 'Sepet Örmeciliği', 'klasor': 'Sepet Örmeciliği'},
    {'id': 447, 'isim': 'Serbest Dalış (Tüpsüz)', 'klasor': 'Serbest Dalış (Tüpsüz)'},
    {'id': 448, 'isim': 'Serbest Düşüş', 'klasor': 'Serbest Düşüş'},
    {'id': 449, 'isim': 'Serbest Koşu (Parkur)', 'klasor': 'Serbest Koşu (Parkur)'},
    {'id': 450, 'isim': 'Ses Tasarımı', 'klasor': 'Ses Tasarımı'},
    {'id': 451, 'isim': 'Sesli Kitap Dinleme', 'klasor': 'Sesli Kitap Dinleme'},
    {'id': 452, 'isim': 'Seyahat', 'klasor': 'Seyahat'},
    {'id': 453, 'isim': 'Siber Güvenlik', 'klasor': 'Siber Güvenlik'},
    {'id': 454, 'isim': 'Sihirbazlık', 'klasor': 'Sihirbazlık'},
    {'id': 455, 'isim': 'Simülasyon Yarışçılığı', 'klasor': 'Simülasyon Yarışçılığı'},
    {'id': 456, 'isim': 'Sinemaya Gitmek', 'klasor': 'Sinemaya Gitmek'},
    {'id': 457, 'isim': 'Sitar Çalmak', 'klasor': 'Sitar Çalmak'},
    {'id': 458, 'isim': 'Snooker', 'klasor': 'Snooker'},
    {'id': 459, 'isim': 'Snowboard', 'klasor': 'Snowboard'},
    {'id': 460, 'isim': 'Sokak Müzisyenliği', 'klasor': 'Sokak Müzisyenliği'},
    {'id': 461, 'isim': 'Sosyal Medyada Takılmak', 'klasor': 'Sosyal Medyada Takılmak'},
    {'id': 462, 'isim': "Spa'ya Gitmek", 'klasor': "Spa'ya Gitmek"},
    {'id': 463, 'isim': 'Spor Ayakkabı Koleksiyonu', 'klasor': 'Spor Ayakkabı Koleksiyonu'},
    {'id': 464, 'isim': 'Squash', 'klasor': 'Squash'},
    {'id': 465, 'isim': 'Stand-up', 'klasor': 'Stand-up'},
    {'id': 466, 'isim': 'Stop Motion Animasyon', 'klasor': 'Stop Motion Animasyon'},
    {'id': 467, 'isim': 'Suda Taş Sektirmek', 'klasor': 'Suda Taş Sektirmek'},
    {'id': 468, 'isim': 'Sukulent Yetiştirme', 'klasor': 'Sukulent Yetiştirme'},
    {'id': 469, 'isim': 'Sumo Güreşi', 'klasor': 'Sumo Güreşi'},
    {'id': 470, 'isim': 'Sutopu', 'klasor': 'Sutopu'},
    {'id': 471, 'isim': 'Synthesizer Kullanımı', 'klasor': 'Synthesizer Kullanımı'},
    {'id': 472, 'isim': 'Sörf', 'klasor': 'Sörf'},
    {'id': 473, 'isim': 'Sözlü Şiir (Beat Poetry)', 'klasor': 'Sözlü Şiir (Beat Poetry)'},
    {'id': 474, 'isim': 'Sürüngen Besleme', 'klasor': 'Sürüngen Besleme'},
    {'id': 475, 'isim': 'Sıcak Hava Balonu', 'klasor': 'Sıcak Hava Balonu'},
    {'id': 476, 'isim': 'Sıfır Atık Yaşamı', 'klasor': 'Sıfır Atık Yaşamı'},
    {'id': 477, 'isim': 'Sığ Su Sörfü (Skimboard)', 'klasor': 'Sığ Su Sörfü (Skimboard)'},
    {'id': 478, 'isim': 'Tahta Bacakla Yürüme', 'klasor': 'Tahta Bacakla Yürüme'},
    {'id': 479, 'isim': 'Tai Chi', 'klasor': 'Tai Chi'},
    {'id': 480, 'isim': 'Tango', 'klasor': 'Tango'},
    {'id': 481, 'isim': 'Tarantula Beslemek', 'klasor': 'Tarantula Beslemek'},
    {'id': 482, 'isim': 'Tarih Araştırmaları', 'klasor': 'Tarih Araştırmaları'},
    {'id': 483, 'isim': 'Tarihi Canlandırma', 'klasor': 'Tarihi Canlandırma'},
    {'id': 484, 'isim': 'Tarot Falı Bakmak', 'klasor': 'Tarot Falı Bakmak'},
    {'id': 485, 'isim': 'Tatil Planı Yapmak', 'klasor': 'Tatil Planı Yapmak'},
    {'id': 486, 'isim': 'Tavla', 'klasor': 'Tavla'},
    {'id': 487, 'isim': 'Taze Makarna Yapımı', 'klasor': 'Taze Makarna Yapımı'},
    {'id': 488, 'isim': 'Taş Boyama', 'klasor': 'Taş Boyama'},
    {'id': 489, 'isim': 'Taş Oyma Sanatı', 'klasor': 'Taş Oyma Sanatı'},
    {'id': 490, 'isim': 'Tek Tekerlekli Bisiklet', 'klasor': 'Tek Tekerlekli Bisiklet'},
    {'id': 491, 'isim': 'Tekvando', 'klasor': 'Tekvando'},
    {'id': 492, 'isim': 'Teleskop Yapımı', 'klasor': 'Teleskop Yapımı'},
    {'id': 493, 'isim': 'Temizlik Yapmak', 'klasor': 'Temizlik Yapmak'},
    {'id': 494, 'isim': 'Tenis', 'klasor': 'Tenis'},
    {'id': 495, 'isim': 'Teraryum Yapımı', 'klasor': 'Teraryum Yapımı'},
    {'id': 496, 'isim': 'Terk Edilmiş Yerleri Keşfetme', 'klasor': 'Terk Edilmiş Yerleri Keşfetme'},
    {'id': 497, 'isim': 'Tezhip Sanatı', 'klasor': 'Tezhip Sanatı'},
    {'id': 498, 'isim': 'TikTok İzlemek', 'klasor': 'TikTok İzlemek'},
    {'id': 499, 'isim': 'Tiny House (Minik Ev) Yaşamı', 'klasor': 'Tiny House (Minik Ev) Yaşamı'},
    {'id': 500, 'isim': 'Tiyatroya Gitmek', 'klasor': 'Tiyatroya Gitmek'},
    {'id': 501, 'isim': 'Tombala', 'klasor': 'Tombala'},
    {'id': 502, 'isim': 'Topluluk Önünde Konuşma', 'klasor': 'Topluluk Önünde Konuşma'},
    {'id': 503, 'isim': 'Topraksız Tarım', 'klasor': 'Topraksız Tarım'},
    {'id': 504, 'isim': 'Trambolin', 'klasor': 'Trambolin'},
    {'id': 505, 'isim': 'Transandantal Meditasyon', 'klasor': 'Transandantal Meditasyon'},
    {'id': 506, 'isim': 'Tren Gözlemciliği', 'klasor': 'Tren Gözlemciliği'},
    {'id': 507, 'isim': 'Triatlon', 'klasor': 'Triatlon'},
    {'id': 508, 'isim': 'Trompet Çalmak', 'klasor': 'Trompet Çalmak'},
    {'id': 509, 'isim': 'Turistik Gezi', 'klasor': 'Turistik Gezi'},
    {'id': 510, 'isim': 'Tüplü Dalış', 'klasor': 'Tüplü Dalış'},
    {'id': 511, 'isim': 'Tırmanış', 'klasor': 'Tırmanış'},
    {'id': 512, 'isim': 'Tırnak Süsleme Sanatı', 'klasor': 'Tırnak Süsleme Sanatı'},
    {'id': 513, 'isim': 'Ud Çalmak', 'klasor': 'Ud Çalmak'},
    {'id': 514, 'isim': 'Ukulele Çalmak', 'klasor': 'Ukulele Çalmak'},
    {'id': 515, 'isim': 'Ultimate Frizbi', 'klasor': 'Ultimate Frizbi'},
    {'id': 516, 'isim': 'Uno Oynamak', 'klasor': 'Uno Oynamak'},
    {'id': 517, 'isim': 'Uykuyu Almak (Geç Uyanmak)', 'klasor': 'Uykuyu Almak (Geç Uyanmak)'},
    {'id': 518, 'isim': 'Uyumak', 'klasor': 'Uyumak'},
    {'id': 519, 'isim': 'Uzaktan Kumandalı Araba', 'klasor': 'Uzaktan Kumandalı Araba'},
    {'id': 520, 'isim': 'Uzun Yolculuğa Çıkmak', 'klasor': 'Uzun Yolculuğa Çıkmak'},
    {'id': 521, 'isim': 'Uçak Gözlemciliği', 'klasor': 'Uçak Gözlemciliği'},
    {'id': 522, 'isim': 'Uçurtma Sörfü', 'klasor': 'Uçurtma Sörfü'},
    {'id': 523, 'isim': 'Uçurtma Uçurmak', 'klasor': 'Uçurtma Uçurmak'},
    {'id': 524, 'isim': 'VHS Kaset Koleksiyonu', 'klasor': 'VHS Kaset Koleksiyonu'},
    {'id': 525, 'isim': 'Vegan Yaşam Tarzı', 'klasor': 'Vegan Yaşam Tarzı'},
    {'id': 526, 'isim': 'Vegan Yemek Yapımı', 'klasor': 'Vegan Yemek Yapımı'},
    {'id': 527, 'isim': 'Vektör Çizim', 'klasor': 'Vektör Çizim'},
    {'id': 528, 'isim': 'Video Kurgu', 'klasor': 'Video Kurgu'},
    {'id': 529, 'isim': 'Vitray', 'klasor': 'Vitray'},
    {'id': 530, 'isim': 'Vitrin Gezmek', 'klasor': 'Vitrin Gezmek'},
    {'id': 531, 'isim': 'Vlog Çekmek', 'klasor': 'Vlog Çekmek'},
    {'id': 532, 'isim': 'Walkman Dinlemek', 'klasor': 'Walkman Dinlemek'},
    {'id': 533, 'isim': 'Wikipedia Editörlüğü', 'klasor': 'Wikipedia Editörlüğü'},
    {'id': 534, 'isim': "Wikipedia'da Gezinmek", 'klasor': "Wikipedia'da Gezinmek"},
    {'id': 535, 'isim': 'Yakalamaca Oynamak (Top)', 'klasor': 'Yakalamaca Oynamak (Top)'},
    {'id': 536, 'isim': 'Yamaç Paraşütü', 'klasor': 'Yamaç Paraşütü'},
    {'id': 537, 'isim': 'Yapay Zeka Görsel Tasarımı', 'klasor': 'Yapay Zeka Görsel Tasarımı'},
    {'id': 538, 'isim': 'Yapboz Yapmak', 'klasor': 'Yapboz Yapmak'},
    {'id': 539, 'isim': 'Yazarlık', 'klasor': 'Yazarlık'},
    {'id': 540, 'isim': 'Yazılım', 'klasor': 'Yazılım'},
    {'id': 541, 'isim': 'Yelkencilik', 'klasor': 'Yelkencilik'},
    {'id': 542, 'isim': 'Yemek Stilistliği', 'klasor': 'Yemek Stilistliği'},
    {'id': 543, 'isim': 'Yemek Yapmak', 'klasor': 'Yemek Yapmak'},
    {'id': 544, 'isim': 'Yeni İnsanlarla Tanışmak', 'klasor': 'Yeni İnsanlarla Tanışmak'},
    {'id': 545, 'isim': 'Yo-Yo', 'klasor': 'Yo-Yo'},
    {'id': 546, 'isim': 'Yodel Söylemek', 'klasor': 'Yodel Söylemek'},
    {'id': 547, 'isim': 'Yoga', 'klasor': 'Yoga'},
    {'id': 548, 'isim': 'Yoğurt Mayalamak', 'klasor': 'Yoğurt Mayalamak'},
    {'id': 549, 'isim': 'Yumurta Kabuğu Oyma', 'klasor': 'Yumurta Kabuğu Oyma'},
    {'id': 550, 'isim': 'Yün Eğirme', 'klasor': 'Yün Eğirme'},
    {'id': 551, 'isim': 'Yürüyüş Yapmak', 'klasor': 'Yürüyüş Yapmak'},
    {'id': 552, 'isim': 'Yüzme', 'klasor': 'Yüzme'},
    {'id': 553, 'isim': 'Yılan Beslemek', 'klasor': 'Yılan Beslemek'},
    {'id': 554, 'isim': 'Yıldızları İzlemek', 'klasor': 'Yıldızları İzlemek'},
    {'id': 555, 'isim': 'Zihin Haritası Yapmak', 'klasor': 'Zihin Haritası Yapmak'},
    {'id': 556, 'isim': 'Zorbing (Yuvarlanma Topu)', 'klasor': 'Zorbing (Yuvarlanma Topu)'},
    {'id': 557, 'isim': 'Çakmak Koleksiyonu', 'klasor': 'Çakmak Koleksiyonu'},
    {'id': 558, 'isim': 'Çamaşır Yıkamak', 'klasor': 'Çamaşır Yıkamak'},
    {'id': 559, 'isim': 'Çay Harmanlama', 'klasor': 'Çay Harmanlama'},
    {'id': 560, 'isim': 'Çay Seremonisi', 'klasor': 'Çay Seremonisi'},
    {'id': 561, 'isim': 'Çay İçmek', 'klasor': 'Çay İçmek'},
    {'id': 562, 'isim': 'Çekilişlere Katılmak', 'klasor': 'Çekilişlere Katılmak'},
    {'id': 563, 'isim': 'Çello Çalmak', 'klasor': 'Çello Çalmak'},
    {'id': 564, 'isim': 'Çikolata Yemek', 'klasor': 'Çikolata Yemek'},
    {'id': 565, 'isim': 'Çim Bakımı', 'klasor': 'Çim Bakımı'},
    {'id': 566, 'isim': 'Çini Sanatı', 'klasor': 'Çini Sanatı'},
    {'id': 567, 'isim': 'Çizgi Film İzlemek', 'klasor': 'Çizgi Film İzlemek'},
    {'id': 568, 'isim': 'Çizgi Roman Koleksiyonu', 'klasor': 'Çizgi Roman Koleksiyonu'},
    {'id': 569, 'isim': 'Çizgi Roman Okumak', 'klasor': 'Çizgi Roman Okumak'},
    {'id': 570, 'isim': 'Çizim', 'klasor': 'Çizim'},
    {'id': 571, 'isim': 'Çiçek Düzenleme (İkebana)', 'klasor': 'Çiçek Düzenleme (İkebana)'},
    {'id': 572, 'isim': 'Çiçek Kurutma', 'klasor': 'Çiçek Kurutma'},
    {'id': 573, 'isim': 'Çiçek Presleme', 'klasor': 'Çiçek Presleme'},
    {'id': 574, 'isim': 'Çiçek Sulamak', 'klasor': 'Çiçek Sulamak'},
    {'id': 575, 'isim': 'Çömlekçilik', 'klasor': 'Çömlekçilik'},
    {'id': 576, 'isim': 'Ördek Beslemek', 'klasor': 'Ördek Beslemek'},
    {'id': 577, 'isim': 'Örgü Örmek', 'klasor': 'Örgü Örmek'},
    {'id': 578, 'isim': 'Ütü Yapmak', 'klasor': 'Ütü Yapmak'},
    {'id': 579, 'isim': 'İleri Dönüşüm (Eşya Yenileme)', 'klasor': 'İleri Dönüşüm (Eşya Yenileme)'},
    {'id': 580, 'isim': 'İnsanları İzlemek', 'klasor': 'İnsanları İzlemek'},
    {'id': 581, 'isim': 'İnternet Alışverişi', 'klasor': 'İnternet Alışverişi'},
    {'id': 582, 'isim': 'İnternette Gezinmek', 'klasor': 'İnternette Gezinmek'},
    {'id': 583, 'isim': 'İp Atlamak', 'klasor': 'İp Atlamak'},
    {'id': 584, 'isim': 'İp Cambazlığı', 'klasor': 'İp Cambazlığı'},
    {'id': 585, 'isim': 'İp Üzerinde Yürüme (Slackline)', 'klasor': 'İp Üzerinde Yürüme (Slackline)'},
    {'id': 586, 'isim': 'İşaret Dili Öğrenmek', 'klasor': 'İşaret Dili Öğrenmek'},
    {'id': 587, 'isim': 'Şahincilik (Yırtıcı Kuş Eğitimi)', 'klasor': 'Şahincilik (Yırtıcı Kuş Eğitimi)'},
    {'id': 588, 'isim': 'Şapka Koleksiyonu', 'klasor': 'Şapka Koleksiyonu'},
    {'id': 589, 'isim': 'Şarap Eşleştirme', 'klasor': 'Şarap Eşleştirme'},
    {'id': 590, 'isim': 'Şarap Tadımı', 'klasor': 'Şarap Tadımı'},
    {'id': 591, 'isim': 'Şarap Uzmanlığı', 'klasor': 'Şarap Uzmanlığı'},
    {'id': 592, 'isim': 'Şarap İçmek', 'klasor': 'Şarap İçmek'},
    {'id': 593, 'isim': 'Şarkı Söylemek', 'klasor': 'Şarkı Söylemek'},
    {'id': 594, 'isim': 'Şarkı Sözü Yazarlığı', 'klasor': 'Şarkı Sözü Yazarlığı'},
    {'id': 595, 'isim': 'Şehir Bahçeciliği', 'klasor': 'Şehir Bahçeciliği'},
    {'id': 596, 'isim': 'Şiir Ezberlemek', 'klasor': 'Şiir Ezberlemek'},
    {'id': 597, 'isim': 'Şiir Yazmak', 'klasor': 'Şiir Yazmak'},
    {'id': 598, 'isim': 'Şişe Koleksiyonu', 'klasor': 'Şişe Koleksiyonu'},
    {'id': 599, 'isim': 'Şişe İçinde Kum Sanatı', 'klasor': 'Şişe İçinde Kum Sanatı'},
    {'id': 600, 'isim': 'Şnorkelle Dalış', 'klasor': 'Şnorkelle Dalış'}
]

fobiler = [
    {'id': 1, 'isim': 'Akrofobi', 'aciklama': 'Yükseklik korkusu', 'resim': 'Akrofobi'},
    {'id': 2, 'isim': 'Aerofobi', 'aciklama': 'Uçuş veya uçak korkusu', 'resim': 'Aerofobi'},
    {'id': 3, 'isim': 'Agorafobi', 'aciklama': 'Açık alan veya kalabalık korkusu', 'resim': 'Agorafobi'},      
    {'id': 4, 'isim': 'Ailurofobi', 'aciklama': 'Kedi korkusu', 'resim': 'Ailurofobi'},
    {'id': 5, 'isim': 'Alektorofobi', 'aciklama': 'Tavuk korkusu', 'resim': 'Alektorofobi'},
    {'id': 6, 'isim': 'Amaksofobi', 'aciklama': 'Taşıt veya araçta olma korkusu', 'resim': 'Amaksofobi'},      
    {'id': 7, 'isim': 'Androfobi', 'aciklama': 'Erkeklerden korkma durumu', 'resim': 'Androfobi'},
    {'id': 8, 'isim': 'Antofobi', 'aciklama': 'Çiçek korkusu', 'resim': 'Antofobi'},
    {'id': 9, 'isim': 'Antropofobi', 'aciklama': 'İnsanlardan veya toplumdan korkma', 'resim': 'Antropofobi'}, 
    {'id': 10, 'isim': 'Akuafobi', 'aciklama': 'Su korkusu', 'resim': 'Akuafobi'},
    {'id': 11, 'isim': 'Araknofobi', 'aciklama': 'Örümcek korkusu', 'resim': 'Araknofobi'},
    {'id': 12, 'isim': 'Aritmofobi', 'aciklama': 'Sayı veya matematik korkusu', 'resim': 'Aritmofobi'},        
    {'id': 13, 'isim': 'Astrafobi', 'aciklama': 'Şimşek ve gök gürültüsü korkusu', 'resim': 'Astrafobi'},      
    {'id': 14, 'isim': 'Ataksofobi', 'aciklama': 'Düzensizlik veya dağınıklık korkusu', 'resim': 'Ataksofobi'},
    {'id': 15, 'isim': 'Atelofobi', 'aciklama': 'Yetersizlik veya kusurlu olma korkusu', 'resim': 'Atelofobi'},
    {'id': 16, 'isim': 'Atikifobi', 'aciklama': 'Başarısızlık korkusu', 'resim': 'Atikifobi'},
    {'id': 17, 'isim': 'Otofobi', 'aciklama': 'Yalnız kalma korkusu', 'resim': 'Otofobi'},
    {'id': 18, 'isim': 'Bakteriyofobi', 'aciklama': 'Bakteri veya mikrop korkusu', 'resim': 'Bakteriyofobi'},
    {'id': 19, 'isim': 'Barofobi', 'aciklama': 'Yerçekimi korkusu', 'resim': 'Barofobi'},
    {'id': 20, 'isim': 'Batmofobi', 'aciklama': 'Merdiven veya dik yokuş korkusu', 'resim': 'Batmofobi'},
    {'id': 21, 'isim': 'Batrakofobi', 'aciklama': 'Kurbağa ve amfibiyan korkusu', 'resim': 'Batrakofobi'},
    {'id': 22, 'isim': 'Bibliyofobi', 'aciklama': 'Kitap korkusu', 'resim': 'Bibliyofobi'},
    {'id': 23, 'isim': 'Botanofobi', 'aciklama': 'Bitki korkusu', 'resim': 'Botanofobi'},
    {'id': 24, 'isim': 'Kakofobi', 'aciklama': 'Çirkinlik veya çirkin şeylerden korkma', 'resim': 'Kakofobi'},
    {'id': 25, 'isim': 'Katoptrofobi', 'aciklama': 'Ayna korkusu', 'resim': 'Katoptrofobi'},
    {'id': 26, 'isim': 'Kiyonofobi', 'aciklama': 'Kar korkusu', 'resim': 'Kiyonofobi'},
    {'id': 27, 'isim': 'Kromofobi', 'aciklama': 'Renk korkusu', 'resim': 'Kromofobi'},
    {'id': 28, 'isim': 'Kronofobi', 'aciklama': 'Zamanın ilerlemesi veya zaman korkusu', 'resim': 'Kronofobi'},
    {'id': 29, 'isim': 'Klostrofobi', 'aciklama': 'Kapalı alan korkusu', 'resim': 'Klostrofobi'},
    {'id': 30, 'isim': 'Koulrofobi', 'aciklama': 'Palyaço korkusu', 'resim': 'Koulrofobi'},
    {'id': 31, 'isim': 'Siberfobi', 'aciklama': 'Bilgisayar veya teknoloji korkusu', 'resim': 'Siberfobi'},
    {'id': 32, 'isim': 'Sinofobi', 'aciklama': 'Köpek korkusu', 'resim': 'Sinofobi'},
    {'id': 33, 'isim': 'Demonofobi', 'aciklama': 'Şeytan veya kötü ruh korkusu', 'resim': 'Demonofobi'},
    {'id': 34, 'isim': 'Dendrofobi', 'aciklama': 'Ağaç korkusu', 'resim': 'Dendrofobi'},
    {'id': 35, 'isim': 'Dentofobi', 'aciklama': 'Dişçi korkusu', 'resim': 'Dentofobi'},
    {'id': 36, 'isim': 'Didaskaleinofobi', 'aciklama': 'Okul korkusu', 'resim': 'Didaskaleinofobi'},
    {'id': 37, 'isim': 'Dipsofobi', 'aciklama': 'İçki içme korkusu', 'resim': 'Dipsofobi'},
    {'id': 38, 'isim': 'Dishabiliyofobi', 'aciklama': 'Birinin önünde soyunma korkusu', 'resim': 'Dishabiliyofobi'},
    {'id': 39, 'isim': 'Domatofobi', 'aciklama': 'Evde bulunma korkusu', 'resim': 'Domatofobi'},
    {'id': 40, 'isim': 'Distikifobi', 'aciklama': 'Kaza yapma korkusu', 'resim': 'Distikifobi'},
    {'id': 41, 'isim': 'Eisoptrofobi', 'aciklama': 'Aynada kendini görme korkusu', 'resim': 'Eisoptrofobi'},
    {'id': 42, 'isim': 'Elektrofobi', 'aciklama': 'Elektrik korkusu', 'resim': 'Elektrofobi'},
    {'id': 43, 'isim': 'Elöterofobi', 'aciklama': 'Özgürlük korkusu', 'resim': 'Elöterofobi'},
    {'id': 44, 'isim': 'Emetofobi', 'aciklama': 'Kusma korkusu', 'resim': 'Emetofobi'},
    {'id': 45, 'isim': 'Enoklofobi', 'aciklama': 'Kalabalık korkusu', 'resim': 'Enoklofobi'},
    {'id': 46, 'isim': 'Entomofobi', 'aciklama': 'Böcek korkusu', 'resim': 'Entomofobi'},
    {'id': 47, 'isim': 'Ekinofobi', 'aciklama': 'At korkusu', 'resim': 'Ekinofobi'},
    {'id': 48, 'isim': 'Ergofobi', 'aciklama': 'İş veya çalışma korkusu', 'resim': 'Ergofobi'},
    {'id': 49, 'isim': 'Erotofobi', 'aciklama': 'Cinsellik korkusu', 'resim': 'Erotofobi'},
    {'id': 50, 'isim': 'Gametofobi', 'aciklama': 'Evlilik korkusu', 'resim': 'Gametofobi'},
    {'id': 51, 'isim': 'Genofobi', 'aciklama': 'Cinsel ilişki korkusu', 'resim': 'Genofobi'},
    {'id': 52, 'isim': 'Geraskofobi', 'aciklama': 'Yaşlanma korkusu', 'resim': 'Geraskofobi'},
    {'id': 53, 'isim': 'Globofobi', 'aciklama': 'Balon korkusu', 'resim': 'Globofobi'},
    {'id': 54, 'isim': 'Glossofobi', 'aciklama': 'Topluluk önünde konuşma korkusu', 'resim': 'Glossofobi'},
    {'id': 55, 'isim': 'Jinofobi', 'aciklama': 'Kadınlardan korkma', 'resim': 'Jinofobi'},
    {'id': 56, 'isim': 'Hadefobi', 'aciklama': 'Cehennem korkusu', 'resim': 'Hadefobi'},
    {'id': 57, 'isim': 'Hagiofobi', 'aciklama': 'Azizler veya kutsal şeylerden korkma', 'resim': 'Hagiofobi'},
    {'id': 58, 'isim': 'Hedonofobi', 'aciklama': 'Zevk alma korkusu', 'resim': 'Hedonofobi'},
    {'id': 59, 'isim': 'Helyofobi', 'aciklama': 'Güneş korkusu', 'resim': 'Helyofobi'},
    {'id': 60, 'isim': 'Hemofobi', 'aciklama': 'Kan korkusu', 'resim': 'Hemofobi'},
    {'id': 61, 'isim': 'Herpetofobi', 'aciklama': 'Sürüngen korkusu', 'resim': 'Herpetofobi'},
    {'id': 62, 'isim': 'Hipopotomonstrosesquipedalyofobi', 'aciklama': 'Uzun kelime korkusu', 'resim': 'Hipopotomonstrosesquipedalyofobi'},
    {'id': 63, 'isim': 'Hodofobi', 'aciklama': 'Seyahat etme korkusu', 'resim': 'Hodofobi'},
    {'id': 64, 'isim': 'Homofobi', 'aciklama': 'Eşcinsellik korkusu veya nefreti', 'resim': 'Homofobi'},
    {'id': 65, 'isim': 'Hilofobi', 'aciklama': 'Orman korkusu', 'resim': 'Hilofobi'},
    {'id': 66, 'isim': 'Hipnofobi', 'aciklama': 'Uyku korkusu', 'resim': 'Hipnofobi'},
    {'id': 67, 'isim': 'Yatrofobi', 'aciklama': 'Doktor korkusu', 'resim': 'Yatrofobi'},
    {'id': 68, 'isim': 'İhtiyofobi', 'aciklama': 'Balık korkusu', 'resim': 'İhtiyofobi'},
    {'id': 69, 'isim': 'Katsaridafobi', 'aciklama': 'Hamamböceği korkusu', 'resim': 'Katsaridafobi'},
    {'id': 70, 'isim': 'Kenofobi', 'aciklama': 'Boş alan veya boşluk korkusu', 'resim': 'Kenofobi'},
    {'id': 71, 'isim': 'Kinetofobi', 'aciklama': 'Hareket korkusu', 'resim': 'Kinetofobi'},
    {'id': 72, 'isim': 'Koinonifobi', 'aciklama': 'Oda korkusu', 'resim': 'Koinonifobi'},
    {'id': 73, 'isim': 'Lakanofobi', 'aciklama': 'Sebze korkusu', 'resim': 'Lakanofobi'},
    {'id': 74, 'isim': 'Lökofobi', 'aciklama': 'Beyaz renk korkusu', 'resim': 'Lökofobi'},
    {'id': 75, 'isim': 'Lilapsofobi', 'aciklama': 'Kasırga veya fırtına korkusu', 'resim': 'Lilapsofobi'},
    {'id': 76, 'isim': 'Logofobi', 'aciklama': 'Kelime korkusu', 'resim': 'Logofobi'},
    {'id': 77, 'isim': 'Mageirokofobi', 'aciklama': 'Yemek pişirme korkusu', 'resim': 'Mageirokofobi'},
    {'id': 78, 'isim': 'Mayosiyofobi', 'aciklama': 'Hamilelik korkusu', 'resim': 'Mayosiyofobi'},
    {'id': 79, 'isim': 'Megalofobi', 'aciklama': 'Büyük nesnelerden korkma', 'resim': 'Megalofobi'},
    {'id': 80, 'isim': 'Melanofobi', 'aciklama': 'Siyah renk korkusu', 'resim': 'Melanofobi'},
    {'id': 81, 'isim': 'Melofobi', 'aciklama': 'Müzik korkusu', 'resim': 'Melofobi'},
    {'id': 82, 'isim': 'Menofobi', 'aciklama': 'Adet görme korkusu', 'resim': 'Menofobi'},
    {'id': 83, 'isim': 'Merintofobi', 'aciklama': 'Bağlanma veya iple bağlanma korkusu', 'resim': 'Merintofobi'},
    {'id': 84, 'isim': 'Metallofobi', 'aciklama': 'Metal korkusu', 'resim': 'Metallofobi'},
    {'id': 85, 'isim': 'Meteorofobi', 'aciklama': 'Meteor korkusu', 'resim': 'Meteorofobi'},
    {'id': 86, 'isim': 'Metifobi', 'aciklama': 'Alkol korkusu', 'resim': 'Metifobi'},
    {'id': 87, 'isim': 'Mikrofobi', 'aciklama': 'Küçük şeyler veya mikroplar korkusu', 'resim': 'Mikrofobi'},
    {'id': 88, 'isim': 'Monofobi', 'aciklama': 'Yalnızlık korkusu', 'resim': 'Monofobi'},
    {'id': 89, 'isim': 'Musofobi', 'aciklama': 'Fare korkusu', 'resim': 'Musofobi'},
    {'id': 90, 'isim': 'Mikofobi', 'aciklama': 'Mantar korkusu', 'resim': 'Mikofobi'},
    {'id': 91, 'isim': 'Mirmekofobi', 'aciklama': 'Karınca korkusu', 'resim': 'Mirmekofobi'},
    {'id': 92, 'isim': 'Misofobi', 'aciklama': 'Mikrop veya kirlenme korkusu', 'resim': 'Misofobi'},
    {'id': 93, 'isim': 'Nekrofobi', 'aciklama': 'Ölüm veya ceset korkusu', 'resim': 'Nekrofobi'},
    {'id': 94, 'isim': 'Neofobi', 'aciklama': 'Yenilik korkusu', 'resim': 'Neofobi'},
    {'id': 95, 'isim': 'Noktifobi', 'aciklama': 'Gece korkusu', 'resim': 'Noktifobi'},
    {'id': 96, 'isim': 'Nomofobi', 'aciklama': 'Telefonsuz kalma korkusu', 'resim': 'Nomofobi'},
    {'id': 97, 'isim': 'Nozofobi', 'aciklama': 'Hastalık kapma korkusu', 'resim': 'Nozofobi'},
    {'id': 98, 'isim': 'Numerofobi', 'aciklama': 'Sayı korkusu', 'resim': 'Numerofobi'},
    {'id': 99, 'isim': 'Obezofobi', 'aciklama': 'Şişmanlama korkusu', 'resim': 'Obezofobi'},
    {'id': 100, 'isim': 'Okofobi', 'aciklama': 'Taşıt korkusu', 'resim': 'Okofobi'},
    {'id': 101, 'isim': 'Odontofobi', 'aciklama': 'Diş tedavisi korkusu', 'resim': 'Odontofobi'},
    {'id': 102, 'isim': 'Önofobi', 'aciklama': 'Şarap korkusu', 'resim': 'Önofobi'},
    {'id': 103, 'isim': 'Ombrofobi', 'aciklama': 'Yağmur korkusu', 'resim': 'Ombrofobi'},
    {'id': 104, 'isim': 'Ommetofobi', 'aciklama': 'Göz korkusu', 'resim': 'Ommetofobi'},
    {'id': 105, 'isim': 'Onirofobi', 'aciklama': 'Rüya görme korkusu', 'resim': 'Onirofobi'},
    {'id': 106, 'isim': 'Ofidiyofobi', 'aciklama': 'Yılan korkusu', 'resim': 'Ofidiyofobi'},
    {'id': 107, 'isim': 'Oftalmofobi', 'aciklama': 'Biri tarafından izlenme korkusu', 'resim': 'Oftalmofobi'},
    {'id': 108, 'isim': 'Ornitofobi', 'aciklama': 'Kuş korkusu', 'resim': 'Ornitofobi'},
    {'id': 109, 'isim': 'Ostrakonofobi', 'aciklama': 'Kabuklu deniz hayvanı korkusu', 'resim': 'Ostrakonofobi'},
    {'id': 110, 'isim': 'Pagofobi', 'aciklama': 'Buz veya don korkusu', 'resim': 'Pagofobi'},
    {'id': 111, 'isim': 'Papirofobi', 'aciklama': 'Kağıt korkusu', 'resim': 'Papirofobi'},
    {'id': 112, 'isim': 'Parazitofobi', 'aciklama': 'Parazit korkusu', 'resim': 'Parazitofobi'},
    {'id': 113, 'isim': 'Patofobi', 'aciklama': 'Hastalık korkusu', 'resim': 'Patofobi'},
    {'id': 114, 'isim': 'Pekkatofobi', 'aciklama': 'Günah işleme korkusu', 'resim': 'Pekkatofobi'},
    {'id': 115, 'isim': 'Pedofobi', 'aciklama': 'Çocuk korkusu', 'resim': 'Pedofobi'},
    {'id': 116, 'isim': 'Penyofobi', 'aciklama': 'Fakirleşme korkusu', 'resim': 'Penyofobi'},
    {'id': 117, 'isim': 'Farmakofobi', 'aciklama': 'İlaç alma korkusu', 'resim': 'Farmakofobi'},
    {'id': 118, 'isim': 'Fazmofobi', 'aciklama': 'Hayalet korkusu', 'resim': 'Fazmofobi'},
    {'id': 119, 'isim': 'Fengofobi', 'aciklama': 'Gün ışığı korkusu', 'resim': 'Fengofobi'},
    {'id': 120, 'isim': 'Filemafobi', 'aciklama': 'Öpüşme korkusu', 'resim': 'Filemafobi'},
    {'id': 121, 'isim': 'Filofobi', 'aciklama': 'Aşık olma korkusu', 'resim': 'Filofobi'},
    {'id': 122, 'isim': 'Fonofobi', 'aciklama': 'Yüksek ses korkusu', 'resim': 'Fonofobi'},
    {'id': 123, 'isim': 'Fotoaugliyafobi', 'aciklama': 'Parlak ışık korkusu', 'resim': 'Fotoaugliyafobi'},
    {'id': 124, 'isim': 'Fotofobi', 'aciklama': 'Işık korkusu', 'resim': 'Fotofobi'},
    {'id': 125, 'isim': 'Fronemofobi', 'aciklama': 'Düşünme korkusu', 'resim': 'Fronemofobi'},
    {'id': 126, 'isim': 'Pnomatifobi', 'aciklama': 'Ruh korkusu', 'resim': 'Pnomatifobi'},
    {'id': 127, 'isim': 'Pogonofobi', 'aciklama': 'Sakal korkusu', 'resim': 'Pogonofobi'},
    {'id': 128, 'isim': 'Polifobi', 'aciklama': 'Birçok şeyden korkma', 'resim': 'Polifobi'},
    {'id': 129, 'isim': 'Poinefobi', 'aciklama': 'Ceza korkusu', 'resim': 'Poinefobi'},
    {'id': 130, 'isim': 'Ponofobi', 'aciklama': 'Aşırı çalışma veya acı korkusu', 'resim': 'Ponofobi'},
    {'id': 131, 'isim': 'Porfirofobi', 'aciklama': 'Mor renk korkusu', 'resim': 'Porfirofobi'},
    {'id': 132, 'isim': 'Potamofobi', 'aciklama': 'Nehir veya akarsu korkusu', 'resim': 'Potamofobi'},
    {'id': 133, 'isim': 'Prosofobi', 'aciklama': 'İlerleme korkusu', 'resim': 'Prosofobi'},
    {'id': 134, 'isim': 'Psikofobi', 'aciklama': 'Zihin korkusu', 'resim': 'Psikofobi'},
    {'id': 135, 'isim': 'Psikrofobi', 'aciklama': 'Soğuk korkusu', 'resim': 'Psikrofobi'},
    {'id': 136, 'isim': 'Pteromerhanofobi', 'aciklama': 'Uçma korkusu', 'resim': 'Pteromerhanofobi'},
    {'id': 137, 'isim': 'Pteronofobi', 'aciklama': 'Tüy ile gıdıklanma korkusu', 'resim': 'Pteronofobi'},
    {'id': 138, 'isim': 'Pupafobi', 'aciklama': 'Kukla korkusu', 'resim': 'Pupafobi'},
    {'id': 139, 'isim': 'Pirofobi', 'aciklama': 'Ateş korkusu', 'resim': 'Pirofobi'},
    {'id': 140, 'isim': 'Radyofobi', 'aciklama': 'Radyasyon veya röntgen korkusu', 'resim': 'Radyofobi'},
    {'id': 141, 'isim': 'Ranidafobi', 'aciklama': 'Kurbağa korkusu', 'resim': 'Ranidafobi'},
    {'id': 142, 'isim': 'Samhainofobi', 'aciklama': 'Cadılar Bayramı korkusu', 'resim': 'Samhainofobi'},
    {'id': 143, 'isim': 'Sarmassofobi', 'aciklama': 'Aşk oyunları korkusu', 'resim': 'Sarmassofobi'},
    {'id': 144, 'isim': 'Satanofobi', 'aciklama': 'Şeytan korkusu', 'resim': 'Satanofobi'},
    {'id': 145, 'isim': 'Skabiyofobi', 'aciklama': 'Uyuz hastalığı korkusu', 'resim': 'Skabiyofobi'},
    {'id': 146, 'isim': 'Skatofobi', 'aciklama': 'Dışkı korkusu', 'resim': 'Skatofobi'},
    {'id': 147, 'isim': 'Siyofobi', 'aciklama': 'Gölge korkusu', 'resim': 'Siyofobi'},
    {'id': 148, 'isim': 'Skolesifobi', 'aciklama': 'Solucan korkusu', 'resim': 'Skolesifobi'},
    {'id': 149, 'isim': 'Selakofobi', 'aciklama': 'Köpekbalığı korkusu', 'resim': 'Selakofobi'},
    {'id': 150, 'isim': 'Siderodromofobi', 'aciklama': 'Tren korkusu', 'resim': 'Siderodromofobi'},
    {'id': 151, 'isim': 'Siderofobi', 'aciklama': 'Yıldız korkusu', 'resim': 'Siderofobi'},
    {'id': 152, 'isim': 'Sitofobi', 'aciklama': 'Yemek yeme korkusu', 'resim': 'Sitofobi'},
    {'id': 153, 'isim': 'Sosyal Fobi', 'aciklama': 'Sosyal ortamlarda bulunma korkusu', 'resim': 'Sosyal Fobi'},
    {'id': 154, 'isim': 'Sosyofobi', 'aciklama': 'Toplum korkusu', 'resim': 'Sosyofobi'},
    {'id': 155, 'isim': 'Sofofobi', 'aciklama': 'Öğrenme korkusu', 'resim': 'Sofofobi'},
    {'id': 156, 'isim': 'Uzay Fobisi', 'aciklama': 'Uzay korkusu', 'resim': 'Uzay Fobisi'},
    {'id': 157, 'isim': 'Spektrofobi', 'aciklama': 'Ayna veya hayalet korkusu', 'resim': 'Spektrofobi'},
    {'id': 158, 'isim': 'Sfeksofobi', 'aciklama': 'Eşek arısı korkusu', 'resim': 'Sfeksofobi'},
    {'id': 159, 'isim': 'Stenofobi', 'aciklama': 'Dar alan veya yol korkusu', 'resim': 'Stenofobi'},
    {'id': 160, 'isim': 'Sembolofobi', 'aciklama': 'Sembol korkusu', 'resim': 'Sembolofobi'},
    {'id': 161, 'isim': 'Simetrofobi', 'aciklama': 'Simetri korkusu', 'resim': 'Simetrofobi'},
    {'id': 162, 'isim': 'Singenesofobi', 'aciklama': 'Akraba korkusu', 'resim': 'Singenesofobi'},
    {'id': 163, 'isim': 'Takofobi', 'aciklama': 'Hız korkusu', 'resim': 'Takofobi'},
    {'id': 164, 'isim': 'Tenyofobi', 'aciklama': 'Tenya korkusu', 'resim': 'Tenyofobi'},
    {'id': 165, 'isim': 'Törofobi', 'aciklama': 'Boğa korkusu', 'resim': 'Törofobi'},
    {'id': 166, 'isim': 'Teknofobi', 'aciklama': 'Teknoloji korkusu', 'resim': 'Teknofobi'},
    {'id': 167, 'isim': 'Telefonofobi', 'aciklama': 'Telefonla konuşma korkusu', 'resim': 'Telefonofobi'},
    {'id': 168, 'isim': 'Testofobi', 'aciklama': 'Sınav korkusu', 'resim': 'Testofobi'},
    {'id': 169, 'isim': 'Taasofobi', 'aciklama': 'Oturma korkusu', 'resim': 'Taasofobi'},
    {'id': 170, 'isim': 'Talasofobi', 'aciklama': 'Derin deniz veya okyanus korkusu', 'resim': 'Talasofobi'},
    {'id': 171, 'isim': 'Teatrofobi', 'aciklama': 'Tiyatro korkusu', 'resim': 'Teatrofobi'},
    {'id': 172, 'isim': 'Teofobi', 'aciklama': 'Tanrı veya din korkusu', 'resim': 'Teofobi'},
    {'id': 173, 'isim': 'Termofobi', 'aciklama': 'Isı veya sıcak korkusu', 'resim': 'Termofobi'},
    {'id': 174, 'isim': 'Tomofobi', 'aciklama': 'Ameliyat korkusu', 'resim': 'Tomofobi'},
    {'id': 175, 'isim': 'Tonitrofobi', 'aciklama': 'Gök gürültüsü korkusu', 'resim': 'Tonitrofobi'},
    {'id': 176, 'isim': 'Topofobi', 'aciklama': 'Belirli bir yer korkusu', 'resim': 'Topofobi'},
    {'id': 177, 'isim': 'Toksikofobi', 'aciklama': 'Zehirlenme korkusu', 'resim': 'Toksikofobi'},
    {'id': 178, 'isim': 'Travmatofobi', 'aciklama': 'Yaralanma korkusu', 'resim': 'Travmatofobi'},
    {'id': 179, 'isim': 'Trikofobi', 'aciklama': 'Saç veya tüy korkusu', 'resim': 'Trikofobi'},
    {'id': 180, 'isim': 'Tropofobi', 'aciklama': 'Hareket etme veya değişiklik korkusu', 'resim': 'Tropofobi'},
    {'id': 181, 'isim': 'Tripanofobi', 'aciklama': 'İğne veya aşı olma korkusu', 'resim': 'Tripanofobi'},
    {'id': 182, 'isim': 'Tripofobi', 'aciklama': 'Delikli yüzeyler korkusu', 'resim': 'Tripofobi'},
    {'id': 183, 'isim': 'Uranofobi', 'aciklama': 'Cennet korkusu', 'resim': 'Uranofobi'},
    {'id': 184, 'isim': 'Urofobi', 'aciklama': 'İdrar yapma veya idrar korkusu', 'resim': 'Urofobi'},
    {'id': 185, 'isim': 'Venustrafobi', 'aciklama': 'Güzel kadınlardan korkma', 'resim': 'Venustrafobi'},
    {'id': 186, 'isim': 'Verminofobi', 'aciklama': 'Mikrop korkusu', 'resim': 'Verminofobi'},
    {'id': 187, 'isim': 'Vitrikofobi', 'aciklama': 'Üvey baba korkusu', 'resim': 'Vitrikofobi'},
    {'id': 188, 'isim': 'Vikka Fobisi', 'aciklama': 'Cadı korkusu', 'resim': 'Vikka Fobisi'},
    {'id': 189, 'isim': 'Ksantofobi', 'aciklama': 'Sarı renk korkusu', 'resim': 'Ksantofobi'},
    {'id': 190, 'isim': 'Zenofobi', 'aciklama': 'Yabancı korkusu veya nefreti', 'resim': 'Zenofobi'},
    {'id': 191, 'isim': 'Ksilofobi', 'aciklama': 'Tahta veya orman korkusu', 'resim': 'Ksilofobi'},
    {'id': 192, 'isim': 'Zeusofobi', 'aciklama': 'Tanrı veya yüce güç korkusu', 'resim': 'Zeusofobi'},
    {'id': 193, 'isim': 'Zoofobi', 'aciklama': 'Hayvan korkusu', 'resim': 'Zoofobi'},
    {'id': 194, 'isim': 'Agrizoofobi', 'aciklama': 'Vahşi hayvan korkusu', 'resim': 'Agrizoofobi'},
    {'id': 195, 'isim': 'Aikmofobi', 'aciklama': 'Sivri uçlu nesne korkusu', 'resim': 'Aikmofobi'},
    {'id': 196, 'isim': 'Alliyumfobi', 'aciklama': 'Sarımsak korkusu', 'resim': 'Alliyumfobi'},
    {'id': 197, 'isim': 'Allodoksafobi', 'aciklama': 'Fikir veya görüş korkusu', 'resim': 'Allodoksafobi'},
    {'id': 198, 'isim': 'Ambulofobi', 'aciklama': 'Yürüme korkusu', 'resim': 'Ambulofobi'},
    {'id': 199, 'isim': 'Amnezifobi', 'aciklama': 'Hafıza kaybı korkusu', 'resim': 'Amnezifobi'},
    {'id': 200, 'isim': 'Amikofobi', 'aciklama': 'Tırmalanma korkusu', 'resim': 'Amikofobi'},
    {'id': 201, 'isim': 'Anablefobi', 'aciklama': 'Yukarı bakma korkusu', 'resim': 'Anablefobi'},
    {'id': 202, 'isim': 'Ankraofobi', 'aciklama': 'Rüzgar korkusu', 'resim': 'Ankraofobi'},
    {'id': 203, 'isim': 'Ankilofobi', 'aciklama': 'Eklem hareketsizliği korkusu', 'resim': 'Ankilofobi'},
    {'id': 204, 'isim': 'Apeyrofobi', 'aciklama': 'Sonsuzluk korkusu', 'resim': 'Apeyrofobi'},
    {'id': 205, 'isim': 'Apifobi', 'aciklama': 'Arı korkusu', 'resim': 'Apifobi'},
    {'id': 206, 'isim': 'Apotemnofobi', 'aciklama': 'Uzuv kesilme korkusu', 'resim': 'Apotemnofobi'},
    {'id': 207, 'isim': 'Arakibutyrofobi', 'aciklama': 'Fıstık ezmesinin damağa yapışma korkusu', 'resim': 'Arakibutyrofobi'},
    {'id': 208, 'isim': 'Arsonfobi', 'aciklama': 'Yangın korkusu', 'resim': 'Arsonfobi'},
    {'id': 209, 'isim': 'Astrofobi', 'aciklama': 'Yıldız veya uzay korkusu', 'resim': 'Astrofobi'},
    {'id': 210, 'isim': 'Asimetrifobi', 'aciklama': 'Simetrik olmayan şeylerden korkma', 'resim': 'Asimetrifobi'},
    {'id': 211, 'isim': 'Atomozofobi', 'aciklama': 'Atom patlaması korkusu', 'resim': 'Atomozofobi'},
    {'id': 212, 'isim': 'Olofobi', 'aciklama': 'Flüt korkusu', 'resim': 'Olofobi'},
    {'id': 213, 'isim': 'Orofobi', 'aciklama': 'Altın korkusu', 'resim': 'Orofobi'},
    {'id': 214, 'isim': 'Otomatonofobi', 'aciklama': 'Vantrolog kuklası veya balmumu heykel korkusu', 'resim': 'Otomatonofobi'},
    {'id': 215, 'isim': 'Otomizofobi', 'aciklama': 'Kirlenme korkusu', 'resim': 'Otomizofobi'},
    {'id': 216, 'isim': 'Kaliginefobi', 'aciklama': 'Güzel kadın korkusu', 'resim': 'Kaliginefobi'},
    {'id': 217, 'isim': 'Kardiyofobi', 'aciklama': 'Kalp hastalığı korkusu', 'resim': 'Kardiyofobi'},
    {'id': 218, 'isim': 'Karnofobi', 'aciklama': 'Et korkusu', 'resim': 'Karnofobi'},
    {'id': 219, 'isim': 'Ketofobi', 'aciklama': 'Saç korkusu', 'resim': 'Ketofobi'},
    {'id': 220, 'isim': 'Kemofobi', 'aciklama': 'Kimyasal madde korkusu', 'resim': 'Kemofobi'},
    {'id': 221, 'isim': 'Kerofobi', 'aciklama': 'Mutluluk korkusu', 'resim': 'Kerofobi'},
    {'id': 222, 'isim': 'Kirofobi', 'aciklama': 'El korkusu', 'resim': 'Kirofobi'},
    {'id': 223, 'isim': 'Kolerofobi', 'aciklama': 'Kolera korkusu', 'resim': 'Kolerofobi'},
    {'id': 224, 'isim': 'Korofobi', 'aciklama': 'Dans etme korkusu', 'resim': 'Korofobi'},
    {'id': 225, 'isim': 'Sibofobi', 'aciklama': 'Yemek korkusu', 'resim': 'Sibofobi'},
    {'id': 226, 'isim': 'Kleitrofobi', 'aciklama': 'Kapalı yerde kilitli kalma korkusu', 'resim': 'Kleitrofobi'},
    {'id': 227, 'isim': 'Klitrofobi', 'aciklama': 'Kapatılma korkusu', 'resim': 'Klitrofobi'},
    {'id': 228, 'isim': 'Koimetrofobi', 'aciklama': 'Mezarlık korkusu', 'resim': 'Koimetrofobi'},
    {'id': 229, 'isim': 'Kometofobi', 'aciklama': 'Kuyruklu yıldız korkusu', 'resim': 'Kometofobi'},
    {'id': 230, 'isim': 'Koprastasofobi', 'aciklama': 'Kabızlık korkusu', 'resim': 'Koprastasofobi'},
    {'id': 231, 'isim': 'Kriyofobi', 'aciklama': 'Aşırı soğuk korkusu', 'resim': 'Kriyofobi'},
    {'id': 232, 'isim': 'Kristallofobi', 'aciklama': 'Kristal veya cam korkusu', 'resim': 'Kristallofobi'},
    {'id': 233, 'isim': 'Siklofobi', 'aciklama': 'Bisiklet korkusu', 'resim': 'Siklofobi'},
    {'id': 234, 'isim': 'Kimofobi', 'aciklama': 'Dalga korkusu', 'resim': 'Kimofobi'},
    {'id': 235, 'isim': 'Desidofobi', 'aciklama': 'Karar verme korkusu', 'resim': 'Desidofobi'},
    {'id': 236, 'isim': 'Dermatofobi', 'aciklama': 'Deri hastalığı korkusu', 'resim': 'Dermatofobi'},
    {'id': 237, 'isim': 'Dekstrofobi', 'aciklama': 'Sağ taraf korkusu', 'resim': 'Dekstrofobi'},
    {'id': 238, 'isim': 'Diyabetofobi', 'aciklama': 'Diyabet korkusu', 'resim': 'Diyabetofobi'},
    {'id': 239, 'isim': 'Dinofobi', 'aciklama': 'Baş dönmesi korkusu', 'resim': 'Dinofobi'},
    {'id': 240, 'isim': 'Diplofobi', 'aciklama': 'Çift görme korkusu', 'resim': 'Diplofobi'},
    {'id': 241, 'isim': 'Dorafobi', 'aciklama': 'Hayvan kürkü korkusu', 'resim': 'Dorafobi'},
    {'id': 242, 'isim': 'Doksofobi', 'aciklama': 'Fikir belirtme korkusu', 'resim': 'Doksofobi'},
    {'id': 243, 'isim': 'Dromofobi', 'aciklama': 'Karşıdan karşıya geçme korkusu', 'resim': 'Dromofobi'},
    {'id': 244, 'isim': 'Ekleziyofobi', 'aciklama': 'Kilise korkusu', 'resim': 'Ekleziyofobi'},
    {'id': 245, 'isim': 'Enetofobi', 'aciklama': 'İğne korkusu', 'resim': 'Enetofobi'},
    {'id': 246, 'isim': 'Epistemofobi', 'aciklama': 'Bilgi korkusu', 'resim': 'Epistemofobi'},
    {'id': 247, 'isim': 'Ergasiyofobi', 'aciklama': 'Çalışma korkusu', 'resim': 'Ergasiyofobi'},
    {'id': 248, 'isim': 'Öfobi', 'aciklama': 'İyi haber duyma korkusu', 'resim': 'Öfobi'},
    {'id': 249, 'isim': 'Frankofobi', 'aciklama': 'Fransız korkusu', 'resim': 'Frankofobi'},
    {'id': 250, 'isim': 'Galeofobi', 'aciklama': 'Köpekbalığı veya kedi korkusu', 'resim': 'Galeofobi'},
    {'id': 251, 'isim': 'Geniyofobi', 'aciklama': 'Çene korkusu', 'resim': 'Geniyofobi'},
    {'id': 252, 'isim': 'Jenufobi', 'aciklama': 'Diz korkusu', 'resim': 'Jenufobi'},
    {'id': 253, 'isim': 'Gefirofobi', 'aciklama': 'Köprüden geçme korkusu', 'resim': 'Gefirofobi'},
    {'id': 254, 'isim': 'Gerontofobi', 'aciklama': 'Yaşlı insan korkusu', 'resim': 'Gerontofobi'},
    {'id': 255, 'isim': 'Gömofobi', 'aciklama': 'Tat alma korkusu', 'resim': 'Gömofobi'},
    {'id': 256, 'isim': 'Grafofobi', 'aciklama': 'Yazı yazma korkusu', 'resim': 'Grafofobi'},
    {'id': 257, 'isim': 'Hellenologofobi', 'aciklama': 'Karmaşık bilimsel terim korkusu', 'resim': 'Hellenologofobi'},
    {'id': 258, 'isim': 'Herezifobi', 'aciklama': 'Sapkın fikir korkusu', 'resim': 'Herezifobi'},
    {'id': 259, 'isim': 'Heksakosioiheksekontaheksafobi', 'aciklama': '666 sayısı korkusu', 'resim': 'Heksakosioiheksekontaheksafobi'},
    {'id': 260, 'isim': 'Hiyerofobi', 'aciklama': 'Rahip veya kutsal eşya korkusu', 'resim': 'Hiyerofobi'},
    {'id': 261, 'isim': 'Homiklofobi', 'aciklama': 'Sis korkusu', 'resim': 'Homiklofobi'},
    {'id': 262, 'isim': 'Homilofobi', 'aciklama': 'Vaaz korkusu', 'resim': 'Homilofobi'},
    {'id': 263, 'isim': 'Hidrarjirofobi', 'aciklama': 'Cıva korkusu', 'resim': 'Hidrarjirofobi'},
    {'id': 264, 'isim': 'Hidrofobi', 'aciklama': 'Su veya kuduz korkusu', 'resim': 'Hidrofobi'},
    {'id': 265, 'isim': 'Hiyelofobi', 'aciklama': 'Cam korkusu', 'resim': 'Hiyelofobi'},
    {'id': 266, 'isim': 'Hipokondria', 'aciklama': 'Hastalık hastası olma korkusu', 'resim': 'Hipokondria'},
    {'id': 267, 'isim': 'İdeofobi', 'aciklama': 'Fikir korkusu', 'resim': 'İdeofobi'},
    {'id': 268, 'isim': 'İllingofobi', 'aciklama': 'Aşağı bakma baş dönmesi korkusu', 'resim': 'İllingofobi'},
    {'id': 269, 'isim': 'İyofobi', 'aciklama': 'Zehir korkusu', 'resim': 'İyofobi'},
    {'id': 270, 'isim': 'İzopterofobi', 'aciklama': 'Termit veya böcek korkusu', 'resim': 'İzopterofobi'},
    {'id': 271, 'isim': 'İtifallofobi', 'aciklama': 'Ereksiyon korkusu', 'resim': 'İtifallofobi'},
    {'id': 272, 'isim': 'Japanofobi', 'aciklama': 'Japon korkusu', 'resim': 'Japanofobi'},
    {'id': 273, 'isim': 'Judeofobi', 'aciklama': 'Yahudi korkusu', 'resim': 'Judeofobi'},
    {'id': 274, 'isim': 'Keraunofobi', 'aciklama': 'Şimşek korkusu', 'resim': 'Keraunofobi'},
    {'id': 275, 'isim': 'Kopofobi', 'aciklama': 'Yorgunluk korkusu', 'resim': 'Kopofobi'},
    {'id': 276, 'isim': 'Kosmikofobi', 'aciklama': 'Kozmik olay korkusu', 'resim': 'Kosmikofobi'},
    {'id': 277, 'isim': 'Laliyofobi', 'aciklama': 'Konuşma korkusu', 'resim': 'Laliyofobi'},
    {'id': 278, 'isim': 'Leprofobi', 'aciklama': 'Cüzzam korkusu', 'resim': 'Leprofobi'},
    {'id': 279, 'isim': 'Limnofobi', 'aciklama': 'Göl korkusu', 'resim': 'Limnofobi'},
    {'id': 280, 'isim': 'Linonofobi', 'aciklama': 'İp korkusu', 'resim': 'Linonofobi'},
    {'id': 281, 'isim': 'Litikafobi', 'aciklama': 'Dava edilme korkusu', 'resim': 'Litikafobi'},
    {'id': 282, 'isim': 'Logizomekanofobi', 'aciklama': 'Bilgisayar korkusu', 'resim': 'Logizomekanofobi'},
    {'id': 283, 'isim': 'Makrofobi', 'aciklama': 'Uzun bekleme korkusu', 'resim': 'Makrofobi'},
    {'id': 284, 'isim': 'Maniyafobi', 'aciklama': 'Delilik korkusu', 'resim': 'Maniyafobi'},
    {'id': 285, 'isim': 'Mastigofobi', 'aciklama': 'Cezalandırılma korkusu', 'resim': 'Mastigofobi'},
    {'id': 286, 'isim': 'Mekanofobi', 'aciklama': 'Makine korkusu', 'resim': 'Mekanofobi'},
    {'id': 287, 'isim': 'Menenjitofobi', 'aciklama': 'Beyin hastalığı korkusu', 'resim': 'Menenjitofobi'},
    {'id': 288, 'isim': 'Molisomofobi', 'aciklama': 'Enfeksiyon korkusu', 'resim': 'Molisomofobi'},
    {'id': 289, 'isim': 'Monopatofobi', 'aciklama': 'Belirli bir hastalık korkusu', 'resim': 'Monopatofobi'},
    {'id': 290, 'isim': 'Mottefobi', 'aciklama': 'Güve korkusu', 'resim': 'Mottefobi'},
    {'id': 291, 'isim': 'Mitofobi', 'aciklama': 'Efsane veya hikaye korkusu', 'resim': 'Mitofobi'},
    {'id': 292, 'isim': 'Nelofobi', 'aciklama': 'Cam kırığı korkusu', 'resim': 'Nelofobi'},
    {'id': 293, 'isim': 'Neofarmafobi', 'aciklama': 'Yeni ilaç korkusu', 'resim': 'Neofarmafobi'},
    {'id': 294, 'isim': 'Nefofobi', 'aciklama': 'Bulut korkusu', 'resim': 'Nefofobi'},
    {'id': 295, 'isim': 'Noverkafobi', 'aciklama': 'Üvey anne korkusu', 'resim': 'Noverkafobi'},
    {'id': 296, 'isim': 'Nukleomitufobi', 'aciklama': 'Nükleer silah korkusu', 'resim': 'Nukleomitufobi'},
    {'id': 297, 'isim': 'Niktohilofobi', 'aciklama': 'Geceleri ormanda olma korkusu', 'resim': 'Niktohilofobi'},
    {'id': 298, 'isim': 'Papafobi', 'aciklama': 'Papa korkusu', 'resim': 'Papafobi'},
    {'id': 299, 'isim': 'Patroyofobi', 'aciklama': 'Kalıtım korkusu', 'resim': 'Patroyofobi'},
    {'id': 300, 'isim': 'Pedyofobi', 'aciklama': 'Oyuncak bebek korkusu', 'resim': 'Pedyofobi'}
]


@uygulama.route('/filmler')
def film_sec():
    if 'kullanici_email' not in session:
        return redirect(url_for('anasayfa'))
    
    return render_template('filmler.html', filmler=filmler)

@uygulama.route('/film-kaydet', methods=['POST'])
def film_kaydet():
    if 'kullanici_email' not in session or 'kullanici_id' not in session:
        return jsonify({'hata': 'Oturum bulunamadı'}), 401
    
    veri = request.get_json()
    secili_film_idler = veri.get('secili_filmler', [])
    
    if len(secili_film_idler) < 1 or len(secili_film_idler) > 10:
        return jsonify({'hata': 'En az 1, en fazla 10 film seçmelisiniz'}), 400
    
    kullanici_id = session['kullanici_id']
    
    film_idleri_str = ','.join(map(str, secili_film_idler))
    
    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor()
        
        try:
            cursor.execute(
                "SELECT kullanici_id FROM kullanici_secimler WHERE kullanici_id = %s",
                (kullanici_id,)
            )
            mevcut = cursor.fetchone() # Kullanıcı daha önceden kayıt olduysa TRUE değilse FALSE döndürecek
            
            if mevcut:
                cursor.execute(
                    "UPDATE kullanici_secimler SET filmler = %s WHERE kullanici_id = %s",
                    (film_idleri_str, kullanici_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO kullanici_secimler (kullanici_id, filmler) VALUES (%s, %s)",
                    (kullanici_id, film_idleri_str)
                )
            
            baglanti.commit()
            print(f"✅ Filmler kaydedildi - Kullanıcı UUID: {kullanici_id}")
            print(f"   Film ID'leri: {film_idleri_str}")
            
        except Error as e:
            print(f"❌ Film kayıt hatası: {e}")
            baglanti.rollback()
        
        finally:
            cursor.close()
            baglanti.close()
    
    return jsonify({'basarili': True, 'yonlendir': '/diziler'})

@uygulama.route('/diziler')
def dizi_sec():
    if 'kullanici_email' not in session:
        return redirect(url_for('anasayfa'))
    
    return render_template('diziler.html', diziler=diziler)

@uygulama.route('/dizi-kaydet', methods=['POST'])
def dizi_kaydet():
    if 'kullanici_email' not in session or 'kullanici_id' not in session:
        return jsonify({'hata': 'Oturum bulunamadı'}), 401
    
    veri = request.get_json()
    secili_dizi_idler = veri.get('secili_diziler', [])
    
    if len(secili_dizi_idler) < 1 or len(secili_dizi_idler) > 10:
        return jsonify({'hata': 'En az 1, en fazla 10 dizi seçmelisiniz'}), 400
    
    kullanici_id = session['kullanici_id']
    dizi_idleri_str = ','.join(map(str, secili_dizi_idler))
    
    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor()
        
        try:
            cursor.execute(
                "SELECT kullanici_id FROM kullanici_secimler WHERE kullanici_id = %s",
                (kullanici_id,)
            )
            mevcut = cursor.fetchone()
            
            if mevcut:
                cursor.execute(
                    "UPDATE kullanici_secimler SET diziler = %s WHERE kullanici_id = %s",
                    (dizi_idleri_str, kullanici_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO kullanici_secimler (kullanici_id, diziler) VALUES (%s, %s)",
                    (kullanici_id, dizi_idleri_str)
                )
            
            baglanti.commit()
            print(f"✅ Diziler kaydedildi - UUID: {kullanici_id}, ID'ler: {dizi_idleri_str}")
            
        except Error as e:
            print(f"❌ Dizi kayıt hatası: {e}")
            baglanti.rollback()
        
        finally:
            cursor.close()
            baglanti.close()
    
    return jsonify({'basarili': True, 'yonlendir': '/sarkilar'})

@uygulama.route('/sarkilar')
def sarki_sec():
    if 'kullanici_email' not in session:
        return redirect(url_for('anasayfa'))
    
    return render_template('sarkilar.html', sarkilar=sarkilar)

@uygulama.route('/sarki-kaydet', methods=['POST'])
def sarki_kaydet():
    if 'kullanici_email' not in session or 'kullanici_id' not in session:
        return jsonify({'hata': 'Oturum bulunamadı'}), 401
    
    veri = request.get_json()
    secili_sarki_idler = veri.get('secili_sarkilar', [])
    
    if len(secili_sarki_idler) < 1 or len(secili_sarki_idler) > 10:
        return jsonify({'hata': 'En az 1, en fazla 10 şarkı seçmelisiniz'}), 400
    
    kullanici_id = session['kullanici_id']
    sarki_idleri_str = ','.join(map(str, secili_sarki_idler))
    
    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor()
        
        try:
            cursor.execute(
                "SELECT kullanici_id FROM kullanici_secimler WHERE kullanici_id = %s",
                (kullanici_id,)
            )
            mevcut = cursor.fetchone()
            
            if mevcut:
                cursor.execute(
                    "UPDATE kullanici_secimler SET sarkilar = %s WHERE kullanici_id = %s",
                    (sarki_idleri_str, kullanici_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO kullanici_secimler (kullanici_id, sarkilar) VALUES (%s, %s)",
                    (kullanici_id, sarki_idleri_str)
                )
            
            baglanti.commit()
            print(f"✅ Şarkılar kaydedildi - UUID: {kullanici_id}, ID'ler: {sarki_idleri_str}")
            
        except Error as e:
            print(f"❌ Şarkı kayıt hatası: {e}")
            baglanti.rollback()
        
        finally:
            cursor.close()
            baglanti.close()
    
    return jsonify({'basarili': True, 'yonlendir': '/kitaplar'})

@uygulama.route('/sarki-cal/<path:klasor>')
def sarki_cal(klasor):
    dosya_yolu = os.path.join('static', 'sarkilar', klasor, 'preview.mp3')
    return send_file(dosya_yolu, mimetype='audio/mpeg') # Audio kullanıcıya gönderilir

@uygulama.route('/kitaplar')
def kitap_sec():
    if 'kullanici_email' not in session:
        return redirect(url_for('anasayfa'))
    
    return render_template('kitaplar.html', kitaplar=kitaplar)

@uygulama.route('/kitap-kaydet', methods=['POST'])
def kitap_kaydet():
    if 'kullanici_email' not in session or 'kullanici_id' not in session:
        return jsonify({'hata': 'Oturum bulunamadı'}), 401
    
    veri = request.get_json()
    secili_kitap_idler = veri.get('secili_kitaplar', [])
    
    if len(secili_kitap_idler) < 1 or len(secili_kitap_idler) > 10:
        return jsonify({'hata': 'En az 1, en fazla 10 kitap seçmelisiniz'}), 400
    
    kullanici_id = session['kullanici_id']
    kitap_idleri_str = ','.join(map(str, secili_kitap_idler))
    
    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor()
        
        try:
            cursor.execute(
                "SELECT kullanici_id FROM kullanici_secimler WHERE kullanici_id = %s",
                (kullanici_id,)
            )
            mevcut = cursor.fetchone()
            
            if mevcut:
                cursor.execute(
                    "UPDATE kullanici_secimler SET kitaplar = %s WHERE kullanici_id = %s",
                    (kitap_idleri_str, kullanici_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO kullanici_secimler (kullanici_id, kitaplar) VALUES (%s, %s)",
                    (kullanici_id, kitap_idleri_str)
                )
            
            baglanti.commit()
            print(f"✅ Kitaplar kaydedildi - UUID: {kullanici_id}, ID'ler: {kitap_idleri_str}")
            
        except Error as e:
            print(f"❌ Kitap kayıt hatası: {e}")
            baglanti.rollback()
        
        finally:
            cursor.close()
            baglanti.close()
    
    return jsonify({'basarili': True, 'yonlendir': '/hobiler'})

@uygulama.route('/hobiler')
def hobi_sec():
    if 'kullanici_email' not in session:
        return redirect(url_for('anasayfa'))
    
    return render_template('hobiler.html', hobiler=hobiler)
@uygulama.route('/hobi-kaydet', methods=['POST'])
def hobi_kaydet():
    if 'kullanici_email' not in session or 'kullanici_id' not in session:
        return jsonify({'hata': 'Oturum bulunamadı'}), 401
    
    veri = request.get_json()
    secili_hobi_idler = veri.get('secili_hobiler', [])
    
    if len(secili_hobi_idler) < 1 or len(secili_hobi_idler) > 10:
        return jsonify({'hata': 'En az 1, en fazla 10 hobi seçmelisiniz'}), 400
    
    kullanici_id = session['kullanici_id']
    hobi_idleri_str = ','.join(map(str, secili_hobi_idler))
    
    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor()
        
        try:
            cursor.execute(
                "SELECT kullanici_id FROM kullanici_secimler WHERE kullanici_id = %s",
                (kullanici_id,)
            )
            mevcut = cursor.fetchone()
            
            if mevcut:
                cursor.execute(
                    "UPDATE kullanici_secimler SET hobiler = %s WHERE kullanici_id = %s",
                    (hobi_idleri_str, kullanici_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO kullanici_secimler (kullanici_id, hobiler) VALUES (%s, %s)",
                    (kullanici_id, hobi_idleri_str)
                )
            
            baglanti.commit()
            print(f"✅ Hobiler kaydedildi - UUID: {kullanici_id}, ID'ler: {hobi_idleri_str}")
        except Error as e:
            print(f"❌ Hobi kayıt hatası: {e}")
            baglanti.rollback()
        
        finally:
            cursor.close()
            baglanti.close()
    
    return jsonify({'basarili': True, 'yonlendir': '/fobiler'})

@uygulama.route('/fobiler')
def fobi_sec():
    if 'kullanici_email' not in session:
        return redirect(url_for('anasayfa'))
    
    return render_template('fobiler.html', fobiler=fobiler)

@uygulama.route('/fobi-kaydet', methods=['POST'])
def fobi_kaydet():
    if 'kullanici_email' not in session or 'kullanici_id' not in session:
        return jsonify({'hata': 'Oturum bulunamadı'}), 401
    
    veri = request.get_json()
    secili_fobi_idler = veri.get('secili_fobiler', [])
    
    if len(secili_fobi_idler) < 1 or len(secili_fobi_idler) > 10:
        return jsonify({'hata': 'En az 1, en fazla 10 fobi seçmelisiniz'}), 400
    
    kullanici_id = session['kullanici_id']
    Fobi_idleri_str = ','.join(map(str, secili_fobi_idler))
    
    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor()
        
        try:
            cursor.execute(
                "SELECT kullanici_id FROM kullanici_secimler WHERE kullanici_id = %s",
                (kullanici_id,)
            )
            mevcut = cursor.fetchone()
            
            if mevcut:
                cursor.execute(
                    "UPDATE kullanici_secimler SET Fobiler = %s WHERE kullanici_id = %s",
                    (Fobi_idleri_str, kullanici_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO kullanici_secimler (kullanici_id, Fobiler) VALUES (%s, %s)",
                    (kullanici_id, Fobi_idleri_str)
                )
            
            baglanti.commit()
            print(f"✅ Fobiler kaydedildi - UUID: {kullanici_id}, ID'ler: {Fobi_idleri_str}")
            
        except Error as e:
            print(f"❌ Fobi kayıt hatası: {e}")
            baglanti.rollback()
        
        finally:
            cursor.close()
            baglanti.close()
    
    return jsonify({'basarili': True, 'yonlendir': '/eslesme'})


def email_gonder(alici_email, dogrulama_kodu):
    """Gerçek email gönderme fonksiyonu"""
    try:
        mesaj = MIMEMultipart()
        mesaj['From'] = GMAIL_ADRES
        mesaj['To'] = alici_email
        mesaj['Subject'] = "Doğrulama Kodunuz - Eşleşme Sistemi"
        
        icerik = f"""
Merhaba,

Eşleşme sistemine hoş geldiniz!

Doğrulama kodunuz: {dogrulama_kodu}

Bu kodu doğrulama sayfasına girerek kaydınızı tamamlayabilirsiniz.

İyi günler!
        """
        
        mesaj.attach(MIMEText(icerik, 'plain', 'utf-8'))
        
        sunucu = smtplib.SMTP('smtp.gmail.com', 587) # 587 Güvenli mail gönderme portu
        sunucu.starttls()
        sunucu.login(GMAIL_ADRES, GMAIL_SIFRE)
        sunucu.send_message(mesaj)
        sunucu.quit()
        
        print(f"✅ Email başarıyla gönderildi: {alici_email}")
        return True
        
    except Exception as hata:
        print(f"❌ Email gönderme hatası: {hata}")
        return False

@uygulama.route('/')
def anasayfa():
    return render_template('kayit.html')


@uygulama.route('/kayit-ol', methods=['POST'])
def kayit_ol():
    ad = request.form.get('ad')
    soyad = request.form.get('soyad')
    email = request.form.get('email')
    dogum_tarihi = request.form.get('dogum_tarihi')
    cinsiyet = request.form.get('cinsiyet')
    bolge = request.form.get('bolge')
    egitim = request.form.get('egitim')
    
    if not all([ad, soyad, email, dogum_tarihi, cinsiyet, bolge, egitim]):
        return redirect(url_for('anasayfa'))

    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor()
        cursor.execute("SELECT id FROM kullanicilar WHERE email = %s", (email,))
        mevcut_kullanici = cursor.fetchone()
        cursor.close()
        baglanti.close()
        
        if mevcut_kullanici:
            return redirect(url_for('anasayfa', hata='email_kayitli'))
    dogum = datetime.strptime(dogum_tarihi, '%Y-%m-%d')
    bugun = datetime.now()
    yas = bugun.year - dogum.year - ((bugun.month, bugun.day) < (dogum.month, dogum.day))
    

    if yas < 18:
        return redirect(url_for('anasayfa', hata='yas'))

    dogrulama_kodu = random.randint(100000, 999999)
    
    dogrulama_kodlari[email] = {
        'kod': dogrulama_kodu,
        'ad': ad,
        'soyad': soyad,
        'dogum_tarihi': dogum_tarihi,
        'yas': yas,
        'cinsiyet': cinsiyet,
        'bolge': bolge,
        'egitim': egitim
    }
    
    email_gonder(email, dogrulama_kodu)
    
    session['dogrulama_email'] = email

    return redirect(url_for('dogrulama_sayfasi'))

@uygulama.route('/dogrulama')
def dogrulama_sayfasi():
    if 'dogrulama_email' not in session:
        return redirect(url_for('anasayfa'))
    
    return render_template('dogrulama.html')

@uygulama.route('/kod-dogrula', methods=['POST'])
def kod_dogrula():
    girilen_kod = request.form.get('kod')
    email = session.get('dogrulama_email')
    
    if not email or email not in dogrulama_kodlari:
        return redirect(url_for('anasayfa'))
    
    dogru_kod = str(dogrulama_kodlari[email]['kod'])
    
    if girilen_kod == dogru_kod:
        session['onay_email'] = email
        return redirect(url_for('sifre_belirle'))
    else:
        return redirect(url_for('dogrulama_sayfasi'))
    
@uygulama.route('/sifre-belirle')
def sifre_belirle():
    if 'onay_email' not in session:
        return redirect(url_for('anasayfa'))
    
    return render_template('sifre.html')

@uygulama.route('/sifre-kaydet', methods=['POST'])
def sifre_kaydet():
    if 'onay_email' not in session:
        return redirect(url_for('anasayfa'))
    
    email = session.get('onay_email')
    sifre = request.form.get('sifre')
    sifre_tekrar = request.form.get('sifre_tekrar')

    if sifre != sifre_tekrar:
        return redirect(url_for('sifre_belirle', hata='eslesmiyor'))
    
    if len(sifre) < 6:
        return redirect(url_for('sifre_belirle', hata='kisa'))
    
    if email not in dogrulama_kodlari:
        print(f"❌ HATA: {email} dogrulama_kodlari içinde bulunamadı!")
        return redirect(url_for('anasayfa'))
    
    kullanici_id = str(uuid.uuid4())
    
    kullanici_bilgileri = dogrulama_kodlari[email]
    
    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor()
        
        try:
            sql = """
            INSERT INTO kullanicilar 
            (id, ad, soyad, email, sifre, dogum_tarihi, yas, cinsiyet, bolge, egitim) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                kullanici_id,
                kullanici_bilgileri['ad'],
                kullanici_bilgileri['soyad'],
                email,
                sifre,
                kullanici_bilgileri['dogum_tarihi'],
                kullanici_bilgileri['yas'],
                kullanici_bilgileri['cinsiyet'],
                kullanici_bilgileri['bolge'],
                kullanici_bilgileri['egitim']
            )
            
            cursor.execute(sql, values)
            baglanti.commit()
            
            print(f"✅ Kullanıcı kaydedildi: {email}")
            print(f"   UUID: {kullanici_id}")
            print(f"   Ad: {kullanici_bilgileri['ad']} {kullanici_bilgileri['soyad']}")
            
        except Error as e:
            print(f"❌ Kayıt hatası: {e}")
            baglanti.rollback()
        
        finally:
            cursor.close()
            baglanti.close()
    
    session.pop('onay_email', None)
    session.pop('dogrulama_email', None)
    del dogrulama_kodlari[email]
    
    return redirect(url_for('giris_sayfasi', basarili='true'))
        
@uygulama.route('/giris')
def giris_sayfasi():
    return render_template('giris.html')

@uygulama.route('/giris-yap', methods=['POST'])
def giris_yap():
    email = request.form.get('email')
    sifre = request.form.get('sifre')
    
    baglanti = veritabani_baglantisi()
    if baglanti:
        cursor = baglanti.cursor(dictionary=True)
        
        try:
            sql = "SELECT id, ad, soyad, email FROM kullanicilar WHERE email = %s AND sifre = %s"
            cursor.execute(sql, (email, sifre))
            kullanici = cursor.fetchone()
            
            if kullanici:
                session['kullanici_email'] = email
                session['kullanici_id'] = kullanici['id']
                
                print(f"✅ Giriş başarılı: {email}")
                print(f"   UUID: {kullanici['id']}")
                
                cursor.close()
                baglanti.close()
                return redirect(url_for('film_sec'))
            else:
                cursor.close()
                baglanti.close()
                return redirect(url_for('giris_sayfasi', hata='yanlis'))
                
        except Error as e:
            print(f"❌ Giriş hatası: {e}")
            cursor.close()
            baglanti.close()
            return redirect(url_for('giris_sayfasi', hata='yanlis'))
    
    return redirect(url_for('giris_sayfasi', hata='yanlis'))

@uygulama.route('/eslesme-hesapla', methods=['POST'])
def eslesme_hesapla_route():
    if 'kullanici_id' not in session:
        return jsonify({'hata': 'Oturum bulunamadı'}), 401
    
    try:
        motor_baslat()
        kullanici_id = session['kullanici_id']

        eslesme_sonuclari = eslesme_hesapla(kullanici_id)
        session['eslesme_sonuclari'] = eslesme_sonuclari
        
        return jsonify({'basarili': True})
        
    except Exception as e:
        print(f"❌ Eşleşme hesaplama hatası: {e}")
        return jsonify({'hata': str(e)}), 500
    
@uygulama.route('/eslesme')
def eslesme_sayfasi():
    if 'kullanici_email' not in session or 'kullanici_id' not in session:
        return redirect(url_for('anasayfa'))
    
    baglanti = veritabani_baglantisi()
    cursor = baglanti.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM kullanici_secimler 
        WHERE (filmler IS NOT NULL OR filmler != '')
           OR (diziler IS NOT NULL OR diziler != '')
           OR (sarkilar IS NOT NULL OR sarkilar != '')
           OR (kitaplar IS NOT NULL OR kitaplar != '')
           OR (hobiler IS NOT NULL OR hobiler != '')
           OR (Fobiler IS NOT NULL OR Fobiler != '')
    """) # Bu kısım en az bir seçim yapmış kullanıcıların sayılması için önemlidir
    kullanici_sayisi = cursor.fetchone()[0]
    cursor.close()
    baglanti.close()
    
    if kullanici_sayisi < 2:
        return redirect(url_for('sonuc_sayfasi'))
    
    return render_template('eslesme.html')


@uygulama.route('/sonuc')
def sonuc_sayfasi():
    if 'kullanici_email' not in session or 'kullanici_id' not in session:
        return redirect(url_for('anasayfa'))
    
    kullanici_id = session['kullanici_id']
    
    eslesme_sonuclari = session.get('eslesme_sonuclari', None)

    if eslesme_sonuclari is None:

        baglanti = veritabani_baglantisi()
        cursor = baglanti.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM kullanici_secimler 
            WHERE (filmler IS NOT NULL OR filmler != '')
               OR (diziler IS NOT NULL OR diziler != '')
               OR (sarkilar IS NOT NULL OR sarkilar != '')
               OR (kitaplar IS NOT NULL OR kitaplar != '')
               OR (hobiler IS NOT NULL OR hobiler != '')
               OR (Fobiler IS NOT NULL OR Fobiler != '')
        """)
        kullanici_sayisi = cursor.fetchone()[0]
        cursor.close()
        baglanti.close()
        
        if kullanici_sayisi < 2:
            return render_template('sonuc.html', sonuclar=None)
        
        motor_baslat()
        eslesme_sonuclari = eslesme_hesapla(kullanici_id)
    
    session.pop('eslesme_sonuclari', None)
    
    return render_template('sonuc.html', sonuclar=eslesme_sonuclari)

def eslesme_hesapla(kullanici_id):
    global eslesme_motoru
    
    if eslesme_motoru is None:
        motor_baslat()

    baglanti = veritabani_baglantisi()
    cursor = baglanti.cursor()
    cursor.execute("SELECT COUNT(*) FROM kullanici_secimler")
    kullanici_sayisi = cursor.fetchone()[0] # Bu kısımda üstteki SQL sorgusundan dönen count sayısını alıyor count sayısı tek sütun ve tek satır olduğu için [0] diyerek ilk elemanını yani ihtiyacımız olan elemanı almış oluyoruz
    cursor.close()
    baglanti.close()
    
    if kullanici_sayisi < 2:
        return None
    
    sonuclar = eslesme_motoru.hibrit_eslesme_hesapla(kullanici_id)
    
    eslesme_listesi = []
    for sonuc in sonuclar:
        diger_kullanici_id = sonuc['kullanici_id']
        eslesme_orani = sonuc['eslesme_orani']
        
        baglanti = veritabani_baglantisi()
        cursor = baglanti.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT k.id, k.ad, k.soyad, k.email, k.cinsiyet,
                   s.filmler, s.diziler, s.sarkilar, s.kitaplar, s.hobiler, s.Fobiler
            FROM kullanicilar k
            LEFT JOIN kullanici_secimler s ON k.id = s.kullanici_id
            WHERE k.id = %s
            """,
            (diger_kullanici_id,)
        )
        kullanici = cursor.fetchone()
        
        if kullanici:
            filmler_isimleri = id_den_isme_cevir(kullanici['filmler'], 'film') if kullanici['filmler'] else []
            diziler_isimleri = id_den_isme_cevir(kullanici['diziler'], 'dizi') if kullanici['diziler'] else []
            sarkilar_isimleri = id_den_isme_cevir(kullanici['sarkilar'], 'sarki') if kullanici['sarkilar'] else []
            kitaplar_isimleri = id_den_isme_cevir(kullanici['kitaplar'], 'kitap') if kullanici['kitaplar'] else []
            hobiler_isimleri = id_den_isme_cevir(kullanici['hobiler'], 'hobi') if kullanici['hobiler'] else []
            fobiler_isimleri = id_den_isme_cevir(kullanici['Fobiler'], 'fobi') if kullanici['Fobiler'] else []
            
            eslesme_listesi.append({
                'id': kullanici['id'],
                'ad': kullanici['ad'],
                'soyad': kullanici['soyad'],
                'email': kullanici['email'],
                'cinsiyet': kullanici['cinsiyet'],
                'eslesme_orani': int(eslesme_orani),
                'filmler': filmler_isimleri,
                'diziler': diziler_isimleri,
                'sarkilar': sarkilar_isimleri,
                'kitaplar': kitaplar_isimleri,
                'hobiler': hobiler_isimleri,
                'fobiler': fobiler_isimleri
            })
        
        cursor.close()
        baglanti.close()
    
    en_iyi_eslesme = eslesme_listesi[0] if eslesme_listesi else None
    diger_eslesmeler = eslesme_listesi[1:] if len(eslesme_listesi) > 1 else []
    
    baglanti = veritabani_baglantisi()
    cursor = baglanti.cursor(dictionary=True)
    cursor.execute("SELECT ad, soyad, email, cinsiyet FROM kullanicilar WHERE id = %s", (kullanici_id,))
    giris_yapan_kullanici = cursor.fetchone()
    cursor.close()
    baglanti.close()
    
    return {
        'giris_yapan': giris_yapan_kullanici,
        'en_iyi_eslesme': en_iyi_eslesme,
        'diger_eslesmeler': diger_eslesmeler
    }

def id_den_isme_cevir(id_str, kategori):
    """ID'leri isimlere çevir"""
    if not id_str:
        return []
    
    id_listesi = [int(x.strip()) for x in id_str.split(',')]
    isimler = []
    
    if kategori == 'film':
        for film_id in id_listesi:
            film = next((f for f in filmler if f['id'] == film_id), None)
            if film:
                isimler.append(film['isim'])
    
    elif kategori == 'dizi':
        for dizi_id in id_listesi:
            dizi = next((d for d in diziler if d['id'] == dizi_id), None)
            if dizi:
                isimler.append(dizi['isim'])
    
    elif kategori == 'sarki':
        for sarki_id in id_listesi:
            sarki = next((s for s in sarkilar if s['id'] == sarki_id), None)
            if sarki:
                isimler.append(sarki['isim'])
    
    elif kategori == 'kitap':
        for kitap_id in id_listesi:
            kitap = next((k for k in kitaplar if k['id'] == kitap_id), None)
            if kitap:
                isimler.append(kitap['isim'])
    
    elif kategori == 'hobi':
        for hobi_id in id_listesi:
            hobi = next((h for h in hobiler if h['id'] == hobi_id), None)
            if hobi:
                isimler.append(hobi['isim'])
    
    elif kategori == 'fobi':
        for fobi_id in id_listesi:
            fobi = next((f for f in fobiler if f['id'] == fobi_id), None)
            if fobi:
                isimler.append(fobi['isim'])
    
    return isimler

if __name__ == '__main__':
    uygulama.run(debug=True)
