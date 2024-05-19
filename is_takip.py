import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3


class Veritabani:
    def __init__(self):
        self.conn = sqlite3.connect("proje_yonetim.db")
        self.cur = self.conn.cursor()
        self.tablo_olustur()

    def tablo_olustur(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS projeler (
                                id INTEGER PRIMARY KEY,
                                isim TEXT,
                                baslangic_tarihi TEXT,
                                bitis_tarihi TEXT,
                                ilerleme INTEGER DEFAULT 0
                            )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS gorevler (
                                id INTEGER PRIMARY KEY,
                                proje_id INTEGER,
                                isim TEXT,
                                sorumlu TEXT,
                                FOREIGN KEY(proje_id) REFERENCES projeler(id)
                            )""")
        self.conn.commit()

    def proje_ekle(self, isim, baslangic_tarihi, bitis_tarihi):
        self.cur.execute("INSERT INTO projeler (isim, baslangic_tarihi, bitis_tarihi) VALUES (?, ?, ?)",
                         (isim, baslangic_tarihi, bitis_tarihi))
        self.conn.commit()

    def projeleri_al(self):
        self.cur.execute("SELECT * FROM projeler")
        return self.cur.fetchall()

    def proje_al(self, proje_id):
        self.cur.execute("SELECT * FROM projeler WHERE id=?", (proje_id,))
        return self.cur.fetchone()

    def gorevleri_al(self, proje_id):
        self.cur.execute("SELECT * FROM gorevler WHERE proje_id=?", (proje_id,))
        return self.cur.fetchall()

    def gorev_ekle(self, proje_id, isim, sorumlu):
        self.cur.execute("INSERT INTO gorevler (proje_id, isim, sorumlu) VALUES (?, ?, ?)", (proje_id, isim, sorumlu))
        self.conn.commit()

    def proje_sil(self, proje_id):
        self.cur.execute("DELETE FROM gorevler WHERE proje_id=?", (proje_id,))
        self.cur.execute("DELETE FROM projeler WHERE id=?", (proje_id,))
        self.conn.commit()

    def gorev_sil(self, gorev_id):
        self.cur.execute("DELETE FROM gorevler WHERE id=?", (gorev_id,))
        self.conn.commit()

    def proje_ilerleme_guncelle(self, proje_id, ilerleme):
        self.cur.execute("UPDATE projeler SET ilerleme=? WHERE id=?", (ilerleme, proje_id))
        self.conn.commit()


class Proje:
    def __init__(self, id, isim, baslangic_tarihi, bitis_tarihi, ilerleme=0):
        self.id = id
        self.isim = isim
        self.baslangic_tarihi = baslangic_tarihi
        self.bitis_tarihi = bitis_tarihi
        self.ilerleme = ilerleme
        self.gorevler = []

    def gorev_ekle(self, gorev):
        self.gorevler.append(gorev)

    def ilerleme_kaydet(self, ilerleme):
        self.ilerleme = ilerleme


class Gorev:
    def __init__(self, id, proje_id, isim, sorumlu):
        self.id = id
        self.proje_id = proje_id
        self.isim = isim
        self.sorumlu = sorumlu


class Uygulama:
    def __init__(self, root):
        self.root = root
        self.root.title("İş Takip ve Yönetim Sistemi")

        self.veritabani = Veritabani()

        self.projeler = self.projeleri_yukle()

        self.ana_cerceve = tk.Frame(self.root)
        self.ana_cerceve.pack(padx=20, pady=20)

        self.proje_olustur_buton = tk.Button(self.ana_cerceve, text="Yeni Proje Oluştur", command=self.proje_olustur)
        self.proje_olustur_buton.grid(row=0, column=0, padx=10, pady=5)

        self.gorev_olustur_buton = tk.Button(self.ana_cerceve, text="Yeni Görev Ata", command=self.gorev_olustur)
        self.gorev_olustur_buton.grid(row=0, column=1, padx=10, pady=5)

        self.proje_sil_buton = tk.Button(self.ana_cerceve, text="Seçili Projeyi Sil", command=self.secili_proje_sil)
        self.proje_sil_buton.grid(row=0, column=2, padx=10, pady=5)
        self.kilavuz_buton = tk.Button(self.ana_cerceve, text="Kullanım Kılavuzu", command=self.goster_kilavuz)
        self.kilavuz_buton.grid(row=0, column=3, padx=10, pady=5)
        self.proje_cerceve = tk.Frame(self.ana_cerceve)
        self.proje_cerceve.grid(row=1, column=0, columnspan=4, padx=10, pady=10)




        self.projeleri_goster()


    def goster_kilavuz(self):
        kilavuz_metni = """
           KULLANIM KILAVUZU

           1. Yeni Proje Oluşturma:
           - 'Yeni Proje Oluştur' butonuna tıklayarak yeni bir proje oluşturabilirsiniz.
           - Açılan pencerede proje adı, başlangıç tarihi ve bitiş tarihi bilgilerini girerek 'Oluştur' butonuna basın.

           2. Yeni Görev Atama:
           - 'Yeni Görev Ata' butonuna tıklayarak projeye yeni bir görev atayabilirsiniz.
           - Açılan pencerede ilgili projeyi seçin, görev adını ve sorumlu kişiyi girin, sonra 'Ata' butonuna basın.

           3. Seçili Projeyi Silme:
           - 'Seçili Projeyi Sil' butonuna tıklayarak seçili projeyi ve tüm görevlerini silebilirsiniz.
           - Silme işlemi onaylandığında projenin ve görevlerinin kalıcı olarak silineceğine dikkat edin.

           Bu şekilde iş takip ve yönetim sistemi kullanımınızı daha verimli hale getirebilirsiniz.
           """

        messagebox.showinfo("Kullanım Kılavuzu", kilavuz_metni)
    def projeleri_yukle(self):
        projeler = []
        for proje_data in self.veritabani.projeleri_al():
            proje = Proje(*proje_data)
            proje_gorevler = self.veritabani.gorevleri_al(proje.id)
            for gorev_data in proje_gorevler:
                gorev = Gorev(*gorev_data)
                proje.gorev_ekle(gorev)
            projeler.append(proje)
        return projeler

    def proje_olustur(self):
        proje_penceresi = tk.Toplevel(self.root)
        proje_penceresi.title("Yeni Proje Oluştur")

        tk.Label(proje_penceresi, text="Proje Adı:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5,
                                                                                  sticky="w")
        self.proje_adi_giris = tk.Entry(proje_penceresi, font=("Helvetica", 12))
        self.proje_adi_giris.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(proje_penceresi, text="Başlangıç Tarihi:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10,
                                                                                         pady=5, sticky="w")
        self.baslangic_tarihi_giris = tk.Entry(proje_penceresi, font=("Helvetica", 12))
        self.baslangic_tarihi_giris.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(proje_penceresi, text="Bitiş Tarihi:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5,
                                                                                     sticky="w")
        self.bitis_tarihi_giris = tk.Entry(proje_penceresi, font=("Helvetica", 12))
        self.bitis_tarihi_giris.grid(row=2, column=1, padx=10, pady=5)

        olustur_buton = tk.Button(proje_penceresi, text="Oluştur", font=("Helvetica", 12), command=self.proje_kaydet)
        olustur_buton.grid(row=3, columnspan=2, pady=10)

    def proje_kaydet(self):
        isim = self.proje_adi_giris.get()
        baslangic_tarihi = self.baslangic_tarihi_giris.get()
        bitis_tarihi = self.bitis_tarihi_giris.get()

        if isim and baslangic_tarihi and bitis_tarihi:
            self.veritabani.proje_ekle(isim, baslangic_tarihi, bitis_tarihi)
            self.projeler = self.projeleri_yukle()
            self.projeleri_goster()
            messagebox.showinfo("Başarılı", "Proje başarıyla oluşturuldu.")
        else:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")

    def gorev_olustur(self):
        if not self.projeler:
            messagebox.showerror("Hata", "Önce bir proje oluşturun.")
            return

        gorev_penceresi = tk.Toplevel(self.root)
        gorev_penceresi.title("Yeni Görev Ata")

        tk.Label(gorev_penceresi, text="Proje Seçin:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5,
                                                                                    sticky="w")
        self.secili_proje = tk.StringVar(gorev_penceresi)
        self.secili_proje.set(self.projeler[0].isim)
        self.proje_acilir_menu = tk.OptionMenu(gorev_penceresi, self.secili_proje,
                                               *[proje.isim for proje in self.projeler])
        self.proje_acilir_menu.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(gorev_penceresi, text="Görev Adı:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5,
                                                                                  sticky="w")
        self.gorev_adi_giris = tk.Entry(gorev_penceresi, font=("Helvetica", 12))
        self.gorev_adi_giris.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(gorev_penceresi, text="Sorumlu Kişi:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5,
                                                                                     sticky="w")
        self.sorumlu_giris = tk.Entry(gorev_penceresi, font=("Helvetica", 12))
        self.sorumlu_giris.grid(row=2, column=1, padx=10, pady=5)

        ata_buton = tk.Button(gorev_penceresi, text="Ata", font=("Helvetica", 12), command=self.gorev_kaydet)
        ata_buton.grid(row=3, columnspan=2, pady=10)

    def gorev_kaydet(self):
        proje_adi = self.secili_proje.get()
        gorev_adi = self.gorev_adi_giris.get()
        sorumlu = self.sorumlu_giris.get()

        if gorev_adi and sorumlu:
            proje_id = [proje.id for proje in self.projeler if proje.isim == proje_adi][0]
            self.veritabani.gorev_ekle(proje_id, gorev_adi, sorumlu)
            self.projeler = self.projeleri_yukle()
            self.projeleri_goster()
            messagebox.showinfo("Başarılı", "Görev başarıyla atandı.")
        else:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")

    def secili_proje_sil(self):
        secili_proje_index = self.proje_listbox.curselection()
        if not secili_proje_index:
            messagebox.showerror("Hata", "Silmek için bir proje seçin.")
            return

        secili_proje_index = secili_proje_index[0]
        proje_adi = self.proje_listbox.get(secili_proje_index)
        proje_adi = proje_adi.split("-")[0].strip()
        proje_id = [proje.id for proje in self.projeler if proje.isim == proje_adi][0]

        onay = messagebox.askyesno("Uyarı", "Projeyi ve tüm görevlerini silmek istediğinizden emin misiniz?")
        if onay:
            self.veritabani.proje_sil(proje_id)
            self.projeler = self.projeleri_yukle()
            self.projeleri_goster()
            messagebox.showinfo("Başarılı", "Proje başarıyla silindi.")

    def gorev_sil(self):
        secili_proje_index = self.proje_listbox.curselection()
        if not secili_proje_index:
            messagebox.showerror("Hata", "Silmek için bir görev seçin.")
            return

        secili_proje_index = secili_proje_index[0]
        proje_adi = self.proje_listbox.get(secili_proje_index)
        proje_adi = proje_adi.split("-")[0].strip()
        proje_id = [proje.id for proje in self.projeler if proje.isim == proje_adi][0]
        secili_gorev_index = self.gorev_listbox.curselection()
        if not secili_gorev_index:
            messagebox.showerror("Hata", "Silmek için bir görev seçin.")
            return

        secili_gorev_index = secili_gorev_index[0]
        gorev_adi = self.gorev_listbox.get(secili_gorev_index)
        gorev_adi = gorev_adi.split(":")[1].strip().split("-")[0].strip()
        gorev_id = [gorev.id for gorev in self.veritabani.gorevleri_al(proje_id) if gorev[2] == gorev_adi][0]

        onay = messagebox.askyesno("Uyarı", "Görevi silmek istediğinizden emin misiniz?")
        if onay:
            self.veritabani.gorev_sil(gorev_id)
            self.projeler = self.projeleri_yukle()
            self.projeleri_goster()
            messagebox.showinfo("Başarılı", "Görev başarıyla silindi.")

    def projeleri_goster(self):
        for widget in self.proje_cerceve.winfo_children():
            widget.destroy()

        tk.Label(self.proje_cerceve, text="Projeler", font=("Helvetica", 14, "bold")).pack()

        self.proje_listbox = tk.Listbox(self.proje_cerceve, width=70, height=10)
        self.proje_listbox.pack(padx=10, pady=10)

        for proje in self.projeler:
            self.proje_listbox.insert(tk.END,
                                      f"    {proje.isim}    -   İlerleme: %{proje.ilerleme}")

        self.proje_listbox.bind("<<ListboxSelect>>", self.proje_gorevlerini_goster)

    def proje_gorevlerini_goster(self, event):
        secili_proje_index = self.proje_listbox.curselection()
        if not secili_proje_index:
            return

        secili_proje_index = secili_proje_index[0]
        proje_adi = self.proje_listbox.get(secili_proje_index)
        proje_adi = proje_adi.split("-")[0].strip()
        proje_id = [proje.id for proje in self.projeler if proje.isim == proje_adi][0]

        for widget in self.proje_cerceve.winfo_children():
            if widget != self.proje_listbox:
                widget.destroy()

        proje = [proje for proje in self.projeler if proje.id == proje_id][0]

        proje_cercevesi = tk.Frame(self.proje_cerceve, bd=2, relief=tk.GROOVE)
        proje_cercevesi.pack(padx=10, pady=5)

        proje_baslik_cercevesi = tk.Frame(proje_cercevesi)
        proje_baslik_cercevesi.pack(fill=tk.X, padx=5, pady=2)

        proje_adi_label = tk.Label(proje_baslik_cercevesi, text=f"Proje Adı: {proje.isim}",
                                   font=("Helvetica", 12, "bold italic"), anchor="w", width=30)
        proje_adi_label.pack(side=tk.LEFT)

        proje_duzenle_buton = tk.Button(proje_baslik_cercevesi, text="Düzenle", font=("Helvetica", 10),
                                        command=lambda p=proje_id: self.proje_duzenle(p))
        proje_duzenle_buton.pack(side=tk.RIGHT)

        tk.Label(proje_cercevesi,
                 text=f"Başlangıç Tarihi: {proje.baslangic_tarihi} \t|\t Bitiş Tarihi: {proje.bitis_tarihi}\n İlerleme: %{proje.ilerleme}",
                 font=("Helvetica", 10), anchor="w").pack(fill=tk.X, padx=5, pady=2, anchor='center')

        proje_ilerleme_buton = tk.Button(proje_cercevesi, text="İlerleme Kaydet", font=("Helvetica", 10),
                                         command=lambda p=proje_id: self.proje_ilerleme_kaydet(p))
        proje_ilerleme_buton.pack(pady=5, anchor='center')

        if proje.gorevler:
            gorev_cercevesi = tk.Frame(proje_cercevesi, bd=2, relief=tk.GROOVE)
            gorev_cercevesi.pack(padx=5, pady=2, fill=tk.X)

            tk.Label(gorev_cercevesi, text="Görevler:", font=("Helvetica", 10, "bold"), anchor="w").pack(fill=tk.X,
                                                                                                         padx=5, pady=2)

            self.gorev_listbox = tk.Listbox(gorev_cercevesi, width=70, height=5)
            self.gorev_listbox.pack(padx=10, pady=10)

            for gorev in proje.gorevler:
                self.gorev_listbox.insert(tk.END, f"Görev: {gorev.isim}  ~   Sorumlu: {gorev.sorumlu}")

            gorev_sil_buton = tk.Button(gorev_cercevesi, text="Seçili Görevi Sil", font=("Helvetica", 10),
                                        command=self.gorev_sil)
            gorev_sil_buton.pack(pady=5)

    def proje_ilerleme_kaydet(self, proje_id):
        proje = [proje for proje in self.projeler if proje.id == proje_id][0]
        yeni_ilerleme = simpledialog.askinteger("İlerleme Kaydet", "İlerleme yüzdesini girin:",
                                                initialvalue=proje.ilerleme, minvalue=0, maxvalue=100)

        if yeni_ilerleme is not None:
            self.veritabani.proje_ilerleme_guncelle(proje.id, yeni_ilerleme)
            proje.ilerleme = yeni_ilerleme
            self.projeleri_goster()
            messagebox.showinfo("Başarılı", "Proje ilerlemesi başarıyla kaydedildi.")

    def proje_duzenle(self, proje_id):
        proje = [proje for proje in self.projeler if proje.id == proje_id][0]

        proje_penceresi = tk.Toplevel(self.root)
        proje_penceresi.title("Proje Düzenle")

        tk.Label(proje_penceresi, text="Proje Adı:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5,
                                                                                  sticky="w")
        self.proje_adi_giris = tk.Entry(proje_penceresi, font=("Helvetica", 12))
        self.proje_adi_giris.grid(row=0, column=1, padx=10, pady=5)
        self.proje_adi_giris.insert(0, proje.isim)

        tk.Label(proje_penceresi, text="Başlangıç Tarihi:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10,
                                                                                         pady=5, sticky="w")
        self.baslangic_tarihi_giris = tk.Entry(proje_penceresi, font=("Helvetica", 12))
        self.baslangic_tarihi_giris.grid(row=1, column=1, padx=10, pady=5)
        self.baslangic_tarihi_giris.insert(0, proje.baslangic_tarihi)

        tk.Label(proje_penceresi, text="Bitiş Tarihi:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5,
                                                                                     sticky="w")
        self.bitis_tarihi_giris = tk.Entry(proje_penceresi, font=("Helvetica", 12))
        self.bitis_tarihi_giris.grid(row=2, column=1, padx=10, pady=5)
        self.bitis_tarihi_giris.insert(0, proje.bitis_tarihi)

        kaydet_buton = tk.Button(proje_penceresi, text="Kaydet", font=("Helvetica", 12),
                                 command=lambda: self.proje_guncelle(proje_id))
        kaydet_buton.grid(row=3, columnspan=2, pady=10)

    def proje_guncelle(self, proje_id):
        yeni_isim = self.proje_adi_giris.get()
        yeni_baslangic_tarihi = self.baslangic_tarihi_giris.get()
        yeni_bitis_tarihi = self.bitis_tarihi_giris.get()

        if yeni_isim and yeni_baslangic_tarihi and yeni_bitis_tarihi:
            self.veritabani.cur.execute("UPDATE projeler SET isim=?, baslangic_tarihi=?, bitis_tarihi=? WHERE id=?",
                                        (yeni_isim, yeni_baslangic_tarihi, yeni_bitis_tarihi, proje_id))
            self.veritabani.conn.commit()
            self.projeler = self.projeleri_yukle()
            self.projeleri_goster()
            messagebox.showinfo("Başarılı", "Proje başarıyla güncellendi.")
        else:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")


if __name__ == "__main__":
    root = tk.Tk()
    app = Uygulama(root)
    root.mainloop()
