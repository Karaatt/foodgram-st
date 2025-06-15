import csv
import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredients
from foodgram import settings


class Command(BaseCommand):
    help = "Импорт данных об ингредиентах в базу данных"

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, "data", "ingredients.csv")
        ingredients_to_add = []
        existing_names = set(
            Ingredients.objects.values_list("name", flat=True)
        )

        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) < 2:
                    continue
                name, unit = row[0].strip(), row[1].strip()
                if name and unit and name not in existing_names:
                    ingredients_to_add.append(
                        Ingredients(name=name, measurement_unit=unit)
                    )
                    existing_names.add(name)

        if ingredients_to_add:
            Ingredients.objects.bulk_create(
                ingredients_to_add, batch_size=1000
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Загружено {len(ingredients_to_add)} ингредиентов"
                )
            )
