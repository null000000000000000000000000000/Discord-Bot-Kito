# TAIKO Bot

A modular Discord bot built with `discord.py`, featuring a hybrid command system, SQLite database, and extensive moderation, economy, leveling, and utility features.

## Features

### Core
- Hybrid commands (slash + prefix)
- Async SQLite database with SQLAlchemy
- Modular Cog architecture
- Comprehensive error handling
- Command cooldowns and permissions
- Maintenance mode

### Systems
| System | Commands |
|--------|----------|
| **Moderation** | `/warn`, `/mute`, `/unmute`, `/kick`, `/ban`, `/unban`, `/purge`, `/history` |
| **AutoMod** | Anti-spam, anti-raid, bad-word filter |
| **Welcome** | Welcome/goodbye messages, auto-role |
| **Tickets** | Create/close tickets with buttons and modals |
| **Economy** | `/balance`, `/daily`, `/work`, `/shop`, `/buy`, `/give` |
| **Leveling** | XP on messages, `/rank`, `/leaderboard` |
| **Fun** | `/8ball`, `/coinflip`, `/dice`, `/choose`, `/rate`, `/joke`, `/meme`, `/ship` |
| **Profile** | `/profile`, `/rank` card |
| **Achievements** | Auto-grant on milestones |
| **Reputation** | `/rep`, `/repleaderboard` |
| **Giveaways** | `/giveaway`, `/endgiveaway` with auto-end |
| **Reaction Roles** | `/rrpanel` with toggle buttons |
| **Polls** | `/poll` with button voting |
| **Suggestions** | `/suggest`, `/spanel` with approve/reject |
| **Reports** | `/report` modal, `/reportmsg` |
| **Reminders** | `/remind` with duration parsing |
| **AFK** | `/afk` with auto-notify |
| **Custom Commands** | `/cccreate`, `/ccdelete`, `/cclist` |
| **Components V2** | `/v2demo`, `/sectiondemo`, `/mediademo` |
| **Premium** | `/premium`, `/upgrade`, `/premiumstatus` |
| **AI** | `/ai` chat with Groq, `/aiclear`, `/aisetup` |
| **Analytics** | `/stats`, `/commandstats` |
| **Security** | Anti-nuke detection, `/securitystatus` |
| **Dashboard** | `/dashboard`, `/setlogchannel`, `/setmuterole` |
| **Owner** | `/eval`, `/botstats`, `/reload`, `/maintenance`, `/announce`, `/emergency` |
| **Logging** | Comprehensive event logging |

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your values:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   OWNER_IDS=123456789012345678,987654321098765432
   DATABASE_URL=sqlite+aiosqlite:///data/taiko.db
   PREFIX=!
   LOG_LEVEL=INFO
   EMBED_COLOR=0x5865F2
   ERROR_COLOR=0xED4245
   SUCCESS_COLOR=0x57F287
   MAINTENANCE_MODE=false
   MAINTENANCE_MESSAGE=Bot is under maintenance.
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python run.py
   ```

## Project Structure

```
taiko-bot/
├── bot.py                 # Core bot instance
├── run.py                 # Entry point
├── requirements.txt       # Dependencies
├── .env.example          # Environment variables template
├── verify.py             # Verification script
├── cogs/                 # Command modules
│   ├── utility.py
│   ├── moderation.py
│   ├── automod.py
│   ├── welcome.py
│   ├── tickets.py
│   ├── economy.py
│   ├── leveling.py
│   ├── fun.py
│   ├── profile.py
│   ├── achievements.py
│   ├── reputation.py
│   ├── giveaways.py
│   ├── reaction_roles.py
│   ├── polls.py
│   ├── suggestions.py
│   ├── reports.py
│   ├── reminders.py
│   ├── afk.py
│   ├── custom_commands.py
│   ├── components_v2.py
│   ├── premium.py
│   ├── ai.py
│   ├── analytics.py
│   ├── security.py
│   ├── dashboard.py
│   ├── logging.py
│   └── owner.py
├── database/             # Database models and manager
│   ├── models.py
│   └── manager.py
├── utils/                # Utility modules
│   ├── config.py
│   ├── logger.py
│   ├── errors.py
│   ├── helpers.py
│   ├── cooldown.py
│   └── permissions.py
├── data/                 # SQLite database files
└── logs/                 # Log files
```

## Verification

Run the verification script to check your setup:
```bash
python verify.py
```

## Requirements

- Python 3.10+
- Discord Bot Token
- Discord Application with Message Content Intent enabled
- (Optional) Groq API Key for AI features

## Notes

- All cogs use hybrid commands (both `/` and prefix)
- Database is async SQLite via SQLAlchemy + aiosqlite
- Moderation actions are logged to a `mod-logs` or `logs` channel
- Premium features are simulated for demo purposes
- Owner commands require IDs in `OWNER_IDS` env var
