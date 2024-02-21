from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget,
    QTableWidgetItem, QTableWidget, QLabel, QHeaderView, QInputDialog, QFileDialog,
    QLineEdit
)
from PyQt5.QtCore import Qt
from datetime import datetime
import json
import os


class CourriersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tab_titles = []  # Keep track of tab titles
        self.tabs = []  # Keep track of tab widgets
        self.current_tab_index = -1  # Initialize current tab index
        self.init_ui()

    def init_ui(self):
        # Create a layout for the widget
        main_layout = QVBoxLayout(self)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()

        # Create a button to add tabs
        self.add_tab_button = QPushButton("Add Tab")
        self.add_tab_button.clicked.connect(self.add_tab)

        # Create a button to load data from JSON
        self.load_json_button = QPushButton("Load from JSON")
        self.load_json_button.clicked.connect(self.load_from_json)

        # Create a button to save data to JSON
        self.save_json_button = QPushButton("Save to JSON")
        self.save_json_button.clicked.connect(self.save_to_json)

        # Add buttons to the button layout
        button_layout.addWidget(self.add_tab_button)
        button_layout.addWidget(self.load_json_button)
        button_layout.addWidget(self.save_json_button)

        # Create a tab widget to contain multiple tabs
        self.tab_widget = QTabWidget()

        # Connect tab change event
        self.tab_widget.currentChanged.connect(self.tab_changed)

        # Add the tab widget and button layout to the main layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tab_widget)

    def __add_tab(self, name):
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        table_widget = QTableWidget()
        table_widget.setColumnCount(5)  # Excluding the ID column
        table_widget.setHorizontalHeaderLabels(
            ["date", "expediteur", "destinataire", "objet", "pieces jointes"])
        # Resize columns to contents
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table_widget)
        # Create search widget
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search by Date or Object")
        search_input.textChanged.connect(lambda text: self.search_table(table_widget, text))
        search_layout.addWidget(search_input)
        layout.addLayout(search_layout)
        # Add button to add rows
        add_row_button = QPushButton("Add Row")
        add_row_button.clicked.connect(lambda: self.add_row(table_widget))
        layout.addWidget(add_row_button)
        new_tab.setLayout(layout)
        # Add the new tab to the tab widget
        self.tabs.append(new_tab)
        #self.tab_titles.append(name)  # You can customize tab titles
        #self.update_saved_tabs()

        return layout

    def add_tab(self):
        # Create a new tab with a table widget
        name, ok = QInputDialog.getText(self, "New Tab Name", "Enter the name for the new tab:")
        if ok:
            self.__add_tab(name)

            self.tab_titles.append(name)  # You can customize tab titles
            self.update_saved_tabs()

    def __add_row(self, table_widget, column, value, row_count, file_paths=None):

        if not file_paths:
            item = QTableWidgetItem(value)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make cell non-editable
            table_widget.setItem(row_count, column, item)

        elif len(file_paths) > 0:
            # Create a button with file path written on top of it
            file_button = QPushButton("\n".join(file_paths))
            file_button.clicked.connect(lambda: self.open_file(file_paths))
            table_widget.setCellWidget(row_count, 4, file_button)

    def add_row(self, table_widget):
        row_count = table_widget.rowCount()
        table_widget.setRowCount(row_count + 1)

        # Set current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Set value for date column
        self.__add_row(table_widget, 0, current_date, row_count)

        # Get expediteur input from user
        expediteur, _ = QInputDialog.getText(self, "Expediteur", "Enter Expediteur:")
        self.__add_row(table_widget, 1, expediteur, row_count)

        # Get destinataire input from user
        destinataire, _ = QInputDialog.getText(self, "Destinataire", "Enter Destinataire:")
        self.__add_row(table_widget, 2, destinataire, row_count)

        # Get objet input from user
        objet, _ = QInputDialog.getText(self, "Objet", "Enter Objet:")
        self.__add_row(table_widget, 3, objet, row_count)

        # Select file for "pieces jointes" column
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select File(s)", "", "All Files (*)")
        self.__add_row(table_widget, 4, "", row_count, file_paths)
        

    def open_file(self, file_paths):
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.startfile(file_path)

    def update_saved_tabs(self):
        # Clear the contents of the tab widget
        self.tab_widget.clear()

        # Create a custom widget for the first tab
        first_tab_widget = QWidget()
        first_tab_layout = QVBoxLayout(first_tab_widget)

        # Add labels for each saved tab title
        for title in self.tab_titles:
            label = QLabel(title)
            label.setStyleSheet("QLabel { color: blue; text-decoration: underline;font-size:30px }")
            label.mousePressEvent = lambda event, title=title: self.label_clicked(title)
            first_tab_layout.addWidget(label)

        # Add the custom widget to the tab widget
        self.tab_widget.addTab(first_tab_widget, "Saved Tabs")

        # Add the rest of the tabs
        for tab, title in zip(self.tabs, self.tab_titles):
            self.tab_widget.addTab(tab, title)

    def save_to_json(self):
        data = {
            "tab_titles": self.tab_titles,
            # Add more data as needed
        }

        # Add rows data for each tab
        for title, tab in zip(self.tab_titles, self.tabs):
            table_widget = tab.findChild(QTableWidget)
            rows_data = []
            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                # Get file paths for "pieces jointes"
                file_button = table_widget.cellWidget(row, 4)
                if file_button:
                    file_paths = file_button.text().split('\n')
                    row_data.append(file_paths)
                else:
                    row_data.append([])
                rows_data.append(row_data)
            data[title] = rows_data

        file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "w") as f:
                json.dump(data, f)


    def load_from_json(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.tab_titles = data.get("tab_titles", [])
                # Load more data as needed

                # Clear existing tabs
                self.tabs.clear()

                # Add the tabs based on the loaded data
                for title in self.tab_titles:
                    layout = self.__add_tab(title)

                    table_widget = layout.itemAt(0).widget()

                    new_tab = layout.parentWidget()

                    self.tab_widget.addTab(new_tab, title)

                    # Load row data
                    rows_data = data.get(title, [])
                    for row_data in rows_data:
                        row_count = table_widget.rowCount()
                        table_widget.setRowCount(row_count + 1)
                        for col, value in enumerate(row_data[:-1]):  # Skip the last element (file paths)
                            self.__add_row(table_widget, col, value, row_count)

                        # Add button with file paths for "pieces jointes"
                        file_paths = row_data[-1]
                        self.__add_row(table_widget, 4, "", row_count, file_paths)

                # Update saved tabs
                self.update_saved_tabs()


    def open_files(self, file_paths):
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.startfile(file_path)



    def label_clicked(self, title):
        index = self.tab_titles.index(title)
        self.tab_widget.setCurrentIndex(index + 1)
        self.current_tab_index = index  # Update current tab index

    def tab_changed(self, index):
        if index == 0:
            # Clicked on "Saved Tabs"
            pass
        else:
            # Clicked on a tab, update current tab index
            self.current_tab_index = index - 1

    def search_table(self, table_widget, text):
        for row in range(table_widget.rowCount()):
            row_hidden = True
            for column in range(table_widget.columnCount()):
                item = table_widget.item(row, column)
                if item is not None and text.lower() in item.text().lower():
                    row_hidden = False
                    break
            table_widget.setRowHidden(row, row_hidden)


if __name__ == "__main__":
    app = QApplication([])

    courriers_widget = CourriersWidget()
    courriers_widget.show()

    app.exec_()
