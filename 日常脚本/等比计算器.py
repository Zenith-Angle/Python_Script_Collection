from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
import sys


def scale_values():
    try:
        scale_factor = float(scale_factor_edit.text())
        numbers = list(map(float, numbers_edit.text().split(",")))
        scaled_numbers = [x * scale_factor for x in numbers]
        scaled_text_edit.setPlainText(", ".join(map(str, scaled_numbers)))
    except ValueError:
        scaled_text_edit.setPlainText("输入无效，请输入数字。")


# Initialize the PyQt application
app = QApplication(sys.argv)

# Create the main window
window = QWidget()
window.setWindowTitle("数值缩放计算器")
window.resize(400, 200)

# Create widgets
numbers_label = QLabel("请输入数值（用逗号分隔）:")
numbers_edit = QLineEdit()

scale_factor_label = QLabel("请输入缩放倍数:")
scale_factor_edit = QLineEdit()

scale_button = QPushButton("缩放")
scale_button.clicked.connect(scale_values)

scaled_text_edit = QTextEdit("缩放后的数值：")
scaled_text_edit.setReadOnly(True)

# Organize widgets with layout
layout = QVBoxLayout()
layout.addWidget(numbers_label)
layout.addWidget(numbers_edit)
layout.addWidget(scale_factor_label)
layout.addWidget(scale_factor_edit)
layout.addWidget(scale_button)
layout.addWidget(scaled_text_edit)

# Set layout to window
window.setLayout(layout)

# Show the window
window.show()

# Run the PyQt event loop
sys.exit(app.exec_())
