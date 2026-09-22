# Research request d916749c-B1-002

Task B1: Search protocol, literature matrix and bibliography

{
  "id": "B1",
  "title": "Search protocol, literature matrix and bibliography",
  "milestone_id": "data",
  "source_task_ids": [
    "lit-1",
    "lit-2",
    "repair-5"
  ],
  "source_phase_ids": [
    "literature",
    "proposal-repair"
  ],
  "dependencies": [
    "A2a"
  ],
  "gates": [],
  "evidence_requirements": [
    "جست‌وجوی واقعی از پیشنهاد جست‌وجو متمایز است.",
    "نبود نتیجه مساوی اثبات عدم وجود مشابه نیست.",
    "هر مقایسه به منبع قابل بازبینی وصل است.",
    "نام مشابه یا دو Key به‌تنهایی معادل روش یکسان تلقی نشده.",
    "BibTeX Parse می‌شود؛ Duplicate Key و Citation ساختگی وجود ندارد."
  ],
  "inputs": [
    "research/claims.csv",
    "گزارش Novelty قبلی دانشجو، اگر در دسترس است؛ جایگزین منبع اصلی نیست.",
    "research/search-results.csv",
    "Full Text منابع منتخب یا Abstract با برچسب محدودیت",
    "research/literature-matrix.csv"
  ],
  "outputs": [
    [
      "research/literature-protocol.md",
      "queries, databases, dates, criteria, access_limits"
    ],
    [
      "research/search-results.csv",
      "title, authors, year, doi_or_url, query_id, inclusion_status"
    ],
    [
      "research/literature-matrix.csv",
      "paper_id, source, status, embedding_space, detector, content_binding, data, attacks, metrics, locator, limitation"
    ],
    [
      "research/references.bib",
      "BibTeX با Key یکتا و DOI/URL معتبر"
    ],
    [
      "research/citation-audit.csv",
      "citation_key, verified_fields, source_url, access_depth"
    ]
  ],
  "steps": [
    {
      "source_task_id": "lit-1",
      "text": "Queryها را بر اساس Semantic/Instance Binding، Diffusion Watermarking، Image-DCT Detection و Regeneration بنویس."
    },
    {
      "source_task_id": "lit-1",
      "text": "Database، Search Date، بازه زمانی، Inclusion/Exclusion و سطح دسترسی را قبل از انتخاب مقاله ثبت کن."
    },
    {
      "source_task_id": "lit-1",
      "text": "نتایج اولیه را با Title، Authors، Year، DOI/URL و Query ذخیره و Deduplicate کن؛ عدم دسترسی به پایگاه را صریح بنویس."
    },
    {
      "source_task_id": "lit-2",
      "text": "برای نزدیک‌ترین روش‌ها از جمله SEAL و آثار نزدیک شناسایی‌شده در Audit، متن اصلی را بخوان."
    },
    {
      "source_task_id": "lit-2",
      "text": "Embedding Space، Detector، نیاز Inversion/Model، Content Binding، Dataset، Attack و Metric را استخراج کن."
    },
    {
      "source_task_id": "lit-2",
      "text": "برای هر گزاره Page/Section و Evidence Depth ثبت کن؛ Preprint را Peer-reviewed معرفی نکن."
    },
    {
      "source_task_id": "lit-2",
      "text": "تفاوت Image-DCT با Latent-DCT و تفاوت Model-free با Inversion-free را در ستون جدا بنویس."
    },
    {
      "source_task_id": "repair-5",
      "text": "برای منابع استفاده‌شده BibTeX معتبر از ناشر/صفحه اصلی تهیه کن."
    },
    {
      "source_task_id": "repair-5",
      "text": "DOI، عنوان، Authors، سال و Publication Status را با منبع تطبیق بده."
    },
    {
      "source_task_id": "repair-5",
      "text": "Citation Key یکتا ایجاد و منابع بدون دسترسی کامل را علامت بزن."
    }
  ],
  "failure_modes": [
    {
      "source_task_id": "lit-1",
      "text": "اگر Search Access موجود نیست، BLOCKED_INPUT؛ نتیجه جست‌وجو یا Citation اختراع نکن."
    },
    {
      "source_task_id": "lit-2",
      "text": "PDF ناموجود: فقط اطلاعات قابل احراز را ثبت و بقیه را UNKNOWN بگذار."
    },
    {
      "source_task_id": "repair-5",
      "text": "منبع تأییدنشده وارد ادعای قطعی نشود؛ فیلدهای ناقص را گزارش کن."
    }
  ],
  "execution": "DOCUMENT"
}