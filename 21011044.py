import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QMessageBox,
)

class SignalInputWidget(QWidget):
    """Widget for inputting A, f, theta for a single signal."""
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        layout = QGridLayout()
        layout.addWidget(QLabel(f"Sinyal {index}"), 0, 0, 1, 2)
        layout.addWidget(QLabel("A:"), 1, 0)
        self.amp_spin = QDoubleSpinBox(); self.amp_spin.setRange(-1000,1000); self.amp_spin.setValue(1)
        layout.addWidget(self.amp_spin,1,1)
        layout.addWidget(QLabel("f (Hz):"),2,0)
        self.freq_spin=QDoubleSpinBox(); self.freq_spin.setRange(0,1000); self.freq_spin.setValue(1)
        layout.addWidget(self.freq_spin,2,1)
        layout.addWidget(QLabel("θ (rad):"),3,0)
        self.phase_spin=QDoubleSpinBox(); self.phase_spin.setRange(-3.1416,3.1416); self.phase_spin.setSingleStep(0.1)
        self.phase_spin.setValue(0)
        layout.addWidget(self.phase_spin,3,1)
        self.setLayout(layout)

    def get_parameters(self):
        return dict(A=self.amp_spin.value(), f=self.freq_spin.value(), theta=self.phase_spin.value())

class FourierInputWidget(QWidget):
    """Widget for Fourier series coefficients and parameters"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        labels = ["a0/2","a1","a2","a3","b1","b2","b3","ω0 (rad/s)","T (s)"]
        self.spins = []
        for i,label in enumerate(labels):
            layout.addWidget(QLabel(label+":"), i, 0)
            spin = QDoubleSpinBox(); spin.setRange(-1000,1000); spin.setValue(0)
            if label in ["ω0 (rad/s)","T (s)"]: spin.setValue(1)
            layout.addWidget(spin, i, 1)
            self.spins.append(spin)
        self.setLayout(layout)

    def get_parameters(self):
        keys = ["a0","a1","a2","a3","b1","b2","b3","omega0","T"]
        vals = [s.value() for s in self.spins]
        params = dict(zip(keys, vals))
        params['a0'] *= 2  # a0 input was half
        return params

    def set_parameters(self, coeffs):
        # coeffs: dict with a0,a1..b3, omega0,T
        self.spins[0].setValue(coeffs.get('a0',0)/2)
        for i in range(1,4):
            self.spins[i].setValue(coeffs.get(f'a{i}',0))
            self.spins[3+i].setValue(coeffs.get(f'b{i}',0))
        self.spins[7].setValue(coeffs.get('omega0',1))
        self.spins[8].setValue(coeffs.get('T',1))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sinüs/Cos ve Fourier Serisi Çizici")

        central = QWidget()
        main_layout = QVBoxLayout()

        # Sinüs/Cos input
        self.signal_inputs = [SignalInputWidget(i) for i in range(1,4)]
        for w in self.signal_inputs:
            main_layout.addWidget(w)
        sincos_btn = QPushButton("Sin/Cos Grafiklerini Göster")
        sincos_btn.clicked.connect(self.show_sincos_window)
        main_layout.addWidget(sincos_btn)

        # Fourier input
        self.fourier_widget = FourierInputWidget()
        main_layout.addWidget(self.fourier_widget)
        fourier_btn = QPushButton("Fourier Serisi Grafiğini Göster")
        fourier_btn.clicked.connect(self.show_fourier_window)
        main_layout.addWidget(fourier_btn)

        # Analysis button
        analyze_btn = QPushButton("Periyodik İşareti Analiz Et")
        analyze_btn.clicked.connect(self.analyze_signal)
        main_layout.addWidget(analyze_btn)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def show_sincos_window(self):
        t = np.linspace(0,1,1000)
        fig, axes = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(6,10))
        y_sum = np.zeros_like(t)
        for ax, widget, idx in zip(axes[:3], self.signal_inputs, range(1,4)):
            p = widget.get_parameters()
            y_sin = p['A'] * np.sin(2*np.pi*p['f']*t + p['theta'])
            y_cos = p['A'] * np.cos(2*np.pi*p['f']*t + p['theta'])
            y_sum += y_sin + y_cos
            ax.plot(t, y_sin, label=f"S{idx} (sin)")
            ax.plot(t, y_cos, linestyle='--', label=f"C{idx} (cos)")
            ax.set_ylabel("Genlik")
            ax.set_title(f"Sinyal {idx}: A={p['A']}, f={p['f']} Hz, θ={p['theta']} rad")
            ax.legend(); ax.grid(True)
        # Sentez sinyal
        ax_sum = axes[3]
        ax_sum.plot(t, y_sum, color='k', label="Sentez Sinyal")
        ax_sum.set_title("Sentez Sinyal (Toplam)")
        ax_sum.set_ylabel("Genlik")
        ax_sum.set_xlabel("t (s)")
        ax_sum.legend(); ax_sum.grid(True)

        fig.suptitle("Sinüs, Cosinüs ve Sentez Sinyalleri")
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def show_fourier_window(self):
        params = self.fourier_widget.get_parameters()
        T = params['T']; omega0 = params['omega0']
        t = np.linspace(0, T, 1000)
        x = params['a0']/2 * np.ones_like(t)
        for k in range(1,4):
            x += params[f'a{k}']*np.cos(k*omega0*t) + params[f'b{k}']*np.sin(k*omega0*t)
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(t, x, label="Fourier Serisi")
        ax.set_title("Fourier Serisi ile Yeniden Oluşturma")
        ax.set_xlabel("t (s)"); ax.set_ylabel("x(t)"); ax.grid(True)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def analyze_signal(self):
        # Set Fourier coefficients from provided table for periodic signal
        coeffs = {
            'a0': 0.0,
            'a1': 0.8106,
            'a2': 0.0,
            'a3': 0.0901,
            'a4': 0.0,
            'a5': 0.0324,
            'a6': 0.0,
            'a7': 0.0165,
            'b1': 0.0,
            'b2': 0.0,
            'b3': 0.0,
            'b4': 0.0,
            'b5': 0.0,
            'b6': 0.0,
            'b7': 0.0,
            'omega0': self.fourier_widget.spins[7].value(),
            'T': self.fourier_widget.spins[8].value()
        }
        self.fourier_widget.set_parameters(coeffs)
        QMessageBox.information(
            self,
            "Analiz Tamam",
            "Periyodik işaretin katsayıları tabloya göre ayarlandı."
        )

if __name__=='__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
