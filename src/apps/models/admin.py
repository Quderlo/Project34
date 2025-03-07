from django import forms
from .models import Person, Camera, ElectronicLock, AccessTime, LockLog
from django.utils.html import format_html
from django.contrib import admin


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'is_active', 'groups_list', 'face_data')
    list_filter = ('is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'patronymic')
    filter_horizontal = ('groups',)
    ordering = ('last_name', 'first_name')

    def get_fieldsets(self, request, obj=None):
        if obj:  # Редактор
            return (
                ('Персональные данные', {
                    'fields': (
                        ('first_name', 'last_name', 'patronymic'),
                        'is_active',
                    )
                }),
                ('Системная информация', {
                    'fields': ('created_at', 'last_seen'),
                }),
                ('Группы доступа', {
                    'fields': ('groups',)
                })
            )
        # Создание
        return (
            ('Персональные данные', {
                'fields': (
                    ('first_name', 'last_name', 'patronymic'),
                    'is_active',
                )
            }),
            ('Группы доступа', {
                'fields': ('groups',)
            })
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return 'created_at', 'last_seen'
        return ()

    # Поле метод
    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.patronymic or ''}".strip()
    full_name.short_description = 'ФИО'

    # Поле метод
    def groups_list(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    groups_list.short_description = 'Группы доступа'

class CameraForm(forms.ModelForm):
    class Meta:
        model = Camera
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }
        fields = '__all__'


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    form = CameraForm
    list_display = ('display_name', 'lock_info', 'status_indicator', 'connection_info')
    list_filter = ('is_live', 'electronic_lock')
    search_fields = ('name', 'ip_address')
    ordering = ('name',)

    fieldsets = (
        ('Основные данные', {
            'fields': (
                'name',
                ('ip_address', 'port', 'image_path', 'image_link'),
                'electronic_lock'
            )
        }),
        ('Статус', {
            'fields': ('is_live',)
        })
    )

    def display_name(self, obj):
        return f"{obj.name} ({obj.ip_address})"
    display_name.short_description = 'Камера'

    def lock_info(self, obj):
        return str(obj.electronic_lock)
    lock_info.short_description = 'Управляемый замок'

    def status_indicator(self, obj):
        color = 'green' if obj.is_live else 'red'
        text = 'Активна' if obj.is_live else 'Неактивна'
        return format_html('<span style="color: {};">● {}</span>', color, text)
    status_indicator.short_description = 'Статус'

    def connection_info(self, obj):
        return f"{obj.name}:{obj.port}"
    connection_info.short_description = 'Подключение'



@admin.register(ElectronicLock)
class ElectronicLockAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'connection_status', 'endpoints_preview')
    readonly_fields = ('is_online',)
    search_fields = ('ip_address',)

    fieldsets = (
        ('Основные параметры', {
            'fields': (
                'ip_address',
                ('status_link', 'lock_link', 'unlock_link'),
                'is_online', 'secret_key'
            )
        }),
    )

    def connection_status(self, obj):
        status = '✅ Онлайн' if obj.is_online else '❌ Офлайн'
        return status

    connection_status.short_description = 'Статус соединения'

    def endpoints_preview(self, obj):
        return f"Закрытие: {obj.lock_link}\nОткрытие: {obj.unlock_link}"

    endpoints_preview.short_description = 'Эндпоинты'


@admin.register(AccessTime)
class AccessTimeAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('person_info', 'camera_info', 'access_time', 'status_indicator')
    list_filter = ('camera', 'created_at')
    search_fields = ('people__last_name', 'people__first_name', 'camera__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': (
                ('people', 'camera'),
            )
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

    def person_info(self, obj):
        return f"{obj.people.last_name} {obj.people.first_name}"

    person_info.short_description = 'Персона'

    def camera_info(self, obj):
        return f"{obj.camera.name} ({obj.camera.ip_address})"

    camera_info.short_description = 'Камера'

    def access_time(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M:%S")

    access_time.short_description = 'Время доступа'

    def status_indicator(self, obj):
        color = '#0f0' if obj.people.is_active else '#f00'
        text = 'Разрешён' if obj.people.is_active else 'Запрещён'
        return format_html('<span style="color: {};">⬤ {}</span>', color, text)

    status_indicator.short_description = 'Статус'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('people', 'camera')



@admin.register(LockLog)
class LockLogAdmin(admin.ModelAdmin):
    list_display = ('lock', 'user', 'action', 'timestamp', 'status', 'details')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False