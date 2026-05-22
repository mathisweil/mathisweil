<h1>Hi, I'm Mathis 👋</h1>

**MSc Data Science & Machine Learning @ UCL** &nbsp;·&nbsp; First-Class BSc Computer Science (QMUL)

I work on applied ML research and production engineering. Current focus: LLM efficiency, retrieval, and reinforcement learning.

📍 London &nbsp;·&nbsp; 📫 mathis.weil@outlook.com &nbsp;·&nbsp; 🔗 [LinkedIn](https://www.linkedin.com/in/mathis-weil/)

---

## 🔬 Research

Two research projects from my UCL MSc.

### Eviction-Aware Fine-Tuning for Pruned KV Cache Inference
*UCL Statistical NLP, 2026*

Investigated train-test distribution shift caused by post-hoc KV cache eviction in long-context LLM inference, and proposed LoRA fine-tuning under active eviction as a mitigation.

- Aggressive cache pruning (75 to 85 percent of tokens) collapsed QA F1 from 32.6% to 19.0% on Llama 3.2 1B.
- Eviction-aware fine-tuning recovered performance to 28.9% F1, closing most of the gap with full-cache inference.
- Characterised the adaptation as a specialisation effect using JS divergence, hidden-state drift, attention-mass redistribution, and Jaccard analysis of retained-token sets.

**Stack:** PyTorch · Hugging Face Transformers · PEFT (LoRA) · Llama 3.2 1B · NAMM

🔗 [Code](https://github.com/mathisweil/evo-memory)

### Discrete Diffusion Planners on Craftax & MiniHack
*UCL Open-Endedness & General Intelligence, 2026*

Investigated Remasking Discrete Diffusion Models (ReMDM) as non-myopic planners that refine entire action trajectories globally, rather than committing step by step like autoregressive policies.

- 70% in-distribution win-rate on MiniHack, an order of magnitude above PPO, A2C, DQN, PPO-RNN, and Decision Transformer baselines.
- Highest zero-shot OOD transfer among all tested architectures.
- 25-condition ablation study mapping the failure modes of RL fine-tuning for discrete diffusion planners on Craftax.

**Stack:** PyTorch · JAX · Craftax · MiniHack

🔗 [Craftax Code](https://github.com/mathisweil/craftax-ReMDM-planner) [Minihack Code](https://github.com/mathisweil/minihack-ReMDM-planner)

---

## 🚀 Featured Projects

### SkillFindr · AI Learning Assistant for IBM SkillsBuild
*Final-year capstone in collaboration with IBM*

Semantic search engine over 1,200+ courses, integrated into a Retrieval-Augmented Generation (RAG) chatbot.

- Recall@20 = 0.899, MRR = 0.843, MAP@20 = 0.712.
- Sentence-BERT embeddings stored in a hybrid PostgreSQL + pgvector store.
- FastAPI retrieval layer driving a chatbot front-end.

**Stack:** Python · Sentence-BERT · PostgreSQL · pgvector · FastAPI

🔗 [Code](https://github.com/mathisweil/SkillFindr-SemanticSearchEngine)

### Other notable work

- **Carbon Credits Web Scraper** · Selenium-based scraper for 5,000+ startup profiles, with multithreading delivering a 40% efficiency uplift.
- **Dog Breed Classifier** · ResNet-50 transfer-learning model built in TensorFlow and PyTorch.
- **Groupe Prunay Showcase Site** · Next.js + Tailwind CSS site with integrated database management and server monitoring, shipped during internship.

---

## 🛠️ Tech Stack

**Languages** · Python · SQL · TypeScript · JavaScript · Java · R

**ML & Research** · PyTorch · Hugging Face Transformers · JAX · scikit-learn · PEFT (LoRA) · NumPy · pandas

**Data & Backend** · FastAPI · PostgreSQL · pgvector · MySQL · LangChain · Selenium

**Frontend** · React · Next.js · Tailwind CSS

**Tools** · Git · Linux

---

## 🎓 Education

**University College London** · MSc Data Science & Machine Learning
*2025 to 2026*
Modules: Applied Machine Learning, Introduction to Statistical Data Science, Statistical Natural Language Processing, Information Retrieval & Data Mining, Bayesian Deep Learning, Open-Endedness & General Intelligence, Digital Finance. Capped by a 60-credit MSc Project.

**Queen Mary University of London** · BSc Computer Science
*2022 to 2025* · First Class Honours, 83% overall
Awarded the Final-Year Prize for Outstanding Academic Achievement.

---

## 💼 Currently

- **Postgraduate Teaching Assistant at UCL** supporting 280+ students across Introductory Programming, Computer Architecture & Operating Systems, Software Engineering, and Compilers.
- **Open to graduate roles** in ML engineering, applied research, and data science across London.

---

## 📜 Certifications

- **Probability & Statistics for ML and Data Science** · DeepLearning.AI
- **Mathematics for Machine Learning** (Linear Algebra & Multivariate Calculus) · Imperial College London
- **Cambridge English C1 Advanced** · Score 184 (CEFR C2)

---

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=mathisweil&show_icons=true&theme=radical" alt="GitHub Stats" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=mathisweil&layout=compact&theme=radical" alt="Top Languages" />
</p>
