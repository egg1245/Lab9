# DormChef - QUICK SUMMARY FOR SHARING

## 🍳 What is DormChef?

A web application that **generates personalized recipes** for university students using **AI (Qwen LLM)**.

**Problem:** Students in dorms have limited cooking equipment and random ingredients. Hard to find recipes that work.

**Solution:** Users input ingredients + select an appliance (toaster, microwave, air fryer, etc.) → AI generates step-by-step recipe.

---

## 🎯 Key Features

✅ **AI Recipe Generation** - Uses real Qwen LLM (not mock)  
✅ **Multi-Appliance Support** - Use 1 or multiple appliances  
✅ **Custom Appliances** - Add your own kitchen tools  
✅ **Recipe History** - Save & browse past recipes  
✅ **Dark Mode** - Toggle light/dark theme  
✅ **Multilingual** - English & Russian support  
✅ **Fully Dockerized** - Deploy anywhere in 2 commands  

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI (Python) |
| **Database** | PostgreSQL |
| **Frontend** | Vanilla JS + Tailwind CSS |
| **LLM** | Qwen Code CLI (real AI) |
| **Deployment** | Docker + docker-compose |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/egg1245/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# Deploy
docker-compose up -d

# Access
Open: http://localhost:8000
```

That's it! 🎉

---

## 📊 Current Status

| Task | Status | Notes |
|------|--------|-------|
| **Code** | ✅ DONE | Fully functional, real LLM working |
| **Deployment** | ✅ DONE | Docker setup, live at 10.93.25.76:8000 |
| **GitHub** | ✅ DONE | Repository: se-toolkit-hackathon |
| **Documentation** | ✅ DONE | README + guides complete |
| **Screenshots** | 🔲 TODO | Need to take 6 screenshots |
| **Demo Video** | 🔲 TODO | Need to record 2-minute demo |
| **Presentation** | 🔲 TODO | Need to create 5-slide deck |

---

## 🎓 What Makes It Special

1. **Real LLM Integration** - Actually calls Qwen, not mocked
2. **Event Stream Parsing** - Handles Qwen's complex JSON output format
3. **Production-Ready** - Error handling, validation, health checks
4. **Full Stack** - Backend + Database + Frontend + LLM
5. **User-Friendly** - Dark mode, multiple languages, real-time updates

---

## 📚 Documentation

- **README:** https://github.com/egg1245/se-toolkit-hackathon/blob/main/README.md
- **Project Summary:** See PROJECT_SUMMARY.md in repo
- **API Docs:** See README.md Usage section
- **Deploy Guide:** See README.md Deployment section

---

## 🔗 Links

- **GitHub:** https://github.com/egg1245/se-toolkit-hackathon
- **Live App:** http://10.93.25.76:8000
- **License:** MIT

---

## 💡 For Questions

- **How to use?** → Open app, enter ingredients, pick appliance, generate!
- **How it works?** → See PROJECT_SUMMARY.md
- **How to deploy?** → See README.md Deployment section
- **Can I contribute?** → Sure! MIT license - fork & PR

---

**Made for:** Lab 9 Hackathon at Innopolis University  
**Date:** April 2026  
**Status:** Fully Working ✅

