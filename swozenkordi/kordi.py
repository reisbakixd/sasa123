import discord
from discord.ext import commands
import json
import os

# Discord botunun token'ını burada tanımlayın
TOKEN = 'MTMwMzYyNDAxMjI1MzEwMjA5MA.GTlaT7.HV10JpfbjRy2JRPrGID2ou1oGatRItid26tqkY'

# Botun intents'lerini tanımlıyoruz
intents = discord.Intents.default()
intents.message_content = True  # Mesaj içeriğine erişim izni veriyoruz

# Botu oluşturma
bot = commands.Bot(command_prefix='.', intents=intents)

# Hesapları saklayacağımız JSON dosyasının adı
HESAP_DOSYASI = 'hesaplar.json'

# Hesapları yükleme
def hesaplari_yukle():
    if os.path.exists(HESAP_DOSYASI):
        with open(HESAP_DOSYASI, 'r') as f:
            return json.load(f)
    return []

# Hesapları kaydetme
def hesaplari_kaydet():
    with open(HESAP_DOSYASI, 'w') as f:
        json.dump(hesap_listesi, f, ensure_ascii=False, indent=4)

# Hesapları tutacak bir liste
hesap_listesi = hesaplari_yukle()

# Komutların çalışacağı kanalın ID'si
KANAL_ID = 1275843669819134023  # Buraya komutların çalışmasını istediğiniz kanalın ID'sini girin

# .kordiekle komutu - Hesap ekleme işlemi
@bot.command()
async def kordiekle(ctx, hesap_adi: str = None, sifre: str = None, dunya: str = None, x: float = None, y: float = None, z: float = None):
    if ctx.channel.id != KANAL_ID:
        await ctx.send("⚠️ Bu komutu yalnızca belirli bir kanalda kullanabilirsiniz.")
        return

    if None in [hesap_adi, sifre, dunya, x, y, z]:
        await ctx.send(
            "⚠️ **Eksik Bilgi!** Lütfen komutu şu şekilde kullanın:\n"
            "`.kordiekle [hesap adı] [şifre] [dünya] [X] [Y] [Z]`\n\n"
            "**Örnek:** `.kordiekle MyAccount P@ssw0rd Dünya1 100 64 300`"
        )
        return
    
    hesap_listesi.append({
        "kullanici_adi": hesap_adi,
        "sifre": sifre,
        "dunya": dunya,
        "koordinatlar": (x, y, z)
    })
    hesaplari_kaydet()  # Hesapları JSON dosyasına kaydediyoruz
    await ctx.send(f"✅ **{hesap_adi}** adlı hesap başarıyla eklendi!")

# İki koordinat arasındaki Manhattan mesafesini (X ve Z farklarının toplamını) hesaplayan fonksiyon
def mesafe_hesapla(x1, z1, x2, z2):
    return abs(x2 - x1) + abs(z2 - z1)

# .kordi komutu - En yakın hesabı arama işlemi (Y eksenini dikkate almadan)
@bot.command()
async def kordi(ctx, dunya: str = None, x: float = None, z: float = None):
    if ctx.channel.id != KANAL_ID:
        await ctx.send("⚠️ Bu komutu yalnızca belirli bir kanalda kullanabilirsiniz.")
        return

    if None in [dunya, x, z]:
        await ctx.send(
            "⚠️ **Eksik Bilgi!** Lütfen komutu şu şekilde kullanın:\n"
            "`.kordi [dünya] [X] [Z]`\n\n"
            "**Örnek:** `.kordi Dünya1 100 300`"
        )
        return

    uygun_hesaplar = [hesap for hesap in hesap_listesi if hesap['dunya'] == dunya]
    
    if not uygun_hesaplar:
        await ctx.send("🔍 **Bu dünya için uygun bir hesap bulunamadı.**")
        return

    en_yakin = min(uygun_hesaplar, key=lambda hesap: mesafe_hesapla(x, z, hesap['koordinatlar'][0], hesap['koordinatlar'][2]))
    mesafe = mesafe_hesapla(x, z, en_yakin['koordinatlar'][0], en_yakin['koordinatlar'][2])
    
    await ctx.send(
        f"🔑 **En yakın hesap bulundu!**\n\n"
        f"**Kullanıcı Adı:** `{en_yakin['kullanici_adi']}`\n"
        f"**Şifre:** `{en_yakin['sifre']}`\n"
        f"**Dünya:** `{en_yakin['dunya']}`\n"
        f"**Koordinatlar:** `X: {en_yakin['koordinatlar'][0]}, Y: {en_yakin['koordinatlar'][1]}, Z: {en_yakin['koordinatlar'][2]}` (Yaklaşık {mesafe:.2f} blok uzaklıkta)"
    )

# .kordisil komutu - Hesap silme işlemi
@bot.command()
async def kordisil(ctx, hesap_adi: str = None):
    if ctx.channel.id != KANAL_ID:
        await ctx.send("⚠️ Bu komutu yalnızca belirli bir kanalda kullanabilirsiniz.")
        return

    if hesap_adi is None:
        await ctx.send(
            "⚠️ **Eksik Bilgi!** Lütfen komutu şu şekilde kullanın:\n"
            "`.kordisil [hesap adı]`\n\n"
            "**Örnek:** `.kordisil MyAccount`"
        )
        return
    
    global hesap_listesi
    hesap_listesi = [hesap for hesap in hesap_listesi if hesap['kullanici_adi'] != hesap_adi]

    hesaplari_kaydet()  # Güncellenen hesapları JSON dosyasına kaydediyoruz
    await ctx.send(f"🗑️ **{hesap_adi}** adlı hesap başarıyla silindi!")

@bot.command(name='hesaplar')
async def hesap_listesi_komutu(ctx):
    if ctx.channel.id != KANAL_ID:
        await ctx.send("⚠️ Bu komutu yalnızca belirli bir kanalda kullanabilirsiniz.")
        return

    if not hesap_listesi:
        embed = discord.Embed(
            title="Kayıtlı Hesaplar",
            description="📂 **Kayıtlı hesap bulunmamaktadır.**",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Kullanıcı adlarını ve şifreleri toplayalım ve tekrar edenleri filtreleyelim
    tekil_hesaplar = {}
    for hesap in hesap_listesi:
        if hesap['kullanici_adi'] not in tekil_hesaplar:
            tekil_hesaplar[hesap['kullanici_adi']] = hesap['sifre']

    # Embed oluşturma
    embed = discord.Embed(
        title="Kayıtlı Hesaplar",
        description="Aşağıda kayıtlı hesapların listesi bulunmaktadır.",
        color=discord.Color.blue()
    )

    # Kullanıcı adı ve şifreleri embed'e ekleyelim
    for kullanici_adi, sifre in tekil_hesaplar.items():
        embed.add_field(
            name=kullanici_adi,
            value=f"**Şifre:** `{sifre}`",
            inline=False
        )

    # Embed tamamlandığında gönder
    await ctx.send(embed=embed)

# Botu çalıştırma
bot.run(TOKEN)
