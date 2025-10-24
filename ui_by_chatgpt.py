import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt


class SnatchScheduler(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Auto Snatch Scheduler")
        self.setFixedSize(600, 500)

        # Layout setup
        main_layout = QVBoxLayout()
        form_layout = QGridLayout()

        # Campus selection
        self.campus_combo = QComboBox()
        self.campus_combo.addItems(["west", "east", "middle", "high_tech"])
        form_layout.addWidget(QLabel("Select Campus:"), 0, 0)
        form_layout.addWidget(self.campus_combo, 0, 1)

        # Today / Tomorrow selection
        self.day_combo = QComboBox()
        self.day_combo.addItems(["today", "tomorrow"])
        form_layout.addWidget(QLabel("Select Day:"), 1, 0)
        form_layout.addWidget(self.day_combo, 1, 1)

        # Time block selection (example: create buttons for time blocks)
        self.time_block_buttons = {}
        for row in range(4):
            for col in range(4):
                time_slot = f"{(row * 4) + col + 7}:00"
                button = QPushButton(time_slot)
                button.setCheckable(True)
                self.time_block_buttons[time_slot] = button
                form_layout.addWidget(button, row + 2, col)

        # Start button
        self.start_button = QPushButton("Start Snatching")
        self.start_button.clicked.connect(self.start_snatching)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.start_button)

        self.setLayout(main_layout)

    def start_snatching(self):
        campus = self.campus_combo.currentText()
        day = self.day_combo.currentText()
        selected_blocks = [time for time, button in self.time_block_buttons.items() if button.isChecked()]

        if not selected_blocks:
            print("Please select at least one time block.")
            return

        print(f"Campus: {campus}, Day: {day}, Selected Time Blocks: {', '.join(selected_blocks)}")
        # Pass the values to your script to start the snatching process
        # main(coord, companion, campus, day, index, start_time, num, stake_out)

        # For now, let's print to simulate:
        print(f"Snatching started for {campus} campus on {day} with blocks {', '.join(selected_blocks)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnatchScheduler()
    window.show()
    sys.exit(app.exec_())
