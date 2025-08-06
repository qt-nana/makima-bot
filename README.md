# 🌸 Makima Bot — Telegram Anime Companion  
[![Telegram Bot](https://img.shields.io/badge/Chat%20Now-@YourBotUsername-fd79a8?logo=telegram&style=for-the-badge)](https://t.me/YourBotUsername)

**Makima Bot** is your ultimate anime companion featuring 150+ commands across 22+ anime series.  
From character-specific content to live search functionality — Makima's got your anime needs covered.

---

## 💡 Overview

Whether you're looking to:
- Explore **150+ character commands** from popular anime series
- Get **high-quality images, videos, and GIFs** with smart content delivery
- Enjoy **live search functionality** with intelligent tag conversion
- Experience **membership-based privacy controls** with group broadcasting
- Navigate through **20-page interactive help system** with full command listings

**Makima Bot** brings comprehensive anime content discovery with advanced features right into your Telegram chat.

> **"Your personal anime companion with content from 22+ series and intelligent search capabilities."** 🌙💖

---

## ✨ Features

- **150+ Anime Commands** — Extensive library covering Naruto, Bleach, Attack on Titan, Demon Slayer, and more
- **Multi-Media Support** — Images, Videos, and GIF animations with spoiler protection
- **Smart Content Delivery** — Advanced anti-duplicate system with pagination and quality scoring
- **Live Search Engine** — Real-time content search with intelligent tag conversion
- **Interactive Navigation** — Refresh, Next, and Back buttons for seamless browsing
- **Membership Control System** — Privacy modes with channel/group verification
- **Owner Broadcasting** — Bulk message distribution to users and groups
- **Responsive Help System** — 20-page interactive guide with command categorization
- **Group & Private Chat Support** — Full functionality in both environments
- **Performance Monitoring** — Rate limiting and cache management for optimal performance

---

## 🛠️ Commands

### Core Commands
| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `/start`     | 🌸 Meet Makima and explore features           |
| `/help`      | 💝 Interactive 20-page complete guide        |
| `/random`    | 🎲 Surprise content from random sources      |
| `/ping`      | 🏓 Check bot response time                    |

### Featured Anime Series
| Command      | Series                    | Characters Available |
|--------------|---------------------------|---------------------|
| `/naruto`    | 🍃 Ninja World           | 18 characters       |
| `/bleach`    | ⚔️ Soul Society         | 15 characters       |
| `/aot`       | ⚡ Attack on Titan      | 11 characters       |
| `/ds`        | 🗡️ Demon Slayer        | 9 characters        |
| `/jjk`       | ✨ Jujutsu Kaisen       | 8 characters        |
| `/mha`       | 🦸 My Hero Academia     | 25 characters       |
| `/cm`        | ⛓️ Chainsaw Man         | 7 characters        |
| `/op`        | 🏴‍☠️ One Piece          | 2 characters        |
| `/opm`       | 💪 One Punch Man        | 2 characters        |
| `/spyfam`    | 🕵️ Spy x Family        | 2 characters        |

### Popular Character Commands
| Command      | Character                 | Series              |
|--------------|---------------------------|---------------------|
| `/hinata`    | 💜 Hinata Hyuga          | Naruto              |
| `/sakura`    | 🌸 Sakura Haruno         | Naruto              |
| `/rukia`     | ❄️ Rukia Kuchiki         | Bleach              |
| `/orihime`   | 🧡 Orihime Inoue         | Bleach              |
| `/mikasa`    | ⚔️ Mikasa Ackerman       | Attack on Titan     |
| `/nezuko`    | 🌺 Nezuko Kamado         | Demon Slayer        |
| `/nobara`    | 🔨 Nobara Kugisaki       | Jujutsu Kaisen      |
| `/power`     | 🩸 Power                 | Chainsaw Man        |
| `/makima`    | 🐕 Makima               | Chainsaw Man        |

### Owner Commands (Restricted)
| Command         | Description                              |
|-----------------|------------------------------------------|
| `/broadcast`    | 📢 Send messages to all users/groups    |
| `/privacy`      | 🔒 Toggle public/membership modes       |

---

## ⚙️ Tech Stack

- **Language:** Python 3.8+
- **Framework:** [aiogram](https://github.com/aiogram/aiogram) 3.x (Async Telegram Bot API)
- **HTTP Client:** aiohttp for async API requests
- **API Integration:** Rule34 API for content fetching
- **Environment:** python-dotenv for configuration
- **Deployment:** HTTP server for cloud hosting (Render, Heroku, Railway compatible)
- **Database:** Stateless (in-memory caching and user tracking)

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/makima-bot.git
cd makima-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file with your bot token:
```env
BOT_TOKEN=your_telegram_bot_token_here
```

### 4. Configure Bot Settings
Edit the following variables in `makimav7.py`:
```python
OWNER_ID = your_telegram_user_id  # Replace with your Telegram user ID
```

### 5. Run the Bot
```bash
python makimav7.py
```

---

## 📋 Requirements.txt
```txt
aiogram>=3.0.0
aiohttp>=3.8.0
python-dotenv>=0.19.0
requests>=2.28.0
```

---

## 🔧 Configuration Options

### Privacy Modes
- **Normal Mode (Default):** Requires channel and group membership
- **Public Mode:** Open access for all users

### Membership Requirements
- **Channel:** [@WorkGlows](https://t.me/WorkGlows)
- **Group:** [SoulMeetsHQ](https://t.me/SoulMeetsHQ)

### Content Settings
- **Rate Limiting:** 60 requests per minute
- **Cache Management:** 10,000 content items max
- **Media Types:** Images (.jpg, .png, .webp), Videos (.mp4, .webm), GIFs (.gif)

---

## 🎯 Key Features Breakdown

### Smart Content Delivery System
- **Anti-Duplicate Engine:** Tracks sent content to ensure fresh results
- **Quality Scoring:** Prioritizes high-rated content
- **Pagination System:** User-specific offsets for varied content
- **Fallback Strategy:** Multiple search attempts with different tag combinations

### Live Search Engine
- **Intelligent Tag Conversion:** Automatically converts common phrases to proper tags
- **Character Name Detection:** Smart handling of anime character names
- **Multi-Strategy Search:** Attempts various search patterns for best results

### Interactive Navigation
- **Media Type Selection:** Choose between Images, Videos, and GIFs
- **Refresh System:** Get new content with a single button press
- **Back Navigation:** Easy return to selection menus

### Performance Optimization
- **Async Operations:** Non-blocking API requests and message handling
- **Memory Management:** Automatic cache cleanup and size limits
- **Rate Limiting:** Prevents API abuse and ensures stable performance

---

## 🌸 Usage Examples

### Basic Usage
```
/start - Welcome message and bot introduction
/help - Interactive guide with all commands
/naruto - Browse Naruto series content
/hinata - Specific character content
```

### Interactive Flow
1. Send `/hinata` - Bot shows character image with media type selection
2. Tap "🎬 Videos" - Bot loads video content with navigation buttons
3. Tap "💞 Refresh" - Get new video content
4. Tap "💘 Next" - Send additional video in new message

### Live Search
Simply type any character or anime name in private chat:
```
"sakura haruno" - Searches for Sakura Haruno content
"attack on titan" - Searches for AOT content
"big breasts anime" - Custom tag search
```

---

## 👥 Group Features

- **Automatic Group Tracking:** Bot tracks groups for broadcasting
- **Membership Verification:** Works in groups with membership checks
- **Add to Group Button:** Dynamic invite link generation
- **Reply-based Responses:** Contextual responses in group chats

---

## 🛡️ Security & Privacy

- **Owner-Only Commands:** Restricted access to administrative functions
- **Membership Verification:** Optional channel/group joining requirements
- **Rate Limiting:** API abuse prevention
- **Secure Configuration:** Environment-based sensitive data storage

---

## 📊 Performance Monitoring

The bot includes built-in performance monitoring:
- Content cache size tracking
- User offset management
- API request rate monitoring
- Memory usage optimization

---

## 🔄 Deployment

### Cloud Platforms
- **Render:** Automatic deployment with HTTP server
- **Heroku:** Compatible with Procfile
- **Railway:** Direct Python deployment
- **VPS:** Manual setup with systemd service

### Environment Variables
```env
BOT_TOKEN=your_bot_token
PORT=10000  # For cloud deployment
```

---

## 👤 Creator

**Developed with ❤️ by Asadul Islam (Asad)**

Connect with the developer:

<p align="center">
  <a href="https://t.me/asad_ofc"><img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" /></a>
  <a href="mailto:mr.asadul.islam00@gmail.com"><img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white" /></a>
  <a href="https://youtube.com/@asad_ofc"><img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" /></a>
  <a href="https://instagram.com/aasad_ofc"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" /></a>
  <a href="https://tiktok.com/@asad_ofc"><img src="https://img.shields.io/badge/TikTok-000000?style=for-the-badge&logo=tiktok&logoColor=white" /></a>
  <a href="https://x.com/asad_ofc"><img src="https://img.shields.io/badge/X-000000?style=for-the-badge&logo=twitter&logoColor=white" /></a>
  <a href="https://facebook.com/aasad.ofc"><img src="https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white" /></a>
  <a href="https://www.threads.net/@aasad_ofc"><img src="https://img.shields.io/badge/Threads-000000?style=for-the-badge&logo=threads&logoColor=white" /></a>
  <a href="https://discord.com/users/1067999831416635473"><img src="https://img.shields.io/badge/Discord-asad__ofc-5865F2?style=for-the-badge&logo=discord&logoColor=white" /></a>
</p>

---

## 📄 License

This project is open source and available under the MIT License.

**Attribution appreciated — Spread anime love, not drama! 🌸**

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⭐ Support

If you found this project helpful, please consider:
- ⭐ Starring the repository
- 📢 Sharing with anime enthusiasts
- 💬 Joining our [support group](https://t.me/SoulMeetsHQ)

---

> **Makima Bot** — *Your Personal Anime Companion*  
[Start now → @YourBotUsername](https://t.me/YourBotUsername)