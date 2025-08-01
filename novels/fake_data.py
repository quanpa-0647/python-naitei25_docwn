from django.templatetags.static import static
import random
from datetime import date, timedelta
card_list = [
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-a/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },
        {
            'image_url': static('novels/images/fake.jpg'),
            'title': 'Tôi chuyển sinh thành thiếu gia phản diện trong game eroge, người khiến tiểu thư bá tước sa ngã làm hầu gái phục vụ. Thế nên tôi quyết tâm né kết cục bị nghiệp quật, và rồi… Nữ chính bắt đầu mò vào phòng tôi mỗi đêm ở Học Viện Dũng Giả',
            'description': 'Và thế là, khóa huấn luyện tình yêu với bạn gái cũ bắt đầu!? Một người quá hoàn hảo để làm đối tượng tập dượt. Nhưng nếu mối tình này nên duyên... Liệu mối quan hệ giữa tôi và Manami sẽ ra sao?Một rom-com thanh xuân ngọt ngào dành cho những trái tim chưa quên rung động đầu đời!',
            'link': '/truyen-b/',
            'chap':'Chương 06: CHFISNFSFNIEHOFIHIER',
            'vol' : 'Tập 01: Vùng đã shfisfihdfihfi'
        },

         ]

discussion_data = [
        {"title": "Hỏi Truyện từ A>Z. Góc dhしfしfhs",
            "time": "24 phút", "color": "green"},
        {"title": "Góp ý và báo lỗijhfidf", "time": "6 giờ", "color": "red"},
        {"title": "Trang yêu cầu xóa truy", "time": "9 giờ", "color": "red"},
        {"title": "Quy Định Đối Với Truyệfbdjbf",
            "time": "10 giờ", "color": "red"},
        {"title": "Thảo luận cho tác giả O.fdfd",
            "time": "12 giờ", "color": "green"},
        {"title": "Hướng dẫn đăng truyện", "time": "12 giờ", "color": "red"},
        {"title": "(HAKO FAQs) NHỮNG Cfjdofj.",
         "time": "15 giờ", "color": "blue"},
        {"title": "Thông báo về AI dịch", "time": "22 giờ", "color": "red"},
        {"title": "Đề xuất LN/WN cho các...", "time": "1 ngày", "color": "green"},
    ]
comments = [
        {
            "title": "Cô hầu gái đầy tính chiếm hữu tôi dhjishfisffsni",
            "comment": "@Kai9206: ừ nhỉ 🐧",
            "username": "Ling-sama",
            "avatar": static('novels/images/avatar.png'),
            "time": "1 giờ"
        },
        {
            "title": "Cô hầu gái đầy tính chiếm hữu tôi fhsifn ",
            "comment": "@Ling-sama: đó không phải áy náy, mà là cảm giác bị phản bội <(\")",
            "username": "Kai9206",
            "avatar": static('novels/images/avatar.png'),
            "time": "1 giờ"
        },
        {
            "title": "Trở thành quái vật không gian với ...",
            "comment": "Cho mình hỏi xíu bóng hồng theo main thuộc chủng loài nào và có sức mạnh ra sao vậy mn?",
            "username": "Fht",
            "avatar": static('novels/images/avatar.png'),
            "time": "1 giờ"
        },
        {
            "title": "Kumo Desu Ga Nani Ka",
            "comment": "Không biết ông nào có biết ở đâu bán LN hay có LN lậu đọc k :))",
            "username": "tututuutuuttuuttu",
            "avatar": static('novels/images/avatar.png'),
            "time": "1 giờ"
        },
        {
            "title": "Tái sinh thành chiến binh vô danh ...",
            "comment": "@Kaedehara Kaguza: bro :))))",
            "username": "Lịch1234",
            "avatar": static('novels/images/avatar.png'),
            "time": "1 giờ"
        }
    ]
top_novels_this_month = [
    {"title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "views": 1234},
    {"title": "Bí Mật Của Naoko", "views": 987},
    {"title": "Nhà Giả Kim", "views": 865},
    {"title": "Đắc Nhân Tâm", "views": 754},
    {"title": "Totto-chan", "views": 690},
]
def getNewNovels():
    today = date.today()
    labels = []
    data = []
    for i in range(29, -1, -1): 
        day = today - timedelta(days=i)
        labels.append(day.strftime("%d/%m"))
        data.append(random.randint(0, 10))  
    return labels, data

new_novels = [
    {"title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "date": "01/07/2025"},
    {"title": "Bí Mật Của Naoko", "date": "05/07/2025"},
    {"title": "Nhà Giả Kim", "date": "12/07/2025"},
    {"title": "Đắc Nhân Tâm", "date": "18/07/2025"},
    {"title": "Totto-chan", "date": "28/07/2025"},
]
authors = [
    {"name": "Nguyễn Nhật Ánh", "total_novels": 12, "total_views": 12000},
    {"name": "Haruki Murakami", "total_novels": 8, "total_views": 9800},
    {"name": "Paulo Coelho", "total_novels": 6, "total_views": 8750},
    {"name": "Dale Carnegie", "total_novels": 4, "total_views": 6500},
    {"name": "Tetsuko Kuroyanagi", "total_novels": 3, "total_views": 4200},
]
novels = [
    {"title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "views": 1572, "date": "2024-05-12", "author": "Nguyễn Nhật Ánh", "tags": ["tuổi thơ", "việt nam"]},
    {"title": "Bí Mật Của Naoko", "views": 1340, "date": "2024-06-01", "author": "Higashino Keigo", "tags": ["trinh thám", "bí ẩn"]},
    {"title": "Nhà Giả Kim", "views": 1680, "date": "2024-04-25", "author": "Paulo Coelho", "tags": ["triết lý", "hành trình"]},
    {"title": "Đắc Nhân Tâm", "views": 2455, "date": "2024-03-19", "author": "Dale Carnegie", "tags": ["kỹ năng sống", "phát triển bản thân"]},
    {"title": "Totto-chan", "views": 1010, "date": "2024-05-30", "author": "Tetsuko Kuroyanagi", "tags": ["giáo dục", "trẻ em"]},
    {"title": "Kẻ Trộm Sách", "views": 980, "date": "2024-04-04", "author": "Markus Zusak", "tags": ["lịch sử", "chiến tranh"]},
    {"title": "Mắt Biếc", "views": 2100, "date": "2024-03-11", "author": "Nguyễn Nhật Ánh", "tags": ["tình yêu", "tuổi học trò"]},
    {"title": "Chiến Binh Cầu Vồng", "views": 870, "date": "2024-02-10", "author": "Andrea Hirata", "tags": ["nghèo đói", "hi vọng"]},
    {"title": "Rừng Nauy", "views": 1205, "date": "2024-05-22", "author": "Haruki Murakami", "tags": ["tâm lý", "đời sống"]},
    {"title": "Không Gia Đình", "views": 890, "date": "2024-06-15", "author": "Hector Malot", "tags": ["phiêu lưu", "mồ côi"]},
    {"title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "views": 1572, "date": "2024-05-12", "author": "Nguyễn Nhật Ánh", "tags": ["tuổi thơ", "quê hương"]},
    {"title": "Bí Mật Của Naoko", "views": 1340, "date": "2024-06-01", "author": "Higashino Keigo", "tags": ["bí ẩn", "nhật bản"]},
    {"title": "Nhà Giả Kim", "views": 1680, "date": "2024-04-25", "author": "Paulo Coelho", "tags": ["triết học", "hành trình"]},
    {"title": "Đắc Nhân Tâm", "views": 2455, "date": "2024-03-19", "author": "Dale Carnegie", "tags": ["kỹ năng", "tâm lý học"]},
    {"title": "Totto-chan", "views": 1010, "date": "2024-05-30", "author": "Tetsuko Kuroyanagi", "tags": ["giáo dục", "tự truyện"]},
    {"title": "Kẻ Trộm Sách", "views": 980, "date": "2024-04-04", "author": "Markus Zusak", "tags": ["đức quốc xã", "văn học thiếu nhi"]},
    {"title": "Mắt Biếc", "views": 2100, "date": "2024-03-11", "author": "Nguyễn Nhật Ánh", "tags": ["tình cảm", "học đường"]},
    {"title": "Chiến Binh Cầu Vồng", "views": 870, "date": "2024-02-10", "author": "Andrea Hirata", "tags": ["cảm hứng", "đấu tranh"]},
    {"title": "Rừng Nauy", "views": 1205, "date": "2024-05-22", "author": "Haruki Murakami", "tags": ["đau thương", "trưởng thành"]},
    {"title": "Không Gia Đình", "views": 890, "date": "2024-06-15", "author": "Hector Malot", "tags": ["gia đình", "cuộc sống"]}
]
users = [
        {"name": "Nguyễn Văn A", "gender": "Nam", "email": "a@example.com", "phone": "0912345678", "status": "active"},
        {"name": "Trần Thị B", "gender": "Nữ", "email": "b@example.com", "phone": "0912345679", "status": "blocked"},
        {"name": "Lê Văn C", "gender": "Nam", "email": "c@example.com", "phone": "0912345680", "status": "active"},
        {"name": "Phạm Thị D", "gender": "Nữ", "email": "d@example.com", "phone": "0912345681", "status": "blocked"},
        {"name": "Hoàng Văn E", "gender": "Nam", "email": "e@example.com", "phone": "0912345682", "status": "active"},
         {"name": "Nguyễn Văn A", "gender": "Nam", "email": "a@example.com", "phone": "0912345678", "status": "active"},
        {"name": "Trần Thị B", "gender": "Nữ", "email": "b@example.com", "phone": "0912345679", "status": "blocked"},
        {"name": "Lê Văn C", "gender": "Nam", "email": "c@example.com", "phone": "0912345680", "status": "active"},
        {"name": "Phạm Thị D", "gender": "Nữ", "email": "d@example.com", "phone": "0912345681", "status": "blocked"},
        {"name": "Hoàng Văn E", "gender": "Nam", "email": "e@example.com", "phone": "0912345682", "status": "active"},
         {"name": "Nguyễn Văn A", "gender": "Nam", "email": "a@example.com", "phone": "0912345678", "status": "active"},
        {"name": "Trần Thị B", "gender": "Nữ", "email": "b@example.com", "phone": "0912345679", "status": "blocked"},
        {"name": "Lê Văn C", "gender": "Nam", "email": "c@example.com", "phone": "0912345680", "status": "active"},
        {"name": "Phạm Thị D", "gender": "Nữ", "email": "d@example.com", "phone": "0912345681", "status": "blocked"},
        {"name": "Hoàng Văn E", "gender": "Nam", "email": "e@example.com", "phone": "0912345682", "status": "active"},
]
comments = [
    {"id": 1, "username": "nguyenhoa", "novel": "Tôi thấy hoa vàng...", "content": "Truyện hay quá!", "status": "Bị báo cáo"},
    {"id": 2, "username": "phuonglinh", "novel": "Mắt biếc", "content": "Tác phẩm cảm động", "status": "Không"},
    {"id": 3, "username": "thanhtrung", "novel": "Tuổi thơ dữ dội", "content": "Đáng đọc!", "status": "Bị báo cáo"},
    {"id": 4, "username": "admin", "novel": "Dế mèn phiêu lưu ký", "content": "Tuổi thơ ùa về", "status": "Không"},
    {"id": 5, "username": "minhthu", "novel": "Lão Hạc", "content": "Buồn và thấm", "status": "Không"},
    {"id": 6, "username": "trieuanh", "novel": "Số đỏ", "content": "Hài hước mà sâu sắc", "status": "Bị báo cáo"},
    {"id": 7, "username": "leminh", "novel": "Chí Phèo", "content": "Nam Cao quá đỉnh", "status": "Không"},
    {"id": 8, "username": "ngoclan", "novel": "Vợ nhặt", "content": "Nặng trĩu lòng", "status": "Không"},
    {"id": 9, "username": "quanghuy", "novel": "Nhật ký trong tù", "content": "Bác Hồ tài ba", "status": "Bị báo cáo"},
    {"id": 10, "username": "maianh", "novel": "Đất rừng phương Nam", "content": "Gần gũi thiên nhiên", "status": "Không"},
    {"id": 11, "username": "trangnguyen", "novel": "Thép đã tôi thế đấy", "content": "Quyết tâm và lý tưởng", "status": "Không"},
    {"id": 12, "username": "vandiep", "novel": "Người lái đò sông Đà", "content": "Cảnh thiên nhiên hùng vĩ", "status": "Bị báo cáo"},
    {"id": 13, "username": "honghanh", "novel": "Chiếc thuyền ngoài xa", "content": "Nghệ thuật và đời sống", "status": "Không"},
    {"id": 14, "username": "khanhlinh", "novel": "Ai đã đặt tên cho dòng sông", "content": "Thơ mộng và sâu lắng", "status": "Không"},
    {"id": 15, "username": "manhtien", "novel": "Đời thừa", "content": "Cảm xúc khó tả", "status": "Bị báo cáo"},
    {"id": 16, "username": "ngochieu", "novel": "Vợ chồng A Phủ", "content": "Tình người vùng cao", "status": "Không"},
    {"id": 17, "username": "bachkhoa", "novel": "Tắt đèn", "content": "Phận nghèo bị áp bức", "status": "Không"},
    {"id": 18, "username": "hanhphuc", "novel": "Lặng lẽ Sa Pa", "content": "Lặng lẽ mà đẹp", "status": "Bị báo cáo"},
     {"id": 19, "username": "bachkhoa", "novel": "Tắt đèn", "content": "Phận nghèo bị áp bức", "status": "Không"},
    {"id": 20, "username": "hanhphuc", "novel": "Lặng lẽ Sa Pa", "content": "Lặng lẽ mà đẹp", "status": "Bị báo cáo"},
]
novel_uploads = [
    {"id": 1, "title": "Vầng Trăng Máu", "user": "Lê Minh", "tags": ["Kinh dị"], "upload_date": "2025-07-10"},
    {"id": 2, "title": "Gió Qua Đỉnh Núi", "user": "Nguyễn An", "tags": ["Lãng mạn"], "upload_date": "2025-07-12"},
    {"id": 3, "title": "Sát Thủ Vô Hình", "user": "Trần Bảo", "tags": ["Hành động"], "upload_date": "2025-07-14"},
    {"id": 4, "title": "Ánh Sáng Lặng Thầm", "user": "Hương Giang", "tags": ["Tâm lý", "Tình cảm"], "upload_date": "2025-07-15"},
    {"id": 5, "title": "Người Giữ Mộ", "user": "Lưu Thành", "tags": ["Kinh dị"], "upload_date": "2025-07-16"},
    {"id": 6, "title": "Mặt Trời Đêm", "user": "Phan Hoàng", "tags": ["Khoa học viễn tưởng"], "upload_date": "2025-07-17"},
    {"id": 7, "title": "Thế Giới Phản Chiếu", "user": "Minh Phúc", "tags": ["Phiêu lưu"], "upload_date": "2025-07-17"},
    {"id": 8, "title": "Ký Ức Đỏ", "user": "Trà My", "tags": ["Tình cảm"], "upload_date": "2025-07-18"},
    {"id": 9, "title": "Bão Trong Đêm", "user": "Hữu Nghĩa", "tags": ["Hành động"], "upload_date": "2025-07-18"},
    {"id": 10, "title": "Thiên Sứ Bóng Tối", "user": "Diệu Nhi", "tags": ["Giả tưởng"], "upload_date": "2025-07-19"},
    {"id": 11, "title": "Cuộc Gọi Từ Quá Khứ", "user": "Thanh Lam", "tags": ["Trinh thám"], "upload_date": "2025-07-19"},
    {"id": 12, "title": "Ngọn Gió Lạ", "user": "Kim Ngân", "tags": ["Tình cảm"], "upload_date": "2025-07-20"},
    {"id": 13, "title": "Đứa Trẻ Mồ Côi", "user": "Hoàng Vũ", "tags": ["Tâm lý"], "upload_date": "2025-07-20"},
    {"id": 14, "title": "Thị Trấn Ma", "user": "Nam Phong", "tags": ["Kinh dị"], "upload_date": "2025-07-21"},
    {"id": 15, "title": "Lạc Trong Ký Ức", "user": "Thu Thảo", "tags": ["Huyền bí"], "upload_date": "2025-07-22"},
    {"id": 16, "title": "Người Đến Từ Sao Hỏa", "user": "Quốc Bảo", "tags": ["Viễn tưởng"], "upload_date": "2025-07-22"},
    {"id": 17, "title": "Chiến Binh Ánh Sáng", "user": "Bảo Anh", "tags": ["Hành động"], "upload_date": "2025-07-23"},
    {"id": 18, "title": "Vết Cắt Thời Gian", "user": "Mai Chi", "tags": ["Khoa học viễn tưởng"], "upload_date": "2025-07-24"},
    {"id": 19, "title": "Hoa Nở Trong Bóng Tối", "user": "Linh Đan", "tags": ["Tình cảm"], "upload_date": "2025-07-25"},
    {"id": 20, "title": "Vùng Đất Câm Lặng", "user": "Trí Dũng", "tags": ["Kinh dị"], "upload_date": "2025-07-26"},
]
chapter_uploads = [
   {"title": "Vầng Trăng Máu", "chapter_number": 1, "upload_date": "2025-07-11"},
    {"title": "Vầng Trăng Máu", "chapter_number": 2, "upload_date": "2025-07-12"},
    {"title": "Gió Qua Đỉnh Núi", "chapter_number": 1, "upload_date": "2025-07-13"},
    {"title": "Sát Thủ Vô Hình", "chapter_number": 1, "upload_date": "2025-07-14"},
    {"title": "Sát Thủ Vô Hình", "chapter_number": 2, "upload_date": "2025-07-15"},
    {"title": "Ánh Sáng Lặng Thầm", "chapter_number": 1, "upload_date": "2025-07-15"},
    {"title": "Trò Chơi Sinh Tử", "chapter_number": 1, "upload_date": "2025-07-17"},
    {"title": "Hồ Sơ Tội Phạm", "chapter_number": 1, "upload_date": "2025-07-19"},
    {"title": "Giấc Mơ Đêm Đông", "chapter_number": 1, "upload_date": "2025-07-21"},
    {"title": "Hồi Ký Người Vô Danh", "chapter_number": 1, "upload_date": "2025-07-22"},
    {"title": "Cánh Cửa Âm Dương", "chapter_number": 1, "upload_date": "2025-07-23"},
    {"title": "Một Ngày Không Em", "chapter_number": 1, "upload_date": "2025-07-25"},
    {"title": "Ngục Tối Rực Lửa", "chapter_number": 1, "upload_date": "2025-07-26"},
    {"title": "Thành Phố Mộng Mơ", "chapter_number": 1, "upload_date": "2025-07-27"},
    {"title": "Sương Mù Trên Phố", "chapter_number": 1, "upload_date": "2025-07-28"},
    {"title": "Vùng Đất Hứa", "chapter_number": 1, "upload_date": "2025-07-29"},
    {"title": "Nhật Ký Ký Ức", "chapter_number": 1, "upload_date": "2025-07-30"},
    {"title": "Lưỡi Dao Trong Bóng Tối", "chapter_number": 1, "upload_date": "2025-07-30"},
    {"title": "Mắt Biếc", "chapter_number": 1, "upload_date": "2025-07-31"},
    {"title": "Lạc Vào Hư Vô", "chapter_number": 1, "upload_date": "2025-07-31"},
]
volume_uploads = [
    {"title": "Vầng Trăng Máu","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-12"},
    {"title": "Vầng Trăng Máu","chapter_number": 1, "episode_number": 2, "upload_date": "2025-07-13"},
    {"title": "Gió Qua Đỉnh Núi","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-14"},
    {"title": "Sát Thủ Vô Hình","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-15"},
    {"title": "Ánh Sáng Lặng Thầm","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-16"},
    {"title": "Trò Chơi Sinh Tử","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-17"},
    {"title": "Hồ Sơ Tội Phạm","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-19"},
    {"title": "Giấc Mơ Đêm Đông","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-21"},
    {"title": "Hồi Ký Người Vô Danh","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-22"},
    {"title": "Cánh Cửa Âm Dương","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-23"},
    {"title": "Một Ngày Không Em","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-25"},
    {"title": "Ngục Tối Rực Lửa","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-26"},
    {"title": "Thành Phố Mộng Mơ","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-27"},
    {"title": "Sương Mù Trên Phố","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-28"},
    {"title": "Vùng Đất Hứa","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-29"},
    {"title": "Nhật Ký Ký Ức","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-30"},
    {"title": "Lưỡi Dao Trong Bóng Tối","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-30"},
    {"title": "Mắt Biếc","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-31"},
    {"title": "Lạc Vào Hư Vô","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-31"},
    {"title": "Ánh Sáng Cuối Đường","chapter_number": 1, "episode_number": 1, "upload_date": "2025-07-31"},
]

