# TFT — Nghiên cứu chiến thuật xuyên mùa

**Phiên bản 4.0 | 25/11/2026 | Phạm vi: chế độ TFT tiêu chuẩn**

## 1. Phạm vi và phương pháp

Tài liệu hợp nhất kiến thức nền tảng và nghiên cứu bổ sung về ra quyết định, dành cho người chơi và hệ thống AI phân tích TFT. Không sử dụng tier list của một mùa làm quy luật chung. Phân biệt ba loại kiến thức: **cơ chế** (phải đối chiếu phiên bản), **heuristic** (kinh nghiệm có ngoại lệ), **mô hình đề xuất** (chưa được kiểm chứng). Nguồn chính thức Riot [1,2] xác định triết lý thiết kế; các hướng dẫn cộng đồng [3–9] cung cấp thực hành; các mô hình toán và AI dưới đây là tổng hợp đề xuất, không phải thuật toán nội bộ Riot.

## 2. Mục tiêu và bản chất trò chơi

TFT là trò chơi nhiều tác nhân, tuần tự, ngẫu nhiên, thông tin không đầy đủ. Trạng thái thay đổi sau mỗi hành động, cửa hàng và giao tranh. Mục tiêu thông thường là giảm thứ hạng kỳ vọng E[rank]; nếu tối ưu leo rank cần dùng hàm lợi ích LP phù hợp thay vì coi mọi bậc hạng có giá trị bằng nhau. Thi đấu giải có thể có mục tiêu khác. Không đánh đồng chất lượng quyết định với kết quả của một trận. Riot nhấn mạnh kiến thức, linh hoạt, quản lý may rủi, quan sát và tốc độ phán đoán [1,2].

## 3. Kinh tế, máu và tempo

### 3.1 Vàng và chi phí cơ hội

Trong quy tắc tiêu chuẩn thường gặp, lợi tức I(g)=min(5,floor(g/10)); thu nhập cơ bản, thưởng chuỗi và thời điểm tính vàng phải lấy từ cấu hình phiên bản. Vàng, XP, máu, trang bị, tướng, ô hàng chờ, thời gian và thông tin đều là tài nguyên. Giữ vàng chỉ có giá trị nếu có thể chuyển hóa thành sức mạnh trước khi bị loại.

Ví dụ: từ 50 xuống 30 vàng, mất 2 vàng lợi tức ở lần tính tiếp theo nếu không có thay đổi khác; chi phí tích lũy phải mô phỏng từng vòng chứ không nhân cố định cho mọi tình huống. Giữ một cặp tướng qua mốc lợi tức đáng giá nếu cơ hội nâng sao hoặc pivot bù đắp khoản thu nhập mất đi. Bán tướng dự phòng khi giá trị kỳ vọng của chúng thấp hơn chi phí giữ.

### 3.2 Chuỗi và trạng thái kinh tế

Chuỗi thắng đồng thời tạo thu nhập và bảo vệ máu; chuỗi thua tạo thu nhập nhưng tiêu hao thời gian sống. Chuỗi xen kẽ có thể kém hiệu quả kinh tế, nhưng thắng một vòng vẫn có giá trị nếu ngăn nguy cơ bị loại. Không cố giữ chuỗi thua khi đối thủ yếu hơn hoặc thiệt hại dự kiến quá lớn. So sánh giá trị bảo vệ chuỗi với vàng cần bỏ ra, xác suất thắng và chất lượng phương án sau đó [3,4,5].

### 3.3 Ngân sách máu

Ước lượng phân phối sát thương của các đối thủ có thể gặp. Nếu HP=24 và thua thường mất 6–12 máu, nguy cơ bị loại sau 2–4 trận thua là đáng kể; không diễn giải đây là số vòng sống chắc chắn. Dùng P(bị loại trong k vòng) thay vì ngưỡng HP cố định. Máu cao không đồng nghĩa có thể tham nếu lobby sắp tăng sức mạnh đồng loạt.

### 3.4 Tempo và stabilization

Tempo là tốc độ tăng sức mạnh tương đối so với lobby. Power spike có thể đến từ nâng sao, thêm tướng, trang bị, mốc tộc hệ, lõi hoặc thay bố trí. Stabilize nghĩa là tăng sức mạnh đủ để giảm rủi ro hiện tại rồi tái tích lũy, không nhất thiết hoàn thành đội hình cuối. Xác định đối thủ sắp tăng sức mạnh, không chỉ nhìn số trận vừa thắng.

## 4. Xây dựng và đánh giá đội hình

Vai trò gồm tank chính/phụ, carry chính/phụ, fighter, khống chế, hỗ trợ, phá đội hình và tướng kích hệ. Một tướng có thể đảm nhiệm nhiều vai trò. Chọn bộ khung theo khả năng gây sát thương, chống chịu, tiếp cận mục tiêu và tiện ích thay vì số tộc hệ kích hoạt. Strongest board là đội hình tốt nhất hiện tại có xét chi phí chuyển tiếp, không nhất thiết là đội hình endgame.

### 4.1 Phân rã sức mạnh

- Sức mạnh cá thể: cấp sao, chỉ số, kỹ năng, trang bị, thời gian tung chiêu đầu tiên.
- Sức mạnh tập thể: hiệu ứng tộc hệ, buff, debuff, phối hợp mục tiêu, phân bố sát thương.
- Độ bền: EHP theo từng loại sát thương, lá chắn, hồi phục, thời gian sống của tank và carry.
- Tính tương thích: cơ chế skill, tầm đánh, đường di chuyển, khống chế, matchup.
- Độ ổn định: khả năng hoạt động khi carry bị khống chế hoặc tank chính chết sớm.

DPS × thời gian hoạt động là xấp xỉ tổng sát thương, không phản ánh burst, overkill, kháng, chọn mục tiêu hoặc tăng tiến sức mạnh theo thời gian. Với kháng không âm R, mô hình thông thường EHP=HP×(1+R/100) áp dụng riêng loại sát thương tương ứng; kiểm tra cơ chế phiên bản.

### 4.2 Chẩn đoán giao tranh

| Hiện tượng | Giả thuyết | Thử nghiệm |
|---|---|---|
| Tank chết trước lần tung chiêu chính | Thiếu chống chịu hoặc bị dồn sát thương | Đổi tank, đồ thủ, vị trí |
| Carry sống đến cuối nhưng không giết được tank | Thiếu DPS hoặc giảm kháng | Thử trang bị, nguồn sát thương phụ |
| Carry chết sớm | Bị tiếp cận, AoE hoặc chọn mục tiêu bất lợi | Đổi góc, phân tán, tướng mồi |
| Thua sát nút thường xuyên | Thiếu một nâng cấp biên | Thêm utility, nâng sao, ghép đồ |
| Thua nặng dù nominal power cao | Tương tác hệ hoặc matchup xấu | Xem lại giao tranh, không chỉ tổng giá tướng |

Đánh giá nhiều matchup; không suy luận nhân quả từ một trận combat.

### 4.3 Vertical và horizontal

Vertical ưu tiên mốc cao một hệ khi lợi ích biên đáng giá. Horizontal kết hợp nhiều hệ nhỏ và tướng độc lập mạnh. So sánh đóng góp của tướng thêm vào với tướng bị thay thế, bao gồm hiệu ứng mất đi. Không mặc định mốc hệ cao luôn mạnh hơn tướng chất lượng.

## 5. Lựa chọn chiến thuật và chuyển bài

| Hướng | Điều kiện thuận lợi | Rủi ro chính |
|---|---|---|
| Hyper roll | Nhiều bản sao giá thấp, cửa hàng phù hợp | Cạn vàng sớm |
| Slow roll | Có thời gian, đủ máu và ít tranh | Không kịp hoàn thành 3 sao |
| Fast level | Kinh tế tốt, đội giữ máu, cần tướng đắt | Lên cấp nhưng thiếu vàng mua/roll |
| Tempo | Đội sẵn mạnh, cơ hội giữ chuỗi | Trần sức mạnh thấp nếu tiêu quá nhiều |
| Flex | Nhiều hướng dùng chung trang bị | Chi phí thao tác, giữ hàng chờ |
| Force | Hiểu sâu một bài, điều kiện phù hợp | Tranh bài, đồ và lõi không tương thích |

Fast 7/8/9/10 là tên kế hoạch, không phải mốc bắt buộc. Một line tốt có opener, tướng giữ đồ, bộ khung giữa trận, carry/tank cuối, phương án thay thế và điều kiện thoát. Pivot từng phần (thay carry giữ tank) thường ít tốn kém hơn thay toàn bộ. Không bán bộ khung đang hoạt động trước khi đủ tướng thay thế nếu không cần thiết. Chi phí đã bỏ ra là sunk cost; chỉ xét giá trị còn lại và chi phí tương lai.

## 6. Xác suất cửa hàng và kỷ luật roll

Nếu xác suất bậc giá c ở cấp L là q, còn n bản sao mục tiêu trong N bản sao cùng bậc, xác suất một ô xấp xỉ p=q×n/N. Với m ô độc lập và p không đổi, P(ít nhất một)=1−(1−p)^m. Ví dụ 30 vàng chỉ dành cho 15 lần refresh giá 2, mỗi shop 5 ô, p=0,024: xác suất ít nhất một bản sao khoảng 83,8%. Không đồng nghĩa xác suất nâng 2 sao. Cần dự trữ vàng mua tướng.

Xác suất ít nhất k bản sao theo xấp xỉ nhị thức: 1−Σ[j=0..k−1] C(m,j)p^j(1−p)^(m−j). Mô hình chính xác hơn mô phỏng rút không hoàn lại trong shop, cập nhật kho khi mua/bán và quy tắc refresh thực tế. Nếu không thấy đầy đủ kho chung, dùng khoảng ước lượng. Đối thủ mua mục tiêu làm giảm số bản sao; mua tướng khác cùng bậc có thể tăng tỷ lệ tương đối của mục tiêu.

Kế hoạch rolldown: đặt mục tiêu chính, danh sách nâng cấp phụ, ngân sách mua, ngưỡng vàng dừng, phương án hụt và thời gian còn lại. Dừng khi đã ổn định hoặc lợi ích kỳ vọng của lần roll tiếp theo thấp hơn phương án khác. Không roll tiếp chỉ vì đã tiêu nhiều vàng.

## 7. Trang bị và lõi

Phân nhóm trang bị theo AD/AP, tốc đánh, mana, chí mạng, khuếch đại, máu, kháng, sustain, giảm hồi máu, giảm giáp/kháng phép và utility. Chọn theo cơ chế skill, loại sát thương, khả năng tung chiêu và thời gian sống. Slam đồ hữu ích sớm nếu giá trị giữ máu/chuỗi cao hơn giá trị chờ BIS. Đồ tank có thể cải thiện tổng sát thương của cả đội bằng cách kéo dài thời gian carry hoạt động. Tránh trùng hiệu ứng không cộng dồn; tra quy tắc phiên bản.

Lõi: combat, economy, XP, reroll, item, trait, champion-specific, scaling, conditional, transformative. Đánh giá khả năng kích hoạt, thời gian thu hồi vốn, sức mạnh tức thời, tương thích trang bị và đội hình, khả năng chuyển bài. Lõi tăng tiến có thể vô giá trị nếu không sống đủ lâu. Thống kê thứ hạng lõi bị ảnh hưởng bởi ai chọn lõi, thời điểm chọn và trạng thái trước khi chọn; không dùng trung bình thô như tác động nhân quả.

## 8. Scouting và positioning

Trước commit/rolldown: đếm bản sao chủ lực trên sân và bench, phân biệt người giữ tạm với người theo bài, xác định sức mạnh tương đối và các power spike sắp tới. Tín hiệu gồm trang bị, lõi, cặp tướng, cấp và hướng kinh tế. Không coi vàng hoặc đối thủ tiếp theo là quan sát được nếu phiên bản/UI không cung cấp. Khi có nhiều đối thủ khả dĩ, tối ưu bố trí theo phân phối matchup, không chỉ người mạnh nhất [3,6].

Xếp cờ: ưu tiên thời gian sống của carry, hướng tiếp cận, phân bổ aggro, tầm đánh, góc kỹ năng, tránh overkill và AoE. Phân tán chống AoE; tập trung khi cần buff vùng; tướng mồi chống cơ chế nhắm đặc biệt; dồn một phía khi có lợi về mục tiêu. Các cách này phụ thuộc targeting thực tế. So sánh các bố trí khả thi thay vì mặc định carry ở góc luôn tốt. Positioning không tốn vàng nhưng tốn thời gian và có thể làm matchup khác xấu đi [7,8].

## 9. Kế hoạch theo giai đoạn

Stage 1: thu thập tài nguyên, giữ các cặp có giá trị. Stage 2: chọn hướng chuỗi/kinh tế và ghép đồ hợp lý. Stage 3: xác định reroll hay level, đánh giá tempo. Stage 4: hoàn thiện bộ khung và ổn định. Stage 5: nâng cấp biên hoặc lên cấp nếu đủ nguồn lực. Stage 6+: tập trung sống sót, matchup và tối ưu thứ hạng. Đây là lịch tham khảo, không phải luật cố định.

## 10. Khung quyết định thực chiến

1. Quan sát trạng thái hợp lệ và thời gian còn lại.
2. Ước lượng sức mạnh hiện tại đối với các đối thủ khả dĩ; đánh giá khả năng bị loại.
3. Tìm nút thắt: tank, carry, thiếu tướng, trang bị, matchup hay kinh tế.
4. Tạo phương án giữ vàng, mua, roll, level, ghép đồ, đổi vị trí, pivot.
5. Ước lượng chi phí và kết quả khi thành công/thất bại; loại phương án không đủ tài nguyên.
6. Chọn mục tiêu hành động, ngân sách và điều kiện dừng.
7. Thực hiện trong thời gian cho phép, ghi nhận kết quả và cập nhật nhận định.

### Tình huống mẫu (giả lập)

A. 70 HP, 50 vàng, đội thắng phần lớn lobby: ưu tiên tích lũy nếu không có cơ hội bảo vệ chuỗi giá rẻ. B. 24 HP, 50 vàng, nhiều trận thua nặng: ưu tiên stabilization; không lên cấp nếu không còn ngân sách mua/roll. C. Cần một bản sao 4 vàng nhưng đối thủ giữ nhiều: tính xác suất còn lại và giá trị carry phụ trước khi commit. D. Đội mạnh nhưng thua một matchup AoE: thử thay vị trí trước khi tiêu vàng. E. Reroll gần hoàn thành nhưng nguy cơ chết: cân nhắc roll dưới mốc lợi tức và giữ ngân sách mua. Những tình huống này là bài tập, không phải quy tắc máy móc.

## 11. Thiết kế AI xuyên mùa

Kiến trúc đề xuất: SetConfig → State Normalizer → Economy/Shop/Board/Matchup/Risk Evaluators → Candidate Generator → Decision Ranker → Explanation. Chỉ dùng dữ liệu được phép, ưu tiên phân tích replay/offline và tuân thủ chính sách nhà phát hành. Không giả định có API live đầy đủ.

| Thành phần | Kỹ thuật khởi đầu | Nâng cao |
|---|---|---|
| Economy | Quy tắc và mô phỏng dòng vàng | Dynamic programming |
| Shop | Xác suất và Monte Carlo | Bayesian uncertainty |
| Board | Feature engineering, heuristic | Gradient boosting, mô hình tập hợp |
| Combat | Dự đoán thắng/thua, sát thương | Simulator có kiểm chứng |
| Composition | Tìm kiếm beam, constraint | Search có mô hình học |
| Position | Sinh phương án và chấm matchup | Search/simulation |
| Strategy | Xếp hạng quyết định theo utility | Planning/MCTS khi có simulator |
| Explanation | Template hoặc LLM | RAG tài liệu theo phiên bản |

### 11.1 Dữ liệu và biểu diễn

State gồm player HP/gold/level/XP/streak, board và bench, shop, item, augment, round, opponent observations, lịch sử và timestamp. Mỗi trường ghi known/unknown, nguồn và thời điểm quan sát. Core feature dùng vai trò, cấp sao, cost tier, chỉ số hiệu dụng, loại kỹ năng, hiệu ứng tộc hệ, tầm đánh, tương tác trang bị; không chỉ one-hot tên tướng. SetConfig chứa pool, odds, giá roll/XP, luật chiến đấu, trait, item, augment, targeting, giới hạn sân/bench và quy tắc ghép đối thủ. Cấu hình phải version theo patch.

Action primitive: buy/sell/roll/lock/XP/equip/combine/place; macro: stabilize, commit, pivot, save. Macro phải được phân rã thành chuỗi hành động hợp lệ. Không đồng nhất hành động chiến thuật với thao tác UI.

### 11.2 Board evaluator và combat predictor

Baseline: tổng sức mạnh tướng có trọng số, frontline EHP, carry DPS proxy, thời gian tung chiêu, số mốc hệ, utility, item fit, synergy, matchup. Không cộng trực tiếp các đại lượng khác đơn vị nếu chưa chuẩn hóa. Dùng ML dự đoán P(win|state, opponent), expected damage và phân phối damage. Thử logistic regression rồi gradient boosting; chỉ dùng deep learning khi dữ liệu và baseline chứng minh nhu cầu. Mô hình đối đầu dùng feature của cả hai đội và tương tác giữa chúng. Đo calibration bằng Brier score/log loss, MAE cho sát thương, phân tích theo stage và set. Thắng combat không đồng nghĩa tối ưu quyết định dài hạn.

### 11.3 Decision ranker

Mục tiêu đề xuất: U(a)=E[u(rank)|s,a]−λ×P(elimination in horizon)−cost thao tác nếu cần. Chú ý không phạt trùng rủi ro đã nằm trong utility. Với dữ liệu hạn chế, dùng proxy sức mạnh/HP/vàng và công bố đây là proxy. Mô phỏng nhiều kết quả roll; không chọn dựa trên trường hợp may mắn nhất. Trả về top 3 phương án, lý do, giả định, rủi ro và điều kiện dừng. Nếu độ tin cậy thấp, báo thiếu dữ liệu.

### 11.4 Dữ liệu và kiểm định

Thu thập replay/VOD hoặc snapshot hợp lệ trước quyết định; nhãn gồm combat win, sát thương, nâng cấp đạt được, thứ hạng cuối. Dữ liệu cuối trận không đủ để học hành động từng vòng. Split theo match và thời gian; giữ riêng patch/set chưa thấy. Không dùng thông tin tương lai (đội hình cuối, HP sau combat, shop tương lai) làm feature trước hành động. So sánh với baseline rule-based; kiểm tra ablation từng evaluator. Dữ liệu quan sát không cho biết kết quả phản thực tế của hành động không chọn; cần simulator đáng tin, thử nghiệm hoặc phương pháp off-policy có giả định rõ. Không quảng cáo cải thiện rank nếu chỉ cải thiện accuracy combat.

## 12. Lộ trình nghiên cứu và học tập

P0: kiểm chứng rules/odds, chuẩn hóa state, gold/HP/tempo, baseline board. P1: matchup prediction, item fit, composition search, pivot, scouting. P2: positioning search, simulator và planning. P3: RL chỉ khi có môi trường đủ chính xác, action masking và đánh giá out-of-set. LLM chủ yếu hỗ trợ diễn giải và tra cứu; không thay engine tính toán.

Bài tập người chơi: ghi 10 trận, mỗi trận chọn 3 quyết định quan trọng, ghi lý do trước khi biết kết quả. Đánh dấu vàng mất do interest, HP mất do giữ đồ/roll muộn, nâng cấp bị bỏ qua, matchup xếp sai. Xem lại VOD, so sánh quyết định với phương án thay thế; đánh giá theo nhiều trận. Học một vài line dùng chung đồ trước khi mở rộng flex.

## 13. Nguồn tham khảo và giới hạn

[1] Riot, Design Pillars of TFT: https://teamfighttactics.leagueoflegends.com/en-au/news/dev/dev-design-pillars-of-tft/

[2] Riot, TFT Set 1 Learnings: https://teamfighttactics.leagueoflegends.com/en-us/news/dev/dev-tft-set-1-learnings/

[3] TFT Lab, kho hướng dẫn xuyên mùa: https://hugolacaci.github.io/tft-lab/guides/

[4] TFT Ninja, kho hướng dẫn cơ chế và chiến thuật: https://tft.ninja/guides

[5] TFT Academy/Frodan, Your Econ Is Holding You Back! (mô tả video, chưa phân tích toàn bộ video): https://www.youtube.com/watch?v=VnwiiG4Ke_I

[6] PivotTFT, How to Scout: https://www.pivottft.com/guides/how-to-scout-tft/

[7] TFT Lab, Positioning: https://hugolacaci.github.io/tft-lab/guides/positioning/

[8] Mobalytics, Positioning Guide: https://mobalytics.gg/blog/tft/tft-positioning-guide-how-to-get-the-most-from-your-units/

[9] TFT Ninja, Scouting: https://tft.ninja/guides/strategy/scouting

[10] Change is Hard: Consistent Player Behavior Across Games with Conflicting Incentives, CHI 2026 (tham khảo định nghĩa flexibility xuyên set; không suy ra chiến thuật tối ưu): https://doi.org/10.1145/3772318.3791411

Các nguồn được rà soát qua kết quả tìm kiếm ngày 25/11/2026; chưa đọc toàn văn mọi bài, chưa phân tích VOD chuyên nghiệp, chưa backtest qua nhiều mùa. Nguồn cộng đồng có thể chứa quy tắc riêng của set; các công thức giản lược và ví dụ trong tài liệu không phải kết quả thực nghiệm. Các mốc, luật và tính khả dụng của dữ liệu cần xác minh theo patch trước khi triển khai. Tài liệu không khẳng định một chiến thuật luôn thắng.

# Phần II — Sổ tay quyết định thực chiến chuyên sâu (v3.0)

Các tình huống dưới đây là ví dụ tự xây dựng, không phải dữ liệu trận đấu thực nghiệm. Mọi con số về luật game là giả định minh họa nếu không có chú thích khác. Mục tiêu là biến khái niệm thành quy trình có đầu vào, hành động, tiêu chí dừng và ngoại lệ.

## 14. Vận hành kinh tế từng vòng

### 14.1 Tính trước ngân sách thay vì chỉ nhìn vàng hiện tại

Trước mỗi vòng, ghi G (vàng), L (cấp), XP còn thiếu, số cặp trên bench, thu nhập chắc chắn, thu nhập có điều kiện. Chọn vòng mục tiêu T và lập ngân sách: vàng dự kiến tại T trừ tiền mua XP, tiền mua tướng và khoản dự phòng. Phần dư mới là ngân sách roll. Khi tính thu nhập, cập nhật lợi tức sau mỗi lần tiêu; không cộng mặc định 10 vàng mỗi vòng.

Ví dụ giả định mỗi vòng nhận 5 vàng cơ bản, tối đa 5 lợi tức, không có thưởng khác. Có 50 vàng, còn ba lần nhận thu nhập trước thời điểm lên cấp, chi phí XP 32 vàng và dự kiến mua tướng 16 vàng. Nếu không tiêu thêm, 50→60→70→80, sau khi lên cấp còn 48, trừ tiền mua tướng còn 32 vàng roll, tương đương 16 lần đổi shop nếu giá 2 vàng. Nếu tiêu 20 vàng ngay, 30→38→46→55, đến mốc mục tiêu chỉ còn 7 vàng roll. Khoản chênh 25 gồm 20 vốn và 5 lợi tức. Chi 20 sớm chỉ hợp lý nếu sức mạnh thu được, thu nhập từ chiến thắng hoặc lượng máu cứu được đủ giá trị.

### 14.2 Giữ cặp hay bán để lấy lợi tức

Tại 29 vàng, bench có một tướng 1 vàng không thuộc bất kỳ hướng khả thi nào: bán để đạt 30 thường có giá trị. Nhưng nếu đó là bản sao thứ hai của tank đang dùng, giữ lại có thể tốt hơn. Đánh giá cặp theo bốn tiêu chí: khả năng xuất hiện bản thứ ba trước khi cần dùng, mức tăng sức mạnh nếu nâng sao, khả năng giữ tướng qua giai đoạn chuyển bài, chi phí vàng và ô bench. Không giữ mười phương án chỉ vì mỗi phương án có vẻ hữu ích riêng lẻ.

Quy trình dọn bench: bán tướng không có vai trò → bán tướng thuộc line đã loại bỏ → bán cặp ít khả năng sử dụng → cuối cùng mới cân nhắc bán cặp chủ lực/tank. Trước khi hết giờ kiểm tra lại mốc lợi tức; không bán quân đang chiến đấu nếu việc đó làm đội yếu hoặc vi phạm quy tắc pha hiện hành.

### 14.3 Bảo vệ chuỗi thắng và chuỗi thua

Đang thắng liên tiếp: kiểm tra các đối thủ có thể gặp, tìm đối thủ mạnh nhất trong nhóm, xác định một nâng cấp có thể thay đổi kết quả. Nếu lên cấp thêm được tank hoặc kích hệ hữu ích, so sánh với roll tìm một trong nhiều cặp. Nếu lên cấp không có quân để thêm và roll chỉ có một mục tiêu hiếm, giữ vàng cũng có thể tối ưu dù mất chuỗi. Không đốt 20 vàng chỉ để bảo vệ khoản thưởng chuỗi nhỏ nếu vẫn không thể thắng.

Đang thua liên tiếp: không đồng nhất thua với bỏ trống sân. Mục tiêu là giảm sát thương nhận mà không phá kế hoạch kinh tế; ưu tiên giết được vài tướng đối phương. Trước khi cố duy trì chuỗi, kiểm tra người chơi yếu hơn, nguy cơ thua vòng PvE, và thời điểm phải chuyển sang thắng. Nếu HP không đủ đến thời điểm tiêu vàng, hủy kế hoạch tích lũy. Không thể bảo đảm thua khi ghép đối thủ ngẫu nhiên.

## 15. Ước tính rủi ro máu và thời điểm tiêu vàng

### 15.1 Ước lượng thiệt hại theo matchup

Ví dụ có 28 HP, năm đối thủ khả dĩ với sát thương nhận dự kiến [0, 5, 9, 14, 18]. Nếu giả định đồng xác suất, kỳ vọng là 9,2 HP/vòng. Nhưng không được kết luận chắc chắn sống ba vòng. Với hai vòng độc lập và phân phối không đổi, có 4/25 cặp kết quả có tổng sát thương >=28 (16% nguy cơ bị loại). Đây là mô hình thô: đối thủ thực tế không nhất thiết đồng xác suất, kết quả không độc lập và cả lobby có thể nâng cấp.

Cần ước tính cả kịch bản thuận lợi, trung bình, xấu; riêng kịch bản xấu dùng để quyết định liệu có đủ thời gian chờ vòng sau hay không. Nếu 28 HP, gặp một đối thủ mạnh có thể mất 18, chờ thêm một vòng sẽ khiến nhiều matchup trở thành trận sinh tử. Roll khi còn hai mạng thường cho phép sửa sai tốt hơn roll ở vòng cuối.

### 15.2 Quyết định stabilize

Bước 1: xác định nguyên nhân yếu nhất (tank, damage, số lượng quân, trang bị, positioning). Bước 2: liệt kê nâng cấp khả thi ngay tại cấp hiện tại. Bước 3: ước lượng tiền và xác suất hoàn thành. Bước 4: đặt điểm dừng cụ thể, ví dụ nâng tank 2 sao và thêm một nguồn sát thương phụ; không yêu cầu cả đội hoàn hảo. Bước 5: sau mỗi nâng cấp lớn đánh giá lại matchup và nguy cơ bị loại; nếu đã đủ an toàn thì dừng. Nếu hết ngân sách mà vẫn yếu, dùng quân thay thế thay vì giữ slot trống chờ tướng lý tưởng.

## 16. Chọn line, opener và chuyển đội hình

### 16.1 Xây dựng từ tài nguyên thực tế

Tạo 2–3 line ứng viên. Với mỗi line ghi: carry chính/phụ, tank, loại đồ, tướng giữ đồ, cấp roll, số bản sao cần, lõi tương thích, tướng tranh chấp, độ mạnh khi chưa hoàn thành và trần sức mạnh. Loại line không thể thực hiện vì thiếu điều kiện bắt buộc, nhưng phân biệt đồ không hoàn hảo với đồ không sử dụng được.

Ví dụ opener có tank 2 sao, carry vật lý 2 sao, hai linh kiện công vật lý và một linh kiện thủ. Line A dùng carry vật lý đắt tiền, line B dùng carry vật lý rẻ hơn để reroll, line C dùng carry phép. A và B có thể chia sẻ trang bị; C có chi phí chuyển cao hơn nếu đã ghép đồ chuyên biệt. Nếu có sáu bản sao carry B từ sớm và ít tranh, xem xét B; nếu chỉ hai bản sao và kinh tế tốt, A có thể phù hợp. Không quyết định bằng số bản sao duy nhất: còn phải xét khả năng scaling, chất lượng lõi và tướng hỗ trợ.

### 16.2 Item holder và bàn giao trang bị

Tướng giữ đồ cần dùng được đồ hiện có, mạnh ngay, dễ thay thế và không phải mắt xích bắt buộc của đội cuối. Trước khi bán holder, chuẩn bị chủ lực mới và kiểm tra đội hình sau bán còn đủ quân, đủ frontline và hệ không. Carry mới 1 sao có thể yếu hơn holder 2 sao; cân nhắc giữ holder thêm một vòng cho tới khi nâng cấp. Quy tắc gỡ đồ, máy tháo đồ và việc tự trả đồ khi bán phải kiểm tra theo phiên bản.

### 16.3 Pivot từng bước, không phá cả bàn

Giữ các tank và utility dùng chung. Mua carry ứng viên khi xuất hiện; mua bộ khung mới trên bench; xác định tướng thay thế từng slot; chuyển đồ ở bước cuối khi carry mới đủ sức mạnh. Nếu chỉ còn ít thời gian, ưu tiên thay carry hoặc tank đơn lẻ, tránh chuyển toàn bộ đội hình. Không tiếp tục roll chỉ vì đã đầu tư nhiều vàng trước đó: đó là chi phí chìm. Chỉ xét tài nguyên còn lại và khả năng hoàn thành từ trạng thái hiện tại.

## 17. Rolldown: xác suất, quy trình, quản lý thời gian

### 17.1 Tính khả năng hit nhiều bản sao

Giả sử p=0,024 mỗi ô, roll 30 vàng được 75 ô, kỳ vọng 1,8 bản sao. Mô hình nhị thức cho P(X>=k)=1−sum[j=0..k−1] C(n,j)p^j(1−p)^(n−j). P(hit ít nhất một) khoảng 83,8%; P(hit ít nhất hai) khoảng 53,9%; P(hit ít nhất ba) khoảng 26,8%. Kỳ vọng 1,8 không có nghĩa chắc chắn nhận hai bản sao. Mô hình cố định p bỏ qua việc mua tướng làm giảm kho, shop lấy mẫu không hoàn lại trong từng lần và đối thủ mua/bán đồng thời.

Nếu đối thủ giữ nhiều tướng mục tiêu khiến p giảm còn 0,012, xác suất hit ≥1 sau 75 ô còn khoảng 59,5%. Trước khi theo đuổi 3 sao, kiểm tra điều kiện số bản sao còn có thể mua được; nếu thiếu về mặt số lượng, không roll với kỳ vọng hoàn thành trừ khi có cơ chế hợp lệ bổ sung bản sao hoặc đối thủ bán.

### 17.2 Roll để tìm nhiều nâng cấp

Ví dụ ở cấp hiện tại có ba cặp tank/carry/support; mỗi mục tiêu có xác suất riêng. Roll tìm bất kỳ nâng cấp hữu ích nào thường hiệu quả hơn chỉ tìm một champion. Nhưng không cộng xác suất hit trên cả shop một cách máy móc, vì có giao nhau. Sau khi hit tank, mục tiêu và phân phối giá trị đổi: có thể dừng nếu tank là điểm nghẽn, hoặc tiếp tục nếu carry vẫn thiếu sát thương.

### 17.3 Checklist rolldown

Trước roll: scout tranh bài, chọn cấp, đặt ngân sách mua quân, lập danh sách ưu tiên A (nâng cấp ngay), B (phương án thay thế), C (chỉ mua nếu còn vàng/bench). Trong roll: mua A trước, giữ B nếu không phá ngân sách, xử lý nâng sao để giải phóng ô; định kỳ nhìn vàng và đồng hồ. Sau roll: đưa tướng lên sân, ghép đồ, kích hệ, xếp vị trí, kiểm tra slot trống. Nếu còn một bản sao thiếu nhưng phải bán nhiều tank để có tiền roll, đánh giá lại rủi ro thay vì tự động all-in.

## 18. Mổ xẻ giao tranh và xây dựng strongest board

### 18.1 Đọc giao tranh theo thứ tự thời gian

Ghi thời điểm tank đầu chết, carry tung chiêu lần đầu, carry chết, kẻ địch dùng khống chế, số quân còn sống cuối trận. Phân biệt chết vì thiếu chống chịu, bị chọn mục tiêu trực tiếp, bị khóa kỹ năng, hay sát thương diện rộng. Bảng tổng sát thương không nói đầy đủ giá trị: sát thương lên lá chắn hoặc mục tiêu hồi phục có thể ít hiệu quả; khống chế và buff có thể quyết định thắng dù người tạo hiệu ứng gây ít sát thương.

Ví dụ tank chết ở giây 4, carry cần 7 giây mới dùng kỹ năng, cả hai đều có đồ. Thử tăng khả năng chống chịu hoặc đổi nguồn mana để carry sử dụng kỹ năng sớm hơn. Nếu tank giữ được 15 giây nhưng carry không kết liễu ai, ưu tiên sát thương, giảm kháng hoặc tập trung mục tiêu. Chỉ thay một biến nếu muốn chẩn đoán; so sánh nhiều trận tương tự.

### 18.2 So sánh hai quân cho một ô sân

Đánh giá bằng delta: quân mới đóng góp bao nhiêu damage, tanking, CC, buff, debuff; khi bỏ quân cũ mất những gì; mốc hệ nào thay đổi; vị trí nào trở nên khó xếp; quân nào có khả năng nâng sao tiếp. Một tướng kích hệ yếu có thể đáng dùng nếu tăng sức mạnh của ba chủ lực; ngược lại, mốc hệ chỉ tăng chỉ số cho quân không có đồ có thể kém hơn thêm tank mạnh. Không dùng tổng giá tướng làm điểm sức mạnh duy nhất.

### 18.3 Tối ưu sát thương hiệu dụng

Ví dụ 2.000 HP, 100 giáp tương ứng 4.000 EHP trước sát thương vật lý. Thêm 400 HP tạo 800 EHP; thêm 40 giáp cũng tạo 800 EHP trong mô hình này. Nếu đối thủ chủ yếu gây phép, tăng giáp không đem lại lợi ích tương đương. Với sát thương hỗn hợp có thể dùng xấp xỉ tốc độ mất máu = DPS vật lý×100/(100+giáp) + DPS phép×100/(100+kháng phép) + DPS chuẩn. Thời gian sống ≈ HP/tốc độ mất máu khi bỏ qua hồi phục, lá chắn, burst và biến động mục tiêu.

## 19. Trang bị và lõi: ra quyết định trong điều kiện thiếu lựa chọn

### 19.1 Đánh giá từng món đồ

Với carry, ghi loại sát thương, scaling, tốc đánh, mana khởi đầu/tối đa, thời gian khóa mana, số mục tiêu, tầm đánh, khả năng sống sót và điều kiện proc. Xác định điểm nghẽn trước khi chọn thuộc tính. Carry cần dùng chiêu thường xuyên không mặc định mọi đồ mana đều tối ưu: nếu đã đủ tốc độ cast hoặc kỹ năng khóa mana lâu, giá trị biên giảm. Tank cần kháng phù hợp lobby và máu để tận dụng kháng; đồ hồi phục giảm hiệu quả khi bị anti-heal. Kiểm tra hiệu ứng trùng lặp, giới hạn và cách cộng dồn theo patch.

Slam hay giữ: liệt kê món ghép được, line nào sử dụng, số vòng sử dụng dự kiến, lợi ích giữ máu và chi phí mất lựa chọn tương lai. Nếu một món tốt cho hai hướng khả thi và có thể giúp thắng ngay, ưu tiên hơn linh kiện chờ BIS chưa chắc xuất hiện. Nếu ghép sẽ khóa hướng không phù hợp hoặc đang chuẩn bị nhận phần thưởng cho phép chọn đồ, việc chờ có thể có giá trị.

### 19.2 Chọn lõi bằng kế hoạch triển khai

Với mỗi lõi, trả lời: hiệu ứng có tác dụng ngay không, cần điều kiện gì, khi nào hoàn vốn, đội nào hưởng lợi, có làm mất tính linh hoạt hay không, có đủ máu chờ payoff không. Lõi kinh tế cho 12 vàng tương lai không bằng 12 vàng hiện tại nếu sắp bị loại. Lõi tăng sức mạnh cho một nhóm tướng có thể tốt dù thống kê chung thấp nếu đội đang sở hữu đúng quân và đồ. Khi đọc thống kê, phân biệt pick rate, average placement, sample size và điều kiện chọn; người chơi mạnh hoặc opener thuận lợi có thể tự chọn lõi và tạo selection bias.

## 20. Scouting và xếp cờ theo matchup

Quy trình quan sát trước khi roll: đếm bản sao mục tiêu trên sân và bench, ghi những đối thủ có dấu hiệu commit, phân biệt holder tạm với carry cuối; kiểm tra cấp và khả năng tiêu vàng sắp tới nếu thông tin đó có thể quan sát hợp lệ. Trước combat: xác định nhóm đối thủ có thể gặp theo thông tin client thực sự cung cấp; không giả định biết chắc người tiếp theo.

| Tình huống | Thao tác thử | Điều cần kiểm tra |
|---|---|---|
| Carry địch bắn vào tank gần nhất | Đặt tank khỏe ở hướng chạm đầu | Có bị dồn damage làm chết trước khi cast không? |
| Hai tank địch xa nhau | Dồn carry và frontline về một phía | Đường di chuyển có khiến carry bước lên không? |
| AoE tập trung vùng đông quân | Giãn cách carry và support | Có mất buff phạm vi nhỏ không? |
| Kỹ năng nhắm mục tiêu xa | Đặt quân rẻ làm mồi xa hơn | Quy tắc chọn mục tiêu và tie-break thực tế |
| Carry cận chiến chết sớm | Đặt hàng sau frontline hoặc lệch mép | Đường tiếp cận và nguy cơ bị kẹt |
| CC lớn ở đầu combat | Tách hai nguồn sát thương | Có bị cả hai dính cùng một vùng không? |

Khi nhiều đối thủ khả dĩ, lựa chọn vị trí theo kỳ vọng và rủi ro thua nặng. Ví dụ vị trí A có xác suất thắng 70% trước X, 20% trước Y; B lần lượt 50%, 55%. Nếu X,Y đồng xác suất, B đạt 52,5% so với 45% của A. Nếu X xuất hiện với xác suất 80%, A đạt 60% so với 51% của B. Đây là ví dụ toán học, các xác suất không phải dự báo thực tế. Với HP thấp, còn phải xét xác suất nhận sát thương gây loại, không chỉ tỷ lệ thắng.

## 21. Bốn tình huống tổng hợp

**A – Mở đầu mạnh:** 90 HP, 30 vàng, nhiều quân 2 sao, có đồ ghép dùng chung. Ưu tiên giữ sức mạnh hiện có; kiểm tra cấp thêm có tạo nâng cấp thực sự; nếu không, tích lũy. Duy trì hai line tương thích đồ. Sai lầm: roll liên tục tìm đội hình cuối khi bàn hiện tại đã thắng tốt.

**B – Mở đầu yếu nhưng giàu:** 60 HP, 60 vàng, ít nâng sao, đối thủ bắt đầu tiêu tiền. Tính số vòng sống trong kịch bản xấu; cân nhắc roll nhỏ tìm tank/carry tạm hoặc lên cấp nếu thêm quân có tác dụng rõ. Không được xem 60 vàng là tín hiệu tự động fast 9. Dừng khi thiệt hại dự kiến giảm đủ để đến mốc kế tiếp.

**C – Reroll bị tranh:** có sáu bản sao carry, đối thủ giữ năm bản sao; cần thêm ba. Kiểm tra tổng pool và số bản sao đang bị giữ khác. Nếu vẫn đủ, đánh giá xác suất và thời gian; nếu không khả thi, chuyển mục tiêu sang carry thay thế hoặc giữ 2 sao và lên cấp. Không bán ngay toàn bộ đội nếu line hiện tại vẫn mạnh.

**D – Cuối trận thấp máu:** còn 12 HP, 25 vàng, một cặp tank và carry 2 sao, hai đối thủ mạnh. Ưu tiên phương án nâng cấp ngay; chỉ mua XP nếu đủ lên cấp và có quân thêm tạo lợi ích. Scout vị trí đối thủ, dùng linh kiện còn lại và bảo đảm không để vàng vô ích nếu trận sau có thể là cuối. Nếu đã thắng chắc các matchup khả dĩ thì vẫn có thể giữ một phần vàng để nâng trần.

## 22. Quy trình học và kiểm chứng xuyên mùa

Mỗi replay ghi trạng thái TRƯỚC quyết định: round, HP, gold, level/XP, đội, bench, đồ, lõi, shop, thông tin đối thủ có sẵn, quyết định và lý do. Sau đó mới ghi outcome, damage nhận, vàng còn và placement. Chấm lỗi theo nhóm: nhận diện trạng thái sai, chọn mục tiêu sai, dự toán sai, thao tác chậm, hoặc ngẫu nhiên bất lợi dù quyết định hợp lý. Không dùng kết quả cuối trận để giả định người chơi có thể biết trước.

Thực hiện các bài tập riêng: 10 trận tập dự toán ngân sách; 10 trận đo máu mất khi chờ power spike; 10 trận theo dõi ba line ứng viên; 10 trận xem lại nguyên nhân thua combat; 10 trận ghi thay đổi positioning và giả thuyết. Số trận này chỉ là gợi ý học tập, không đủ để chứng minh hiệu quả thống kê. Đối với AI, dùng cùng schema ghi nhận và kiểm định trên các trận, patch và set tách biệt. Chỉ sử dụng dữ liệu được phép; thiết kế công cụ phân tích ngoài trận hoặc replay, kiểm tra chính sách Riot trước khi triển khai tính năng hỗ trợ trực tiếp.

## 23. Nguồn bổ sung và mức độ bằng chứng

[11] TFT Lab, Scouting: https://hugolacaci.github.io/tft-lab/guides/scouting/ — tham khảo cách gắn quan sát với quyết định.

[12] TFT Ninja, Stage-by-stage: https://tft.ninja/guides/advanced/stage-by-stage — tham khảo cấu trúc game plan; không sao chép lịch cấp, odds hoặc damage của một set thành luật xuyên mùa.

[13] Mobalytics, Economy: https://mobalytics.gg/tft/guides/how-to-manage-your-economy-in-teamfight-tactics-three-strategies — đối chiếu đánh đổi giữa đầu tư sớm và tích lũy.

Phần II tổng hợp và phát triển các khung thực hành từ [3, 4, 9, 11–13]; các tình huống, thuật toán, phép tính là ví dụ phân tích độc lập. Mới rà soát nội dung nguồn qua tìm kiếm, chưa phân tích VOD hoặc thu thập dữ liệu nhiều mùa. Không có bằng chứng thực nghiệm rằng các ngưỡng giả định là tối ưu. Cần xác minh luật theo patch và kiểm chứng các heuristic bằng dữ liệu trước khi dùng làm AI policy.

# Phần III — Cơ chế, định lượng và thuật toán quyết định (v4.0)

## 24. Phân biệt nguyên lý xuyên mùa với luật phiên bản

Riot 13.23 thay đổi đồng thời kho tướng, tỷ lệ shop và sát thương người chơi [14]. Riot 15.1 đưa vào cơ chế vai trò, quy tắc mana và ưu tiên mục tiêu khi đồng khoảng cách [15]. Riot 18.1 loại bỏ việc tự chọn lại mục tiêu chỉ vì vừa thoát khống chế [16]. Ba ví dụ lịch sử này chứng minh không thể coi luật combat của một mùa là bất biến. Nguyên lý bền vững là tối ưu thời gian hoạt động của carry, phân bổ sát thương, tiếp cận mục tiêu quan trọng và đầu tư đúng thời điểm. Luật thực hiện phải gắn patch, mode và nguồn.

Schema tối thiểu cho mỗi luật: rule_id, set_id, patch_from, patch_to, mode, parameters, exceptions, source_url, evidence_level, verified_at. Khi thiếu luật, đánh dấu UNKNOWN; không điền bằng giá trị từ mùa cũ. Ví dụ, tie_breaker và retarget_on_cc_end là hai tham số riêng biệt. Kiểm tra chúng độc lập trước khi mô phỏng giao tranh.

## 25. Phân tích combat từ cơ chế đến kết quả

### 25.1 Vòng đời giao tranh

Khung mô hình đề xuất (không phải thứ tự xử lý nội bộ đã được Riot công bố): khởi tạo chỉ số và buff; chọn mục tiêu; kiểm tra tầm đánh; di chuyển nếu cần; thực hiện đòn đánh hoặc kỹ năng; giải quyết sát thương và hiệu ứng; cập nhật tài nguyên; kiểm tra chết, mục tiêu mới và kết thúc. Một simulator phải tách thời điểm bắt đầu cast, thời điểm hiệu ứng xảy ra và thời điểm kết thúc cast. Không mặc định các sự kiện đồng thời được xử lý theo thứ tự nào.

Ví dụ: carry A dùng kỹ năng tại giây 5, đạn trúng ở giây 6.2; carry B bị hạ ở giây 5.8. Có thể B đã bắt đầu cast nhưng không gây sát thương, hoặc kỹ năng vẫn tồn tại sau khi chết. Đây là hai hành vi khác nhau, cần kiểm chứng theo kỹ năng. Nếu chỉ lấy tổng DPS, mô hình không phân biệt được.

### 25.2 Targeting và pathfinding

Đánh giá theo bốn lớp: mục tiêu đòn đánh, mục tiêu kỹ năng, đường đi tới mục tiêu, điều kiện retarget. Một tướng có thể đánh tank gần nhất nhưng dùng chiêu vào mục tiêu xa nhất; không suy ra cái thứ hai từ cái thứ nhất. Hướng dẫn positioning của Mobalytics [17] hữu ích để hình thành giả thuyết về tầm đánh và tắc đường, nhưng các suy đoán về tie-break phải nhường cho patch note chính thức.

Để tính khoảng cách lục giác, chuyển tọa độ offset của sân về axial (q,r) theo đúng quy ước hàng chẵn/lẻ. Khoảng cách = (|dq|+|dr|+|dq+dr|)/2. Đường đi tối thiểu thực tế còn phụ thuộc ô bị chiếm, vùng cấm và luật di chuyển. Có thể dùng BFS cho đồ thị không trọng số; A* khi chi phí đường đi khác nhau. Đây là thuật toán xây dựng simulator, không khẳng định Riot dùng BFS hay A*.

Tình huống: tank A chịu được 10 giây, tank B chịu được 4 giây. Nếu đặt B đối diện phần lớn carry địch, B chết sớm mở đường vào backline. Đổi A sang phía đó có thể kéo dài thời gian carry mình hoạt động. Nhưng nếu địch có đòn xuyên hàng hoặc đánh mục tiêu xa, đổi tank không giải quyết được nguyên nhân; phải đổi vị trí carry hoặc đặt mồi.

### 25.3 Năng lượng và ngưỡng cast

Mô hình mana: M(t)=M0 + mana từ đòn đánh + mana theo thời gian + mana từ sát thương nhận + hiệu ứng khác - mana tiêu hao. Giới hạn, khóa mana và nguồn tạo mana phải lấy theo patch. Nếu giả định 60 mana còn thiếu, 10 mana/đòn, 1.25 đòn/giây, không nguồn khác, cần 6 đòn, khoảng 4.8 giây nếu đòn đầu sau một chu kỳ. Thời điểm thực tế còn phụ thuộc delay đòn đầu và thời gian di chuyển. Tăng tốc đánh 25% giảm thời gian lý tưởng còn 3.84 giây, nhưng không đảm bảo tăng số lần cast nếu combat ngắn hoặc có mana lock.

Đánh giá đồ mana bằng số cast hoàn thành chứ không chỉ mana/giây. Ví dụ combat 12 giây, chu kỳ cast 6 giây so với 5 giây đều có thể chỉ hoàn thành 2 cast; giảm xuống 4 giây có thể tạo cast thứ ba. Hiệu quả là phi tuyến và phụ thuộc thời gian sống.

### 25.4 Định lượng sát thương thực tế

Dùng D_effective = tổng min(sát thương sau giảm trừ, máu mục tiêu còn lại) với giả định không hồi phục giữa các hit. Overkill không giúp giết mục tiêu khác nếu kỹ năng không có cơ chế lan hoặc chuyển sát thương. Ví dụ đòn 900 vào mục tiêu còn 100 máu tạo 100 damage hữu dụng, lãng phí 800. Carry đánh nhiều mục tiêu có thể ít lãng phí hơn nhưng lại thiếu khả năng kết liễu, tạo cơ hội cho tank đối phương hồi máu. Vì thế cần đo time-to-first-kill, time-to-kill-tank, damage uptime, cast completion, effective damage per target và số đơn vị địch sống sót.

Ví dụ 100 giáp, 2000 HP cho EHP vật lý 4000 trong mô hình chuẩn không hiệu ứng khác. Nếu giảm giáp 30% còn 70, EHP còn 3400. DPS vật lý 500 mất khoảng 8 giây trước giảm giáp và 6.8 giây sau giảm giáp. Nếu 70% sát thương của đội là phép, lợi ích giảm giáp của cả đội nhỏ hơn nhiều. Các phép tính này là giả định; cần lấy cơ chế cộng dồn, mức giảm và loại sát thương theo phiên bản.

### 25.5 Giá trị khống chế, hồi phục và utility

Khống chế có giá trị lớn nếu ngăn được cast quan trọng hoặc làm mất uptime của carry. Hai stun 2 giây chồng nhau hoàn toàn chỉ tạo 2 giây gián đoạn; tách nhau có thể tạo 4 giây nếu không có miễn nhiễm. Hồi 1000 HP khi chỉ mất 200 HP chỉ tạo 200 hữu dụng. Lá chắn hết hạn trước khi bị đánh có giá trị thực tế thấp. Anti-heal nên được đánh giá qua lượng hồi phục bị ngăn trong thời gian debuff, không phải chỉ dựa trên việc đối thủ có đồ hồi máu. Đo hiệu ứng theo timeline và tránh tính trùng lợi ích giữa sát thương, khống chế và thời gian sống.

## 26. Xác suất shop nâng cao và ngân sách hữu hạn

### 26.1 Mô hình lấy mẫu không hoàn lại có điều kiện

Giả sử mỗi ô chọn bậc c với xác suất q, sau đó lấy ngẫu nhiên một bản sao trong pool bậc đó; không hoàn lại trong cùng shop. Nếu shop có m ô và K ô bậc c, K ~ Binomial(m,q). Với N bản sao cùng bậc và n bản sao mục tiêu, số mục tiêu X theo Hypergeometric(N,n,K). Do đó P(X=x)= tổng theo k từ x đến m của C(m,k)q^k(1-q)^(m-k) C(n,x)C(N-n,k-x)/C(N,k). Đây là mô hình có điều kiện, chỉ chính xác nếu giả định tạo shop đúng; phải kiểm tra cơ chế đặc biệt, shop đang khóa và ngoại lệ pool.

Giữa hai lần roll, bản sao không mua có thể quay lại pool theo luật hiện hành; bản sao đã mua giảm n và N. Đừng dùng một phân phối hypergeometric cho toàn bộ 100 ô của 20 shop như thể không bản sao nào được trả lại.

### 26.2 Tính ngân sách mua tướng

Ví dụ có 30 vàng, thiếu 2 bản sao tướng 4 vàng. Nếu muốn bảo đảm giữ tiền mua cả hai, ngân sách roll tối đa ban đầu là 22 vàng = 11 lần roll (giả định 2 vàng/lần). Nếu p mỗi ô là 2%, 55 ô độc lập cho P(X>=2)=1-0.98^55-55*0.02*0.98^54, xấp xỉ 30.1%. Không được diễn giải số này là xác suất thật của game vì p thay đổi sau khi mua và còn các nâng cấp khác. Nếu cần giữ 10 vàng lợi tức thì chỉ còn 12 vàng roll. Mục tiêu roll phải có cả tiền mua, không chỉ phí refresh.

### 26.3 Dynamic programming cho quyết định roll

Trạng thái tối giản (g,k,n,N,L), trong đó g là vàng, k là số bản sao đã có. Với mỗi kết quả shop, liệt kê các tập mua hợp lệ, cập nhật g,k,n,N; tối đa hóa giá trị giữa dừng, mua hoặc roll tiếp. Đặt V(s)=max(U_stop(s), E_shop[max_{purchase} V(s')]) khi có đủ vàng và mỗi lần roll giảm g. U_stop phải định lượng cả sức mạnh, vàng còn lại và rủi ro bị loại. Khi chỉ cần tính xác suất hit, U_stop=1 nếu đủ bản sao, 0 nếu thất bại. Khi có nhiều tướng, dùng beam search hoặc Monte Carlo thay vì liệt kê toàn bộ trạng thái.

Ví dụ có 2 cặp tank và 1 cặp carry: roll có ba hướng hit. Nếu mỗi ô có xác suất tổng 6% gặp bất kỳ tướng cần, 25 ô cho xác suất ít nhất một hit khoảng 78.7%, so với 39.7% nếu chỉ nhắm một tướng với p=2%. Nhưng các hit không có giá trị ngang nhau: tank có thể chỉ thêm một ít sức mạnh, carry 2 sao có thể tạo ngưỡng kết liễu mới. Xác suất hit không thay thế hàm giá trị.

### 26.4 Phân tích độ nhạy pool

Với q=25%, N=100, n=8, p=2%. Nếu đối thủ mua thêm 4 bản sao mục tiêu, n=4, N=96, p≈1.04%. Nếu họ mua 20 bản sao khác cùng bậc thay vì mục tiêu, n=8, N=80, p=2.5%. Đây là lý do số tướng khác cùng bậc bị lấy khỏi pool cũng quan trọng. Quan sát đối thủ không đầy đủ nên cần mô hình khoảng: n_min, n_max, N_min, N_max; mô phỏng tình huống xấu và tốt thay vì báo một xác suất chính xác giả tạo.

## 27. Thuật toán tự xây dựng đội hình

### 27.1 Từ dữ liệu đến candidate board

Input: tướng đang có, shop, bench, số ô sân, item, augment, trait, level, vàng, đối thủ. Output: danh sách board khả thi kèm chi phí chuyển đổi. Ràng buộc cứng: không dùng tướng chưa sở hữu trừ phương án mua rõ ràng; không vượt slot; không gán trùng item; tôn trọng giới hạn vật phẩm và đặc tính tướng. Hàm điểm mềm: khả năng thắng, sát thương kỳ vọng nhận, độ ổn định, vàng còn lại, khả năng nâng cấp tương lai, độ tương thích tài nguyên.

Quy trình: tạo lõi gồm carry và tank; thêm tướng mở mốc quan trọng; sinh các phương án thay một hoặc hai quân; ước lượng combat; giữ K phương án tốt và đa dạng; lặp đến khi hết ngân sách tính toán. Không loại bỏ toàn bộ board chỉ vì một mốc trait không kích hoạt. Ví dụ một tank 2 sao thay quân 1 sao chỉ để kích trait có thể thắng dù mất bonus nhỏ; kiểm tra tác động trên toàn đội và trên từng matchup.

### 27.2 Tối ưu tổ hợp bằng beam search

Giả sử 20 đơn vị ứng viên và 8 slot, có C(20,8)=125970 tổ hợp trước cả việc xếp vị trí và đồ. Beam search giữ K board mỗi bước thêm tướng: tạo board con, bỏ trùng, tính điểm proxy, chọn K. Một proxy tốt gồm tank uptime, damage uptime, trait breakpoint, thời gian cast và utility, không đơn thuần tổng cost. Nguy cơ: bỏ sớm một nửa combo yếu nhưng khi đầy đủ lại mạnh. Giảm nguy cơ bằng beam đa dạng theo carry/trait, lưu các nhánh có synergy tiềm năng và kiểm tra các thay đổi hai quân.

### 27.3 Định lượng giá trị biên

Delta(unit)=V(board sau thay)-V(board trước thay). Một support tăng 20% DPS của hai carry tổng 800 DPS có thể tạo thêm 160 DPS lý tưởng; một damage dealer 150 DPS có thể kém hơn dù tự gây sát thương nhiều hơn. Ngược lại nếu support chết trước khi buff, giá trị bằng không. Đánh giá Delta trên phân phối đối thủ, không chỉ một trận. Tách Delta chiến đấu và Delta kinh tế: một quân tốn 4 vàng có thể tăng sức mạnh ngang quân đã sở hữu nhưng làm mất tiền roll.

### 27.4 Item assignment

Với mỗi tướng, tạo các tổ hợp item hợp lệ; tính giá trị kết hợp thay vì cộng điểm từng món. Một item mana có thể yếu khi đứng một mình nhưng tạo cast bổ sung khi kết hợp tốc đánh. Sử dụng search có pruning hoặc integer programming nếu giá trị có thể biểu diễn bằng biến tổ hợp. Đánh giá item trên những carry thay thế để tránh trang bị khóa line. Nếu item không thể tháo bằng quy tắc hiện hành, thêm chi phí bán hoặc công cụ tháo vào phương án chuyển.

## 28. Định lượng quyết định: giá trị vàng, máu và thời gian

Vàng và máu không có tỷ giá cố định. Giá trị biên của vàng là chênh lệch kỳ vọng thứ hạng giữa hai trạng thái chỉ khác một vàng; giá trị biên HP tương tự. Dùng hàm utility U=-E[placement] hoặc điểm giải đấu cụ thể. So sánh hành động bằng E[U(S_next)] sau khi tính mọi kết quả có thể xảy ra. Không cộng trực tiếp HP và vàng với hệ số tự chọn rồi gọi đó là mô hình tối ưu đã chứng minh.

Ví dụ: giữ tiền thêm 2 vòng giúp có 12 vàng bổ sung so với tiêu ngay (giả định từ bảng dự toán). Nhưng 20 HP hiện tại và hai trận thua tiềm năng 11 damage mỗi trận có thể loại người chơi trước khi dùng tiền. Nếu xác suất thua mỗi trận 60%, độc lập có điều kiện, nguy cơ thua cả hai là 36%. Nếu roll ngay giúp giảm rủi ro loại đáng kể thì giá trị 12 vàng phải được so với rủi ro này. Hai trận không thực sự độc lập nếu board thay đổi; đây chỉ là phép tính minh họa.

Quy tắc thực hành: dự toán 2–3 vòng; ghi mốc sức mạnh có thể đạt; tính ngân sách sau tiền mua tướng; đánh giá worst-case; lựa chọn phương án ít hối tiếc. Nếu rủi ro bị loại trước mốc tiếp theo cao, không cố giữ tiền để đạt mốc lý tưởng. Nếu board đã ổn và midgame còn dài, tránh roll vì một nâng cấp nhỏ không thay đổi matchup.

## 29. Tối ưu positioning đa đối thủ

Đặt P là cấu hình vị trí và O_i là ứng viên đối thủ, w_i là xác suất gặp (không suy diễn từ luật ghép đối thủ cũ). Chọn P tối đa hóa tổng w_i E[U(combat(P,O_i))]. Khi còn ít máu, có thể thêm phạt cho xác suất nhận damage >= HP. Ví dụ hai đối thủ đồng xác suất, cách xếp A thắng 80% trước X và 20% trước Y; B thắng 60% cả hai. B có xác suất thắng tổng 60% so với 50% của A. Nhưng nếu X có thể gây 18 damage còn Y chỉ 5 và người chơi còn 10 HP, bảo vệ trước X có thể đáng giá hơn tỷ lệ thắng tổng. Phải tối ưu phân phối damage, không chỉ win rate.

Sinh ứng viên bằng swap carry trái/phải, đổi tank chính, trải đội hình, thay bait, đổi hàng carry cận chiến. Đánh giá bằng simulator hoặc heuristic trước, rồi thử nhiều seed cho ứng viên cuối. Dùng cùng seed để so sánh hai cấu hình nếu simulator cho phép; đo chênh lệch và khoảng bất định. Đừng tuyên bố vị trí tối ưu khi chưa biết targeting hoặc đường đi.

## 30. Quy trình quyết định chi tiết cho người chơi

Trước vòng: xác định số vòng sống, đối thủ nguy hiểm, số vàng cần cho mục tiêu và hướng bài dự phòng. Trong shop: ưu tiên mua hit trực tiếp, kiểm tra cặp, quyết định tiếp tục roll chỉ khi còn ngân sách mua. Trước combat: đặt tank nhận sát thương đúng hướng, kiểm tra carry có thể đánh từ đầu hay phải đi bộ, tách quân yếu khỏi cụm bị AoE, kiểm tra debuff có chạm mục tiêu chính. Sau combat: ghi thời điểm tank chết, carry cast lần đầu, mục tiêu đầu tiên bị hạ, quân không làm gì vì di chuyển, damage nhận. Nếu thua vì vị trí, thử sửa vị trí trước khi tiêu vàng; nếu thiếu sát thương dù tank sống lâu, đầu tư carry; nếu carry chết trước cast, kiểm tra protection và targeting trước khi ghép thêm đồ damage.

Bài tập: ghi 20 combat trong replay, mỗi combat nêu một giả thuyết trước khi xem kết quả. Phân loại nguyên nhân chính và phụ. So sánh dự đoán với thực tế, sửa quy tắc khi sai. Không suy ra quan hệ nhân quả từ một combat; cần nhiều matchup tương đương.

## 31. Thiết kế kiểm chứng và thí nghiệm xuyên mùa

Tách dữ liệu bằng match_id, patch và set; không chia ngẫu nhiên snapshot cùng trận vào train/test. Mỗi dữ liệu chỉ chứa thông tin biết được tại thời điểm quyết định. Label combat gồm win, damage, survivors, cast counts nếu có. Label placement không được dùng như feature. Baseline: dự đoán từ chênh level, số sao, item count; sau đó thêm trait, vai trò, positioning, lịch sử. Báo cáo Brier score và calibration cho win probability; MAE cho damage; sai số theo stage và nhóm đội hình. Ablation bỏ từng nhóm feature để đo đóng góp. Dùng bootstrap theo match, không theo từng snapshot độc lập.

Đánh giá policy khó hơn dự đoán: dữ liệu quan sát chỉ cho biết kết quả hành động đã chọn, không cho biết kết quả hành động khác. So sánh replay chỉ tạo giả thuyết, không chứng minh roll tốt hơn giữ vàng. Cần simulator đã kiểm chứng hoặc nghiên cứu có thiết kế phù hợp. Kiểm tra generalization bằng holdout nguyên set, công bố coverage và lỗi do mechanic chưa biết. Không dùng thông tin ẩn, dữ liệu không được phép hoặc hành động tự động trong trận; ưu tiên môi trường mô phỏng và phân tích sau trận.

## 32. Nguồn mới và giới hạn v4.0

[14] Riot Games, patch 13.23 (lịch sử thay đổi shop, pool, damage): https://teamfighttactics.leagueoflegends.com/en-sg/news/game-updates/teamfight-tactics-patch-13-23-notes/

[15] Riot Games, patch 15.1 (vai trò, mana, targeting): https://teamfighttactics.leagueoflegends.com/en-sg/news/game-updates/teamfight-tactics-patch-15-1-notes-2025/

[16] Riot Games, patch 18.1 (retarget sau CC): https://teamfighttactics.leagueoflegends.com/en-sg/news/game-updates/teamfight-tactics-patch-18-1/

[17] Mobalytics, positioning guide: https://mobalytics.gg/blog/tft/tft-positioning-guide-how-to-get-the-most-from-your-units/

[18] TFT Ninja, tổng mục hướng dẫn cơ chế và chiến thuật: https://tft.ninja/guides

Các nguồn [14–16] là bằng chứng chính thức về thay đổi lịch sử, không phải cam kết luật của mọi phiên bản. [17–18] là hướng dẫn cộng đồng. Các công thức xác suất, DP, beam search, utility, thiết kế thí nghiệm trong phần III là mô hình phân tích đề xuất. Chưa xây simulator, chưa chạy backtest, chưa xác minh thứ tự xử lý sự kiện nội bộ và chưa phân tích VOD Challenger hàng loạt. Không coi ví dụ số là kết quả thực nghiệm.
