import tkinter as tk
from tkinter import scrolledtext, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import webbrowser

# Configuration de l'application
class WebAnalyzerPro:
    def __init__(self, master):
        self.master = master
        self.master.title("WebAnalyzer Pro")
        self.master.geometry("800x650")
        self.last_json_file = None
        self.setup_ui()
        
        # Style personnalisé
        self.style = ttk.Style()
        self.style.configure('success.TButton', font=('Helvetica', 10, 'bold'))
        self.style.configure('info.TButton', font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Helvetica', 9))
        self.style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principale
        self.main_frame = ttk.Frame(self.master, padding=10)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Header avec logo et titre
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            self.header_frame, 
            text="🌐", 
            font=('Helvetica', 20), 
            bootstyle=PRIMARY
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk.Label(
            self.header_frame, 
            text="WEBANALYZER PRO", 
            style='Title.TLabel', 
            bootstyle=PRIMARY
        ).pack(side=LEFT)
        
        ttk.Label(
            self.header_frame, 
            text="Analyse professionnelle de sites web", 
            bootstyle=SECONDARY
        ).pack(side=LEFT, padx=(10, 0))

        # Section de saisie URL
        self.url_frame = ttk.Labelframe(
            self.main_frame, 
            text=" URL à analyser ", 
            padding=10,
            bootstyle=INFO
        )
        self.url_frame.pack(fill=X, pady=(0, 15))
        
        self.url_entry = ttk.Entry(
            self.url_frame, 
            font=('Consolas', 10)
        )
        self.url_entry.pack(fill=X, ipady=5)
        self.url_entry.insert(0, "https://")

        # Boutons d'action
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=X, pady=(0, 15))
        
        self.analyze_btn = ttk.Button(
            self.buttons_frame,
            text="Lancer l'analyse",
            command=self.launch_analysis,
            style='success.TButton',
            width=15
        )
        self.analyze_btn.pack(side=LEFT, padx=(0, 10))
        
        self.open_btn = ttk.Button(
            self.buttons_frame,
            text="Ouvrir le rapport",
            command=self.open_report,
            style='info.TButton',
            width=15
        )
        self.open_btn.pack(side=LEFT)

        # Barre de statut et progression
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=X, pady=(0, 15))
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Prêt à analyser",
            bootstyle=SECONDARY
        )
        self.status_label.pack(side=LEFT, anchor=W)
        
        self.progress = ttk.Progressbar(
            self.status_frame,
            orient=HORIZONTAL,
            mode='indeterminate',
            length=200,
            bootstyle=(STRIPED, PRIMARY)
        )
        self.progress.pack(side=RIGHT, anchor=E)

        # Zone de résultats
        self.results_frame = ttk.Labelframe(
            self.main_frame, 
            text=" Résultats de l'analyse ", 
            padding=10,
            bootstyle=INFO
        )
        self.results_frame.pack(fill=BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            wrap=WORD,
            font=('Consolas', 9),
            padx=5,
            pady=5,
            height=20
        )
        self.results_text.pack(fill=BOTH, expand=True)

    def launch_analysis(self):
        """Lance l'analyse du site web"""
        url = self.url_entry.get().strip()
        
        if not url or url == "https://":
            messagebox.showwarning("URL requise", "Veuillez saisir une URL valide.")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
            
        self.results_text.delete(1.0, END)
        self.status_label.config(text="Analyse en cours...", bootstyle=WARNING)
        self.progress.start()
        
        try:
            self.analyze_website(url)
        except Exception as e:
            self.status_label.config(text=f"Erreur: {str(e)}", bootstyle=DANGER)
            self.progress.stop()
            messagebox.showerror("Erreur", f"Une erreur est survenue:\n{str(e)}")

    def analyze_website(self, url):
        """Analyse le contenu du site web"""
        self.log(f"🌐 Connexion à: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        self.log(f"✅ Connexion réussie (Code: {response.status_code})")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        self.log("🔍 Analyse du contenu...\n")
        
        data = {
            "url": url,
            "date": datetime.now().isoformat(),
            "titres": [],
            "paragraphes": [],
            "liens": [],
            "images": [],
            "metadonnees": [],
            "scripts": []
        }

        # Analyse des sections
        sections = [
            ("Titres", soup.find_all(['h1', 'h2', 'h3'])),
            ("Paragraphes", soup.find_all('p')),
            ("Liens", soup.find_all('a', href=True)),
            ("Images", soup.find_all('img', src=True)),
            ("Métadonnées", soup.find_all('meta')),
            ("Scripts", soup.find_all('script'))
        ]

        for name, elements in sections:
            count = len(elements)
            data[name.lower()] = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
            self.log(f"▸ {name}: {count} éléments trouvés")

        # Sauvegarde des résultats
        filename = f"WebAnalyzer_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        self.last_json_file = filename
        self.log(f"\n📊 Analyse terminée en {response.elapsed.total_seconds():.2f}s")
        self.log(f"💾 Rapport sauvegardé: {filename}")
        self.status_label.config(text="Analyse terminée avec succès", bootstyle=SUCCESS)
        self.progress.stop()

    def open_report(self):
        """Ouvre le dernier rapport généré"""
        if self.last_json_file and os.path.exists(self.last_json_file):
            webbrowser.open(self.last_json_file)
        else:
            messagebox.showinfo("Aucun rapport", "Veuillez d'abord effectuer une analyse.")

    def log(self, message):
        """Ajoute un message au journal de résultats"""
        self.results_text.insert(END, message + "\n")
        self.results_text.see(END)

# Lancement de l'application
if __name__ == "__main__":
    app = ttk.Window(
        themename="superhero",  # Thème élégant - autres options: 'cosmo', 'flatly', 'journal', etc.
        title="WebAnalyzer Pro",
        iconphoto="logo.jpg",  # Ajoutez le chemin vers votre icône
        size=(800, 650),
        resizable=(True, True))
    
    WebAnalyzerPro(app)
    app.mainloop()