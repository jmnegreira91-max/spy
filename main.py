from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import yfinance as yf
import matplotlib.pyplot as plt
import io

class SPYMonitorPro(App):
    def build(self):
        # Layout Principal Oscuro
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
       
        # 1. Gráfico Automático
        self.img_grafico = Image(source='', allow_stretch=True, size_hint=(1, 0.6))
       
        # 2. Caja de Alerta (Cambiará de color cuando haya entrada)
        self.alerta_bg = BoxLayout(orientation='vertical', size_hint=(1, 0.4), padding=10)
        self.lbl_veredicto = Label(
            text="[ BUSCANDO ENTRADA... ]",
            font_size='22sp', bold=True, halign='center'
        )
        self.lbl_datos = Label(
            text="Conectando con SPY...",
            font_size='16sp', halign='center'
        )
       
        self.alerta_bg.add_widget(self.lbl_veredicto)
        self.alerta_bg.add_widget(self.lbl_datos)
       
        self.layout.add_widget(self.img_grafico)
        self.layout.add_widget(self.alerta_bg)
       
        # Actualización automática cada 30 segundos
        Clock.schedule_interval(self.analisis_automatico, 30)
        self.analisis_automatico(0)
       
        return self.layout

    def analisis_automatico(self, dt):
        try:
            # Obtener datos del SPY (2 de abril de 2026)
            spy = yf.Ticker("SPY")
            df = spy.history(period="1d", interval="5m")
            precio_actual = df['Close'].iloc[-1]
            media_20 = df['Close'].rolling(window=20).mean().iloc[-1]
           
            # --- LÓGICA DE DETECCIÓN DE ENTRADA ---
            # Una "buena entrada" aquí es cuando el precio cruza su promedio
            distancia_otm = 0.015 # 1.5% OTM
           
            if precio_actual > media_20:
                tipo = "CALL"
                strike = round(precio_actual * (1 + distancia_otm))
                color_alerta = get_color_from_hex('#00FF41') # Verde Neón
                texto_veredicto = f"🟢 ENTRADA {tipo} DETECTADA"
            else:
                tipo = "PUT"
                strike = round(precio_actual * (1 - distancia_otm))
                color_alerta = get_color_from_hex('#FF3131') # Rojo Neón
                texto_veredicto = f"🔴 ENTRADA {tipo} DETECTADA"

            # --- ACTUALIZACIÓN DE INTERFAZ ---
            self.lbl_veredicto.text = texto_veredicto
            self.lbl_datos.text = (
                f"Precio SPY: ${precio_actual:.2f}\n"
                f"STRIKE OTM SUGERIDO: ${strike}\n"
                f"Vencimiento: +3 Días (Conservador)"
            )
           
            # Dibujar gráfico
            plt.figure(figsize=(6, 4))
            plt.style.use('dark_background')
            plt.plot(df['Close'], color='#00E5FF', linewidth=2)
            plt.title(f"SPY Intradía")
           
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            with open("live_chart.png", "wb") as f: f.write(buf.read())
           
            self.img_grafico.source = "live_chart.png"
            self.img_grafico.reload()
           
        except Exception as e:
            self.lbl_datos.text = "Error de conexión..."

if __name__ == "__main__":
    SPYMonitorPro().run()