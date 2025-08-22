# ThereThen - Missed Connection Finder App

A mobile application that allows users to leave and find messages tied to specific locations and time periods, enabling people to connect based on shared presence at the same place and time.

## Features

- **Location & Time Selection**: Draw rectangular areas on maps and specify time periods
- **Message System**: Leave and discover messages in location-based channels
- **Privacy Controls**: Anonymous messaging with optional PII restrictions
- **Group Messaging**: Multi-user channels for shared locations/times
- **Verification System**: Human verification and identity verification processes
- **Clean Modern UI**: Platform-native design with intuitive user experience

## Project Structure

```
there_then/
├── therethen_backend/          # Django backend API
│   ├── core/                   # Core models and views
│   ├── messaging/              # Messaging system
│   ├── verification/           # User verification
│   └── settings.py            # Django configuration
├── therethen_ios/              # iOS mobile app
│   └── therethen_ios/         # SwiftUI source code
├── requirements.txt            # Python dependencies
├── env.example                 # Environment configuration
└── README.md                   # This file
```

## Backend API (Django)

### Prerequisites

- Python 3.9+
- uv package manager
- PostgreSQL with PostGIS (for production)
- SQLite (for development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd there_then
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

### API Endpoints

- **Users**: `/api/users/`
- **Geographic Areas**: `/api/areas/`
- **Channels**: `/api/channels/`
- **Messages**: `/api/messages/`
- **Direct Messages**: `/api/direct-messages/`
- **Reactions**: `/api/reactions/`

### Database Models

- **User**: Custom user model with verification status
- **GeographicArea**: Location areas with PostGIS geometry
- **Channel**: Messaging channels for specific areas/times
- **Message**: Individual messages with privacy controls
- **ChannelMembership**: User membership in channels
- **VerificationRequest**: User verification processes

## iOS Mobile App

### Prerequisites

- Xcode 15.0+
- iOS 17.0+ deployment target
- macOS 14.0+

### Features

- **Map Interface**: Interactive map with drawing tools
- **Authentication**: User registration and login
- **Message Browsing**: View and filter messages
- **Channel Management**: Join/leave messaging channels
- **Profile Management**: User profile and settings

### Architecture

- **SwiftUI**: Modern declarative UI framework
- **Combine**: Reactive programming for data flow
- **MapKit**: Native iOS mapping capabilities
- **Core Location**: Location services and permissions

### Building the App

1. **Open in Xcode**
   ```bash
   open therethen_ios/therethen_ios.xcodeproj
   ```

2. **Configure signing**
   - Select your development team
   - Update bundle identifier if needed

3. **Build and run**
   - Select target device/simulator
   - Press Cmd+R to build and run

## Development Workflow

### Phase 1: Core Infrastructure ✅
- [x] Django REST Framework setup
- [x] Database schema design
- [x] Basic API endpoints
- [x] User authentication system

### Phase 2: Geographic Features ✅
- [x] Map interface implementation
- [x] Area drawing functionality
- [x] Time range selection
- [x] Geographic queries

### Phase 3: Messaging System ✅
- [x] Channel architecture
- [x] Multi-user messaging
- [x] Privacy controls
- [x] Message reactions

### Phase 4: Mobile SDK & UI ✅
- [x] iOS app structure
- [x] API client implementation
- [x] Clean modern design
- [x] Core functionality

### Phase 5: Verification & Security 🔄
- [ ] Human verification system
- [ ] Identity verification
- [ ] Security hardening
- [ ] Privacy controls

## Configuration

### Environment Variables

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (for production)
DB_NAME=therethen_db
DB_USER=therethen_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

# Redis Settings (for channels)
REDIS_URL=redis://localhost:6379/0
```

### Database Configuration

**Development (SQLite)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Production (PostgreSQL + PostGIS)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

## Testing

### Backend Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test core
python manage.py test messaging
python manage.py test verification
```

### iOS Testing
- Use Xcode's built-in testing framework
- Run tests with Cmd+U
- Test on both simulator and device

## Deployment

### Backend Deployment
1. Set up PostgreSQL with PostGIS
2. Configure environment variables
3. Run migrations
4. Set up static file serving
5. Configure web server (nginx + gunicorn)

### iOS App Deployment
1. Archive the app in Xcode
2. Upload to App Store Connect
3. Submit for review
4. Release to App Store

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Roadmap

- [ ] Real-time messaging with WebSockets
- [ ] Push notifications
- [ ] Offline support
- [ ] Advanced privacy controls
- [ ] Social features
- [ ] Analytics and insights
- [ ] Multi-platform support (Android, Web)
