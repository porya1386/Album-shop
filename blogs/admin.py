from django.contrib import admin

from .models import Post, PostComment, PostImage


class CommentInline(admin.TabularInline):
    model = PostComment
    extra = 0
    fields = ("user", "body", "created_at")
    readonly_fields = ("user", "body", "created_at")
    can_delete = True

    def has_add_permission(self, request, obj=None):
        return False


class ImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ("order", "image", "caption", "caption_fa")
    verbose_name = "image in the text"
    verbose_name_plural = "Images in the text (write [image 1], [image 2] ... on its own line in the text)"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "views", "like_total", "comment_total")
    list_filter = ("status", "author")
    search_fields = ("title", "title_fa", "body", "body_fa")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    readonly_fields = ("views", "created_at", "updated_at")
    inlines = [ImageInline, CommentInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "cover", "excerpt", "body")}),
        ("Persian (فارسی)", {"fields": ("title_fa", "excerpt_fa", "body_fa")}),
        ("Publishing", {"fields": ("status", "published_at", "author")}),
        ("Numbers", {"fields": ("views", "created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        from django.db.models import Count
        return super().get_queryset(request).annotate(_likes=Count("likes", distinct=True),
                                                      _comments=Count("comments", distinct=True))

    @admin.display(description="Likes", ordering="_likes")
    def like_total(self, obj):
        return obj._likes

    @admin.display(description="Comments", ordering="_comments")
    def comment_total(self, obj):
        return obj._comments

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ("short_body", "user", "post", "created_at")
    list_filter = ("post",)
    search_fields = ("body", "user__username")

    @admin.display(description="Comment")
    def short_body(self, obj):
        return obj.body[:60]
