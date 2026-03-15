from django.contrib import admin
from .models import Review, OurResults, OurResultImages, RequestQuote

# ------------------ Review Admin ------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'username', 'rating', 'created_at')
    search_fields = ('display_name', 'username', 'comment')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


# ------------------ OurResultImages Inline ------------------
class OurResultImagesInline(admin.TabularInline):  # or admin.StackedInline
    model = OurResultImages
    extra = 1  # Number of empty image forms to display
    fields = ('image', 'created_at')
    readonly_fields = ('created_at',)
    # show preview (optional)
    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" />'
        return "-"
    image_tag.allow_tags = True
    image_tag.short_description = 'Preview'


# ------------------ OurResults Admin ------------------
@admin.register(OurResults)
class OurResultsAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'created_at')
    search_fields = ('title', 'subtitle')
    inlines = [OurResultImagesInline]  # Add images inline
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(RequestQuote)
