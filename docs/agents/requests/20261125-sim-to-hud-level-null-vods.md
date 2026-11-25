# Yêu cầu: trường cấp trống ở 9 đoạn VOD trong log schema 2

dataset: 9 file trong `claude/hud-data-set18` @ `1b4c468`: `2924500482-210000`, `-3180000`, `-5380000`, `-8240000`; `2926218384-10725000` (1,6%), `-1390000`, `-3852000`, `-6030000`, `-8080000`. Trường `level` gần như luôn null trong khi `gold` đọc được (50–66%).
fields: `level`, khả năng đọc từ vùng cấp (xem `scripts/hud-campaign/*.json` cho các VOD này).
schema: không đổi.
why: nhìn số liệu, đây là lỗi profile vùng đọc cấp của các VOD đó, không phải nhiễu ngẫu nhiên, vì cùng VOD đó vàng đọc được. Thiếu cấp làm mất khả năng suy ra mua XP và làm mất một nửa dữ liệu để đo tỷ lệ cửa hàng theo cấp.
unblocks: đo tỷ lệ cửa hàng theo cấp (U2), nhãn mua XP.
deadline:
status: mở
