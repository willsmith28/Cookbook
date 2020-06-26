"""empty message

Revision ID: dfc38175b5cc
Revises: 
Create Date: 2020-06-25 14:25:13.345935

"""
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "dfc38175b5cc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    recipes = op.create_table(
        "recipes",
        sa.Column("id", postgresql.UUID, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("servings", sa.Integer(), nullable=False),
        sa.Column("cook_time", sa.String(), nullable=False),
        sa.Column(
            "created_on", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("last_updated_on", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    tags = op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID, nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("value"),
    )
    ingredients = op.create_table(
        "ingredients",
        sa.Column("id", postgresql.UUID, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("recipe_id", postgresql.UUID, nullable=True),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("recipe_id"),
    )
    op.create_table(
        "recipe_tags",
        sa.Column("recipe_id", postgresql.UUID, nullable=False),
        sa.Column("tag_id", postgresql.UUID, nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("recipe_id", "tag_id", name="recipe_tag_primary_key"),
    )
    steps = op.create_table(
        "steps",
        sa.Column("id", postgresql.UUID, nullable=False),
        sa.Column("instruction", sa.String(), nullable=True),
        sa.Column("order", sa.INTEGER(), nullable=True),
        sa.Column("recipe_id", postgresql.UUID, nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order", "recipe_id", name="step_primary_key"),
    )
    ingredients_in_recipe = op.create_table(
        "ingredients_in_recipe",
        sa.Column("recipe_id", postgresql.UUID, nullable=False),
        sa.Column("ingredient_id", postgresql.UUID, nullable=False),
        sa.Column("amount", sa.DECIMAL(precision=6, scale=2), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("specifier", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingredient_id"], ["ingredients.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint(
            "recipe_id", "ingredient_id", name="ingredients_in_recipe_pk"
        ),
    )
    # ### end Alembic commands ###
    # add base data
    recipe_uuid = str(uuid.uuid4())
    data = {
        ingredients: [
            {
                "id": (cumin_uuid := str(uuid.uuid4())),
                "recipe_id": None,
                "name": "Cumin",
            },
            {
                "id": (paprika_uuid := str(uuid.uuid4())),
                "recipe_id": None,
                "name": "Paprika",
            },
            {
                "id": (chili_uuid := str(uuid.uuid4())),
                "recipe_id": None,
                "name": "Ancho Chili Powder",
            },
            {
                "id": (garlic_uuid := str(uuid.uuid4())),
                "recipe_id": None,
                "name": "Garlic Powder",
            },
            {
                "id": (oregano_uuid := str(uuid.uuid4())),
                "recipe_id": None,
                "name": "Oregano",
            },
            {
                "id": (onion_uuid := str(uuid.uuid4())),
                "recipe_id": None,
                "name": "Onion Powder",
            },
            {
                "id": (cyaenne_uuid := str(uuid.uuid4())),
                "recipe_id": None,
                "name": "Cayenne Powder",
            },
        ],
        recipes: [
            {
                "id": (recipe_uuid := str(uuid.uuid4())),
                "name": "Crock-Pot Chili Powder",
                "description": "Chili powder to be used in Crock-Pot Chili",
                "servings": 1,
                "cook_time": "5 minutes",
            }
        ],
        ingredients_in_recipe: [
            {
                "recipe_id": recipe_uuid,
                "ingredient_id": cumin_uuid,
                "amount": 1,
                "unit": "tblsp",
                "specifier": "",
            },
            {
                "recipe_id": recipe_uuid,
                "ingredient_id": paprika_uuid,
                "amount": 2,
                "unit": "tblsp",
                "specifier": "",
            },
            {
                "recipe_id": recipe_uuid,
                "ingredient_id": chili_uuid,
                "amount": 1,
                "unit": "tblsp",
                "specifier": "",
            },
            {
                "recipe_id": recipe_uuid,
                "ingredient_id": garlic_uuid,
                "amount": 1.5,
                "unit": "tsp",
                "specifier": "",
            },
            {
                "recipe_id": recipe_uuid,
                "ingredient_id": oregano_uuid,
                "amount": 2,
                "unit": "tsp",
                "specifier": "Dried",
            },
            {
                "recipe_id": recipe_uuid,
                "ingredient_id": onion_uuid,
                "amount": 0.75,
                "unit": "tsp",
                "specifier": "",
            },
            {
                "recipe_id": recipe_uuid,
                "ingredient_id": cyaenne_uuid,
                "amount": 0.5,
                "unit": "tsp",
                "specifier": "",
            },
        ],
        steps: [
            {
                "id": str(uuid.uuid4()),
                "recipe_id": recipe_uuid,
                "order": 1,
                "instruction": "mix spices",
            },
        ],
    }

    for table, fixtures in data.items():
        op.bulk_insert(table, fixtures)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("ingredients_in_recipe")
    op.drop_table("steps")
    op.drop_table("recipe_tags")
    op.drop_table("ingredients")
    op.drop_table("tags")
    op.drop_table("recipes")
    # ### end Alembic commands ###
