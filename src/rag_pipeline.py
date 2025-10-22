from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.embeddings import HuggingFaceEmbeddings

# .env dosyasından API key yükle
load_dotenv()

class FinancialChatbot:
    def __init__(self, data_path='data/all_qa_data.json'):
        """RAG tabanlı finansal chatbot"""
        print(" Chatbot başlatılıyor...")
        
        # API key kontrolü
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("❌ GOOGLE_API_KEY bulunamadı! .env dosyasını kontrol edin.")
        
        # Veriyi yükle
        print(" Veri yükleniyor...")
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f" {len(self.data)} veri yüklendi")
        
        # Dökümanları hazırla
        print(" Dökümanlar hazırlanıyor...")
        documents = []
        for item in self.data:
            doc_text = f"Soru: {item['question']}\n\nCevap: {item['answer']}\n\nKategori: {item['category']}"
            documents.append(doc_text)
        
        # Embeddings oluştur
        print(" Embeddings oluşturuluyor...")
        from langchain.embeddings import HuggingFaceEmbeddings
        self.embeddings = HuggingFaceEmbeddings(
           model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # FAISS vector store oluştur
        print(" Vector database oluşturuluyor...")
        self.vectorstore = FAISS.from_texts(documents, self.embeddings)
        print(" Vector database hazır!")
        

        # LLM başlat
        self.llm = GoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Custom prompt template
        template = """Sen Akbank'ın yapay zeka destekli finansal asistanısın. Kullanıcılara finansal okur yazarlık konusunda yardımcı oluyorsun ve bankacılık sorunlarına çözüm üretiyorsun.

Aşağıdaki bilgileri kullanarak soruyu Türkçe olarak yanıtla:

{context}

Soru: {question}

Yanıt kuralları:
- Nazik ve profesyonel ol
- Açık ve anlaşılır açıkla
- Türkçe yanıt ver
- Bilmiyorsan "Bu konuda kesin bilgim yok" de
- Finansal tavsiye verirken dikkatli ol

Yanıt:"""

        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # RAG chain oluştur
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}  # En yakın 3 döküman
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        print(" Chatbot hazır! Sorularınızı sorabilirsiniz.\n")
    
    def ask(self, question):
        """Soru sor ve cevap al"""
        try:
            result = self.qa_chain({"query": question})
            return result['result']
        except Exception as e:
            return f" Hata oluştu: {str(e)}"
    
    def chat(self):
        """Terminal'de sohbet et"""
        print(" Chatbot başlatıldı! Çıkmak için 'exit' yazın.\n")
        
        while True:
            question = input("👤 Siz: ")
            
            if question.lower() in ['exit', 'çıkış', 'quit']:
                print("👋 Görüşmek üzere!")
                break
            
            if not question.strip():
                continue
            
            print("🤖 Asistan: ", end="")
            answer = self.ask(question)
            print(answer)
            print()

# Test fonksiyonu
def test_chatbot():
    """Chatbot'u test et"""
    bot = FinancialChatbot()
    
    test_questions = [
        "Bütçe nasıl yapılır?",
        "Kredi kartı borcu nasıl ödenir?",
        "Hesap açmak istiyorum"
    ]
    
    print(" Test soruları çalıştırılıyor...\n")
    for q in test_questions:
        print(f" Soru: {q}")
        print(f" Cevap: {bot.ask(q)}\n")
        print("-" * 80 + "\n")

if __name__ == "__main__":
    # Chatbot'u başlat ve terminal'de konuş
    bot = FinancialChatbot()
    bot.chat()