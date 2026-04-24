import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")
        
        # Список тренировок
        self.trainings = []
        
        # Путь к файлу данных
        self.data_file = "trainings.json"
        
        # Загрузка данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # Основная рамка
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Поля ввода
        ttk.Label(main_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(main_frame, width=15)
        self.date_entry.grid(row=0, column=1, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(main_frame, text="Тип тренировки:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(10,0))
        self.type_combo = ttk.Combobox(main_frame, values=["Бег", "Плавание", "Велосипед", "Силовая", "Йога"], width=15)
        self.type_combo.grid(row=0, column=3, pady=5)
        self.type_combo.set("Бег")
        
        ttk.Label(main_frame, text="Длительность (мин):").grid(row=0, column=4, sticky=tk.W, pady=5, padx=(10,0))
        self.duration_entry = ttk.Entry(main_frame, width=10)
        self.duration_entry.grid(row=0, column=5, pady=5)
        
        add_button = ttk.Button(main_frame, text="Добавить тренировку", command=self.add_training)
        add_button.grid(row=0, column=6, padx=(20,0), pady=5)
        
        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтры", padding="5")
        filter_frame.grid(row=1, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, padx=5)
        self.filter_type = ttk.Combobox(filter_frame, values=["Все", "Бег", "Плавание", "Велосипед", "Силовая", "Йога"], width=15)
        self.filter_type.grid(row=0, column=1, padx=5)
        self.filter_type.set("Все")
        
        ttk.Label(filter_frame, text="Дата от:").grid(row=0, column=2, padx=5)
        self.filter_date_from = ttk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=5)
        
        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=5)
        self.filter_date_to = ttk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=5)
        
        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=6, padx=10)
        
        reset_button = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        reset_button.grid(row=0, column=7, padx=5)
        
        # Таблица для отображения
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)
        
        self.tree.grid(row=2, column=0, columnspan=7, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=2, column=7, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=7, pady=10)
        
        delete_button = ttk.Button(button_frame, text="Удалить выбранное", command=self.delete_training)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        save_button = ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_to_json)
        save_button.pack(side=tk.LEFT, padx=5)
        
        load_button = ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_from_json)
        load_button.pack(side=tk.LEFT, padx=5)
        
        # Статистика
        self.stats_label = ttk.Label(main_frame, text="")
        self.stats_label.grid(row=4, column=0, columnspan=7, pady=5)
        
        # Настройка весов
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_str):
        """Проверка длительности"""
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get().strip()
        training_type = self.type_combo.get()
        duration = self.duration_entry.get().strip()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        # Добавление тренировки
        training = {
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        
        self.trainings.append(training)
        self.save_data()
        self.refresh_table()
        
        # Очистка поля длительности
        self.duration_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Тренировка '{training_type}' добавлена!")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную тренировку?"):
            # Получение индекса
            item = self.tree.item(selected[0])
            values = item['values']
            
            # Поиск и удаление
            for i, training in enumerate(self.trainings):
                if (training['date'] == values[0] and 
                    training['type'] == values[1] and 
                    training['duration'] == float(values[2])):
                    del self.trainings[i]
                    break
            
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", "Тренировка удалена")
    
    def apply_filter(self):
        """Применение фильтров"""
        filter_type = self.filter_type.get()
        filter_from = self.filter_date_from.get().strip()
        filter_to = self.filter_date_to.get().strip()
        
        filtered = self.trainings.copy()
        
        # Фильтр по типу
        if filter_type != "Все":
            filtered = [t for t in filtered if t['type'] == filter_type]
        
        # Фильтр по дате от
        if filter_from:
            if not self.validate_date(filter_from):
                messagebox.showerror("Ошибка", "Неверный формат даты 'от'")
                return
            filtered = [t for t in filtered if t['date'] >= filter_from]
        
        # Фильтр по дате до
        if filter_to:
            if not self.validate_date(filter_to):
                messagebox.showerror("Ошибка", "Неверный формат даты 'до'")
                return
            filtered = [t for t in filtered if t['date'] <= filter_to]
        
        self.display_trainings(filtered)
        self.update_stats(filtered)
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_type.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
    
    def refresh_table(self):
        """Обновление таблицы со всеми тренировками"""
        self.display_trainings(self.trainings)
        self.update_stats(self.trainings)
    
    def display_trainings(self, trainings_list):
        """Отображение тренировок в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление данных
        for training in trainings_list:
            self.tree.insert("", tk.END, values=(
                training['date'],
                training['type'],
                f"{training['duration']:.1f}"
            ))
    
    def update_stats(self, trainings_list):
        """Обновление статистики"""
        if not trainings_list:
            self.stats_label.config(text="Нет тренировок для отображения")
            return
        
        total_duration = sum(t['duration'] for t in trainings_list)
        avg_duration = total_duration / len(trainings_list)
        
        self.stats_label.config(
            text=f"Всего тренировок: {len(trainings_list)} | "
                 f"Общая длительность: {total_duration:.1f} мин | "
                 f"Средняя длительность: {avg_duration:.1f} мин"
        )
    
    def save_data(self):
        """Автосохранение данных"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Автозагрузка данных"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.trainings = []
    
    def save_to_json(self):
        """Ручное сохранение в JSON"""
        filename = "trainings_export.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_from_json(self):
        """Ручная загрузка из JSON"""
        filename = "trainings_export.json"
        if not os.path.exists(filename):
            messagebox.showwarning("Предупреждение", f"Файл {filename} не найден")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            self.trainings = loaded_data
            self.save_data()
            self.refresh_table()
            messagebox.showinfo("Успех", f"Загружено {len(loaded_data)} тренировок")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
