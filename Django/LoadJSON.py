import os
import json
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ml_pharm_web.settings')
django.setup()
from django.conf import settings
from pharm_web.models import Type_Drugs_MedScape, Name_Drugs_MedScape

json_folder_medscape_en = 'D:\\Programs\\ml_palm1\\data_collection\\medscape\\data\\medscape_en\\testmedscape_en'
json_folder_medscape_ru = 'D:\\Programs\\ml_palm1\\data_collection\\medscape\\data\\medscape_ru\\testmedscape_ru'

# json_folder = 'D:\\Programs\\ml_palm1\\data_collection\\drugs\\data\\drugs_en\\all_medications' # путь к папке с JSON файлами
for file_name in os.listdir(json_folder_medscape_en):  # проходим по всем файлам в папке
    print(file_name)
    if file_name.endswith('.json'):  # если файл имеет расширение .json
        # Поиск аналогичного русского файла JSON
        f_ru = open(os.path.join(json_folder_medscape_ru, file_name), 'r', encoding='utf-8')
        with open(os.path.join(json_folder_medscape_en, file_name), 'r',
                  encoding='utf-8') as f:  # открываем файл для чтения
            data = json.load(f)  # загружаем данные из файла в переменную data
            data_ru = json.load(f_ru)
            #            my_model_instance = MyModel(field1=data['field1'], field2=data['field2'], ...) # создаем экземпляр модели и заполняем поля данными из файла
            #            my_model_instance.save() # сохраняем экземпляр модели в базу данных PostgreSQL
            # Создаем объект Type_Drugs
            print(data['classes'])
            print(data_ru['classes'])
            arr_drug_obj = []
            i = 0
            while i < len(data['classes']):
                type_drug_en = data['classes'][i]
                type_drug_ru = data_ru['classes'][i]
                print(type_drug_en, type_drug_ru)
                type_drug_obj, _ = Type_Drugs_MedScape.objects.get_or_create(Type_en=type_drug_en, Type_ru=type_drug_ru)
                print(type_drug_obj)
                type_drug_obj.save()
                arr_drug_obj.append(type_drug_obj)
                i = i + 1

            # Создаем объекты Group_Type_Drugs и связи с Name_Drugs

            group_type_en = data['name']
            group_type_ru = data_ru['name']
            group_type_obj, _ = Name_Drugs_MedScape.objects.get_or_create(Name_en=group_type_en,
                                                                          Name_ru=group_type_ru)
            i_arr_drug_obj = 0
            while i_arr_drug_obj < len(arr_drug_obj):
                group_type_obj.Group_Type.add(arr_drug_obj[i_arr_drug_obj])
            print(group_type_obj)
            group_type_obj.save()
            i = 0
            while i < len(data['other_names']):
                group_type_en = data['other_names']
                group_type_ru = data_ru['other_names']
                group_type_obj, _ = Name_Drugs_MedScape.objects.get_or_create(Name_en=group_type_en,
                                                                              Name_ru=group_type_ru)
                i_arr_drug_obj = 0
                while i_arr_drug_obj < len(arr_drug_obj):
                    group_type_obj.Group_Type.add(arr_drug_obj[i_arr_drug_obj])
                print(group_type_obj)
                group_type_obj.save()
                i = i + 1
"""
            # Создаем объект Drugs_information и связываем с остальными объектами
            name_drugs_drugs_information = models.ManyToManyField('Name_Drugs')
            group_type_obj.append(type_drug_obj)
            name_file_drugs_information = file_name
            Comment_en_drugs_information = data['comment']
            Comment_ru_drugs_information = data_ru['comment']
            drugs_info_obj = group_type_obj.drugs_information
            drugs_info_obj.Type_Drugs = type_drug_obj
            drugs_info_obj.Source_Drugs.add(source_obj)
            drugs_info_obj.Pregnancy_and_lactation = preg_lact_obj
            drugs_info_obj.Warnings.set(warnings_objs)
            drugs_info_obj.Adverse_Effects.set(adverse_effects_objs)
            drugs_info_obj.save()

            # Создаем объекты Warnings и связи с Drugs_information
            warnings_objs = []
            for warning in data['warnings']['cautions']['common']:
                warning_en = warning
                warning_ru = 'Опасность'  # заполнить соответствующим значением
                warning_type = 'Тип опасности'  # заполнить соответствующим значением
                warning_obj = Warnings.objects.create(
                    Drugs_information=name_drug_obj,
                    warnings_name_en=warning_en,
                    warnings_name_ru=warning_ru,
                    warnings_type=warning_type
                )
                warnings_objs.append(warning_obj)

            # Создаем объекты Adverse_Effects и связи с Drugs_information
            adverse_effects_objs = []
            for adverse_effect in data['adverse effects']:
                adverse_effect_en = adverse_effect['name']
                adverse_effect_ru = 'Побочное действие'  # заполнить соответствующим значением
                adverse_effect_percent = adverse_effect['percent']
                adverse_effect_obj = Adverse_Effects.objects.create(
                    Drugs_information=name_drug_obj,
                    adverse_effects_name_en=adverse_effect_en,
                    adverse_effects_name_ru=adverse_effect_ru,
                    adverse_effects_percent=adverse_effect_percent
                )
            adverse_effects_objs.append(adverse_effect_obj)

        # Создаем объекты Source_Drugs и связи с Drugs_information
        source_en = data['source']
        source_obj = Source_Drugs.objects.create(Drugs_information=name_drug_obj, Source=source_en)

        # Создаем объект Pregnancy_and_lactation и связи с Drugs_information
        pregnancy_common_en = '. '.join(data['pregnancy']['common'])
        pregnancy_specific_en = '. '.join(data['pregnancy']['specific'])
        lactation_common_en = '. '.join(data['lactation']['common'])
        lactation_specific_en = '. '.join(data['lactation']['specific'])
        pregnancy_common_ru = '. '.join(data_ru['pregnancy']['common'])
        pregnancy_specific_ru = '. '.join(data_ru['pregnancy']['specific'])
        lactation_common_ru = '. '.join(data_ru['lactation']['common'])
        lactation_specific_ru = '. '.join(data_ru['lactation']['specific'])
        preg_lact_obj = Pregnancy_and_lactation.objects.create(
            Drugs_information=name_drug_obj,
            Pregnancy_common_en=pregnancy_common_en,
            Pregnancy_specific_en=pregnancy_specific_en,
            Lactation_common_en=lactation_common_en,
            Lactation_specific_en=lactation_specific_en,
            Pregnancy_common_ru=pregnancy_common_ru,
            Pregnancy_specific_ru=pregnancy_specific_ru,
            Lactation_common_ru=lactation_common_ru,
            Lactation_specific_ru=lactation_specific_ru
        )
"""
