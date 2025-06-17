import os
import webview
import subprocess
import sys

import settings

from db import DataBase


class API:
    def __init__(self):
        self.db = DataBase(settings.DB_NAME)

    def get_main_html(self):
        raw_html = self.read_html(resource_path('pages/index.html'))
        group_rows = ""

        all_groups = self.db.get_all_groups()
        if not all_groups:
            group_rows = """
            <div class="group">
                <div class="group-info">
                    <div class="group-name">Схоже, у вас ще немає груп</div>
                    <div class="group-programs">Натисніть 'Створити групу', щоб почати.</div>
                </div>
            </div>
            """
        else:
            for group_id, name in all_groups:
                programs = self.db.get_programs_by_group(group_id)
                prog_list = ", ".join(p[0] for p in programs) if programs else "Програм не додано"               

                group_rows += f"""
                    <div class="group">
                        <div class="group-info">
                            <div class="group-name">{name}</div>
                            <div class="group-programs">{prog_list}</div>
                        </div>
                        <div class="actions">
                            <button class="btn-run" onclick="pywebview.api.run_group({group_id})">Запустити</button>
                            <button class="btn-edit" onclick="pywebview.api.edit_group({group_id})">Змінити</button>
                            <button class="btn-delete" onclick="confirmDelete({group_id})">Видалити</button>
                        </div>
                    </div>
                """
        return raw_html.replace("{{GROUPS}}", group_rows)

    def create_group(self):
        html = self.read_html(resource_path('pages/create.html'))
        webview.windows[0].load_html(html)

    def create_group_with_programs(self, name, program_ids):
        self.db.add_group_with_programs(name, program_ids)
        self.back_to_main()

    def create_group_with_custom_programs(self, name, program_list: list):
        group_id = self.db.add_group_with_programs(name, [])
        for program in program_list:
            program_id = self.db.add_program(program['name'], program['path'])
            self.db.link_program_to_group(group_id, program_id)
        self.back_to_main()

    def back_to_main(self):
        html = self.get_main_html()
        webview.windows[0].load_html(html)

    def delete_group(self, group_id):
        self.db.delete_group(group_id)
        self.back_to_main()

    def select_program_file(self):
        file_type = ['Програми (*.exe)'] if os.name == 'nt' else ['Усі файли (*.*)']
        file_paths = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_type)

        if file_paths:
            filepath = file_paths[0]
            return {'name': os.path.basename(filepath), 'path': filepath}
        return None

    def run_program_by_path(self, path):
        subprocess.Popen(path, shell=True)

    def run_group(self, group_id):
        programs = self.db.get_programs_by_group(group_id)
        print(programs)
        for program_name, path in programs:
            if path:
                subprocess.Popen(['start', '', path], shell=True)

    def read_html(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()      

    def edit_group(self, group_id):
        group_details = self.db.get_group_details(group_id)
        if group_details:
            html = self.read_html(resource_path('pages/update.html'))
            webview.windows[0].load_html(html)
            webview.windows[0].evaluate_js(f'loadGroupData({group_details})')

    def save_updated_group(self, group_id, name, programs):
        self.db.update_group(group_id, name, programs)
        self.back_to_main()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    api = API()
    window = webview.create_window("Групи програм", html=api.get_main_html(), js_api=api)
    webview.start()
