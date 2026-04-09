\*\*Xúc xắc màu\*\*

Xúc xắc màu là bản chuyển thể của PlayAural từ trò \*Color Game\* quen thuộc ở các \*perya\* Philippines. Mọi người cùng xuống cửa màu, ba viên xúc xắc màu được tung chung, rồi từng cửa được tính thắng thua đúng theo số viên ra trúng màu đó.

\*\*Lối chơi\*\*

\* Bàn chơi có \*\*6 cửa màu\*\*: đỏ, xanh dương, vàng, xanh lá, trắng và cam.
\* Mỗi vòng dùng \*\*3 viên xúc xắc màu\*\*.
\* Cả 3 viên đều có cùng 6 màu này, nên một màu có thể xuất hiện \*\*0, 1, 2 hoặc 3 lần\*\* trong một vòng.
\* Khi bắt đầu trận, mỗi người chơi nhận một lượng \*\*vốn khởi điểm\*\* theo cài đặt của bàn.
\* Mỗi vòng mở ra một \*\*pha đặt cược chung\*\*. Đây không phải kiểu chờ từng người một khi đang mở cửa cược. Tất cả người chơi còn vốn đều có thể hành động trong cùng một khoảng thời gian.
\* Trong tài liệu này, \*\*người chơi còn vốn\*\* nghĩa là người có bankroll lớn hơn 0.
\* Trong pha đặt cược, bạn có thể xuống vốn vào \*\*một cửa màu\*\* hoặc chia vốn ra \*\*nhiều cửa màu khác nhau\*\*.
\* Mỗi cửa được tính độc lập. Bạn không chọn một màu thắng duy nhất cho cả vòng.
\* Khi đã chốt xong, bạn dùng \*\*Khóa cược\*\*.
\* Nếu tất cả người chơi còn vốn đều khóa sớm, xúc xắc sẽ được tung ngay.
\* Nếu hết giờ trước, hệ thống sẽ tự động khóa những người còn lại với đúng bảng cược họ đang có, kể cả trường hợp \*\*không xuống cửa nào\*\*.
\* Sau khi có kết quả, vốn được cập nhật, bảng xếp hạng được đọc ra, rồi hệ thống mở vòng cược mới nếu trận chưa kết thúc.

\*\*Cơ chế đặc biệt\*\*

\* \*\*Pha cược đồng thời:\*\* tất cả người chơi còn vốn đều có thể đặt và sửa cửa trong cùng một cửa sổ thời gian.
\* \*\*Khóa cược:\*\* sau khi đã khóa, bạn không thể đổi cửa của vòng đó nữa.
\* \*\*Bỏ vòng:\*\* bạn có thể khóa ở trạng thái không đặt cửa nào. Khi đó, bạn không lời cũng không lỗ ở vòng đó.
\* \*\*Cháy vốn:\*\* nếu vốn của bạn về 0, tên bạn vẫn nằm trên bảng xếp hạng nhưng bạn không thể đặt cược mới.
\* \*\*Hết giờ cược:\*\* khi đồng hồ về 0, hệ thống không xóa các cửa bạn đang có. Nó chỉ khóa nguyên trạng bảng cược hiện tại.

\*\*Cách tính vốn\*\*

Xúc xắc màu là trò chơi xoay quanh \*\*vốn hiện có\*\*.

\* Giá trị cạnh tranh chính của bạn là \*\*bankroll\*\*.
\* Bảng xếp hạng còn theo dõi:
\* \*\*Vòng có lãi:\*\* số vòng bạn kết thúc với mức lời dương
\* \*\*Lãi lớn nhất:\*\* khoản lời cao nhất của bạn trong một vòng

\*\*Cách trả thưởng\*\*

Mỗi \*\*cửa màu\*\* được tính riêng theo đúng công thức trong mã nguồn:

\* \*\*Trúng 0 viên:\*\* lãi lỗ ròng là \*\*-tiền cược\*\*
\* \*\*Trúng 1 viên:\*\* lãi lỗ ròng là \*\*+1 lần tiền cược\*\*
\* \*\*Trúng 2 viên:\*\* lãi lỗ ròng là \*\*+2 lần tiền cược\*\*
\* \*\*Trúng 3 viên:\*\* lãi lỗ ròng là \*\*+3 lần tiền cược\*\*

Đó chính là kiểu trả thưởng truyền thống \*\*1 ăn 1, 1 ăn 2, 1 ăn 3\*\* của Color Game.

Ví dụ:

\* Bạn đặt 5 vốn vào cửa đỏ và 3 vốn vào cửa xanh dương.
\* Kết quả ra là đỏ, đỏ, xanh lá.
\* Cửa đỏ trúng \*\*2 viên\*\*, nên phần lãi lỗ ròng của riêng cửa đó là \*\*+10\*\*.
\* Cửa xanh dương trượt hoàn toàn, nên phần lãi lỗ ròng là \*\*-3\*\*.
\* Tổng kết cả vòng, bạn \*\*lời 7 vốn\*\*.

\*\*Cách thắng trận\*\*

Trò chơi có hai cách tính thắng:

\* \*\*Trụ lại cuối cùng\*\*
\* \*\*Nhiều vốn nhất khi hết số vòng\*\*

Tuy nhiên, mã nguồn hiện tại còn có thêm một quy tắc kết thúc sớm áp dụng chung:

\* Nếu chỉ còn \*\*một người chơi còn vốn\*\*, trận sẽ kết thúc ngay, dù chưa chạm giới hạn số vòng.

Vì vậy, cách chạy chính xác của trò chơi là:

\* \*\*Trụ lại cuối cùng:\*\*
\* Nếu chỉ còn một người vẫn còn vốn, người đó thắng ngay.
\* Nếu chạm giới hạn số vòng trước, người có nhiều vốn nhất sẽ thắng.
\* \*\*Nhiều vốn nhất khi hết số vòng:\*\*
\* Ý chính của chế độ này là chấm theo vốn ở cuối giới hạn.
\* Nhưng nếu trước đó chỉ còn một người vẫn còn vốn, mã hiện tại cũng sẽ kết thúc ngay tại thời điểm đó.

Nếu nhiều người hòa nhau ở đầu bảng, thứ tự phân định chính xác là:

\* vốn cao hơn
\* nhiều vòng có lãi hơn
\* lãi lớn nhất trong một vòng cao hơn
\* nếu vẫn hòa, kết quả giữ nguyên là hòa

\*\*Tùy chỉnh tại bàn\*\*

\* \*\*Vốn khởi điểm:\*\* Mặc định \*\*100\*\*. Phạm vi hợp lệ: \*\*10 đến 1000\*\*.
\* Mỗi người chơi bắt đầu trận với đúng số vốn này.

\* \*\*Mức cược tối thiểu:\*\* Mặc định \*\*1\*\*. Phạm vi hợp lệ: \*\*1 đến 100\*\*.
\* Mọi cửa cược khác 0 đều phải ít nhất bằng mức này.

\* \*\*Tổng cược tối đa mỗi vòng:\*\* Mặc định \*\*20\*\*. Phạm vi trong ô tùy chọn: \*\*1 đến 1000\*\*.
\* Ngoài ra, logic của trò chơi còn kiểm tra thêm:
\* giá trị này phải lớn hơn hoặc bằng Mức cược tối thiểu
\* giá trị này không được vượt quá Vốn khởi điểm
\* Trần cược thực tế của mỗi người trong một vòng là số nhỏ hơn giữa:
\* bankroll hiện có của người đó
\* tùy chọn này

\* \*\*Thời gian đặt cược:\*\* Mặc định \*\*15 giây\*\*. Phạm vi hợp lệ: \*\*5 đến 60 giây\*\*.
\* Đây là đồng hồ chung của pha đặt cược trong mỗi vòng.

\* \*\*Giới hạn số vòng:\*\* Mặc định \*\*20\*\*. Phạm vi hợp lệ: \*\*1 đến 100\*\*.
\* Khi đạt tới số vòng này, trận buộc phải kết thúc và chốt bảng xếp hạng.

\* \*\*Cách tính thắng:\*\* Mặc định \*\*Trụ lại cuối cùng\*\*.
\* Các lựa chọn:
\* \*\*Trụ lại cuối cùng\*\*
\* \*\*Nhiều vốn nhất khi hết số vòng\*\*

\*\*Phím tắt\*\*

\* \*\*R:\*\* Đặt cửa đỏ.
\* \*\*U:\*\* Đặt cửa xanh dương.
\* \*\*Y:\*\* Đặt cửa vàng.
\* \*\*G:\*\* Đặt cửa xanh lá.
\* \*\*W:\*\* Đặt cửa trắng.
\* \*\*O:\*\* Đặt cửa cam.
\* \*\*C:\*\* Xóa toàn bộ cửa cược hiện tại của bạn.
\* \*\*Dấu cách:\*\* Khóa cược cho vòng hiện tại.
\* \*\*E:\*\* Nghe pha hiện tại, thời gian còn lại, vốn, trạng thái khóa cược và người đang dẫn đầu.
\* \*\*V:\*\* Nghe bảng cược hiện tại của mọi người.
\* \*\*D:\*\* Nghe lượt ra gần nhất và kết quả của từng người ở lượt đó.
\* \*\*T:\*\* Nghe thông báo pha hiện tại.
\* \*\*S:\*\* Nghe bảng vốn.
\* \*\*Ctrl+U:\*\* Nghe những ai đang ngồi tại bàn.
