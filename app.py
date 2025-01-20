import datetime
import pandas as pd
import streamlit as st

# Load dataset dari file CSV
mobil_df = pd.read_csv('https://raw.githubusercontent.com/Meisterbogen21/python8/refs/heads/main/mobil_data_spesifik.csv')
penyewa_df = pd.read_csv('https://raw.githubusercontent.com/Meisterbogen21/python8/refs/heads/main/penyewa_data_spesifik.csv')

# Fungsi untuk menambahkan penyewa baru
def tambah_penyewa(id_penyewa, nama_penyewa, nomor_ktp, nomor_hp, nomor_sim, id_mobil, durasi):
    global mobil_df, penyewa_df

    # Cari mobil berdasarkan ID
    mobil = mobil_df.loc[mobil_df['id_mobil'] == id_mobil]
    if mobil.empty:
        st.error("Mobil tidak ditemukan.")
        return

    if mobil.iloc[0]['status'] != "Tersedia":
        st.error("Mobil sedang tidak tersedia.")
        return

    tanggal_sewa = datetime.date.today()
    tanggal_kembali = tanggal_sewa + datetime.timedelta(days=durasi)
    harga_total = mobil.iloc[0]['harga_dasar'] * durasi

    penyewa_baru = {
        "id_penyewa": id_penyewa,
        "nama_penyewa": nama_penyewa,
        "nomor_ktp": nomor_ktp,
        "nomor_hp": nomor_hp,
        "nomor_sim": nomor_sim,
        "nama_mobil": mobil.iloc[0]['nama_mobil'],
        "merek_mobil": mobil.iloc[0]['merek_mobil'],
        "tipe_mobil": mobil.iloc[0]['tipe_mobil'],
        "transmisi_mobil": mobil.iloc[0]['transmisi'],
        "jumlah_penumpang": mobil.iloc[0]['jumlah_penumpang'],
        "tanggal_mulai": tanggal_sewa,
        "tanggal_kembali": tanggal_kembali,
        "harga_total": harga_total
    }

    # Tambahkan penyewa baru ke DataFrame
    penyewa_df = pd.concat([penyewa_df, pd.DataFrame([penyewa_baru])], ignore_index=True)

    # Update status mobil menjadi "Disewa"
    mobil_df.loc[mobil_df['id_mobil'] == id_mobil, 'status'] = "Disewa"

    st.success(f"Penyewa {nama_penyewa} berhasil ditambahkan dengan total harga Rp {harga_total}.")

# Fungsi untuk menampilkan daftar mobil
def tampilkan_mobil():
    st.subheader("Daftar Mobil")
    st.dataframe(mobil_df)

# Fungsi untuk menampilkan daftar penyewa
def tampilkan_penyewa():
    st.subheader("Daftar Penyewa")
    st.dataframe(penyewa_df)

# Fungsi untuk mencari mobil berdasarkan nama atau tipe
def cari_mobil(kata_kunci):
    hasil = mobil_df[(mobil_df['nama_mobil'].str.contains(kata_kunci, case=False)) | (mobil_df['tipe_mobil'].str.contains(kata_kunci, case=False))]
    if hasil.empty:
        st.error("Tidak ada mobil yang cocok dengan kata kunci tersebut.")
    else:
        st.subheader("Hasil Pencarian Mobil")
        st.dataframe(hasil)

# Fungsi untuk mencari penyewa berdasarkan nama atau ID
def cari_penyewa(kata_kunci):
    hasil = penyewa_df[(penyewa_df['nama_penyewa'].str.contains(kata_kunci, case=False)) | (penyewa_df['id_penyewa'].str.contains(kata_kunci, case=False))]
    if hasil.empty:
        st.error("Tidak ada penyewa yang cocok dengan kata kunci tersebut.")
    else:
        st.subheader("Hasil Pencarian Penyewa")
        st.dataframe(hasil)

# Fungsi untuk mengembalikan mobil
def kembalikan_mobil(id_penyewa):
    global mobil_df, penyewa_df

    penyewa = penyewa_df.loc[penyewa_df['id_penyewa'] == id_penyewa]
    if penyewa.empty:
        st.error("Penyewa tidak ditemukan.")
        return

    id_mobil = mobil_df.loc[mobil_df['nama_mobil'] == penyewa.iloc[0]['nama_mobil'], 'id_mobil'].values[0]
    mobil_df.loc[mobil_df['id_mobil'] == id_mobil, 'status'] = "Tersedia"

    penyewa_df = penyewa_df[penyewa_df['id_penyewa'] != id_penyewa]
    st.success("Mobil berhasil dikembalikan.")

# Fungsi untuk mengganti mobil jika mobil mengalami kerusakan
def ganti_mobil(id_penyewa):
    global mobil_df, penyewa_df

    # Cari data penyewa berdasarkan ID
    penyewa = penyewa_df.loc[penyewa_df['id_penyewa'] == id_penyewa]
    if penyewa.empty:
        st.error("Penyewa tidak ditemukan.")
        return

    tipe_mobil = penyewa.iloc[0]['tipe_mobil']
    mobil_tersedia = mobil_df[(mobil_df['tipe_mobil'] == tipe_mobil) & (mobil_df['status'] == "Tersedia")]

    if mobil_tersedia.empty:
        st.error("Tidak ada mobil pengganti yang tersedia untuk tipe ini.")
        return

    st.subheader("Daftar Mobil Pengganti yang Tersedia")
    st.dataframe(mobil_tersedia[['id_mobil', 'nama_mobil', 'merek_mobil']])

    id_mobil_baru = st.selectbox("Pilih ID Mobil Pengganti", mobil_tersedia['id_mobil'].tolist())

    # Update data penyewa dengan mobil baru
    mobil_baru = mobil_tersedia[mobil_tersedia['id_mobil'] == id_mobil_baru]
    penyewa_df.loc[penyewa_df['id_penyewa'] == id_penyewa, 'nama_mobil'] = mobil_baru.iloc[0]['nama_mobil']
    penyewa_df.loc[penyewa_df['id_penyewa'] == id_penyewa, 'merek_mobil'] = mobil_baru.iloc[0]['merek_mobil']
    penyewa_df.loc[penyewa_df['id_penyewa'] == id_penyewa, 'transmisi_mobil'] = mobil_baru.iloc[0]['transmisi']
    penyewa_df.loc[penyewa_df['id_penyewa'] == id_penyewa, 'jumlah_penumpang'] = mobil_baru.iloc[0]['jumlah_penumpang']

    # Update status mobil lama menjadi "Rusak"
    mobil_df.loc[mobil_df['nama_mobil'] == penyewa.iloc[0]['nama_mobil'], 'status'] = "Rusak"

    # Update status mobil baru menjadi "Disewa"
    mobil_df.loc[mobil_df['id_mobil'] == mobil_baru.iloc[0]['id_mobil'], 'status'] = "Disewa"

    st.success(f"Mobil penyewa dengan ID {id_penyewa} telah diganti dengan mobil {mobil_baru.iloc[0]['nama_mobil']}.")

# Aplikasi Streamlit
def main():
    st.title("Sistem Pendataan Sewa Mobil")

    menu = ["Tampilkan Mobil", "Tampilkan Penyewa", "Tambah Penyewa", "Kembalikan Mobil", "Ganti Mobil", "Cari Mobil", "Cari Penyewa"]
    pilihan = st.sidebar.selectbox("Menu", menu)

    if pilihan == "Tampilkan Mobil":
        tampilkan_mobil()
    elif pilihan == "Tampilkan Penyewa":
        tampilkan_penyewa()
    elif pilihan == "Tambah Penyewa":
        st.subheader("Tambah Penyewa")
        id_penyewa = st.text_input("Masukkan ID Penyewa")
        nama_penyewa = st.text_input("Masukkan Nama Penyewa")
        nomor_ktp = st.text_input("Masukkan Nomor KTP")
        nomor_hp = st.text_input("Masukkan Nomor HP")
        nomor_sim = st.text_input("Masukkan Nomor SIM")
        id_mobil = st.text_input("Masukkan ID Mobil yang Disewa")
        durasi = st.number_input("Masukkan Durasi Sewa (hari)", min_value=1, step=1)
        if st.button("Tambah Penyewa"):
            tambah_penyewa(id_penyewa, nama_penyewa, nomor_ktp, nomor_hp, nomor_sim, id_mobil, durasi)
    elif pilihan == "Kembalikan Mobil":
        st.subheader("Kembalikan Mobil")
        id_penyewa = st.text_input("Masukkan ID Penyewa")
        if st.button("Kembalikan Mobil"):
            kembalikan_mobil(id_penyewa)
    elif pilihan == "Ganti Mobil":
        st.subheader("Ganti Mobil Penyewa")
        id_penyewa = st.text_input("Masukkan ID Penyewa")
        if st.button("Ganti Mobil"):
            ganti_mobil(id_penyewa)
    elif pilihan == "Cari Mobil":
        st.subheader("Cari Mobil")
        kata_kunci = st.text_input("Masukkan Nama atau Tipe Mobil")
        if st.button("Cari"):
            cari_mobil(kata_kunci)
    elif pilihan == "Cari Penyewa":
        st.subheader("Cari Penyewa")
        kata_kunci = st.text_input("Masukkan Nama Penyewa atau ID Penyewa")
        if st.button("Cari"):
            cari_penyewa(kata_kunci)

if __name__ == "__main__":
    main()

