# 矢量母版

`moyu-angel-maid-master.svg` 是从最终清晰版 v2 图集追踪得到的双层 SVG 母版：

- 白色轮廓层：每个已使用单元格的宠物剪影；
- 黑色墨线层：面部、头发、服装、翅膀和动作细节；
- 所有图形都是真实 SVG 路径，不嵌入 PNG 或 WebP；
- 画布仍保持 `1536×2288`，便于和运行包逐格对照。

当前 Codex 运行时仍使用根目录的 `spritesheet.webp`。SVG 适合放大检查、再编辑、改色和制作更高分辨率导出；修改 SVG 后，需要重新导出符合 Codex Pet v2 合约的 WebP 图集。

追踪脚本位于 [`tools/build_vector_master.py`](../tools/build_vector_master.py)，依赖 Pillow 和 Potrace。
