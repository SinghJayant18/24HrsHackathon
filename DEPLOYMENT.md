# Deployment Guide - 24Hrs Inventory Management System

This guide will help you deploy both the backend and frontend to production.

## 🚀 Quick Deployment Options

### Option 1: Railway (Recommended - Easiest)
Railway can deploy both backend and frontend automatically.

### Option 2: Render + Vercel
- Backend on Render
- Frontend on Vercel

---

## 📦 Backend Deployment (Railway/Render)

### Using Railway:

1. **Sign up/Login to Railway**: https://railway.app
2. **Create New Project** → "Deploy from GitHub repo"
3. **Select your repository**
4. **Add Environment Variables** in Railway dashboard:
   ```
   JWT_SECRET_KEY=your-very-secret-key-here-change-this
   GEMINI_API_KEY=your-gemini-api-key
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   EMAIL_FROM=your-email@gmail.com
   OWNER_EMAIL=owner@email.com
   ```
5. **Set Root Directory**: `./` (root)
6. **Set Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
7. **Deploy!** Railway will automatically detect Python and install dependencies

### Using Render:

1. **Sign up/Login to Render**: https://render.com
2. **Create New Web Service**
3. **Connect GitHub repository**
4. **Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. **Add Environment Variables** (same as Railway above)
6. **Deploy!**

### Backend URL:
After deployment, you'll get a URL like: `https://your-app.railway.app` or `https://your-app.onrender.com`

---

## 🎨 Frontend Deployment (Vercel)

### Using Vercel:

1. **Sign up/Login to Vercel**: https://vercel.com
2. **Import Project** → Select your GitHub repository
3. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. **Add Environment Variable**:
   ```
   VITE_API_BASE_URL=https://your-backend-url.railway.app
   ```
   (Replace with your actual backend URL)
5. **Deploy!**

### Frontend URL:
After deployment, you'll get a URL like: `https://your-app.vercel.app`

---

## 🔧 Local Setup (Before Deployment)

### Backend:
```bash
cd /Users/jayantsingh/24HrsHack
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend:
```bash
cd frontend
npm install
```

---

## 📝 Environment Variables Checklist

### Backend (.env file):
```env
# JWT Authentication
JWT_SECRET_KEY=your-secret-key-change-this

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
OWNER_EMAIL=owner@email.com

# Gemini API
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# Database (SQLite - auto-created)
SQLITE_PATH=./data/app.db

# CORS (for production, set your frontend URL)
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

### Frontend (.env file in frontend/):
```env
VITE_API_BASE_URL=https://your-backend-url.railway.app
```

---

## 🎯 Post-Deployment Steps

1. **Test Registration**: Go to `/register` and create an owner account
2. **Test Login**: Login with your credentials
3. **Add Items**: Create some inventory items
4. **Test Orders**: Create a test order
5. **Check Emails**: Verify email sending works (check SMTP settings)

---

## 🔒 Security Notes

1. **Change JWT_SECRET_KEY** in production
2. **Use strong passwords** for SMTP
3. **Enable 2FA** on Gmail for App Passwords
4. **Set CORS_ORIGINS** to your frontend URL only
5. **Use HTTPS** (Railway/Render/Vercel provide this automatically)

---

## 🐛 Troubleshooting

### Backend not starting:
- Check environment variables are set correctly
- Verify Python version (3.11+)
- Check logs in Railway/Render dashboard

### Frontend can't connect to backend:
- Verify `VITE_API_BASE_URL` is correct
- Check CORS settings in backend
- Ensure backend is running and accessible

### Email not sending:
- Verify SMTP credentials
- Check Gmail App Password is correct
- Check SSL certificate issues (should be fixed in code)

---

## 📞 Support

For issues, check:
- Backend logs in Railway/Render dashboard
- Frontend build logs in Vercel
- Browser console for frontend errors

---

## ✅ Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Environment variables set
- [ ] Registration working
- [ ] Login working
- [ ] Dashboard accessible
- [ ] Email sending working
- [ ] Orders can be created

---

**🎉 Your app is now live! Share the frontend URL with users.**

