import requests
import json
import time
import sys
import os
from urllib.parse import quote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class CatBackup:
    def __init__(self):
        self.group_name = "PD-132"
        self.base_url = "https://cataas.com"
        self.yandex_token = "y0__xD4lvGiBBjblgMgk9m0yhQwvvnhjAjnGe56l2WVL0792g0fGH0Iun2Bow"
        
        self.headers_ya = {
            'Authorization': f'OAuth {self.yandex_token}'
        }
        
    def get_cat_image(self, text):
        try:
            image_url = f"{self.base_url}/cat/says/{quote(text)}"
            print(f"eURL картинки: {image_url}")
            response = requests.get(image_url, timeout=10)
            print(f"Статус получения картинки: {response.status_code}")
            
            if response.status_code == 200:
                return {
                    'image_url': image_url,
                    'text': text
                }
            else:
                raise Exception(f"Ошибка получения картинки: {response.status_code}")
        except Exception as e:
            raise Exception(f"Ошибка при получении картинки: {str(e)}")
    
    def create_ya_folder(self):
        try:
            url = "https://cloud-api.yandex.net/v1/disk/resources"
            params = {'path': f'/{self.group_name}'}
            
            response = requests.put(url, headers=self.headers_ya, params=params, timeout=10)
            print(f"Статус создания папки: {response.status_code}")
            
            if response.status_code == 409:
                print("Папка уже существует")
                return True
            elif response.status_code == 201:
                print("Папка успешно создана")
                return True
            else:
                print(f"Ошибка создания папки: {response.text}")
                return False
        except Exception as e:
            print(f"Ошибка при создании папки: {str(e)}")
            return False
    
    def upload_to_yadisk(self, file_path, image_url):
        try:
            url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            params = {
                'path': file_path,
                'url': image_url
            }
            
            response = requests.post(url, headers=self.headers_ya, params=params, timeout=30)
            print(f"Статус загрузки: {response.status_code}")
            
            if response.status_code == 202:
                print("Запрос на загрузку принят")
                return True
            else:
                print(f"Ошибка загрузки: {response.text}")
                return False
        except Exception as e:
            print(f"Ошибка при загрузке: {str(e)}")
            return False
    
    def get_file_info(self, file_path):
        try:
            time.sleep(3)
            url = "https://cloud-api.yandex.net/v1/disk/resources"
            params = {'path': file_path}
            
            response = requests.get(url, headers=self.headers_ya, params=params, timeout=10)
            print(f"Статус получения информации: {response.status_code}")
            
            if response.status_code == 200:
                file_info = response.json()
                print(f"Информация о файле получена")
                return file_info
            else:
                print(f"Не удалось получить информацию: {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при получении информации: {str(e)}")
            return None
    
    def save_backup_info(self, backup_data):
        try:
            print("Сохраняем информацию в JSON...")
            
            with open('backup_info.json', 'w', encoding='utf-8') as f:
                json.dump([backup_data], f, ensure_ascii=False, indent=4)
            print("JSON файл успешно создан!")
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения JSON: {e}")
            return False
    
    def backup_cat_image(self, text):
        try:
            print(f"\nНачинаем backup для текста: '{text}'")
            
            cat_data = self.get_cat_image(text)
            image_url = cat_data['image_url']
            
            if not self.create_ya_folder():
                print("Не удалось создать папку")
                return False
            
            file_name = f"{text.replace(' ', '_')}.jpg"
            ya_path = f"/{self.group_name}/{file_name}"
            
            if not self.upload_to_yadisk(ya_path, image_url):
                print("Не удалось загрузить картинку")
                return False
            
            file_info = self.get_file_info(ya_path)
            
            backup_info = {
                'file_name': file_name,
                'size': file_info.get('size', 0) if file_info else 0,
                'created': file_info.get('created', '') if file_info else '',
                'modified': file_info.get('modified', '') if file_info else '',
                'ya_path': ya_path,
                'original_url': image_url,
                'text': text,
                'backup_date': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if self.save_backup_info(backup_info):
                print("🎉Backup завершен успешно!")
                return True
            else:
                print("Не удалось сохранить JSON")
                return False
                
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            return False

def main():
    print("=== Резервное копирование картинок с котиками ===")
    
    backup = CatBackup()
    
    while True:
        print("\n" + "="*50)
        text = input("Введите текст для картинки (или 'exit' для выхода): ").strip()
        
        if text.lower() == 'exit':
            print("👋До свидания!")
            break
        elif text:
            backup.backup_cat_image(text)
        else:
            print("Текст не может быть пустым")

if __name__ == "__main__":
    main()