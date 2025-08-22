from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from novels.models import Novel
from interactions.models import Comment
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Tạo nhiều comment con (reply) cho các comment có sẵn của novel"

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

        # lấy các comment cha (chỉ lấy 10 cái đầu cho gọn)
        parent_comments = Comment.objects.filter(novel=novel, parent_comment__isnull=True)[:10]

        if not parent_comments.exists():
            self.stdout.write(self.style.ERROR("Chưa có comment cha để tạo reply"))
            return

        replies_list = [
            "Đúng rồi, mình cũng thấy thế!",
            "Haha chuẩn luôn",
            "Mình nghĩ tác giả sẽ còn plot twist.",
            "Công nhận, đọc cuốn thật.",
            "Bạn nói chuẩn quá.",
            "Tớ thì lại nghĩ khác chút.",
            "Có lẽ chap sau sẽ rõ hơn.",
            "Mình cũng đang hóng đây.",
            "Thật sự bất ngờ với tình tiết này.",
            "Đọc mà cười muốn xỉu"
        ]

        created_count = 0
        for parent in parent_comments:
            for i in range(random.randint(2, 4)):  # mỗi comment cha có 2-4 reply
                user = random.choice(users)
                content = random.choice(replies_list)
                Comment.objects.create(
                    novel=novel,
                    user=user,
                    content=content,
                    parent_comment=parent
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Đã tạo {created_count} comment con thành công!"))
