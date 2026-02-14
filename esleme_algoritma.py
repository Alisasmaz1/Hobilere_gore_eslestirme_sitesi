import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import jaccard
from scipy.stats import pearsonr
import mysql.connector
from mysql.connector import Error
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import hashlib
import warnings
warnings.filterwarnings('ignore')


class GelismisHibritEslesmeMotoru:
    
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.users_df = None
        self.selections_df = None
        self.user_vectors = None
        self.demographic_vectors = None
        self.nmf_features = None
        self.svd_features = None
        self.clusters_kmeans = None
        self.clusters_dbscan = None
        self.knn_model = None
        self.category_weights = None
        self.similarity_cache = {}
        
        self.standard_scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        
        self.weights = {
            'collaborative_cosine': 0.12,
            'collaborative_pearson': 0.08,
            'vector_cosine': 0.10,
            'vector_euclidean': 0.06,
            'jaccard_similarity': 0.25,
            'nmf_factorization': 0.10,
            'svd_factorization': 0.06,
            'kmeans_clustering': 0.10,
            'dbscan_clustering': 0.06,
            'knn_neighbors': 0.07
        }
        
        self.category_ids = {
            'filmler': [],
            'diziler': [],
            'sarkilar': [],
            'kitaplar': [],
            'hobiler': [],
            'fobiler': []
        }
        
        self.user_category_preferences = {}
        
    def veritabani_baglantisi(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except Error as e:
            print(f"Veritabani baglanti hatasi: {e}")
            return None
    
    def veri_yukle(self):
        baglanti = self.veritabani_baglantisi()
        if not baglanti:
            return False
        
        try:
            query_users = """
                SELECT id, ad, soyad, email, yas, cinsiyet, bolge, egitim
                FROM kullanicilar
                ORDER BY id
            """
            self.users_df = pd.read_sql(query_users, baglanti)
            
            query_selections = """
                SELECT kullanici_id, filmler, diziler, sarkilar, kitaplar, hobiler, Fobiler
                FROM kullanici_secimler
                ORDER BY kullanici_id
            """
            self.selections_df = pd.read_sql(query_selections, baglanti)
            
            baglanti.close()
            return True
            
        except Error as e:
            print(f"Veri yukleme hatasi: {e}")
            if baglanti:
                baglanti.close()
            return False
    
    def kategori_id_toplama(self):
        for kategori in ['filmler', 'diziler', 'sarkilar', 'kitaplar', 'hobiler', 'Fobiler']:
            all_ids = set()
            col_name = kategori if kategori != 'Fobiler' else 'Fobiler'
            
            for _, row in self.selections_df.iterrows():
                if pd.notna(row[col_name]):
                    ids = [int(x.strip()) for x in str(row[col_name]).split(',') if x.strip()]
                    all_ids.update(ids)
            
            key = 'fobiler' if kategori == 'Fobiler' else kategori
            self.category_ids[key] = sorted(list(all_ids))
    
    def kategori_agirlik_hesapla(self):
        self.category_weights = {
            'filmler': 1.0,
            'diziler': 1.0,
            'sarkilar': 1.0,
            'kitaplar': 1.0,
            'hobiler': 0.8,
            'fobiler': 1.2
        }
    
    def ana_vektor_olustur(self):
        all_vectors = []
        
        for _, selection in self.selections_df.iterrows():
            user_vector = []
            
            for kategori in ['filmler', 'diziler', 'sarkilar', 'kitaplar', 'hobiler', 'fobiler']:
                col_name = 'Fobiler' if kategori == 'fobiler' else kategori
                category_vector = self._kategori_vektoru_olustur(
                    selection[col_name], 
                    self.category_ids[kategori]
                )
                
                weight = self.category_weights.get(kategori, 1.0)
                weighted_vector = np.array(category_vector) * weight
                user_vector.extend(weighted_vector)
            
            all_vectors.append(user_vector)
        
        self.user_vectors = np.array(all_vectors)
        return self.user_vectors
    
    def _kategori_vektoru_olustur(self, selection_str, all_ids):
        if pd.isna(selection_str) or not all_ids:
            return [0] * len(all_ids)
        
        selected_ids = set([int(x.strip()) for x in str(selection_str).split(',') if x.strip()])
        return [1 if item_id in selected_ids else 0 for item_id in all_ids]
    
    def demografik_ozellik_olustur(self):
        merged = self.selections_df.merge(
            self.users_df[['id', 'yas', 'cinsiyet', 'bolge', 'egitim']], 
            left_on='kullanici_id', 
            right_on='id',
            how='left'
        )
        
        merged['yas'] = merged['yas'].fillna(25)
        merged['cinsiyet'] = merged['cinsiyet'].fillna('diger')
        merged['bolge'] = merged['bolge'].fillna('bilinmeyen')
        merged['egitim'] = merged['egitim'].fillna('lise')
        
        yas_norm = (merged['yas'] - 18) / 82
        yas_norm = np.array(yas_norm)
        yas_norm = np.nan_to_num(yas_norm, nan=0.5)
        
        cinsiyet_encoded = merged['cinsiyet'].map({'erkek': 0, 'kadin': 1, 'diger': 0.5})
        cinsiyet_encoded = np.array(cinsiyet_encoded.fillna(0.5))
        
        unique_bolge = sorted(merged['bolge'].unique())
        if len(unique_bolge) > 1:
            bolge_map = {b: i for i, b in enumerate(unique_bolge)}
            bolge_encoded = merged['bolge'].map(bolge_map) / (len(unique_bolge) - 1)
        else:
            bolge_encoded = merged['bolge'].map(lambda x: 0.5)
        bolge_encoded = np.array(bolge_encoded.fillna(0.5))
        
        egitim_map = {'ilkokul': 0.2, 'ortaokul': 0.4, 'lise': 0.6, 'universite': 0.8, 'lisansustu': 1.0}
        egitim_encoded = merged['egitim'].map(egitim_map)
        egitim_encoded = np.array(egitim_encoded.fillna(0.6))
        
        yas_cinsiyet_interaction = yas_norm * cinsiyet_encoded
        yas_egitim_interaction = yas_norm * egitim_encoded
        
        self.demographic_vectors = np.column_stack([
            yas_norm,
            cinsiyet_encoded,
            bolge_encoded,
            egitim_encoded,
            yas_cinsiyet_interaction,
            yas_egitim_interaction
        ])
        
        self.demographic_vectors = np.nan_to_num(self.demographic_vectors, nan=0.5)
        
        demographic_scaled = self.minmax_scaler.fit_transform(self.demographic_vectors)
        demographic_weighted = demographic_scaled * 0.35
        
        if self.user_vectors is not None:
            self.user_vectors = np.hstack([self.user_vectors, demographic_weighted])
            self.user_vectors = np.nan_to_num(self.user_vectors, nan=0.0)
    
    def kullanici_tercih_profili_olustur(self):
        for idx, selection in self.selections_df.iterrows():
            user_id = selection['kullanici_id']
            profile = {}
            
            for kategori in ['filmler', 'diziler', 'sarkilar', 'kitaplar', 'hobiler', 'fobiler']:
                col_name = 'Fobiler' if kategori == 'fobiler' else kategori
                if pd.notna(selection[col_name]):
                    selected = [int(x.strip()) for x in str(selection[col_name]).split(',') if x.strip()]
                    profile[kategori] = {
                        'count': len(selected),
                        'ids': set(selected),
                        'diversity': len(selected) / len(self.category_ids[kategori]) if self.category_ids[kategori] else 0
                    }
                else:
                    profile[kategori] = {'count': 0, 'ids': set(), 'diversity': 0}
            
            self.user_category_preferences[user_id] = profile
    
    def _generate_cache_key(self, user_idx: int, method: str) -> str:
        user_data = str(self.user_vectors[user_idx].tolist())
        return hashlib.md5(f"{user_idx}_{method}_{user_data}".encode()).hexdigest()
    
    def yontem1_collaborative_cosine(self, user_idx: int) -> np.ndarray:
        cache_key = self._generate_cache_key(user_idx, 'collab_cosine')
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        user_vec = self.user_vectors[user_idx].reshape(1, -1)
        similarities = cosine_similarity(user_vec, self.user_vectors)[0]
        similarities[user_idx] = 0
        
        self.similarity_cache[cache_key] = similarities
        return similarities
    
    def yontem2_collaborative_pearson(self, user_idx: int) -> np.ndarray:
        cache_key = self._generate_cache_key(user_idx, 'collab_pearson')
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        user_vec = self.user_vectors[user_idx]
        n_users = self.user_vectors.shape[0]
        correlations = np.zeros(n_users)
        
        for i in range(n_users):
            if i != user_idx:
                other_vec = self.user_vectors[i]
                if np.std(user_vec) > 0 and np.std(other_vec) > 0:
                    corr, _ = pearsonr(user_vec, other_vec)
                    correlations[i] = max(0, corr)
        
        self.similarity_cache[cache_key] = correlations
        return correlations
    
    def yontem3_vector_cosine_normalized(self, user_idx: int) -> np.ndarray:
        norms = np.linalg.norm(self.user_vectors, axis=1, keepdims=True)
        normalized = self.user_vectors / (norms + 1e-10)
        
        user_vec = normalized[user_idx].reshape(1, -1)
        similarities = cosine_similarity(user_vec, normalized)[0]
        similarities[user_idx] = 0
        return similarities
    
    def yontem4_vector_euclidean(self, user_idx: int) -> np.ndarray:
        user_vec = self.user_vectors[user_idx].reshape(1, -1)
        distances = euclidean_distances(user_vec, self.user_vectors)[0]
        
        max_dist = distances.max()
        if max_dist > 0:
            similarities = 1 - (distances / max_dist)
        else:
            similarities = np.zeros_like(distances)
        
        similarities[user_idx] = 0
        return similarities
    
    def yontem5_jaccard_similarity(self, user_idx: int) -> np.ndarray:
        n_users = self.user_vectors.shape[0]
        similarities = np.zeros(n_users)
        
        user_vec = (self.user_vectors[user_idx] > 0).astype(int)
        
        for i in range(n_users):
            if i != user_idx:
                other_vec = (self.user_vectors[i] > 0).astype(int)
                intersection = np.sum(user_vec & other_vec)
                union = np.sum(user_vec | other_vec)
                if union > 0:
                    similarities[i] = intersection / union
        
        return similarities
    
    def yontem6_nmf_factorization(self, user_idx: int, n_components: int = 30) -> np.ndarray:
        if self.nmf_features is None:
            positive_vectors = np.abs(self.user_vectors)
            n_comp = min(n_components, positive_vectors.shape[1] - 1, positive_vectors.shape[0] - 1)
            
            nmf = NMF(n_components=n_comp, init='nndsvda', random_state=42, max_iter=1000, alpha_W=0.1, alpha_H=0.1, l1_ratio=0.5)
            self.nmf_features = nmf.fit_transform(positive_vectors)
        
        user_features = self.nmf_features[user_idx].reshape(1, -1)
        similarities = cosine_similarity(user_features, self.nmf_features)[0]
        similarities[user_idx] = 0
        return similarities
    
    def yontem7_svd_factorization(self, user_idx: int, n_components: int = 25) -> np.ndarray:
        if self.svd_features is None:
            n_comp = min(n_components, self.user_vectors.shape[1] - 1, self.user_vectors.shape[0] - 1)
            svd = TruncatedSVD(n_components=n_comp, random_state=42, n_iter=10)
            self.svd_features = svd.fit_transform(self.user_vectors)
        
        user_features = self.svd_features[user_idx].reshape(1, -1)
        similarities = cosine_similarity(user_features, self.svd_features)[0]
        similarities[user_idx] = 0
        return similarities
    
    def yontem8_kmeans_clustering(self, user_idx: int, n_clusters: int = 8) -> np.ndarray:
        if self.clusters_kmeans is None:
            scaled_vectors = self.standard_scaler.fit_transform(self.user_vectors)
            n_clust = min(n_clusters, len(self.users_df) // 3)
            if n_clust < 2:
                return np.zeros(len(self.users_df))
            
            kmeans = KMeans(n_clusters=n_clust, random_state=42, n_init=15, max_iter=500)
            self.clusters_kmeans = kmeans.fit_predict(scaled_vectors)
        
        user_cluster = self.clusters_kmeans[user_idx]
        cluster_scores = (self.clusters_kmeans == user_cluster).astype(float)
        cluster_scores[user_idx] = 0
        return cluster_scores
    
    def yontem9_dbscan_clustering(self, user_idx: int, eps: float = 0.5, min_samples: int = 2) -> np.ndarray:
        if self.clusters_dbscan is None:
            scaled_vectors = self.standard_scaler.fit_transform(self.user_vectors)
            dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
            self.clusters_dbscan = dbscan.fit_predict(scaled_vectors)
        
        user_cluster = self.clusters_dbscan[user_idx]
        if user_cluster == -1:
            return np.zeros(len(self.users_df))
        
        cluster_scores = (self.clusters_dbscan == user_cluster).astype(float)
        cluster_scores[user_idx] = 0
        return cluster_scores
    
    def yontem10_knn_neighbors(self, user_idx: int, n_neighbors: int = 10) -> np.ndarray:
        if self.knn_model is None:
            n_neigh = min(n_neighbors, len(self.users_df) - 1)
            self.knn_model = NearestNeighbors(n_neighbors=n_neigh, metric='cosine', algorithm='brute')
            self.knn_model.fit(self.user_vectors)
        
        user_vec = self.user_vectors[user_idx].reshape(1, -1)
        distances, indices = self.knn_model.kneighbors(user_vec)
        
        knn_scores = np.zeros(len(self.users_df))
        for dist, idx in zip(distances[0], indices[0]):
            if idx != user_idx:
                knn_scores[idx] = 1 - dist
        
        return knn_scores
    
    def kategori_benzerlik_bonusu(self, user_idx: int) -> np.ndarray:
        user_id = self.selections_df.iloc[user_idx]['kullanici_id']
        user_profile = self.user_category_preferences.get(user_id, {})
        
        n_users = len(self.selections_df)
        bonus_scores = np.zeros(n_users)
        
        for idx in range(n_users):
            if idx == user_idx:
                continue
            
            other_id = self.selections_df.iloc[idx]['kullanici_id']
            other_profile = self.user_category_preferences.get(other_id, {})
            
            category_match_scores = []
            for kategori in ['filmler', 'diziler', 'sarkilar', 'kitaplar', 'hobiler', 'fobiler']:
                user_ids = user_profile.get(kategori, {}).get('ids', set())
                other_ids = other_profile.get(kategori, {}).get('ids', set())
                
                if user_ids or other_ids:
                    intersection = len(user_ids & other_ids)
                    union = len(user_ids | other_ids)
                    
                    if union > 0:
                        jaccard_sim = intersection / union
                        category_match_scores.append(jaccard_sim)
                    else:
                        category_match_scores.append(0)
            
            if category_match_scores:
                bonus_scores[idx] = np.mean(category_match_scores)
        
        return bonus_scores
    
    def hibrit_eslesme_hesapla(self, kullanici_id: str) -> List[Dict]:
        user_row = self.selections_df[self.selections_df['kullanici_id'] == kullanici_id]
        if user_row.empty:
            return []
        
        user_idx = user_row.index[0]
        
        score1 = self.yontem1_collaborative_cosine(user_idx)
        score2 = self.yontem2_collaborative_pearson(user_idx)
        score3 = self.yontem3_vector_cosine_normalized(user_idx)
        score4 = self.yontem4_vector_euclidean(user_idx)
        score5 = self.yontem5_jaccard_similarity(user_idx)
        score6 = self.yontem6_nmf_factorization(user_idx)
        score7 = self.yontem7_svd_factorization(user_idx)
        score8 = self.yontem8_kmeans_clustering(user_idx)
        score9 = self.yontem9_dbscan_clustering(user_idx)
        score10 = self.yontem10_knn_neighbors(user_idx)
        
        bonus = self.kategori_benzerlik_bonusu(user_idx)
        
        raw_scores = (
            self.weights['collaborative_cosine'] * score1 +
            self.weights['collaborative_pearson'] * score2 +
            self.weights['vector_cosine'] * score3 +
            self.weights['vector_euclidean'] * score4 +
            self.weights['jaccard_similarity'] * score5 +
            self.weights['nmf_factorization'] * score6 +
            self.weights['svd_factorization'] * score7 +
            self.weights['kmeans_clustering'] * score8 +
            self.weights['dbscan_clustering'] * score9 +
            self.weights['knn_neighbors'] * score10
        )
        
        final_scores = raw_scores + (0.03 * bonus)
        
        final_scores = np.clip(final_scores * 100, 0, 100)
        
        sonuclar = []
        for idx, score in enumerate(final_scores):
            if score > 0:
                kullanici_id_diger = self.selections_df.iloc[idx]['kullanici_id']
                sonuclar.append({
                    'kullanici_id': kullanici_id_diger,
                    'eslesme_orani': round(float(score), 2)
                })
        
        sonuclar.sort(key=lambda x: x['eslesme_orani'], reverse=True)
        return sonuclar
    
    def model_egit(self):
        if not self.veri_yukle():
            return False
        
        self.kategori_id_toplama()
        self.kategori_agirlik_hesapla()
        self.ana_vektor_olustur()
        self.demografik_ozellik_olustur()
        self.kullanici_tercih_profili_olustur()
        
        dummy_idx = 0
        _ = self.yontem6_nmf_factorization(dummy_idx)
        _ = self.yontem7_svd_factorization(dummy_idx)
        _ = self.yontem8_kmeans_clustering(dummy_idx)
        _ = self.yontem9_dbscan_clustering(dummy_idx)
        _ = self.yontem10_knn_neighbors(dummy_idx)
        
        return True