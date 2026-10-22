# Font tự host (D35, 15/10/2026)

Nguồn: npm `@fontsource/be-vietnam-pro@5.3.0` và `@fontsource/jetbrains-mono@5.3.0` qua cdn.jsdelivr.net, thư mục `files/`. Giấy phép SIL OFL 1.1 (file `OFL-*.txt`).

Be Vietnam Pro: 400, 500, 600, 700, 800. JetBrains Mono: 400, 500. Mỗi độ đậm có ba bộ ký tự: `vietnamese`, `latin-ext`, `latin`. `unicode-range` của từng bộ lấy theo file `tham-khao-fontsource-*-400.css`; plan 2f viết `@font-face` riêng, không import file tham khảo.

```
03d1b589cff172e1a670b3573e731d3380bc326f80cf83b0d3504e3188e2e074  be-vietnam-pro-latin-400-normal.woff2
b621f77d35f777023aa11ca524462d511b4b28a813adbc0e9d15a10fc61dfe4e  be-vietnam-pro-latin-500-normal.woff2
9503dec2a7c532c8331e9600bcafea287a4fd208573b8668d85ab8d8de1863c7  be-vietnam-pro-latin-600-normal.woff2
a193dd87699bd2e18ddf72dc271493ea82a23dad9f5c334d9f2a257b1e05fc30  be-vietnam-pro-latin-700-normal.woff2
7c5d0871188c09339a6eb46948420ed9b11f3d06ea3ff1c5d1cf41b06a3504e7  be-vietnam-pro-latin-800-normal.woff2
f7a2811e471c2973a1179ce39da3ad6bb8082381aa8d1535ccfcbc3d6d78a052  be-vietnam-pro-latin-ext-400-normal.woff2
947d592eb7676914507ff68fc11fcf2cfdecd6ebaf0fa2af6047f66a63ea7d0f  be-vietnam-pro-latin-ext-500-normal.woff2
20cc75daeaaaa0fa8af2b616b2de2b2900f0ce14ae8e9faa47d272cedd93827f  be-vietnam-pro-latin-ext-600-normal.woff2
33d57e5bd840b03921568e08d2be1082d453e55f1ba55f421e41a1aa54e12601  be-vietnam-pro-latin-ext-700-normal.woff2
85a2008e6d5f2381a076d36d38771957b118683d0fff3029844737aff6b96a10  be-vietnam-pro-latin-ext-800-normal.woff2
dc085e2fba3414e5c5bf1e6172f921a9f81c5859946a4ed3d63c1e470d96a9e2  be-vietnam-pro-vietnamese-400-normal.woff2
86341610cbe907eecf461c9159c168d5efb52bb1a33963813a08f520555d8e66  be-vietnam-pro-vietnamese-500-normal.woff2
97658c6f9a384f29a3005c3d96e2a0d1c810192cf68979071c290f5a377a9f99  be-vietnam-pro-vietnamese-600-normal.woff2
4f58af2d1c3e28a9ba14c51c82db2751d78344b75bdcb34de24a1031ebe59da6  be-vietnam-pro-vietnamese-700-normal.woff2
26b241d1d5f489c8a65c1a3c4cdcdb48dd114a9ed7e0c0180182191f087cbe96  be-vietnam-pro-vietnamese-800-normal.woff2
14425ba9c695763c1547f48a206b7aa60350a33ae23de09f0407877f3fcd89eb  jetbrains-mono-latin-400-normal.woff2
cb182feeed4d798ff6961d3c79f7026279448fca0676438aaecb21f3fc39553a  jetbrains-mono-latin-500-normal.woff2
505dfba8ecbe77e82765f36d317ed7ef4ac42719dc5f4ae68d1c483fd22d0d14  jetbrains-mono-latin-ext-400-normal.woff2
879df9319f1cbf633bee1dd489e376a9e1e8c458f4abddcfe381cb83b5e6b027  jetbrains-mono-latin-ext-500-normal.woff2
efc9e0df126ca6dd1c37a022bfe1d664d23b3fcaa32979d2028ecb4c074306c8  jetbrains-mono-vietnamese-400-normal.woff2
bb7b98e92899b511e8f3e99c924142f4421896b2cbc9406c3727c25427662cc9  jetbrains-mono-vietnamese-500-normal.woff2
```
