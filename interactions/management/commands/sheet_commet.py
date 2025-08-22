from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from novels.models import Novel
from interactions.models import Comment
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Tạo nhiều comment mẫu cho 1 novel"

    def handle(self, *args, **kwargs):
        try:
            novel = Novel.objects.get(id=1)
        except Novel.DoesNotExist:
            self.stdout.write(self.style.ERROR("Novel không tồn tại"))
            return

        user_ids = [1, 2]
        users = User.objects.filter(id__in=user_ids)
        if not users.exists():
            self.stdout.write(self.style.ERROR("Không tìm thấy user id=1,2"))
            return

        comments_list = [
            "Truyện này đọc cuốn thật sự!",
            "Mong tác giả ra chap mới sớm.",
            "Nội dung hấp dẫn, nhân vật chính bá quá.",
            "Tình tiết có chút nhanh, nhưng vẫn rất hay.",
            "Càng đọc càng thấy cuốn hút.",
            "Văn phong khá ổn, dịch mượt.",
            "Có ai biết truyện này còn bản raw không?",
            "Đọc mà không dứt ra nổi luôn.",
            "Hóng chap tiếp theo từng ngày.",
            "Một trong những truyện yêu thích nhất của mình."
        ]

        for i in range(20):  # tạo 20 comment
            user = random.choice(users)
            content = random.choice(comments_list)
            Comment.objects.create(
                novel=novel,
                user=user,
                content=content,
                is_active=True
            )

        self.stdout.write(self.style.SUCCESS("Đã tạo 20 comment mẫu thành công!"))
