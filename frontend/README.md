# Body Language Translator - Frontend

A React-based frontend application for real-time body language translation, designed to help communication-disabled individuals express themselves through technology.

## Features

### Core Functionality
- **Body Language to Text**: Convert body gestures, poses, and facial expressions to text
- **Text to Body Language**: Generate body language instructions from text input
- **Real-time Translation**: Live camera feed processing with WebSocket communication
- **Audio Integration**: Speech-to-text and text-to-speech capabilities
- **Multi-language Support**: Translation in multiple languages

### User Interface
- **Modern Material-UI Design**: Clean, accessible interface
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Real-time Feedback**: Live confidence scores and gesture detection
- **Settings Management**: Customizable preferences and accessibility options
- **Session History**: View and manage past translations
- **Dark/Light Theme**: Toggle between themes

### Accessibility Features
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and semantic HTML
- **High Contrast Mode**: Enhanced visibility options
- **Voice Commands**: Speech input for hands-free operation
- **Adjustable Text Size**: Customizable font scaling

## Technology Stack

### Core Technologies
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Material-UI (MUI)**: Professional UI component library
- **React Router**: Client-side routing and navigation

### Real-time Communication
- **WebSocket API**: Real-time bidirectional communication
- **MediaDevices API**: Camera and microphone access
- **WebRTC**: Advanced media handling capabilities

### State Management & Data
- **React Hooks**: Local state management
- **Local Storage**: Persistent user settings
- **Session Storage**: Temporary session data

### Development Tools
- **Create React App**: Development environment
- **Jest**: Unit and integration testing
- **React Testing Library**: Component testing utilities
- **ESLint**: Code quality and consistency

## Installation

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn package manager
- Modern web browser with camera access

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd body-language-translator/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

4. **Open in browser**
   Navigate to `http://localhost:3000`

### Production Build

1. **Create production build**
   ```bash
   npm run build
   ```

2. **Serve the build**
   ```bash
   npm install -g serve
   serve -s build
   ```

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── Header.tsx              # Navigation header
│   │   ├── BodyLanguageTranslator.tsx  # Main translation interface
│   │   ├── RealTimeTranslation.tsx # Real-time processing
│   │   ├── Settings.tsx            # User settings
│   │   ├── History.tsx             # Session history
│   │   └── About.tsx               # About page
│   ├── App.tsx                     # Main application component
│   ├── index.tsx                   # Application entry point
│   └── test_frontend.tsx           # Comprehensive test suite
├── package.json                    # Dependencies and scripts
└── README.md                       # This file
```

## Component Overview

### Header Component
- Navigation menu with routing
- Connection status indicator
- Responsive mobile menu
- Theme toggle functionality

### BodyLanguageTranslator Component
- Dual-mode translation interface
- Webcam integration for video input
- File upload for pre-recorded videos
- Text input for manual translation
- Real-time confidence scoring
- Translation result display

### RealTimeTranslation Component
- Live camera feed processing
- WebSocket connection management
- Real-time message display
- Audio input/output controls
- Connection status monitoring

### Settings Component
- Language preferences
- Confidence thresholds
- Audio settings (voice, speed, pitch)
- Accessibility options
- Theme preferences
- API endpoint configuration

### History Component
- Paginated session history
- Search and filter functionality
- Session details modal
- Export and sharing options
- Bulk operations

### About Component
- Application information
- Technology stack details
- Use cases and impact
- Contact information

## API Integration

### Backend Communication
- **Base URL**: `http://localhost:8000`
- **REST API**: HTTP endpoints for translation
- **WebSocket**: Real-time communication
- **Error Handling**: Graceful error management

### Key Endpoints
- `POST /translate/body-to-text`: Body language to text translation
- `POST /translate/text-to-body`: Text to body language instructions
- `GET /sessions`: Retrieve translation history
- `POST /feedback`: Submit user feedback
- `WS /ws/realtime-translation`: Real-time WebSocket connection

## Testing

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Accessibility Tests**: ARIA compliance and keyboard navigation
- **Error Handling Tests**: API error scenarios
- **Performance Tests**: Rendering efficiency

### Running Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- test_frontend.tsx
```

### Test Structure
- **Component Tests**: Render and interaction testing
- **API Mocking**: Simulated backend responses
- **WebSocket Mocking**: Real-time communication testing
- **User Interaction**: Click, input, and navigation testing

## Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0
```

### Local Storage Keys
- `bodyLanguageTranslatorSettings`: User preferences
- `bodyLanguageTranslatorHistory`: Session cache
- `bodyLanguageTranslatorTheme`: Theme preference

## Performance Optimization

### Code Splitting
- Route-based code splitting
- Lazy loading of components
- Dynamic imports for heavy features

### Bundle Optimization
- Tree shaking for unused code
- Compression and minification
- CDN for static assets

### Caching Strategy
- Service worker for offline support
- Browser caching for static resources
- API response caching

## Security Considerations

### Data Protection
- HTTPS enforcement in production
- Secure WebSocket connections
- Input sanitization and validation

### Privacy Features
- Local processing when possible
- User consent for camera access
- Data retention policies
- GDPR compliance measures

## Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Required Features
- WebRTC (getUserMedia)
- WebSocket API
- Local Storage
- ES6+ JavaScript features

## Deployment

### Build Process
1. **Environment Setup**: Configure production environment
2. **Dependency Installation**: Install production dependencies
3. **Build Generation**: Create optimized production build
4. **Asset Optimization**: Compress and optimize static assets
5. **Deployment**: Deploy to hosting platform

### Hosting Options
- **Netlify**: Static site hosting
- **Vercel**: React-optimized hosting
- **AWS S3**: Scalable object storage
- **Firebase Hosting**: Google's hosting solution

## Troubleshooting

### Common Issues

**Camera Access Denied**
- Ensure HTTPS in production
- Check browser permissions
- Verify camera availability

**WebSocket Connection Failed**
- Check backend server status
- Verify WebSocket URL configuration
- Check firewall settings

**Translation Not Working**
- Verify API endpoint configuration
- Check network connectivity
- Review browser console for errors

### Debug Mode
Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'true');
```

## Contributing

### Development Guidelines
- Follow TypeScript best practices
- Use functional components with hooks
- Implement proper error boundaries
- Write comprehensive tests
- Follow Material-UI design patterns

### Code Style
- Use Prettier for code formatting
- Follow ESLint rules
- Use meaningful component names
- Add JSDoc comments for complex functions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- **Documentation**: Check this README and inline comments
- **Issues**: Report bugs via GitHub issues
- **Discussions**: Use GitHub discussions for questions
- **Email**: Contact the development team

## Roadmap

### Future Enhancements
- **Mobile App**: React Native version
- **Offline Mode**: Service worker implementation
- **Advanced AI**: Enhanced gesture recognition
- **Multi-user**: Collaborative translation sessions
- **Integration**: MS Teams and Zoom plugins
- **Analytics**: Usage tracking and insights
