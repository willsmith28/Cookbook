TAG_KINDS = (
    ("Cuisine", "Cuisine"),
    ("Meal", "Meal"),
    ("Prep Method", "Prep Method"),
)

INGREDIENT_UNITS = (
    (
        "Volume",
        (
            ("tsp", "teaspoon"),
            ("tbsp", "tablespoon"),
            ("fl oz", "fluid ounce"),
            ("c", "cup"),
            ("pt", "pint"),
            ("qt", "quart"),
            ("gal", "gallon"),
            ("ml", "milliliter"),
            ("l", "liter"),
        ),
    ),
    ("Mass", (("lb", "pound"), ("oz", "ounce"), ("g", "gram"),)),
    ("Length", (("in", "inch"), ("mm", "millimeter"), ("cm", "centimeter"))),
    ("Other", (("pieces", ""), ("n/a", ""))),
)

MEAL_PLAN_TYPES = (
    ("Breakfast", "Breakfast"),
    ("Lunch", "Lunch"),
    ("Dinner", "Dinner"),
    ("Snack", "Snack"),
)

