import pandas as pd
from datasets import load_dataset
import json
import os

def prepare_banking_data():
    """
    talkmap/banking-conversation-corpus dataset'inden ilk 1000 kaydı alır,
    anahtar kelimelere göre Türkçe bankacılık cevapları ile Q&A formatına çevirir ve döndürür.
    """
    print(" Banking dataset indiriliyor...")
    
    try:
        # Dataset'i yükle
        # Not: Bu adım internet bağlantısı gerektirir ve biraz zaman alabilir.
        dataset = load_dataset("talkmap/banking-conversation-corpus")
        
        # İlk 1000 satırı al (veya daha azı varsa tamamını)
        df = pd.DataFrame(dataset['train'][:1000])
        
        print(f" {len(df)} konuşma yüklendi")
        
    except Exception as e:
        print(f"Hata: Banking dataset yüklenemedi. ({e}) Boş veri döndürülüyor.")
        return []

    qa_pairs = []

    # Örnek bankacılık cevapları (Türkçe)
    banking_answers = {
        "card": "Kart işleminiz için size yardımcı olabilirim. Kredi kartı veya banka kartı ile ilgili sorunlarınızı çözebiliriz. Lütfen kartınızla ilgili detaylı bilgi verin.",
        "account": "Hesap işlemleriniz için buradayım. Hesap açma, kapatma, bakiye sorgulama gibi işlemlerde yardımcı olabilirim.",
        "transfer": "Para transferi işleminizi gerçekleştirebiliriz. Havale, EFT veya FAST işlemleriniz için destek sağlayabilirim.",
        "payment": "Ödeme işlemlerinizde size yardımcı olabilirim. Fatura, kredi kartı veya diğer ödemelerinizi yapabilirsiniz.",
        "loan": "Kredi başvurunuz veya mevcut kredinizle ilgili destek verebilirim. Detaylı bilgi için müşteri temsilcimize bağlanabilirsiniz.",
        "atm": "ATM işlemlerinizle ilgili yardımcı olabilirim. Para çekme, yatırma veya ATM sorunlarınızı çözebiliriz.",
        "online": "Online bankacılık işlemlerinizde size destek olabilirim. Şifre, giriş veya uygulama sorunlarınızı çözebilirim.",
        "balance": "Bakiye sorgulamanızda yardımcı olabilirim. Hesap veya kart bakiyenizi öğrenebilirsiniz.",
        "pin": "PIN/şifre işlemlerinizde destek sağlayabilirim. Şifre yenileme veya unutma durumlarında yardımcı olabilirim.",
        "default": "Bankacılık işleminizde size yardımcı olmak için buradayım. Lütfen sorunuzu daha detaylı anlatın."
    }

    # Q&A formatına çevir
    for _, row in df.iterrows():
        # 'text' sütununun string olduğundan emin ol
        text = str(row['text']).lower() 
        
        # Kategori bazlı Türkçe cevap seç
        if 'card' in text or 'credit' in text or 'kart' in text:
            answer = banking_answers['card']
        elif 'account' in text or 'hesap' in text:
            answer = banking_answers['account']
        elif 'transfer' in text or 'havale' in text or 'eft' in text:
            answer = banking_answers['transfer']
        elif 'payment' in text or 'ödeme' in text or 'fatura' in text:
            answer = banking_answers['payment']
        elif 'loan' in text or 'kredi' in text:
            answer = banking_answers['loan']
        elif 'atm' in text:
            answer = banking_answers['atm']
        elif 'online' in text or 'app' in text or 'uygulama' in text:
            answer = banking_answers['online']
        elif 'balance' in text or 'bakiye' in text:
            answer = banking_answers['balance']
        elif 'pin' in text or 'password' in text or 'şifre' in text:
            answer = banking_answers['pin']
        else:
            answer = banking_answers['default']
        
        qa_pairs.append({
            "question": row['text'],
            "answer": answer,
            "category": "banking",
            "source": "banking_corpus"
        })
    
    return qa_pairs

def prepare_financial_literacy_data():
    """Finansal okur yazarlıkla ilgili özel olarak oluşturulmuş Q&A verilerini döndürür."""
    print(" Finansal okur yazarlık verileri oluşturuluyor...")
    
    financial_qa = [
        {
            "question": "Bütçe nasıl yapılır?",
            "answer": "Bütçe yapmak için şu adımları izleyin: 1) Aylık gelirinizi hesaplayın, 2) Sabit giderlerinizi (kira, fatura, kredi) listeleyin, 3) Değişken giderlerinizi (market, ulaşım) tahmin edin, 4) Tasarruf için %20 ayırın, 5) Kalan parayı planlamaya göre harcayın. Excel veya bütçe uygulaması kullanabilirsiniz.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Yatırım yapmak için ne kadar param olmalı?",
            "answer": "Yatırım için minimum tutar yoktur. 100 TL ile bile başlayabilirsiniz. Önemli olan düzenli yatırım yapmaktır. Öncelikle 3-6 aylık acil fon oluşturun, sonra küçük miktarlarla yatırıma başlayın. Hisse senedi, tahvil, altın veya fonlar gibi farklı araçları araştırın.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Kredi kartı borcu nasıl ödenir?",
            "answer": "Kredi kartı borcunu ödemek için: 1) Toplam borcunuzu tespit edin, 2) Minimum ödemeden fazla ödemeye çalışın, 3) Yeni harcama yapmayın, 4) Mümkünse tek seferde kapatın, 5) Bankadan taksitlendirme veya borç yapılandırma seçeneklerini sorun. Faiz oranları yüksek olduğu için erken ödemek önemlidir.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Tasarruf nasıl yapılır?",
            "answer": "Tasarruf için pratik yöntemler: 1) Maaşınızın %20'sini hemen ayırın, 2) Otomatik havale talimatı verin, 3) Gereksiz abonelikleri iptal edin, 4) Alışverişte liste kullanın, 5) İkinci el ürün almayı düşünün, 6) Ev yemeği pişirin, 7) Fırsatları bekleyin. Küçük tasarruflar zamanla büyük birikim yapar.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Acil fon ne kadar olmalı?",
            "answer": "Acil fon, 3-6 aylık zorunlu giderinizi karşılayacak kadar olmalıdır. Örneğin aylık gideriniz 10,000 TL ise, 30,000-60,000 TL acil fon bulundurmalısınız. Bu parayı kolay erişilebilir ama harcamayacağınız bir yerde (vadeli hesap, likit fon) tutun. Acil fon, iş kaybı, hastalık gibi beklenmedik durumlar içindir.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Enflasyondan nasıl korunurum?",
            "answer": "Enflasyondan korunmak için: 1) Paranızı boş bırakmayın, değerlendirin, 2) Döviz, altın gibi koruma araçları kullanın, 3) Enflasyona endeksli tahvil alın, 4) Hisse senedi yatırımı yapın, 5) Gayrimenkul değerlendirin, 6) Yabancı para birimi fonları kullanın. Çeşitlendirme yaparak riski dağıtın.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Kredi notu nasıl yükseltilir?",
            "answer": "Kredi notunu yükseltmek için: 1) Fatura ve kredi ödemelerinizi zamanında yapın, 2) Kredi kartı limitinizin %30'undan fazlasını kullanmayın, 3) Çok fazla kredi başvurusu yapmayın, 4) Eski kredi kartlarınızı kapatmayın, 5) Borç/gelir oranınızı düşük tutun, 6) KKB raporunuzu kontrol edin. Not yükselmesi 3-6 ay sürebilir.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Emeklilik için nasıl birikim yapmalıyım?",
            "answer": "Emeklilik için birikim yaparken: 1) Bireysel emeklilik sistemine (BES) katılın (devlet katkısı %25), 2) Gelirinizin en az %10-15'ini ayırın, 3) Erken başlayın (bileşik faiz etkisi), 4) Uzun vadeli yatırım fonları seçin, 5) Yılda bir kez gözden geçirin, 6) Risk iştahınıza göre portföy oluşturun. 30 yaşında başlamak 40'ta başlamaktan çok daha avantajlıdır.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Hangi yatırım aracını seçmeliyim?",
            "answer": "Yatırım aracı seçerken: 1) Risk toleransınızı belirleyin, 2) Yatırım sürenizi planlayın (kısa/orta/uzun vade), 3) Çeşitlendirme yapın (hisse, tahvil, altın, döviz), 4) Küçük başlayın ve öğrenin, 5) Profesyonel danışman desteği alın. Genç yatırımcılar daha riskli (hisse), yaşlılar daha güvenli (tahvil) araçları tercih edebilir.",
            "category": "financial_literacy",
            "source": "custom"
        },
        {
            "question": "Sigorta almak gerekli mi?",
            "answer": "Sigorta, beklenmedik durumlara karşı finansal koruma sağlar. Temel sigortalar: 1) Sağlık sigortası (zorunlu), 2) Hayat sigortası (aileniz varsa), 3) Konut sigortası (deprem, yangın), 4) Trafik sigortası (araç sahibi iseniz). Sigorta prim ödemek masraf gibi görünse de, büyük kayıplara karşı korur. Genç ve sağlıklıyken almak daha ucuzdur.",
            "category": "financial_literacy",
            "source": "custom"
        }
    ]
    
    print(f" {len(financial_qa)} finansal eğitim verisi eklendi")
    return financial_qa

def save_all_data():
    """Tüm bankacılık ve finansal okur yazarlık verilerini birleştirir ve JSON dosyasına kaydeder."""
    print(" Veriler birleştiriliyor...")
    
    # İki veri setini al
    banking_data = prepare_banking_data()
    financial_data = prepare_financial_literacy_data()
    
    # Birleştir
    all_data = banking_data + financial_data
    
    # Kaydet
    output_path = 'data/all_qa_data.json'
    # Klasör yoksa oluştur
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # JSON olarak kaydet
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n Toplam {len(all_data)} veri {output_path} dosyasına kaydedildi!")
    print(f"   - Bankacılık Konuşmaları: {len(banking_data)} adet")
    print(f"   - Finansal Okur Yazarlık: {len(financial_data)} adet")

if __name__ == "__main__":
    save_all_data()