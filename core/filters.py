import django_filters

from .models import Job


class JobFilter(django_filters.FilterSet):
    salary_min = django_filters.NumberFilter(
        field_name="salary_min",
        lookup_expr="gte"
    )

    salary_max = django_filters.NumberFilter(
        field_name="salary_max",
        lookup_expr="lte"
    )

    experience_min = django_filters.NumberFilter(
        field_name="experience",
        lookup_expr="gte"
    )

    experience_max = django_filters.NumberFilter(
        field_name="experience",
        lookup_expr="lte"
    )

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains"
    )

    class Meta:
        model = Job
        fields = [
            "job_type",
            "location",
            "title",
        ]