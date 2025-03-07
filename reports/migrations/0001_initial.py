# Generated by Django 5.1.6 on 2025-03-05 15:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("core", "0003_remove_transaction_attachment_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReportPeriod",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100, verbose_name="عنوان")),
                (
                    "period_type",
                    models.CharField(
                        choices=[
                            ("daily", "روزانه"),
                            ("weekly", "هفتگی"),
                            ("monthly", "ماهانه"),
                            ("quarterly", "سه ماهه"),
                            ("yearly", "سالانه"),
                            ("custom", "دلخواه"),
                        ],
                        default="monthly",
                        max_length=20,
                        verbose_name="نوع دوره",
                    ),
                ),
                ("start_date", models.DateField(verbose_name="تاریخ شروع")),
                ("end_date", models.DateField(verbose_name="تاریخ پایان")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد"),
                ),
            ],
            options={
                "verbose_name": "دوره گزارش",
                "verbose_name_plural": "دوره\u200cهای گزارش",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="FinancialReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="عنوان گزارش")),
                (
                    "report_type",
                    models.CharField(
                        choices=[
                            ("income", "گزارش درآمد"),
                            ("expense", "گزارش هزینه"),
                            ("cash_flow", "گزارش جریان نقدی"),
                            ("balance", "گزارش تراز"),
                        ],
                        max_length=20,
                        verbose_name="نوع گزارش",
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="توضیحات")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی"),
                ),
                (
                    "accounts",
                    models.ManyToManyField(
                        to="core.account", verbose_name="حساب\u200cهای بانکی"
                    ),
                ),
                (
                    "categories",
                    models.ManyToManyField(
                        blank=True,
                        to="core.category",
                        verbose_name="دسته\u200cبندی\u200cها",
                    ),
                ),
                (
                    "period",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="reports.reportperiod",
                        verbose_name="دوره گزارش",
                    ),
                ),
            ],
            options={
                "verbose_name": "گزارش مالی",
                "verbose_name_plural": "گزارش\u200cهای مالی",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ReportChart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=100, verbose_name="عنوان نمودار"),
                ),
                (
                    "chart_type",
                    models.CharField(
                        choices=[
                            ("line", "نمودار خطی"),
                            ("bar", "نمودار میله\u200cای"),
                            ("pie", "نمودار دایره\u200cای"),
                            ("area", "نمودار مساحت"),
                        ],
                        max_length=20,
                        verbose_name="نوع نمودار",
                    ),
                ),
                ("data_config", models.JSONField(verbose_name="تنظیمات داده")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد"),
                ),
                (
                    "report",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="reports.financialreport",
                        verbose_name="گزارش مالی",
                    ),
                ),
            ],
            options={
                "verbose_name": "نمودار گزارش",
                "verbose_name_plural": "نمودارهای گزارش",
                "ordering": ["created_at"],
            },
        ),
    ]
