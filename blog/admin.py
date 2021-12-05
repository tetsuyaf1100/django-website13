from django.contrib import admin
from . import models
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin import AdminSite

class PostInline(admin.TabularInline):
    model = models.Post
    fields = ('title', 'body')
    extra = 1


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [PostInline]


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass


class PostTitleFilter(admin.SimpleListFilter):
    title = '本文'
    parameter_name = 'body_contains'

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(body__icontains=self.value())
        return queryset

    def lookups(self, request, model_admin):
        return [
            ("ブログ", "「ブログ」を含む"),
            ("日記", "「日記」を含む"),
            ("開発", "「開発」を含む"),
        ]


class PostAdminForm(forms.ModelForm):
    class Meta:
        labels = {
            'title': 'ブログタイトル',
        }
    def clean(self):
        body = self.cleaned_data.get('body')
        if '<' in body:
            raise forms.ValidationError('HTMLタグは使えません。')


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    #fields = ('title',)
    #fields = ('title', 'body', 'category', 'tags')
    readonly_fields = ('created', 'updated')
    #fields = ('title', 'body', 'category', 'tags', 'created', 'updated')
    fieldsets = [
        (None, {'fields': ('title', )}),
        ('コンテンツ', {'fields': ('body', )}),
        ('分類', {'fields': ('category', 'tags')}),
        ('メタ', {'fields': ('created', 'updated')})
    ]
    filter_horizontal = ('tags',)

    def save_model(self, request, obj, form, change):
        print("before save")
        super().save_model(request, obj, form, change)
        print("after save")

    list_display = ('id', 'title', 'category', 'tags_summary', 'published', 'created', 'updated')
    list_select_related = ('category', )
    list_editable = ('title', 'category')
    search_fields = ('title', 'category__name', 'tags__name', 'created', 'updated')
    ordering = ('-updated', '-created')
    list_filter = (PostTitleFilter, 'category', 'tags', 'created', 'updated')

    def tags_summary(self, obj):
        qs = obj.tags.all()
        label = ', '.join(map(str, qs))
        return label
    tags_summary.short_description = "tags"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
    actions = ["publish", "unpublish"]

    def publish(self, request, queryset):
        queryset.update(published=True)
        
    publish.short_description = "公開する"
        
    def unpublish(self, request, queryset):
        queryset.update(published=False)
        
    unpublish.short_description = "下書きに戻す"
    form = PostAdminForm
    class Media:
        js = ('post.js',)


class BlogAdminSite(AdminSite):
    site_header = 'マイページ'
    site_title = 'マイページ'
    index_title = 'ホーム'
    site_url = None
    login_form = AuthenticationForm

    def has_permission(self, request):
        return request.user.is_active


mypage_site = BlogAdminSite(name="mypage")

mypage_site.register(models.Post)
mypage_site.register(models.Tag)
mypage_site.register(models.Category)
