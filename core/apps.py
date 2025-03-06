from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "هسته اصلی"

    def ready(self):
        # ثبت template tags
        from django.template.defaulttags import register
        from .templatetags import custom_filters
