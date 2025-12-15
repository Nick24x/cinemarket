from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0004_remove_perfil_usuario_perfil_user"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE IF EXISTS usuarios_customuser DROP COLUMN IF EXISTS rut;
                ALTER TABLE IF EXISTS auth_user DROP COLUMN IF EXISTS rut;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
