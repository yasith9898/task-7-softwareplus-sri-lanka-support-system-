# 🏛️ Citizen Services Portal - Sri Lanka

A comprehensive government services portal built with Flask, MongoDB, and modern web technologies. This platform provides citizens with easy access to 20+ ministry services with multilingual support (English, Sinhala, Tamil).

## 📋 Features

- **Multilingual Support**: English, Sinhala (සිංහල), Tamil (தமிழ்)
- **20+ Ministries**: Complete coverage of government services
- **User Engagement Tracking**: Anonymous analytics for service improvement
- **Admin Dashboard**: Real-time insights with interactive charts
- **Premium Help Suggestions**: AI-ready analytics for identifying users needing assistance
- **CSV Export**: Download engagement data for analysis
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account (free tier) or local MongoDB
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
```bash
cd c:\Users\Hi\Desktop\softwareplus\task6
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
The `.env` file is already configured with MongoDB Atlas connection:
```

```

5. **Seed the database**
```bash
python seed_data.py
```

6. **Run the application**
```bash
python app.py
```

7. **Access the portal**
- **Public Portal**: http://127.0.0.1:5000/
- **Admin Dashboard**: http://127.0.0.1:5000/admin
  - Username: `admin`
  - Password: `admin123`

## 📁 Project Structure

```
citizen-portal/
├── app.py                 # Flask application with all routes
├── requirements.txt       # Python dependencies
├── seed_data.py          # Database seeding script
├── .env                  # Environment configuration
├── templates/
│   ├── index.html        # Public portal interface
│   ├── admin.html        # Admin dashboard
│   └── manage.html       # Service management page
├── static/
│   ├── style.css         # Modern, responsive styles
│   ├── script.js         # Public portal JavaScript
│   ├── admin.js          # Admin dashboard logic
│   └── manage.js         # Service management logic
└── README.md             # This file
```

## 🎯 Usage

### For Citizens

1. **Select Language**: Choose between English, සිංහල, or தமிழ்
2. **Browse Ministries**: Click on any ministry from the left sidebar
3. **Select Service**: Choose a subservice from the middle panel
4. **Get Information**: Click on a question to view answers, downloads, and locations
5. **Provide Feedback**: Optionally share your demographics to help improve services

### For Administrators

1. **Login**: Access `/admin` with credentials (admin/admin123)
2. **View Analytics**: 
   - Age distribution of users
   - Job categories
   - Popular services and questions
   - Premium help suggestions
3. **Export Data**: Download engagement data as CSV
4. **Monitor Engagements**: View recent user interactions in real-time

## 📊 Admin Dashboard Features

- **Age Distribution Chart**: Bar chart showing user demographics
- **Job Categories**: Pie chart of user occupations
- **Popular Services**: Doughnut chart of most accessed services
- **Top Questions**: Bar chart of frequently asked questions
- **Premium Suggestions**: Identifies users who need additional help
- **Engagement Table**: Detailed view of all user interactions
- **CSV Export**: Download complete engagement data

## 🔐 Security Notes

**⚠️ Important for Production:**
- Change default admin password in `.env`
- Use bcrypt for password hashing (currently plaintext)
- Enable HTTPS
- Add rate limiting
- Implement CSRF protection
- Validate and sanitize all inputs
- Use environment-specific secrets

## 🤖 AI Integration (Future)

The platform is designed to support AI-powered features:

### Knowledge Retrieval
- Vector database integration (FAISS/Pinecone/Weaviate)
- Document embeddings for semantic search
- LLM-powered answer generation
- Source citation and verification

### Recommendation System
- Collaborative filtering for service suggestions
- Pattern recognition in user behavior
- Automated premium help triggers
- Personalized service recommendations

### Implementation Steps
1. Scrape and clean official government documents
2. Generate embeddings using OpenAI or SentenceTransformer
3. Index documents in vector database
4. Implement `/api/ai/search` endpoint
5. Train ML models on engagement data
6. Deploy recommendation engine

## 🌐 API Endpoints

### Public Endpoints
- `GET /` - Public portal homepage
- `GET /api/services` - List all services
- `GET /api/service/<id>` - Get specific service
- `POST /api/engagement` - Log user engagement
- `POST /api/ai/search` - AI-powered search (placeholder)

### Admin Endpoints (Authentication Required)
- `GET /admin` - Admin dashboard
- `POST /admin/login` - Admin login
- `POST /api/admin/logout` - Admin logout
- `GET /api/admin/insights` - Analytics data
- `GET /api/admin/engagements` - Recent engagements
- `GET /api/admin/export_csv` - Export data as CSV
- `GET /api/admin/services` - List services (admin)
- `POST /api/admin/services` - Create/update service
- `DELETE /api/admin/services/<id>` - Delete service

## 🎨 Design Features

- **Modern Gradient Backgrounds**: Eye-catching color schemes
- **Glassmorphism Effects**: Frosted glass UI elements
- **Smooth Animations**: Micro-interactions for better UX
- **Responsive Layout**: Mobile-first design approach
- **Custom Scrollbars**: Styled for consistency
- **Interactive Charts**: Chart.js visualizations
- **Premium Typography**: Inter font family

## 📦 Dependencies

- **Flask 2.3.2**: Web framework
- **flask-cors 3.0.10**: CORS support
- **pymongo[srv] 4.4.1**: MongoDB driver
- **dnspython 2.4.2**: DNS resolution for MongoDB
- **python-dotenv 1.0.1**: Environment variable management
- **Chart.js**: Frontend charting library (CDN)

## 🔧 Troubleshooting

### Database Connection Issues
- Verify MongoDB Atlas credentials in `.env`
- Check IP whitelist in MongoDB Atlas
- Ensure internet connectivity

### Port Already in Use
```bash
# Change PORT in .env file
PORT=5001
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 📝 License

This project is created for educational and government service purposes.

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review MongoDB Atlas connection settings
3. Verify all dependencies are installed
4. Check Python version compatibility

## 🚀 Deployment

### Production Checklist
- [ ] Change all default passwords
- [ ] Enable HTTPS
- [ ] Set up proper authentication
- [ ] Configure production database
- [ ] Add rate limiting
- [ ] Enable logging and monitoring
- [ ] Set up backup strategy
- [ ] Configure CDN for static files
- [ ] Implement caching
- [ ] Add error tracking (Sentry)

---

**Built with ❤️ for Sri Lankan Citizens**


PS C:\Users\Hi\Desktop\softwareplus\task6> venv\Scripts\python app.py
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.102.53.207:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 122-895-577


run project command

python app.py

http://127.0.0.1:5000/admin/login

admin/admin123


