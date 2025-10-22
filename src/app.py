import os
from dotenv import load_dotenv
import streamlit as st
from rag_pipeline import FinancialChatbot

THEME_AWARE_CSS = """
<style>
:root {
  --bubble-user-bg: var(--secondary-background);
  --bubble-user-fg: var(--text-color);
  --bubble-assistant-bg: var(--primary-color);
  --bubble-assistant-fg: #ffffff;
}

/* streamlit değişkenlerini tema'dan oku */
html[data-theme="light"] :root {
  --primary-color: var(--color-primary);
  --text-color: black;
  --secondary-background: #e9ecef;
}
html[data-theme="dark"] :root {
  --primary-color: var(--color-primary);
  --text-color: #eaeef5;
  --secondary-background: #222831;
}

/* sohbet alanı */
.block-container { padding-top: 1.2rem; }

/* mesaj kartı genişliği */
.stChatMessage { max-width: 900px; }

/* baloncuk gövdeleri */
.stChatMessage [data-testid="stChatMessageContent"] > div {
  padding: 10px 14px;
  border-radius: 16px;
  line-height: 1.55;
}

/* assistant baloncuğu */
.stChatMessage:has([data-testid="chat-avatar"][aria-label="assistant"]) 
  [data-testid="stChatMessageContent"] > div {
  background: var(--bubble-assistant-bg);
  color: var(--bubble-assistant-fg);
  border-radius: 16px 16px 16px 4px;
}

/* user baloncuğu */
.stChatMessage:has([data-testid="chat-avatar"][aria-label="user"]) 
  [data-testid="stChatMessageContent"] > div {
  background: var(--bubble-user-bg);
  color: var(--bubble-user-fg);
  border-radius: 16px 16px 4px 16px;
}

/* yapışkan input */
.stChatInput { position: sticky; bottom: 0; z-index: 2; }

/* başlık çubuğu */
.app-header {
  position: sticky; top: 0; z-index: 3;
  backdrop-filter: blur(6px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  padding: 10px 0;
}
</style>
"""


# 0) page config en başta olmalı
st.set_page_config(page_title="Finansal Asistan", page_icon="🏦", layout="wide")

# 1) env ve tema CSS
load_dotenv()
st.markdown(THEME_AWARE_CSS, unsafe_allow_html=True)

# 2) header
with st.container():
    st.markdown(
        """
        <div class="app-header">
          <div style="display:flex;align-items:center;gap:12px;">
            <img src="https://w7.pngwing.com/pngs/98/991/png-transparent-computer-icons-bank-icon-design-screenshot-bank-blue-angle-logo.png" width="36">
            <div>
              <h2 style="margin:0">Dijital Finansal Merkezi</h2>
              <p style="margin:0;color:#8a94a6;font-size:14px">
                Finansal okuryazarlık ve bankacılık konularında hızlı, güvenilir rehberlik.
              </p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 3) chatbot yükleme
@st.cache_resource(show_spinner=False)
def load_chatbot():
    try:
        return FinancialChatbot()
    except Exception as e:
        st.error(f"Sistem başlatılamadı: {e}")
        return None

chatbot = load_chatbot()

# 4) session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stats" not in st.session_state:
    st.session_state.stats = {"turns": 0, "avg_latency_ms": 0}

# 5) sidebar: durum, yönetim, metrikler
# 5) sidebar: durum, yönetim
with st.sidebar:
    st.subheader("Sistem Durumu")
    if chatbot:
        st.success("Asistan Çevrimiçi ✅")
    else:
        st.warning("Asistan Çevrimdışı ⚠️")

    st.divider()
    st.subheader("Yönetim")
    if st.button("🧹 Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.session_state.stats = {"turns": 0, "avg_latency_ms": 0}
        st.rerun()

    if st.button("⬇️ Sohbeti Dışa Aktar (.txt)", use_container_width=True):
        from io import StringIO
        buf = StringIO()
        for m in st.session_state.messages:
            role = m["role"].upper()
            buf.write(f"{role}: {m['content']}\n\n")
        st.download_button(
            "İndir", 
            data=buf.getvalue(), 
            file_name="sohbet.txt", 
            mime="text/plain"
        )

    st.divider()
    st.caption("Geliştirici: Akbank GenAI Projesi")


# 6) sekmeler
tab_chat, tab_learn, tab_tools = st.tabs(["Sohbet", "Öğren", "Araçlar"])

with tab_chat:
    # hızlı başlangıç çipleri
    st.write("Hızlı Başlangıç")
    cols = st.columns(4)
    examples = [
        "Aylık bütçeyi nasıl planlarım?",
        "Kredi kartı borcunu azaltmanın yolları?",
        "Acil durum fonu için hedef ne olmalı?",
        "Vadeli mevduat ile fon farkı nedir?"
    ]
    for i, q in enumerate(examples):
        with cols[i]:
            if st.button(q, key=f"chip_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

    st.divider()

    # geçmişi çiz
    for msg in st.session_state.messages:
        avatar = "🧑" if msg["role"] == "user" else "💼"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # --- OTOMATİK CEVAP: son mesaj kullanıcıysa yanıt üret
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        if chatbot is not None:
            user_prompt = st.session_state.messages[-1]["content"]
            with st.chat_message("assistant", avatar="💼"):
                with st.spinner("Analiz ediliyor..."):
                    try:
                        raw = chatbot.ask(user_prompt)  # str veya {text, sources}
                    except Exception as e:
                        raw = {"text": f"Hata: {e}", "sources": []}

                    if isinstance(raw, str):
                        text, sources = raw, []
                    else:
                        text = raw.get("text") or raw.get("answer") or ""
                        sources = raw.get("sources") or raw.get("citations") or []

                    st.markdown(text)
                    if sources:
                        with st.expander("Kaynaklar"):
                            for s in sources:
                                st.markdown(f"- {s}")

                    # (opsiyonel) geri bildirim butonları
                    fb1, fb2, _ = st.columns([0.15, 0.2, 0.65])
                    with fb1:
                        if st.button("Yararlı", key=f"fb_up_{len(st.session_state.messages)}"):
                            st.toast("Teşekkürler, geri bildirimin kaydedildi.")
                    with fb2:
                        if st.button("Yararsız", key=f"fb_dn_{len(st.session_state.messages)}"):
                            st.toast("Geri bildirimin alındı.")

                    st.session_state.messages.append({"role": "assistant", "content": text})
                    st.session_state.stats["turns"] += 1
                    st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Sistem çevrimdışı."})
            st.rerun()

    # giriş (sadece mesaj ekle, yanıt üretimini yukarıdaki blok yapıyor)
    user_text = st.chat_input("Finansal bir soru yazın...")
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.rerun()


with tab_learn:
    st.subheader("Kısa Rehberler")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Bütçe Planı 50/30/20")
        st.markdown("- Zorunlu: %50\n- İstekler: %30\n- Tasarruf/Borç: %20")
        st.markdown("#### İpucu\nGelir değişkense önce acil fonu tamamla.")
    with c2:
        st.markdown("### Acil Durum Fonu")
        st.markdown("- Hedef: 3–6 ay gider\n- Yöntem: Otomatik ayırma\n- Yer: Düşük riskli, likit")

    st.divider()
    st.markdown("### Sık Sorulanlar")

    # 1) Kategori içerikleri
    FAQ_CONTENT = {
        "Kredi Notu": {
            "summary": "Kredi notu; ödeme alışkanlığı, mevcut borçluluk ve kredi kullanım geçmişine göre belirlenir.",
            "bullets": [
                "Ödemeleri zamanında yapmak en güçlü etkendir.",
                "Kredi kullanım oranını düşük tut (kullanılan limit / toplam limit).",
                "Sık kredi/limit başvuruları kısa vadede notu olumsuz etkileyebilir.",
                "Uzun ve sorunsuz geçmiş notu destekler."
            ],
            "tips": [
                "Asgari değil tam ödeme yap.",
                "Limitinin %30’unu aşmamaya çalış.",
                "Gereksiz başvurulardan kaçın."
            ],
            "prompt": "Kredi notumu hızlı ve sürdürülebilir şekilde artırmak için kişisel bir plan öner."
        },
        "Vadeli Mevduat": {
            "summary": "Vadeli mevduat, anapara korunurken vade sonunda faiz geliri sağlar.",
            "bullets": [
                "Vade kırılmadan çekimde faiz kaybı olabilir.",
                "Stopaj sonrası net getiri hesaplanmalı.",
                "Faiz oranı ve vade seçimi net getiriyi belirler."
            ],
            "tips": [
                "Vade sonunda otomatik yenileme koşullarını kontrol et.",
                "Acil nakit için vadesiz kenarda tutar bırak."
            ],
            "prompt": "100.000 TL için 32 gün vadede stopaj sonrası net getiriyi hesapla; farklı oranlara duyarlılık analizi yap."
        },
        "Fonlar": {
            "summary": "Yatırım fonları profesyonel yönetilen portföylerdir; risk ve getiri profilleri farklıdır.",
            "bullets": [
                "Para piyasası fonları düşük riskli ve likittir.",
                "Borçlanma araçları fonları orta riskte sabit getirili enstrümanlara yatırım yapar.",
                "Hisse senedi fonları daha değişkendir; uzun vadede potansiyel getiri yüksektir.",
                "Katılım fonları faizsiz ilkelere göre yönetilir."
            ],
            "tips": [
                "Risk-getiri tercihini ve vade hedefini netleştir.",
                "Masraf ve yönetim ücretlerini kıyasla."
            ],
            "prompt": "Orta risk profiline uygun üç farklı fon dağılımı öner ve aylık birikim planı çıkar."
        },
        "Altın/Döviz Riskleri": {
            "summary": "Altın ve döviz, kur ve küresel faktörlere duyarlı varlıklardır; kısa vadede oynaklık yüksektir.",
            "bullets": [
                "Kur riski ve jeopolitik riskler fiyatları etkiler.",
                "Merkez bankası adımları ve faizler önemli belirleyicidir.",
                "Uzun vadede portföye çeşitlendirme sağlar."
            ],
            "tips": [
                "Tek varlığa yoğunlaşma riskini azalt.",
                "Kademeli alım stratejisiyle fiyat dalgalanmasını yumuşat."
            ],
            "prompt": "Gelirimin yüzde kaçını altın/dövizde tutmalıyım? Risk iştahıma göre bir dağılım öner."
        },
    }

    # 2) Kategori seçimi
    category = st.selectbox("Konu seçin", list(FAQ_CONTENT.keys()))

    # 3) İçeriği göster
    data = FAQ_CONTENT[category]
    st.markdown(f"#### {category}")
    st.write(data["summary"])

    st.markdown("**Öne çıkan noktalar**")
    for b in data["bullets"]:
        st.markdown(f"- {b}")

    if data.get("tips"):
        st.markdown("**İpuçları**")
        for t in data["tips"]:
            st.markdown(f"- {t}")

    st.divider()

    # İstersen doğrudan burada da cevap üretebilirsin (RAG çalışsın)
    with st.expander("Bu sekmede hızlı cevap al (isteğe bağlı)"):
        if st.button("Bu kategori için açıklama üret"):
            if chatbot is None:
                st.error("Asistan şu anda çevrimdışı.")
            else:
                with st.spinner("Analiz ediliyor..."):
                    try:
                        raw = chatbot.ask(data["prompt"])
                    except Exception as e:
                        raw = {"text": f"Hata: {e}", "sources": []}

                    if isinstance(raw, str):
                        text, sources = raw, []
                    else:
                        text = raw.get("text") or raw.get("answer") or ""
                        sources = raw.get("sources") or raw.get("citations") or []

                    st.markdown(text)
                    if sources:
                        with st.expander("Kaynaklar"):
                            for s in sources:
                                st.markdown(f"- {s}")


with tab_tools:
    st.subheader("Hesaplama Araçları")
    colA, colB = st.columns(2)

    with colA:
        st.markdown("#### Borç Azaltma Basit Simülasyon")
        bakiye = st.number_input("Başlangıç borcu", min_value=0.0, value=20000.0, step=500.0)
        faiz = st.number_input("Aylık faiz (%)", min_value=0.0, value=2.5, step=0.1)
        odeme = st.number_input("Aylık ödeme", min_value=0.0, value=1500.0, step=100.0)
        if st.button("Hesapla", key="debt_calc"):
            if odeme <= bakiye * (faiz/100):
                st.error("Aylık ödeme faizden düşük; borç büyür. Ödemeyi artır.")
            else:
                import math
                r = faiz/100
                ay = math.log(odeme/(odeme - bakiye*r)) / math.log(1+r)
                st.success(f"Tahmini bitiş: {math.ceil(ay)} ay")

    with colB:
        st.markdown("#### Tasarruf Hedefi")
        hedef = st.number_input("Hedef tutar", min_value=0.0, value=60000.0, step=1000.0)
        aylik = st.number_input("Aylık birikim", min_value=0.0, value=2500.0, step=100.0)
        getiri = st.number_input("Aylık getiri (%)", min_value=0.0, value=0.6, step=0.1)
        if st.button("Planla", key="save_plan"):
            r = getiri/100
            ay = 0
            toplam = 0.0
            while toplam < hedef and ay < 1200:
                toplam = toplam*(1+r) + aylik
                ay += 1
            st.success(f"Hedefe ulaşma süresi: {ay} ay")