# Review #3 deck source

`gen.js` builds `../PlantIQ_Review3_updated.pptx` (PptxGenJS). It recreates the previous Review #3 deck
(`../PlantIQ_Review3.pdf`) with one shared component set and the updated content. `assets/` holds the PES logo, the
leaf icon, the architecture diagram and the demo screenshot extracted from that PDF.

    npm install pptxgenjs@3.12.0 react-icons@5.3.0 react@18.3.1 react-dom@18.3.1 sharp@0.33.5
    node gen.js ../PlantIQ_Review3_updated.pptx

The typeface is Satoshi (Satoshi Light for the cover title). `QA_FONT=Arial node gen.js preview.pptx` builds a preview
copy for machines without Satoshi; `render.ps1` exports slide PNGs through PowerPoint.
