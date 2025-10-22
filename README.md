# 🏦 Akbank Dijital Finansal Merkezi
Bu proje, Akbank GenAI Bootcamp kapsamında geliştirilmiş, RAG (Retrieval-Augmented Generation) mimarisine dayanan yapay zeka destekli bir finansal asistandır. Kullanıcılara finansal okuryazarlık ve bankacılık işlemleri hakkında hızlı, güvenilir ve kişiselleştirilmiş rehberlik sağlamayı amaçlar.
## 🎯 1. Projenin Amacı
Projenin temel amacı, Gemini 2.5 Flash modelini kullanarak, bankacılık sohbet verileri ve finansal okuryazarlık içeriği ile zenginleştirilmiş (RAG), Türkçe konuşan bir chatbot geliştirmektir.Proje, hem temel bankacılık sorularını yanıtlayabilen hem de kullanıcılara bütçeleme, tasarruf ve yatırım konularında eğitim verebilen bir web arayüzü (Streamlit) üzerinden hizmet veren bir ürün ortaya koyar.
## 💾 2. Veri Seti Hazırlama
Proje, iki ana veri kaynağının birleştirilmesiyle oluşturulan data/all_qa_data.json dosyasını kullanmaktadır. Toplamda yaklaşık 1010 adet Soru-Cevap (Q&A) çifti, Vector Store oluşturulmasında bağlam (context) olarak kullanılmaktadır.
| Veri Seti | Açıklama | Hazırlık Metodu |
| :--- | :--- | :--- |
| **Bankacılık Konuşma Metinleri** | `talkmap/banking-conversation-corpus` adlı genel veri setinden ilk 1000 kayıt. | Anahtar kelime bazlı eşleştirme ile standart Türkçe bankacılık cevaplarına dönüştürüldü (`data_prep.py` - `prepare_banking_data()`). |
| **Finansal Okuryazarlık Q&A** | Bütçeleme, tasarruf, kredi notu, yatırım ve acil fon gibi temel finansal konularda özel olarak hazırlanmış 10 Q&A çifti. | Manuel olarak özel Soru-Cevap çiftleri eklendi (`data_prep.py` - `prepare_financial_literacy_data()`). |

## 🛠️ 3. Kodunuzun Çalışma KılavuzuBu kılavuz, projenin yerel bilgisayarınızda nasıl kurulacağını ve çalıştırılacağını açıklar.
### 3.1. Ön Gereksinimler
Python 3.9+

Google Gemini API Anahtarı
### 3.2. Geliştirme Ortamı Kurulumu
Proje, bağımlılık çakışmalarını önlemek için sanal ortamda çalıştırılmalıdır.

### Sanal ortam oluşturma
python -m venv venv

### Sanal ortamı etkinleştirme (Linux/macOS)
source venv/bin/activate

### Sanal ortamı etkinleştirme (Windows)
.\venv\Scripts\activate

### Gerekli bağımlılıkları yükleme (requirements.txt dosyası deponuzda olmalıdır)
pip install -r requirements.txt 

### 3.3. API Anahtarını AyarlamaGemini modelini kullanmak için API anahtarınızı güvenli bir şekilde tanımlayın.
Projenin ana dizininde .env adında bir dosya oluşturun.
Anahtarınızı aşağıdaki formatta ekleyin:
GOOGLE_API_KEY="AIzaSy...API...Key...Buraya"
### 3.4. Veri Hazırlığı
RAG modelinin kullanacağı Q&A verilerini hazırlayın. Eğer data/all_qa_data.json dosyası GitHub'a eklenmediyse bu adım zorunludur.
python data_prep.py
Bu komut, kaynakları indirir ve 'data/all_qa_data.json' dosyasını oluşturur.

### 3.5. Uygulamayı Başlatma
Web arayüzünü (Streamlit) başlatarak projeyi çalıştırın:
streamlit run app.py
Uygulama, otomatik olarak tarayıcınızda açılacaktır (genellikle http://localhost:8501).
## ⚙️ 4. Çözüm Mimarisi
### 4.1. Kullanılan Teknolojiler
| Kategori | Teknoloji | Amaç |
| :--- | :--- | :--- |
| **Büyük Dil Modeli** | Google Gemini 2.5 Flash | Soru yanıtlama (Generation) |
| **Gömme Modeli** | HuggingFace (MiniLM-L12-v2) | Vektör oluşturma (Embedding) |
| **Vektör Veritabanı** | FAISS | Hızlı benzerlik araması (Retrieval) |
| **Orkestrasyon** | LangChain | RAG zincirinin yönetimi |
| **Web Arayüzü** | Streamlit | Kullanıcı arayüzü (Front-end) ve Product Kılavuzu |
### 4.2. RAG (Retrieval-Augmented Generation) Mimarisi
Proje, Akbank asistanı rolünü üstlenen kontrollü bir RAG mimarisi kullanır
Veri Hazırlama: Q&A çiftleri yüklenir.Embedding: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 modeli ile her bir Q&A çifti vektörlere dönüştürülür.
Vektör Veritabanı: Vektörler, FAISS'e kaydedilir.Retrieval: Kullanıcının sorusu vektöre dönüştürülerek FAISS'te en yakın 3 döküman (k=3) geri çağrılır.
Generation: Geri çağrılan 3 döküman, Akbank asistanı kişiliğini ve yanıtlama kurallarını (nazik, Türkçe, profesyonel vb.) içeren özel bir Prompt Template'in {context} alanına yerleştirilir.
Cevap Üretimi: Gemini 2.5 Flash modeli, bu prompt ve bağlamı kullanarak son kullanıcıya nihai cevabı üretir. Bu süreç LangChain RetrievalQA Chain ile yönetilir.
## 🖥️ 5. Web Arayüzü & Product KılavuzuUygulama, kullanıcı deneyimini zenginleştirmek için 3 ana sekmeyle tasarlanmıştır.
### Elde Edilen Sonuçlar
Çift Odaklı Asistan: Hem teknik bankacılık sorularına (hesap, transfer) hem de uzun vadeli finansal eğitime (bütçe, tasarruf, yatırım) odaklanan iki farklı bilgi türü tek bir RAG mimarisinde birleştirilmiştir.
Kontrollü Yanıtlama: Prompt Template, LLM'e bankanın kurumsal kimliğini ve belirli yanıt kurallarını entegre ederek daha kontrollü ve amaca uygun Türkçe yanıtlar elde edilmesini sağlar.
Zengin Kullanıcı Deneyimi: Streamlit arayüzü, etkileşimli sohbetin yanı sıra "Öğren" sekmesinde finansal kısa rehberler ve "Araçlar" sekmesinde basit finansal hesaplayıcılara erişim sunar.
Çalışma Akışı ve Test Adımları
| Sekme | Amaç | Test Adımı |
| :--- | :--- | :--- |
| **Sohbet Sekmesi** | Bankacılık ve finansal sorulara RAG üzerinden yanıt almak. | Hızlı Başlangıç çiplerinden birine tıklayın (örn: *Aylık bütçeyi nasıl planlarım?*) veya *Kredi kartı borcu nasıl ödenir?* gibi bir soru sorun. |
| **Öğren Sekmesi** | Temel finansal konular hakkında hızlı rehberlik ve ipuçları sunmak. | **"Konu seçin"** menüsünden bir kategori seçin (örn: *Vadeli Mevduat*) ve **"Bu kategori için açıklama üret"** butonu ile LLM'den detaylı plan talep edin. |
| **Araçlar Sekmesi** | Kullanıcıların temel finansal senaryoları (borç, tasarruf) simüle etmesini sağlamak. | **Borç Azaltma Simülasyonu** veya **Tasarruf Hedefi** alanlarındaki değişkenleri değiştirerek "Hesapla" veya "Planla" butonlarına tıklayın. |
## 🔗 Web LinkinizProjenizin canlı linkini buraya yapıştırın.
Web Linki: https://akbank-financial-chatbot-x5bqhxavamrbijtbfapkms.streamlit.app/
